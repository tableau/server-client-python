import unittest
import tableauserverclient as TSC


class SiteModelTests(unittest.TestCase):
    def test_invalid_name(self):
        self.assertRaises(ValueError, TSC.SiteItem, None, "url")
        self.assertRaises(ValueError, TSC.SiteItem, "", "url")
        site = TSC.SiteItem("site", "url")
        with self.assertRaises(ValueError):
            site.name = None

        with self.assertRaises(ValueError):
            site.name = ""

    def test_invalid_admin_mode(self):
        site = TSC.SiteItem("site", "url")
        with self.assertRaises(ValueError):
            site.admin_mode = "Hello"

    def test_invalid_content_url(self):
        self.assertRaises(ValueError, TSC.SiteItem, "site", None)
        site = TSC.SiteItem("site", "url")
        with self.assertRaises(ValueError):
            site.content_url = None

    def test_invalid_disable_subscriptions(self):
        site = TSC.SiteItem("site", "url")
        with self.assertRaises(ValueError):
            site.disable_subscriptions = "Hello"

        with self.assertRaises(ValueError):
            site.disable_subscriptions = None

    def test_invalid_revision_history_enabled(self):
        site = TSC.SiteItem("site", "url")
        with self.assertRaises(ValueError):
            site.revision_history_enabled = "Hello"

        with self.assertRaises(ValueError):
            site.revision_history_enabled = None

    def test_invalid_state(self):
        site = TSC.SiteItem("site", "url")
        with self.assertRaises(ValueError):
            site.state = "Hello"

    def test_invalid_subscribe_others_enabled(self):
        site = TSC.SiteItem("site", "url")
        with self.assertRaises(ValueError):
            site.subscribe_others_enabled = "Hello"

        with self.assertRaises(ValueError):
            site.subscribe_others_enabled = None
