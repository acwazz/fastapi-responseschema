# ☄️ FastAPI Response Schema
[![PyPI](https://img.shields.io/pypi/v/fastapi-responseschema)](https://pypi.org/project/fastapi-responseschema/) [![PyPI - Python Version](https://img.shields.io/pypi/pyversions/fastapi-responseschema)](https://pypi.org/project/fastapi-responseschema/) [![GitHub code size in bytes](https://img.shields.io/github/languages/code-size/acwazz/fastapi-responseschema)](https://github.com/acwazz/fastapi-responseschema/releases) [![Commits](https://img.shields.io/github/last-commit/acwazz/fastapi-responseschema)](https://github.com/acwazz/fastapi-responseschema/commit/master) [![Tests](https://github.com/acwazz/fastapi-responseschema/actions/workflows/test.yml/badge.svg)](https://github.com/acwazz/fastapi-responseschema/actions/workflows/test.yml)[![Lint](https://github.com/acwazz/fastapi-responseschema/actions/workflows/lint.yml/badge.svg)](https://github.com/acwazz/fastapi-responseschema/actions/workflows/lint.yml)

> FastAPI Response Schema is in production now! 

## Overview
This package extends the [FastAPI](https://fastapi.tiangolo.com/) response model schema allowing you to have a common response wrapper via a `fastapi.routing.APIRoute`.

This library supports Python versions **>=3.8** and FastAPI versions **>=0.66.0**.


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

```py
from typing import Generic, TypeVar, Any, Optional, List
from pydantic import BaseModel
from fastapi import FastAPI
from fastapi_responseschema import AbstractResponseSchema, SchemaAPIRoute, wrap_app_responses


# Build your "Response Schema"
class ResponseMetadata(BaseModel):
    error: bool
    message: Optional[str]


T = TypeVar("T")


class ResponseSchema(AbstractResponseSchema[T], Generic[T]):
    data: T
    meta: ResponseMetadata

    @classmethod
    def from_exception(cls, reason, status_code, message: str = "Error", **others):
        return cls(
            data=reason,
            meta=ResponseMetadata(error=status_code >= 400, message=message)
        )

    @classmethod
    def from_api_route(
        cls, content: Any, status_code: int, description: Optional[str] = None, **others
    ):
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


@app.get("/items", response_model=List[Item], description="This is a route")
def get_operation():
    return [Item(id=1, name="ciao"), Item(id=2, name="hola"), Item(id=3, name="hello")]
```

Te result of `GET /items`:
```http
HTTP/1.1 200 OK
content-length: 131
content-type: application/json

{
    "data": [
        {
            "id": 1,
            "name": "ciao"
        },
        {
            "id": 2,
            "name": "hola"
        },
        {
            "id": 3,
            "name": "hello"
        }
    ],
    "meta": {
        "error": false,
        "message": "This is a route"
    }
}
```


## Docs
You can find detailed info for this package in the [Documentation](https://acwazz.github.io/fastapi-responseschema/).



## Contributing

Contributions are very welcome!

### How to contribute
Just open an issue or submit a pull request on [GitHub](https://github.com/acwazz/fastapi-responseschema).

While submitting a pull request describe what changes have been made.

More info on [Docs section](https://acwazz.github.io/fastapi-responseschema/contributing/)

## Contributors Wall
[![Contributors Wall](https://contrib.rocks/image?repo=acwazz/fastapi-responseschema)](https://github.com/acwazz/fastapi-responseschema/graphs/contributors)
