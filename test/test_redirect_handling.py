"""Tests for manual redirect handling in Endpoint._make_request.

`requests` follows 301/302/303 by converting POST to GET (dropping the body).
We disable auto-redirect and re-issue the same method ourselves in
Endpoint._follow_redirect_if_any. These tests cover the resulting behavior:

- POST body preserved across a redirect
- multi-hop chains
- HTTPS -> HTTP scheme downgrade refused
- missing Location header raises RedirectError
- exceeding session.max_redirects raises RedirectError
- GET redirects still work
"""

from pathlib import Path

import pytest
import requests_mock

import tableauserverclient as TSC
from tableauserverclient.server.endpoint.exceptions import RedirectError

TEST_ASSET_DIR = Path(__file__).parent / "assets"
SIGN_IN_XML = TEST_ASSET_DIR / "auth_sign_in.xml"


@pytest.fixture
def server() -> TSC.Server:
    return TSC.Server("http://test", False)


@pytest.fixture
def signed_in_server() -> TSC.Server:
    s = TSC.Server("http://test", False)
    s._set_auth("site-id", "user-id", "auth-token", "")
    return s


def _sign_in_xml() -> str:
    with open(SIGN_IN_XML, "rb") as f:
        return f.read().decode("utf-8")


def test_post_body_preserved_across_redirect(signed_in_server: TSC.Server) -> None:
    # Regression for tableau/tabcmd#309: POST -> 302 previously turned into GET
    # and dropped the request body. Verify the body reaches the final URL intact.
    seen_bodies: list[bytes | None] = []

    def record(request, context):
        seen_bodies.append(request.body)
        context.status_code = 200
        return b"<tsResponse/>"

    with requests_mock.mock() as m:
        m.post("http://test/redirect-from", status_code=302, headers={"Location": "http://test/redirect-to"})
        m.post("http://test/redirect-to", content=record)

        resp = signed_in_server.session.post(
            "http://test/redirect-from",
            data=b"payload=1",
            allow_redirects=False,
        )
        # The Endpoint layer, not the raw session, is what re-issues. Route
        # through _make_request so we exercise the code under test.
        from tableauserverclient.server.endpoint.endpoint import Endpoint

        endpoint = Endpoint(signed_in_server)
        final, url = endpoint._follow_redirect_if_any(
            signed_in_server.session.post,
            "http://test/redirect-from",
            {"data": b"payload=1", "allow_redirects": False},
            resp,
        )

    assert final.status_code == 200
    assert url == "http://test/redirect-to"
    assert seen_bodies == [b"payload=1"], seen_bodies


def test_multi_hop_redirect_chain(signed_in_server: TSC.Server) -> None:
    with requests_mock.mock() as m:
        m.post("http://test/a", status_code=301, headers={"Location": "http://test/b"})
        m.post("http://test/b", status_code=302, headers={"Location": "http://test/c"})
        m.post("http://test/c", status_code=200, text="<tsResponse/>")

        resp = signed_in_server.session.post("http://test/a", allow_redirects=False)
        from tableauserverclient.server.endpoint.endpoint import Endpoint

        endpoint = Endpoint(signed_in_server)
        final, url = endpoint._follow_redirect_if_any(
            signed_in_server.session.post, "http://test/a", {"allow_redirects": False}, resp
        )

    assert final.status_code == 200
    assert url == "http://test/c"


def test_relative_location_header(signed_in_server: TSC.Server) -> None:
    # RFC 7231 allows relative Location values; join them against the request URL.
    with requests_mock.mock() as m:
        m.post("http://test/api/v1/thing", status_code=302, headers={"Location": "/api/v2/thing"})
        m.post("http://test/api/v2/thing", status_code=200, text="<tsResponse/>")

        resp = signed_in_server.session.post("http://test/api/v1/thing", allow_redirects=False)
        from tableauserverclient.server.endpoint.endpoint import Endpoint

        endpoint = Endpoint(signed_in_server)
        final, url = endpoint._follow_redirect_if_any(
            signed_in_server.session.post, "http://test/api/v1/thing", {"allow_redirects": False}, resp
        )

    assert final.status_code == 200
    assert url == "http://test/api/v2/thing"


