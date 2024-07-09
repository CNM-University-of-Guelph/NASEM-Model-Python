import glob
import json
import math
import os
from typing import Tuple, Dict, Union, List

import importlib_resources
import numpy as np
import pandas as pd
import pytest

from nasem_dairy.ration_balancer.execute_model import execute_model
 
####################
# Define Functions
####################
def read_test_json(file_path: str
) -> Union[Dict, Dict, Dict, Dict, pd.DataFrame, Dict]:
    with open(file_path, 'r') as json_file:
        data = json.load(json_file)

    AA_list = [
        'Arg', 'His', 'Ile', 'Leu', 'Lys', 'Met', 'Phe', 'Thr', 'Trp', 'Val'
    ]

    input_data = data['input']
    output = data['output']
    user_diet_in = pd.DataFrame(input_data['user_diet_in'].items(),
                                columns=['Feedstuff', 'kg_user'])
    animal_input_in = input_data['animal_input_in']
    equation_selection_in = input_data['equation_selection_in']
    coeff_dict_in = input_data["coeff_dict"]
    infusion_input_in = input_data["infusion_input"]
    MP_NP_efficiency_input_in = input_data["MP_NP_efficiency_input"]
    mPrt_coeff_list_in = input_data["mPrt_coeff_list"]
    f_Imb_in = pd.Series(input_data["f_Imb"],
                         index=[
                             'Arg', 'His', 'Ile', 'Leu', 'Lys', 'Met', 'Phe', 
                             'Thr', 'Trp', 'Val'
                             ])
    output_data = output['output_data']
    AA_values = pd.DataFrame(output['AA_values'], index=AA_list)
    AA_values = AA_values.rename(columns={"mPrt_AA_0.1": "mPrt_AA_01"})
    arrays = output['arrays']
    for key in arrays.keys():
        arrays[key] = np.array(arrays[key])
    return (
        user_diet_in, animal_input_in, equation_selection_in, coeff_dict_in, 
        infusion_input_in, MP_NP_efficiency_input_in, mPrt_coeff_list_in, 
        f_Imb_in, output_data, AA_values, arrays
    )


def assert_values(expected_output: dict,
                  expected_AA_values: pd.DataFrame,
                  expected_arrays: dict,
                  model_output: dict,
                  tolerance: float=1e-3
) -> None:
    for key, expected_value in expected_output.items():
        model_value = model_output[key]
        if not isinstance(model_value, str) and not isinstance(
                expected_value, str):
            assert math.isclose(model_value, expected_value, rel_tol=tolerance, abs_tol=tolerance), \
                f"Mismatch for {key}: {model_value} != {expected_value}"

    model_AA_values = model_output['AA_values']
    pd.testing.assert_frame_equal(expected_AA_values,
                                  model_AA_values,
                                  rtol=tolerance,
                                  atol=tolerance)

    for key, value in expected_arrays.items():
        assert np.allclose(expected_arrays[key], model_output[key], rtol=tolerance, atol=tolerance), \
            f"Mismatch for {key}: {model_output[key]} != {expected_arrays[key]}"


@pytest.mark.parametrize("json_file", glob.glob("tests/integration/*.json"))
def test_end_to_end(json_file: str) -> None:
    (
        user_diet_in, animal_input_in, equation_selection_in, coeff_dict_in, 
        infusion_input_in, MP_NP_efficiency_input_in, mPrt_coeff_list_in, 
        f_Imb_in, output_data, AA_values, arrays
    ) = read_test_json(json_file)
    path_to_package_data = importlib_resources.files("nasem_dairy.data")
    feed_library_in = pd.read_csv(
        path_to_package_data.joinpath("NASEM_feed_library.csv"))
    output = execute_model(user_diet=user_diet_in,
                           animal_input=animal_input_in,
                           equation_selection=equation_selection_in,
                           feed_library_df=feed_library_in,
                           coeff_dict=coeff_dict_in,
                           infusion_input=infusion_input_in,
                           MP_NP_efficiency_input=MP_NP_efficiency_input_in,
                           mPrt_coeff_list=mPrt_coeff_list_in,
                           f_Imb=f_Imb_in
                           )
    model_output = output.export_to_dict()
    assert_values(output_data, AA_values, arrays, model_output)
