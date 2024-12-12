import unittest

import tableauserverclient as TSC


class TableauAuthModelTests(unittest.TestCase):
    def setUp(self):
        self.auth = TSC.TableauAuth("user", "password", site_id="site1", user_id_to_impersonate="admin")

    def test_username_password_required(self):
        with self.assertRaises(TypeError):
            TSC.TableauAuth()
