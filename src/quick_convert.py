"""Pure parser and dispatcher for type-to-convert expressions."""

from dataclasses import dataclass
import re

from . import (
    convert_angle,
    convert_area,
    convert_data_rate,
    convert_digital,
    convert_energy,
    convert_fuel_economy,
    convert_length,
    convert_pressure,
    convert_speed,
    convert_temp,
    convert_time,
    convert_volume,
    convert_weight,
)
from .conversion_utils import require_finite
from .unit_registry import UnitRef, resolve_unit


@dataclass(frozen=True)
class ParsedExpression:
    amount: float
    source: UnitRef
    target: UnitRef


@dataclass(frozen=True)
class ConversionResult:
    value: float
    source_label: str
    target_label: str


_NUMBER = r"[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?"
_EXPRESSION = re.compile(
    rf"^\s*({_NUMBER})\s+(.+?)\s+(?:to|in)\s+(.+?)\s*$",
    re.IGNORECASE,
)

_LINEAR_CONVERTERS = {
    "angle": convert_angle,
    "area": convert_area,
    "data_rate": convert_data_rate,
    "digital": convert_digital,
    "energy": convert_energy,
    "fuel_economy": convert_fuel_economy,
    "length": convert_length,
    "pressure": convert_pressure,
    "speed": convert_speed,
    "time": convert_time,
    "volume": convert_volume,
    "weight": convert_weight,
}


def parse_expression(text: str) -> ParsedExpression:
    match = _EXPRESSION.fullmatch(text if isinstance(text, str) else "")
    if match is None:
        raise ValueError("Use '<amount> <unit> to <unit>', for example '10 km in mi'.")

    amount = require_finite(float(match.group(1)))
    source = resolve_unit(match.group(2))
    target = resolve_unit(match.group(3))
    if source.category != target.category:
        raise ValueError(
            f"Both units must be from the same category; got {source.category} and {target.category}."
        )
    return ParsedExpression(amount, source, target)


def _convert_temperature(amount: float, source: str, target: str) -> float:
    if source == target:
        if source == "c":
            convert_temp.convert_celToKel(amount)
        elif source == "f":
            convert_temp.convert_fahToKel(amount)
        else:
            convert_temp.convert_kelToCel(amount)
        return amount

    conversions = {
        ("c", "f"): convert_temp.convert_celToFah,
        ("c", "k"): convert_temp.convert_celToKel,
        ("f", "c"): convert_temp.convert_fahToCel,
        ("f", "k"): convert_temp.convert_fahToKel,
        ("k", "c"): convert_temp.convert_kelToCel,
        ("k", "f"): convert_temp.convert_kelTofah,
    }
    try:
        converter = conversions[(source, target)]
    except KeyError as error:
        raise ValueError(f"unknown temperature unit: {error.args[0]}") from error
    return converter(amount)


def convert_expression(text: str) -> ConversionResult:
    parsed = parse_expression(text)
    if parsed.source.category == "temperature":
        value = _convert_temperature(
            parsed.amount, parsed.source.code, parsed.target.code
        )
    else:
        value = _LINEAR_CONVERTERS[parsed.source.category].convert(
            parsed.amount, parsed.source.code, parsed.target.code
        )
    return ConversionResult(
        require_finite(value),
        parsed.source.label,
        parsed.target.label,
    )
