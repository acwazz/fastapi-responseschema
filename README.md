# ☄️ FastAPI Response Schema

## Overview
This package extends the [FastAPI](https://fastapi.tiangolo.com/) response model schema allowing you to have a common response wrapper via a `fastapi.routing.APIRoute`.


## Getting started

### Install the package
```sh
pip install fastapi-responseschema
```

If you are planning to use the pagination integration, you can install the package including [fastapi-pagination](https://github.com/uriyyo/fastapi-pagination)
```sh
pip install fastapi-responseschema[pagination]
```

### Usage

This is just a prelude:
```py
from typing import Generic, TypeVar, Any, Optional
from pydantic import BaseModel
from fastapi import FastAPI
from fastapi_responseschema import AbstractResponseSchema, SchemaAPIRoute, wrap_app_responses


# Build your "Response Schema"
class ResponseMetadata(BaseModel):
    error: bool
    message: Optional[str]


T = TypeVar("T")


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


# Create an APIRoute
class Route(SchemaAPIRoute):
    response_schema = ResponseSchema

# Integrate in FastAPI app
app = FastAPI()
wrap_app_responses(app, Route)

class Item(BaseModel):
    id: int
    name: str


@app.get("/", response_model=Item, description="This is a route")
def get_operation():
    return [Item(id=0, name="ciao"), Item(id=1, name="hola"), Item(id=1, name="hello")]
```

Te result of `GET /`:
```http
HTTP/1.1 200 OK
content-length: 131
content-type: application/json
date: Tue, 26 Jul 2022 22:25:43 GMT
server: uvicorn

{
    "data": [
        {
            "id": 0,
            "name": "ciao"
        },
        {
            "id": 1,
            "name": "hola"
        },
        {
            "id": 1,
            "name": "hello"
        }
    ],
    "meta": {
        "error": false,
        "message": "This is a route"
    }
}
```


