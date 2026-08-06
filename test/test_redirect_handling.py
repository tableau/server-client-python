"""Tests for manual redirect handling in Endpoint._make_request.

`requests` follows 301/302/303 by converting POST to GET (dropping the body).
We disable auto-redirect and re-issue the same method ourselves inside
`Endpoint._make_request`. These tests drive real endpoint calls (sign_in,
workbooks.get, etc.) through a `requests_mock` transport, so they exercise
the same code path production traffic takes -- not the helper in isolation.
"""

from pathlib import Path

import pytest
import requests_mock

import tableauserverclient as TSC
from tableauserverclient.server.endpoint.exceptions import RedirectError

TEST_ASSET_DIR = Path(__file__).parent / "assets"
SIGN_IN_XML = TEST_ASSET_DIR / "auth_sign_in.xml"
GET_XML = TEST_ASSET_DIR / "workbook_get.xml"


@pytest.fixture
def server() -> TSC.Server:
    s = TSC.Server("http://test", False)
    return s


@pytest.fixture
def signed_in_server() -> TSC.Server:
    s = TSC.Server("http://test", False)
    s.version = "3.10"
    s._set_auth("site-id", "user-id", "auth-token", "")
    return s


def _sign_in_xml() -> str:
    return SIGN_IN_XML.read_text()


def _workbooks_get_xml() -> str:
    return GET_XML.read_text()


# --- Body / method preservation ---------------------------------------------


def test_post_body_preserved_across_redirect(server: TSC.Server) -> None:
    # Regression for tableau/tabcmd#309: POST -> 302 previously turned into GET
    # and dropped the body. Sign-in is the load-bearing POST path; drive it
    # end-to-end and verify (a) the body reaches the final URL intact, and
    # (b) sign_in still parses the response and sets auth state.
    xml = _sign_in_xml()
    seen_bodies: list[bytes | None] = []

    def record_final(request, context):
        seen_bodies.append(request.body)
        context.status_code = 200
        return xml

    with requests_mock.mock() as m:
        m.post(
            server.auth.baseurl + "/signin",
            status_code=302,
            headers={"Location": "http://test/api/3.6/auth/signin"},
        )
        m.post("http://test/api/3.6/auth/signin", text=record_final)

        tableau_auth = TSC.TableauAuth("u", "p", site_id="Samples")
        server.auth.sign_in(tableau_auth)

    assert server.auth_token is not None, "sign_in did not complete"
    assert len(seen_bodies) == 1
    assert seen_bodies[0] is not None
    assert b"<credentials" in seen_bodies[0], "signin XML body was lost across redirect"


def test_post_body_preserved_across_multi_hop_chain(server: TSC.Server) -> None:
    xml = _sign_in_xml()
    with requests_mock.mock() as m:
        m.post(server.auth.baseurl + "/signin", status_code=301, headers={"Location": "http://test/b"})
        m.post("http://test/b", status_code=302, headers={"Location": "http://test/c"})
        m.post("http://test/c", status_code=303, headers={"Location": "http://test/d"})
        m.post("http://test/d", text=xml)

        server.auth.sign_in(TSC.TableauAuth("u", "p"))

    assert server.auth_token is not None


def test_headers_survive_redirect(signed_in_server: TSC.Server) -> None:
    # Regression: the whole point of the PR is method+body+*headers*
    # preservation. Verify X-Tableau-Auth reaches the redirect target.
    seen_headers: list[dict] = []

    def capture(request, context):
        seen_headers.append(dict(request.headers))
        context.status_code = 200
        return _workbooks_get_xml()

    baseurl = signed_in_server.workbooks.baseurl
    with requests_mock.mock() as m:
        m.get(baseurl, status_code=302, headers={"Location": baseurl + "?redirected=1"})
        m.get(baseurl + "?redirected=1", text=capture)
        signed_in_server.workbooks.get()

    # Last hop was the terminal 200 -- inspect its headers.
    assert seen_headers, "final GET never fired"
    final = seen_headers[-1]
    assert final.get("x-tableau-auth") == "auth-token" or final.get("X-Tableau-Auth") == "auth-token", final


def test_get_redirect_still_works(signed_in_server: TSC.Server) -> None:
    baseurl = signed_in_server.workbooks.baseurl
    with requests_mock.mock() as m:
        m.get(baseurl, status_code=301, headers={"Location": baseurl + "?v=2"})
        m.get(baseurl + "?v=2", text=_workbooks_get_xml())
        result = signed_in_server.workbooks.get()
    assert result[0] is not None


# --- Redirect codes ---------------------------------------------------------


@pytest.mark.parametrize("code", [301, 302, 303, 307, 308])
def test_all_supported_redirect_codes_preserve_post_body(server: TSC.Server, code: int) -> None:
    xml = _sign_in_xml()
    seen_bodies: list[bytes | None] = []

    def capture(request, context):
        seen_bodies.append(request.body)
        context.status_code = 200
        return xml

    with requests_mock.mock() as m:
        m.post(server.auth.baseurl + "/signin", status_code=code, headers={"Location": "http://test/new"})
        m.post("http://test/new", text=capture)
        server.auth.sign_in(TSC.TableauAuth("u", "p"))

    assert len(seen_bodies) == 1
    assert seen_bodies[0] is not None
    assert b"<credentials" in seen_bodies[0]


