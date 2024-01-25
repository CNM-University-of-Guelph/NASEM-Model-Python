import pytest
import nasem_dairy as nd
import pandas as pd

# TODO Add tests for wrapper functions calculate_An_data_initial and calculate_An_data_complete

@pytest.fixture
def nutrient_intakes_data():
    return pd.read_json("./tests/animal_equations_test.json")


def test_from_json(nutrient_intakes_data):
    for index, row in nutrient_intakes_data.iterrows():
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
