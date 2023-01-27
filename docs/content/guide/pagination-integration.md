---
hide:
  - footer
---

FastAPI Response Schema integrates with [FastAPI Pagination](https://github.com/uriyyo/fastapi-pagination) to handle pagination logic without reinventig the wheel.

However, you can implement your own pagination utilities and integrate them with FastaAPI Response Schema.


## PagedResponseSchema
A `PagedResponseSchema` is a generic that inherits from `fastapi_pagination.base.AbstractPage` and `fastapi_responseschema.interfaces.AbstractResponseSchema`.

You can use this type of classes to handle pagination with a global response schema logic.

```py
from typing import Sequence, TypeVar, Any, Generic, Union
from fastapi_responseschema.integrations.pagination import AbstractPagedResponseSchema, PaginationMetadata, PagedSchemaAPIRoute, PaginationParams


class ResponseMetadata(BaseModel):
    error: bool
    message: Optional[str]
    pagination: Optional[PaginationMetadata]

T = TypeVar("T")

class PagedResponseSchema(AbstractPagedResponseSchema[T], Generic[T]):
    data: Union[Sequence[T], T]  # In case of error response we will pass a scalar type, a string or a dict
    meta: ResponseMetadata

    @classmethod
    def create(
            cls,
            items: Sequence[T],
            total: int,
            params: PaginationParams,
    ):  # This constructor gets called first and creates the FastAPI Pagination response model.
    # For fields that are not present in this method signature just set some defaults,
    # you will override them in the `from_api_route` constructor
        return cls(
            data=items,
            meta=ResponseMetadata(
                error=False,  
                pagination=PaginationMetadata.from_abstract_page_create(total=total, params=params)
            )
        )

    @classmethod
    def from_exception(cls, reason: T, status_code: int, **others):
        return cls(
            data=reason,
            meta=ResponseMetadata(error=status_code >= 400, message=message)
        )

    @classmethod
    def from_api_route(cls, content: Sequence[T], description: Optional[str] = None, **others): 
        # `content` parameter is the output from the `create` constructor.
        return cls(error=status_code >= 400, data=content.data, meta=content.meta)
```

## PagedSchemaAPIRoute

This is a SchemaAPIRoute that supports a `PagedResponseSchema` for paginated responses.

```py
from fastapi_responseschema.integrations.pagination import PagedSchemaAPIRoute

...

class PagedRoute(PagedSchemaAPIRoute):
    response_schema = ResponseSchema
    paged_response_schema = PagedResponseSchema

``` 
This `PagedSchemaAPIRoute` can be integrated in fastapi as a `SchemaAPIRoute`.


## Usage
The `AbstractPagedResponseSchema` class inherits from the `fastapi_pagination.bases.AbstractPage` and has to be used to configure the pagination correctly.


```py
from pydantic import BaseModel
from fastapi import FastAPI
from fastapi_pagination import paginate, add_pagination
from fastapi_responseschema import wrap_app_responses
from .myroutes import PagedRoute  # the SchemaAPIRoute you defined
from .myschemas import PagedResponseSchema  # the ResponseSchema you defined

app = FastAPI()
wrap_app_responses(app, route_class=PagedRoute)

class Bird(BaseModel):
    id: int


@app.get("/birds", response_model=PagedResponseSchema[Bird])
def list_birds_w_pagination():
    return paginate([Bird(id=n) for n in range(1, 3000)])

add_pagination(app)
```


## `PaginationParams` and `PaginationMetadata`

Just take a look at the [API documentation](/api/pagination-integration/#class-paginationmetadata) to learn more about.
