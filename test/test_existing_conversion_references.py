from itertools import product

import pytest

from src import (
    area,
    convert_area,
    convert_digital,
    convert_energy,
    convert_length,
    convert_pressure,
    convert_speed,
    convert_time,
    convert_volume,
    convert_weight,
    convert_temp,
    energy,
    speed,
    time_converter,
    volume,
    weight,
)


LINEAR_CONVERTERS = [
    (convert_area, "sqm", {
        "sqm": 1, "sqkm": 1_000_000, "sqr": 1011.7141056,
        "sqcm": 0.0001, "sqf": 0.09290304, "sqin": 0.00064516,
        "sqmile": 2_589_988.110336, "sqmm": 0.000001, "mm": 0.000001,
        "sqrod": 25.29285264, "sqyard": 0.83612736,
        "sqtownship": 93_239_571.972096, "sqacre": 4046.8564224,
        "sqare": 100, "sqbarn": 1e-28, "sqhectare": 10_000,
        "sqhomestead": 647_497.027584,
    }),
    (convert_digital, "byte", {
        "PB": 1e15, "TB": 1e12, "GB": 1e9, "MB": 1e6,
        "kB": 1e3, "bit": 1 / 8, "byte": 1,
    }),
    (convert_energy, "j", {
        "j": 1, "kj": 1e3, "cal": 4.184, "kcal": 4184,
        "wh": 3600, "kwh": 3.6e6, "btu": 1055.05585262,
        "ftlb": 1.3558179483314004, "ev": 1.602176634e-19,
    }),
    (convert_length, "m", {
        "nmi": 1852, "mi": 1609.344, "yd": 0.9144, "ft": 0.3048,
        "inch": 0.0254, "km": 1000, "m": 1, "cm": 0.01,
        "mm": 0.001,
    }),
    (convert_pressure, "pa", {
        "pa": 1, "kpa": 1000, "bar": 100000,
        "psi": 6894.757293168, "atm": 101325,
        "torr": 101325 / 760, "mmhg": 133.322387415,
    }),
    (convert_speed, "mps", {
        "mps": 1, "kph": 1 / 3.6, "mph": 1609.344 / 3600,
        "fps": 0.3048, "knot": 1852 / 3600, "mach": 343.2,
    }),
    (convert_time, "sec", {
        "sec": 1, "min": 60, "hr": 3600, "day": 86400,
        "week": 604800, "month": 2_629_746, "year": 31_556_952,
        "ms": 0.001, "us": 0.000001,
    }),
    (convert_volume, "ml", {
        "ml": 1, "l": 1000, "cup": 236.5882365,
        "pint": 473.176473, "quart": 946.352946,
        "gal": 3785.411784, "floz": 29.5735295625,
        "tsp": 4.92892159375, "tbsp": 14.78676478125,
        "m3": 1_000_000, "cm3": 1, "in3": 16.387064,
        "ft3": 28_316.846592,
    }),
    (convert_weight, "g", {
        "kg": 1000, "hg": 100, "dag": 10, "g": 1,
        "dg": 0.1, "deg": 0.1, "cg": 0.01, "mg": 0.001,
    }),
]


@pytest.mark.parametrize(
    "converter,base,expected",
    LINEAR_CONVERTERS,
    ids=["area", "digital", "energy", "length", "pressure", "speed", "time", "volume", "weight"],
)
def test_every_linear_unit_matches_its_reference(converter, base, expected):
    assert set(converter.factors) == set(expected)
    for unit, factor in expected.items():
        assert converter.convert(1, unit, base) == pytest.approx(
            factor, rel=1e-12, abs=0
        )


@pytest.mark.parametrize(
    "converter,base,expected",
    LINEAR_CONVERTERS,
    ids=["area", "digital", "energy", "length", "pressure", "speed", "time", "volume", "weight"],
)
def test_every_ordered_linear_unit_pair_round_trips(converter, base, expected):
    del base
    for source, target in product(expected, repeat=2):
        converted = converter.convert(3.125, source, target)
        assert converter.convert(converted, target, source) == pytest.approx(3.125, rel=1e-9)


