from .conversion_utils import convert_by_factors

factors = {
    "PB": 1_000_000_000_000_000,
    "TB": 1_000_000_000_000,
    "GB": 1_000_000_000,
    "MB": 1_000_000,
    "kB": 1000,
    "bit": 1 / 8,
    "byte": 1,
}


def convert(amt, frm, to):
    return convert_by_factors(amt, frm, to, factors)
