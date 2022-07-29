from typing import Generic, TypeVar, Any, Optional, Type, get_args
from pydantic import BaseModel
from fastapi import FastAPI
from fastapi_responseschema import AbstractResponseSchema, SchemaAPIRoute, wrap_app_responses
from fastapi_pagination import paginate, Page, add_pagination

T = TypeVar("T")


# Build your "Response Schema"
class ResponseMetadata(BaseModel):
    error: bool
    message: Optional[str]


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

    def override_response_model(self, wrapper_model: Type[AbstractResponseSchema[Any]], response_model: Type[Any]) -> Type[AbstractResponseSchema[Any]]:
        print(response_model.__parameters__)
        return super().override_response_model(wrapper_model, response_model)
    
    def _wrap_endpoint_output(self, endpoint_output: Any, wrapper_model: Type[AbstractResponseSchema], response_model: Type[Any], **params) -> Any:
        print(endpoint_output)
        return super()._wrap_endpoint_output(endpoint_output, wrapper_model, response_model, **params)

# Setup you FastAPI app
app = FastAPI(debug=True)
wrap_app_responses(app, Route)


class Item(BaseModel):
    id: int
    name: str


@app.get("/", response_model=Page[Item], description="This is a route")
def get_operation():
    page = paginate([Item(id=0, name="ciao"), Item(id=1, name="hola"), Item(id=1, name="hello")])
    print(page)
    return page

add_pagination(app)

