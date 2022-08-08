from typing import Any
from fastapi import Request
from fastapi_responseschema.exceptions import NotFound
from .common import SimpleResponseSchema


def test_from_exception():
    exc = NotFound(detail="oh no!")
    resp = SimpleResponseSchema[Any].from_exception(reason=exc.detail, status_code=exc.status_code)
    assert resp.error
    assert resp.data == exc.detail


def test_from_exception_handler():
    req = Request(
        {
            "type": "http",
            "body": b"",
            "more_body": False,
        }
    )
    exc = NotFound(detail="oh no!")
    resp = SimpleResponseSchema[Any].from_exception_handler(request=req, exception=exc)
    assert resp.error
    assert resp.data == exc.detail


def test_from_api_route_params():
    resp = SimpleResponseSchema[dict].from_api_route_params(content={"hello": "world"}, status_code=201)
    assert not resp.error
    assert resp.data.get("hello") == "world"
