"""Temperature conversion functions with absolute-zero validation."""

from .conversion_utils import require_finite


def _check_kelvin(kel_temp):
    kelvin = require_finite(kel_temp)
    if kelvin < 0:
        raise ValueError("temperature cannot be below absolute zero")
    return kelvin


def _celsius(cel_temp):
    celsius = require_finite(cel_temp)
    if celsius < -273.15:
        raise ValueError("temperature cannot be below absolute zero")
    return celsius


def _fahrenheit(fah_temp):
    fahrenheit = require_finite(fah_temp)
    if fahrenheit < -459.67:
        raise ValueError("temperature cannot be below absolute zero")
    return fahrenheit


def convert_celToFah(celTemp):
    return _celsius(celTemp) * 9 / 5 + 32


def convert_celToKel(celTemp):
    return _celsius(celTemp) + 273.15


def covert_celToKel(celTemp):
    """Deprecated spelling retained for compatibility."""
    return convert_celToKel(celTemp)


def convert_fahToCel(fahTemp):
    return (_fahrenheit(fahTemp) - 32) * (5 / 9)


def convert_fahToKel(fahTemp):
    return (_fahrenheit(fahTemp) - 32) * (5 / 9) + 273.15


def convert_kelToCel(kelTemp):
    return _check_kelvin(kelTemp) - 273.15


def convert_kelTofah(kelTemp):
    return (_check_kelvin(kelTemp) - 273.15) * 9 / 5 + 32
