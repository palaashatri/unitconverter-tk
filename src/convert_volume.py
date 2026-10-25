from .conversion_utils import convert_by_factors

factors = {
    "ml": 1,
    "l": 1000,
    "cup": 236.5882365,
    "pint": 473.176473,
    "quart": 946.352946,
    "gal": 3785.411784,
    "floz": 29.5735295625,
    "tsp": 4.92892159375,
    "tbsp": 14.78676478125,
    "m3": 1_000_000,
    "cm3": 1,
    "in3": 16.387064,
    "ft3": 28_316.846592,
}

def convert(amt, frm, to):
    return convert_by_factors(amt, frm, to, factors)
