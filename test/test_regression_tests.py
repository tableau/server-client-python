import unittest

try:
    from unittest import mock
except ImportError:
    import mock  # type: ignore[no-redef]

import tableauserverclient.server.request_factory as factory
from tableauserverclient.helpers.strings import redact_xml
from tableauserverclient.filesys_helpers import to_filename, make_download_path


class BugFix257(unittest.TestCase):
    def test_empty_request_works(self):
        result = factory.EmptyRequest().empty_req()
        self.assertEqual(b"<tsRequest />", result)


class FileSysHelpers(unittest.TestCase):
    def test_to_filename(self):
        invalid = [
            "23brhafbjrjhkbbea.txt",
            "a_b_C.txt",
            "windows space.txt",
            "abc#def.txt",
            "t@bL3A()",
        ]

        valid = [
            "23brhafbjrjhkbbea.txt",
            "a_b_C.txt",
            "windows space.txt",
            "abcdef.txt",
            "tbL3A",
        ]

        self.assertTrue(all([(to_filename(i) == v) for i, v in zip(invalid, valid)]))

    def test_make_download_path(self):
        no_file_path = (None, "file.ext")
        has_file_path_folder = ("/root/folder/", "file.ext")
        has_file_path_file = ("outx", "file.ext")

        self.assertEqual("file.ext", make_download_path(*no_file_path))
        self.assertEqual("outx.ext", make_download_path(*has_file_path_file))

        with mock.patch("os.path.isdir") as mocked_isdir:
            mocked_isdir.return_value = True
            self.assertEqual("/root/folder/file.ext", make_download_path(*has_file_path_folder))


class LoggingTest(unittest.TestCase):
    def test_redact_password_string(self):
        redacted = redact_xml(
            "<?xml version='1.0'?><workbook><password>this is password: my_super_secret_passphrase_which_nobody_should_ever_see  password: value</password></workbook>"
        )
        assert redacted.find("value") == -1
        assert redacted.find("secret") == -1
        assert redacted.find("ever_see") == -1
        assert redacted.find("my_super_secret_passphrase_which_nobody_should_ever_see") == -1

    def test_redact_password_bytes(self):
        redacted = redact_xml(
            b"<?xml version='1.0'?><datasource><data-connection name='con-artist' password='value string with at least a password: valuesecret or two in it'/></datasource>"
        )
        assert redacted.find(b"value") == -1
        assert redacted.find(b"secret") == -1

    def test_redact_password_with_special_char(self):
        redacted = redact_xml(
            "<?xml version='1.0'?><content><safe_text value='this is a nondescript text line which is public' password='my_s per_secre>_passphrase_which_nobody_should_ever_see with password: value'> </safe_text></content>"
        )
        assert redacted.find("my_s per_secre>_passphrase_which_nobody_should_ever_see with password: value") == -1

    def test_redact_password_not_xml(self):
        redacted = redact_xml(
            "<content><safe_text value='this is a nondescript text line which is public' password='my_s per_secre>_passphrase_which_nobody_should_ever_see with password: value'> </safe_text></content>"
        )
        assert redacted.find("my_s per_secre>_passphrase_which_nobody_should_ever_see") == -1

    def test_redact_password_really_not_xml(self):
        redacted = redact_xml(
            "value='this is a nondescript text line which is public' password='my_s per_secre>_passphrase_which_nobody_should_ever_see with password: value and then a cookie "
        )
        assert redacted.find("my_s per_secre>_passphrase_which_nobody_should_ever_see") == -1
        assert redacted.find("passphrase") == -1, redacted
        assert redacted.find("cookie") == -1, redacted
