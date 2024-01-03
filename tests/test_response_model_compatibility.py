from __future__ import annotations
from typing import Any
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


@app.get("/model-exclude", response_model=RModel, response_model_exclude={"data": {"name"}})
def filter_via_response_model_exclude() -> dict[str, str]:
    return {"id": "1", "name": "excluded"}


@app.get("/model-filters", response_model=RModel)
def filter_via_response_model_schema() -> dict[str, Any]:
    return {"id": "1", "name": "ok", "hidden": True}


client = TestClient(app)


def test_response_model_exclude_works() -> None:
    r = client.get("/model-exclude")
    assert r.json() == {"error": False, "data": {"id": "1"}}


def test_inner_response_model_schema_not_overridden() -> None:
    r = client.get("/model-filters")
    assert r.json() == {"error": False, "data": {"id": "1", "name": "ok"}}
