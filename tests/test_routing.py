from fastapi_responseschema.routing import respond
from fastapi_responseschema.interfaces import ResponseWithMetadata


def test_respond_returns_meta():
    out = respond({"a": 1}, first=1, second=2)
    assert isinstance(out, ResponseWithMetadata)
    assert out.response_content.get("a") == 1
    assert out.metadata.get("first") == 1
    assert out.metadata.get("second") == 2
