"""Shared validation for pure unit conversion functions."""

import math


def require_finite(amt: float) -> float:
    """Return a finite amount or raise ``ValueError``."""
    try:
        amount = float(amt)
    except (TypeError, ValueError) as error:
        raise ValueError("amount must be a finite number") from error
    if not math.isfinite(amount):
        raise ValueError("amount must be a finite number")
    return amount