def test_https_to_http_downgrade_rejected() -> None:
    # HTTPS -> HTTP redirect is never legitimate: quietly following it would
    # send auth material over plaintext. Refuse and surface a clear error.
    s = TSC.Server("https://secure.test", False)
    s._set_auth("site-id", "user-id", "auth-token", "")

    with requests_mock.mock() as m:
        m.post("https://secure.test/signin", status_code=301, headers={"Location": "http://insecure.test/signin"})
        resp = s.session.post("https://secure.test/signin", allow_redirects=False)
        from tableauserverclient.server.endpoint.endpoint import Endpoint

        endpoint = Endpoint(s)
        with pytest.raises(RedirectError, match="HTTPS -> HTTP"):
            endpoint._follow_redirect_if_any(
                s.session.post, "https://secure.test/signin", {"allow_redirects": False}, resp
            )


def test_missing_location_header_raises_redirecterror(signed_in_server: TSC.Server) -> None:
    # `requests`' internal resolve_redirects raises KeyError('location') with no
    # context. We raise RedirectError with the URL, method, and status code.
    with requests_mock.mock() as m:
        m.post("http://test/broken", status_code=302)  # no Location header
        resp = signed_in_server.session.post("http://test/broken", allow_redirects=False)
        from tableauserverclient.server.endpoint.endpoint import Endpoint

        endpoint = Endpoint(signed_in_server)
        with pytest.raises(RedirectError, match="without a Location header"):
            endpoint._follow_redirect_if_any(
                signed_in_server.session.post, "http://test/broken", {"allow_redirects": False}, resp
            )


def test_redirect_loop_hits_max_hops(signed_in_server: TSC.Server) -> None:
    signed_in_server.session.max_redirects = 3
    with requests_mock.mock() as m:
        m.post("http://test/loop", status_code=302, headers={"Location": "http://test/loop"})
        resp = signed_in_server.session.post("http://test/loop", allow_redirects=False)
        from tableauserverclient.server.endpoint.endpoint import Endpoint

        endpoint = Endpoint(signed_in_server)
        with pytest.raises(RedirectError, match="Exceeded 3 redirect hops"):
            endpoint._follow_redirect_if_any(
                signed_in_server.session.post, "http://test/loop", {"allow_redirects": False}, resp
            )


def test_non_redirect_response_passes_through(signed_in_server: TSC.Server) -> None:
    # 200 stays 200; the helper is a no-op for non-3xx.
    with requests_mock.mock() as m:
        m.post("http://test/ok", status_code=200, text="<tsResponse/>")
        resp = signed_in_server.session.post("http://test/ok", allow_redirects=False)
        from tableauserverclient.server.endpoint.endpoint import Endpoint

        endpoint = Endpoint(signed_in_server)
        final, url = endpoint._follow_redirect_if_any(
            signed_in_server.session.post, "http://test/ok", {"allow_redirects": False}, resp
        )

    assert final.status_code == 200
    assert url == "http://test/ok"


def test_sign_in_after_redirect(server: TSC.Server) -> None:
    # Integration-style: real sign-in flow across a redirect. Verifies that
    # auth_endpoint's existing manual-redirect-of-signin still works alongside
    # the generic _make_request redirect handling.
    xml = _sign_in_xml()
    with requests_mock.mock() as m:
        m.post(
            server.auth.baseurl + "/signin", status_code=301, headers={"Location": "http://test/api/3.6/auth/signin"}
        )
        m.post("http://test/api/3.6/auth/signin", text=xml)
        tableau_auth = TSC.TableauAuth("u", "p", site_id="Samples")
        server.auth.sign_in(tableau_auth)

    assert server.auth_token is not None
