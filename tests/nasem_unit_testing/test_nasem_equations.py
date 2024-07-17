import os

import numpy as np
import pandas as pd
import pytest

import nasem_dairy as nd

rtol = 1e-3
atol = 1e-2

def find_json_files() -> list:
    script_dir = os.path.dirname(os.path.abspath(__file__))
    return [
        os.path.join(script_dir, file) for file in os.listdir(script_dir) 
        if file.endswith(".json")
        ]


def load_json(file_path: str) -> pd.DataFrame:    
    return pd.read_json(file_path)


def replace_nan_in_input(d):
    for key, value in d.items():
        if isinstance(value, dict):
            replace_nan_in_input(value)
        elif isinstance(value, pd.DataFrame):
            d[key] = value.map(lambda x: np.nan if x == "nan" else x)
        elif isinstance(value, pd.Series):
            d[key] = value.apply(lambda x: np.nan if x == "nan" else x)
        else:
            d[key] = np.nan if value == "nan" else value


def compare_dicts_with_tolerance(input: dict, 
                                 output: dict
) -> None:
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
                                  output: pd.Series
) -> bool:
    return np.allclose(input, output, rtol=rtol, atol=atol, equal_nan=True)


@pytest.mark.parametrize("json_file", find_json_files())
def test_from_json(json_file: str) -> None:
    input_data = load_json(json_file)
    for index, row in input_data.iterrows():
        try:
            func = getattr(nd, row.Name)
            input_params = row.Input.copy()
            
            # Load constants
            if (("coeff_dict" in input_params) and
                input_params["coeff_dict"] == None
                ):
                input_params["coeff_dict"] = nd.coeff_dict

            if (("MP_NP_efficiency_dict" in input_params) and
                input_params["MP_NP_efficiency_dict"] == None
                ):
                input_params["MP_NP_efficiency_dict"] = nd.MP_NP_efficiency_dict

            if (("mPrt_coeff" in input_params) and
                input_params["mPrt_coeff"] == None
                ):
                input_params["mPrt_coeff"] = nd.mPrt_coeff_list[0]  # NOTE Is there a way to select dynamically for unit tests?

            if (("f_Imb" in input_params) and
                input_params["f_Imb"] == None
                ):
                input_params["f_Imb"] = nd.f_Imb

            if (("AA_list" in input_params) and
                input_params["AA_list"] == None
                ):
                input_params["AA_list"] = ["Arg", "His", "Ile", "Leu", "Lys", 
                                           "Met", "Phe", "Thr", "Trp", "Val"]

            # Convert data types
            if "df" in input_params:
                input_params["df"] = pd.DataFrame(input_params["df"])           
            
            convert_to_series = [key for key in input_params.keys() 
                                 if key.endswith('_series')]
            for key in convert_to_series:
                input_params[key.replace("_series", "")] = pd.Series(input_params.pop(key))

            replace_nan_in_input(input_params)

            if row.Output == "none":
                row.Output = None

            if row.Output == "nan":
                row.Output = np.nan
            elif isinstance(row.Output, list):
                    row.Output = [np.nan if val == "nan" 
                                  else val for val in row.Output]                

            # Run test
            if isinstance(row.Output, list):
                output_series = pd.Series(row.Output)
                input_series = func(**input_params)
                assert compare_series_with_tolerance(input_series, output_series)

            elif isinstance(row.Output, dict):
                compare_dicts_with_tolerance(func(**input_params), row.Output)

            else:
                result = func(**input_params)
                if row.Output is None:
                    assert result is None, (
                        f"{row.Name} failed: {result} does not equal {row.Output}"
                    )
                elif np.isnan(result) and np.isnan(row.Output):
                    assert True
                else:
                    assert result == pytest.approx(row.Output), (
                        f"{row.Name} failed: {result} does not equal {row.Output}"
                    )


        except AttributeError:
            print(f"Function {row.Name} not found in module.")
