---
hide:
  - footer
---
Once you have created your response schemas you can define the `SchemaAPIRoute` that will be used for your API set.

A `SchemaAPIRoute` just inherits from `fastapi.routing.APIRoute`.

```py
from fastapi_responseschema import SchemaAPIRoute
from .myschemas import StandardResponseSchema  # The response schema you defined

class StandardAPIRoute(SchemaAPIRoute):
    response_schema = StandardResponseSchema  # This attribute is required
```

If you want to handle different schemas for success and error responses you can set the error response schema.

```py
from fastapi_responseschema import SchemaAPIRoute
from .myschemas import OKResponseSchema, KOResponseSchema   # The response schemas you defined

class StandardAPIRoute(SchemaAPIRoute):
    response_schema = OKResponseSchema  # This attribute is required
    error_response_schema = KOResponseSchema  # If not set defaults to `SchemaAPIRoute.response_schema`
```

### Integrating in your API

You can set the defined `SchemaAPIRoute` in you FastAPI application.

```py
from fastapi import FastAPI
from .myroutes import StandardAPIRoute  # the SchemaAPIRoute you defined

app = FastAPI()

app.router.route_class = StandardAPIRoute

@app.get("/")
def just_a_route():
    return {"message": "It Works!"}
```

You can even integrate the schema api route in `APIRouter`.

```py
from pydantic import BaseModel
from fastapi import APIRouter
from .myroutes import StandardAPIRoute  # the SchemaAPIRoute you defined

router = APIRouter(route_class=StandardAPIRoute)

class ParrotMessage(BaseModel):
    message: str


@router.post("/parrot")
def repeat(body: ParrotMessage):
    return {"parrot_says": body.message}
```

### Handling errors
You can wrap all error responses with the `wrap_error_responses` helper.

```py
from fastapi import FastAPI
from fastapi_responseschema import wrap_error_responses
from .myroutes import StandardAPIRoute
from .myschemas import KOResponseSchema

app = FastAPI()

app.router.route_class = StandardAPIRoute
wrap_error_responses(app, error_response_schema=KOResponseSchema)

@app.get("/")
def just_a_route():
    return {"message": "It Works!"}
```


### Handling errors and override application APIRoute
The same functionality as:
```py
...

app.router.route_class = StandardAPIRoute
wrap_error_responses(app, error_response_schema=KOResponseSchema)

...
```

Can be achieved with `wrap_app_responses`:
```py
from fastapi import FastAPI
from fastapi_responseschema import wrap_app_responses
from .myroutes import StandardAPIRoute  # the SchemaAPIRoute you defined

app = FastAPI()

wrap_app_responses(app, route_class=StandardAPIRoute)

@app.get("/")
def just_a_route():
    return {"message": "It Works!"}
```

> You still need to configure the route class for every `fastapi.APIRouter`.

### About `response_model_exclude`, `response_model_include` and others `response_model_*` parametrs
When using response fields modifiers on-the-fly. you must consider that the final output of `response_model` will be wrapped by the configured ResponseSchema.

For this snippet:
```py
from typing import TypeVar, Generic
from pydantic import BaseModel
from fastapi import APIRouter
from fastapi_responseschema import AbstractResponseSchema, SchemaAPIRoute

T = TypeVar("T")

class ResponseSchema(AbstractResponseSchema[T], Generic[T]):
    data: T
    error: bool
    message: Optional[str]

    ... # constructors etc.

class Item(BaseModel):
    id: int
    name: str
    additional_desc: Optional[str]

class MainAPIRoute(SchemaAPIRoute):
    response_schema = ResponseSchema

router = APIRouter(route_class=MainAPIRoute)

@router.get("/item", response_model=Item)
def show_item():
    return {"id": 11, "name": "Just a Teapot!"}
```

The resulting response payload of `GET /items` will be:
```json
{
    "data": {
        "id": 11, 
        "name": "Just a Teapot!",
        "additional_desc": null
    },
    "error": false,
    "message": null
}
```

When applying the `response_model_exclude` and `additional_model_include` for the `response_model` remeber to consider the nested output.

For Example:
```py
...

@router.get("/item", response_model=Item, response_model_exclude={"data": {"name"}})  # Exclusion of nested fields
def show_item():
    return {"id": 11, "name": "Just a Teapot!"}
```
Returns:

```json
{
    "data": {
        "id": 11, 
        "additional_desc": null
    },
    "error": false,
    "message": null
}
```

When you use `response_model_exclude_none` and similar parameters the configuration will be applyed to all the response schema.

For example:
```py
...

@router.get("/item", response_model=Item, response_model_exclude_none=True)  # Exclusion of nested fields
def show_item():
    return {"id": 11, "name": "Just a Teapot!"}
```
Returns:

```json
{
    "data": {
        "id": 11, 
        "name": "Just a Teapot!"
    },
    "error": false
}
```

> To modify the response content you should prefer the definition of dedicated models.