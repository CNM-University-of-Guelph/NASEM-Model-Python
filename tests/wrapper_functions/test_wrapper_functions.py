import glob
import json
import os

import numpy as np
import pandas as pd
import pytest

import nasem_dairy as nd
import tests.testing_helpers as helper

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

        convert_to_df = [key for key in input_params.keys() 
                         if key.endswith("_df")]
        for key in convert_to_df:
            input_params[key.replace("_df", "")] = pd.DataFrame(input_params.pop(key))

        # Run test
        if isinstance(output, dict):
            helper.compare_dicts_with_tolerance(func(**input_params), output)
        else:
            raise TypeError(f"Output for {function} is not a dict")

    except AttributeError:
        print(f"Function {function} not found in module.")


# if __name__ == "__main__": 
#     script_dir = os.path.dirname(os.path.abspath(__file__))
#     json_files = helper.find_json_files(script_dir)
#     for json_file in json_files:
#         test_wrapper_functions(json_file)