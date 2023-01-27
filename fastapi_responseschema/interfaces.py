from __future__ import annotations
from typing import Optional, Any, Type, List, Union, Set, TypeVar, Generic, NamedTuple, ClassVar, Tuple
from dataclasses import dataclass
from abc import ABC, abstractmethod
from fastapi import Request, Response
from pydantic import BaseModel
from pydantic.generics import GenericModel
from fastapi.encoders import DictIntStrAny, SetIntStr
from fastapi.exceptions import RequestValidationError, HTTPException as FastAPIHTTPException
from starlette.exceptions import HTTPException as StarletteHTTPException
from .exceptions import BaseGenericHTTPException

T = TypeVar("T")
TResponseSchema = TypeVar("TResponseSchema", bound="AbstractResponseSchema")


@dataclass
class HTTPExceptionAdapter:
    reason: Any
    status_code: int
    headers: Optional[dict]
    extra_params: Any

    @classmethod
    def from_starlette_exc(cls, exc: StarletteHTTPException) -> "HTTPExceptionAdapter":
        return cls(
            status_code=exc.status_code, reason=getattr(exc, "detail", str(exc)), headers=None, extra_params=dict()
        )

    @classmethod
    def from_fastapi_exc(cls, exc: FastAPIHTTPException) -> "HTTPExceptionAdapter":
        return cls(
            status_code=exc.status_code,
            reason=getattr(exc, "detail", str(exc)),
            headers=exc.headers,
            extra_params=dict(),
        )

    @classmethod
    def from_request_validation_err(cls, exc: RequestValidationError) -> "HTTPExceptionAdapter":
        return cls(status_code=422, reason=exc.errors(), headers=None, extra_params=dict())

    @classmethod
    def from_generic_http_exc(cls, exc: BaseGenericHTTPException) -> "HTTPExceptionAdapter":
        return cls(
            status_code=exc.status_code if exc.status_code is not None else 500,
            reason=exc.detail,
            headers=exc.headers,
            extra_params=exc.extra_params,
        )


class AbstractResponseSchema(GenericModel, Generic[T], ABC):
    """Abstract generic model for building response schema interfaces."""

    __inner_type__: ClassVar[Union[Type[Any], Tuple[Type[Any], ...]]]

    @classmethod
    @abstractmethod
    def from_api_route(
        cls: Type[TResponseSchema],
        content: T,
        path: str,
        status_code: int,
        response_model: Optional[Type[BaseModel]] = None,
        tags: Optional[List[str]] = None,
        summary: Optional[str] = None,
        description: Optional[str] = None,
        response_description: str = "Successful Response",
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
        response_class: Optional[Type[Response]] = None,
        **extra_params: Any,
    ) -> TResponseSchema:  # pragma: no cover
        """Builds an instance of response model from an API Route constructor.
        This method must be overridden by subclasses.

        Args:
            content (Any): The response content.
            path (str): Response path info.
            status_code (int): response status code.
            response_model (Optional[Type[BaseModel]], optional): The route response model. Defaults to None.
            tags (Optional[List[str]], optional): OpenAPI Tags configured in the API Route. Defaults to None.
            summary (Optional[str], optional): OpenAPI Summary. Defaults to None.
            description (Optional[str], optional): OpenAPI description. Defaults to None.
            response_description (str, optional): A string describing the response. Defaults to "Successful Response".
            deprecated (Optional[bool], optional): OpenAPI deprecation flag. Defaults to None.
            name (Optional[str], optional): Operation name. Defaults to None.
            methods (Optional[Union[Set[str], List[str]]], optional): supoported methods. Defaults to None.
            operation_id (Optional[str], optional): OpenAPI operation ID. Defaults to None.
            response_model_include (Optional[Union[SetIntStr, DictIntStrAny]], optional): `response_model` Included fields. Defaults to None.
            response_model_exclude (Optional[Union[SetIntStr, DictIntStrAny]], optional): `response_model` Excluded fields. Defaults to None.
            response_model_by_alias (bool, optional): Enable or disable field aliases in `response_model`. Defaults to True.
            response_model_exclude_unset (bool, optional): excludes unset values in `response_model`. Defaults to False.
            response_model_exclude_defaults (bool, optional): excludes default values in `response_model`. Defaults to False.
            response_model_exclude_none (bool, optional): excludes None values in `response_model`. Defaults to False.
            include_in_schema (bool, optional): wether or not include this operation in the OpenAPI Schema. Defaults to True.
            response_class (Optional[Type[Response]], optional): FastaAPI/Starlette Response Class. Defaults to None.

        Returns:
            TResponseSchema: A ResponseSchema instance
        """
        pass

    @classmethod
    @abstractmethod
    def from_exception(
        cls: Type[TResponseSchema],
        request: Request,
        reason: T,
        status_code: int,
        headers: Optional[dict] = None,
        **extra_params: Any,
    ) -> TResponseSchema:  # pragma: no cover
        """Builds a ResponseSchema instance from an exception.
        This method must be overridden by subclasses.

        Args:
            request (Request): A FastaAPI/Starlette Request.
            reason (str): The `Exception` description or response data.
            status_code (int): the response status code.
            headers (dict): the response_headers

        Returns:
            TResponseSchema: A ResponseSchema instance
        """
        pass

    @classmethod
    def from_exception_handler(
        cls: Type[TResponseSchema],
        request: Request,
        exception: Union[
            RequestValidationError, StarletteHTTPException, FastAPIHTTPException, BaseGenericHTTPException
        ],
    ) -> TResponseSchema:
        """Used in exception handlers to build a ResponseSchema instance.
        This method should not be overridden by subclasses.

        Args:
            request (Request): A FastaAPI/Starlette Request.
            exception (Union[RequestValidationError, StarletteHTTPException, FastAPIHTTPException, BaseGenericHTTPException]): The instantiated raised exception.

        Returns:
            TResponseSchema: A ResponseSchema instance
        """
        if isinstance(exception, BaseGenericHTTPException):
            adapted = HTTPExceptionAdapter.from_generic_http_exc(exception)
        elif isinstance(exception, FastAPIHTTPException):
            adapted = HTTPExceptionAdapter.from_fastapi_exc(exception)
        elif isinstance(exception, StarletteHTTPException):
            adapted = HTTPExceptionAdapter.from_starlette_exc(exception)
        else:
            adapted = HTTPExceptionAdapter.from_request_validation_err(exception)
        return cls.from_exception(
            request=request,
            reason=adapted.reason,
            status_code=adapted.status_code,
            headers=adapted.headers,
            **adapted.extra_params,
        )

    def __class_getitem__(
        cls: Type[TResponseSchema], params: Union[Type[Any], Tuple[Type[Any], ...]]
    ) -> Type[TResponseSchema]:
        cls.__inner_type__ = params
        return super().__class_getitem__(params)

    class Config:
        arbitrary_types_allowed = True


class ResponseWithMetadata(NamedTuple):
    """This Interface wraps the response content with the additional metadata

    Args:
        metadata (dict): A dictionary containing the metadata fields.
        response_content (Optional[Any]): The content of the response. Default to None.

    """

    metadata: dict
    response_content: Optional[Any] = None
