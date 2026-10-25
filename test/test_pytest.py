import pytest
from src import convert_digital, convert_weight, convert_length, convert_area, convert_temp

def test_convert_digital():
    assert convert_digital.convert(1,"kB","byte") == pytest.approx(1000)

def test_convert_weight():
    assert convert_weight.convert(1,"kg","g") == pytest.approx(1000)

def test_convert_length():
    assert convert_length.convert(1000,"cm","m") == pytest.approx(10)

def test_convert_area():
    assert convert_area.convert(1,"sqm","sqcm") == pytest.approx(10000)

def test_convert_temp():
    assert convert_temp.convert_celToKel(38) == pytest.approx(311.15)
    assert convert_temp.convert_celToFah(38) == pytest.approx(100.4)
