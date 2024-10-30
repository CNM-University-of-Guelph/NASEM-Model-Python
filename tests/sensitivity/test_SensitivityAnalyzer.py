import os
import pickle
import pytest
from unittest.mock import patch, MagicMock

import numpy as np
import pandas as pd

from nasem_dairy.sensitivity.SensitivityAnalyzer import SensitivityAnalyzer
from nasem_dairy.data.constants import coeff_dict
from nasem_dairy.model.utility import demo


# Sample data for mocking
mock_problem_df = pd.DataFrame([{'problem_id': 1, 'date_run': '2024-10-29', 'filename': 'test_file.csv'}])
mock_samples_df = pd.DataFrame([{'sample_id': 1, 'sample_index': 0, 'param1': 0.1, 'param2': 0.2}])
mock_response_df = pd.DataFrame([{'sample_id': 1, 'sample_index': 0, 'Mlk_Prod': 30.0}])
mock_response_summary_df = pd.DataFrame([{'Mlk_Prod': [30.0, 31.0, 32.0]}])
mock_variable_list = ['Mlk_Prod', 'Mlk_Fat_g']
mock_problems_by_coeff = pd.DataFrame([{'problem_id': 1, 'date_run': '2024-10-29', 'filename': 'test_file.csv'}])
mock_coefficients_df = pd.DataFrame([{'coeff_id': 1, 'name': 'param1'}])


def test_validate_value_ranges_correct():
    analyzer = SensitivityAnalyzer(db_path=':memory:')
    valid_value_ranges = {'param1': (0.1, 0.5), 'param2': (0.2, 0.6)}
    coeffs = ['param1', 'param2']

    # Should not raise any error
    analyzer._validate_value_ranges(valid_value_ranges, coeffs)


def test_validate_value_ranges_errors():
    analyzer = SensitivityAnalyzer(db_path=':memory:')

    # Test with missing keys
    missing_keys_ranges = {'param1': (0.1, 0.5), 'param3': (0.3, 0.7)}
    coeffs = ['param1', 'param2']
    with pytest.raises(ValueError, match="Keys not found in coefficients:"):
        analyzer._validate_value_ranges(missing_keys_ranges, coeffs)

    # Test with non-numeric value ranges
    non_numeric_ranges = {'param1': ('low', 'high'), 'param2': (0.2, 0.6)}
    with pytest.raises(TypeError, match="All values in value_ranges should be numeric."):
        analyzer._validate_value_ranges(non_numeric_ranges, coeffs)

    # Test with min >= max in value ranges
    invalid_ranges = {'param1': (0.5, 0.1), 'param2': (0.2, 0.6)}
    with pytest.raises(ValueError, match="Min value should be smaller than max value for these keys:"):
        analyzer._validate_value_ranges(invalid_ranges, coeffs)


def test_create_problem_correct():
    analyzer = SensitivityAnalyzer(db_path=':memory:')
    value_ranges = {'param1': (0.1, 0.5), 'param2': (0.2, 0.6)}

    problem = analyzer._create_problem(value_ranges)

    assert problem['num_vars'] == 2, "Number of variables is incorrect."
    assert problem['names'] == ['param1', 'param2'], "Variable names are incorrect."
    assert problem['bounds'] == [(0.1, 0.5), (0.2, 0.6)], "Bounds are incorrect."


def test_update_coeff_dict_correct():
    analyzer = SensitivityAnalyzer(db_path=':memory:')
    param_array = [0.3, 0.4]
    coeff_dict = {'param1': 0.1, 'param2': 0.2}
    coeff_names = ['param1', 'param2']

    updated_coeff_dict = analyzer._update_coeff_dict(param_array, coeff_dict, coeff_names)

    assert updated_coeff_dict['param1'] == 0.3, "param1 was not updated correctly."
    assert updated_coeff_dict['param2'] == 0.4, "param2 was not updated correctly."


