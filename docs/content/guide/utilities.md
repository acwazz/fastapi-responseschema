---
hide:
  - footer
---
### Additional metadata in the resulting response schema
If you need to add fields to the response schema that are not supported by [`AbstractResponseSchema.from_api_route_params`](/api/interfaces/#from_api_route_params), you can use the `respond` function.

```py
# schemas.py file
from typing import TypeVar, Generic
from fastapi_responseschema import AbstractResponseSchema

T = TypeVar("T")


class ResponseSchema(AbstractResponseSchema[T], Generic[T]):
    data: Any
    error: bool
    code: str  # From a `result_code` field, not natively supported by constructors

    @classmethod
    def from_exception(cls, reason, status_code, result_code: str = "Error", **others):
        return cls(
            data=reason,
            error=status_code >= 400, 
            code=result_code
        )

    @classmethod
    def from_api_route_params(
        cls, content: Any, status_code: int, result_code: Optional[str] = None, **others
    ):
        return cls(
            data=content,
            error=status_code >= 400, 
            code=result_code
        )

...

# api.py file
from fastapi import APIRouter
from fastapi_responseschema import respond
from .schemas import StandardAPIRoute  # the SchemaAPIRoute you defined

router = APIRouter(route_class=StandardAPIRoute)

class ParrotMessage(BaseModel):
    message: str


@router.post("/parrot")
def repeat(body: ParrotMessage):
    return respond({"parrot_says": body.message}, result_code="OK_PARROT_HEALTHY")
```

In a similar way, for fields that are not supported in [`AbstractResponseSchema.from_exception`](/api/interfaces/#from_exception) you can raise an exception with metadata:
```py
from fastapi_responseschema.exceptions import GenericHTTPException
...

@router.get("/faulty")
def repeat():
    raise GenericHTTPException(status_code=405, detail="This is a faulty service", result_code="KO_NOT_SUPPORTED")
```

### Exceptions
When developing a backend service usually we keep raising the same few excpetions with the same status code.
You can use the `exceptions` module to reduce a little bit the boilerplate code.

```py
from fastapi_responseschema.exceptions import MethodNotAllowed, Gone, NotFound

...

@router.get("/faulty")
def repeat():
    raise MethodNotAllowed(detail="This is a faulty service", result_code="KO_NOT_SUPPORTED")

@router.get("/ghost")
def ghost():
    raise Gone(detail="This resource is gone, forever.", result_code="KO_CREEPY_GONE")

@router.get("/nope")
def ghost():
    raise NotFound(detail="Nope man, can't help you", result_code="KO_NOT_FOUND")
```