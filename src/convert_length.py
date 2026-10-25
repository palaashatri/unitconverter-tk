from .conversion_utils import convert_by_factors

factors = {
    "nmi": 1852,
    "mi": 1609.344,
    "yd": 0.9144,
    "ft": 0.3048,
    "inch": 0.0254,
    "km": 1000,
    "m": 1,
    "cm": 0.01,
    "mm": 0.001,
}


def convert(amt, frm, to):
    return convert_by_factors(amt, frm, to, factors)
