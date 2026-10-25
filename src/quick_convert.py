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
_AMOUNT_AND_UNITS = re.compile(rf"^\s*({_NUMBER})\s+(.+?)\s*$")
_UNIT_SEPARATOR = re.compile(r"(?=(\s+(?:to|in)\s+))", re.IGNORECASE)

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
    match = _AMOUNT_AND_UNITS.fullmatch(text if isinstance(text, str) else "")
    if match is None:
        raise ValueError("Use '<amount> <unit> to <unit>', for example '10 km in mi'.")

    amount = require_finite(float(match.group(1)))
    units = match.group(2)
    candidates = []
    category_errors = []
    unit_errors = []
    for separator in _UNIT_SEPARATOR.finditer(units):
        separator_start, separator_end = separator.span(1)
        source_text = units[:separator_start].strip()
        target_text = units[separator_end:].strip()
        if not source_text or not target_text:
            continue

        source = target = None
        errors = []
        for resolver, alias, target_side in (
            (resolve_unit, source_text, False),
            (resolve_unit, target_text, True),
        ):
            try:
                resolved = resolver(alias)
            except ValueError as error:
                errors.append(error)
                if target_side:
                    target = None
                else:
                    source = None
            else:
                if target_side:
                    target = resolved
                else:
                    source = resolved

        if errors:
            unit_errors.append((int(source is not None) + int(target is not None), errors[0]))
            continue
        if source.category != target.category:
            category_errors.append(
                ValueError(
                    "Both units must be from the same category; "
                    f"got {source.category} and {target.category}."
                )
            )
            continue
        candidates.append((source, target))

    if len(candidates) == 1:
        source, target = candidates[0]
        return ParsedExpression(amount, source, target)
    if len(candidates) > 1:
        raise ValueError("Ambiguous unit separator; use a clearer expression.")
    if category_errors:
        raise category_errors[0]
    if unit_errors:
        raise max(unit_errors, key=lambda item: item[0])[1]
    raise ValueError("Use '<amount> <unit> to <unit>', for example '10 km in mi'.")


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
