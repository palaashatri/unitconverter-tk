factors = {
    'mps': 1,
    'kph': 0.277778,
    'mph': 0.44704,
    'fps': 0.3048,
    'knot': 0.514444,
    'mach': 343
}

def convert(amt, frm, to):
    if frm != 'mps':
        amt = amt * factors[frm]
    return amt / factors[to]
