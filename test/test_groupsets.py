from pathlib import Path
import unittest

from defusedxml.ElementTree import fromstring
import requests_mock

import tableauserverclient as TSC
from tableauserverclient.models.reference_item import ResourceReference

TEST_ASSET_DIR = Path(__file__).parent / "assets"
GROUPSET_CREATE = TEST_ASSET_DIR / "groupsets_create.xml"
GROUPSETS_GET = TEST_ASSET_DIR / "groupsets_get.xml"
GROUPSET_GET_BY_ID = TEST_ASSET_DIR / "groupsets_get_by_id.xml"
GROUPSET_UPDATE = TEST_ASSET_DIR / "groupsets_get_by_id.xml"


class TestGroupSets(unittest.TestCase):
    def setUp(self) -> None:
        self.server = TSC.Server("http://test", False)
        self.server.version = "3.22"

        # Fake signin
        self.server._site_id = "dad65087-b08b-4603-af4e-2887b8aafc67"
        self.server._auth_token = "j80k54ll2lfMZ0tv97mlPvvSCRyD0DOM"

        self.baseurl = self.server.group_sets.baseurl

    def test_get(self) -> None:
        with requests_mock.mock() as m:
            m.get(self.baseurl, text=GROUPSETS_GET.read_text())
            groupsets, pagination_item = self.server.group_sets.get()

        assert len(groupsets) == 3
        assert pagination_item.total_available == 3
        assert groupsets[0].id == "1a2b3c4d-5e6f-7a8b-9c0d-1e2f3a4b5c6d"
        assert groupsets[0].name == "All Users"
        assert groupsets[0].group_count == 1
        assert groupsets[0].groups[0].name == "group-one"
        assert groupsets[0].groups[0].id == "gs-1"

        assert groupsets[1].id == "9a8a7b6b-5c4c-3d2d-1e0e-9a8a7b6b5b4b"
        assert groupsets[1].name == "active-directory-group-import"
        assert groupsets[1].group_count == 1
        assert groupsets[1].groups[0].name == "group-two"
        assert groupsets[1].groups[0].id == "gs21"

        assert groupsets[2].id == "7b6b59a8-ac3c-4d1d-2e9e-0b5b4ba8a7b6"
        assert groupsets[2].name == "local-group-license-on-login"
        assert groupsets[2].group_count == 1
        assert groupsets[2].groups[0].name == "group-three"
        assert groupsets[2].groups[0].id == "gs-3"

    def test_get_by_id(self) -> None:
        with requests_mock.mock() as m:
            m.get(f"{self.baseurl}/1a2b3c4d-5e6f-7a8b-9c0d-1e2f3a4b5c6d", text=GROUPSET_GET_BY_ID.read_text())
            groupset = self.server.group_sets.get_by_id("1a2b3c4d-5e6f-7a8b-9c0d-1e2f3a4b5c6d")

        assert groupset.id == "1a2b3c4d-5e6f-7a8b-9c0d-1e2f3a4b5c6d"
        assert groupset.name == "All Users"
        assert groupset.group_count == 3
        assert len(groupset.groups) == 3

        assert groupset.groups[0].name == "group-one"
        assert groupset.groups[0].id == "gs-1"
        assert groupset.groups[1].name == "group-two"
        assert groupset.groups[1].id == "gs21"
        assert groupset.groups[2].name == "group-three"
        assert groupset.groups[2].id == "gs-3"

    def test_update(self) -> None:
        id_ = "1a2b3c4d-5e6f-7a8b-9c0d-1e2f3a4b5c6d"
        groupset = TSC.GroupSetItem("All Users")
        groupset.id = id_
        with requests_mock.mock() as m:
            m.put(f"{self.baseurl}/{id_}", text=GROUPSET_UPDATE.read_text())
            groupset = self.server.group_sets.update(groupset)

        assert groupset.id == id_
        assert groupset.name == "All Users"
        assert groupset.group_count == 3
        assert len(groupset.groups) == 3

        assert groupset.groups[0].name == "group-one"
        assert groupset.groups[0].id == "gs-1"
        assert groupset.groups[1].name == "group-two"
        assert groupset.groups[1].id == "gs21"
        assert groupset.groups[2].name == "group-three"
        assert groupset.groups[2].id == "gs-3"

    def test_create(self) -> None:
        groupset = TSC.GroupSetItem("All Users")
        with requests_mock.mock() as m:
            m.post(self.baseurl, text=GROUPSET_CREATE.read_text())
            groupset = self.server.group_sets.create(groupset)

        assert groupset.id == "1a2b3c4d-5e6f-7a8b-9c0d-1e2f3a4b5c6d"
        assert groupset.name == "All Users"
        assert groupset.group_count == 0
        assert len(groupset.groups) == 0

    def test_add_group(self) -> None:
        groupset = TSC.GroupSetItem("All")
        groupset.id = "1a2b3c4d-5e6f-7a8b-9c0d-1e2f3a4b5c6d"
        group = TSC.GroupItem("Example")
        group._id = "ef8b19c0-43b6-11e6-af50-63f5805dbe3c"

        with requests_mock.mock() as m:
            m.put(f"{self.baseurl}/{groupset.id}/groups/{group._id}")
            self.server.group_sets.add_group(groupset, group)

            history = m.request_history

        assert len(history) == 1
        assert history[0].method == "PUT"
        assert history[0].url == f"{self.baseurl}/{groupset.id}/groups/{group._id}"

    def test_remove_group(self) -> None:
        groupset = TSC.GroupSetItem("All")
        groupset.id = "1a2b3c4d-5e6f-7a8b-9c0d-1e2f3a4b5c6d"
        group = TSC.GroupItem("Example")
        group._id = "ef8b19c0-43b6-11e6-af50-63f5805dbe3c"

        with requests_mock.mock() as m:
            m.delete(f"{self.baseurl}/{groupset.id}/groups/{group._id}")
            self.server.group_sets.remove_group(groupset, group)

            history = m.request_history

        assert len(history) == 1
        assert history[0].method == "DELETE"
        assert history[0].url == f"{self.baseurl}/{groupset.id}/groups/{group._id}"

    def test_as_reference(self) -> None:
        groupset = TSC.GroupSetItem()
        groupset.id = "1a2b3c4d-5e6f-7a8b-9c0d-1e2f3a4b5c6d"
        ref = groupset.as_reference(groupset.id)
        assert ref.id == groupset.id
        assert ref.tag_name == groupset.tag_name
        assert isinstance(ref, ResourceReference)
