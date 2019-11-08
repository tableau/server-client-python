import unittest

try:
    from unittest import mock
except ImportError:
    import mock

import tableauserverclient.server.request_factory as factory
from tableauserverclient.server.endpoint import Endpoint
from tableauserverclient.filesys_helpers import to_filename, make_download_path


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


class FileSysHelpers(unittest.TestCase):
    def test_to_filename(self):
        invalid = [
            "23brhafbjrjhkbbea.txt",
            'a_b_C.txt',
            'windows space.txt',
            'abc#def.txt',
            't@bL3A()',
        ]

        valid = [
            "23brhafbjrjhkbbea.txt",
            'a_b_C.txt',
            'windows space.txt',
            'abcdef.txt',
            'tbL3A',
        ]

        self.assertTrue(all([(to_filename(i) == v) for i, v in zip(invalid, valid)]))

    def test_make_download_path(self):
        no_file_path = (None, 'file.ext')
        has_file_path_folder = ('/root/folder/', 'file.ext')
        has_file_path_file = ('out', 'file.ext')

        self.assertEqual('file.ext', make_download_path(*no_file_path))
        self.assertEqual('out.ext', make_download_path(*has_file_path_file))

        with mock.patch('os.path.isdir') as mocked_isdir:
            mocked_isdir.return_value = True
            self.assertEqual('/root/folder/file.ext', make_download_path(*has_file_path_folder))
