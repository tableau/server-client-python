import requests
import tableauserverclient as TSC


# see https://requestbin.net/ to create your own endpoint
test_request_bin = "o3sis36a9xu2byiu.b.requestbin.net"


def session_factory():
    session = requests.session()
    session.headers.update({'x-test': 'true'})
    return session


# now we initialize the server, including 'use_server_version' which will trigger a request to the server url.
# The operation will fail, because that's not Tableau Server!
server = TSC.Server(test_request_bin, use_server_version=True, session_factory=session_factory)
# To validate the session factory, go visit the request bin and confirm you saw the headers
