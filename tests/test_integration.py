from fastapi import FastAPI, APIRouter
from fastapi.testclient import TestClient
from fastapi_responseschema import SchemaAPIRoute, wrap_app_responses
from .common import SimpleResponseSchema


class Route(SchemaAPIRoute):
    response_schema = SimpleResponseSchema


app_wrapped_no_router = FastAPI()

wrap_app_responses(app_wrapped_no_router, Route)


@app_wrapped_no_router.get("/wrapped", response_model=bool)
def wrapped_call_first():
    return True


router_unwrapped = APIRouter()


@router_unwrapped.get("/unwrapped", response_model=dict)
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


app_not_wrapped = FastAPI()


@app_not_wrapped.get("/unwrapped", response_model=dict)
def un_wrapped_call_second():
    return {"unwrapped": True}


router_wrapped = APIRouter(route_class=Route)


@router_wrapped.get("/wrapped", response_model=dict)
def wrapped_call_second():
    return {"wrapped": True}


app_not_wrapped.include_router(router_wrapped)

client_app_not_wrapped = TestClient(app_not_wrapped)


def test_not_recursive_wrapping_on_router():
    r = client_app_not_wrapped.get("/wrapped")
    resp = r.json()
    assert resp.get("data").get("wrapped")
    assert not resp.get("error")


def test_app_unwrapped_call():
    r = client_app_wrapped_no_router.get("/unwrapped")
    resp = r.json()
    assert resp.get("unwrapped")
