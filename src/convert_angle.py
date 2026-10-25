"""Angle conversion factors relative to the radian."""

import math

from .conversion_utils import convert_by_factors


factors = {
    "rad": 1,
    "deg": math.pi / 180,
    "grad": math.pi / 200,
    "turn": 2 * math.pi,
    "arcmin": math.pi / 10_800,
    "arcsec": math.pi / 648_000,
}


def convert(amt, frm, to):
    return convert_by_factors(amt, frm, to, factors)
