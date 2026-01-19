factors = {
    'sec': 1,
    'min': 60,
    'hr': 3600,
    'day': 86400,
    'week': 604800,
    'month': 2628000,
    'year': 31536000,
    'ms': 0.001,
    'us': 0.000001
}

def convert(amt, frm, to):
    if frm != 'sec':
        amt = amt * factors[frm]
    return amt / factors[to]
