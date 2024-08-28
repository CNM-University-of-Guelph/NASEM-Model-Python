import os

import numpy as np
import pandas as pd
import pytest

import nasem_dairy as nd
import tests.testing_helpers as helper

def load_json(file_path: str) -> pd.DataFrame:    
    return pd.read_json(file_path)


@pytest.mark.parametrize(
        "json_file", 
        helper.find_json_files(os.path.dirname(os.path.abspath(__file__)))
        )
def test_from_json(json_file: str) -> None:
    input_data = load_json(json_file)
    for index, row in input_data.iterrows():
        try:
            func = getattr(nd, row.Name)
            input_params = row.Input.copy()            
            input_params = helper.update_constants(input_params)

            # Convert data types  
            input_params = helper.create_dataframe(input_params)    
            if isinstance(row.Output, dict):
                row.Output = helper.create_dataframe(row.Output)  
            
            convert_to_series = [key for key in input_params.keys() 
                                 if key.endswith('_series')]
            for key in convert_to_series:
                input_params[key.replace("_series", "")] = pd.Series(input_params.pop(key))

            helper.convert_special_input(input_params)             
            row.Output = helper.convert_special_output(row.Output)

            # Run test
            if isinstance(row.Output, list):
                output_series = pd.Series(row.Output)
                input_series = func(**input_params)
                assert helper.compare_series_with_tolerance(input_series, output_series)

            elif isinstance(row.Output, dict):
                helper.compare_dicts_with_tolerance(func(**input_params), row.Output)

            elif isinstance(row.Output, pd.DataFrame):
                pd.testing.assert_frame_equal(
                    func(**input_params), row.Output, rtol=1e-3, atol=1e-2
                    )
            elif isinstance(row.Output, str):
                with pytest.raises(ValueError, match=row.Output):
                    func(**input_params)

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
