from math import ceil
from typing import Generic, TypeVar, Type, Any, Optional, ClassVar, Protocol
from fastapi import Query
from fastapi_pagination.bases import AbstractPage, AbstractParams, RawParams
from fastapi_pagination.links.bases import Links, create_links
from pydantic import BaseModel
from pydantic.types import conint
from fastapi_responseschema.routing import SchemaAPIRoute
from fastapi_responseschema.interfaces import AbstractResponseSchema


T = TypeVar("T")
TPagedResponseSchema = TypeVar("TPagedResponseSchema", bound="AbstractPagedResponseSchema")


class SupportedParams(Protocol):  # pragma: no cover
    page: int
    page_size: int

    def to_raw_params(self) -> RawParams:
        pass


class PaginationMetadata(BaseModel):
    """Pagination metadata model for pagination info.

    Args:
        total (int): Total number of items.
        page_size (int): Number of items per page.
        page (int): Page number.
        links (dict): Object containing pagination links.
    """

    total: conint(ge=0)  # type: ignore
    page_size: conint(ge=0)  # type: ignore
    page: conint(ge=1)  # type: ignore
    links: Links

    @classmethod
    def from_abstract_page_create(cls, total: int, params: SupportedParams) -> "PaginationMetadata":
        """Create pagination metadata from an abstract page.

        Args:
            total (int): Total number of items.
            params (SupportedParams): A FastaAPI Pagination Params instance.

        Returns:
            PaginationMetadata: PaginationMetadata instance
        """
        return cls(
            total=total,
            page_size=params.page_size,
            page=params.page,
            links=create_links(
                first={"page": 1},
                last={"page": ceil(total / params.page_size) if total > 0 else 1},
                next={"page": params.page + 1} if params.page * params.page_size < total else None,
                prev={"page": params.page - 1} if 1 <= params.page - 1 else None,
            ),
        )


class PaginationParams(BaseModel, AbstractParams):  # pragma: no cover
    """Pagination Querystring parameters

    Args:
        page (int): The page number.
        page_size (int): Number of items per page.
    """

    page: int = Query(1, ge=1, description="Page number")
    page_size: int = Query(50, ge=1, le=100, description="Page size")

    def to_raw_params(self) -> RawParams:
        return RawParams(
            limit=self.page_size,
            offset=self.page_size * (self.page - 1),
        )


class AbstractPagedResponseSchema(AbstractPage[T], AbstractResponseSchema[T], Generic[T]):
    """Abstract generic model for building response schema interfaces with pagination logic."""

    __params_type__: ClassVar[Type[AbstractParams]] = PaginationParams

    class Config:
        arbitrary_types_allowed = True


class PagedSchemaAPIRoute(SchemaAPIRoute):
    """A SchemaAPIRoute class with pagination support.
    Must be subclassed setting at least SchemaAPIRoute.response_model.

    Usage:

        from typing import Generic, TypeVar
        from fastapi_responseschema.integrations.pagination import AbstractPagedResponseSchema

        T = TypeVar("T")
        class MyResponseSchema(AbstractPagedResponseSchema[T], Generic[T]):
            ...

        class MyAPIRoute(SchemaPagedAPIRoute):
            response_schema = MyResponseSchema
            paged_response_schema = MyResponseSchema

        from fastapi import APIRouter

        router = APIRouter(route_class=MyAPIRoute)
    """

    paged_response_schema: Type[AbstractPagedResponseSchema[Any]]
    response_schema: Optional[Type[AbstractResponseSchema[Any]]] = None  # type: ignore
    error_response_schema: Optional[Type[AbstractResponseSchema[Any]]] = None

    def __init_subclass__(cls) -> None:
        if not hasattr(cls, "paged_response_schema") or getattr(cls, "paged_response_schema") is None:
            raise AttributeError("`paged_response_schema` must be defined in subclass.")
        if not hasattr(cls, "response_schema") or getattr(cls, "response_schema") is None:
            raise AttributeError("`response_schema` must be defined in subclass.")
        return super().__init_subclass__()

    def get_wrapper_model(self, is_error: bool, response_model: Type[Any]) -> Type[AbstractResponseSchema[Any]]:
        if issubclass(response_model, AbstractPagedResponseSchema):
            if not self.error_response_schema:
                return self.paged_response_schema
            return self.error_response_schema if is_error else self.paged_response_schema
        return super().get_wrapper_model(is_error, response_model)