@patch('nasem_dairy.model.utility.read_csv_input')
@patch('nasem_dairy.model.utility.read_json_input')
def test_load_input_correct(mock_read_json_input, mock_read_csv_input):
    analyzer = SensitivityAnalyzer(db_path=':memory:')
    mock_read_csv_input.return_value = ("csv_data", {}, {}, {})
    mock_read_json_input.return_value = ("json_data", {}, {}, {})

    result = analyzer._load_input('test_input.csv')
    assert result == ("csv_data", {}, {}, {}), "CSV input was not loaded correctly."
    mock_read_csv_input.assert_called_once()

    result = analyzer._load_input('test_input.json')
    assert result == ("json_data", {}, {}, {}), "JSON input was not loaded correctly."
    mock_read_json_input.assert_called_once()


@patch('nasem_dairy.model.utility.read_csv_input')
@patch('nasem_dairy.model.utility.read_json_input')
def test_load_input_errors(mock_read_json_input, mock_read_csv_input):
    analyzer = SensitivityAnalyzer(db_path=':memory:')

    with pytest.raises(ValueError, match="Unsupported file type: .txt. Only CSV and JSON are supported."):
        analyzer._load_input('test_input.txt')


@patch('pandas.read_csv')
def test_load_feed_library_correct(mock_read_csv):
    analyzer = SensitivityAnalyzer(db_path=':memory:')
    mock_read_csv.return_value = pd.DataFrame({'col1': [1, 2], 'col2': [3, 4]})

    result = analyzer._load_feed_library('feed_library.csv')
    assert not result.empty, "Feed library should not be empty."
    mock_read_csv.assert_called_once_with('feed_library.csv')

    result = analyzer._load_feed_library(None)
    assert result is None, "Feed library should be None when no path is provided."


@patch('os.makedirs')
@patch('nasem_dairy.model_output.ModelOutput.ModelOutput.export_to_JSON')
def test_save_full_model_output_JSON_correct(mock_export_to_JSON, mock_makedirs):
    analyzer = SensitivityAnalyzer(db_path=':memory:')
    mock_model_output = MagicMock()
    mock_model_output.export_to_JSON = mock_export_to_JSON

    problem_id = 1
    sample_index = 0
    expected_dir = os.path.join('model_outputs', f'problem_{problem_id}')
    expected_file_path = os.path.join(expected_dir, f'sample_{sample_index}.json')

    file_path = analyzer._save_full_model_output_JSON(problem_id, sample_index, mock_model_output)

    mock_makedirs.assert_called_once_with(expected_dir, exist_ok=True)
    mock_export_to_JSON.assert_called_once_with(expected_file_path)
    assert file_path == expected_file_path, "File path is incorrect."


