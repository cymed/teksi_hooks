import pytest

from teksi_hooks.exceptions import TeksiHookError
from teksi_hooks.ili_definitions import Standardoid


def test_standardoid_accepts_valid_value() -> None:
    oid = Standardoid("ch000000geping01")

    assert str(oid) == "ch000000geping01"
    assert oid.value == "ch000000geping01"


@pytest.mark.parametrize(
    "value",
    [
        "",
        "too_short",
        "ch000000geping001",  # too long
        "ch000000-geping1",   # dash
        "ch000000gäping01",    # non-ASCII
    ],
)
def test_standardoid_rejects_invalid_value(
    value: str,
) -> None:
    with pytest.raises(TeksiHookError):
        Standardoid(value)