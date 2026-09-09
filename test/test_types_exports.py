"""Guard that types.py public exports don't silently regress."""

import tableauserverclient as TSC


def test_types_are_top_level_importable():
    for name in (
        "HyperAction",
        "HyperActionCondition",
        "HyperActionRow",
        "HyperActionTable",
        "FilePath",
        "FileObjectR",
        "FileObjectW",
        "PathOrFileR",
        "PathOrFileW",
        "AddResponse",
        "HasIdpConfigurationID",
    ):
        assert hasattr(TSC, name), f"missing {name}"
        assert name in TSC.__all__, f"{name} not in __all__"


def test_add_response_shape():
    # namedtuple contract that samples/users depend on
    assert TSC.AddResponse._fields == ("result", "error", "warnings", "task_created")
