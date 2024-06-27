import pytest

import nasem_dairy as nd
from nasem_dairy.ration_balancer.input_validation import validate_mPrt_coeff_list

def test_not_a_list():
    with pytest.raises(TypeError, match="mPrt_coeff_list must be a list"):
        validate_mPrt_coeff_list("not a list")


def test_not_a_dict_in_list():
    invalid_list = ["not a dict"]
    with pytest.raises(TypeError, match="mPrt_coeff_list\\[0\\] must be a dict"):
        validate_mPrt_coeff_list(invalid_list)


def test_missing_key_raises_key_error():
    invalid_list = [
        {
            "mPrt_Int_src": -97.0,
        }
    ]
    with pytest.raises(KeyError, match="The following keys are missing"):
        validate_mPrt_coeff_list(invalid_list)


def test_non_numeric_value_raises_type_error():
    invalid_list = [
        {
            "mPrt_Int_src": -97.0,
            "mPrt_k_BW_src": -0.4201,
            "mPrt_k_DEInp_src": 10.79,
            "mPrt_k_DigNDF_src": "non-numeric",
            "mPrt_k_DEIn_StFA_src": 0,
            "mPrt_k_DEIn_NDF_src": 0,
            "mPrt_k_Arg_src": 0,
            "mPrt_k_His_src": 1.675,
            "mPrt_k_Ile_src": 0.885,
            "mPrt_k_Leu_src": 0.466,
            "mPrt_k_Lys_src": 1.153,
            "mPrt_k_Met_src": 1.839,
            "mPrt_k_Phe_src": 0,
            "mPrt_k_Thr_src": 0,
            "mPrt_k_Trp_src": 0.0,
            "mPrt_k_Val_src": 0,
            "mPrt_k_NEAA_src": 0,
            "mPrt_k_OthAA_src": 0.0773,
            "mPrt_k_EAA2_src": -0.00215
        }
    ]
    with pytest.raises(TypeError, match="Value for mPrt_k_DigNDF_src in mPrt_coeff_list\\[0\\] must be int or float"):
        validate_mPrt_coeff_list(invalid_list)


def test_valid_input():
    result = validate_mPrt_coeff_list(nd.mPrt_coeff_list)
    assert result == nd.mPrt_coeff_list
