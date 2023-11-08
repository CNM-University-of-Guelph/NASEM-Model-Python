from nasem_dairy.NASEM_equations.temporary_functions import calculate_Mlk_MEout
from nasem_dairy.ration_balancer.coeff_dict import coeff_dict
from nasem_dairy.ration_balancer.ration_balancer_functions import check_coeffs_in_coeff_dict
import pytest

def test_Mlk_MEout():
    result = calculate_Mlk_MEout(30, 0.7, coeff_dict)
    assert result == pytest.approx(31.818181), "Result does not equal 31.818181"

