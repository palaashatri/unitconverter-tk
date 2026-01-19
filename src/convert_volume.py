factors = {
    'ml': 1,
    'l': 1000,
    'cup': 236.588,
    'pint': 473.176,
    'quart': 946.353,
    'gal': 3785.41,
    'floz': 29.5735,
    'm3': 1000000,
    'cm3': 1,
    'in3': 16.3871,
    'ft3': 28316.8
}

def convert(amt, frm, to):
    if frm != 'ml':
        amt = amt * factors[frm]
    return amt / factors[to]
