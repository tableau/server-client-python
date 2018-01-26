import unittest
import tableauserverclient.server.request_factory as factory


class BugFix257(unittest.TestCase):
    def test_empty_request_works(self):
        result = factory.EmptyRequest().empty_req()
        self.assertEqual(b'<tsRequest />', result)
