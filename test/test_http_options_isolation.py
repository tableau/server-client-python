import copy
from pathlib import Path

import requests_mock

import tableauserverclient as TSC
from tableauserverclient.server.endpoint.endpoint import TABLEAU_AUTH_HEADER

SIGN_IN_XML = (Path(__file__).parent / "assets" / "auth_sign_in.xml").read_text()
TOKEN_A = "eIX6mvFsqyansa4KqEI1UwOpS8ggRs2l"


def _shared_options() -> dict:
    return {"headers": {"X-Corp": "1"}, "timeout": 30}


def _sign_in_and_call(server: TSC.Server, m: requests_mock.Mocker) -> None:
    m.post(server.auth.baseurl + "/signin", text=SIGN_IN_XML)
    server.auth.sign_in(TSC.TableauAuth("user", "password", site_id="Samples"))
    m.get(server.workbooks.baseurl, text="<tsResponse/>")
    server.workbooks.get_request(server.workbooks.baseurl)


def test_sign_in_does_not_mutate_caller_http_options() -> None:
    shared = _shared_options()
    original = copy.deepcopy(shared)
    server_a = TSC.Server("http://a.example", http_options=shared)
    server_b = TSC.Server("http://b.example", http_options=shared)

    with requests_mock.mock() as m:
        _sign_in_and_call(server_a, m)

    assert shared == original
    assert TABLEAU_AUTH_HEADER not in server_a.http_options["headers"]
    assert TABLEAU_AUTH_HEADER not in server_b.http_options["headers"]
    assert server_a.http_options["headers"]["X-Corp"] == "1"


def test_sign_in_to_second_server_does_not_send_first_server_token() -> None:
    shared = _shared_options()
    server_a = TSC.Server("http://a.example", http_options=shared)
    server_b = TSC.Server("http://b.example", http_options=shared)

    with requests_mock.mock() as m:
        _sign_in_and_call(server_a, m)
        assert m.last_request.headers[TABLEAU_AUTH_HEADER] == TOKEN_A
        m.post(server_b.auth.baseurl + "/signin", text=SIGN_IN_XML)
        server_b.auth.sign_in(TSC.TableauAuth("user", "password", site_id="Samples"))
        sign_in_b = m.last_request

    assert sign_in_b.hostname == "b.example"
    assert TABLEAU_AUTH_HEADER not in sign_in_b.headers
    assert sign_in_b.headers["X-Corp"] == "1"


def test_requests_after_sign_out_carry_no_token() -> None:
    server = TSC.Server("http://a.example", http_options=_shared_options())

    with requests_mock.mock() as m:
        _sign_in_and_call(server, m)
        m.post(server.auth.baseurl + "/signout", text="")
        server.auth.sign_out()
        m.post(server.auth.baseurl + "/signin", text=SIGN_IN_XML)
        server.auth.sign_in(TSC.TableauAuth("user", "password", site_id="Samples"))
        sign_in_again = m.last_request

    assert TABLEAU_AUTH_HEADER not in sign_in_again.headers
