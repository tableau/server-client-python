from pathlib import Path

import pytest
import requests_mock

import tableauserverclient as TSC
from tableauserverclient import GroupItem

TEST_ASSET_DIR = Path(__file__).parent / "assets"

GET_XML = TEST_ASSET_DIR / "project_get.xml"
GET_XML_ALL_FIELDS = TEST_ASSET_DIR / "project_get_all_fields.xml"
UPDATE_XML = TEST_ASSET_DIR / "project_update.xml"
SET_CONTENT_PERMISSIONS_XML = TEST_ASSET_DIR / "project_content_permission.xml"
CREATE_XML = TEST_ASSET_DIR / "project_create.xml"
POPULATE_PERMISSIONS_XML = TEST_ASSET_DIR / "project_populate_permissions.xml"
POPULATE_WORKBOOK_DEFAULT_PERMISSIONS_XML = TEST_ASSET_DIR / "project_populate_workbook_default_permissions.xml"
UPDATE_DATASOURCE_DEFAULT_PERMISSIONS_XML = TEST_ASSET_DIR / "project_update_datasource_default_permissions.xml"
POPULATE_VIRTUALCONNECTION_DEFAULT_PERMISSIONS_XML = (
    TEST_ASSET_DIR / "project_populate_virtualconnection_default_permissions.xml"
)
UPDATE_VIRTUALCONNECTION_DEFAULT_PERMISSIONS_XML = (
    TEST_ASSET_DIR / "project_update_virtualconnection_default_permissions.xml"
)


@pytest.fixture(scope="function")
def server():
    """Fixture to create a TSC.Server instance for testing."""
    server = TSC.Server("http://test", False)

    # Fake signin
    server._site_id = "dad65087-b08b-4603-af4e-2887b8aafc67"
    server._auth_token = "j80k54ll2lfMZ0tv97mlPvvSCRyD0DOM"

    return server


def test_get(server: TSC.Server) -> None:
    response_xml = GET_XML.read_text()
    with requests_mock.mock() as m:
        m.get(server.projects.baseurl, text=response_xml)
        all_projects, pagination_item = server.projects.get()

    assert 3 == pagination_item.total_available
    assert "ee8c6e70-43b6-11e6-af4f-f7b0d8e20760" == all_projects[0].id
    assert "default" == all_projects[0].name
    assert "The default project that was automatically created by Tableau." == all_projects[0].description
    assert "ManagedByOwner" == all_projects[0].content_permissions
    assert None == all_projects[0].parent_id
    assert "dd2239f6-ddf1-4107-981a-4cf94e415794" == all_projects[0].owner_id

    assert "1d0304cd-3796-429f-b815-7258370b9b74" == all_projects[1].id
    assert "Tableau" == all_projects[1].name
    assert "ManagedByOwner" == all_projects[1].content_permissions
    assert None == all_projects[1].parent_id
    assert "2a47bbf8-8900-4ebb-b0a4-2723bd7c46c3" == all_projects[1].owner_id

    assert "4cc52973-5e3a-4d1f-a4fb-5b5f73796edf" == all_projects[2].id
    assert "Tableau > Child 1" == all_projects[2].name
    assert "ManagedByOwner" == all_projects[2].content_permissions
    assert "1d0304cd-3796-429f-b815-7258370b9b74" == all_projects[2].parent_id
    assert "dd2239f6-ddf1-4107-981a-4cf94e415794" == all_projects[2].owner_id


def test_get_before_signin(server: TSC.Server) -> None:
    server._auth_token = None
    with pytest.raises(TSC.NotSignedInError):
        server.projects.get()


def test_delete(server: TSC.Server) -> None:
    with requests_mock.mock() as m:
        m.delete(server.projects.baseurl + "/ee8c6e70-43b6-11e6-af4f-f7b0d8e20760", status_code=204)
        server.projects.delete("ee8c6e70-43b6-11e6-af4f-f7b0d8e20760")


def test_delete_missing_id(server: TSC.Server) -> None:
    with pytest.raises(ValueError):
        server.projects.delete("")

