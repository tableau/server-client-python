from itertools import product
from pathlib import Path

from defusedxml import ElementTree as ET
import pytest
import requests_mock

import tableauserverclient as TSC
from tableauserverclient.server.request_factory import RequestFactory

from . import _utils

TEST_ASSET_DIR = Path(__file__).parent / "assets"

GET_XML = TEST_ASSET_DIR / "site_get.xml"
GET_BY_ID_XML = TEST_ASSET_DIR / "site_get_by_id.xml"
GET_BY_NAME_XML = TEST_ASSET_DIR / "site_get_by_name.xml"
UPDATE_XML = TEST_ASSET_DIR / "site_update.xml"
CREATE_XML = TEST_ASSET_DIR / "site_create.xml"
SITE_AUTH_CONFIG_XML = TEST_ASSET_DIR / "site_auth_configurations.xml"


@pytest.fixture(scope="function")
def server():
    """Fixture to create a TSC.Server instance for testing."""
    server = TSC.Server("http://test", False)

    # Fake signin
    server._site_id = "0626857c-1def-4503-a7d8-7907c3ff9d9f"
    server._auth_token = "j80k54ll2lfMZ0tv97mlPvvSCRyD0DOM"
    server.version = "3.10"

    return server


def test_get(server: TSC.Server) -> None:
    response_xml = GET_XML.read_text()
    with requests_mock.mock() as m:
        m.get(server.sites.baseurl, text=response_xml)
        all_sites, pagination_item = server.sites.get()

    assert 2 == pagination_item.total_available
    assert "dad65087-b08b-4603-af4e-2887b8aafc67" == all_sites[0].id
    assert "Active" == all_sites[0].state
    assert "Default" == all_sites[0].name
    assert "ContentOnly" == all_sites[0].admin_mode
    assert all_sites[0].revision_history_enabled is False
    assert all_sites[0].subscribe_others_enabled is True
    assert 25 == all_sites[0].revision_limit
    assert None == all_sites[0].num_users
    assert None == all_sites[0].storage
    assert all_sites[0].cataloging_enabled is True
    assert all_sites[0].editing_flows_enabled is False
    assert all_sites[0].scheduling_flows_enabled is False
    assert all_sites[0].allow_subscription_attachments is True
    assert "6b7179ba-b82b-4f0f-91ed-812074ac5da6" == all_sites[1].id
    assert "Active" == all_sites[1].state
    assert "Samples" == all_sites[1].name
    assert "ContentOnly" == all_sites[1].admin_mode
    assert all_sites[1].revision_history_enabled is False
    assert all_sites[1].subscribe_others_enabled is True
    assert all_sites[1].guest_access_enabled is False
    assert all_sites[1].cache_warmup_enabled is True
    assert all_sites[1].commenting_enabled is True
    assert all_sites[1].cache_warmup_enabled is True
    assert all_sites[1].request_access_enabled is False
    assert all_sites[1].run_now_enabled is True
    assert 1 == all_sites[1].tier_explorer_capacity
    assert 2 == all_sites[1].tier_creator_capacity
    assert 1 == all_sites[1].tier_viewer_capacity
    assert all_sites[1].flows_enabled is False
    assert None == all_sites[1].data_acceleration_mode


def test_get_before_signin(server: TSC.Server) -> None:
    server._auth_token = None
    with pytest.raises(TSC.NotSignedInError):
        server.sites.get()


def test_get_by_id(server: TSC.Server) -> None:
    response_xml = GET_BY_ID_XML.read_text()
    with requests_mock.mock() as m:
        m.get(server.sites.baseurl + "/" + server.site_id, text=response_xml)
        single_site = server.sites.get_by_id(server.site_id)

    assert server.site_id == single_site.id
    assert "Active" == single_site.state
    assert "Default" == single_site.name
    assert "ContentOnly" == single_site.admin_mode
    assert single_site.revision_history_enabled is False
    assert single_site.subscribe_others_enabled is True
    assert single_site.disable_subscriptions is False
    assert single_site.data_alerts_enabled is False
    assert single_site.commenting_mentions_enabled is False
    assert single_site.catalog_obfuscation_enabled is True


def test_get_by_id_missing_id(server: TSC.Server) -> None:
    with pytest.raises(ValueError):
        server.sites.get_by_id("")


def test_get_by_name(server: TSC.Server) -> None:
    response_xml = GET_BY_NAME_XML.read_text()
    with requests_mock.mock() as m:
        m.get(server.sites.baseurl + "/testsite?key=name", text=response_xml)
        single_site = server.sites.get_by_name("testsite")

    assert server.site_id == single_site.id
    assert "Active" == single_site.state
    assert "testsite" == single_site.name
    assert "ContentOnly" == single_site.admin_mode
    assert single_site.revision_history_enabled is False
    assert single_site.subscribe_others_enabled is True
    assert single_site.disable_subscriptions is False


