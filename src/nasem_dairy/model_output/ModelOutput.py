import json
import os
import re
from typing import Any, Dict, List, Union

import numpy as np
import pandas as pd


class ModelOutput:
    def __init__(self, 
                 locals_input: dict, 
                 config_path: str = "./model_output_structure.json",
                 report_config_path: str = "./report_structure.json"
    ) -> None:
        self.locals_input = locals_input
        self.dev_out = {}
        self.categories_structure = self.__load_structure(config_path)
        self.report_structure = self.__load_structure(report_config_path)

        self.__filter_locals_input()
        for name, structure in self.categories_structure.items():
            self.__populate_category(name, structure)
        self.__populate_uncategorized()

    ### Initalization ###
    def __load_structure(self, config_path: str) -> dict:
        """Load category structure from a JSON file."""
        base_path = os.path.dirname(__file__)
        full_path = os.path.join(base_path, config_path)

        if not os.path.exists(full_path):
            raise FileNotFoundError(f"The configuration file {full_path} does not exist.")
        
        with open(full_path, 'r') as file:
            try:
                return json.load(file)
            except json.JSONDecodeError as e:
                raise ValueError(f"Error decoding JSON file {full_path}: {e}")

    def __filter_locals_input(self) -> None:
        """Filter out specified variables from locals_input."""
        variables_to_remove = [
            "key", "value", "num_value", "feed_data", "feed_library_df",
            "diet_info_initial", "diet_data_initial", "AA_list",
            "An_data_initial", "mPrt_coeff_list", "mPrt_k_AA"
        ]
        for key in variables_to_remove:
            if key in self.locals_input:
                self.dev_out[key] = self.locals_input.pop(key)

    def __populate_category(self, category_name: str, group_structure: dict) -> None:
        """
        Create and populate nested dictionaries using the structure from JSON.
        """
        def recursive_populate(sub_category, sub_structure):
            for key, value in sub_structure.items():
                if isinstance(value, dict):
                    if key not in sub_category:
                        sub_category[key] = {}
                    recursive_populate(sub_category[key], value)
                    # Remove empty sub-categories
                    if not sub_category[key]:
                        del sub_category[key]
                else:
                    if key in self.locals_input:
                        sub_category[key] = self.locals_input.pop(key)
        
        if not hasattr(self, category_name):
            setattr(self, category_name, {})
        category = getattr(self, category_name)

        recursive_populate(category, group_structure)
        
        # Remove empty categories
        if not category:
            delattr(self, category_name)

    def __populate_uncategorized(self) -> None:
        """
        Store all remaining values in the Uncategorized category and pop them from locals_input.
        """
        setattr(self, 'Uncategorized', {})
        self.Uncategorized.update(self.locals_input)
        self.locals_input.clear()

    ### Display Methods ###
    def _repr_html_(self) -> str:
        #This is the HTML display when the ModelOutput object is called directly
        # in a IPython setting (e.g. juptyer notebook, VSCode interactive)
        # summary_sentence = f"Outputs for a {self.get_value('An_StatePhys')}, weighing {self.get_value('An_BW')} kg, eating {self.get_value('DMI')} kg with {self.get_value('An_LactDay')} days in milk."
        # df_diet_html = pd.DataFrame(self.get_value('user_diet')).to_html(index=False, escape=False)

        snapshot_data = self.__snapshot_data()
        # snapshot_data = [{'Description': description, 'Value': self.get_value(key)} for description, key in snapshot_vars.items()]
        df_snapshot_html = pd.DataFrame(snapshot_data).to_html(index=False,
                                                               escape=False)

        # Constructing the accordion (drop down box) for the "Access Model Outputs" section
        accordion_html = """
        <details>
            <summary><strong>Click this drop-down for ModelOutput description</strong></summary>
            <p>This is a <code>ModelOutput</code> object returned by <code>nd.execute_model()</code>.</p>
            <p>Each of the following categories can be called directly as methods, for example, if the name of my object is <code>output</code>, I would call <code>output.Production</code> to see the contents of Production.</p>
            <p>The following list shows which objects are within each category (most are dictionaries):</p>
            <ul>
        """
        skip_attrs = ['categories_structure', 'report_structure', 'locals_input', 'dev_out']
        categories = {attr: getattr(self, attr) for attr in dir(self)
                      if not attr.startswith("_") and 
                      attr not in skip_attrs and
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

        # Note: This method must return a string containing HTML, so if using in a live Jupyter environment,
        # you might want to use 'display(HTML(final_html))' instead of 'return final_html' for direct rendering.
        return final_html

    def __str__(self) -> str:
        summary = "=====================\n"
        summary += "Model Output Snapshot\n"
        summary += "=====================\n"

        lines = [
            f"{entry['Description']}: {entry['Value']}"
            for entry in self.__snapshot_data()
        ]
        summary += "\n".join(lines)
        summary += "\n\nThis is a `ModelOutput` object with methods to access all model outputs. See help(ModelOutput)."

        return summary

    def __snapshot_data(self) -> List[Dict[str, Any]]:
        """
        Return a list of dictionaries of snapshot variables for _refr_html_ and __str__
        """
        snapshot_dict = {
            'Milk production kg (Mlk_Prod_comp)':
                'Mlk_Prod_comp',
            'Milk fat g/g (MlkFat_Milk)':
                'MlkFat_Milk',
            'Milk protein g/g (MlkNP_Milk)':
                'MlkNP_Milk',
            'Milk Production - MP allowable kg (Mlk_Prod_MPalow)':
                'Mlk_Prod_MPalow',
            'Milk Production - NE allowable kg (Mlk_Prod_NEalow)':
                'Mlk_Prod_NEalow',
            'Animal ME intake Mcal/d (An_MEIn)':
                'An_MEIn',
            'Target ME use Mcal/d (Trg_MEuse)':
                'Trg_MEuse',
            'Animal MP intake g/d (An_MPIn_g)':
                'An_MPIn_g',
            'Animal MP use g/d (An_MPuse_g_Trg)':
                'An_MPuse_g_Trg',
            'Animal RDP intake g/d (An_RDPIn_g)':
                'An_RDPIn_g',
            'Diet DCAD meq (An_DCADmeq)':
                'An_DCADmeq'
        }

        snapshot_data = []
        for description, key in snapshot_dict.items():
            raw_value = self.get_value(key)
            # Check if the value is numeric
            if isinstance(raw_value, (float, int)):
                value = round(raw_value, 3)
            # elif isinstance(raw_value, (np.ndarray)) and raw_value.size == 1:
            #     # This is required for any numbers handled by np.where() that 
            #     # return arrays instead of floats - needs cleaning up
            #     value = round(float(raw_value), 3)
            else:
                value = raw_value

            snapshot_data.append({'Description': description, 'Value': value})

        return snapshot_data

    ### Data Access ### 
    def get_value(self, 
                  name: str
    ) -> Union[str, int, float, dict, pd.DataFrame, None]:
        """
        Retrieve a value, dictionary or dataframe with a given name from the ModelOutput instance.

        Parameters:
        name (str): The name of the group to retrieve.

        Returns:
        str or int or float or dict or pd.DataFrame or None: The object with the given name, or None if not found.
        """
        def recursive_search(dictionary, target_name):
            """
            Helper function to recursively search for a group in a nested dictionary
            """
            if target_name in dictionary:
                return dictionary[target_name]
            for key, value in dictionary.items():
                if isinstance(value, dict):
                    result = recursive_search(value, target_name)
                    if result is not None:
                        return result
                elif isinstance(value, pd.DataFrame):
                    if target_name in value.columns:
                        return value[target_name]
            return None

        # Search in all dictionaries contained in self except the ones listed below
        skip_attrs = ['categories_structure', 'report_structure', 'locals_input', 'dev_out']
        
        for category_name in dir(self):
            if category_name in skip_attrs:
                continue
            category = getattr(self, category_name, None)
            if category is not None:
                if isinstance(category, dict):
                    if category_name == name:
                        return category
                    result = recursive_search(category, name)
                    if result is not None:
                        return result
        return None                   

    def search(self, 
               search_string: str, 
               dictionaries_to_search: Union[None, List[str]] = None,
               case_sensitive: bool = False
    ) -> pd.DataFrame:
        
        def recursive_search(d: Dict[str, Any], path: str = '') -> None:
            for key, value in d.items():
                full_key = path + key
                if ((re.search(search_string, str(full_key), 
                               flags=user_flags)) and 
                    full_key not in visited_keys
                    ):
                    result[full_key] = value
                    visited_keys.add(full_key)
                if isinstance(value, dict):
                    recursive_search(value, full_key + '.')
                elif isinstance(value, pd.DataFrame):
                    matching_columns = [
                        col for col in value.columns
                        if re.search(search_string, col, flags=user_flags)
                    ]
                    if matching_columns:
                        columns_key = full_key + '_columns'
                        if columns_key not in visited_keys:
                            result[columns_key] = matching_columns
                            visited_keys.add(columns_key)


        def extract_dataframe_and_column(key: str, 
                                         value: Any
        ) -> Dict[str, Union[str, List[str]]]:
            '''
            Only used when key endswith('_columns')
            '''
            df_name = key.split('.')[-1].rsplit('_', 1)[0]

            return {'Name': value, 
                    "Value": "pd.Series",
                    'Category': key.split(".")[0],
                    "Level 1": df_name,
                    "Level 2": value
                    }
    

        # Define the dictionaries to search within, by default all dictionaries 
        # where outputs are stored
        if dictionaries_to_search is None:
            dictionaries_to_search = [
                'Inputs', 'Intakes', 'Requirements', 'Production', 'Excretion',
                'Digestibility', 'Efficiencies', 'Miscellaneous',
                'Uncategorized'
            ]
        result = {}
        visited_keys = set()
        table_rows = []

        user_flags = 0 if case_sensitive else re.IGNORECASE

        # Iterate over specified dictionaries
        for dictionary_name in dictionaries_to_search:
            dictionary = getattr(self, dictionary_name, None)
            if dictionary is not None and isinstance(dictionary, dict):
                recursive_search(dictionary, dictionary_name + '.')

        # Create output dataframe
        if not result:
            print(f"No matches found for '{search_string}'")
            return pd.DataFrame(
                columns=['Name', 'Value', 'Category', 'Level 1', 'Level 2']
                )

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
                    [extract_dataframe_and_column(key, col) for col in value])
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
                for index, value in enumerate(parts):
                    row[f"Level {index + 1}"] = value
                table_rows.append(row)
        output_table = pd.DataFrame(table_rows)
        output_table = (output_table
                        .fillna('')
                        .sort_values(by="Name")
                        .reset_index(drop=True))
        return output_table 

    def export_to_dict(self) -> Dict[str, Any]:
        def recursive_extract(value: Any, parent_key: str = '') -> None:
            if isinstance(value, dict):
                for k, v in value.items():
                    full_key = f"{parent_key}.{k}" if parent_key else k
                    if isinstance(v, dict):
                        recursive_extract(v, full_key)
                    else:
                        final_key = full_key.split('.')[-1]
                        data_dict[final_key] = v
                        categorize_key(final_key, v)
            elif isinstance(value, list):
                for i, item in enumerate(value):
                    full_key = f"{parent_key}[{i}]"
                    recursive_extract(item, full_key)
            else:
                final_key = parent_key.split('.')[-1]
                data_dict[final_key] = value
                categorize_key(parent_key, value)


        def categorize_key(key: str, value: Any) -> None:
            if isinstance(value, pd.DataFrame):
                special_keys['dataframe'].append(key)
            elif isinstance(value, pd.Series):
                special_keys['series'].append(key)
            elif isinstance(value, np.ndarray):
                special_keys['ndarray'].append(key)
            elif isinstance(value, dict):
                special_keys['dict'].append(key)
            elif isinstance(value, list):
                special_keys['list'].append(key)


        data_dict = {}
        special_keys = {
            'dataframe': [],
            'series': [],
            'ndarray': [],
            'dict': [],
            'list': []
        }

        skip_attrs = ['categories_structure', 'report_structure', 'locals_input', 'dev_out']
        for attr_name in dir(self):
            if attr_name.startswith('__') or attr_name in skip_attrs:
                continue

            attr = getattr(self, attr_name, None)
            if attr is not None:
                recursive_extract(attr, attr_name)

        print("DataFrame keys:", special_keys['dataframe'])
        print("Series keys:", special_keys['series'])
        print("Numpy array keys:", special_keys['ndarray'])
        print("Dict keys:", special_keys['dict'])
        print("List keys:", special_keys['list'])
        return data_dict

    ### Report Creation ###
    def get_report(self, report_name: str) -> pd.DataFrame:
        """
        Generate a report based on the report structure defined in JSON.

        Parameters:
            report_name (str): The name of the report to generate.

        Returns:
            pd.DataFrame: The generated report as a DataFrame.
        """
        if report_name not in self.report_structure:
            raise ValueError(f"Report {report_name} not found in the report structure.")

        report_config = self.report_structure[report_name]
        columns = list(report_config.keys())

        description_columns = ["Description", "Target Performance"]
        special_keys = ["Total", "Footnote"]

        data = {col_name: [] for col_name in columns if col_name not in special_keys}

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
