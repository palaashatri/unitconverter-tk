factors = {
    'pa': 1,
    'kpa': 1000,
    'bar': 100000,
    'psi': 6894.76,
    'atm': 101325,
    'torr': 133.322,
    'mmhg': 133.322
}

def convert(amt, frm, to):
    if frm != 'pa':
        amt = amt * factors[frm]
    return amt / factors[to]
