from .conversion_utils import convert_by_factors

factors = {
    "j": 1,
    "kj": 1000,
    "cal": 4.184,  # Thermochemical calorie.
    "kcal": 4184,
    "wh": 3600,
    "kwh": 3_600_000,
    "btu": 1055.05585262,  # International Table BTU.
    "ftlb": 1.3558179483314004,
    "ev": 1.602176634e-19,  # Exact SI value.
}

def convert(amt, frm, to):
    return convert_by_factors(amt, frm, to, factors)
