import unittest
import tableauserverclient.server.request_factory as factory
from tableauserverclient.server.endpoint import Endpoint


class BugFix257(unittest.TestCase):
    def test_empty_request_works(self):
        result = factory.EmptyRequest().empty_req()
        self.assertEqual(b'<tsRequest />', result)


class BugFix273(unittest.TestCase):
    def test_binary_log_truncated(self):

        class FakeResponse(object):

            headers = {'Content-Type': 'application/octet-stream'}
            content = b'\x1337' * 1000
            status_code = 200

        server_response = FakeResponse()

        self.assertEqual(Endpoint._safe_to_log(server_response), '[Truncated File Contents]')
