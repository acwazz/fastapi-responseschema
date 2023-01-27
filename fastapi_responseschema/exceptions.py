from __future__ import annotations
from typing import Optional, Dict, Any
from starlette import status
from fastapi.exceptions import HTTPException as FastAPIHTTPException


class BaseGenericHTTPException(FastAPIHTTPException):
    """BaseClass for HTTPExceptions with additional data"""

    status_code: Optional[int] = None  # type: ignore

    def __init__(self, detail: Any = None, headers: Optional[Dict[str, Any]] = None, **extra_params: Any) -> None:
        """Instances can be initialized with a set of extra params.

        Args:
            detail (Any, optional): The error response content. Defaults to None.
            headers (Optional[Dict[str, Any]], optional): A set of headers to be returned in the response. Defaults to None.
        """
        self.extra_params = extra_params
        super().__init__(status_code=self.status_code, detail=detail, headers=headers)  # type: ignore

    def __init_subclass__(cls) -> None:
        if not hasattr(cls, "status_code") or cls.status_code is None:
            raise AttributeError("`status_code` must be defined in subclass.")
        return super().__init_subclass__()


class GenericHTTPException(BaseGenericHTTPException):
    """HTTP exception with extra data"""

    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR

    def __init__(
        self, status_code: int, detail: Any = None, headers: Optional[Dict[str, Any]] = None, **extra_params: Any
    ) -> None:
        """Used to raise custom exceptions with extra params.

        Args:
            status_code (int): Exception status code.
            detail (Any, optional): Error response content. Defaults to None.
            headers (Optional[Dict[str, Any]], optional): Error response data. Defaults to None.
        """
        self.status_code = status_code
        super().__init__(detail=detail, headers=headers, extra_params=extra_params)


class InternalServerError(BaseGenericHTTPException):
    """Raises with HTTP status 500

    Args:
        detail (Any, optional): The error response content. Defaults to None.
        headers (Optional[Dict[str, Any]], optional): A set of headers to be returned in the response. Defaults to None.
    """

    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR


class BadRequest(BaseGenericHTTPException):
    """Raises with HTTP status 400

    Args:
        detail (Any, optional): The error response content. Defaults to None.
        headers (Optional[Dict[str, Any]], optional): A set of headers to be returned in the response. Defaults to None.
    """

    status_code = status.HTTP_400_BAD_REQUEST


class Unauthorized(BaseGenericHTTPException):
    """Raises with HTTP status 401

    Args:
        detail (Any, optional): The error response content. Defaults to None.
        headers (Optional[Dict[str, Any]], optional): A set of headers to be returned in the response. Defaults to None.
    """

    status_code = status.HTTP_401_UNAUTHORIZED


class Forbidden(BaseGenericHTTPException):
    """Raises with HTTP status 403

    Args:
        detail (Any, optional): The error response content. Defaults to None.
        headers (Optional[Dict[str, Any]], optional): A set of headers to be returned in the response. Defaults to None.
    """

    status_code = status.HTTP_403_FORBIDDEN


class NotFound(BaseGenericHTTPException):
    """Raises with HTTP status 404

    Args:
        detail (Any, optional): The error response content. Defaults to None.
        headers (Optional[Dict[str, Any]], optional): A set of headers to be returned in the response. Defaults to None.
    """

    status_code = status.HTTP_404_NOT_FOUND


class MethodNotAllowed(BaseGenericHTTPException):
    """Raises with HTTP status 405

    Args:
        detail (Any, optional): The error response content. Defaults to None.
        headers (Optional[Dict[str, Any]], optional): A set of headers to be returned in the response. Defaults to None.
    """

    status_code = status.HTTP_405_METHOD_NOT_ALLOWED


class Conflict(BaseGenericHTTPException):
    """Raises with HTTP status 409

    Args:
        detail (Any, optional): The error response content. Defaults to None.
        headers (Optional[Dict[str, Any]], optional): A set of headers to be returned in the response. Defaults to None.
    """

    status_code = status.HTTP_409_CONFLICT


class Gone(BaseGenericHTTPException):
    """Raises with HTTP status 410

    Args:
        detail (Any, optional): The error response content. Defaults to None.
        headers (Optional[Dict[str, Any]], optional): A set of headers to be returned in the response. Defaults to None.
    """

    status_code = status.HTTP_410_GONE


class UnprocessableEntity(BaseGenericHTTPException):
    """Raises with HTTP status 422

    Args:
        detail (Any, optional): The error response content. Defaults to None.
        headers (Optional[Dict[str, Any]], optional): A set of headers to be returned in the response. Defaults to None.
    """

    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
