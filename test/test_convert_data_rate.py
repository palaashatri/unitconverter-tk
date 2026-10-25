from itertools import product

import pytest

from src import convert_data_rate


REFERENCE_BITS_PER_SECOND = {
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


@pytest.mark.parametrize("unit,expected", REFERENCE_BITS_PER_SECOND.items())
def test_each_data_rate_unit_matches_bits_per_second(unit, expected):
    assert convert_data_rate.convert(1, unit, "bit/s") == pytest.approx(expected)


def test_all_data_rate_unit_pairs_round_trip():
    for source, target in product(REFERENCE_BITS_PER_SECOND, repeat=2):
        result = convert_data_rate.convert(3.125, source, target)
        assert convert_data_rate.convert(result, target, source) == pytest.approx(3.125)


@pytest.mark.parametrize("source,target", [("unknown", "bit/s"), ("bit/s", "unknown")])
def test_data_rate_converter_rejects_unknown_units(source, target):
    with pytest.raises(ValueError, match="unit"):
        convert_data_rate.convert(1, source, target)
