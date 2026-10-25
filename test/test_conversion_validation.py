import math

import pytest

from src.conversion_utils import convert_by_factors, require_finite


@pytest.mark.parametrize("value", [0, 1.25, -3.5])
def test_require_finite_preserves_finite_values(value):
    assert require_finite(value) == value


@pytest.mark.parametrize("value", [math.nan, math.inf, -math.inf])
def test_require_finite_rejects_non_finite_values(value):
    with pytest.raises(ValueError, match="finite"):
        require_finite(value)


def test_convert_by_factors_converts_and_rejects_unknown_units():
    factors = {"base": 1, "large": 1000}
    assert convert_by_factors(2, "large", "base", factors) == 2000
    with pytest.raises(ValueError, match="unit"):
        convert_by_factors(1, "missing", "base", factors)
