import pytest

import nasem_dairy as nd
from nasem_dairy.ration_balancer.input_validation import validate_coeff_dict

def test_not_a_dictionary():
    with pytest.raises(TypeError, match="coeff_dict must be a dictionary"):
        validate_coeff_dict(["not", "a", "dictionary"])


def test_missing_keys():
    user_coeff_dict = {
        'VmMiNInt': 100.8,  
        'VmMiNRDPSlp': 81.56,  
        'KmMiNRDNDF': 0.0939,  
        'KmMiNRDSt': 0.0274
    }
    with pytest.raises(KeyError, match="The following keys are missing from the user entered coeff_dict:"):
        validate_coeff_dict(user_coeff_dict)


def test_incorrect_type():
    user_coeff_dict = nd.coeff_dict.copy()
    user_coeff_dict['VmMiNInt'] = "100.8"
    with pytest.raises(TypeError, match="Value for VmMiNInt must be of type float. Got str instead"):
        validate_coeff_dict(user_coeff_dict)


def test_differing_values(capfd):
    user_coeff_dict = nd.coeff_dict.copy()
    user_coeff_dict['VmMiNInt'] = 101.0     
    validate_coeff_dict(user_coeff_dict)
    out, err = capfd.readouterr()
    assert "The following keys differ from their default values:" in out
    assert "VmMiNInt: User: 101.0, Default: 100.8" in out


def test_all_values_match(capfd):
    user_coeff_dict = nd.coeff_dict.copy()   
    validate_coeff_dict(user_coeff_dict)
    out, err = capfd.readouterr()
    assert "All values match the default coefficients." in out