def test_get_by_name_missing_name(server: TSC.Server) -> None:
    with pytest.raises(ValueError):
        server.sites.get_by_name("")


@pytest.mark.filterwarnings("ignore:Tiered license level is set")
@pytest.mark.filterwarnings("ignore:FlowsEnabled has been removed")
def test_update(server: TSC.Server) -> None:
    response_xml = UPDATE_XML.read_text()
    with requests_mock.mock() as m:
        m.put(server.sites.baseurl + "/" + server.site_id, text=response_xml)
        single_site = TSC.SiteItem(
            name="Tableau",
            content_url="tableau",
            admin_mode=TSC.SiteItem.AdminMode.ContentAndUsers,
            user_quota=15,
            storage_quota=1000,
            disable_subscriptions=True,
            revision_history_enabled=False,
            data_acceleration_mode="disable",
            flow_auto_save_enabled=True,
            web_extraction_enabled=False,
            metrics_content_type_enabled=True,
            notify_site_admins_on_throttle=False,
            authoring_enabled=True,
            custom_subscription_email_enabled=True,
            custom_subscription_email="test@test.com",
            custom_subscription_footer_enabled=True,
            custom_subscription_footer="example_footer",
            ask_data_mode="EnabledByDefault",
            named_sharing_enabled=False,
            mobile_biometrics_enabled=True,
            sheet_image_enabled=False,
            derived_permissions_enabled=True,
            user_visibility_mode="FULL",
            use_default_time_zone=False,
            time_zone="America/Los_Angeles",
            auto_suspend_refresh_enabled=True,
            auto_suspend_refresh_inactivity_window=55,
            tier_creator_capacity=5,
            tier_explorer_capacity=5,
            tier_viewer_capacity=5,
        )
        single_site._id = server.site_id
        server.sites.parent_srv = server
        single_site = server.sites.update(single_site)

    assert server.site_id == single_site.id
    assert "tableau" == single_site.content_url
    assert "Suspended" == single_site.state
    assert "Tableau" == single_site.name
    assert "ContentAndUsers" == single_site.admin_mode
    assert single_site.revision_history_enabled is True
    assert 13 == single_site.revision_limit
    assert single_site.disable_subscriptions is True
    assert None == single_site.user_quota
    assert 5 == single_site.tier_creator_capacity
    assert 5 == single_site.tier_explorer_capacity
    assert 5 == single_site.tier_viewer_capacity
    assert "disable" == single_site.data_acceleration_mode
    assert single_site.flows_enabled is True
    assert single_site.cataloging_enabled is True
    assert single_site.flow_auto_save_enabled is True
    assert single_site.web_extraction_enabled is False
    assert single_site.metrics_content_type_enabled is True
    assert single_site.notify_site_admins_on_throttle is False
    assert single_site.authoring_enabled is True
    assert single_site.custom_subscription_email_enabled is True
    assert "test@test.com" == single_site.custom_subscription_email
    assert single_site.custom_subscription_footer_enabled is True
    assert "example_footer" == single_site.custom_subscription_footer
    assert "EnabledByDefault" == single_site.ask_data_mode
    assert single_site.named_sharing_enabled is False
    assert single_site.mobile_biometrics_enabled is True
    assert single_site.sheet_image_enabled is False
    assert single_site.derived_permissions_enabled is True
    assert "FULL" == single_site.user_visibility_mode
    assert single_site.use_default_time_zone is False
    assert "America/Los_Angeles" == single_site.time_zone
    assert single_site.auto_suspend_refresh_enabled is True
    assert 55 == single_site.auto_suspend_refresh_inactivity_window


def test_update_missing_id(server: TSC.Server) -> None:
    single_site = TSC.SiteItem("test", "test")
    with pytest.raises(TSC.MissingRequiredFieldError):
        server.sites.update(single_site)


def test_null_site_quota(server: TSC.Server) -> None:
    test_site = TSC.SiteItem("testname", "testcontenturl", tier_explorer_capacity=1, user_quota=None)
    assert test_site.tier_explorer_capacity == 1
    with pytest.raises(ValueError):
        test_site.user_quota = 1
    test_site.tier_explorer_capacity = None
    test_site.user_quota = 1


def test_replace_license_tiers_with_user_quota(server: TSC.Server) -> None:
    test_site = TSC.SiteItem("testname", "testcontenturl", tier_explorer_capacity=1, user_quota=None)
    assert test_site.tier_explorer_capacity == 1
    with pytest.raises(ValueError):
        test_site.user_quota = 1
    test_site.replace_license_tiers_with_user_quota(1)
    assert 1 == test_site.user_quota
    assert test_site.tier_explorer_capacity is None