def test_get_by_id(server: TSC.Server) -> None:
    response_xml = UPDATE_XML.read_text()
    with requests_mock.mock() as m:
        m.put(server.projects.baseurl + "/1d0304cd-3796-429f-b815-7258370b9b74", text=response_xml)
        project = server.projects.get_by_id("1d0304cd-3796-429f-b815-7258370b9b74")
    assert "1d0304cd-3796-429f-b815-7258370b9b74" == project.id
    assert "Test Project" == project.name
    assert "Project created for testing" == project.description
    assert "LockedToProject" == project.content_permissions
    assert "9a8f2265-70f3-4494-96c5-e5949d7a1120" == project.parent_id
    assert "dd2239f6-ddf1-4107-981a-4cf94e415794" == project.owner_id
    assert "LockedToProject" == project.content_permissions


def test_get_by_id_missing_id(server: TSC.Server) -> None:
    with pytest.raises(ValueError):
        server.projects.get_by_id("")


def test_update(server: TSC.Server) -> None:
    response_xml = UPDATE_XML.read_text()
    with requests_mock.mock() as m:
        m.put(server.projects.baseurl + "/1d0304cd-3796-429f-b815-7258370b9b74", text=response_xml)
        single_project = TSC.ProjectItem(
            name="Test Project",
            content_permissions="LockedToProject",
            description="Project created for testing",
            parent_id="9a8f2265-70f3-4494-96c5-e5949d7a1120",
        )
        single_project._id = "1d0304cd-3796-429f-b815-7258370b9b74"
        single_project.owner_id = "dd2239f6-ddf1-4107-981a-4cf94e415794"
        single_project = server.projects.update(single_project)

    assert "1d0304cd-3796-429f-b815-7258370b9b74" == single_project.id
    assert "Test Project" == single_project.name
    assert "Project created for testing" == single_project.description
    assert "LockedToProject" == single_project.content_permissions
    assert "9a8f2265-70f3-4494-96c5-e5949d7a1120" == single_project.parent_id
    assert "dd2239f6-ddf1-4107-981a-4cf94e415794" == single_project.owner_id


def test_content_permission_locked_to_project_without_nested(server: TSC.Server) -> None:
    response_xml = SET_CONTENT_PERMISSIONS_XML.read_text()
    with requests_mock.mock() as m:
        m.put(server.projects.baseurl + "/cb3759e5-da4a-4ade-b916-7e2b4ea7ec86", text=response_xml)
        project_item = TSC.ProjectItem(
            name="Test Project Permissions",
            content_permissions="LockedToProjectWithoutNested",
            description="Project created for testing",
            parent_id="7687bc43-a543-42f3-b86f-80caed03a813",
        )
        project_item._id = "cb3759e5-da4a-4ade-b916-7e2b4ea7ec86"
        project_item = server.projects.update(project_item)
    assert "cb3759e5-da4a-4ade-b916-7e2b4ea7ec86" == project_item.id
    assert "Test Project Permissions" == project_item.name
    assert "Project created for testing" == project_item.description
    assert "LockedToProjectWithoutNested" == project_item.content_permissions
    assert "7687bc43-a543-42f3-b86f-80caed03a813" == project_item.parent_id


def test_update_datasource_default_permission(server: TSC.Server) -> None:
    response_xml = UPDATE_DATASOURCE_DEFAULT_PERMISSIONS_XML.read_text()
    with requests_mock.mock() as m:
        m.put(
            server.projects.baseurl + "/b4065286-80f0-11ea-af1b-cb7191f48e45/default-permissions/datasources",
            text=response_xml,
        )
        project = TSC.ProjectItem("test-project")
        project._id = "b4065286-80f0-11ea-af1b-cb7191f48e45"

        group = TSC.GroupItem("test-group")
        group._id = "b4488bce-80f0-11ea-af1c-976d0c1dab39"

        capabilities = {TSC.Permission.Capability.ExportXml: TSC.Permission.Mode.Deny}

        rules = [TSC.PermissionsRule(grantee=GroupItem.as_reference(group._id), capabilities=capabilities)]

        new_rules = server.projects.update_datasource_default_permissions(project, rules)

    assert "b4488bce-80f0-11ea-af1c-976d0c1dab39" == new_rules[0].grantee.id

    updated_capabilities = new_rules[0].capabilities
    assert 4 == len(updated_capabilities)
    assert "Deny" == updated_capabilities["ExportXml"]
    assert "Allow" == updated_capabilities["Read"]
    assert "Allow" == updated_capabilities["Write"]
    assert "Allow" == updated_capabilities["Connect"]


