from .conversion_utils import convert_by_factors

factors = {
    "kg": 1000,
    "hg": 100,
    "dag": 10,
    "g": 1,
    "dg": 0.1,
    "deg": 0.1,  # Deprecated alias for the SI decigram symbol.
    "cg": 0.01,
    "mg": 0.001,
}


def convert(amt, frm, to):
    return convert_by_factors(amt, frm, to, factors)
