import unittest
import tableauserverclient as TSC


class UserModelTests(unittest.TestCase):
    def test_invalid_name(self):
        self.assertRaises(ValueError, TSC.UserItem, None, TSC.UserItem.Roles.Publisher)
        self.assertRaises(ValueError, TSC.UserItem, "", TSC.UserItem.Roles.Publisher)
        user = TSC.UserItem("me", TSC.UserItem.Roles.Publisher)
        with self.assertRaises(ValueError):
            user.name = None

        with self.assertRaises(ValueError):
            user.name = ""

    def test_invalid_auth_setting(self):
        user = TSC.UserItem("me", TSC.UserItem.Roles.Publisher)
        with self.assertRaises(ValueError):
            user.auth_setting = "Hello"

    def test_invalid_site_role(self):
        user = TSC.UserItem("me", TSC.UserItem.Roles.Publisher)
        with self.assertRaises(ValueError):
            user.site_role = "Hello"