@patch('nasem_dairy.sensitivity.SensitivityAnalyzer.SensitivityAnalyzer._load_input')
@patch('nasem_dairy.sensitivity.SensitivityAnalyzer.SensitivityAnalyzer._save_full_model_output_JSON')
@patch('nasem_dairy.sensitivity.DatabaseManager.DatabaseManager.insert_problem')
@patch('nasem_dairy.sensitivity.DatabaseManager.DatabaseManager.insert_sample')
@patch('nasem_dairy.sensitivity.DatabaseManager.DatabaseManager.insert_response_variables')
@patch('nasem_dairy.sensitivity.SensitivityAnalyzer.nasem')
def test_evaluate(
    mock_nasem,
    mock_insert_response_variables,
    mock_insert_sample,
    mock_insert_problem,
    mock_save_full_model_output_JSON,
    mock_load_input
):
    
    demo_file = "lactating_cow_test"
    user_diet, animal_input, equation_selection, infusion_input = demo(
        demo_file
        )

    analyzer = SensitivityAnalyzer(db_path=':memory:')

    # Set up mock return values
    mock_load_input.return_value = (
        user_diet, animal_input, equation_selection, infusion_input
        )
    mock_insert_problem.return_value = 1
    mock_model_output = MagicMock()
    mock_model_output.to_response_variables.return_value = {
        "Mlk_Prod": 30.0, "Mlk_Fat_g": 15.0
    }
    mock_nasem.return_value = mock_model_output
    mock_insert_sample.return_value = 1
    mock_save_full_model_output_JSON.return_value = "path/to/full_output.json"

    # Define inputs for _evaluate
    param_values = [[0.1, 0.2], [0.3, 0.4]]
    coeff_dict_in = coeff_dict
    coeff_names = ['param1', 'param2']
    input_path = demo_file
    feed_library_path = None
    problem = {
        'num_vars': 2,
        'names': ['param1', 'param2'],
        'bounds': [(0.0, 1.0), (0.0, 1.0)]
    }
    save_full_output = True

    problem_id = analyzer._evaluate(
        param_values, coeff_dict_in, coeff_names, 
        input_path, feed_library_path, problem, save_full_output
    )

    # Verify the interactions
    mock_insert_problem.assert_called_once_with(
        filename=demo_file,
        user_diet=user_diet,
        animal_input=animal_input,
        equation_selection=equation_selection,
        infusion_input=infusion_input,
        problem=problem,
        coefficient_names=coeff_names
    )

    assert mock_nasem.call_count == len(param_values), "nasem called incorrect number of times."
    assert mock_insert_sample.call_count == len(param_values), "insert_sample called incorrect number of times."
    assert mock_insert_response_variables.call_count == len(param_values), "insert_response_variables called incorrect number of times."

    if save_full_output:
        assert mock_save_full_model_output_JSON.call_count == len(param_values)

    assert problem_id == 1


@patch('nasem_dairy.sensitivity.SensitivityAnalyzer.input_validation.validate_coeff_dict')
@patch('nasem_dairy.sensitivity.SensitivityAnalyzer.SensitivityAnalyzer._validate_value_ranges')
@patch('nasem_dairy.sensitivity.DatabaseManager.DatabaseManager.insert_coefficients')
@patch('nasem_dairy.sensitivity.SensitivityAnalyzer.SensitivityAnalyzer._create_problem')
@patch('nasem_dairy.sensitivity.SensitivityAnalyzer.saltelli.sample')
@patch('nasem_dairy.sensitivity.SensitivityAnalyzer.SensitivityAnalyzer._evaluate')
def test_run_sensitivity(
    mock_evaluate,
    mock_sample,
    mock_create_problem,
    mock_insert_coefficients,
    mock_validate_value_ranges,
    mock_validate_coeff_dict
):
    analyzer = SensitivityAnalyzer(db_path=':memory:')

    # Mock return values
    mock_validate_coeff_dict.return_value = {'param1': 0.0, 'param2': 0.0}
    mock_create_problem.return_value = {
        'num_vars': 2,
        'names': ['param1', 'param2'],
        'bounds': [(0.0, 1.0), (0.0, 1.0)]
    }
    mock_sample.return_value = [[0.1, 0.2], [0.3, 0.4]]
    mock_evaluate.return_value = 1

    # Define inputs for run_sensitivity
    value_ranges = {'param1': (0.0, 1.0), 'param2': (0.0, 1.0)}
    num_samples = 2
    input_path = 'input.json'
    feed_library_path = None
    user_coeff_dict = {'param1': 0.0, 'param2': 0.0}
    calc_second_order = True
    save_full_output = True

    analyzer.run_sensitivity(
        value_ranges, num_samples, input_path, feed_library_path, 
        user_coeff_dict, calc_second_order, save_full_output
    )

    mock_validate_coeff_dict.assert_called_once_with(user_coeff_dict)
    mock_validate_value_ranges.assert_called_once_with(value_ranges, list(user_coeff_dict.keys()))
    mock_insert_coefficients.assert_called_once_with(list(value_ranges.keys()))
    mock_create_problem.assert_called_once_with(value_ranges)
    mock_sample.assert_called_once_with(mock_create_problem.return_value, num_samples, calc_second_order=calc_second_order)
    mock_evaluate.assert_called_once_with(
        mock_sample.return_value, mock_validate_coeff_dict.return_value, 
        list(value_ranges.keys()), input_path, feed_library_path, 
        mock_create_problem.return_value, save_full_output
    )


