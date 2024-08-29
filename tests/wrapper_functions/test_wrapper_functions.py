import json
import os

import pandas as pd
import pytest

import nasem_dairy as nd
import tests.testing_helpers as helper


def compare_dataframe_columns(df1: pd.DataFrame, df2: pd.DataFrame):
    df1_columns = set(df1.columns)
    df2_columns = set(df2.columns)
    only_in_df1 = df1_columns - df2_columns    
    only_in_df2 = df2_columns - df1_columns
    return only_in_df1, only_in_df2


def read_test_json(file_path: str):
    with open(file_path, "r") as json_file:
        data = json.load(json_file)
    return data["name"], data["input"], data["output"]
    

@pytest.mark.parametrize(
        "json_file", 
        helper.find_json_files(os.path.dirname(os.path.abspath(__file__)))
        )
def test_wrapper_functions(json_file: str) -> None:
    function, input_params, output = read_test_json(json_file)
    try:
        func = getattr(nd, function)
        input_params = helper.update_constants(input_params)
        input_params = helper.create_dataframe(input_params)
        convert_to_series = [key for key in input_params.keys() 
                        if key.endswith('_series')]
        for key in convert_to_series:
            input_params[key.replace("_series", "")] = pd.Series(
                input_params.pop(key)
                )
        output = helper.create_dataframe(output)

        input_df = func(**input_params)
        output_df = output.copy()
        only_in_left, only_in_right = compare_dataframe_columns(
            input_df, output_df
            )

        print("Columns only in the left DataFrame:")
        print(only_in_left)

        print("\nColumns only in the right DataFrame:")
        print(only_in_right)

        # Run test
        if isinstance(output, dict):
            helper.compare_dicts_with_tolerance(func(**input_params), output)
        elif isinstance(output, pd.DataFrame):
            pd.testing.assert_frame_equal(
                func(**input_params), output, check_dtype=False, 
                rtol=1e-3, atol=1e-2
            )
        else:
            raise TypeError(f"Output for {function} is not a dict")

    except AttributeError:
        print(f"Function {function} not found in module.")
