import pytest
from nasem_dairy.NASEM_equations.dev_milk_equations import calculate_Trg_NEmilk_Milk

def test_Trg_NEmilk_Milk():
    result = calculate_Trg_NEmilk_Milk(3.2, 4.1, 4.85)
    assert result == pytest.approx(0.759665), "Trg_NEmilk_Milk does not equal 0.759665"
