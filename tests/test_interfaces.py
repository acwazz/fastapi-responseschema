import pytest
from typing import Any, TypeVar, Generic
from pydantic import BaseModel
from fastapi import Request
from fastapi_responseschema.interfaces import AbstractResponseSchema
from fastapi_responseschema.exceptions import NotFound

T = TypeVar("T")


class AResponseModel(BaseModel):
    id: int
    name: str


class AResponseSchema(AbstractResponseSchema[T], Generic[T]):
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


WrappedResponseModel = AResponseSchema[AResponseModel]


@pytest.fixture
def fake_request():
    return Request({
        "type": "http",
        "body": b"",
        "more_body": False,
    })

def test_from_exception():
    exc = NotFound(detail="oh no!", headers={"X-Error-H": "NotFound"})
    resp = WrappedResponseModel.from_exception(
        reason=exc.detail,
        status_code=exc.status_code
    )
    assert resp.error
    assert resp.data == exc.detail


def test_from_exception_handler(fake_request):
    exc = NotFound(detail="oh no!", headers={"X-Error-H": "NotFound"})
    resp = WrappedResponseModel.from_exception_handler(request=fake_request, exception=exc)
    assert resp.error
    assert resp.data == exc.detail


def test_from_api_route_params():
    resp = WrappedResponseModel.from_api_route_params(content="hello", status_code=201)
    assert not resp.error
    assert resp.data == "hello"
