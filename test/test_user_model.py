import logging
from unittest.mock import *
import io

import pytest

import tableauserverclient as TSC


def test_invalid_auth_setting():
    user = TSC.UserItem("me", TSC.UserItem.Roles.Publisher)
    with pytest.raises(ValueError):
        user.auth_setting = "Hello"


def test_invalid_site_role():
    user = TSC.UserItem("me", TSC.UserItem.Roles.Publisher)
    with pytest.raises(ValueError):
        user.site_role = "Hello"


logger = logging.getLogger("UserModelTest")


role_inputs = [
    ["creator", "system", "yes", "SiteAdministrator"],
    ["None", "system", "no", "SiteAdministrator"],
    ["explorer", "SysTEm", "no", "SiteAdministrator"],
    ["creator", "site", "yes", "SiteAdministratorCreator"],
    ["explorer", "site", "yes", "SiteAdministratorExplorer"],
    ["creator", "SITE", "no", "SiteAdministratorCreator"],
    ["creator", "none", "yes", "Creator"],
    ["explorer", "none", "yes", "ExplorerCanPublish"],
    ["viewer", "None", "no", "Viewer"],
    ["explorer", "no", "yes", "ExplorerCanPublish"],
    ["EXPLORER", "noNO", "yes", "ExplorerCanPublish"],
    ["explorer", "no", "no", "Explorer"],
    ["unlicensed", "none", "no", "Unlicensed"],
    ["Chef", "none", "yes", "Unlicensed"],
    ["yes", "yes", "yes", "Unlicensed"],
]

valid_import_content = [
    "username, pword, fname, creator, site, yes, email",
    "username, pword, fname, explorer, none, no, email",
    "",
    "u",
    "p",
]

valid_username_content = ["jfitzgerald@tableau.com"]

usernames = [
    "valid",
    "valid@email.com",
    "domain/valid",
    "domain/valid@tmail.com",
    "va!@#$%^&*()lid",
    "in@v@lid",
    "in valid",
    "",
]


def test_validate_usernames() -> None:
    TSC.UserItem.validate_username_or_throw(usernames[0])
    TSC.UserItem.validate_username_or_throw(usernames[1])
    TSC.UserItem.validate_username_or_throw(usernames[2])
    TSC.UserItem.validate_username_or_throw(usernames[3])
    TSC.UserItem.validate_username_or_throw(usernames[4])
    with pytest.raises(AttributeError):
        TSC.UserItem.validate_username_or_throw(usernames[5])
    with pytest.raises(AttributeError):
        TSC.UserItem.validate_username_or_throw(usernames[6])


def test_evaluate_role() -> None:
    for line in role_inputs:
        actual = TSC.UserItem.CSVImport._evaluate_site_role(line[0], line[1], line[2])
        assert actual == line[3], line + [actual]


def test_get_user_detail_empty_line() -> None:
    test_line = ""
    test_user = TSC.UserItem.CSVImport.create_user_from_line(test_line)
    assert test_user is None


def test_get_user_detail_standard() -> None:
    test_line = "username, pword, fname, license, admin, pub, email"
    test_user = TSC.UserItem.CSVImport.create_user_from_line(test_line)
    assert test_user is not None
    assert test_user.name == "username", test_user.name
    assert test_user.fullname == "fname", test_user.fullname
    assert test_user.site_role == "Unlicensed", test_user.site_role
    assert test_user.email == "email", test_user.email


def test_get_user_details_only_username() -> None:
    test_line = "username"
    test_user = TSC.UserItem.CSVImport.create_user_from_line(test_line)


def test_populate_user_details_only_some() -> None:
    values = "username, , , creator, admin"
    user = TSC.UserItem.CSVImport.create_user_from_line(values)
    assert user is not None
    assert user.name == "username"


def test_validate_user_detail_standard() -> None:
    test_line = "username, pword, fname, creator, site, 1, email"
    TSC.UserItem.CSVImport._validate_import_line_or_throw(test_line, logger)
    TSC.UserItem.CSVImport.create_user_from_line(test_line)


# for file handling
def _mock_file_content(content: list[str]) -> io.TextIOWrapper:
    # the empty string represents EOF
    # the tests run through the file twice, first to validate then to fetch
    mock = MagicMock(io.TextIOWrapper)
    content.append("")  # EOF
    mock.readline.side_effect = content
    mock.name = "file-mock"
    return mock


