from typing import Generic, TypeVar, Any, Optional, Type, Sequence
from pydantic import BaseModel
from fastapi import FastAPI
from fastapi_responseschema import AbstractResponseSchema, wrap_app_responses
from fastapi_responseschema.integrations.pagination import AbstractPagedResponseSchema, PaginationMetadata, PagedSchemaAPIRoute, PaginationParams
from fastapi_pagination import paginate, add_pagination

T = TypeVar("T")


# Build your "Response Schema"
class ResponseMetadata(BaseModel):
    error: bool
    message: Optional[str]
    pagination: Optional[PaginationMetadata]


class ResponseSchema(AbstractResponseSchema[T], Generic[T]):
    data: Any
    meta: ResponseMetadata

    @classmethod
    def from_exception(cls, reason, status_code, message: str = "Error", **others):
        return cls(
            data=reason,
            meta=ResponseMetadata(error=status_code >= 400, message=message)
        )

    @classmethod
    def from_api_route_params(cls, content: Any, status_code: int, description: Optional[str] = None, **others):
        return cls(
            data=content,
            meta=ResponseMetadata(error=status_code >= 400, message=description)
        )


class PagedResponseSchema(AbstractPagedResponseSchema[T], Generic[T]):
    data: Any
    meta: ResponseMetadata

    @classmethod
    def create(
            cls,
            items: Sequence[T],
            total: int,
            params: PaginationParams,
    ) -> 'PagedResponseSchema':
        return cls(
            data=items,
            meta=ResponseMetadata(
                error=False, 
                pagination=PaginationMetadata.from_abstract_page_create(total=total, params=params)
            )
        )

    @classmethod
    def from_exception(cls, reason, status_code, message: str = "Error", **others):
        return cls(
            data=reason,
            meta=ResponseMetadata(error=status_code >= 400, message=message)
        )

    @classmethod
    def from_api_route_params(cls, content: Any, status_code: int, description: Optional[str] = None, **others):
        return cls(error=status_code >= 400, data=content.data, meta=content.meta)

# Create an APIRoute
class Route(PagedSchemaAPIRoute):
    response_schema = ResponseSchema
    paged_response_schema = PagedResponseSchema

# Setup you FastAPI app
app = FastAPI(debug=True)
wrap_app_responses(app, Route)


class Item(BaseModel):
    id: int
    name: str


@app.get("/", response_model=PagedResponseSchema[Item], description="This is a route")
def get_operation():
    page = paginate([Item(id=0, name="ciao"), Item(id=1, name="hola"), Item(id=1, name="hello")])
    print(page)
    return page

add_pagination(app)


