import os
from typing import Dict, Tuple, Union, List

import numpy as np
import pandas as pd
import SALib.sample.saltelli as saltelli
import SALib.analyze.sobol as sobol

from nasem_dairy.model.nasem import nasem
from nasem_dairy.data.constants import coeff_dict
import nasem_dairy.model.input_validation as input_validation
import nasem_dairy.model.utility as utility
from nasem_dairy.sensitivity.DatabaseManager import DatabaseManager

class SensitivityAnalyzer:
    """Class for running sensitivity analysis of NASEM model to the coefficients in coeff_dict.
    """
    def __init__(self, db_path: str):
        self.db_manager = DatabaseManager(db_path)

    def _validate_value_ranges(self, value_ranges, coeffs):
        df = pd.DataFrame.from_dict(
            value_ranges, orient='index', columns=['min', 'max']
            )

        missing_keys = set(df.index) - set(coeffs)
        if missing_keys:
            raise ValueError(f"Keys not found in coefficients: {list(missing_keys)}")

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
    ) -> Dict:
        return {
            "num_vars": len(value_ranges.keys()),
            "names": list(value_ranges.keys()),
            "bounds": [val for val in value_ranges.values()]
        }

    def update_coeff_dict(self, param_array, coeff_dict, coeff_names):
        modified_coeff_dict = coeff_dict.copy()
        for name, value in zip(param_array, coeff_names):
            modified_coeff_dict[name] = value
        return modified_coeff_dict

    def load_input(self, input_path):
        file_extension = os.path.splitext(input_path)[-1].lower()

        if file_extension == '.csv':
            return utility.read_csv_input(input_path)
        elif file_extension == '.json':
            return utility.read_json_input(input_path)
        else:
            raise ValueError(f"Unsupported file type: {file_extension}. Only CSV and JSON are supported.")

    def _save_full_model_output_JSON(self, problem_id: int, sample_index: int, model_output):
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
        param_values, 
        coeff_dict, 
        coeff_names, 
        input_path, 
        problem,
        save_full_output
    ):
        user_diet, animal_input, equation_selection, infusion_input = self.load_input(
            input_path
            )

        # Store the problem information in the Problems table
        problem_id = self.db_manager.insert_problem(
            filename=os.path.basename(input_path),
            user_diet=user_diet,
            animal_input=animal_input,
            equation_selection=equation_selection,
            infusion_input=infusion_input,
            problem=problem
        )

        for index, param_array in enumerate(param_values):
            modified_coeff_dict = self.update_coeff_dict(
                param_array, coeff_dict, coeff_names
            )

            model_output = nasem(
                user_diet, animal_input, equation_selection, 
                infusion_input=infusion_input, coeff_dict=modified_coeff_dict
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
        user_coeff_dict: Dict[str, Union[int, float]] = coeff_dict,
        calc_second_order: bool = True,
        save_full_output: bool = False
    ):
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
            input_path, problem, save_full_output
            )
        print(
            "Sensitivity Analysis is complete! "
            f"Results are stored as problem_id: {problem_id}"
            )
        
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

    def get_response_variables(self, problem_id: int, variable_names: List[str]) -> pd.DataFrame:
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
    