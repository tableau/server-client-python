import pytest

import tableauserverclient as TSC


def test_username_password_required():
    with pytest.raises(TypeError):
        TSC.TableauAuth()
