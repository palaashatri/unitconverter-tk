"""Shared validation for pure unit conversion functions."""

import math
from collections.abc import Mapping


def require_finite(amt: float) -> float:
    """Return a finite amount or raise ``ValueError``."""
    try:
        amount = float(amt)
    except (TypeError, ValueError) as error:
        raise ValueError("amount must be a finite number") from error
    if not math.isfinite(amount):
        raise ValueError("amount must be a finite number")
    return amount


def convert_by_factors(
    amt: float, frm: str, to: str, factors: Mapping[str, float]
) -> float:
    """Convert through a shared base unit using a category's factors."""
    amount = require_finite(amt)
    try:
        factor = factors[frm] / factors[to]
    except KeyError as error:
        raise ValueError(f"unknown unit: {error.args[0]}") from error
    result = amount * factor
    if not math.isfinite(result):
        raise ValueError("conversion result is outside the finite number range")
    return result
