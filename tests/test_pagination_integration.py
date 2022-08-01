from fastapi_responseschema.integrations.pagination import AbstractPagedResponseSchema, PagedSchemaAPIRoute


def test_paged_response_schema_inner_types():
    V = AbstractPagedResponseSchema[int]
    assert V.__inner_types__ == int