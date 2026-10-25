"""Data-rate conversion factors relative to bits per second."""

from .conversion_utils import convert_by_factors


factors = {
    "bit/s": 1,
    "kbit/s": 1_000,
    "Mbit/s": 1_000_000,
    "Gbit/s": 1_000_000_000,
    "Tbit/s": 1_000_000_000_000,
    "byte/s": 8,
    "kB/s": 8_000,
    "MB/s": 8_000_000,
    "GB/s": 8_000_000_000,
    "TB/s": 8_000_000_000_000,
    "Kibit/s": 1024,
    "Mibit/s": 1024**2,
    "Gibit/s": 1024**3,
    "Tibit/s": 1024**4,
    "KiB/s": 8 * 1024,
    "MiB/s": 8 * 1024**2,
    "GiB/s": 8 * 1024**3,
    "TiB/s": 8 * 1024**4,
}


def convert(amt, frm, to):
    return convert_by_factors(amt, frm, to, factors)
