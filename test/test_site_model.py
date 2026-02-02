import pytest

import tableauserverclient as TSC


def test_invalid_name():
    with pytest.raises(ValueError):
        TSC.SiteItem(None, "url")
    with pytest.raises(ValueError):
        TSC.SiteItem("", "url")
    site = TSC.SiteItem("site", "url")
    with pytest.raises(ValueError):
        site.name = None

    with pytest.raises(ValueError):
        site.name = ""


def test_invalid_admin_mode():
    site = TSC.SiteItem("site", "url")
    with pytest.raises(ValueError):
        site.admin_mode = "Hello"


def test_invalid_content_url():
    with pytest.raises(ValueError):
        site = TSC.SiteItem(name="蚵仔煎", content_url="蚵仔煎")

    with pytest.raises(ValueError):
        site = TSC.SiteItem(name="蚵仔煎", content_url=None)


def test_set_valid_content_url():
    # Default Site
    site = TSC.SiteItem(name="Default", content_url="")
    assert site.content_url == ""

    # Unicode Name and ascii content_url
    site = TSC.SiteItem(name="蚵仔煎", content_url="omlette")
    assert site.content_url == "omlette"


def test_invalid_disable_subscriptions():
    site = TSC.SiteItem("site", "url")
    with pytest.raises(ValueError):
        site.disable_subscriptions = "Hello"

    with pytest.raises(ValueError):
        site.disable_subscriptions = None


def test_invalid_revision_history_enabled():
    site = TSC.SiteItem("site", "url")
    with pytest.raises(ValueError):
        site.revision_history_enabled = "Hello"

    with pytest.raises(ValueError):
        site.revision_history_enabled = None


def test_invalid_state():
    site = TSC.SiteItem("site", "url")
    with pytest.raises(ValueError):
        site.state = "Hello"


def test_invalid_subscribe_others_enabled():
    site = TSC.SiteItem("site", "url")
    with pytest.raises(ValueError):
        site.subscribe_others_enabled = "Hello"

    with pytest.raises(ValueError):
        site.subscribe_others_enabled = None
