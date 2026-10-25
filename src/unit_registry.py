"""Canonical unit names and aliases used by quick conversion input."""

from dataclasses import dataclass
import re


@dataclass(frozen=True)
class UnitRef:
    category: str
    code: str
    label: str


def _normalize(alias: str) -> str:
    return re.sub(r"\s+", " ", alias.strip().casefold())


_definitions = [
    # category, code, display label, aliases
    ("length", "nmi", "Nautical miles", ("nmi", "nautical mile", "nautical miles")),
    ("length", "mi", "Miles", ("mi", "mile", "miles")),
    ("length", "yd", "Yards", ("yd", "yard", "yards")),
    ("length", "ft", "Feet", ("ft", "foot", "feet")),
    ("length", "inch", "Inches", ("inch", "inches", "in")),
    ("length", "km", "Kilometers", ("km", "kilometer", "kilometers", "kilometre", "kilometres")),
    ("length", "m", "Meters", ("m", "meter", "meters", "metre", "metres")),
    ("length", "cm", "Centimeters", ("cm", "centimeter", "centimeters", "centimetre", "centimetres")),
    ("length", "mm", "Millimeters", ("mm", "millimeter", "millimeters", "millimetre", "millimetres")),
    ("area", "sqm", "Square meters", ("sqm", "square meter", "square meters", "square metre", "square metres")),
    ("area", "sqkm", "Square kilometers", ("sqkm", "square km", "square kilometer", "square kilometers")),
    ("area", "sqr", "Square rood", ("sqr", "square rood", "square roods")),
    ("area", "sqcm", "Square centimeters", ("sqcm", "square cm", "square centimeter", "square centimeters")),
    ("area", "sqf", "Square feet", ("sqf", "square foot", "square feet", "sq ft")),
    ("area", "sqin", "Square inches", ("sqin", "square inch", "square inches", "sq in")),
    ("area", "sqmile", "Square miles", ("sqmile", "square mile", "square miles", "sq mi")),
    ("area", "sqmm", "Square millimeter", ("sqmm", "square mm", "square millimeter", "square millimeters")),
    ("area", "sqrod", "Square rods", ("sqrod", "square rod", "square rods")),
    ("area", "sqyard", "Square yards", ("sqyard", "square yard", "square yards", "sq yd")),
    ("area", "sqtownship", "Square townships", ("sqtownship", "square township", "square townships")),
    ("area", "sqacre", "Acres", ("sqacre", "acre", "acres", "square acre", "square acres")),
    ("area", "sqare", "Ares", ("sqare", "are", "ares", "square are")),
    ("area", "sqbarn", "Barns", ("sqbarn", "barn", "barns", "square barn")),
    ("area", "sqhectare", "Hectares", ("sqhectare", "hectare", "hectares", "square hectare")),
    ("area", "sqhomestead", "Homesteads", ("sqhomestead", "homestead", "homesteads", "square homestead")),
    ("digital", "bit", "Bits", ("bit", "bits")),
    ("digital", "byte", "Bytes", ("byte", "bytes", "B")),
    ("digital", "kB", "Kilobytes", ("kb", "kilobyte", "kilobytes")),
    ("digital", "MB", "Megabytes", ("mb", "megabyte", "megabytes")),
    ("digital", "GB", "Gigabytes", ("gb", "gigabyte", "gigabytes")),
    ("digital", "TB", "Terabytes", ("tb", "terabyte", "terabytes")),
    ("digital", "PB", "Petabytes", ("pb", "petabyte", "petabytes")),
    ("weight", "kg", "Kilogram", ("kg", "kilogram", "kilograms")),
    ("weight", "hg", "Hectogram", ("hg", "hectogram", "hectograms")),
    ("weight", "dag", "Decagram", ("dag", "decagram", "decagrams")),
    ("weight", "g", "Gram", ("g", "gram", "grams")),
    ("weight", "dg", "Decigram", ("dg", "decigram", "decigrams")),
    ("weight", "cg", "Centigram", ("cg", "centigram", "centigrams")),
    ("weight", "mg", "Milligram", ("mg", "milligram", "milligrams")),
    ("volume", "ml", "Milliliter", ("ml", "milliliter", "milliliters", "millilitre", "millilitres")),
    ("volume", "l", "Liter", ("l", "liter", "liters", "litre", "litres")),
    ("volume", "tsp", "U.S. customary teaspoon", ("tsp", "teaspoon", "teaspoons", "us teaspoon")),
    ("volume", "tbsp", "U.S. customary tablespoon", ("tbsp", "tablespoon", "tablespoons", "us tablespoon")),
    ("volume", "cup", "U.S. customary cup", ("cup", "cups", "us cup")),
    ("volume", "floz", "U.S. customary fluid ounce", ("floz", "us fl oz", "us fluid ounce", "us fluid ounces")),
    ("volume", "pint", "U.S. customary liquid pint", ("pint", "pints", "us pint")),
    ("volume", "quart", "U.S. customary liquid quart", ("quart", "quarts", "us quart")),
    ("volume", "gal", "U.S. customary liquid gallon", ("gal", "gallon", "gallons", "us gallon")),
    ("volume", "m3", "Cubic meters", ("m3", "cubic meter", "cubic meters", "cubic metre", "cubic metres")),
    ("volume", "cm3", "Cubic centimeters", ("cm3", "cubic centimeter", "cubic centimeters", "cubic centimetre", "cubic centimetres")),
    ("volume", "in3", "Cubic inches", ("in3", "cubic inch", "cubic inches")),
    ("volume", "ft3", "Cubic feet", ("ft3", "cubic foot", "cubic feet")),
    ("speed", "mps", "Meters/sec", ("mps", "m/s", "meter per second", "meters per second")),
    ("speed", "kph", "Kilometers/hr", ("kph", "km/h", "km/hr", "kilometers per hour")),
    ("speed", "mph", "Miles/hr", ("mph", "mile per hour", "miles per hour")),
    ("speed", "fps", "Feet/sec", ("fps", "ft/s", "feet per second")),
    ("speed", "knot", "Knots", ("knot", "knots", "kt")),
    ("speed", "mach", "Mach (dry air at 20 °C)", ("mach", "mach 1")),
    ("time", "us", "Microseconds", ("us", "microsecond", "microseconds", "µs")),
    ("time", "ms", "Milliseconds", ("ms", "millisecond", "milliseconds")),
    ("time", "sec", "Seconds", ("sec", "s", "second", "seconds")),
    ("time", "min", "Minutes", ("min", "minute", "minutes")),
    ("time", "hr", "Hours", ("hr", "h", "hour", "hours")),
    ("time", "day", "Days", ("day", "days")),
    ("time", "week", "Weeks", ("week", "weeks")),
    ("time", "month", "Average Gregorian month", ("month", "months", "average gregorian month")),
    ("time", "year", "Average Gregorian year", ("year", "years", "average gregorian year")),
    ("pressure", "pa", "Pascal", ("pa", "pascal", "pascals")),
    ("pressure", "kpa", "Kilopascal", ("kpa", "kilopascal", "kilopascals")),
    ("pressure", "bar", "Bar", ("bar", "bars")),
    ("pressure", "psi", "PSI", ("psi", "pound per square inch", "pounds per square inch")),
    ("pressure", "atm", "Atmosphere", ("atm", "atmosphere", "atmospheres")),
    ("pressure", "torr", "Torr", ("torr",)),
    ("pressure", "mmhg", "mmHg", ("mmhg", "mm hg")),
    ("energy", "j", "Joule", ("j", "joule", "joules")),
    ("energy", "kj", "Kilojoule", ("kj", "kilojoule", "kilojoules")),
    ("energy", "cal", "Calorie (thermochemical)", ("cal", "thermochemical calorie")),
    ("energy", "kcal", "Kilocalorie (thermochemical)", ("kcal", "thermochemical kilocalorie")),
    ("energy", "wh", "Watt-hour", ("wh", "watt hour", "watt hours")),
    ("energy", "kwh", "Kilowatt-hour", ("kwh", "kilowatt hour", "kilowatt hours")),
    ("energy", "btu", "BTU (IT)", ("btu", "it btu", "international table btu")),
    ("energy", "ftlb", "Foot-pound force", ("ftlb", "foot pound force", "foot-pounds force")),
    ("energy", "ev", "Electronvolt", ("ev", "electronvolt", "electronvolts")),
    ("temperature", "c", "Celsius", ("c", "°c", "celsius", "degrees celsius")),
    ("temperature", "f", "Fahrenheit", ("f", "°f", "fahrenheit", "degrees fahrenheit")),
    ("temperature", "k", "Kelvin", ("k", "kelvin", "kelvins")),
    ("angle", "rad", "Radians", ("rad", "radian", "radians")),
    ("angle", "deg", "Degrees", ("deg", "degree", "degrees", "°")),
    ("angle", "grad", "Gradians", ("grad", "gon", "gradian", "gradians")),
    ("angle", "turn", "Turns", ("turn", "turns", "revolution", "revolutions")),
    ("angle", "arcmin", "Arcminutes", ("arcmin", "arcminute", "arcminutes")),
    ("angle", "arcsec", "Arcseconds", ("arcsec", "arcsecond", "arcseconds")),
    ("data_rate", "bit/s", "bit/s", ("bit/s", "bps", "bits per second")),
    ("data_rate", "kbit/s", "kbit/s", ("kbit/s", "kilobit/s", "kilobits per second")),
    ("data_rate", "Mbit/s", "Mbit/s", ("mbit/s", "megabit/s", "megabits per second")),
    ("data_rate", "Gbit/s", "Gbit/s", ("gbit/s", "gigabit/s", "gigabits per second")),
    ("data_rate", "Tbit/s", "Tbit/s", ("tbit/s", "terabit/s", "terabits per second")),
    ("data_rate", "byte/s", "Byte/s", ("byte/s", "bytes per second")),
    ("data_rate", "kB/s", "kB/s", ("kb/s", "kilobyte/s", "kilobytes per second")),
    ("data_rate", "MB/s", "MB/s", ("mb/s", "megabyte/s", "megabytes per second")),
    ("data_rate", "GB/s", "GB/s", ("gb/s", "gigabyte/s", "gigabytes per second")),
    ("data_rate", "TB/s", "TB/s", ("tb/s", "terabyte/s", "terabytes per second")),
    ("data_rate", "Kibit/s", "Kibit/s", ("kibit/s", "kibibit/s")),
    ("data_rate", "Mibit/s", "Mibit/s", ("mibit/s", "mebibit/s")),
    ("data_rate", "Gibit/s", "Gibit/s", ("gibit/s", "gibibit/s")),
    ("data_rate", "Tibit/s", "Tibit/s", ("tibit/s", "tebibit/s")),
    ("data_rate", "KiB/s", "KiB/s", ("kib/s", "kibibyte/s")),
    ("data_rate", "MiB/s", "MiB/s", ("mib/s", "mebibyte/s")),
    ("data_rate", "GiB/s", "GiB/s", ("gib/s", "gibibyte/s")),
    ("data_rate", "TiB/s", "TiB/s", ("tib/s", "tebibyte/s")),
    ("fuel_economy", "l_per_100km", "L/100 km", ("l/100 km", "l/100km", "liters per 100 km", "litres per 100 km")),
    ("fuel_economy", "km_per_l", "km/L", ("km/l", "kilometers per liter", "kilometres per litre")),
    ("fuel_economy", "mpg_us", "U.S. mpg", ("mpg", "mpg us", "mpg (us)", "us mpg", "u.s. mpg")),
    ("fuel_economy", "mpg_imp", "Imperial mpg", ("mpg imp", "mpg imperial", "mpg (imperial)", "imperial mpg")),
]


def _build_registry():
    registry = {}
    for category, code, label, aliases in _definitions:
        unit = UnitRef(category, code, label)
        for alias in (code, label, *aliases):
            normalized = _normalize(alias)
            units = registry.setdefault(normalized, [])
            if unit not in units:
                units.append(unit)
    return {alias: tuple(units) for alias, units in registry.items()}


UNIT_REGISTRY = _build_registry()


def resolve_unit(alias: str) -> UnitRef:
    normalized = _normalize(alias)
    matches = UNIT_REGISTRY.get(normalized, ())
    if not matches:
        raise ValueError(f"unknown unit {alias!r}")
    if len(matches) != 1:
        categories = ", ".join(sorted({unit.category for unit in matches}))
        raise ValueError(f"ambiguous unit {alias!r}; matches {categories}")
    return matches[0]