@pytest.mark.parametrize(
    "converter,base,_expected",
    LINEAR_CONVERTERS,
    ids=["area", "digital", "energy", "length", "pressure", "speed", "time", "volume", "weight"],
)
def test_linear_converters_reject_unknown_unit(converter, base, _expected):
    with pytest.raises(ValueError, match="unit"):
        converter.convert(1, "unknown", base)


@pytest.mark.parametrize(
    "source,target,function,expected",
    [
        ("C", "F", convert_temp.convert_celToFah, 100.4),
        ("C", "K", convert_temp.convert_celToKel, 311.15),
        ("F", "C", convert_temp.convert_fahToCel, 38),
        ("F", "K", convert_temp.convert_fahToKel, 273.15),
        ("K", "C", convert_temp.convert_kelToCel, -273.15),
        ("K", "F", convert_temp.convert_kelTofah, 32),
    ],
)
def test_temperature_reference_values(source, target, function, expected):
    value = {"C": 38, "F": 100.4, "K": 273.15}[source]
    if source == "F" and target == "K":
        value = 32
    if source == "K" and target == "C":
        value = 0
    assert function(value) == pytest.approx(expected)


@pytest.mark.parametrize(
    "source,target,function",
    [
        ("C", "F", convert_temp.convert_celToFah),
        ("C", "K", convert_temp.convert_celToKel),
        ("F", "C", convert_temp.convert_fahToCel),
        ("F", "K", convert_temp.convert_fahToKel),
        ("K", "C", convert_temp.convert_kelToCel),
        ("K", "F", convert_temp.convert_kelTofah),
    ],
)
def test_every_ordered_temperature_pair_round_trips(source, target, function):
    inverse = {
        ("C", "F"): convert_temp.convert_fahToCel,
        ("C", "K"): convert_temp.convert_kelToCel,
        ("F", "C"): convert_temp.convert_celToFah,
        ("F", "K"): convert_temp.convert_kelTofah,
        ("K", "C"): convert_temp.convert_celToKel,
        ("K", "F"): convert_temp.convert_fahToKel,
    }[(source, target)]
    sample = 38 if source == "C" else (100 if source == "F" else 311.15)
    assert inverse(function(sample)) == pytest.approx(sample, rel=1e-12)


def test_temperature_rejects_values_below_absolute_zero():
    with pytest.raises(ValueError, match="absolute zero"):
        convert_temp.convert_celToKel(-273.16)
    with pytest.raises(ValueError, match="absolute zero"):
        convert_temp.convert_fahToKel(-459.68)
    with pytest.raises(ValueError, match="absolute zero"):
        convert_temp.convert_kelToCel(-0.01)


def test_fahrenheit_absolute_zero_round_trips_to_zero_kelvin():
    kelvin = convert_temp.convert_fahToKel(-459.67)

    assert kelvin == 0
    assert convert_temp.convert_kelTofah(kelvin) == pytest.approx(-459.67)
    with pytest.raises(ValueError, match="absolute zero"):
        convert_temp.convert_kelTofah(-1e-15)


def test_correct_temperature_name_keeps_legacy_alias():
    assert convert_temp.covert_celToKel(38) == pytest.approx(
        convert_temp.convert_celToKel(38)
    )


def test_existing_ui_labels_disclose_unit_conventions():
    assert area.UNIT_LABELS["Square millimeter"] == "sqmm"
    assert weight.UNIT_LABELS["Decagram"] == "dag"
    assert weight.UNIT_LABELS["Decigram"] == "dg"
    assert volume.UNIT_LABELS["US cup"] == "cup"
    assert energy.UNIT_LABELS["Calorie (thermochemical)"] == "cal"
    assert energy.UNIT_LABELS["BTU (IT)"] == "btu"
    assert energy.UNIT_LABELS["Foot-pound force"] == "ftlb"
    assert speed.UNIT_LABELS["Mach (dry air at 20 °C)"] == "mach"
    assert time_converter.UNIT_LABELS["Average Gregorian month"] == "month"
    assert time_converter.UNIT_LABELS["Average Gregorian year"] == "year"
