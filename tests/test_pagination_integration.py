from typing import TypeVar, Generic, Any, Sequence, Union
import pytest
from fastapi import FastAPI, APIRouter
from fastapi.testclient import TestClient
from fastapi_responseschema.integrations.pagination import (
    AbstractPagedResponseSchema,
    PagedSchemaAPIRoute,
    PaginationMetadata,
    PaginationParams,
)
from fastapi_pagination import paginate, add_pagination
from .common import SimpleResponseSchema


def test_paged_response_schema_inner_types():
    V = AbstractPagedResponseSchema[int]
    assert V.__inner_type__ == int


T = TypeVar("T")


class SimplePagedResponseSchema(AbstractPagedResponseSchema[T], Generic[T]):
    data: Union[Sequence[T], T]
    error: bool
    pagination: PaginationMetadata

    @classmethod
    def create(cls, items: Sequence[T], total: int, params: PaginationParams):
        return cls(
            data=items, error=False, pagination=PaginationMetadata.from_abstract_page_create(total=total, params=params)
        )

    @classmethod
    def from_exception(cls, reason, status_code, **others):
        return cls(data=reason, error=status_code >= 400)

    @classmethod
    def from_api_route(cls, content: Any, status_code: int, **others):
        return cls(error=status_code >= 400, data=content.data, pagination=content.pagination)


def test_get_wrapper_model_pagination_success():
    class Route(PagedSchemaAPIRoute):
        response_schema = SimpleResponseSchema
        paged_response_schema = SimplePagedResponseSchema

    r = Route("/", lambda: [True, False, True], response_model=SimplePagedResponseSchema[bool])
    assert (
        r.get_wrapper_model(is_error=False, response_model=SimplePagedResponseSchema[bool]) == SimplePagedResponseSchema
    )


def test_get_wrapper_model_pagination_error_fallaback():
    class Route(PagedSchemaAPIRoute):
        response_schema = SimpleResponseSchema
        paged_response_schema = SimplePagedResponseSchema

    r = Route("/", lambda: [True, False, True], response_model=SimplePagedResponseSchema[bool])
    assert (
        r.get_wrapper_model(is_error=True, response_model=SimplePagedResponseSchema[bool]) == SimplePagedResponseSchema
    )


def test_get_wrapper_model_pagination_error():
    class Route(PagedSchemaAPIRoute):
        response_schema = SimpleResponseSchema
        paged_response_schema = SimplePagedResponseSchema
        error_response_schema = SimpleResponseSchema

    r = Route("/", lambda: [True, False, True], response_model=SimplePagedResponseSchema[bool])
    assert r.get_wrapper_model(is_error=True, response_model=SimplePagedResponseSchema[bool]) == SimpleResponseSchema


def test_get_wrapper_model_no_pagination():
    class Route(PagedSchemaAPIRoute):
        response_schema = SimpleResponseSchema
        paged_response_schema = SimplePagedResponseSchema

    r = Route("/", lambda: True, response_model=bool)
    assert r.get_wrapper_model(is_error=False, response_model=bool) == SimpleResponseSchema


def test_wrong_subsclassing_paged_schema():
    with pytest.raises(AttributeError):

        class Route(PagedSchemaAPIRoute):
            response_schema = SimpleResponseSchema


def test_subsclassing_response_schema_is_none():
    with pytest.raises(AttributeError):

        class Route(PagedSchemaAPIRoute):
            response_schema = None
            paged_response_schema = SimplePagedResponseSchema


def test_subsclassing_response_schema_is_unset():
    with pytest.raises(AttributeError):

        class Route(PagedSchemaAPIRoute):
            paged_response_schema = SimplePagedResponseSchema


class Route(PagedSchemaAPIRoute):
    response_schema = SimpleResponseSchema
    paged_response_schema = SimplePagedResponseSchema


app = FastAPI()
app.router.route_class = Route


@app.get("/with-model", response_model=SimplePagedResponseSchema[bool])
def with_response_model():
    return paginate([True, False, True, False])


router = APIRouter(route_class=Route)


@router.get("/with-router", response_model=SimplePagedResponseSchema[bool])
def with_router():
    return paginate([True, False, True, False])


app.include_router(router)

add_pagination(app)

client = TestClient(app)


def test_response_model_paginated_wrapping_in_app():
    raw = client.get("/with-model")
    r = raw.json()
    assert not r.get("data")[1]
    assert r.get("pagination").get("total") == 4
    assert not r.get("error")


def test_response_model_paginated_wrapping_in_router():
    raw = client.get("/with-router")
    r = raw.json()
    assert not r.get("data")[1]
    assert r.get("pagination").get("total") == 4
    assert not r.get("error")
