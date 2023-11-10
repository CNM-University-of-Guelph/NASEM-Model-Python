import pytest
from nasem_dairy.NASEM_equations.dev_DMI_equations import calculate_Dt_DMIn_Lact1


def test_Dt_DMIn_Lact1():
    result = calculate_Dt_DMIn_Lact1(30, 700, 3, 160, 1, 0.75)
    assert result == pytest.approx(23.894448), "Dt_DMIn_Lact1 does not equal 23.894448"