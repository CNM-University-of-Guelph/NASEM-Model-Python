import re

import pytest

from nasem_dairy.model.input_validation import validate_equation_selection

def test_not_a_dictionary():
    with pytest.raises(TypeError, match="equation_selection must be a dict"):
        validate_equation_selection(["not", "a", "dict"])


def test_missing_key_raises_key_error():
    equation_selection = {
        "Use_DNDF_IV": 1,
        "DMIn_eqn": 5,
    }
    with pytest.raises(KeyError, match="The following keys are missing: "):
        validate_equation_selection(equation_selection)


def test_invalid_value_type():
    equation_selection = {
        "Use_DNDF_IV": 1,
        "DMIn_eqn": 5,
        "mProd_eqn": "invalid",
        "MiN_eqn": 2,
        "NonMilkCP_ClfLiq": 1,
        "Monensin_eqn": 0,
        "mPrt_eqn": 2,
        "mFat_eqn": 1,
        "RumDevDisc_Clf": 0
    }
    with pytest.raises(
        TypeError, match="Value for mProd_eqn must be of type int."
                         " Got str instead and failed to convert."):
        validate_equation_selection(equation_selection)


def test_invalid_value_range():
    equation_selection = {
        "Use_DNDF_IV": 1,
        "DMIn_eqn": 20,
        "mProd_eqn": 3,
        "MiN_eqn": 2,
        "NonMilkCP_ClfLiq": 1,
        "Monensin_eqn": 0,
        "mPrt_eqn": 2,
        "mFat_eqn": 1,
        "RumDevDisc_Clf": 0
    }
    with pytest.raises(ValueError, match=re.escape(
        "DMIn_eqn must be one of (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13,"
         " 14, 15, 16, 17, 18), 20 was given"
         )):
        validate_equation_selection(equation_selection)


def test_valid_input():
    equation_selection = {
        "Use_DNDF_IV": 1,
        "DMIn_eqn": 5,
        "mProd_eqn": 3,
        "MiN_eqn": 2,
        "NonMilkCP_ClfLiq": 1,
        "Monensin_eqn": 0,
        "mPrt_eqn": 2,
        "mFat_eqn": 1,
        "RumDevDisc_Clf": 0
    }
    result = validate_equation_selection(equation_selection)
    assert result == equation_selection
    