import unittest
import tableauserverclient as TSC


class ProjectModelTests(unittest.TestCase):
    def test_invalid_name(self):
        self.assertRaises(ValueError, TSC.ProjectItem, None)
        self.assertRaises(ValueError, TSC.ProjectItem, "")
        project = TSC.ProjectItem("proj")
        with self.assertRaises(ValueError):
            project.name = None

        with self.assertRaises(ValueError):
            project.name = ""

    def test_invalid_content_permissions(self):
        project = TSC.ProjectItem("proj")
        with self.assertRaises(ValueError):
            project.content_permissions = "Hello"
