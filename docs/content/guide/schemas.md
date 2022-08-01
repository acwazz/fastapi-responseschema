---
hide:
  - footer
---
Response schemas heavily rely on the concept of [pydantic GenericModel](https://pydantic-docs.helpmanual.io/usage/models/#generic-models).

In this way `response_model` can be wrapped by the `ResponseSchema` in the fastapi operation.

**`ResponseSchema` will wrap your response ONLY if you configured a `response_model` in your route operation.**

In order to create a response schema you need to make the class a [Generic](https://docs.python.org/3.8/library/typing.html#generics) type. 
```py
from typing import TypeVar, Generic
from fastapi_responseschema import AbstractResponseSchema

T = TypeVar("T")


class ResponseSchema(AbstractResponseSchema[T], Generic[T]):
    ...
```

## Constructors
When creating a response schema, constructors must be defined in subclass to ensure that the final response model gets correctly created and additional metadata can be passed to the final response.

### `AbstractResponseSchema.from_exception`
This constructor wraps the final response from an [exception handler](https://fastapi.tiangolo.com/tutorial/handling-errors/#install-custom-exception-handlers).
You can view the full parameter list [here](/api/interfaces/#from_exception).

### `AbstractResponseSchema.from_api_route_params`
This constructor wraps the final response when initializing an [APIRoute](https://fastapi.tiangolo.com/advanced/custom-request-and-route/?h=apiroute).
You can view the full parameter list [here](/api/interfaces/#from_api_route_params).


```py
from typing import TypeVar, Generic
from fastapi_responseschema import AbstractResponseSchema

T = TypeVar("T")


class ResponseSchema(AbstractResponseSchema[T], Generic[T]):
    data: Any
    error: bool
    message: str

    @classmethod
    def from_exception(cls, reason, status_code, message: str = "Error", **others):  # from an exception handler 
        return cls(
            data=reason,
            error=status_code >= 400, 
            message=message
        )

    @classmethod
    def from_api_route_params(
        cls, content: Any, status_code: int, description: Optional[str] = None, **others
    ):  # from an api route
        return cls(
            data=content,
            error=status_code >= 400, 
            description=description
        )
```

> Multiple response schemas can be built and composed in `SchemaAPIRoute` subclasses.