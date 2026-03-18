import pytest

from OpenHosta.guarded.primitives import GuardedPrimitive, ProxyWrapper


def test_guardedprimitive_must_be_first_base_in_multiple_inheritance():
    with pytest.raises(TypeError, match="must declare GuardedPrimitive as first base"):
        class BadGuardedOrder(ProxyWrapper, GuardedPrimitive):
            _type_en = "bad order"
            _type_py = str
            _type_json = {"type": "string"}


def test_guardedprimitive_first_base_is_allowed():
    class GoodGuardedOrder(GuardedPrimitive, ProxyWrapper):
        _type_en = "good order"
        _type_py = str
        _type_json = {"type": "string"}

    assert GoodGuardedOrder.__bases__[0] is GuardedPrimitive