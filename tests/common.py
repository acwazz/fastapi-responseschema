from typing import TypeVar, Generic
from pydantic import BaseModel
from fastapi_responseschema.interfaces import AbstractResponseSchema


T = TypeVar("T")


class AResponseModel(BaseModel):
    id: int
    name: str


class SimpleResponseSchema(AbstractResponseSchema[T], Generic[T]):
    data: T
    error: bool

    @classmethod
    def from_exception(cls, reason: T, status_code: int, **others):
        return cls(data=reason, error=status_code >= 400)

    @classmethod
    def from_api_route(cls, content: T, status_code: int, **others):
        return cls(data=content, error=status_code >= 400)


class SimpleErrorResponseSchema(AbstractResponseSchema[T], Generic[T]):
    reason: T
    error: bool = True

    @classmethod
    def from_exception(cls, reason: T, status_code: int, **others):
        return cls(reason=reason, error=status_code >= 400)

    @classmethod
    def from_api_route(cls, content: T, status_code: int, **others):
        return cls(reason=content, error=status_code >= 400)
