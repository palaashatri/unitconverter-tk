"""Fuel-economy conversions for explicitly named regional units."""

from .conversion_utils import require_finite


factors = {
    "l_per_100km": 1,
    "km_per_l": 100,
    "mpg_us": 100 * 3.785411784 / 1.609344,
    "mpg_imp": 100 * 4.54609 / 1.609344,
}


def convert(amt, frm, to):
    try:
        amount = require_finite(amt)
    except ValueError as error:
        raise ValueError("fuel economy must be a positive finite number") from error
    if amount <= 0:
        raise ValueError("fuel economy must be a positive finite number")
    try:
        source_factor = factors[frm]
        target_factor = factors[to]
    except KeyError as error:
        raise ValueError(f"unknown unit: {error.args[0]}") from error

    try:
        liters_per_100km = (
            amount if frm == "l_per_100km" else source_factor / amount
        )
        result = (
            liters_per_100km
            if to == "l_per_100km"
            else target_factor / liters_per_100km
        )
        result = require_finite(result)
    except (OverflowError, ZeroDivisionError) as error:
        raise ValueError("fuel economy result is outside the finite range") from error
    if result <= 0:
        raise ValueError("fuel economy result must be positive and finite")
    return result
