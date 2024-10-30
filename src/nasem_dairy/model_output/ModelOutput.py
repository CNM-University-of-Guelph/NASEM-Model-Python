"""Model output handling and reporting.

This module defines the `ModelOutput` class, which is responsible for organizing,
accessing, and reporting the results of model computations. The `ModelOutput`
class loads output structures from JSON configuration files, categorizes the
model outputs, and provides various methods for retrieving, displaying, and
exporting the model data.

Class:
    ModelOutput: Handles the organization and retrieval of model outputs.
"""

import json
import logging
import os
import re
from typing import Any, Dict, List, Union

import numpy as np
import pandas as pd

from nasem_dairy.sensitivity.response_variables_config import RESPONSE_VARIABLE_NAMES


class ModelOutput:
    def __init__(
        self, 
        locals_input: dict, 
        config_path: str = "./model_output_structure.json",
        report_config_path: str = "./report_structure.json"
    ):
        """
        Initialize ModelOutput with input data and configuration paths.

        Args:
            locals_input (dict): Dictionary of local input data.
            config_path (str): Path to the JSON file containing the model output structure.
            report_config_path (str): Path to the JSON file containing the report structure.
        """
        self.skip_attrs = ["categories_structure", "report_structure", 
                           "locals_input", "dev_out"]
        self.locals_input = locals_input
        self.dev_out = {}
        self.categories_structure = self.__load_structure(config_path)
        self.report_structure = self.__load_structure(report_config_path)
        self.__filter_locals_input()
        for name, structure in self.categories_structure.items():
            self.__populate_category(name, structure)
        self.__populate_uncategorized()
        self.categories = self.__get_category_list()

    ### Initalization ###
    def __load_structure(self, config_path: str) -> dict:
        """
        Load category structure from a JSON file.

         Args:
            config_path (str): Path to the JSON file containing the structure.

        Returns:
            dict: The structure loaded from the JSON file.

        Raises:
            FileNotFoundError: If the JSON file does not exist.
            ValueError: If there is an error decoding the JSON file.
        """
        base_path = os.path.dirname(__file__)
        full_path = os.path.join(base_path, config_path)

        if not os.path.exists(full_path):
            raise FileNotFoundError(
                f"The configuration file {full_path} does not exist."
                )
        
        with open(full_path, 'r') as file:
            try:
                return json.load(file)
            except json.JSONDecodeError as e:
                raise ValueError(f"Error decoding JSON file {full_path}: {e}")

    def __filter_locals_input(self) -> None:
        """
        Filter out specified variables from locals_input and store them in dev_out.

        This method removes certain predefined variables from the locals_input
        dictionary and stores them in the dev_out dictionary for further use.

        Variables filtered:
            - key
            - value
            - num_value
            - feed_data
            - feed_library
            - aa_list
            - mPrt_coeff_list
            - mPrt_k_AA
            - path_to_package_data
        """
        variables_to_remove = [
            "key", "value", "num_value", "feed_library", "aa_list",
            "mPrt_coeff_list", "mPrt_k_AA", "path_to_package_data"
        ]
        for key in variables_to_remove:
            if key in self.locals_input:
                self.dev_out[key] = self.locals_input.pop(key)

    def __populate_category(
        self, 
        category_name: str, 
        group_structure: dict
    ) -> None:
        """
        Create and populate nested dictionaries using the structure from JSON.

        Args:
            category_name (str): The name of the category to populate.
            group_structure (dict): The structure of the group from the JSON file.
        """
        def _recursive_populate(
            sub_category: dict, 
            sub_structure: dict
        ) -> None:
            """
            Recursively populate sub-categories based on the provided structure.

            Args:
                sub_category (dict): The sub-category dictionary to populate.
                sub_structure (dict): The structure of the sub-category from JSON.
            """
            for key, value in sub_structure.items():
                if isinstance(value, dict):
                    if key not in sub_category:
                        sub_category[key] = {}
                    _recursive_populate(sub_category[key], value)
                    # Remove empty sub-categories
                    if not sub_category[key]:
                        del sub_category[key]
                else:
                    if key in self.locals_input:
                        sub_category[key] = self.locals_input.pop(key)
        

        if not hasattr(self, category_name):
            setattr(self, category_name, {})
        category = getattr(self, category_name)

        _recursive_populate(category, group_structure)
        if not category:
            delattr(self, category_name)

    def __populate_uncategorized(self) -> None:
        """
        Store all remaining values in the Uncategorized category and clear locals_input.

        This method moves all remaining key-value pairs from the locals_input
        dictionary to a new Uncategorized dictionary, then clears locals_input.
        """
        setattr(self, 'Uncategorized', {})
        self.Uncategorized.update(self.locals_input)
        self.locals_input.clear()

    def __get_category_list(self) -> List[str]:
        """
        Returns a list of category names.

        This method iterates over all attributes of the class instance, filtering out
        special attributes (those starting with '__') and any attributes listed in
        skip_attrs. It then checks if the attribute is a dictionary and includes it
        in the returned list.

        Returns:
            List[str]: A list of category names.
        """
        return [
            attr_name for attr_name in dir(self)
            if not attr_name.startswith("__")
            and attr_name not in self.skip_attrs
            and isinstance(getattr(self, attr_name, None), dict)
        ]

    ### Display Methods ###
    def _repr_html_(self) -> str:
        """
        Generate an HTML representation of the ModelOutput object for IPython.

        This method is called when the ModelOutput object is displayed directly
        in an IPython setting (e.g., Jupyter notebook, VSCode interactive).

        Returns:
            str: An HTML string representing the ModelOutput object.
        """
        # Generate snapshot of data and convert to HTML
        snapshot_data = self.__snapshot_data()
        df_snapshot_html = pd.DataFrame(snapshot_data).to_html(index=False,
                                                               escape=False)

        # Constructing the accordion (drop down box) for the "Access Model Outputs" section
        accordion_html = """
        <details>
            <summary><strong>Click this drop-down for ModelOutput description</strong></summary>
            <p>This is a <code>ModelOutput</code> object returned by <code>nd.nasem()</code>.</p>
            <p>Each of the following categories can be called directly as methods, for example, if the name of my object is <code>output</code>, I would call <code>output.Production</code> to see the contents of Production.</p>
            <p>The following list shows which objects are within each category (most are dictionaries):</p>
            <ul>
        """
        categories = {attr: getattr(self, attr) for attr in dir(self)
                      if not attr.startswith("_") and 
                      attr not in self.skip_attrs and
                      isinstance(getattr(self, attr), dict)}

        # Adding categories and keys to the accordion content as bullet points
        for category, keys in categories.items():
            accordion_html += f"<li><b>{category}:</b> {', '.join(keys.keys())}</li>"

        accordion_html += """
            </ul>
            <div>
                <p>There is a <code>.search()</code> method which takes a string and will return a dataframe of all outputs with that string (default is not case-sensitive), e.g., <code>output.search('Mlk', case_sensitive=False)</code>.</p>
                <p>The Path that is returned by the <code>.search()</code> method can be used to access the parent object of the value in that row. 
                For example, the Path for <code>Mlk_Fat_g</code> is <code>Production['milk']</code> which means that calling 
                <code>output.Production['milk']</code> would show the dict that contains <code>Mlk_Fat_g</code>.</p>
                <p>However, the safest way to retrieve an individual output is to do so directly by providing its exact name to the <code>.get_value()</code> method, e.g., <code>output.get_value('Mlk_Fat_g')</code>.</p>
            </div>
        </details>
        """

        # Combining everything into the final HTML
        final_html = f"""
        <div>
            <h2>Model Output Snapshot</h2>
            {df_snapshot_html}
            <hr>
            {accordion_html}
        </div>
        """

        # NOTE: This method must return a string containing HTML, so if using in
        # a live Jupyter environment, you might want to use 'display(HTML(final_html))' 
        # instead of 'return final_html' for direct rendering.
        return final_html

    def __str__(self) -> str:
        """
        Generate a string representation of the ModelOutput object.

        This method provides a summary of the model outputs, which includes
        descriptions and values of the snapshot data.

        Returns:
            str: A string representation of the ModelOutput object.
        """
        summary = (
            "=====================\n"
            "Model Output Snapshot\n"
            "=====================\n"
        )
        lines = [
            f"{entry['Description']}: {entry['Value']}"
            for entry in self.__snapshot_data()
        ]
        summary += "\n".join(lines)
        summary += (
            "\n\nThis is a `ModelOutput` object with methods to access all model"
            " outputs. See help(ModelOutput)."
        )
        return summary

    def __snapshot_data(self) -> List[Dict[str, Any]]:
        """
        Return a list of dictionaries of snapshot variables for _repr_html_ and __str__.

        This method retrieves specific model output values, formats them, and
        returns them as a list of dictionaries with descriptions.

        Returns:
            List[Dict[str, Any]]: A list of dictionaries containing snapshot
            descriptions and their corresponding values.
        """
        snapshot_dict = {
            'Milk production kg (Mlk_Prod_comp)': 'Mlk_Prod_comp',
            'Milk fat g/g (MlkFat_Milk)': 'MlkFat_Milk',
            'Milk protein g/g (MlkNP_Milk)': 'MlkNP_Milk',
            'Milk Production - MP allowable kg (Mlk_Prod_MPalow)': 'Mlk_Prod_MPalow',
            'Milk Production - NE allowable kg (Mlk_Prod_NEalow)': 'Mlk_Prod_NEalow',
            'Animal ME intake Mcal/d (An_MEIn)': 'An_MEIn',
            'Target ME use Mcal/d (Trg_MEuse)': 'Trg_MEuse',
            'Animal MP intake g/d (An_MPIn_g)': 'An_MPIn_g',
            'Animal MP use g/d (An_MPuse_g_Trg)': 'An_MPuse_g_Trg',
            'Animal RDP intake g/d (An_RDPIn_g)': 'An_RDPIn_g',
            'Diet DCAD meq (An_DCADmeq)': 'An_DCADmeq'
        }
        snapshot_data = []
        for description, key in snapshot_dict.items():
            value = self.get_value(key)
            if isinstance(value, (float, int)):
                value = round(value, 3)
            snapshot_data.append({'Description': description, 'Value': value})
        return snapshot_data

    ### Data Access ### 
    def get_value(
        self, 
        name: str
    ) -> Union[str, int, float, dict, pd.DataFrame, None]:
        """
        Retrieve a value, dictionary, or dataframe with a given name.

        This method searches through the ModelOutput instance to find a specific
        value, dictionary, or dataframe by name.

        Args:
            name (str): The name of the group to retrieve.

        Returns:
            Union[str, int, float, dict, pd.DataFrame, None]: The object with the
            given name, or None if not found.
        """
        def _recursive_search_get_value(
            dictionary: dict, 
            target_name: str
        ) -> Union[Any, None]:
            """
            Recursively search for a group in a nested dictionary.

            Args:
                dictionary (dict): The dictionary to search within.
                target_name (str): The name of the target group.

            Returns:
                Union[Any, None]: The found object or None if not found.
            """
            if target_name in dictionary:
                return dictionary[target_name]
            for key, value in dictionary.items():
                if isinstance(value, dict):
                    result = _recursive_search_get_value(value, target_name)
                    if result is not None:
                        return result
                elif isinstance(value, pd.DataFrame):
                    if target_name in value.columns:
                        return value[target_name]
            return None

        
        for category_name in self.categories:
            if category_name == name:
                return getattr(self, category_name)
            result = _recursive_search_get_value(
                getattr(self, category_name), name
                )
            if result is not None:
                return result
        return None                   

    def search(
        self, 
        search_string: str, 
        dictionaries_to_search: Union[None, List[str]] = None,
        case_sensitive: bool = False
    ) -> pd.DataFrame:
        """
        Search for a string in the ModelOutput instance and return matching results.

        This method searches for a given string within the specified dictionaries
        in the ModelOutput instance and returns the matching results in a DataFrame.

        Args:
            search_string (str): The string to search for.
            dictionaries_to_search (Union[None, List[str]]): The list of dictionaries
                to search within. If None, all relevant dictionaries are searched.
            case_sensitive (bool): Whether the search should be case-sensitive.
                Default is False.

        Returns:
            pd.DataFrame: A DataFrame containing the search results.
        """
        def _recursive_search_search(
            dict_to_search: Dict[str, Any], 
            path: str = ""
        ) -> None:
            """
            Recursively search for a string in a nested dictionary.

            Args:
                dict_to_search (Dict[str, Any]): The dictionary to search within.
                path (str): The current search path.
            """
            for key, value in dict_to_search.items():
                full_key = path + key
                if ((re.search(search_string, str(full_key), 
                               flags=user_flags)) and 
                    full_key not in visited_keys
                    ):
                    result[full_key] = value
                    visited_keys.add(full_key)
                if isinstance(value, dict):
                    _recursive_search_search(value, full_key + ".")
                elif isinstance(value, pd.DataFrame):
                    matching_columns = [
                        col for col in value.columns
                        if re.search(search_string, col, flags=user_flags)
                    ]
                    if matching_columns:
                        columns_key = full_key + "_columns"
                        if columns_key not in visited_keys:
                            result[columns_key] = matching_columns
                            visited_keys.add(columns_key)


        def _extract_dataframe_and_column(
            key: str, 
            value: Any
        ) -> Dict[str, Union[str, List[str]]]:
            """
            Extract information from a DataFrame column.

            Args:
                key (str): The key of the DataFrame.
                value (Any): The value associated with the key.

            Returns:
                Dict[str, Union[str, List[str]]]: A dictionary containing
                information about the DataFrame column.
            """
            df_name = key.split(".")[-1].rsplit("_", 1)[0]
            return {'Name': value, 
                    "Value": "pd.Series",
                    'Category': key.split(".")[0],
                    "Level 1": df_name,
                    "Level 2": value
                    }
    

        def _create_output_dataframe(result: dict) -> pd.DataFrame:
            """
            Create a DataFrame from the search result.

            Args:
                result (dict): The dictionary containing search results.

            Returns:
                pd.DataFrame: A DataFrame containing the search results.
            """
            table_rows = []
            for key, value in result.items():
                variable_name = key.split('.')[-1]
                parts = key.split('.')
                
                category = parts.pop(0)
                
                if isinstance(value, dict):
                    value_display = 'Dictionary'
                elif isinstance(value, pd.DataFrame):
                    value_display = 'DataFrame'
                elif isinstance(value, list) and key.endswith('_columns'):
                    table_rows.extend(
                        [_extract_dataframe_and_column(key, col) for col in value])
                elif isinstance(value, list):
                    value_display = 'List'
                else:
                    value_display = value
                # Add the current row to the list
                if not (isinstance(value, list) and key.endswith('_columns')):
                    row = {
                        'Name': variable_name,
                        'Value': value_display,
                        'Category': category
                    }
                    for index, part in enumerate(parts):
                        row[f"Level {index + 1}"] = part
                    table_rows.append(row)
            output_table = pd.DataFrame(table_rows)
            output_table = (output_table
                            .fillna('')
                            .sort_values(by="Name")
                            .reset_index(drop=True))
            return output_table


        if dictionaries_to_search is None:
            dictionaries_to_search = self.categories
            
        result = {}
        visited_keys = set()
        user_flags = 0 if case_sensitive else re.IGNORECASE

        for dictionary_name in dictionaries_to_search:
            dictionary = getattr(self, dictionary_name, None)
            if dictionary is not None and isinstance(dictionary, dict):
                _recursive_search_search(dictionary, dictionary_name + '.')

        if not result:
            print(f"No matches found for '{search_string}'")
            return pd.DataFrame(
                columns=['Name', 'Value', 'Category', 'Level 1', 'Level 2']
                )
        return _create_output_dataframe(result)

    def export_to_dict(self) -> Dict[str, Any]:
        """
        Export the ModelOutput instance to a dictionary.

        This method extracts all values from the ModelOutput instance and organizes
        them into a dictionary.

        Returns:
            Dict[str, Any]: A dictionary containing all the values from the
            ModelOutput instance.
        """
        def _recursive_extract(value: Any, parent_key: str = "") -> None:
            """
            Recursively extract values from a nested structure.

            Args:
                value (Any): The value to extract from.
                parent_key (str): The parent key for the current value.
            """
            if isinstance(value, dict):
                for key, value in value.items():
                    full_key = f"{parent_key}.{key}" if parent_key else key
                    if isinstance(value, dict):
                        _recursive_extract(value, full_key)
                    else:
                        final_key = full_key.split(".")[-1]
                        data_dict[final_key] = value
                        _categorize_key(final_key, value)


        def _categorize_key(key: str, value: Any) -> None:
            """
            Categorize the key based on the value type.

            Args:
                key (str): The key to categorize.
                value (Any): The value associated with the key.
            """
            if isinstance(value, pd.DataFrame):
                special_keys["dataframe"].append(key)
            elif isinstance(value, pd.Series):
                special_keys["series"].append(key)
            elif isinstance(value, np.ndarray):
                special_keys["ndarray"].append(key)
            elif isinstance(value, list):
                special_keys["list"].append(key)


        data_dict = {}
        special_keys = {
            "dataframe": [],
            "series": [],
            "ndarray": [],
            "list": []
        }
        for attr_name in self.categories:
            _recursive_extract(getattr(self, attr_name), attr_name)

        # print("DataFrame keys:", special_keys["dataframe"])
        # print("Series keys:", special_keys["series"])
        # print("Numpy array keys:", special_keys["ndarray"])
        # print("List keys:", special_keys["list"])
        return data_dict

    def export_variable_names(self) -> List[str]: 
        """
        Extract a list of variable names stored in the class.
        If a value is a DataFrame, replace the DataFrame name with its column names.

        Returns:
            List[str]: A list of variable names including DataFrame column names.
        """
        variables_dict = self.export_to_dict()
        variable_names = []

        for key, value in variables_dict.items():
            if isinstance(value, pd.DataFrame):
                variable_names.extend(value.columns.tolist())
            else:
                variable_names.append(key)
        return list(set(variable_names))

    def export_to_JSON(self, file_path: str):
        """
        Export the entire ModelOutput instance to a JSON file.

        Args:
            file_path (str): The path where the JSON file will be saved.
        """
        output_dict = self.export_to_dict()
        with open(file_path, 'w') as json_file:
            json.dump(output_dict, json_file, indent=4, cls=CustomJSONEncoder)

    def to_response_variables(self) -> List[Dict[str, Any]]:
        """
        Convert the ModelOutput instance into a list of response variables suitable for database storage.

        Returns:
            List[Dict[str, Any]]: A list of dictionaries containing 'variable_name' and 'value' keys.
        """
        data_dict = self.export_to_dict()
        response_variables = {}
        for name in RESPONSE_VARIABLE_NAMES:
            response_variables[name] = (data_dict.get(name))
        return response_variables

    ### Report Creation ###
    def get_report(self, report_name: str) -> pd.DataFrame:
        """
        Generate a report based on the report structure defined in JSON.

        Args:
            report_name (str): The name of the report to generate.

        Returns:
            pd.DataFrame: The generated report as a DataFrame.

        Raises:
            ValueError: If the report name is not found in the report structure.
        """
        if report_name not in self.report_structure:
            raise ValueError(
                f"Report {report_name} not found in the report structure."
                )

        report_config = self.report_structure[report_name]
        columns = list(report_config.keys())

        description_columns = ["Description", "Target Performance"]
        special_keys = ["Total", "Footnote"]

        data = {col_name: [] for col_name in columns 
                if col_name not in special_keys}

        for col_name, variables in report_config.items():
            if col_name in special_keys:
                continue
            if col_name in description_columns:
                data[col_name].extend(variables)
                continue
            for variable_name in variables:
                if isinstance(variable_name, (int, float)):
                    data[col_name].append(variable_name)
                    continue

                value = self.get_value(variable_name)
                if isinstance(value, (pd.Series, np.ndarray)):
                    data[col_name].extend(value.tolist())
                elif value is not None:
                    data[col_name].append(value)
                else:
                    data[col_name].append("")

        report_df = pd.DataFrame(data)     

        if "Total" in report_config:
            total_row = ["Total"] + [self.get_value(value) 
                                     for value in report_config["Total"] 
                                     if value != "Total"] 
            report_df.loc[len(report_df)] = total_row
            
        # NOTE This works to include footnotes in the table but it's very ugly.
        # Dataframes aren't really meant to display long strings like this so
        # they end up getting cut off. I can't find anything about including footnotes
        # with a Dataframe. I think it's important to include this info but there 
        # may be a better way to format it. Maybe we edit the footnotes to be shorter?
        # - Braeden
        if "Footnote" in report_config:
            footnotes = report_config["Footnote"]
            for key, footnote in footnotes.items():
                # Adjust length of footnote row based on size of Dataframe
                footnote_row = [key, footnote] + [""]*(len(report_df.columns)-2)
                report_df.loc[len(report_df)] = footnote_row
        return report_df


class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, (np.integer, np.int_, np.intc, np.intp, 
                              np.int8, np.int16, np.int32, np.int64)):
            return int(obj)
        elif isinstance(obj, (np.floating, np.float_, np.float16, 
                              np.float32, np.float64)):
            return float(obj)
        elif isinstance(obj, (np.bool_, bool)):
            return bool(obj)
        elif isinstance(obj, np.dtype):
            return str(obj)
        elif isinstance(obj, pd.DataFrame):
            return obj.to_dict(orient='records')
        elif isinstance(obj, pd.Series):
            return obj.to_dict()
        elif isinstance(obj, pd.Timestamp):
            return obj.isoformat()
        elif isinstance(obj, pd.Timedelta):
            return str(obj)
        elif isinstance(obj, complex):
            return {'real': obj.real, 'imag': obj.imag}
        elif isinstance(obj, (bytes, bytearray)):
            return obj.decode('utf-8', errors='replace')
        elif isinstance(obj, set):
            return list(obj)
        elif hasattr(obj, '__dict__'):
            return self.default(vars(obj))
        elif callable(obj):
            return None  
        else:
            logging.warning(f"Encountered non-serializable object of type {type(obj)}: {repr(obj)}")
            return str(obj)
        