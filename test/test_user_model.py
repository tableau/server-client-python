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


# _decompose_site_role writes CSV rows that the server (and TSC's own
# _evaluate_site_role) parse back into a site role. This parametrized test
# pins the round-trip so a change in either direction can't drift silently.
# The two documented asymmetries are the ServerAdministrator/SiteAdministrator
# label pair and the legacy-role fold; both are captured explicitly below.
@pytest.mark.parametrize(
    "role, expected",
    [
        # Canonical current-model roles round-trip identity.
        ("SiteAdministratorCreator", "SiteAdministratorCreator"),
        ("SiteAdministratorExplorer", "SiteAdministratorExplorer"),
        ("Creator", "Creator"),
        ("ExplorerCanPublish", "ExplorerCanPublish"),
        ("Explorer", "Explorer"),
        ("Viewer", "Viewer"),
        ("Unlicensed", "Unlicensed"),
        # admin="System" always evaluates back to the legacy "SiteAdministrator"
        # label -- that's the only label _evaluate_site_role emits for System.
        ("ServerAdministrator", "SiteAdministrator"),
        # Legacy roles fold into their modern equivalents on the way through.
        # Documented in _decompose_site_role's docstring.
        ("SiteAdministrator", "SiteAdministratorExplorer"),
        ("ReadOnly", "Viewer"),
        ("Publisher", "ExplorerCanPublish"),
        ("Interactor", "Explorer"),
    ],
)
def test_decompose_then_evaluate_round_trips(role: str, expected: str) -> None:
    license_level, admin_level, publish = TSC.UserItem.CSVImport._decompose_site_role(role)
    actual = TSC.UserItem.CSVImport._evaluate_site_role(license_level, admin_level, publish)
    assert actual == expected, (role, license_level, admin_level, publish, actual)


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


def test_validate_mixed_case_license() -> None:
    # Regression: issue #1809 -- 'Viewer' (capital V) was rejected by case-sensitive check
    TSC.UserItem.CSVImport._validate_import_line_or_throw("username, pword, fname, Viewer, None, no, email", logger)
    TSC.UserItem.CSVImport._validate_import_line_or_throw("username, pword, fname, Creator, Site, yes, email", logger)
    TSC.UserItem.CSVImport._validate_import_line_or_throw("username, pword, fname, EXPLORER, NONE, YES, email", logger)


def test_validate_tableauid_with_mfa_auth() -> None:
    # TableauIDWithMFA is a valid auth value and must not be rejected
    TSC.UserItem.CSVImport._validate_import_line_or_throw(
        "username, pword, fname, creator, none, yes, email, TableauIDWithMFA", logger
    )


def test_create_user_preserves_username_case() -> None:
    # Username must not be lowercased -- case matters for LDAP and email-format usernames
    user = TSC.UserItem.CSVImport.create_user_from_line("JSmith, pword, John Smith, creator, none, yes, j@example.com")
    assert user is not None
    assert user.name == "JSmith", f"Username was lowercased: {user.name}"


def test_create_user_with_auth_column() -> None:
    # AUTH column (position 7) must be parsed -- was broken by MAX=7 off-by-one
    user = TSC.UserItem.CSVImport.create_user_from_line("username, pword, fname, creator, none, yes, email, SAML")
    assert user is not None
    assert user.auth_setting == "SAML", f"Expected SAML, got {user.auth_setting}"


def test_too_many_columns_raises() -> None:
    with pytest.raises((ValueError, AttributeError)):
        TSC.UserItem.CSVImport.create_user_from_line("u, p, n, creator, none, yes, email, SAML, extra")
