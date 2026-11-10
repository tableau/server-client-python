import tableauserverclient as TSC
from tableauserverclient.server import server as server_module


def test_default_namespace_matches_server_namespace() -> None:
    # TSC.DEFAULT_NAMESPACE is a literal in __init__.py (importing it from server.py is circular).
    assert TSC.DEFAULT_NAMESPACE == server_module.NAMESPACE


def test_server_namespace_maps_t_prefix() -> None:
    server = TSC.Server("http://test", False)
    assert server.namespace == {"t": TSC.DEFAULT_NAMESPACE}


def test_server_namespace_is_a_copy() -> None:
    server = TSC.Server("http://test", False)
    server.namespace["t"] = "mutated"
    server.namespace["x"] = "extra"
    assert server.namespace == {"t": TSC.DEFAULT_NAMESPACE}
    assert TSC.Server("http://other", False).namespace == {"t": TSC.DEFAULT_NAMESPACE}