@pytest.mark.filterwarnings("ignore:FlowsEnabled has been removed")
def test_create(server: TSC.Server) -> None:
    response_xml = CREATE_XML.read_text()
    with requests_mock.mock() as m:
        m.post(server.sites.baseurl, text=response_xml)
        new_site = TSC.SiteItem(
            name="Tableau",
            content_url="tableau",
            admin_mode=TSC.SiteItem.AdminMode.ContentAndUsers,
            user_quota=15,
            storage_quota=1000,
            disable_subscriptions=True,
        )
        new_site = server.sites.create(new_site)

    new_site._tier_viewer_capacity = None
    new_site._tier_creator_capacity = None
    new_site._tier_explorer_capacity = None
    assert "0626857c-1def-4503-a7d8-7907c3ff9d9f" == new_site.id
    assert "tableau" == new_site.content_url
    assert "Tableau" == new_site.name
    assert "Active" == new_site.state
    assert "ContentAndUsers" == new_site.admin_mode
    assert new_site.revision_history_enabled is False
    assert new_site.subscribe_others_enabled is True
    assert new_site.disable_subscriptions is True
    assert 15 == new_site.user_quota


def test_delete(server: TSC.Server) -> None:
    with requests_mock.mock() as m:
        m.delete(server.sites.baseurl + "/0626857c-1def-4503-a7d8-7907c3ff9d9f", status_code=204)
        server.sites.delete("0626857c-1def-4503-a7d8-7907c3ff9d9f")


def test_delete_missing_id(server: TSC.Server) -> None:
    with pytest.raises(ValueError):
        server.sites.delete("")


def test_encrypt(server: TSC.Server) -> None:
    with requests_mock.mock() as m:
        m.post(server.sites.baseurl + "/0626857c-1def-4503-a7d8-7907c3ff9d9f/encrypt-extracts", status_code=200)
        server.sites.encrypt_extracts("0626857c-1def-4503-a7d8-7907c3ff9d9f")


def test_recrypt(server: TSC.Server) -> None:
    with requests_mock.mock() as m:
        m.post(server.sites.baseurl + "/0626857c-1def-4503-a7d8-7907c3ff9d9f/reencrypt-extracts", status_code=200)
        server.sites.re_encrypt_extracts("0626857c-1def-4503-a7d8-7907c3ff9d9f")


def test_decrypt(server: TSC.Server) -> None:
    with requests_mock.mock() as m:
        m.post(server.sites.baseurl + "/0626857c-1def-4503-a7d8-7907c3ff9d9f/decrypt-extracts", status_code=200)
        server.sites.decrypt_extracts("0626857c-1def-4503-a7d8-7907c3ff9d9f")


def test_list_auth_configurations(server: TSC.Server) -> None:
    server.version = "3.24"
    response_xml = SITE_AUTH_CONFIG_XML.read_text()

    assert server.sites.baseurl == server.sites.baseurl

    with requests_mock.mock() as m:
        m.get(f"{server.sites.baseurl}/{server.site_id}/site-auth-configurations", status_code=200, text=response_xml)
        configs = server.sites.list_auth_configurations()

    assert len(configs) == 2, "Expected 2 auth configurations"

    assert configs[0].auth_setting == "OIDC"
    assert configs[0].enabled
    assert configs[0].idp_configuration_id == "00000000-0000-0000-0000-000000000000"
    assert configs[0].idp_configuration_name == "Initial Salesforce"
    assert configs[0].known_provider_alias == "Salesforce"
    assert configs[1].auth_setting == "SAML"
    assert configs[1].enabled
    assert configs[1].idp_configuration_id == "11111111-1111-1111-1111-111111111111"
    assert configs[1].idp_configuration_name == "Initial SAML"
    assert configs[1].known_provider_alias is None


@pytest.mark.parametrize("capture", [True, False, None])
def test_parsing_attr_capture(capture):
    server = TSC.Server("http://test", False)
    server.version = "3.10"
    attrs = {"contentUrl": "test", "name": "test"}
    if capture is not None:
        attrs |= {"attributeCaptureEnabled": str(capture).lower()}
    xml = _utils.server_response_factory("site", **attrs)
    site = TSC.SiteItem.from_response(xml, server.namespace)[0]

    assert site.attribute_capture_enabled is capture, "Attribute capture not captured correctly"


@pytest.mark.filterwarnings("ignore:FlowsEnabled has been removed")
@pytest.mark.parametrize("req, capture", product(["create_req", "update_req"], [True, False, None]))
def test_encoding_attr_capture(req, capture):
    site = TSC.SiteItem(
        content_url="test",
        name="test",
        attribute_capture_enabled=capture,
    )
    xml = getattr(RequestFactory.Site, req)(site)
    site_elem = ET.fromstring(xml).find(".//site")
    assert site_elem is not None, "Site element missing from XML body."

    if capture is not None:
        assert (
            site_elem.attrib["attributeCaptureEnabled"] == str(capture).lower()
        ), "Attribute capture not encoded correctly"
    else:
        assert "attributeCaptureEnabled" not in site_elem.attrib, "Attribute capture should not be encoded when None"
