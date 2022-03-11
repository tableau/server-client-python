import unittest

import tableauserverclient as TSC


class GroupModelTests(unittest.TestCase):
    def test_invalid_name(self):
        self.assertRaises(ValueError, TSC.GroupItem, None)
        self.assertRaises(ValueError, TSC.GroupItem, "")
        group = TSC.GroupItem("grp")
        with self.assertRaises(ValueError):
            group.name = None

        with self.assertRaises(ValueError):
            group.name = ""

    def test_invalid_minimum_site_role(self):
        group = TSC.GroupItem("grp")
        with self.assertRaises(ValueError):
            group.minimum_site_role = "Captain"

    def test_invalid_license_mode(self):
        group = TSC.GroupItem("grp")
        with self.assertRaises(ValueError):
            group.license_mode = "off"
