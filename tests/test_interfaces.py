from fastapi import Request
from fastapi_responseschema.exceptions import NotFound
from .common import SimpleWrappedResponseModel


def test_from_exception():
    exc = NotFound(detail="oh no!")
    resp = SimpleWrappedResponseModel.from_exception(reason=exc.detail, status_code=exc.status_code)
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
    resp = SimpleWrappedResponseModel.from_exception_handler(request=req, exception=exc)
    assert resp.error
    assert resp.data == exc.detail


def test_from_api_route_params():
    resp = SimpleWrappedResponseModel.from_api_route_params(content="hello", status_code=201)
    assert not resp.error
    assert resp.data == "hello"
