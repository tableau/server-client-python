"""Tests for the structural protocols defined in tableauserverclient.models.base_item.

Verifies that:
- Each runtime_checkable protocol can be used with isinstance().
- Representative item classes satisfy the protocols they are documented to satisfy.
- Items that lack required attributes do NOT satisfy stricter protocols.
"""

import datetime

import pytest

import tableauserverclient as TSC
from tableauserverclient.models.base_item import TableauItem, ContentItem, OwnedItem, TaggableItem

# ---------------------------------------------------------------------------
# TableauItem: id + name
# ---------------------------------------------------------------------------


class TestTableauItem:
    def test_workbook_satisfies_tableau_item(self):
        item = TSC.WorkbookItem(project_id="p1", name="wb")
        assert isinstance(item, TableauItem)

    def test_datasource_satisfies_tableau_item(self):
        item = TSC.DatasourceItem(project_id="p1", name="ds")
        assert isinstance(item, TableauItem)

    def test_view_satisfies_tableau_item(self):
        item = TSC.ViewItem()
        assert isinstance(item, TableauItem)

    def test_flow_satisfies_tableau_item(self):
        item = TSC.FlowItem(project_id="p1", name="f")
        assert isinstance(item, TableauItem)

    def test_project_satisfies_tableau_item(self):
        item = TSC.ProjectItem(name="proj")
        assert isinstance(item, TableauItem)

    def test_metric_satisfies_tableau_item(self):
        item = TSC.MetricItem()
        assert isinstance(item, TableauItem)

    def test_user_satisfies_tableau_item(self):
        item = TSC.UserItem(name="u", site_role="Viewer")
        assert isinstance(item, TableauItem)

    def test_database_satisfies_tableau_item(self):
        item = TSC.DatabaseItem(name="db")
        assert isinstance(item, TableauItem)

    def test_table_satisfies_tableau_item(self):
        item = TSC.TableItem(name="tbl")
        assert isinstance(item, TableauItem)

    def test_virtual_connection_satisfies_tableau_item(self):
        item = TSC.VirtualConnectionItem(name="vc")
        assert isinstance(item, TableauItem)

    def test_task_item_does_not_satisfy_tableau_item(self):
        """TaskItem has an id but no name attribute."""
        item = TSC.TaskItem(id_="t1", task_type="refresh", priority=1)
        assert not isinstance(item, TableauItem)

    def test_issubclass_on_data_protocol_raises(self):
        """runtime_checkable data-attribute Protocols don't support issubclass;
        they raise TypeError. Callers must use isinstance() on an instance."""
        with pytest.raises(TypeError):
            issubclass(TSC.WorkbookItem, TableauItem)

    def test_plain_object_with_id_and_name_satisfies_tableau_item(self):
        """Structural subtyping: any object with id and name suffices."""

        class Minimal:
            id: str | None = None
            name: str | None = "x"

        assert isinstance(Minimal(), TableauItem)

    def test_object_missing_name_does_not_satisfy_tableau_item(self):
        class NoName:
            id: str | None = None

        assert not isinstance(NoName(), TableauItem)

    def test_object_missing_id_does_not_satisfy_tableau_item(self):
        class NoId:
            name: str | None = "x"

        assert not isinstance(NoId(), TableauItem)


# ---------------------------------------------------------------------------
# OwnedItem: BaseItem + owner_id
# ---------------------------------------------------------------------------


class TestOwnedItem:
    def test_workbook_satisfies_owned_item(self):
        item = TSC.WorkbookItem(project_id="p1", name="wb")
        assert isinstance(item, OwnedItem)

    def test_datasource_satisfies_owned_item(self):
        item = TSC.DatasourceItem(project_id="p1", name="ds")
        assert isinstance(item, OwnedItem)

    def test_view_satisfies_owned_item(self):
        item = TSC.ViewItem()
        assert isinstance(item, OwnedItem)

    def test_flow_satisfies_owned_item(self):
        item = TSC.FlowItem(project_id="p1", name="f")
        assert isinstance(item, OwnedItem)

    def test_project_satisfies_owned_item(self):
        item = TSC.ProjectItem(name="proj")
        assert isinstance(item, OwnedItem)

    def test_metric_satisfies_owned_item(self):
        item = TSC.MetricItem()
        assert isinstance(item, OwnedItem)

    def test_user_does_not_satisfy_owned_item(self):
        """UserItem has no owner_id attribute."""
        item = TSC.UserItem(name="u", site_role="Viewer")
        assert not isinstance(item, OwnedItem)

    def test_virtual_connection_satisfies_owned_item(self):
        item = TSC.VirtualConnectionItem(name="vc")
        assert isinstance(item, OwnedItem)

    def test_plain_object_satisfies_owned_item(self):
        class Owned:
            id: str | None = None
            name: str | None = "x"

            @property
            def owner_id(self) -> str | None:
                return None

        assert isinstance(Owned(), OwnedItem)

    def test_object_missing_owner_id_does_not_satisfy_owned_item(self):
        class NoOwner:
            id: str | None = None
            name: str | None = "x"

        assert not isinstance(NoOwner(), OwnedItem)


