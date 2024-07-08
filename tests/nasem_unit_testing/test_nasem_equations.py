import os

import numpy as np
import pandas as pd
import pytest

import nasem_dairy as nd


def find_json_files() -> list:
    script_dir = os.path.dirname(os.path.abspath(__file__))
    return [
        os.path.join(script_dir, file) for file in os.listdir(script_dir) 
        if file.endswith(".json")
        ]


def load_json(file_path: str) -> pd.DataFrame:    
    return pd.read_json(file_path).replace(np.nan, None)


def compare_dicts_with_tolerance(input: dict, 
                                 output: dict, 
                                 rtol: float = 1e-3,
                                 atol: float = 1e-2
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


@pytest.mark.parametrize("json_file", find_json_files())
def test_from_json(json_file: str) -> None:
    input_data = load_json(json_file)
    for index, row in input_data.iterrows():
        try:
            func = getattr(nd, row.Name)
            input_params = row.Input.copy()
            
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

            if "df" in input_params:
                input_params["df"] = pd.DataFrame(input_params["df"])           
           
            if isinstance(row.Output, dict):
                compare_dicts_with_tolerance(func(**input_params), row.Output)
            else:
                assert (func(**input_params) == pytest.approx(row.Output), 
                        f"{row.Name} failed: {func(**input_params)}" 
                        f"does not equal {row.Output}")
        
        except AttributeError:
            print(f"Function {row.Name} not found in module.")
