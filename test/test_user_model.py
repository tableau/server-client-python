import logging
import unittest
from unittest.mock import *
from typing import List
import io

import pytest

import tableauserverclient as TSC


class UserModelTests(unittest.TestCase):
    def test_invalid_auth_setting(self):
        user = TSC.UserItem("me", TSC.UserItem.Roles.Publisher)
        with self.assertRaises(ValueError):
            user.auth_setting = "Hello"

    def test_invalid_site_role(self):
        user = TSC.UserItem("me", TSC.UserItem.Roles.Publisher)
        with self.assertRaises(ValueError):
            user.site_role = "Hello"


class UserDataTest(unittest.TestCase):
    logger = logging.getLogger("UserDataTest")

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
        TSC.UserItem.validate_username_or_throw(UserDataTest.usernames[0])
        TSC.UserItem.validate_username_or_throw(UserDataTest.usernames[1])
        TSC.UserItem.validate_username_or_throw(UserDataTest.usernames[2])
        TSC.UserItem.validate_username_or_throw(UserDataTest.usernames[3])
        TSC.UserItem.validate_username_or_throw(UserDataTest.usernames[4])
        with self.assertRaises(AttributeError):
            TSC.UserItem.validate_username_or_throw(UserDataTest.usernames[5])
        with self.assertRaises(AttributeError):
            TSC.UserItem.validate_username_or_throw(UserDataTest.usernames[6])

    def test_evaluate_role(self):
        for line in UserDataTest.role_inputs:
            actual = TSC.UserItem.CSVImport._evaluate_site_role(line[0], line[1], line[2])
            assert actual == line[3], line + [actual]

    def test_get_user_detail_empty_line(self):
        test_line = ""
        with self.assertRaises(AttributeError):
            test_user = TSC.UserItem.CSVImport.create_user_model_from_line(test_line, UserDataTest.logger)

    def test_get_user_detail_standard(self):
        test_line = ["username", "pword", "fname", "unlicensed", "no", "no", "email"]
        test_user: TSC.UserItem = TSC.UserItem.CSVImport.create_user_model_from_line(test_line, UserDataTest.logger)
        assert test_user.name == "username", test_user.name
        assert test_user.fullname == "fname", test_user.fullname
        assert test_user.site_role == "Unlicensed", test_user.site_role
        assert test_user.email == "email", test_user.email

    def test_get_user_details_only_username(self):
        test_line = ["username"]
        test_user: TSC.UserItem = TSC.UserItem.CSVImport.create_user_model_from_line(test_line, UserDataTest.logger)

    def test_populate_user_details_only_some(self):
        values = ["username", "", "", "creator", "site"]
        user = TSC.UserItem.CSVImport.create_user_model_from_line(values, UserDataTest.logger)
        assert user.name == "username"

    def test_validate_user_detail_standard(self):
        test_line = ["username", "pword", "fname", "creator", "site", "1", "email"]
        TSC.UserItem.CSVImport.create_user_model_from_line(test_line, UserDataTest.logger)

    def test_validate_import_file(self):
        users, valid, invalid = TSC.UserItem.CSVImport.process_file_for_import(
            "test/assets/data/users_import_2.csv", UserDataTest.logger
        )
        assert len(valid) == 2, "Expected two lines to be valid, got {}".format(len(valid))
        assert invalid is not None, invalid
        assert len(invalid) == 2, "Expected 2 failures, got {}".format(len(invalid))

    def test_validate_usernames_file(self):
        users, valid_lines, errors = TSC.UserItem.CSVImport.process_file_for_import(
            "test/assets/data/usernames.csv", UserDataTest.logger
        )
        assert len(users) == 5, "Expected 5 of the lines to be valid, counted {}".format(len(users))
