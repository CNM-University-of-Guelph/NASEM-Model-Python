import pytest
import nasem_dairy as nd
import pandas as pd

@pytest.fixture
def protein_requirement_data():
    return pd.read_json("./tests/protein_requirement_equations_test.json")


def test_from_json(protein_requirement_data):
    for index, row in protein_requirement_data.iterrows():
        try:
            func = getattr(nd, row.Name)
            input_params = row.Input.copy()
                        # Check if "coeff_dict" is present in input_params
            if "coeff_dict" in input_params:
                # Assign it the actual dictionary
                input_params["coeff_dict"] = nd.coeff_dict
            if "MP_NP_efficiency_dict" in input_params:
                # Assign it correct dictionary
                input_params['MP_NP_efficiency_dict'] = nd.MP_NP_efficiency_dict  
            
            assert func(**input_params) == pytest.approx(row.Output), f"{row.Name} failed: {func(**input_params)} does not equal {row.Output}"
        except AttributeError:
            print(f"Function {row.Name} not found in module.")
            