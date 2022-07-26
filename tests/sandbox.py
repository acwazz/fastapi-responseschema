from typing import Generic, TypeVar, Any, Optional
import uvicorn
from pydantic import BaseModel
from fastapi import FastAPI
from fastapi_responseschema import AbstractResponseSchema, SchemaAPIRoute, wrap_app_responses
from fastapi_pagination import paginate, Page, Params


class Item(BaseModel):
    id: int
    name: str


T = TypeVar("T")


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


class Route(SchemaAPIRoute):
    response_schema = ResponseSchema


app = FastAPI()
wrap_app_responses(app, Route)

@app.get("/", response_model=Page[Item], description="This is a route")
def get_operation():
    return paginate([Item(id=0, name="ddd"), Item(id=1, name="ciao")])






if __name__ == "__main__":
    uvicorn.run("tests.sandbox:app", reload=True)


