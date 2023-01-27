from __future__ import annotations
import asyncio
from typing import Callable, Optional, Any, Type, List, Sequence, Dict, Union, Set
from functools import wraps
from pydantic.utils import lenient_issubclass, lenient_isinstance
from starlette.routing import BaseRoute
from fastapi import params, Response
from fastapi.encoders import DictIntStrAny, SetIntStr
from fastapi.routing import APIRoute
from fastapi.responses import JSONResponse
from fastapi.datastructures import DefaultPlaceholder, Default
from .interfaces import AbstractResponseSchema, ResponseWithMetadata


class SchemaAPIRoute(APIRoute):
    """An APIRoute class to wrap response_model(s) with a ResponseSchema
    Must be subclassed setting at least SchemaAPIRoute.response_model.

    Usage:

        from typing import Generic, TypeVar
        from fastapi_responseschema.interfaces import AbstractResponseSchema

        T = TypeVar("T")
        class MyResponseSchema(AbstractResponseSchema[T], Generic[T]):
            ...

        class MyAPIRoute(SchemaAPIRoute):
            response_schema = MyResponseSchema

        from fastapi import APIRouter

        router = APIRouter(route_class=MyAPIRoute)
    """

    response_schema: Type[AbstractResponseSchema[Any]]
    error_response_schema: Optional[Type[AbstractResponseSchema[Any]]] = None

    def __init_subclass__(cls) -> None:
        if not hasattr(cls, "response_schema"):
            raise AttributeError("`response_schema` must be defined in subclass.")
        return super().__init_subclass__()

    def is_error_state(self, status_code: Optional[int] = None) -> bool:
        """Handles the error_state for the operation evaluating the status_code.
        This method gets called internally and can be overridden to modify the error state of the operation.

        Args:
            status_code (Optional[int], optional): Operation status code. Defaults to None.

        Returns:
            bool: wether or not the operation returns an error
        """
        return (status_code >= 400) if status_code else False

    def get_wrapper_model(self, is_error: bool, response_model: Type[Any]) -> Type[AbstractResponseSchema[Any]]:
        """Implements the ResponseSchema selection logic.
        This method gets called internally and can be overridden to gain control over the ResponseSchema selection logic.

        Args:
            is_error (int): wheteher or not the operation returns an error.
            response_model (Type[Any]): response_model set for APIRoute.

        Returns:
            Type[AbstractResponseSchema[Any]]: The ResponseSchema to wrap the response_model.
        """
        if not self.error_response_schema:
            return self.response_schema
        return self.error_response_schema if is_error else self.response_schema

    def override_response_model(
        self, wrapper_model: Type[AbstractResponseSchema[Any]], response_model: Type[Any]
    ) -> Type[AbstractResponseSchema[Any]]:
        """Wraps the given response_model with the ResponseSchema.
        This method gets called internally and can be overridden to gain control over the response_model wrapping logic.

        Args:
            wrapper_model (Type[AbstractResponseSchema[Any]]): ResponseSchema Model
            response_model (Type[Any]): response_model set for APIRoute
            response_model_include (Optional[Union[SetIntStr, DictIntStrAny]], optional): Pydantic BaseModel include. Defaults to None.
            response_model_exclude (Optional[Union[SetIntStr, DictIntStrAny]], optional): Pydantic BaseModel exclude. Defaults to None.

        Returns:
            Type[AbstractResponseSchema[Any]]: The response_model wrapped in response_schema
        """
        # due to: https://github.com/python/mypy/issues/12392 FIXME: when gets fixed
        return wrapper_model[response_model]  # type: ignore

    def _wrap_endpoint_output(
        self,
        endpoint_output: Any,
        wrapper_model: Type[AbstractResponseSchema],
        response_model: Type[Any],
        **params: Any,
    ) -> Any:
        if lenient_isinstance(endpoint_output, ResponseWithMetadata):  # Handling the `respond` function
            params.update(endpoint_output.metadata)
            content = endpoint_output.response_content
        else:
            content = endpoint_output
        params["status_code"] = params.get("status_code") or 200
        # due to: https://github.com/python/mypy/issues/12392 FIXME: when gets fixed
        wrapped_model = wrapper_model[response_model]  # type: ignore
        return wrapped_model.from_api_route(
            content=content,
            response_model=response_model,
            **params,
        )

    def _create_endpoint_handler_decorator(
        self, wrapper_model: Type[AbstractResponseSchema], response_model: Type[Any], **params: Any
    ) -> Callable:
        def decorator(func: Callable) -> Callable:
            if asyncio.iscoroutinefunction(func):  # Not blocking asncyio loop

                @wraps(func)
                async def wrapper(*args: Any, **kwargs: Any) -> Any:
                    endpoint_output = await func(*args, **kwargs)
                    return self._wrap_endpoint_output(
                        endpoint_output=endpoint_output,
                        wrapper_model=wrapper_model,
                        response_model=response_model,
                        **params,
                    )

            else:

                @wraps(func)
                def wrapper(*args: Any, **kwargs: Any) -> Any:
                    endpoint_output = func(*args, **kwargs)
                    return self._wrap_endpoint_output(
                        endpoint_output=endpoint_output,
                        response_model=response_model,
                        wrapper_model=wrapper_model,
                        **params,
                    )

            return wrapper

        return decorator

    def __init__(
        self,
        path: str,
        endpoint: Callable,
        *,
        response_model: Optional[Type[Any]] = None,
        status_code: int = 200,
        tags: Optional[List[Any]] = None,
        dependencies: Optional[Sequence[params.Depends]] = None,
        summary: Optional[str] = None,
        description: Optional[str] = None,
        response_description: str = "Successful Response",
        responses: Optional[Dict[Union[int, str], Dict[str, Any]]] = None,
        deprecated: Optional[bool] = None,
        name: Optional[str] = None,
        methods: Optional[Union[Set[str], List[str]]] = None,
        operation_id: Optional[str] = None,
        response_model_include: Optional[Union[SetIntStr, DictIntStrAny]] = None,
        response_model_exclude: Optional[Union[SetIntStr, DictIntStrAny]] = None,
        response_model_by_alias: bool = True,
        response_model_exclude_unset: bool = False,
        response_model_exclude_defaults: bool = False,
        response_model_exclude_none: bool = False,
        include_in_schema: bool = True,
        response_class: Union[Type[Response], DefaultPlaceholder] = Default(JSONResponse),
        dependency_overrides_provider: Optional[Any] = None,
        callbacks: Optional[List["BaseRoute"]] = None,
        **kwargs: Any,
    ) -> None:
        if response_model and not lenient_issubclass(
            response_model, AbstractResponseSchema
        ):  # If a `response_model` is set, then wrap the `response_model` with a response schema
            WrapperModel = self.get_wrapper_model(
                is_error=self.is_error_state(status_code=status_code), response_model=response_model
            )
            endpoint_wrapper = self._create_endpoint_handler_decorator(
                path=path,
                wrapper_model=WrapperModel,
                response_model=response_model,
                status_code=status_code,
                tags=tags,
                summary=summary,
                description=description,
                response_description=response_description,
                deprecated=deprecated,
                name=name,
                methods=methods,
                operation_id=operation_id,
                response_model_include=response_model_include,
                response_model_exclude=response_model_exclude,
                response_model_by_alias=response_model_by_alias,
                response_model_exclude_unset=response_model_exclude_unset,
                response_model_exclude_defaults=response_model_exclude_defaults,
                response_model_exclude_none=response_model_exclude_none,
                include_in_schema=include_in_schema,
                response_class=response_class,
            )
            endpoint = endpoint_wrapper(endpoint)
            response_model = self.override_response_model(wrapper_model=WrapperModel, response_model=response_model)
        super().__init__(
            path,
            endpoint,
            response_model=response_model,
            status_code=status_code,
            tags=tags,
            dependencies=dependencies,
            summary=summary,
            description=description,
            response_description=response_description,
            responses=responses,
            deprecated=deprecated,
            name=name,
            methods=methods,
            operation_id=operation_id,
            response_model_include=response_model_include,
            response_model_exclude=response_model_exclude,
            response_model_by_alias=response_model_by_alias,
            response_model_exclude_unset=response_model_exclude_unset,
            response_model_exclude_defaults=response_model_exclude_defaults,
            response_model_exclude_none=response_model_exclude_none,
            include_in_schema=include_in_schema,
            response_class=response_class,
            dependency_overrides_provider=dependency_overrides_provider,
            callbacks=callbacks,
            **kwargs,
        )


def respond(response_content: Optional[Any] = None, **metadata: Any) -> ResponseWithMetadata:
    """Returns the response content with optional metadata

    Args:
        response_content (Optional[Any], optional): Response Content. Defaults to None.
        **metadata: Arbitrary metadata

    Returns:
        ResponseWithMetadata: An intermediate data structure to add metadatato a ResponseSchema serialization
    """
    _metadata = metadata or dict()
    return ResponseWithMetadata(metadata=_metadata, response_content=response_content)