@patch('nasem_dairy.sensitivity.SensitivityAnalyzer.sobol.analyze')
@patch('nasem_dairy.sensitivity.SensitivityAnalyzer.SensitivityAnalyzer.get_problem_details')
@patch('nasem_dairy.sensitivity.SensitivityAnalyzer.SensitivityAnalyzer.get_response_variables')
@patch('nasem_dairy.sensitivity.DatabaseManager.DatabaseManager.insert_results')
def test_analyze(
    mock_insert_results,
    mock_get_response_variables,
    mock_get_problem_details,
    mock_sobol_analyze
):
    analyzer = SensitivityAnalyzer(db_path=':memory:')

    # Mock problem details
    mock_problem_definition = {
        'num_vars': 2,
        'names': ['param1', 'param2'],
        'bounds': [(0.0, 1.0), (0.0, 1.0)]
    }
    mock_problem_df = pd.DataFrame([{
        'problem': mock_problem_definition
    }])
    mock_get_problem_details.return_value = mock_problem_df

    # Mock response variable data
    mock_response_df = pd.DataFrame({
        'sample_id': [1, 2],
        'sample_index': [0, 1],
        'param1': [0.1, 0.2],
        'param2': [0.3, 0.4],
        'Mlk_Prod': [25.0, 30.0]
    })
    mock_get_response_variables.return_value = mock_response_df

    # Mock sensitivity analysis output
    mock_si = {
        'S1': np.array([0.1, 0.2]),
        'ST': np.array([0.3, 0.4]),
        'S2': np.array([[0.0, 0.05], [0.05, 0.0]]),
        'S1_conf': np.array([0.01, 0.02]),
        'ST_conf': np.array([0.03, 0.04]),
        'S2_conf': np.array([[0.0, 0.005], [0.005, 0.0]])
    }
    mock_sobol_analyze.return_value = mock_si

    # Define inputs for the analyze method
    problem_id = 1
    response_variable = 'Mlk_Prod'
    method = 'Sobol'

    # Call the analyze method
    indices_df, s2_df = analyzer.analyze(problem_id, response_variable, method)

    # Verify the interactions
    mock_get_problem_details.assert_called_once_with(problem_id)
    mock_get_response_variables.assert_called_once_with(problem_id, response_variable)
    mock_sobol_analyze.assert_called_once_with(mock_problem_definition, mock_response_df[response_variable].values)

    # Check that results are inserted into the database
    expected_results_data = {
        'S1': pickle.dumps(mock_si['S1']),
        'ST': pickle.dumps(mock_si['ST']),
        'S2': pickle.dumps(mock_si['S2']),
        'S1_conf': pickle.dumps(mock_si['S1_conf']),
        'ST_conf': pickle.dumps(mock_si['ST_conf']),
        'S2_conf': pickle.dumps(mock_si['S2_conf']),
    }
    mock_insert_results.assert_called_once_with(
        problem_id=problem_id,
        response_variable=response_variable,
        method=method,
        analysis_parameters=pickle.dumps({'method': method}),
        **expected_results_data
    )

    # Verify indices_df and s2_df outputs
    expected_indices_df = pd.DataFrame({
        'Parameter': ['param1', 'param2'],
        'S1': [0.1, 0.2],
        'S1_conf': [0.01, 0.02],
        'ST': [0.3, 0.4],
        'ST_conf': [0.03, 0.04]
    })
    pd.testing.assert_frame_equal(indices_df, expected_indices_df)

    expected_s2_df = pd.DataFrame([
        {'Parameter_1': 'param1', 'Parameter_2': 'param2', 'S2': 0.05, 'S2_conf': 0.005}
    ])
    pd.testing.assert_frame_equal(s2_df, expected_s2_df)