def test_update_missing_id(server: TSC.Server) -> None:
    single_project = TSC.ProjectItem("test")
    with pytest.raises(TSC.MissingRequiredFieldError):
        server.projects.update(single_project)


def test_create(server: TSC.Server) -> None:
    response_xml = CREATE_XML.read_text()
    with requests_mock.mock() as m:
        m.post(server.projects.baseurl, text=response_xml)
        new_project = TSC.ProjectItem(name="Test Project", description="Project created for testing")
        new_project.content_permissions = "ManagedByOwner"
        new_project.parent_id = "9a8f2265-70f3-4494-96c5-e5949d7a1120"
        new_project = server.projects.create(new_project)

    assert "ccbea03f-77c4-4209-8774-f67bc59c3cef" == new_project.id
    assert "Test Project" == new_project.name
    assert "Project created for testing" == new_project.description
    assert "ManagedByOwner" == new_project.content_permissions
    assert "9a8f2265-70f3-4494-96c5-e5949d7a1120" == new_project.parent_id


def test_create_missing_name() -> None:
    TSC.ProjectItem()


def test_populate_permissions(server: TSC.Server) -> None:
    response_xml = POPULATE_PERMISSIONS_XML.read_text()
    with requests_mock.mock() as m:
        m.get(server.projects.baseurl + "/0448d2ed-590d-4fa0-b272-a2a8a24555b5/permissions", text=response_xml)
        single_project = TSC.ProjectItem("Project3")
        single_project._id = "0448d2ed-590d-4fa0-b272-a2a8a24555b5"

        server.projects.populate_permissions(single_project)
        permissions = single_project.permissions

        assert permissions[0].grantee.tag_name == "group"
        assert permissions[0].grantee.id == "c8f2773a-c83a-11e8-8c8f-33e6d787b506"
        assert permissions[0].capabilities == {
            TSC.Permission.Capability.Write: TSC.Permission.Mode.Allow,
            TSC.Permission.Capability.Read: TSC.Permission.Mode.Allow,
        }


def test_populate_workbooks(server: TSC.Server) -> None:
    response_xml = POPULATE_WORKBOOK_DEFAULT_PERMISSIONS_XML.read_text()
    with requests_mock.mock() as m:
        m.get(
            server.projects.baseurl + "/9dbd2263-16b5-46e1-9c43-a76bb8ab65fb/default-permissions/workbooks",
            text=response_xml,
        )
        single_project = TSC.ProjectItem("test", "1d0304cd-3796-429f-b815-7258370b9b74")
        single_project.owner_id = "dd2239f6-ddf1-4107-981a-4cf94e415794"
        single_project._id = "9dbd2263-16b5-46e1-9c43-a76bb8ab65fb"

        server.projects.populate_workbook_default_permissions(single_project)
        permissions = single_project.default_workbook_permissions

    rule1 = permissions.pop()

    assert "c8f2773a-c83a-11e8-8c8f-33e6d787b506" == rule1.grantee.id
    assert "group" == rule1.grantee.tag_name
    assert rule1.capabilities == {
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
    }


def test_delete_permission(server: TSC.Server) -> None:
    response_xml = POPULATE_PERMISSIONS_XML.read_text()
    with requests_mock.mock() as m:
        m.get(server.projects.baseurl + "/0448d2ed-590d-4fa0-b272-a2a8a24555b5/permissions", text=response_xml)

        single_group = TSC.GroupItem("Group1")
        single_group._id = "c8f2773a-c83a-11e8-8c8f-33e6d787b506"

        single_project = TSC.ProjectItem("Project3")
        single_project._id = "0448d2ed-590d-4fa0-b272-a2a8a24555b5"

        server.projects.populate_permissions(single_project)
        permissions = single_project.permissions

        capabilities = {}

        for permission in permissions:
            if permission.grantee.tag_name == "group":
                if permission.grantee.id == single_group._id:
                    capabilities = permission.capabilities

        rules = TSC.PermissionsRule(grantee=GroupItem.as_reference(single_group._id), capabilities=capabilities)

        endpoint = f"{single_project._id}/permissions/groups/{single_group._id}"
        m.delete(f"{server.projects.baseurl}/{endpoint}/Read/Allow", status_code=204)
        m.delete(f"{server.projects.baseurl}/{endpoint}/Write/Allow", status_code=204)
        server.projects.delete_permission(item=single_project, rules=rules)


