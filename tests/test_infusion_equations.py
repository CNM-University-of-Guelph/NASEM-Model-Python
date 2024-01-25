import pytest
import nasem_dairy as nd
import pandas as pd

# TODO add test for wrapper function

@pytest.fixture
def infusion_data():
    return pd.read_json("./tests/infusion_equations_test.json")


def test_from_json(infusion_data):
    for index, row in infusion_data.iterrows():
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