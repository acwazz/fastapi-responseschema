import pytest
from fastapi_responseschema import exceptions as exc


class TestBaseGenericHTTPException:
    def test_initialize(self):
        inst = exc.BaseGenericHTTPException(detail="hello", headers={"Test": True}, extra=True)
        assert isinstance(inst, exc.BaseGenericHTTPException)  # Sanity check here
        assert inst.extra_params.get("extra") 
        assert inst.headers.get("Test")
        assert inst.detail ==  "hello"
    
    def test_wrong_subsclassing(self):
        with pytest.raises(AttributeError):
            class Exc(exc.BaseGenericHTTPException):
                pass


def test_generic_http_ecxeption_initialize():
    inst = exc.GenericHTTPException(status_code=501)
    assert inst.status_code == 501


@pytest.mark.parametrize("status_code,exc_class", [
    (400, exc.BadRequest),
    (401, exc.Unauthorized),
    (403, exc.Forbidden),
    (404, exc.NotFound),
    (405, exc.MethodNotAllowed),
    (409, exc.Conflict),
    (410, exc.Gone),
    (422, exc.UnprocessableEntity),
    (500, exc.InternalServerError)
])
def test_web_exceptions_status_codes(status_code, exc_class):
    e = exc_class()
    assert e.status_code == status_code