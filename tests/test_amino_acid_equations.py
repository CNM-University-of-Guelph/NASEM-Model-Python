# NOTE calculate Abs_AA_g needs a test but first the function needs to be refactored

import pytest
import nasem_dairy as nd
import pandas as pd

from nasem_dairy.NASEM_equations.dev_amino_acid_equations import calculate_Abs_AA_g

@pytest.fixture
def nutrient_intakes_data():
    return pd.read_json("./tests/amino_acid_test.json")


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
