import math

import pytest

from src.conversion_utils import require_finite


@pytest.mark.parametrize("value", [0, 1.25, -3.5])
def test_require_finite_preserves_finite_values(value):
    assert require_finite(value) == value


@pytest.mark.parametrize("value", [math.nan, math.inf, -math.inf])
def test_require_finite_rejects_non_finite_values(value):
    with pytest.raises(ValueError, match="finite"):
        require_finite(value)
