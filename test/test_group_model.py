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
