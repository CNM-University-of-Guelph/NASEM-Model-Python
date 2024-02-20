import pytest
import nasem_dairy as nd
import pandas as pd
from nasem_dairy.NASEM_equations.amino_acid_equations import calculate_Abs_AA_g


@pytest.fixture
def sample_data():
    AA_list = ["AA1", "AA2", "AA3", "AA4", "AA5", "AA6", "AA7", "AA8", "AA9", "AA10"]
    # Assign value based on last character of AA name, AA1 = 1.0, AA2 = 2.0, etc.
    An_data = {f"An_Id{AA}In": float(AA[-1]) for AA in AA_list}
    infusion_data = {f"Inf_{AA}_g": float(AA[-1]) + 1.0 for AA in AA_list}
    Inf_Art = 3.0
    return AA_list, An_data, infusion_data, Inf_Art


def test_calculate_Abs_AA_g(sample_data):
    AA_list, An_data, infusion_data, Inf_Art = sample_data
    result = calculate_Abs_AA_g(AA_list, An_data, infusion_data, Inf_Art)
    # Check the result is a Pandas Series
    assert isinstance(result, pd.Series)
    expected_value = {
        "AA1": 7,
        "AA2": 11,
        "AA3": 15,
        "AA4": 19,
        "AA5": 23,
        "AA6": 27,
        "AA7": 31,
        "AA8": 35,
        "AA9": 39,
        "AA10": 3
    }
    for AA in AA_list:
        assert result[AA] == expected_value[AA]


@pytest.fixture
def amino_acid_data():
    return pd.read_json("./tests/amino_acid_test.json")


def test_from_json(amino_acid_data):
    for index, row in amino_acid_data.iterrows():
        try:
            func = getattr(nd, row.Name)
            input_params = row.Input.copy()
                        # Check if "coeff_dict" is present in input_params
            if "coeff_dict" in input_params:
                # Assign it the actual dictionary
                input_params["coeff_dict"] = nd.coeff_dict            
            
            assert func(**input_params) == pytest.approx(row.Output), f"{row.Name} failed: {func(**input_params)} does not equal {row.Output}"
        except AttributeError:
            print(f"Function {row.Name} not found in module.")
