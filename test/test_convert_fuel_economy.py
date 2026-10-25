from itertools import product
import math

import pytest

from src import convert_fuel_economy


REFERENCE_L_PER_100KM = {
    "l_per_100km": 1,
    "km_per_l": 100,
    "mpg_us": 100 * 3.785411784 / 1.609344,
    "mpg_imp": 100 * 4.54609 / 1.609344,
}


@pytest.mark.parametrize("unit,expected", REFERENCE_L_PER_100KM.items())
def test_each_fuel_economy_unit_matches_liters_per_100km(unit, expected):
    assert convert_fuel_economy.convert(1, unit, "l_per_100km") == pytest.approx(expected)


def test_all_fuel_economy_unit_pairs_round_trip():
    for source, target in product(REFERENCE_L_PER_100KM, repeat=2):
        converted = convert_fuel_economy.convert(8.5, source, target)
        assert convert_fuel_economy.convert(converted, target, source) == pytest.approx(8.5)


@pytest.mark.parametrize("value", [0, -1, math.nan, math.inf, -math.inf])
def test_fuel_economy_rejects_non_positive_or_non_finite_values(value):
    with pytest.raises(ValueError, match="positive finite"):
        convert_fuel_economy.convert(value, "mpg_us", "km_per_l")


@pytest.mark.parametrize(
    "source,target", [("unknown", "l_per_100km"), ("l_per_100km", "unknown")]
)
def test_fuel_economy_rejects_unknown_units(source, target):
    with pytest.raises(ValueError, match="unit"):
        convert_fuel_economy.convert(1, source, target)
