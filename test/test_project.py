import os
import unittest

import requests_mock

import tableauserverclient as TSC
from tableauserverclient import GroupItem
from ._utils import read_xml_asset, asset

TEST_ASSET_DIR = os.path.join(os.path.dirname(__file__), "assets")

GET_XML = asset("project_get.xml")
UPDATE_XML = asset("project_update.xml")
SET_CONTENT_PERMISSIONS_XML = asset("project_content_permission.xml")
CREATE_XML = asset("project_create.xml")
POPULATE_PERMISSIONS_XML = "project_populate_permissions.xml"
POPULATE_WORKBOOK_DEFAULT_PERMISSIONS_XML = "project_populate_workbook_default_permissions.xml"
UPDATE_DATASOURCE_DEFAULT_PERMISSIONS_XML = "project_update_datasource_default_permissions.xml"


class ProjectTests(unittest.TestCase):
    def setUp(self) -> None:
        self.server = TSC.Server("http://test", False)

        # Fake signin
        self.server._site_id = "dad65087-b08b-4603-af4e-2887b8aafc67"
        self.server._auth_token = "j80k54ll2lfMZ0tv97mlPvvSCRyD0DOM"

        self.baseurl = self.server.projects.baseurl

    def test_get(self) -> None:
        with open(GET_XML, "rb") as f:
            response_xml = f.read().decode("utf-8")
        with requests_mock.mock() as m:
            m.get(self.baseurl, text=response_xml)
            all_projects, pagination_item = self.server.projects.get()

        self.assertEqual(3, pagination_item.total_available)
        self.assertEqual("ee8c6e70-43b6-11e6-af4f-f7b0d8e20760", all_projects[0].id)
        self.assertEqual("default", all_projects[0].name)
        self.assertEqual("The default project that was automatically created by Tableau.", all_projects[0].description)
        self.assertEqual("ManagedByOwner", all_projects[0].content_permissions)
        self.assertEqual(None, all_projects[0].parent_id)
        self.assertEqual("dd2239f6-ddf1-4107-981a-4cf94e415794", all_projects[0].owner_id)

        self.assertEqual("1d0304cd-3796-429f-b815-7258370b9b74", all_projects[1].id)
        self.assertEqual("Tableau", all_projects[1].name)
        self.assertEqual("ManagedByOwner", all_projects[1].content_permissions)
        self.assertEqual(None, all_projects[1].parent_id)
        self.assertEqual("2a47bbf8-8900-4ebb-b0a4-2723bd7c46c3", all_projects[1].owner_id)

        self.assertEqual("4cc52973-5e3a-4d1f-a4fb-5b5f73796edf", all_projects[2].id)
        self.assertEqual("Tableau > Child 1", all_projects[2].name)
        self.assertEqual("ManagedByOwner", all_projects[2].content_permissions)
        self.assertEqual("1d0304cd-3796-429f-b815-7258370b9b74", all_projects[2].parent_id)
        self.assertEqual("dd2239f6-ddf1-4107-981a-4cf94e415794", all_projects[2].owner_id)

    def test_get_before_signin(self) -> None:
        self.server._auth_token = None
        self.assertRaises(TSC.NotSignedInError, self.server.projects.get)

    def test_delete(self) -> None:
        with requests_mock.mock() as m:
            m.delete(self.baseurl + "/ee8c6e70-43b6-11e6-af4f-f7b0d8e20760", status_code=204)
            self.server.projects.delete("ee8c6e70-43b6-11e6-af4f-f7b0d8e20760")

    def test_delete_missing_id(self) -> None:
        self.assertRaises(ValueError, self.server.projects.delete, "")

    def test_update(self) -> None:
        with open(UPDATE_XML, "rb") as f:
            response_xml = f.read().decode("utf-8")
        with requests_mock.mock() as m:
            m.put(self.baseurl + "/1d0304cd-3796-429f-b815-7258370b9b74", text=response_xml)
            single_project = TSC.ProjectItem(
                name="Test Project",
                content_permissions="LockedToProject",
                description="Project created for testing",
                parent_id="9a8f2265-70f3-4494-96c5-e5949d7a1120",
            )
            single_project._id = "1d0304cd-3796-429f-b815-7258370b9b74"
            single_project = self.server.projects.update(single_project)

        self.assertEqual("1d0304cd-3796-429f-b815-7258370b9b74", single_project.id)
        self.assertEqual("Test Project", single_project.name)
        self.assertEqual("Project created for testing", single_project.description)
        self.assertEqual("LockedToProject", single_project.content_permissions)
        self.assertEqual("9a8f2265-70f3-4494-96c5-e5949d7a1120", single_project.parent_id)

    def test_content_permission_locked_to_project_without_nested(self) -> None:
        with open(SET_CONTENT_PERMISSIONS_XML, "rb") as f:
            response_xml = f.read().decode("utf-8")
        with requests_mock.mock() as m:
            m.put(self.baseurl + "/cb3759e5-da4a-4ade-b916-7e2b4ea7ec86", text=response_xml)
            project_item = TSC.ProjectItem(
                name="Test Project Permissions",
                content_permissions="LockedToProjectWithoutNested",
                description="Project created for testing",
                parent_id="7687bc43-a543-42f3-b86f-80caed03a813",
            )
            project_item._id = "cb3759e5-da4a-4ade-b916-7e2b4ea7ec86"
            project_item = self.server.projects.update(project_item)
        self.assertEqual("cb3759e5-da4a-4ade-b916-7e2b4ea7ec86", project_item.id)
        self.assertEqual("Test Project Permissions", project_item.name)
        self.assertEqual("Project created for testing", project_item.description)
        self.assertEqual("LockedToProjectWithoutNested", project_item.content_permissions)
        self.assertEqual("7687bc43-a543-42f3-b86f-80caed03a813", project_item.parent_id)

    def test_update_datasource_default_permission(self) -> None:
        response_xml = read_xml_asset(UPDATE_DATASOURCE_DEFAULT_PERMISSIONS_XML)
        with requests_mock.mock() as m:
            m.put(
                self.baseurl + "/b4065286-80f0-11ea-af1b-cb7191f48e45/default-permissions/datasources",
                text=response_xml,
            )
            project = TSC.ProjectItem("test-project")
            project._id = "b4065286-80f0-11ea-af1b-cb7191f48e45"

            group = TSC.GroupItem("test-group")
            group._id = "b4488bce-80f0-11ea-af1c-976d0c1dab39"

            capabilities = {TSC.Permission.Capability.ExportXml: TSC.Permission.Mode.Deny}

            rules = [TSC.PermissionsRule(grantee=GroupItem.as_reference(group._id), capabilities=capabilities)]

            new_rules = self.server.projects.update_datasource_default_permissions(project, rules)

        self.assertEqual("b4488bce-80f0-11ea-af1c-976d0c1dab39", new_rules[0].grantee.id)

        updated_capabilities = new_rules[0].capabilities
        self.assertEqual(4, len(updated_capabilities))
        self.assertEqual("Deny", updated_capabilities["ExportXml"])
        self.assertEqual("Allow", updated_capabilities["Read"])
        self.assertEqual("Allow", updated_capabilities["Write"])
        self.assertEqual("Allow", updated_capabilities["Connect"])

    def test_update_missing_id(self) -> None:
        single_project = TSC.ProjectItem("test")
        self.assertRaises(TSC.MissingRequiredFieldError, self.server.projects.update, single_project)

    def test_create(self) -> None:

        with open(CREATE_XML, "rb") as f:
            response_xml = f.read().decode("utf-8")
        with requests_mock.mock() as m:
            m.post(self.baseurl, text=response_xml)
            new_project = TSC.ProjectItem(name="Test Project", description="Project created for testing")
            new_project.content_permissions = "ManagedByOwner"
            new_project.parent_id = "9a8f2265-70f3-4494-96c5-e5949d7a1120"
            new_project = self.server.projects.create(new_project)

        self.assertEqual("ccbea03f-77c4-4209-8774-f67bc59c3cef", new_project.id)
        self.assertEqual("Test Project", new_project.name)
        self.assertEqual("Project created for testing", new_project.description)
        self.assertEqual("ManagedByOwner", new_project.content_permissions)
        self.assertEqual("9a8f2265-70f3-4494-96c5-e5949d7a1120", new_project.parent_id)

    def test_create_missing_name(self) -> None:
        self.assertRaises(ValueError, TSC.ProjectItem, "")

    def test_populate_permissions(self) -> None:
        with open(asset(POPULATE_PERMISSIONS_XML), "rb") as f:
            response_xml = f.read().decode("utf-8")
        with requests_mock.mock() as m:
            m.get(self.baseurl + "/0448d2ed-590d-4fa0-b272-a2a8a24555b5/permissions", text=response_xml)
            single_project = TSC.ProjectItem("Project3")
            single_project._id = "0448d2ed-590d-4fa0-b272-a2a8a24555b5"

            self.server.projects.populate_permissions(single_project)
            permissions = single_project.permissions

            self.assertEqual(permissions[0].grantee.tag_name, "group")
            self.assertEqual(permissions[0].grantee.id, "c8f2773a-c83a-11e8-8c8f-33e6d787b506")
            self.assertDictEqual(
                permissions[0].capabilities,
                {
                    TSC.Permission.Capability.Write: TSC.Permission.Mode.Allow,
                    TSC.Permission.Capability.Read: TSC.Permission.Mode.Allow,
                },
            )

    def test_populate_workbooks(self) -> None:
        response_xml = read_xml_asset(POPULATE_WORKBOOK_DEFAULT_PERMISSIONS_XML)
        with requests_mock.mock() as m:
            m.get(
                self.baseurl + "/9dbd2263-16b5-46e1-9c43-a76bb8ab65fb/default-permissions/workbooks", text=response_xml
            )
            single_project = TSC.ProjectItem("test", "1d0304cd-3796-429f-b815-7258370b9b74")
            single_project._owner_id = "dd2239f6-ddf1-4107-981a-4cf94e415794"
            single_project._id = "9dbd2263-16b5-46e1-9c43-a76bb8ab65fb"

            self.server.projects.populate_workbook_default_permissions(single_project)
            permissions = single_project.default_workbook_permissions

        rule1 = permissions.pop()

        self.assertEqual("c8f2773a-c83a-11e8-8c8f-33e6d787b506", rule1.grantee.id)
        self.assertEqual("group", rule1.grantee.tag_name)
        self.assertDictEqual(
            rule1.capabilities,
            {
                TSC.Permission.Capability.Write: TSC.Permission.Mode.Allow,
                TSC.Permission.Capability.Read: TSC.Permission.Mode.Allow,
                TSC.Permission.Capability.Filter: TSC.Permission.Mode.Allow,
                TSC.Permission.Capability.ChangePermissions: TSC.Permission.Mode.Allow,
                TSC.Permission.Capability.WebAuthoring: TSC.Permission.Mode.Allow,
                TSC.Permission.Capability.ExportData: TSC.Permission.Mode.Allow,
                TSC.Permission.Capability.ExportXml: TSC.Permission.Mode.Allow,
                TSC.Permission.Capability.ExportImage: TSC.Permission.Mode.Allow,
                TSC.Permission.Capability.Delete: TSC.Permission.Mode.Deny,
                TSC.Permission.Capability.ShareView: TSC.Permission.Mode.Allow,
                TSC.Permission.Capability.ViewUnderlyingData: TSC.Permission.Mode.Deny,
                TSC.Permission.Capability.ViewComments: TSC.Permission.Mode.Allow,
                TSC.Permission.Capability.AddComment: TSC.Permission.Mode.Allow,
                TSC.Permission.Capability.ChangeHierarchy: TSC.Permission.Mode.Allow,
            },
        )

    def test_delete_permission(self) -> None:
        with open(asset(POPULATE_PERMISSIONS_XML), "rb") as f:
            response_xml = f.read().decode("utf-8")
        with requests_mock.mock() as m:
            m.get(self.baseurl + "/0448d2ed-590d-4fa0-b272-a2a8a24555b5/permissions", text=response_xml)

            single_group = TSC.GroupItem("Group1")
            single_group._id = "c8f2773a-c83a-11e8-8c8f-33e6d787b506"

            single_project = TSC.ProjectItem("Project3")
            single_project._id = "0448d2ed-590d-4fa0-b272-a2a8a24555b5"

            self.server.projects.populate_permissions(single_project)
            permissions = single_project.permissions

            capabilities = {}

            for permission in permissions:
                if permission.grantee.tag_name == "group":
                    if permission.grantee.id == single_group._id:
                        capabilities = permission.capabilities

            rules = TSC.PermissionsRule(grantee=GroupItem.as_reference(single_group._id), capabilities=capabilities)

            endpoint = "{}/permissions/groups/{}".format(single_project._id, single_group._id)
            m.delete("{}/{}/Read/Allow".format(self.baseurl, endpoint), status_code=204)
            m.delete("{}/{}/Write/Allow".format(self.baseurl, endpoint), status_code=204)
            self.server.projects.delete_permission(item=single_project, rules=rules)

    def test_delete_workbook_default_permission(self) -> None:
        with open(asset(POPULATE_WORKBOOK_DEFAULT_PERMISSIONS_XML), "rb") as f:
            response_xml = f.read().decode("utf-8")

        with requests_mock.mock() as m:
            m.get(
                self.baseurl + "/9dbd2263-16b5-46e1-9c43-a76bb8ab65fb/default-permissions/workbooks", text=response_xml
            )

            single_group = TSC.GroupItem("Group1")
            single_group._id = "c8f2773a-c83a-11e8-8c8f-33e6d787b506"

            single_project = TSC.ProjectItem("test", "1d0304cd-3796-429f-b815-7258370b9b74")
            single_project._owner_id = "dd2239f6-ddf1-4107-981a-4cf94e415794"
            single_project._id = "9dbd2263-16b5-46e1-9c43-a76bb8ab65fb"

            self.server.projects.populate_workbook_default_permissions(single_project)
            permissions = single_project.default_workbook_permissions

            capabilities = {
                # View
                TSC.Permission.Capability.Read: TSC.Permission.Mode.Allow,
                TSC.Permission.Capability.ExportImage: TSC.Permission.Mode.Allow,
                TSC.Permission.Capability.ExportData: TSC.Permission.Mode.Allow,
                TSC.Permission.Capability.ViewComments: TSC.Permission.Mode.Allow,
                TSC.Permission.Capability.AddComment: TSC.Permission.Mode.Allow,
                # Interact/Edit
                TSC.Permission.Capability.Filter: TSC.Permission.Mode.Allow,
                TSC.Permission.Capability.ViewUnderlyingData: TSC.Permission.Mode.Deny,
                TSC.Permission.Capability.ShareView: TSC.Permission.Mode.Allow,
                TSC.Permission.Capability.WebAuthoring: TSC.Permission.Mode.Allow,
                # Edit
                TSC.Permission.Capability.Write: TSC.Permission.Mode.Allow,
                TSC.Permission.Capability.ExportXml: TSC.Permission.Mode.Allow,
                TSC.Permission.Capability.ChangeHierarchy: TSC.Permission.Mode.Allow,
                TSC.Permission.Capability.Delete: TSC.Permission.Mode.Deny,
                TSC.Permission.Capability.ChangePermissions: TSC.Permission.Mode.Allow,
            }

            rules = TSC.PermissionsRule(grantee=GroupItem.as_reference(single_group._id), capabilities=capabilities)

            endpoint = "{}/default-permissions/workbooks/groups/{}".format(single_project._id, single_group._id)
            m.delete("{}/{}/Read/Allow".format(self.baseurl, endpoint), status_code=204)
            m.delete("{}/{}/ExportImage/Allow".format(self.baseurl, endpoint), status_code=204)
            m.delete("{}/{}/ExportData/Allow".format(self.baseurl, endpoint), status_code=204)
            m.delete("{}/{}/ViewComments/Allow".format(self.baseurl, endpoint), status_code=204)
            m.delete("{}/{}/AddComment/Allow".format(self.baseurl, endpoint), status_code=204)
            m.delete("{}/{}/Filter/Allow".format(self.baseurl, endpoint), status_code=204)
            m.delete("{}/{}/ViewUnderlyingData/Deny".format(self.baseurl, endpoint), status_code=204)
            m.delete("{}/{}/ShareView/Allow".format(self.baseurl, endpoint), status_code=204)
            m.delete("{}/{}/WebAuthoring/Allow".format(self.baseurl, endpoint), status_code=204)
            m.delete("{}/{}/Write/Allow".format(self.baseurl, endpoint), status_code=204)
            m.delete("{}/{}/ExportXml/Allow".format(self.baseurl, endpoint), status_code=204)
            m.delete("{}/{}/ChangeHierarchy/Allow".format(self.baseurl, endpoint), status_code=204)
            m.delete("{}/{}/Delete/Deny".format(self.baseurl, endpoint), status_code=204)
            m.delete("{}/{}/ChangePermissions/Allow".format(self.baseurl, endpoint), status_code=204)
            self.server.projects.delete_workbook_default_permissions(item=single_project, rule=rules)
