import unittest

import tableauserverclient as TSC


class WorkbookModelTests(unittest.TestCase):
    def test_invalid_show_tabs(self):
        workbook = TSC.WorkbookItem("10")
        with self.assertRaises(ValueError):
            workbook.show_tabs = "Hello"

        with self.assertRaises(ValueError):
            workbook.show_tabs = None
