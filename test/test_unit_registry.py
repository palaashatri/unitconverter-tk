import pytest

from src.unit_registry import UnitRef, UNIT_REGISTRY, resolve_unit


def test_registry_resolves_common_aliases_without_case_sensitivity():
    assert resolve_unit("m") == UnitRef("length", "m", "Meters")
    assert resolve_unit("MILES") == UnitRef("length", "mi", "Miles")
    assert resolve_unit("square mm") == UnitRef("area", "sqmm", "Square millimeter")
    assert resolve_unit("cup").category == "volume"
    assert resolve_unit("MPG").code == "mpg_us"
    assert resolve_unit("imperial mpg").code == "mpg_imp"
    assert resolve_unit("KiB/s").code == "KiB/s"


def test_registry_reports_case_sensitive_bit_and_byte_symbol_as_ambiguous():
    with pytest.raises(ValueError, match="ambiguous"):
        resolve_unit("b")


def test_registry_contains_every_conversion_category():
    categories = {unit.category for units in UNIT_REGISTRY.values() for unit in units}
    assert categories == {
        "length", "area", "digital", "weight", "volume", "speed", "time",
        "pressure", "energy", "temperature", "angle", "data_rate",
        "fuel_economy",
    }


def test_registry_rejects_unknown_and_ambiguous_aliases(monkeypatch):
    with pytest.raises(ValueError, match="unknown unit"):
        resolve_unit("furlong")

    units = (
        UnitRef("length", "m", "Meters"),
        UnitRef("time", "min", "Minutes"),
    )
    monkeypatch.setitem(UNIT_REGISTRY, "shared", units)
    with pytest.raises(ValueError, match="ambiguous"):
        resolve_unit("shared")
