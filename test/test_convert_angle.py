from itertools import product
import math

import pytest

from src import convert_angle


REFERENCE_RADIANS = {
    "rad": 1,
    "deg": math.pi / 180,
    "grad": math.pi / 200,
    "turn": 2 * math.pi,
    "arcmin": math.pi / 10800,
    "arcsec": math.pi / 648000,
}


@pytest.mark.parametrize("unit,expected", REFERENCE_RADIANS.items())
def test_each_angle_unit_matches_radians(unit, expected):
    assert convert_angle.convert(1, unit, "rad") == pytest.approx(expected)


def test_all_angle_unit_pairs_round_trip():
    for source, target in product(REFERENCE_RADIANS, repeat=2):
        result = convert_angle.convert(17.25, source, target)
        assert convert_angle.convert(result, target, source) == pytest.approx(17.25)


def test_large_finite_identity_conversion_does_not_overflow():
    assert convert_angle.convert(1e308, "turn", "turn") == 1e308


def test_unrepresentable_angle_conversion_raises_value_error():
    with pytest.raises(ValueError, match="conversion result"):
        convert_angle.convert(1e308, "turn", "rad")


@pytest.mark.parametrize("source,target", [("unknown", "rad"), ("rad", "unknown")])
def test_angle_converter_rejects_unknown_units(source, target):
    with pytest.raises(ValueError, match="unit"):
        convert_angle.convert(1, source, target)
