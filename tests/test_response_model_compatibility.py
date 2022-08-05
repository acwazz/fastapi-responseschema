from fastapi import FastAPI
from fastapi.testclient import TestClient
from fastapi_responseschema import SchemaAPIRoute, wrap_app_responses
from pydantic import BaseModel
from .common import SimpleResponseSchema


class RModel(BaseModel):
    id: str
    name: str


class Route(SchemaAPIRoute):
    response_schema = SimpleResponseSchema


app = FastAPI()


wrap_app_responses(app, Route)


@app.get("/model-exclude", response_model=RModel, response_model_exclude={"name"})
def wrapped_call_first():
    return {"id": 1, "name": "hiddenfield"}


@app.get("/model-filters", response_model=RModel)
def wrapped_call_first():
    return {"id": 1, "name": "hiddenfield", "hidden": True}


client = TestClient(app)


def test_response_model_exclude_preserved():
    r = client.get("/model-exclude")
    resp = r.json()
    assert not resp.get("error")
    assert resp.get("data").get("id") == 1
    assert not resp.get("data").get("name")


def test_response_model_filters():
    r = client.get("/model-filters")
    resp = r.json()
    assert not resp.get("error")
    assert resp.get("data").get("id") == 1
    assert resp.get("data").get("name")
    assert not resp.get("data").get("hidden")