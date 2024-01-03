from typing import Any, Dict, Set, Union
from importlib.metadata import version
from pydantic import BaseModel  # noqa: E402

PYDANTIC_MAJOR = int(version("pydantic").split(".")[0])

try:
    from fastapi.encoders import DictIntStrAny, SetIntStr  # type: ignore
except ImportError:
    SetIntStr = Set[Union[int, str]]
    DictIntStrAny = Dict[Union[int, str], Any]


if PYDANTIC_MAJOR < 2:
    from pydantic.generics import GenericModel as PydanticGenericModel  # noqa: F401
    from pydantic.utils import lenient_issubclass, lenient_isinstance  # noqa: F401

    def model_to_dict(model: BaseModel) -> dict:
        return model.dict()

else:
    from pydantic import BaseModel as PydanticGenericModel  # noqa: F401
    from pydantic.v1.utils import lenient_issubclass, lenient_isinstance  # noqa: F401

    def model_to_dict(model: BaseModel) -> dict:
        return model.model_dump()
