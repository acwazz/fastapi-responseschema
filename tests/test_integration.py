from fastapi import FastAPI, APIRouter
from fastapi.testclient import TestClient
from fastapi_responseschema import SchemaAPIRoute, wrap_app_responses
from .common import SimpleResponseSchema

class Route(SchemaAPIRoute):
    response_schema = SimpleResponseSchema

app_wrapped_no_router = FastAPI()

wrap_app_responses(app_wrapped_no_router, Route)

@app_wrapped_no_router.get("/wrapped", response_schema=bool)
def wrapped_call_first():
    return True


router_unwrapped = APIRouter()
@router_unwrapped.get("/unwrapped", response_schema=dict)
def unwrapped_call_first():
    return {"unwrapped": True}

app_wrapped_no_router.include_router(router_unwrapped)

client_app_wrapped_no_router = TestClient(app_wrapped_no_router)


def test_app_wrapped_call():
    r = client_app_wrapped_no_router.get("/wrapped")
    resp = r.json()
    assert resp.get("data")
    assert not resp.get("error")


def test_router_unwrapped_call():
    r = client_app_wrapped_no_router.get("/unwrapped")
    resp = r.json()
    assert resp.get("unwrapped")

