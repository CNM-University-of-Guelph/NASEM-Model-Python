import os

import numpy as np
import pandas as pd

import nasem_dairy as nd

rtol = 1e-3
atol = 1e-2

def find_json_files(directory: str) -> list:
    """
    Finds all JSON files in the specified directory.

    Args:
        directory (str): Path of the directory to search.

    Returns:
        list: A list of JSON file paths.

    Example:
        find_json_files(os.path.dirname(os.path.abspath(__file__)))
    """
    files = os.listdir(directory)
    json_files = [os.path.join(directory, file) for file in files 
                  if file.endswith(".json")]
    return json_files


def compare_dicts_with_tolerance(input: dict, 
                                 output: dict,
                                 rtol: float = rtol,
                                 atol: float = atol
) -> None:
    """
    Compares two dictionaries with numerical values with a tolerance.

    Args:
        input (dict): The input dictionary with expected values.
        output (dict): The output dictionary with actual values.
        rtol (float): The relative tolerance parameter (default is 1e-3).
        atol (float): The absolute tolerance parameter (default is 1e-2).

    Raises:
        AssertionError: If numerical values do not match within tolerance.
        KeyError: If keys in the input dictionary are missing from the output dictionary.
    """
    for key in (key for key in input if key in output):
        try:
            np.testing.assert_allclose(
                input[key], output[key], rtol=rtol, atol=atol
                )
        except AssertionError as e:
            print(f"Mismatch found for key '{key}': {input[key]} (expected)"
                    f" vs {output[key]} (actual)")
            raise e
    missing_keys = [key for key in input if key not in output]
    if missing_keys:
        raise KeyError(f"Keys {missing_keys} not found in the output dictionary")



def compare_series_with_tolerance(input: pd.Series,
                                  output: pd.Series,
                                  rtol: float = rtol,
                                  atol: float = atol
) -> bool:
    """
    Compares two pandas Series with numerical values with a tolerance.

    Args:
        input (pd.Series): The input Series with expected values.
        output (pd.Series): The output Series with actual values.
        rtol (float): The relative tolerance parameter (default is 1e-3).
        atol (float): The absolute tolerance parameter (default is 1e-2).

    Returns:
        bool: True if Series are equal within tolerance, otherwise False.
    """
    return np.allclose(input, output, rtol=rtol, atol=atol, equal_nan=True)


def replace_nan_in_input(input_dict: dict) -> None:
    """
    Recursively replaces string "nan" with numpy.nan in a dictionary.

    Args:
        input_dict (dict): The input dictionary to process.
    """
    for key, value in input_dict.items():
        if isinstance(value, dict):
            replace_nan_in_input(value)
        elif isinstance(value, pd.DataFrame):
            input_dict[key] = value.map(lambda x: np.nan if x == "nan" else x)
        elif isinstance(value, pd.Series):
            input_dict[key] = value.apply(lambda x: np.nan if x == "nan" else x)
        else:
            input_dict[key] = np.nan if value == "nan" else value


def update_constants(input_params: dict) -> dict:
    """
    Updates the input parameters with default values if they are None.

    Args:
        input_params (dict): The dictionary of input parameters to update.

    Returns:
        dict: The updated dictionary of input parameters.
    """
    default_values = {
        "coeff_dict": nd.coeff_dict,
        "MP_NP_efficiency_dict": nd.MP_NP_efficiency_dict,
        "mPrt_coeff": nd.mPrt_coeff_list[0],  # NOTE We could dynamically select if needed
        "f_Imb": nd.f_Imb,
        "AA_list": ["Arg", "His", "Ile", "Leu", "Lys", "Met", "Phe", "Thr", "Trp", "Val"]
    }
    
    for key, default_value in default_values.items():
        if key in input_params and input_params[key] is None:
            input_params[key] = default_value
    return input_params
