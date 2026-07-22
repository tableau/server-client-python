import io
import os
from collections import namedtuple
from typing import Literal, Protocol, TypedDict

# File path and object type aliases used across publish/download methods
FilePath = str | os.PathLike
FileObject = io.BufferedReader | io.BytesIO
FileObjectR = io.BufferedReader | io.BytesIO
FileObjectW = io.BufferedWriter | io.BytesIO
PathOrFile = FilePath | FileObject
PathOrFileR = FilePath | FileObjectR
PathOrFileW = FilePath | FileObjectW


# Hyper action types for Datasources.update_hyper_data()
HyperActionCondition = TypedDict(
    "HyperActionCondition",
    {
        "op": str,
        "target-col": str,
        "source-col": str,
    },
)

HyperActionRow = TypedDict(
    "HyperActionRow",
    {
        "action": Literal["update", "upsert", "delete"],
        "source-table": str,
        "target-table": str,
        "condition": HyperActionCondition,
    },
)

HyperActionTable = TypedDict(
    "HyperActionTable",
    {
        "action": Literal["insert", "replace"],
        "source-table": str,
        "target-table": str,
    },
)

HyperAction = HyperActionTable | HyperActionRow


# Return type for Schedules.add_to_schedule()
AddResponse = namedtuple("AddResponse", ("result", "error", "warnings", "task_created"))


# IDP types for OIDC endpoint
class IDPAttributes(Protocol):
    idp_configuration_id: str


class IDPProperty(Protocol):
    @property
    def idp_configuration_id(self) -> str: ...


HasIdpConfigurationID = str | IDPAttributes
