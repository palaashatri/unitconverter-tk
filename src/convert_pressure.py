from .conversion_utils import convert_by_factors

factors = {
    "pa": 1,
    "kpa": 1000,
    "bar": 100_000,
    "psi": 6894.757293168,
    "atm": 101_325,
    "torr": 101_325 / 760,
    "mmhg": 133.322387415,
}

def convert(amt, frm, to):
    return convert_by_factors(amt, frm, to, factors)
