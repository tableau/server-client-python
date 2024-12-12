import unittest

import tableauserverclient as TSC


class ProjectModelTests(unittest.TestCase):
    def test_nullable_name(self):
        TSC.ProjectItem(None)
        TSC.ProjectItem("")
        project = TSC.ProjectItem("proj")
        project.name = None

    def test_invalid_content_permissions(self):
        project = TSC.ProjectItem("proj")
        with self.assertRaises(ValueError):
            project.content_permissions = "Hello"

    def test_parent_id(self):
        project = TSC.ProjectItem("proj")
        project.parent_id = "foo"
        self.assertEqual(project.parent_id, "foo")
