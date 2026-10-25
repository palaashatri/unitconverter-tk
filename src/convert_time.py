from .conversion_utils import convert_by_factors

factors = {
    "sec": 1,
    "min": 60,
    "hr": 3600,
    "day": 86400,
    "week": 604800,
    "month": 2_629_746,  # One twelfth of the average Gregorian year.
    "year": 31_556_952,  # Average Gregorian year (365.2425 days).
    "ms": 0.001,
    "us": 0.000001,
}

def convert(amt, frm, to):
    return convert_by_factors(amt, frm, to, factors)
