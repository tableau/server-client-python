"""
E2E tests for user and group operations against a real Tableau Server.
Requires SiteAdmin credentials.

Run with:
    TABLEAU_SERVER=https://... TABLEAU_SITE=mysite \
    TABLEAU_SITEADMIN_TOKEN_NAME=... TABLEAU_SITEADMIN_TOKEN=... \
    pytest test_e2e/test_users_groups.py -v
"""
import pytest
import tableauserverclient as TSC

pytestmark = pytest.mark.e2e_admin


def test_users_get_returns_nonempty_list(server_admin):
    """users.get() returns at least the current (admin) user."""
    users, pagination = server_admin.users.get()
    assert len(users) >= 1
    assert pagination.total_available >= 1


def test_groups_get_returns_nonempty_list(server_admin):
    """groups.get() returns at least one group."""
    groups, pagination = server_admin.groups.get()
    assert len(groups) >= 1
    assert pagination.total_available >= 1


def test_user_add_creates_user(server_admin):
    """users.add() creates a new local user and returns it with an assigned id."""
    new_user = TSC.UserItem("tsc-e2e-user", TSC.UserItem.Roles.Unlicensed)
    created = None
    try:
        created = server_admin.users.add(new_user)
        assert created.id is not None
        assert created.name == "tsc-e2e-user"
    finally:
        if created and created.id:
            server_admin.users.remove(created.id)


def test_user_get_by_id_returns_user(server_admin):
    """users.get_by_id() returns the correct user for a known id."""
    new_user = TSC.UserItem("tsc-e2e-user-byid", TSC.UserItem.Roles.Unlicensed)
    created = None
    try:
        created = server_admin.users.add(new_user)
        fetched = server_admin.users.get_by_id(created.id)
        assert fetched.id == created.id
        assert fetched.name == "tsc-e2e-user-byid"
    finally:
        if created and created.id:
            server_admin.users.remove(created.id)


def test_user_update_changes_role(server_admin):
    """users.update() with a new site_role persists the change."""
    new_user = TSC.UserItem("tsc-e2e-user-update", TSC.UserItem.Roles.Unlicensed)
    created = None
    try:
        created = server_admin.users.add(new_user)
        created.site_role = TSC.UserItem.Roles.Viewer
        updated = server_admin.users.update(created)
        assert updated.site_role == TSC.UserItem.Roles.Viewer

        # Verify persisted server-side
        fetched = server_admin.users.get_by_id(created.id)
        assert fetched.site_role == TSC.UserItem.Roles.Viewer
    finally:
        if created and created.id:
            server_admin.users.remove(created.id)


def test_group_create_creates_group(server_admin):
    """groups.create() creates a local group and returns it with an assigned id."""
    new_group = TSC.GroupItem("tsc-e2e-group")
    created = None
    try:
        created = server_admin.groups.create(new_group)
        assert created.id is not None
        assert created.name == "tsc-e2e-group"
    finally:
        if created and created.id:
            server_admin.groups.delete(created.id)


def test_group_add_user_appears_in_populate_users(server_admin):
    """groups.add_user() results in the user appearing in groups.populate_users()."""
    user = None
    group = None
    try:
        user = server_admin.users.add(TSC.UserItem("tsc-e2e-user-grp", TSC.UserItem.Roles.Unlicensed))
        group = server_admin.groups.create(TSC.GroupItem("tsc-e2e-group-add"))

        server_admin.groups.add_user(group, user.id)

        server_admin.groups.populate_users(group)
        user_ids = [u.id for u in group.users]
        assert user.id in user_ids
    finally:
        if group and group.id:
            server_admin.groups.delete(group.id)
        if user and user.id:
            server_admin.users.remove(user.id)


def test_group_remove_user_no_longer_in_group(server_admin):
    """groups.remove_user() removes user from group; user is no longer listed."""
    user = None
    group = None
    try:
        user = server_admin.users.add(TSC.UserItem("tsc-e2e-user-rmv", TSC.UserItem.Roles.Unlicensed))
        group = server_admin.groups.create(TSC.GroupItem("tsc-e2e-group-rmv"))

        server_admin.groups.add_user(group, user.id)
        server_admin.groups.remove_user(group, user.id)

        server_admin.groups.populate_users(group)
        user_ids = [u.id for u in group.users]
        assert user.id not in user_ids
    finally:
        if group and group.id:
            server_admin.groups.delete(group.id)
        if user and user.id:
            server_admin.users.remove(user.id)


def test_group_delete_removes_group(server_admin):
    """groups.delete() removes the group; it no longer appears in groups.get()."""
    created = None
    try:
        created = server_admin.groups.create(TSC.GroupItem("tsc-e2e-group-del"))
        group_id = created.id
        server_admin.groups.delete(group_id)
        created = None

        remaining = list(server_admin.groups.filter(name="tsc-e2e-group-del"))
        assert len(remaining) == 0
    finally:
        if created and created.id:
            server_admin.groups.delete(created.id)


def test_user_remove_removes_user(server_admin):
    """users.remove() removes the user; they no longer appear in users.get()."""
    new_user = TSC.UserItem("tsc-e2e-user-del", TSC.UserItem.Roles.Unlicensed)
    created = None
    try:
        created = server_admin.users.add(new_user)
        user_id = created.id
        server_admin.users.remove(user_id)
        created = None

        remaining = list(server_admin.users.filter(name="tsc-e2e-user-del"))
        assert len(remaining) == 0
    finally:
        if created and created.id:
            server_admin.users.remove(created.id)