# ---------------------------------------------------------------------------
# TaggableItem: BaseItem + tags
# ---------------------------------------------------------------------------


class TestTaggableItem:
    def test_workbook_satisfies_taggable_item(self):
        item = TSC.WorkbookItem(project_id="p1", name="wb")
        assert isinstance(item, TaggableItem)

    def test_datasource_satisfies_taggable_item(self):
        item = TSC.DatasourceItem(project_id="p1", name="ds")
        assert isinstance(item, TaggableItem)

    def test_view_satisfies_taggable_item(self):
        item = TSC.ViewItem()
        assert isinstance(item, TaggableItem)

    def test_flow_satisfies_taggable_item(self):
        item = TSC.FlowItem(project_id="p1", name="f")
        assert isinstance(item, TaggableItem)

    def test_metric_satisfies_taggable_item(self):
        item = TSC.MetricItem()
        assert isinstance(item, TaggableItem)

    def test_project_does_not_satisfy_taggable_item(self):
        """ProjectItem does not expose a tags attribute."""
        item = TSC.ProjectItem(name="proj")
        assert not isinstance(item, TaggableItem)

    def test_user_does_not_satisfy_taggable_item(self):
        """UserItem does not expose a tags attribute."""
        item = TSC.UserItem(name="u", site_role="Viewer")
        assert not isinstance(item, TaggableItem)

    def test_virtual_connection_does_not_satisfy_taggable_item(self):
        """VirtualConnectionItem does not expose a tags attribute."""
        item = TSC.VirtualConnectionItem(name="vc")
        assert not isinstance(item, TaggableItem)

    def test_plain_object_with_tags_satisfies_taggable_item(self):
        class Tagged:
            id: str | None = None
            name: str | None = "x"
            tags: set = set()

        assert isinstance(Tagged(), TaggableItem)

    def test_object_missing_tags_does_not_satisfy_taggable_item(self):
        class NoTags:
            id: str | None = None
            name: str | None = "x"

        assert not isinstance(NoTags(), TaggableItem)


# ---------------------------------------------------------------------------
# ContentItem: OwnedItem + TaggableItem + created_at + updated_at
# ---------------------------------------------------------------------------


class TestContentItem:
    def test_workbook_satisfies_content_item(self):
        item = TSC.WorkbookItem(project_id="p1", name="wb")
        assert isinstance(item, ContentItem)

    def test_datasource_satisfies_content_item(self):
        item = TSC.DatasourceItem(project_id="p1", name="ds")
        assert isinstance(item, ContentItem)

    def test_view_satisfies_content_item(self):
        item = TSC.ViewItem()
        assert isinstance(item, ContentItem)

    def test_flow_satisfies_content_item(self):
        item = TSC.FlowItem(project_id="p1", name="f")
        assert isinstance(item, ContentItem)

    def test_metric_satisfies_content_item(self):
        item = TSC.MetricItem()
        assert isinstance(item, ContentItem)

    def test_project_does_not_satisfy_content_item(self):
        """ProjectItem lacks tags, so it cannot satisfy ContentItem."""
        item = TSC.ProjectItem(name="proj")
        assert not isinstance(item, ContentItem)

    def test_user_does_not_satisfy_content_item(self):
        """UserItem lacks owner_id and tags."""
        item = TSC.UserItem(name="u", site_role="Viewer")
        assert not isinstance(item, ContentItem)

    def test_plain_object_missing_timestamps_does_not_satisfy_content_item(self):
        class NoTimestamps:
            id: str | None = None
            name: str | None = "x"
            tags: set = set()

            @property
            def owner_id(self) -> str | None:
                return None

        assert not isinstance(NoTimestamps(), ContentItem)

    def test_complete_plain_object_satisfies_content_item(self):
        class Full:
            id: str | None = None
            name: str | None = "x"
            tags: set = set()
            created_at: datetime.datetime | None = None
            updated_at: datetime.datetime | None = None

            @property
            def owner_id(self) -> str | None:
                return None

        assert isinstance(Full(), ContentItem)


# ---------------------------------------------------------------------------
# Protocol hierarchy: ContentItem implies OwnedItem, TaggableItem, and TableauItem
# ---------------------------------------------------------------------------


class TestProtocolHierarchy:
    """An item that satisfies ContentItem must also satisfy every parent protocol."""

    def test_content_item_satisfier_also_satisfies_owned_item(self):
        item = TSC.WorkbookItem(project_id="p1", name="wb")
        assert isinstance(item, OwnedItem)

    def test_content_item_satisfier_also_satisfies_taggable_item(self):
        item = TSC.WorkbookItem(project_id="p1", name="wb")
        assert isinstance(item, TaggableItem)

    def test_content_item_satisfier_also_satisfies_tableau_item(self):
        item = TSC.WorkbookItem(project_id="p1", name="wb")
        assert isinstance(item, TableauItem)

    def test_owned_item_satisfier_also_satisfies_tableau_item(self):
        item = TSC.ProjectItem(name="proj")
        assert isinstance(item, TableauItem)
