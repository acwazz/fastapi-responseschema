import pytest
from fastapi import FastAPI
from fastapi.exceptions import StarletteHTTPException
from fastapi.testclient import TestClient
from fastapi_responseschema import SchemaAPIRoute
from fastapi_responseschema.exceptions import GenericHTTPException
from fastapi_responseschema.helpers import wrap_app_responses

from .common import SimpleErrorResponseSchema, SimpleResponseSchema, AResponseModel


class Route(SchemaAPIRoute):
    response_schema = SimpleResponseSchema
    error_response_schema = SimpleErrorResponseSchema


app = FastAPI()
wrap_app_responses(app, Route)

client = TestClient(app)


@app.get("/", response_model=AResponseModel)
def wrapped():
    return {"id": 1, "name": "hello"}


@app.get("/exceptions/{code}")
def raise_exception(code: int):
    raise GenericHTTPException(status_code=code)


@app.get("/validation-error/{param}")
def raise_validation_error(param: int):
    return param


@app.get("/starlette-exception")
def raise_starlette_exception():
    raise StarletteHTTPException(400, "Error")


@pytest.mark.parametrize("status_code", [400, 401, 403, 404, 405, 409, 410, 422, 500])
def test_web_exceptions(status_code):
    response = client.get(f"/exceptions/{status_code}/")
    assert response.status_code == status_code


def test_starlette_exception():
    response = client.get("/starlette-exception")
    assert response.status_code == 400
    assert response.json().get("reason") == "Error"
    assert response.json().get("error")


def test_request_validation_error():
    response = client.get("/validation-error/invalid")
    assert response.status_code == 422
    assert response.json().get("error")


def test_response_model_wrapping():
    raw = client.get("/")
    r = raw.json()
    assert r.get("data").get("id") == 1
    assert r.get("data").get("name") == "hello"
    assert not r.get("error")


class Route2(SchemaAPIRoute):
    response_schema = SimpleResponseSchema


app2 = FastAPI()
wrap_app_responses(app2, Route2)

client2 = TestClient(app2)


@app2.get("/starlette-exception")
def raise_starlette_exception():
    raise StarletteHTTPException(400, "Error")


def test_fallback_error_schema():
    response = client2.get("/starlette-exception")
    assert response.status_code == 400
    assert response.json().get("data") == "Error"
    assert response.json().get("error")
