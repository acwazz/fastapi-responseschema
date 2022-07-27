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

You can of course integrate the schema api route in `APIRouter`.

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



