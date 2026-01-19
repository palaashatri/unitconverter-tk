factors = {
    'j': 1,
    'kj': 1000,
    'cal': 4.184,
    'kcal': 4184,
    'wh': 3600,
    'kwh': 3600000,
    'btu': 1055.06,
    'ftlb': 1.35582,
    'ev': 1.60218e-19
}

def convert(amt, frm, to):
    if frm != 'j':
        amt = amt * factors[frm]
    return amt / factors[to]
