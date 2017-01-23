import unittest
import warnings
import tableauserverclient as TSC


class TableauAuthModelTests(unittest.TestCase):
    def test_username_password_required(self):
        with self.assertRaises(TypeError) as context_manager:
            TSC.TableauAuth()

    def test_site_arg_raises_warning(self):
        with warnings.catch_warnings(record=True) as w:
            # Cause all warnings to always be triggered.
            warnings.simplefilter("always")

            tableau_auth = TSC.TableauAuth('user',
                                           'password',
                                           site='dad65087-b08b-4603-af4e-2887b8aafc67')

            assert len(w) == 1
            assert issubclass(w[-1].category, DeprecationWarning)
            assert "deprecated" in str(w[-1].message)
