from typing import Any, TypeVar, Generic
from pydantic import BaseModel
from fastapi_responseschema.interfaces import AbstractResponseSchema


T = TypeVar("T")


class AResponseModel(BaseModel):
    id: int
    name: str


class SimpleResponseSchema(AbstractResponseSchema[T], Generic[T]):
    data: Any
    error: bool

    @classmethod
    def from_exception(cls, reason, status_code, **others):
        return cls(
            data=reason,
            error=status_code >= 400
        )

    @classmethod
    def from_api_route_params(cls, content: Any, status_code: int, **others):
        return cls(
            data=content,
            error=status_code >= 400
        )

class SimpleErrorResponseSchema(AbstractResponseSchema[T], Generic[T]):
    reason: Any
    error: bool = True

    @classmethod
    def from_exception(cls, reason, status_code, **others):
        return cls(
            reason=reason,
            error=status_code >= 400
        )

    @classmethod
    def from_api_route_params(cls, content: Any, status_code: int, **others):
        return cls(
            reason=content,
            error=status_code >= 400
        )


SimpleWrappedResponseModel = SimpleResponseSchema[AResponseModel]