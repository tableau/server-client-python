import io
import os
import unittest
from typing import List
from unittest.mock import *
import requests_mock

import tableauserverclient as TSC

TEST_ASSET_DIR = os.path.join(os.path.dirname(__file__), "assets")


ADD_XML = os.path.join(TEST_ASSET_DIR, "user_add.xml")
USERNAMES = os.path.join(TEST_ASSET_DIR, "Data", "usernames.csv")
USERS = os.path.join(TEST_ASSET_DIR, "Data", "user_details.csv")
USERS_BAD = os.path.join(TEST_ASSET_DIR, "Data", "user_details_fails.csv")

class UserFromCSVTests(unittest.TestCase):
    

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

    def test_validate_usernames(self):
        TSC.UserItem.CSVImport._validate_import_line_or_throw(UserFromCSVTests.usernames[0])
        TSC.UserItem.CSVImport._validate_import_line_or_throw(UserFromCSVTests.usernames[1])
        TSC.UserItem.CSVImport._validate_import_line_or_throw(UserFromCSVTests.usernames[2])
        TSC.UserItem.CSVImport._validate_import_line_or_throw(UserFromCSVTests.usernames[3])
        TSC.UserItem.CSVImport._validate_import_line_or_throw(UserFromCSVTests.usernames[4])
        with self.assertRaises(AttributeError):
            TSC.UserItem.CSVImport._validate_import_line_or_throw(UserFromCSVTests.usernames[5])
        with self.assertRaises(AttributeError):
            TSC.UserItem.CSVImport._validate_import_line_or_throw(UserFromCSVTests.usernames[6])

    def test_evaluate_role(self):
        for line in UserFromCSVTests.role_inputs:
            actual = TSC.UserItem.CSVImport._evaluate_site_role(line[0], line[1], line[2])
            assert actual == line[3], line + [actual]

    def test_get_user_detail_empty_line(self):
        test_line = ""
        test_user = TSC.UserItem.CSVImport.create_user_from_line(test_line)
        assert test_user is None

    def test_get_user_detail_standard(self):
        test_line = "username, pword, fname, license, admin, pub, email"
        test_user: TSC.UserItem = TSC.UserItem.CSVImport.create_user_from_line(test_line)
        assert test_user.name == "username", test_user.name
        assert test_user.fullname == "fname", test_user.fullname
        assert test_user.site_role == "Unlicensed", test_user.site_role
        assert test_user.email == "email", test_user.email

    def test_get_user_details_only_username(self):
        test_line = "username"
        test_user: TSC.UserItem = TSC.UserItem.CSVImport.create_user_from_line(test_line)

    def test_populate_user_details_only_some(self):
        values = ["username", "", "", "creator", "admin"]
        data = TSC.UserItem()
        data.populate(values)

    def test_populate_user_details_all(self):
        values = UserFromCSVTests.valid_import_content[0]
        data = TSC.UserItem.CSVObject()
        data.populate([values])

    def test_validate_user_detail_standard(self):
        test_line = "username, pword, fname, creator, site, 1, email"
        UserCSVImport._validate_user_line_or_throw(test_line)

    # for file handling
    def _mock_file_content(self, content: List[str]) -> io.TextIOWrapper:
        # the empty string represents EOF
        # the tests run through the file twice, first to validate then to fetch
        mock = MagicMock(io.TextIOWrapper)
        content.append("")  # EOF
        mock.readline.side_effect = content
        mock.name = "file-mock"
        return mock

    def test_get_users_from_file_missing_elements(self):
        bad_content = [
            "username, pword, , yes, email",
            "username",
            "username, pword",
            "username, pword, , , yes, email",
        ]
        test_data = self._mock_file_content(bad_content)
        UserCSVImport.get_users_from_file(test_data)

    def test_validate_import_file(self):
        test_data = self._mock_file_content(UserFromCSVTests.valid_import_content)
        num_lines = TSC.UserItem.CSVImport.validate_file_for_import(test_data,  detailed=True)
        assert num_lines == 2, "Expected two lines to be parsed, got {}".format(num_lines)

    def test_validate_usernames_file(self):
        test_data = self._mock_file_content(UserFromCSVTests.usernames)
        n = TSC.UserItem.CSVImport.validate_file_for_import(test_data)
        assert n == 5, "Exactly 5 of the lines were valid, counted {}".format(n)

    def test_validate_usernames_file_strict(self):
        test_data = self._mock_file_content(UserFromCSVTests.usernames)
        with self.assertRaises(SystemExit):
            TSC.UserItem.CSVImport.validate_file_for_import(test_data,  strict=True)

    def test_get_usernames_from_file(self):
        test_data = self._mock_file_content(UserFromCSVTests.usernames)
        user_list = TSC.UserItem.CSVImport.get_users_from_file(test_data)
        assert user_list[0].name == "valid", user_list



class UserImportE2ETests(unittest.TestCase):
    def setUp(self) -> None:
        self.server = TSC.Server("http://test", False)

        # Fake signin
        self.server._site_id = "dad65087-b08b-4603-af4e-2887b8aafc67"
        self.server._auth_token = "j80k54ll2lfMZ0tv97mlPvvSCRyD0DOM"

        self.baseurl = self.server.users.baseurl

    # these tests are weird. The input file USERNAMES will be parsed and invalid lines put in 'failures'
    # Then we will send the valid lines to the server, and the response from that, ADD_XML, is our 'users'.
    # not covered: the server rejects one of our 'valid' lines
    def test_get_usernames_from_file(self):
        with open(ADD_XML, "rb") as f:
            response_xml = f.read().decode("utf-8")
        with requests_mock.mock() as m:
            m.post(self.server.users.baseurl, text=response_xml)
            user_list, failures = self.server.users.create_from_file(USERNAMES)
        assert failures != [], failures
        assert len(failures) == 2, failures
        assert user_list is not None, user_list
        assert user_list[0].name == "Cassie", user_list

    def test_get_users_from_file(self):
        with open(ADD_XML, "rb") as f:
            response_xml = f.read().decode("utf-8")
        with requests_mock.mock() as m:
            m.post(self.server.users.baseurl, text=response_xml)
            users, failures = self.server.users.create_from_file(USERS)
        assert failures != [], failures
        assert len(failures) == 1, failures
        assert users != [], users
        assert users[0].name == "Cassie", users

    def test_too_many_bad_lines(self):
        with open(ADD_XML, "rb") as f:
            response_xml = f.read().decode("utf-8")
        with requests_mock.mock() as m:
            m.post(self.server.users.baseurl, text=response_xml)

            with self.assertRaises(ValueError) as validator:
                users, failures = self.server.users.create_from_file(USERS_BAD)
                assert len(failures) == 4
            assert validator is not None
            self.assertEqual(
                str(validator.exception),
                "More than 3 lines have failed validation. Check the errors and fix your file.",
            )
