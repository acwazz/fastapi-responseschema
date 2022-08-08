import asyncio
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from fastapi.routing import APIRoute
from fastapi_responseschema.routing import respond, SchemaAPIRoute
from fastapi_responseschema.interfaces import ResponseWithMetadata
from .common import SimpleResponseSchema, SimpleErrorResponseSchema, AResponseModel


def test_respond_returns_type():
    out = respond()
    assert isinstance(out, ResponseWithMetadata)


def test_respond_returns_content():
    out = respond({"a": 1})
    assert out.response_content.get("a") == 1


def test_respond_returns_metadata():
    out = respond(None, first=1, second=2)
    assert out.metadata.get("first") == 1
    assert out.metadata.get("second") == 2


class TestSchemaAPIRouteOverridables:
    def test_wrong_subsclassing(self):
        with pytest.raises(AttributeError):

            class Route(SchemaAPIRoute):
                pass

    def test_is_api_route(self):
        class Route(SchemaAPIRoute):
            response_schema = SimpleResponseSchema

        r = Route("/", lambda: True)
        assert isinstance(r, APIRoute)
        assert issubclass(Route, APIRoute)

    def test_is_error_state(self):
        class Route(SchemaAPIRoute):
            response_schema = SimpleResponseSchema

        r = Route("/", lambda: False)
        assert r.is_error_state(status_code=405)
        assert not r.is_error_state(status_code=301)

    def test_get_wrapper_model(self):
        class Route(SchemaAPIRoute):
            response_schema = SimpleResponseSchema

        r = Route("/", lambda: False)
        assert r.get_wrapper_model(is_error=False, response_model=dict) == SimpleResponseSchema
        assert r.get_wrapper_model(is_error=True, response_model=dict) == SimpleResponseSchema

    def test_get_wrapper_model_with_error(self):
        class Route(SchemaAPIRoute):
            response_schema = SimpleResponseSchema
            error_response_schema = SimpleErrorResponseSchema

        r = Route("/", lambda: False)
        assert r.get_wrapper_model(is_error=False, response_model=dict) == SimpleResponseSchema
        assert r.get_wrapper_model(is_error=True, response_model=dict) == SimpleErrorResponseSchema

    def test_override_response_model(self):
        class Route(SchemaAPIRoute):
            response_schema = SimpleResponseSchema

        r = Route("/", lambda: False)
        assert (
            r.override_response_model(wrapper_model=r.response_schema, response_model=AResponseModel)
            == SimpleResponseSchema[AResponseModel]
        )


class SimpleRoute(SchemaAPIRoute):
    response_schema = SimpleResponseSchema
    error_response_schema = SimpleErrorResponseSchema


app = FastAPI()
app.router.route_class = SimpleRoute


@app.get("/")
def simple_route():
    return {"op": True}


@app.get("/with-model", response_model=AResponseModel)
def with_response_model():
    return {"id": 1, "name": "hello"}


@app.get("/as-error", response_model=AResponseModel, status_code=404)
def as_error():
    return {"id": 0, "name": ""}


@app.get("/respond", response_model=AResponseModel)
def responder():
    return respond({"id": 1, "name": "hello"})


@app.get("/async", response_model=AResponseModel)
async def async_route():
    await asyncio.sleep(0.001)
    return {"id": 1, "name": "hello"}


client = TestClient(app)


def test_legacy_behaviour():
    raw = client.get("/")
    r = raw.json()
    assert r.get("op")


def test_response_model_wrapping():
    raw = client.get("/with-model")
    r = raw.json()
    assert r.get("data").get("id") == 1
    assert r.get("data").get("name") == "hello"
    assert not r.get("error")


def test_response_as_error():
    raw = client.get("/as-error")
    r = raw.json()
    assert r.get("reason").get("id") == 0
    assert r.get("reason").get("name") == ""
    assert r.get("error")


def test_respond_in_operation():
    raw = client.get("/respond")
    r = raw.json()
    assert r.get("data").get("id") == 1
    assert r.get("data").get("name") == "hello"
    assert not r.get("error")


def test_async_behavior():
    raw = client.get("/async")
    r = raw.json()
    assert r.get("data").get("id") == 1
    assert r.get("data").get("name") == "hello"
    assert not r.get("error")
