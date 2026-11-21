"""
E2E tests for SiteAdmin-level operations against a real Tableau server.

Requires SiteAdmin credentials:
    TABLEAU_SITEADMIN_TOKEN_NAME=... TABLEAU_SITEADMIN_TOKEN=...

Run with:
    pytest test_e2e/test_site_admin.py -v -m e2e_admin
"""

import uuid
from datetime import time
from pathlib import Path

import pytest
import tableauserverclient as TSC

ASSETS_DIR = Path(__file__).parent / "assets"
SAMPLE_WORKBOOK = ASSETS_DIR / "WorkbookWithoutExtract.twbx"
SAMPLE_DATASOURCE = ASSETS_DIR / "WorldIndicators.tdsx"

pytestmark = pytest.mark.e2e_admin


def _name(base):
    return f"{base}-{uuid.uuid4().hex[:8]}"


# ---------------------------------------------------------------------------
# Schedules
# ---------------------------------------------------------------------------


def test_schedule_create_and_delete(server_admin):
    """An extract schedule can be created and deleted."""
    interval = TSC.HourlyInterval(start_time=time(3, 0), end_time=time(23, 0), interval_value=4)
    schedule = TSC.ScheduleItem(
        name=_name("tsc-e2e-schedule"),
        priority=50,
        schedule_type=TSC.ScheduleItem.Type.Extract,
        execution_order=TSC.ScheduleItem.ExecutionOrder.Parallel,
        interval_item=interval,
    )
    schedule = server_admin.schedules.create(schedule)
    try:
        assert schedule.id is not None
        fetched = server_admin.schedules.get_by_id(schedule.id)
        assert fetched.id == schedule.id
    finally:
        server_admin.schedules.delete(schedule.id)


def test_schedule_add_workbook(server_admin, project_id):
    """A workbook can be added to an extract refresh schedule."""
    interval = TSC.DailyInterval(start_time=time(4, 0))
    schedule_name = _name("tsc-e2e-sched-wb")
    schedule = TSC.ScheduleItem(
        name=schedule_name,
        priority=60,
        schedule_type=TSC.ScheduleItem.Type.Extract,
        execution_order=TSC.ScheduleItem.ExecutionOrder.Serial,
        interval_item=interval,
    )
    schedule = server_admin.schedules.create(schedule)
    wb = TSC.WorkbookItem(name=_name("tsc-e2e-sched-wb"), project_id=project_id)
    wb = server_admin.workbooks.publish(wb, SAMPLE_WORKBOOK, TSC.Server.PublishMode.Overwrite)
    try:
        server_admin.schedules.add_to_schedule(schedule.id, wb)
        tasks, _ = server_admin.tasks.get()
        assert any(getattr(t, "schedule_id", None) == schedule.id for t in tasks)
    finally:
        server_admin.workbooks.delete(wb.id)
        server_admin.schedules.delete(schedule.id)


# ---------------------------------------------------------------------------
# Webhooks
# ---------------------------------------------------------------------------


def test_webhook_create_and_delete(server_admin):
    """A webhook can be created and deleted."""
    webhook = TSC.WebhookItem()
    webhook.name = _name("tsc-e2e-webhook")
    webhook.url = "https://example.com/tsc-e2e-webhook"
    webhook.event = "datasource-created"
    webhook = server_admin.webhooks.create(webhook)
    try:
        assert webhook.id is not None
        all_webhooks, _ = server_admin.webhooks.get()
        assert any(w.id == webhook.id for w in all_webhooks)
    finally:
        server_admin.webhooks.delete(webhook.id)


# ---------------------------------------------------------------------------
# Connection update
# ---------------------------------------------------------------------------