def test_delete_workbook_default_permission(server: TSC.Server) -> None:
    response_xml = POPULATE_WORKBOOK_DEFAULT_PERMISSIONS_XML.read_text()

    with requests_mock.mock() as m:
        m.get(
            server.projects.baseurl + "/9dbd2263-16b5-46e1-9c43-a76bb8ab65fb/default-permissions/workbooks",
            text=response_xml,
        )

        single_group = TSC.GroupItem("Group1")
        single_group._id = "c8f2773a-c83a-11e8-8c8f-33e6d787b506"

        single_project = TSC.ProjectItem("test", "1d0304cd-3796-429f-b815-7258370b9b74")
        single_project._owner_id = "dd2239f6-ddf1-4107-981a-4cf94e415794"
        single_project._id = "9dbd2263-16b5-46e1-9c43-a76bb8ab65fb"

        server.projects.populate_workbook_default_permissions(single_project)
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

        endpoint = f"{single_project._id}/default-permissions/workbooks/groups/{single_group._id}"
        m.delete(f"{server.projects.baseurl}/{endpoint}/Read/Allow", status_code=204)
        m.delete(f"{server.projects.baseurl}/{endpoint}/ExportImage/Allow", status_code=204)
        m.delete(f"{server.projects.baseurl}/{endpoint}/ExportData/Allow", status_code=204)
        m.delete(f"{server.projects.baseurl}/{endpoint}/ViewComments/Allow", status_code=204)
        m.delete(f"{server.projects.baseurl}/{endpoint}/AddComment/Allow", status_code=204)
        m.delete(f"{server.projects.baseurl}/{endpoint}/Filter/Allow", status_code=204)
        m.delete(f"{server.projects.baseurl}/{endpoint}/ViewUnderlyingData/Deny", status_code=204)
        m.delete(f"{server.projects.baseurl}/{endpoint}/ShareView/Allow", status_code=204)
        m.delete(f"{server.projects.baseurl}/{endpoint}/WebAuthoring/Allow", status_code=204)
        m.delete(f"{server.projects.baseurl}/{endpoint}/Write/Allow", status_code=204)
        m.delete(f"{server.projects.baseurl}/{endpoint}/ExportXml/Allow", status_code=204)
        m.delete(f"{server.projects.baseurl}/{endpoint}/ChangeHierarchy/Allow", status_code=204)
        m.delete(f"{server.projects.baseurl}/{endpoint}/Delete/Deny", status_code=204)
        m.delete(f"{server.projects.baseurl}/{endpoint}/ChangePermissions/Allow", status_code=204)
        server.projects.delete_workbook_default_permissions(item=single_project, rule=rules)


def test_populate_virtualconnection_default_permissions(server: TSC.Server) -> None:
    response_xml = POPULATE_VIRTUALCONNECTION_DEFAULT_PERMISSIONS_XML.read_text()

    server.version = "3.23"
    base_url = server.projects.baseurl

    with requests_mock.mock() as m:
        m.get(
            base_url + "/9dbd2263-16b5-46e1-9c43-a76bb8ab65fb/default-permissions/virtualConnections",
            text=response_xml,
        )
        project = TSC.ProjectItem("test", "1d0304cd-3796-429f-b815-7258370b9b74")
        project._id = "9dbd2263-16b5-46e1-9c43-a76bb8ab65fb"

        server.projects.populate_virtualconnection_default_permissions(project)
        permissions = project.default_virtualconnection_permissions

    rule = permissions.pop()

    assert "c8f2773a-c83a-11e8-8c8f-33e6d787b506" == rule.grantee.id
    assert "group" == rule.grantee.tag_name
    assert rule.capabilities == {
        TSC.Permission.Capability.Read: TSC.Permission.Mode.Allow,
        TSC.Permission.Capability.Connect: TSC.Permission.Mode.Allow,
        TSC.Permission.Capability.ChangeHierarchy: TSC.Permission.Mode.Deny,
        TSC.Permission.Capability.Delete: TSC.Permission.Mode.Deny,
        TSC.Permission.Capability.ChangePermissions: TSC.Permission.Mode.Deny,
    }


