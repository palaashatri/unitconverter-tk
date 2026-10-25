from .conversion_utils import convert_by_factors

factors = {
    "sqm": 1,
    "sqkm": 1_000_000,
    "sqr": 1011.7141056,
    "sqcm": 0.0001,
    "sqf": 0.09290304,
    "sqin": 0.00064516,
    "sqmile": 2_589_988.110336,
    "sqmm": 0.000001,
    "mm": 0.000001,  # Deprecated alias for the unambiguous square-mm code.
    "sqrod": 25.29285264,
    "sqyard": 0.83612736,
    "sqtownship": 93_239_571.972096,
    "sqacre": 4046.8564224,
    "sqare": 100,
    "sqbarn": 1e-28,
    "sqhectare": 10_000,
    "sqhomestead": 647_497.027584,
}

def convert(amt, frm, to):
    return convert_by_factors(amt, frm, to, factors)