def test_validate_import_file() -> None:
    test_data = _mock_file_content(valid_import_content)
    valid, invalid = TSC.UserItem.CSVImport.validate_file_for_import(test_data, logger)
    assert valid == 2, f"Expected two lines to be parsed, got {valid}"
    assert invalid == [], f"Expected no failures, got {invalid}"


def test_validate_usernames_file() -> None:
    test_data = _mock_file_content(usernames)
    valid, invalid = TSC.UserItem.CSVImport.validate_file_for_import(test_data, logger)
    assert valid == 5, f"Exactly 5 of the lines were valid, counted {valid + len(invalid)}"


def _mask_present(records: list) -> bool:
    combined = "\n".join(record.getMessage() for record in records)
    return "PASS" in combined and "***" in combined


def test_password_not_logged_at_debug(caplog: pytest.LogCaptureFixture) -> None:
    """Regression test for #1829: passwords must not appear in DEBUG logs."""
    secret = "hunter2SUPERSECRET"
    line = f"jsmith,{secret},John Smith,creator,site,yes,jsmith@example.com"
    with caplog.at_level(logging.DEBUG, logger=logger.name):
        TSC.UserItem.CSVImport._validate_import_line_or_throw(line, logger)
    combined = "\n".join(record.getMessage() for record in caplog.records)
    assert secret not in combined, f"Password leaked into logs: {combined!r}"
    # Positive assertion: something references the PASS column and something is
    # masked as ***, so a "fix" that only removed the log line would not pass.
    assert _mask_present(caplog.records), f"Expected masked PASS log line; got: {combined!r}"


def test_password_not_logged_when_line_invalid(caplog: pytest.LogCaptureFixture) -> None:
    """Regression test for #1829: passwords must not appear when a row fails to validate."""
    secret = "hunter2SUPERSECRET"
    line = f"jsmith,{secret},John Smith,not-a-real-license,site,yes,jsmith@example.com"
    test_data = _mock_file_content([line])
    with caplog.at_level(logging.DEBUG, logger=logger.name):
        valid, invalid = TSC.UserItem.CSVImport.validate_file_for_import(test_data, logger)
    assert valid == 0
    assert len(invalid) == 1
    assert secret not in invalid[0], f"Password leaked into returned invalid_lines: {invalid[0]!r}"
    combined = "\n".join(record.getMessage() for record in caplog.records)
    assert secret not in combined, f"Password leaked into logs on invalid row: {combined!r}"


def test_password_with_comma_partially_masks(caplog: pytest.LogCaptureFixture) -> None:
    """A password containing commas is misaligned by the naive split parser: only the
    portion that lands in column 1 gets masked. The remaining fragments still leak.
    This documents the limitation — fully protecting passwords with embedded commas
    requires a proper CSV parser — but confirms that the column-1 mask holds even
    when the password value contains a comma."""
    line = "jsmith,hunter2,SECRETTAIL,creator,site,yes,jsmith@example.com"
    with caplog.at_level(logging.DEBUG, logger=logger.name):
        try:
            TSC.UserItem.CSVImport._validate_import_line_or_throw(line, logger)
        except Exception:
            pass  # misaligned columns are expected to fail validation
    combined = "\n".join(record.getMessage() for record in caplog.records)
    # Column 1 ("hunter2") is masked; the fragment that spilled into column 2
    # ("SECRETTAIL") is not — this is the documented limitation.
    assert "hunter2" not in combined
    assert _mask_present(caplog.records)


def test_redact_password_column_helper() -> None:
    """Unit-level coverage for _redact_password_column across newline and edge cases."""
    redact = TSC.UserItem.CSVImport._redact_password_column
    # LF-terminated
    assert redact("jsmith,hunter2,fname\n") == "jsmith,***,fname\n"
    # CRLF-terminated (the \r rides with the last field, ending is preserved)
    assert redact("jsmith,hunter2,fname\r\n") == "jsmith,***,fname\r\n"
    # No trailing newline
    assert redact("jsmith,hunter2,fname") == "jsmith,***,fname"
    # Empty password field: still replaced (unconditional mask)
    assert redact("jsmith,,fname") == "jsmith,***,fname"
    # Trailing comma with nothing after: column 1 exists as empty string, gets masked
    assert redact("jsmith,") == "jsmith,***"
    # Single column: no password to redact; return line unchanged
    assert redact("jsmith") == "jsmith"
    assert redact("jsmith\n") == "jsmith\n"