@pytest.mark.parametrize("code", [300, 304, 305, 306])
def test_non_followed_3xx_codes_pass_through(signed_in_server: TSC.Server, code: int) -> None:
    # Only 301/302/303/307/308 are in Redirect_codes. Others should reach
    # _check_status unchanged and surface as ServerResponseError or similar.
    baseurl = signed_in_server.workbooks.baseurl
    with requests_mock.mock() as m:
        m.get(
            baseurl,
            status_code=code,
            text="<tsResponse xmlns='http://tableau.com/api'><error code='foo'><summary>x</summary><detail>y</detail></error></tsResponse>",
        )
        with pytest.raises((TSC.ServerResponseError, Exception)):
            signed_in_server.workbooks.get()


# --- Scheme handling --------------------------------------------------------


def test_https_to_http_downgrade_rejected() -> None:
    s = TSC.Server("https://secure.test", False)
    with requests_mock.mock() as m:
        m.post(
            s.auth.baseurl + "/signin",
            status_code=301,
            headers={"Location": "http://insecure.test/api/3.6/auth/signin"},
        )
        with pytest.raises(RedirectError, match="HTTPS -> HTTP"):
            s.auth.sign_in(TSC.TableauAuth("u", "p"))


def test_https_to_http_downgrade_rejected_on_later_hop() -> None:
    # First hop is https->https (safe), second hop tries to downgrade.
    # Regression coverage that the guard runs each iteration, not just once.
    s = TSC.Server("https://a.test", False)
    with requests_mock.mock() as m:
        m.post(s.auth.baseurl + "/signin", status_code=301, headers={"Location": "https://b.test/signin"})
        m.post("https://b.test/signin", status_code=301, headers={"Location": "http://c.test/signin"})
        with pytest.raises(RedirectError, match="HTTPS -> HTTP"):
            s.auth.sign_in(TSC.TableauAuth("u", "p"))


def test_http_to_https_upgrade_allowed(server: TSC.Server) -> None:
    # Not a security concern -- the whole point of #309 is that
    # http://.../signin -> https://.../signin should work.
    xml = _sign_in_xml()
    with requests_mock.mock() as m:
        m.post(
            server.auth.baseurl + "/signin", status_code=301, headers={"Location": "https://test/api/3.6/auth/signin"}
        )
        m.post("https://test/api/3.6/auth/signin", text=xml)
        server.auth.sign_in(TSC.TableauAuth("u", "p"))
    assert server.auth_token is not None


def test_cross_host_redirect_followed(server: TSC.Server) -> None:
    # e.g. http://online.tableau.com -> http://east.online.tableau.com.
    # This is the scenario in the original inline signin comment.
    xml = _sign_in_xml()
    with requests_mock.mock() as m:
        m.post(
            server.auth.baseurl + "/signin",
            status_code=301,
            headers={"Location": "http://east.test/api/3.6/auth/signin"},
        )
        m.post("http://east.test/api/3.6/auth/signin", text=xml)
        server.auth.sign_in(TSC.TableauAuth("u", "p"))
    assert server.auth_token is not None


# --- Location edge cases ----------------------------------------------------


def test_relative_location_header(server: TSC.Server) -> None:
    # RFC 7231 allows relative Location values; urljoin against request URL.
    xml = _sign_in_xml()
    with requests_mock.mock() as m:
        m.post(server.auth.baseurl + "/signin", status_code=302, headers={"Location": "/api/3.6/auth/signin"})
        m.post("http://test/api/3.6/auth/signin", text=xml)
        server.auth.sign_in(TSC.TableauAuth("u", "p"))
    assert server.auth_token is not None


def test_missing_location_header_raises_redirecterror(server: TSC.Server) -> None:
    # `requests`' internal resolve_redirects raises KeyError('location') with no
    # context. We raise RedirectError with URL, method, status code.
    with requests_mock.mock() as m:
        m.post(server.auth.baseurl + "/signin", status_code=302)  # no Location header
        with pytest.raises(RedirectError, match="without a Location header"):
            server.auth.sign_in(TSC.TableauAuth("u", "p"))


# --- Hop limits -------------------------------------------------------------


def test_redirect_loop_hits_max_hops(server: TSC.Server) -> None:
    server.session.max_redirects = 3
    with requests_mock.mock() as m:
        m.post(server.auth.baseurl + "/signin", status_code=302, headers={"Location": "http://test/loop"})
        m.post("http://test/loop", status_code=302, headers={"Location": "http://test/loop"})
        with pytest.raises(RedirectError, match="Exceeded 3 redirect hops"):
            server.auth.sign_in(TSC.TableauAuth("u", "p"))


def test_max_redirects_zero_passes_non_redirect_response(signed_in_server: TSC.Server) -> None:
    # Regression for the review finding: with the loop bounded by
    # `range(max_hops)`, max_redirects=0 previously fell straight into the
    # "exceeded" error even for a 200 response.
    signed_in_server.session.max_redirects = 0
    baseurl = signed_in_server.workbooks.baseurl
    with requests_mock.mock() as m:
        m.get(baseurl, text=_workbooks_get_xml())
        result = signed_in_server.workbooks.get()
    assert result[0] is not None


def test_max_redirects_one_rejects_second_hop(signed_in_server: TSC.Server) -> None:
    # max_redirects=1 allows one non-redirect response but errors on a second
    # 3xx. (max_redirects=0 is not tested because `requests` itself refuses to
    # complete any request that returns 3xx when max_redirects=0, regardless of
    # allow_redirects; the response never reaches _make_request.)
    signed_in_server.session.max_redirects = 1
    baseurl = signed_in_server.workbooks.baseurl
    with requests_mock.mock() as m:
        m.get(baseurl, status_code=302, headers={"Location": baseurl + "?v=2"})
        m.get(baseurl + "?v=2", status_code=302, headers={"Location": baseurl + "?v=3"})
        with pytest.raises(RedirectError, match="Exceeded 1 redirect hops"):
            signed_in_server.workbooks.get()
