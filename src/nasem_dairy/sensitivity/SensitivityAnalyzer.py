import os
import pickle
from typing import Dict, Tuple, Union, List
import warnings

import pandas as pd
import SALib.sample.saltelli as saltelli
import SALib.analyze.sobol as sobol

from nasem_dairy.data.constants import coeff_dict
import nasem_dairy.model.input_validation as input_validation
from nasem_dairy.model.nasem import nasem
import nasem_dairy.model.utility as utility
from nasem_dairy.model_output.ModelOutput import ModelOutput
from nasem_dairy.sensitivity.DatabaseManager import DatabaseManager

warnings.filterwarnings("ignore", category=FutureWarning, module="SALib")

class SensitivityAnalyzer:
    """Class for running sensitivity analysis of NASEM model.

    This class handles the setup, execution, and analysis of sensitivity 
    experiments, including storage and retrieval of results from a database.
    """
    def __init__(self, db_path: str):
        """Initializes the SensitivityAnalyzer with a database manager.

        Args:
            db_path (str): Path to the SQLite database file.
        """
        self.db_manager = DatabaseManager(db_path)

    def _validate_value_ranges(
        self, 
        value_ranges: Dict[str, Tuple[float, float]], 
        coeffs: List[str]
    ) -> None:
        """Validates the value ranges for sensitivity analysis.

        Ensures that the provided ranges are numeric and that each range 
        contains a minimum value that is less than the maximum value.

        Args:
            value_ranges (Dict[str, Tuple[float, float]]): Dictionary of 
                coefficient names and their min/max ranges.
            coeffs (List[str]): List of coefficient names in coeff_dict.

        Raises:
            ValueError: If any specified coefficients are missing from coeff_dict.
            TypeError: If the min/max values are not numeric.
            ValueError: If any min value is greater than or equal to its max value.
        """
        df = pd.DataFrame.from_dict(
            value_ranges, orient='index', columns=['min', 'max']
            )

        missing_keys = set(df.index) - set(coeffs)
        if missing_keys:
            raise ValueError(
                f"Keys not found in coefficients: {list(missing_keys)}"
                )

        if (not pd.api.types.is_numeric_dtype(df['min']) 
            or not pd.api.types.is_numeric_dtype(df['max'])
            ):
            raise TypeError("All values in value_ranges should be numeric.")

        if not (df['min'] < df['max']).all():
            invalid_rows = df[df['min'] >= df['max']]
            raise ValueError(
                f"Min value should be smaller than max value for these keys: "
                f"{invalid_rows.index.tolist()}"
                )

    def _create_problem(
        self, 
        value_ranges: Dict[str, Tuple[float, float]]
    ) -> Dict[str, Union[int, List[str], List[Tuple[float, float]]]]:
        """Creates the problem definition for SALib package.

        Args:
            value_ranges (Dict[str, Tuple[float, float]]): Dictionary of 
                coefficient names and their min/max ranges.

        Returns:
            Dict[str, Union[int, List[str], List[Tuple[float, float]]]]: 
            A dictionary defining the number of variables, names, and bounds.
        """
        return {
            "num_vars": len(value_ranges.keys()),
            "names": list(value_ranges.keys()),
            "bounds": [val for val in value_ranges.values()]
        }

    def _update_coeff_dict(
        self, 
        param_array: List[float], 
        coeff_dict: Dict[str, float], 
        coeff_names: List[str]
        ) -> Dict[str, float]:
        """Updates the coefficient dictionary with values from a sample.

        Args:
            param_array (List[float]): List of parameter values for a sample.
            coeff_dict (Dict[str, float]): The base coefficient dictionary to modify.
            coeff_names (List[str]): List of coefficient names corresponding to param_array.

        Returns:
            Dict[str, float]: Updated coefficient dictionary.
        """
        modified_coeff_dict = coeff_dict.copy()
        for name, value in zip(coeff_names, param_array):
            modified_coeff_dict[name] = value
        return modified_coeff_dict

    def _load_input(
        self, 
        input_path: str
    ) -> Tuple[pd.DataFrame, Dict, Dict, Dict]:
        """Loads the input data from a specified file.

        Args:
            input_path (str): The path to the input file (CSV or JSON).

        Returns:
            Tuple[Dict, Dict, Dict, Dict]: Parsed data for user_diet, 
                animal_input, equation_selection, and infusion_input.

        Raises:
            ValueError: If the file type is not supported.
        """
        file_extension = os.path.splitext(input_path)[-1].lower()

        if file_extension == '.csv':
            return utility.read_csv_input(input_path)
        elif file_extension == '.json':
            return utility.read_json_input(input_path)
        else:
            raise ValueError(
                f"Unsupported file type: {file_extension}. "
                "Only CSV and JSON are supported."
                )

    def _load_feed_library(
        self, 
        feed_library_path: str
    ) -> Union[pd.DataFrame, None]:
        """Loads the feed library from a specified path.

        Args:
            feed_library_path (str): The path to the feed library file.

        Returns:
            Union[pd.DataFrame, None]: The loaded feed library as a 
                DataFrame or None if no path is provided.
        """
        if feed_library_path:
            return pd.read_csv(feed_library_path)
        return None

    def _save_full_model_output_JSON(
        self, 
        problem_id: int, 
        sample_index: int, 
        model_output: ModelOutput
    ) -> str:
        """
        Serialize and save the full model output to a JSON file.

        Args:
            problem_id (int): The problem_id of the current problem.
            sample_index (int): The index of the sample.
            model_output: The ModelOutput instance.

        Returns:
            str: The file path where the model output was saved.
        """
        output_dir = os.path.join('model_outputs', f'problem_{problem_id}')
        os.makedirs(output_dir, exist_ok=True)
        file_path = os.path.join(output_dir, f'sample_{sample_index}.json')
        model_output.export_to_JSON(file_path)

        return file_path

    def _evaluate(
        self, 
        param_values: List[List[float]], 
        coeff_dict: Dict[str, float],           
        coeff_names: List[str], 
        input_path: str, 
        feed_library_path: str,           
        problem: Dict, 
        save_full_output: bool
    ) -> int:
        """Runs the model evaluation for each sample and stores results.

        Args:
            param_values (List[List[float]]): Parameter values for each sample.
            coeff_dict (Dict[str, float]): Base coefficient dictionary.
            coeff_names (List[str]): List of coefficient names.
            input_path (str): Path to the input file.
            feed_library_path (str): Path to the feed library file.
            problem (Dict): Problem definition for the analysis.
            save_full_output (bool): Whether to save full model output to JSON files.

        Returns:
            int: The problem_id of the newly created problem in the database.
        """
        user_diet, animal_input, equation_selection, infusion_input = (
            self._load_input(input_path)
            )
        
        feed_library = self._load_feed_library(feed_library_path)

        # Store the problem information in the Problems table
        problem_id = self.db_manager.insert_problem(
            filename=os.path.basename(input_path),
            user_diet=user_diet,
            animal_input=animal_input,
            equation_selection=equation_selection,
            infusion_input=infusion_input,
            problem=problem,
            coefficient_names=coeff_names
        )

        for index, param_array in enumerate(param_values):
            modified_coeff_dict = self._update_coeff_dict(
                param_array, coeff_dict, coeff_names
            )

            model_output = nasem(
                user_diet, animal_input, equation_selection, 
                feed_library=feed_library, infusion_input=infusion_input, 
                coeff_dict=modified_coeff_dict
            )

            if save_full_output:
                result_file_path = self._save_full_model_output_JSON(
                    problem_id, index, model_output
                    )
            else:
                result_file_path = None

            sample_parameter_values = dict(zip(coeff_names, param_array))
            sample_id = self.db_manager.insert_sample(
                problem_id=problem_id,
                sample_index=index,
                parameter_values=sample_parameter_values,
                result_file_path=result_file_path
            )

            response_variables = model_output.to_response_variables()
            self.db_manager.insert_response_variables(
                problem_id, sample_id, response_variables
                )
        return problem_id
                
    def run_sensitivity(
        self, 
        value_ranges: Dict[str, Tuple[float, float]], 
        num_samples: int,
        input_path: str,
        feed_library_path: str = None,
        user_coeff_dict: Dict[str, Union[int, float]] = coeff_dict,
        calc_second_order: bool = True,
        save_full_output: bool = False
    ) -> None:
        """Executes the sensitivity analysis for the specified value ranges.

        Args:
            value_ranges (Dict[str, Tuple[float, float]]): Dictionary of 
                coefficient names and their min/max ranges.
            num_samples (int): Number of samples to generate.
            input_path (str): Path to the input file.
            feed_library_path (str, optional): Path to the feed library file. 
                Defaults to None.
            user_coeff_dict (Dict[str, Union[int, float]], optional): 
                User-specified coefficient dictionary. Defaults to None.
            calc_second_order (bool, optional): Whether to calculate 
                second-order indices. Defaults to True.
            save_full_output (bool, optional): Whether to save full model 
                outputs to JSON files. Defaults to False.
        """
        validated_coeff_dict = input_validation.validate_coeff_dict(
            user_coeff_dict
            )
        self._validate_value_ranges(
            value_ranges, list(validated_coeff_dict.keys())
            )

        # Update coefficients in table
        self.db_manager.insert_coefficients(list(value_ranges.keys()))

        problem = self._create_problem(value_ranges)
        param_values = saltelli.sample(
            problem, num_samples, calc_second_order=calc_second_order
            )
        problem_id = self._evaluate(
            param_values, validated_coeff_dict, list(value_ranges.keys()), 
            input_path, feed_library_path, problem, save_full_output
            )
        print(
            "Sensitivity Analysis is complete! "
            f"Results are stored as problem_id: {problem_id}"
            )

    def analyze(
        self, 
        problem_id: int, 
        response_variable: str, 
        method: str = 'Sobol'
    ) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Performs sensitivity analysis using SALib and stores results in the database.

        Args:
            problem_id (int): The ID of the problem to analyze.
            response_variable (str): The name of the response variable to analyze.
            method (str, optional): The sensitivity analysis method to use. Defaults to 'Sobol'.

        Returns:
            Tuple[pd.DataFrame, pd.DataFrame]: 
            Two DataFrames - first-order/total-order indices and second-order indices.
        """
        # Step 1: Retrieve the problem definition
        problem_df = self.get_problem_details(problem_id)
        if problem_df.empty:
            raise ValueError(f"No problem found with problem_id {problem_id}")
        
        problem_definition = problem_df.at[0, 'problem']

        # Step 2: Retrieve response variable data (outputs)
        response_df = self.get_response_variables(problem_id, response_variable)
        if response_df.empty:
            raise ValueError(
                f"No response data found for variable '{response_variable}' in "
                f"problem_id {problem_id}"
                )
        Y = response_df[response_variable].values

        # Step 3: Perform sensitivity analysis
        if method.lower() == 'sobol':
            Si = sobol.analyze(problem_definition, Y)
        else:
            raise NotImplementedError(f"Method '{method}' is not implemented")

        # Step 4: Store the results in the Results table
        analysis_parameters = {'method': method}
        results_data = {
            'S1': pickle.dumps(Si['S1']),
            'ST': pickle.dumps(Si['ST']),
            'S2': pickle.dumps(Si['S2']),
            'S1_conf': pickle.dumps(Si['S1_conf']),
            'ST_conf': pickle.dumps(Si['ST_conf']),
            'S2_conf': pickle.dumps(Si['S2_conf']),
        }

        self.db_manager.insert_results(
            problem_id=problem_id,
            response_variable=response_variable,
            method=method,
            analysis_parameters=pickle.dumps(analysis_parameters),
            **results_data
        )

        # Step 5: Prepare output for user
        indices_df = pd.DataFrame({
            'Parameter': problem_definition['names'],
            'S1': Si['S1'],
            'S1_conf': Si['S1_conf'],
            'ST': Si['ST'],
            'ST_conf': Si['ST_conf']
        })

        param_names = problem_definition['names']
        num_params = len(param_names)
        s2_records = []
        for i in range(num_params):
            for j in range(i + 1, num_params):
                s2_record = {
                    'Parameter_1': param_names[i],
                    'Parameter_2': param_names[j],
                    'S2': Si['S2'][i, j],
                    'S2_conf': Si['S2_conf'][i, j]
                }
                s2_records.append(s2_record)

        s2_df = pd.DataFrame(s2_records)

        return indices_df, s2_df

    # Methods for data retrieval
    def get_all_problems(self) -> pd.DataFrame:
        """
        Retrieve all problems in the database.

        Returns:
            pd.DataFrame: A DataFrame containing problem details.
        """
        return self.db_manager.get_all_problems()

    def get_samples_for_problem(self, problem_id: int) -> pd.DataFrame:
        """
        Retrieve all samples for a specific problem.

        Args:
            problem_id (int): The ID of the problem.

        Returns:
            pd.DataFrame: A DataFrame containing sample details and parameter values.
        """
        return self.db_manager.get_samples_for_problem(problem_id)

    def get_problem_details(self, problem_id: int) -> pd.DataFrame:
        """
        Retrieve detailed information about a specific problem.

        Args:
            problem_id (int): The ID of the problem.

        Returns:
            pd.DataFrame: A DataFrame containing problem details.
        """
        return self.db_manager.get_problem_details(problem_id)

    def get_response_variables(
        self, 
        problem_id: int, 
        variable_names: List[str]
    ) -> pd.DataFrame:
        """
        Retrieve multiple response variables for all samples in a problem.

        Args:
            problem_id (int): The ID of the problem.
            variable_names (List[str]): List of variable names to retrieve.

        Returns:
            pd.DataFrame: A DataFrame containing sample_index and the requested variables.
        """
        return self.db_manager.get_response_variables(problem_id, variable_names)

    def get_response_variable_summary(self, problem_id: int) -> pd.DataFrame:
        """
        Provide summary statistics for all response variables in a problem.

        Args:
            problem_id (int): The ID of the problem.

        Returns:
            pd.DataFrame: A DataFrame containing summary statistics for each variable.
        """
        return self.db_manager.get_response_variable_summary(problem_id)

    def list_response_variables(self) -> List[str]:
        """
        List all response variables recorded in the ResponseVariables table.

        Returns:
            List[str]: A list of response variable names.
        """
        return self.db_manager.list_response_variables()  

    def get_problems_by_coefficient(self, coefficient_name: str) -> pd.DataFrame:
        """
        Retrieve all problems that use a specific coefficient.

        Args:
            coefficient_name (str): The name of the coefficient.

        Returns:
            pd.DataFrame: A DataFrame containing problem details.
        """
        return self.db_manager.get_problems_by_coefficient(coefficient_name)

    def get_coefficients_by_problem(self, problem_id: int) -> pd.DataFrame:
        """
        Retrieve all coefficients used in a specific problem.

        Args:
            problem_id (int): The ID of the problem.

        Returns:
            pd.DataFrame: A DataFrame containing coefficient details.
        """
        return self.db_manager.get_coefficients_by_problem(problem_id)
    