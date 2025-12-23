import pytest

import tableauserverclient as TSC


def test_nullable_name():
    TSC.ProjectItem(None)
    TSC.ProjectItem("")
    project = TSC.ProjectItem("proj")
    project.name = None


def test_invalid_content_permissions():
    project = TSC.ProjectItem("proj")
    with pytest.raises(ValueError):
        project.content_permissions = "Hello"


def test_parent_id():
    project = TSC.ProjectItem("proj")
    project.parent_id = "foo"
    assert project.parent_id == "foo"
