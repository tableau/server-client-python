from unittest import mock

import tableauserverclient.server.request_factory as factory
from tableauserverclient.helpers.strings import redact_xml
from tableauserverclient.filesys_helpers import to_filename, make_download_path


def test_empty_request_works():
    result = factory.EmptyRequest().empty_req()
    assert b"<tsRequest />" == result


def test_to_filename():
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

    assert all([(to_filename(i) == v) for i, v in zip(invalid, valid)])


def test_make_download_path():
    no_file_path = (None, "file.ext")
    has_file_path_folder = ("/root/folder/", "file.ext")
    has_file_path_file = ("outx", "file.ext")

    assert "file.ext" == make_download_path(*no_file_path)
    assert "outx.ext" == make_download_path(*has_file_path_file)

    with mock.patch("os.path.isdir") as mocked_isdir:
        mocked_isdir.return_value = True
        assert "/root/folder/file.ext" == make_download_path(*has_file_path_folder)


def test_redact_password_string():
    redacted = redact_xml(
        "<?xml version='1.0'?><workbook><password>this is password: my_super_secret_passphrase_which_nobody_should_ever_see  password: value</password></workbook>"
    )
    assert redacted.find("value") == -1
    assert redacted.find("secret") == -1
    assert redacted.find("ever_see") == -1
    assert redacted.find("my_super_secret_passphrase_which_nobody_should_ever_see") == -1


def test_redact_password_bytes():
    redacted = redact_xml(
        b"<?xml version='1.0'?><datasource><data-connection name='con-artist' password='value string with at least a password: valuesecret or two in it'/></datasource>"
    )
    assert redacted.find(b"value") == -1
    assert redacted.find(b"secret") == -1


def test_redact_password_with_special_char():
    redacted = redact_xml(
        "<?xml version='1.0'?><content><safe_text value='this is a nondescript text line which is public' password='my_s per_secre>_passphrase_which_nobody_should_ever_see with password: value'> </safe_text></content>"
    )
    assert redacted.find("my_s per_secre>_passphrase_which_nobody_should_ever_see with password: value") == -1


def test_redact_password_not_xml():
    redacted = redact_xml(
        "<content><safe_text value='this is a nondescript text line which is public' password='my_s per_secre>_passphrase_which_nobody_should_ever_see with password: value'> </safe_text></content>"
    )
    assert redacted.find("my_s per_secre>_passphrase_which_nobody_should_ever_see") == -1


def test_redact_password_really_not_xml():
    redacted = redact_xml(
        "value='this is a nondescript text line which is public' password='my_s per_secre>_passphrase_which_nobody_should_ever_see with password: value and then a cookie "
    )
    assert redacted.find("my_s per_secre>_passphrase_which_nobody_should_ever_see") == -1
    assert redacted.find("passphrase") == -1, redacted
    assert redacted.find("cookie") == -1, redacted


def test_redact_personal_access_token_secret():
    redacted = redact_xml(
        b'<tsRequest><credentials personalAccessTokenName="my-token" personalAccessTokenSecret="PAT-SECRET-VALUE">'
        b'<site contentUrl="mysite"/></credentials></tsRequest>'
    )
    assert redacted.find(b"PAT-SECRET-VALUE") == -1, redacted
    assert redacted.find(b"my-token") > 0, redacted
    assert redacted.find(b"mysite") > 0, redacted


def test_redact_jwt():
    redacted = redact_xml(
        '<tsRequest><credentials jwt="eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJ1In0.c2lnbmF0dXJl" isUat="false">'
        '<site contentUrl=""/></credentials></tsRequest>'
    )
    assert redacted.find("eyJhbGciOiJIUzI1NiJ9") == -1, redacted
    assert redacted.find("isUat") > 0, redacted


def test_redact_session_token_in_namespaced_response():
    redacted = redact_xml(
        '<tsResponse xmlns="http://tableau.com/api"><credentials token="SESSION-TOKEN-VALUE">'
        '<site id="6b7179ba" contentUrl="Samples"/><user id="1a96d216"/></credentials></tsResponse>'
    )
    assert redacted.find("SESSION-TOKEN-VALUE") == -1, redacted
    assert redacted.find("6b7179ba") > 0, redacted
    assert redacted.find("1a96d216") > 0, redacted


def test_redact_unknown_credentials_attribute():
    redacted = redact_xml('<tsRequest><credentials name="u" newSecretField="UNKNOWN-SECRET"/></tsRequest>')
    assert redacted.find("UNKNOWN-SECRET") == -1, redacted
    assert redacted.find('name="u"') > 0, redacted


def test_redact_client_secret():
    redacted = redact_xml(
        '<tsRequest><site><openIDConnect clientId="id" clientSecret="CLIENT-SECRET"/></site></tsRequest>'
    )
    assert redacted.find("CLIENT-SECRET") == -1, redacted
    assert redacted.find('clientId="id"') > 0, redacted


def test_redact_truncated_xml_does_not_return_secret():
    body = (
        b'<tsRequest><credentials personalAccessTokenName="n" personalAccessTokenSecret="PAT-SECRET-VALUE">'
        b'<site contentUrl=""/></credentials></tsRequest>'
    )
    redacted = redact_xml(body[:110])
    assert redacted.find(b"PAT-SECRET") == -1, redacted


def test_redact_unparseable_without_password_returns_placeholder():
    redacted = redact_xml(
        "--boundary\r\nContent-Disposition: name=request_payload\r\n\r\n<tsRequest><workbook name='w'"
    )
    assert redacted.find("boundary") == -1, redacted
    assert redacted.find("workbook") == -1, redacted
    assert redacted == "[unparseable content redacted]", redacted
