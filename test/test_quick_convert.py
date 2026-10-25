import math

import pytest

from src.quick_convert import convert_expression, parse_expression


@pytest.mark.parametrize(
    "expression,expected,source_label,target_label",
    [
        ("10 km in mi", 10_000 / 1609.344, "Kilometers", "Miles"),
        ("72 F to C", (72 - 32) * 5 / 9, "Fahrenheit", "Celsius"),
        ("1 mpg to km/L", 100 / (100 * 3.785411784 / 1.609344), "U.S. mpg", "km/L"),
        ("1 turn in deg", 360, "Turns", "Degrees"),
    ],
)
def test_quick_conversion_examples(expression, expected, source_label, target_label):
    result = convert_expression(expression)
    assert result.value == pytest.approx(expected)
    assert result.source_label == source_label
    assert result.target_label == target_label


def test_parser_resolves_case_insensitive_aliases_to_unit_refs():
    parsed = parse_expression("2.5 MILES TO feet")
    assert parsed.amount == 2.5
    assert parsed.source.category == "length"
    assert parsed.source.code == "mi"
    assert parsed.target.code == "ft"


@pytest.mark.parametrize(
    "expression", ["", "10 km", "abc km to mi", "10 km from mi", "10e999 km to mi"]
)
def test_parser_rejects_malformed_or_non_finite_expressions(expression):
    with pytest.raises(ValueError):
        parse_expression(expression)


@pytest.mark.parametrize(
    "expression", ["10 furlong to mi", "10 m to min", "10 sqmm to mm"]
)
def test_parser_rejects_unknown_or_cross_category_units(expression):
    with pytest.raises(ValueError, match="unit|category"):
        parse_expression(expression)


def test_quick_conversion_rejects_below_absolute_zero():
    with pytest.raises(ValueError, match="absolute zero"):
        convert_expression("-1 K to C")


def test_quick_conversion_rejects_non_finite_result():
    with pytest.raises(ValueError, match="positive finite"):
        convert_expression("0 mpg to km/L")
