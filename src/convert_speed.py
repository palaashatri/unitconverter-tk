from .conversion_utils import convert_by_factors

factors = {
    "mps": 1,
    "kph": 1 / 3.6,
    "mph": 1609.344 / 3600,
    "fps": 0.3048,
    "knot": 1852 / 3600,
    "mach": 343.2,  # Dry air at 20 °C.
}

def convert(amt, frm, to):
    return convert_by_factors(amt, frm, to, factors)
