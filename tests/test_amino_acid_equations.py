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


def test_calculate_Abs_AA_g():
    diet_data = {
        'Dt_IdArg_RUPIn': 1.0,
        'Dt_IdHis_RUPIn': 2.0,
        'Dt_IdIle_RUPIn': 3.0,
        'Dt_IdLeu_RUPIn': 4.0,
        'Dt_IdLys_RUPIn': 5.0,
        'Dt_IdMet_RUPIn': 6.0,
        'Dt_IdPhe_RUPIn': 7.0,
        'Dt_IdThr_RUPIn': 8.0,
        'Dt_IdTrp_RUPIn': 9.0,
        'Dt_IdVal_RUPIn': 10.0,
        }
    AA_list = ['Arg', 'His', 'Ile', 'Leu', 'Lys', 'Met', 'Phe', 'Thr', 'Trp', 'Val']
    result = calculate_Abs_AA_g(diet_data, 50, AA_list)





