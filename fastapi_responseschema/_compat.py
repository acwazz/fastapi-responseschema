from typing import Any, Dict, Set, Union

try:
    from fastapi.encoders import DictIntStrAny, SetIntStr  # type: ignore
except ImportError:
    SetIntStr = Set[Union[int, str]]
    DictIntStrAny = Dict[Union[int, str], Any]
