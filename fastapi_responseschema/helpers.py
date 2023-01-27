from __future__ import annotations
from typing import Any, Type, Union
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from .routing import SchemaAPIRoute
from .exceptions import BaseGenericHTTPException
from .interfaces import AbstractResponseSchema


def wrap_error_responses(app: FastAPI, error_response_schema: Type[AbstractResponseSchema]) -> FastAPI:
    """Wraps all exception handlers with the provided response schema.

    Args:
        app (FastAPI): A FastAPI application instance.
        error_response_schema (Type[AbstractResponseSchema]): Response schema wrapper model.

    Returns:
        FastAPI: The application instance
    """

    async def exception_handler(
        request: Request, exc: Union[RequestValidationError, StarletteHTTPException, BaseGenericHTTPException]
    ) -> JSONResponse:
        status_code = getattr(exc, "status_code") if not isinstance(exc, RequestValidationError) else 422
        # due to: https://github.com/python/mypy/issues/12392 FIXME: when gets fixed
        model = error_response_schema[Any]  # type: ignore
        return JSONResponse(
            content=model.from_exception_handler(request=request, exception=exc).dict(),
            status_code=status_code,
            headers=getattr(exc, "headers", dict()),
        )

    app.add_exception_handler(RequestValidationError, exception_handler)
    app.add_exception_handler(StarletteHTTPException, exception_handler)
    app.add_exception_handler(BaseGenericHTTPException, exception_handler)
    return app


def wrap_app_responses(app: FastAPI, route_class: Type[SchemaAPIRoute]) -> FastAPI:
    """Wraps all app defaults responses

    Args:
        app (FastAPI): A FastAPI application instance.
        route_class (Type[SchemaAPIRoute]): The SchemaAPIRoute with your response schemas.

    Returns:
        FastAPI: The application instance.
    """
    app.router.route_class = route_class
    err_schema = getattr(route_class, "error_response_schema")
    if err_schema is None:
        err_schema = route_class.response_schema
    app = wrap_error_responses(app, error_response_schema=err_schema)
    return app
