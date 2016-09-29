import unittest
import tableauserverclient as TSC


class WorkbookModelTests(unittest.TestCase):
    def test_invalid_project_id(self):
        self.assertRaises(ValueError, TSC.WorkbookItem, None)
        workbook = TSC.WorkbookItem("10")
        with self.assertRaises(ValueError):
            workbook.project_id = None

    def test_invalid_show_tabs(self):
        workbook = TSC.WorkbookItem("10")
        with self.assertRaises(ValueError):
            workbook.show_tabs = "Hello"

        with self.assertRaises(ValueError):
            workbook.show_tabs = None
