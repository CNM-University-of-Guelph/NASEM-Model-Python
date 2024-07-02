import pytest

from nasem_dairy.ration_balancer.input_validation import validate_MP_NP_efficiency_input

def test_not_a_dictionary():
    with pytest.raises(TypeError, match="MP_NP_efficiency_input must be a dict"):
        validate_MP_NP_efficiency_input(["not", "a", "dict"])


def test_missing_key_raises_key_error():
    MP_NP_efficiency_input = {
        'Trg_AbsHis_NPHis': 0.75,
        'Trg_AbsIle_NPIle': 0.71,
        'Trg_AbsLeu_NPLeu': 0.73,
        'Trg_AbsLys_NPLys': 0.72,
        'Trg_AbsMet_NPMet': 0.73,
        'Trg_AbsPhe_NPPhe': 0.6,
        'Trg_AbsThr_NPThr': 0.64,
        'Trg_AbsTrp_NPTrp': 0.86,
        'Trg_AbsVal_NPVal': 0.74
    }
    with pytest.raises(KeyError, match="The following keys are missing"):
        validate_MP_NP_efficiency_input(MP_NP_efficiency_input)


def test_correct_data_types():
    MP_NP_efficiency_input = {
        'Trg_AbsHis_NPHis': "0.75",
        'Trg_AbsIle_NPIle': "0.71",
        'Trg_AbsLeu_NPLeu': "0.73",
        'Trg_AbsLys_NPLys': "0.72",
        'Trg_AbsMet_NPMet': "0.73",
        'Trg_AbsPhe_NPPhe': "0.6",
        'Trg_AbsThr_NPThr': "0.64",
        'Trg_AbsTrp_NPTrp': "0.86",
        'Trg_AbsVal_NPVal': "0.74",
        'Trg_MP_NP': "0.69"
    }
    result = validate_MP_NP_efficiency_input(MP_NP_efficiency_input)
    for key, value in MP_NP_efficiency_input.items():
        assert isinstance(result[key], float)


def test_invalid_conversion():
    MP_NP_efficiency_input = {
        'Trg_AbsHis_NPHis': "seventy-five",
        'Trg_AbsIle_NPIle': "0.71",
        'Trg_AbsLeu_NPLeu': "0.73",
        'Trg_AbsLys_NPLys': "0.72",
        'Trg_AbsMet_NPMet': "0.73",
        'Trg_AbsPhe_NPPhe': "0.6",
        'Trg_AbsThr_NPThr': "0.64",
        'Trg_AbsTrp_NPTrp': "0.86",
        'Trg_AbsVal_NPVal': "0.74",
        'Trg_MP_NP': "0.69"
    }
    with pytest.raises(TypeError, match="Value for Trg_AbsHis_NPHis must be of type float"):
        validate_MP_NP_efficiency_input(MP_NP_efficiency_input)


def test_valid_input():
    MP_NP_efficiency_input = {
        'Trg_AbsHis_NPHis': 0.75,
        'Trg_AbsIle_NPIle': 0.71,
        'Trg_AbsLeu_NPLeu': 0.73,
        'Trg_AbsLys_NPLys': 0.72,
        'Trg_AbsMet_NPMet': 0.73,
        'Trg_AbsPhe_NPPhe': 0.6,
        'Trg_AbsThr_NPThr': 0.64,
        'Trg_AbsTrp_NPTrp': 0.86,
        'Trg_AbsVal_NPVal': 0.74,
        'Trg_MP_NP': 0.69
    }
    result = validate_MP_NP_efficiency_input(MP_NP_efficiency_input)
    assert result == MP_NP_efficiency_input
