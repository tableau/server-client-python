from copy import deepcopy
from typing import Any, Generic, Mapping, Optional, TypeVar, Union
from urllib.parse import unquote_plus

T = TypeVar("T", )

def fix_filename(params: Mapping[str, T]) -> Mapping[str, T]:
    if "filename*" not in params:
        return params
    
    params = deepcopy(params)
    filename = params["filename*"]
    prefix = "UTF-8''"
    if filename.startswith(prefix):
        filename = filename[len(prefix):]

    params["filename"] = unquote_plus(filename)
    del params["filename*"]
    return params