def test_datasource_update_connection(server_admin, project_id):
    """A datasource connection's embed_password flag can be toggled via update_connection."""
    ds = TSC.DatasourceItem(project_id=project_id, name=_name("tsc-e2e-conn-ds"))
    ds = server_admin.datasources.publish(ds, str(SAMPLE_DATASOURCE), TSC.Server.PublishMode.Overwrite)
    try:
        server_admin.datasources.populate_connections(ds)
        if not ds.connections:
            pytest.skip("Published datasource has no connections to update")
        conn = ds.connections[0]
        conn.embed_password = False
        updated_conn = server_admin.datasources.update_connection(ds, conn)
        assert updated_conn is not None
    finally:
        server_admin.datasources.delete(ds.id)


# ---------------------------------------------------------------------------
# Data freshness policy
# ---------------------------------------------------------------------------


def test_workbook_data_freshness_policy(server_admin, project_id):
    """Workbook data freshness policy can be set to AlwaysLive and back to SiteDefault."""
    wb = TSC.WorkbookItem(name=_name("tsc-e2e-freshness"), project_id=project_id)
    wb = server_admin.workbooks.publish(wb, SAMPLE_WORKBOOK, TSC.Server.PublishMode.Overwrite)
    try:
        wb.data_freshness_policy = TSC.DataFreshnessPolicyItem(TSC.DataFreshnessPolicyItem.Option.AlwaysLive)
        updated = server_admin.workbooks.update(wb)
        assert updated.data_freshness_policy.option == TSC.DataFreshnessPolicyItem.Option.AlwaysLive

        wb.data_freshness_policy = TSC.DataFreshnessPolicyItem(TSC.DataFreshnessPolicyItem.Option.SiteDefault)
        updated = server_admin.workbooks.update(wb)
        assert updated.data_freshness_policy.option == TSC.DataFreshnessPolicyItem.Option.SiteDefault
    finally:
        server_admin.workbooks.delete(wb.id)


# ---------------------------------------------------------------------------
# Workbook move between projects
# ---------------------------------------------------------------------------


def test_workbook_move_project(server_admin, project_id):
    """A workbook can be moved from one project to another."""
    dest_name = _name("tsc-e2e-dest-proj")
    dest = TSC.ProjectItem(name=dest_name)
    dest = server_admin.projects.create(dest)
    wb = TSC.WorkbookItem(name=_name("tsc-e2e-move-wb"), project_id=project_id)
    wb = server_admin.workbooks.publish(wb, SAMPLE_WORKBOOK, TSC.Server.PublishMode.Overwrite)
    try:
        wb.project_id = dest.id
        updated = server_admin.workbooks.update(wb)
        assert updated.project_id == dest.id
    finally:
        server_admin.workbooks.delete(wb.id)
        server_admin.projects.delete(dest.id)


# ---------------------------------------------------------------------------
# Users
# ---------------------------------------------------------------------------


def test_user_add_and_remove(server_admin):
    """A user can be added to the site and removed."""
    username = _name("tsc-e2e-user")
    user = TSC.UserItem(username, "Unlicensed")
    user = server_admin.users.add(user)
    try:
        assert user.id is not None
        fetched = server_admin.users.get_by_id(user.id)
        assert fetched.name == username
    finally:
        server_admin.users.remove(user.id)


# ---------------------------------------------------------------------------
# Groups
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def group(server_admin):
    g = TSC.GroupItem(_name("tsc-e2e-admin-grp"))
    g = server_admin.groups.create(g)
    yield g
    server_admin.groups.delete(g.id)


def test_group_create_and_get(server_admin, group):
    """Created group appears in the group list."""
    results = list(server_admin.groups.filter(name=group.name))
    assert any(g.id == group.id for g in results)


def test_group_add_and_remove_user(server_admin, group):
    """A user can be added to and removed from a group."""
    username = _name("tsc-e2e-grp-user")
    user = TSC.UserItem(username, "Unlicensed")
    user = server_admin.users.add(user)
    try:
        server_admin.groups.add_user(group, user.id)
        server_admin.groups.populate_users(group)
        assert any(u.id == user.id for u in group.users)

        server_admin.groups.remove_user(group, user.id)
        server_admin.groups.populate_users(group)
        assert all(u.id != user.id for u in group.users)
    finally:
        server_admin.users.remove(user.id)