def test_update_virtualconnection_default_permissions(server: TSC.Server) -> None:
    response_xml = UPDATE_VIRTUALCONNECTION_DEFAULT_PERMISSIONS_XML.read_text()

    server.version = "3.23"
    base_url = server.projects.baseurl

    with requests_mock.mock() as m:
        m.put(
            base_url + "/9dbd2263-16b5-46e1-9c43-a76bb8ab65fb/default-permissions/virtualConnections",
            text=response_xml,
        )
        project = TSC.ProjectItem("test", "1d0304cd-3796-429f-b815-7258370b9b74")
        project._id = "9dbd2263-16b5-46e1-9c43-a76bb8ab65fb"

        group = TSC.GroupItem("test-group")
        group._id = "c8f2773a-c83a-11e8-8c8f-33e6d787b506"

        capabilities = {
            TSC.Permission.Capability.ChangeHierarchy: TSC.Permission.Mode.Allow,
            TSC.Permission.Capability.Delete: TSC.Permission.Mode.Allow,
            TSC.Permission.Capability.Read: TSC.Permission.Mode.Deny,
        }

        assert group.id is not None
        rules = [TSC.PermissionsRule(GroupItem.as_reference(group.id), capabilities)]
        new_rules = server.projects.update_virtualconnection_default_permissions(project, rules)

    rule = new_rules.pop()

    assert group.id == rule.grantee.id
    assert "group" == rule.grantee.tag_name
    assert rule.capabilities == {
        TSC.Permission.Capability.ChangeHierarchy: TSC.Permission.Mode.Allow,
        TSC.Permission.Capability.Delete: TSC.Permission.Mode.Allow,
        TSC.Permission.Capability.Read: TSC.Permission.Mode.Deny,
    }


def test_delete_virtualconnection_default_permimssions(server: TSC.Server) -> None:
    response_xml = POPULATE_VIRTUALCONNECTION_DEFAULT_PERMISSIONS_XML.read_text()

    server.version = "3.23"
    base_url = server.projects.baseurl

    with requests_mock.mock() as m:
        m.get(
            base_url + "/9dbd2263-16b5-46e1-9c43-a76bb8ab65fb/default-permissions/virtualConnections",
            text=response_xml,
        )

        project = TSC.ProjectItem("test", "1d0304cd-3796-429f-b815-7258370b9b74")
        project._id = "9dbd2263-16b5-46e1-9c43-a76bb8ab65fb"

        group = TSC.GroupItem("test-group")
        group._id = "c8f2773a-c83a-11e8-8c8f-33e6d787b506"

        server.projects.populate_virtualconnection_default_permissions(project)
        permissions = project.default_virtualconnection_permissions

        del_caps = {
            TSC.Permission.Capability.ChangeHierarchy: TSC.Permission.Mode.Deny,
            TSC.Permission.Capability.Connect: TSC.Permission.Mode.Allow,
        }

        assert group.id is not None
        rule = TSC.PermissionsRule(GroupItem.as_reference(group.id), del_caps)

        endpoint = f"{project.id}/default-permissions/virtualConnections/groups/{group.id}"
        m.delete(f"{base_url}/{endpoint}/ChangeHierarchy/Deny", status_code=204)
        m.delete(f"{base_url}/{endpoint}/Connect/Allow", status_code=204)

        server.projects.delete_virtualconnection_default_permissions(project, rule)


def test_get_all_fields(server: TSC.Server) -> None:
    server.version = "3.23"
    base_url = server.projects.baseurl
    response_xml = GET_XML_ALL_FIELDS.read_text()

    ro = TSC.RequestOptions()
    ro.all_fields = True

    with requests_mock.mock() as m:
        m.get(f"{base_url}?fields=_all_", text=response_xml)
        all_projects, pagination_item = server.projects.get(req_options=ro)

    assert pagination_item.total_available == 3
    assert len(all_projects) == 1
    project: TSC.ProjectItem = all_projects[0]
    assert isinstance(project, TSC.ProjectItem)
    assert project.id == "ee8c6e70-43b6-11e6-af4f-f7b0d8e20760"
    assert project.name == "Samples"
    assert project.description == "This project includes automatically uploaded samples."
    assert project.top_level_project is True
    assert project.content_permissions == "ManagedByOwner"
    assert project.parent_id is None
    assert project.writeable is True