@patch('nasem_dairy.sensitivity.DatabaseManager.DatabaseManager.get_all_problems', return_value=mock_problem_df)
def test_get_all_problems(mock_get_all_problems):
    analyzer = SensitivityAnalyzer(db_path=':memory:')
    result = analyzer.get_all_problems()
    mock_get_all_problems.assert_called_once()
    pd.testing.assert_frame_equal(result, mock_problem_df)


@patch('nasem_dairy.sensitivity.DatabaseManager.DatabaseManager.get_samples_for_problem', return_value=mock_samples_df)
def test_get_samples_for_problem(mock_get_samples):
    analyzer = SensitivityAnalyzer(db_path=':memory:')
    problem_id = 1
    result = analyzer.get_samples_for_problem(problem_id)
    mock_get_samples.assert_called_once_with(problem_id)
    pd.testing.assert_frame_equal(result, mock_samples_df)


@patch('nasem_dairy.sensitivity.DatabaseManager.DatabaseManager.get_problem_details', return_value=mock_problem_df)
def test_get_problem_details(mock_get_problem_details):
    analyzer = SensitivityAnalyzer(db_path=':memory:')
    problem_id = 1
    result = analyzer.get_problem_details(problem_id)
    mock_get_problem_details.assert_called_once_with(problem_id)
    pd.testing.assert_frame_equal(result, mock_problem_df)


@patch('nasem_dairy.sensitivity.DatabaseManager.DatabaseManager.get_response_variables', return_value=mock_response_df)
def test_get_response_variables(mock_get_response_vars):
    analyzer = SensitivityAnalyzer(db_path=':memory:')
    problem_id = 1
    variable_names = ['Mlk_Prod']
    result = analyzer.get_response_variables(problem_id, variable_names)
    mock_get_response_vars.assert_called_once_with(problem_id, variable_names)
    pd.testing.assert_frame_equal(result, mock_response_df)


@patch('nasem_dairy.sensitivity.DatabaseManager.DatabaseManager.get_response_variable_summary', return_value=mock_response_summary_df)
def test_get_response_variable_summary(mock_get_summary):
    analyzer = SensitivityAnalyzer(db_path=':memory:')
    problem_id = 1
    result = analyzer.get_response_variable_summary(problem_id)
    mock_get_summary.assert_called_once_with(problem_id)
    pd.testing.assert_frame_equal(result, mock_response_summary_df)


@patch('nasem_dairy.sensitivity.DatabaseManager.DatabaseManager.list_response_variables', return_value=mock_variable_list)
def test_list_response_variables(mock_list_response_vars):
    analyzer = SensitivityAnalyzer(db_path=':memory:')
    result = analyzer.list_response_variables()
    mock_list_response_vars.assert_called_once()
    assert result == mock_variable_list


@patch('nasem_dairy.sensitivity.DatabaseManager.DatabaseManager.get_problems_by_coefficient', return_value=mock_problems_by_coeff)
def test_get_problems_by_coefficient(mock_get_problems_by_coeff):
    analyzer = SensitivityAnalyzer(db_path=':memory:')
    coefficient_name = 'param1'
    result = analyzer.get_problems_by_coefficient(coefficient_name)
    mock_get_problems_by_coeff.assert_called_once_with(coefficient_name)
    pd.testing.assert_frame_equal(result, mock_problems_by_coeff)


@patch('nasem_dairy.sensitivity.DatabaseManager.DatabaseManager.get_coefficients_by_problem', return_value=mock_coefficients_df)
def test_get_coefficients_by_problem(mock_get_coefficients):
    analyzer = SensitivityAnalyzer(db_path=':memory:')
    problem_id = 1
    result = analyzer.get_coefficients_by_problem(problem_id)
    mock_get_coefficients.assert_called_once_with(problem_id)
    pd.testing.assert_frame_equal(result, mock_coefficients_df)
