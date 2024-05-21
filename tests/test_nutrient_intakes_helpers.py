import os

import pandas as pd
import pytest
import numpy as np

import nasem_dairy as nd

@pytest.fixture
def nutrient_intake_dfs():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    return pd.read_json(os.path.join(script_dir, 
                                     "nutrient_intakes_helpers_test.json"))


def compare_values_with_tolerance(val1, val2, rtol=1e-3, atol=1e-2):
    if (isinstance(val1, (list, np.ndarray, pd.Series)) and 
        isinstance(val2, (list, np.ndarray, pd.Series))
        ):
        np.testing.assert_allclose(val1, val2, rtol=rtol, atol=atol)
    else:
        np.testing.assert_allclose([val1], [val2], rtol=rtol, atol=atol)


def compare_dicts_with_tolerance(dict1, dict2, rtol=1e-3, atol=1e-2):
    for key in dict1:
        if key in dict2:
            try:
                compare_values_with_tolerance(dict1[key], dict2[key], 
                                              rtol=rtol, atol=atol
                                              )
            except AssertionError as e:
                print(f"Mismatch found for key '{key}': {dict1[key]} (expected)"
                      f" vs {dict2[key]} (actual)")
                raise e
        else:
            raise KeyError(f"Key {key} not found in both dictionaries")


def test_from_json_dict(nutrient_intake_dfs):
    for index, row in nutrient_intake_dfs.iterrows():
        func = getattr(nd, row.Name)
        input_params = row.Input.copy()
        
        # Convert input DataFrame if present
        if 'df' in input_params:
            input_params['df'] = pd.DataFrame(input_params['df'])
        if (('coeff_dict' in input_params) and 
            (input_params['coeff_dict'] == None)
            ):
            input_params['coeff_dict'] = nd.coeff_dict
        
        # Determine if the expected output is a DataFrame or a dictionary
        if isinstance(row.Output, dict):
            expected_output = row.Output
            result = func(**input_params)
            
            # Print debug information
            print(f"Testing function: {row.Name}")
            if 'df' in input_params:
                print("Input DataFrame:")
                print(input_params['df'])
            print("Expected Output:")
            print(expected_output)
            print("Result:")
            print(result)
            
            compare_dicts_with_tolerance(result, expected_output)
        else:
            expected_output = pd.DataFrame(row.Output)
            result = func(**input_params)
            
            # Print debug information
            print(f"Testing function: {row.Name}")
            if 'df' in input_params:
                print("Input DataFrame:")
                print(input_params['df'])
            print("Expected Output DataFrame:")
            print(expected_output)
            print("Result DataFrame:")
            print(result)
            
            pd.testing.assert_frame_equal(result, expected_output, 
                                          rtol=1e-3, atol=1e-2)

if __name__ == "__main__":
    pytest.main(['./tests/test_nutrient_intakes_helpers.py'])
