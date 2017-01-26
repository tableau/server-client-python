import unittest
import warnings
import tableauserverclient as TSC


class TableauAuthModelTests(unittest.TestCase):
    def setUp(self):
        self.auth = TSC.TableauAuth('user',
                                    'password',
                                    site_id='dad65087-b08b-4603-af4e-2887b8aafc67',
                                    user_id_to_impersonate='admin')

    def test_username_password_required(self):
        with self.assertRaises(TypeError):
            TSC.TableauAuth()

    def test_site_arg_raises_warning(self):
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")

            tableau_auth = TSC.TableauAuth('user',
                                           'password',
                                           site='Default')

            self.assertTrue(any(item.category == DeprecationWarning for item in w))
