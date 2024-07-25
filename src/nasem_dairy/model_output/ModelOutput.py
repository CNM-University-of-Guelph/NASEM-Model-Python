import json
import os
import re
from typing import Any, Dict, List, Union

import numpy as np
import pandas as pd


class ModelOutput:
    def __init__(self, 
                 locals_input: dict, 
                 config_path: str = "./model_output_structure.json"
    ) -> None:
        self.locals_input = locals_input
        self.dev_out = {}
        self.categories_structure = self.__load_category_structure(config_path)

        self.__filter_locals_input()
        for name, structure in self.categories_structure.items():
            self.__populate_category(name, structure)
        self.__populate_uncategorized()
        # NOTE We shouldn't be calculating values inside of ModelOutput. Either
        # add values to the end of execute_model() and store them or calculate 
        # these dynamically when they are needed using get_value() 
        self.__calculate_additional_variables()

    ### Initalization ###
    def __load_category_structure(self, config_path: str) -> dict:
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
            "key", "value", "num_value", "feed_library_df", "feed_data",
            "diet_info_initial", "diet_data_initial", "AA_list",
            "An_data_initial", "mPrt_coeff_list", "mPrt_k_AA"
        ]
        for key in variables_to_remove:
            if key in self.locals_input:
                self.dev_out[key] = self.locals_input.pop(key)

    def __populate_category(self, category_name: str, group_structure: dict) -> None:
        """Create and populate nested dictionaries using the structure from JSON."""
        if not hasattr(self, category_name):
            setattr(self, category_name, {})
        category = getattr(self, category_name)

        for key, value in group_structure.items():
            if isinstance(value, dict):
                if key not in category:
                    category[key] = {}
                for sub_key in value:
                    if sub_key in self.locals_input:
                        category[key][sub_key] = self.locals_input.pop(sub_key)
                # Remove empty sub-categories
                if not category[key]:
                    del category[key]
            else:
                if key in self.locals_input:
                    category[key] = self.locals_input.pop(key)
        
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

    def __calculate_additional_variables(self) -> None:
        """
        This method calculates additional values that are useful for reporting but not used by model.
        E.g. Some values are normally reported with different units to what are calculated.

        This will add all to Miscellaneous category under 'post_execute_calcs'
        """
        getattr(self, 'Miscellaneous')['post_execute_calcs'] = {}
                
        new_var = {
            'An_MPuse_kg_Trg': self.get_value('An_MPuse_g_Trg') / 1000,
            'Dt_ForNDFIn_percNDF': (self.get_value('Dt_ForNDFIn') / 
                                    self.get_value('Dt_NDFIn') * 100),
        }

        for key, value in new_var.items():
            getattr(self, 'Miscellaneous')['post_execute_calcs'][key] = value

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

        categories = self.__categories_dict()
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

    def __categories_dict(self) -> Dict[str, Any]:
        """
        Return dictionary of categories from this object for _refr_html_ and __str__
        """
        categories_dict = {
            'Inputs': self.Inputs,
            'Intakes': self.Intakes,
            'Requirements': self.Requirements,
            'Production': self.Production,
            'Excretion': self.Excretion,
            'Digestibility': self.Digestibility,
            'Efficiencies': self.Efficiencies,
            'Miscellaneous': self.Miscellaneous
        }
        return categories_dict

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
            return None

        # Search in all dictionaries contained in self
        for category_name in dir(self):
            category = getattr(self, category_name, None)
            if category is not None:
                if (isinstance(category, dict) and 
                    category_name == name
                    ):
                    return category
                elif (isinstance(category, pd.DataFrame) and 
                      category_name == name
                      ):
                    return category
                elif isinstance(category, dict):
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

        for attr_name in dir(self):
            attr = getattr(self, attr_name, None)
            if attr is not None and not attr_name.startswith('__'):
                recursive_extract(attr, attr_name)

        print("DataFrame keys:", special_keys['dataframe'])
        print("Series keys:", special_keys['series'])
        print("Numpy array keys:", special_keys['ndarray'])
        print("Dict keys:", special_keys['dict'])
        print("List keys:", special_keys['list'])
        return data_dict

    ### Report Creation ###
    def report_minerals(self) -> Dict[str, pd.DataFrame]:
        '''
        Format mineral data with inputs, requirements and balance. 
        Similar to tables 7_1 and 7_2 in R.
        '''       
        def get_mineral_values(keys: List[str]) -> List[Any]:
            return [self.get_value(key) for key in keys]


        # Table 7_1 in R
        keys_list_macro = {
            'Ca': ['Dt_Ca', 'Dt_CaReq_DMI', 'Dt_acCa', 'An_Ca_req', 'Dt_CaIn', 
                   'Abs_CaIn', 'An_Ca_bal', 'Fe_Ca_m', None, 'An_Ca_y', 
                   'An_Ca_l', 'An_Ca_g'],
            'P': ['Dt_P', 'Dt_PReq_DMI', 'Dt_acP', 'An_P_req', 'Dt_PIn', 
                  'Abs_PIn', 'An_P_bal', 'Fe_P_m', 'Ur_P_m', 'An_P_y', 
                  'An_P_l', 'An_P_g'],
            'Mg': ['Dt_Mg', 'Dt_MgReq_DMI', 'Dt_acMg', 'An_Mg_req', 'Dt_MgIn', 
                   'Abs_MgIn', 'An_Mg_bal', 'Fe_Mg_m', 'Ur_Mg_m', 'An_Mg_y', 
                   'An_Mg_l', 'An_Mg_g'],
            'Cl': ['Dt_Cl', 'Dt_ClReq_DMI', 'Dt_acCl', 'An_Cl_req', 'Dt_ClIn', 
                   'Abs_ClIn', 'An_Cl_bal', 'Fe_Cl_m', None, 'An_Cl_y', 
                   'An_Cl_l', 'An_Cl_g'],
            'K': ['Dt_K', 'Dt_KReq_DMI', 'Dt_acK', 'An_K_req', 'Dt_KIn', 
                  'Abs_KIn', 'An_K_bal', 'Fe_K_m', 'Ur_K_m', 'An_K_y', 
                  'An_K_l', 'An_K_g'],
            'Na': ['Dt_Na', 'Dt_NaReq_DMI', 'Dt_acNa', 'An_Na_req', 'Dt_NaIn', 
                   'Abs_NaIn', 'An_Na_bal', 'Fe_Na_m', None, 'An_Na_y', 
                   'An_Na_l', 'An_Na_g'],
            'S': ['Dt_S', 'Dt_SReq_DMI', None, 'An_S_req', 'Dt_SIn', None, 
                  'An_S_bal', None, None, None, None, None]
        }

        # Table 7_2 in R
        keys_list_micro = {
            'Co': ['Dt_Co', 'Dt_CoReq_DMI', 'Dt_acCo', 'An_Co_req', 'Dt_CoIn', 
                   'Abs_CoIn', 'An_Co_bal', None, None, None, None],
            'Cr': ['Dt_Cr', None, None, None, 'Dt_CrIn', None, None, None, 
                   None, None, None],
            'Cu': ['Dt_Cu', 'Dt_CuReq_DMI', 'Dt_acCu', 'An_Cu_req', 'Dt_CuIn', 
                   'Abs_CuIn', 'An_Cu_bal', 'An_Cu_m', 'An_Cu_y', 'An_Cu_l', 
                   'An_Cu_g'],
            'Fe': ['Dt_Fe', 'Dt_FeReq_DMI', 'Dt_acFe', 'An_Fe_req', 'Dt_FeIn', 
                   'Abs_FeIn', 'An_Fe_bal', 'An_Fe_m', 'An_Fe_y', 'An_Fe_l', 
                   'An_Fe_g'],
            'I': ['Dt_I', 'Dt_IReq_DMI', None, 'An_I_req', 'Dt_IIn', None, 
                  'An_I_bal', None, None, None, None],
            'Mn': ['Dt_Mn', 'Dt_MnReq_DMI', 'Dt_acMn', 'An_Mn_req', 'Dt_MnIn', 
                   'Abs_MnIn', 'An_Mn_bal', 'An_Mn_m', 'An_Mn_y', 'An_Mn_l', 
                   'An_Mn_g'],
            'Se': ['Dt_Se', 'Dt_SeReq_DMI', None, 'An_Se_req', 'Dt_SeIn', None, 
                   'An_Se_bal', None, None, None, None],
            'Zn': ['Dt_Zn', 'Dt_ZnReq_DMI', 'Dt_acZn', 'An_Zn_req', 'Dt_ZnIn', 
                   'Abs_ZnIn', 'An_Zn_bal', 'An_Zn_m', 'An_Zn_y', 'An_Zn_l', 
                   'An_Zn_g']
        }
        
        macro_data = {mineral: get_mineral_values(keys) 
                       for mineral, keys in keys_list_macro.items()}

        micro_data = {mineral: get_mineral_values(keys) 
                       for mineral, keys in keys_list_micro.items()}

        index_macro = ["Diet Density, % DM", "Required Diet Density, % of DM", "AC, g/100 g", 
                     "Absorb Required (TAR), g/d", "Diet Supply (TDS), g/d", "Absorbed Supply (TAS), g/d", 
                     "Balance (TAS - TAR), g/d", "Met. Fecal, g/d", "End. Urine g/d", 
                     "Pregn. Req., g/d", "Lact. Req., g/d", "Growth Req., g/d"]

        index_micro = ["Diet, mg/kg", "Diet Required, mg/kg", "AC", 
                     "Absorb Requir., mg/d", "Intake, mg/d", "Absorbed, mg/d", 
                     "Balance, mg/d", "Maintenance, mg/d", "Pregn. Req., mg/d", 
                     "Lact. Req., mg/d", "Growth Req., mg/d"]

        macro_minerals = pd.DataFrame(macro_data, index=index_macro).T
        micro_minerals = pd.DataFrame(micro_data, index=index_micro).T

        return {'macro_minerals': macro_minerals.reset_index(names = 'Mineral'), 
                'micro_minerals': micro_minerals.reset_index(names = 'Mineral')}

    def report_animal_characteristics(self) -> pd.DataFrame:
        '''
        Format animal characteristic data into a table.
        Similar to table Tbl1_1 in R.
        '''
        data = {
            'Animal Type': self.get_value('An_StatePhys'),
            'Animal Breed': self.get_value('An_Breed'),
            'Body Weight, kg': self.get_value('An_BW'),
            'Empty BW, kg': self.get_value('An_BW_empty'),
            'Birth Weight, kg': self.get_value('Fet_BWbrth'),
            'Mature Weight, kg': self.get_value('An_BW_mature'),
            'Mature Empty BW, kg': self.get_value('An_BWmature_empty'),
            'Age, d': self.get_value('An_AgeDay'),
            'Condition Score, 1 to 5': self.get_value('An_BCS'),
            'Percent First Parity': (2 - self.get_value('An_Parity_rl')) * 100,
            'Days in Milk': self.get_value('An_LactDay'),
            # 'Age At First Calving, d': self.get_value('An_AgeConcept1st') + 280,
            'Days Pregnant': self.get_value('An_GestDay'),
            'Temperature, C': self.get_value('Env_TempCurr'),
            'Use In vitro NDF digest': self.get_value('Use_DNDF_IV'),
            'Feeding Monensin, 0=No, 1=Yes': self.get_value('Monensin_eqn'),
            'Grazing': self.get_value('An_Grazing'),
            'Topography': self.get_value('Env_Topo'),
            'Dist. (Pasture to Parlor, m)': self.get_value('Env_DistParlor'),
            'One-Way Trips to the Parlor, m': self.get_value('Env_TripsParlor')
        }

        # Create DataFrame
        animal_characteristics = pd.DataFrame(data, index=[0])
        
        # Transpose the DataFrame
        animal_characteristics = animal_characteristics.T
        
        # Optionally, rename the index if required
        animal_characteristics.columns = ['Value']
        
        return animal_characteristics

    def report_target_performance(self) -> pd.DataFrame:
        '''
        Format target performance data into a table.
        Similar to table Tbl1_2 in R.
        '''
        # Collecting values and calculating necessary operations
        data = {
            'Milk Production': self.get_value('Trg_MilkProd'),
            'Energy/Protein Corrected Milk, kg/d': self.get_value('Trg_MilkProd_EPcor'),
            'Milk Fat, %': self.get_value('Trg_MilkFatp'),
            'Milk True Protein': self.get_value('Trg_MilkTPp'),
            'Milk Lactose, %': self.get_value('Trg_MilkLacp'),
            'Milk Fat, kg/d': self.get_value('Trg_Mlk_Fat'),
            'Milk True Protein, kg/d': self.get_value('Trg_Mlk_NP'),
            'Milk Lactose, kg/d': self.get_value('Trg_MilkProd') * self.get_value('Trg_MilkLacp') / 100,
            'Frame Gain, kg/d': self.get_value('Trg_FrmGain'),
            'Body Reserves Gain, kg/d': self.get_value('Trg_RsrvGain'),
            'Gravid Uterine Gain, kg/d': self.get_value('GrUter_BWgain'),
            'Total Gain, kg/d': self.get_value('An_BodConcgain')
        }

        # Create DataFrame
        target_performance = pd.DataFrame(data, index=[0])
        
        # Transpose the DataFrame
        target_performance = target_performance.T
        
        # Rename the column for clarity
        target_performance.columns = ['Target Performance:']
        
        return target_performance

    # def report_AA(self):
    #     def create_aa_flows_dataframe(self):
    #                 # Data for Tbl6_4
    #         data = {
    #             'Arg': [self.get_value('Ur_ArgEnd_g'), self.get_value('Fe_ArgMet_g'), self.get_value('Scrf_Arg_g'), 
    #                     self.get_value('Gest_Arg_g'), self.get_value('Body_ArgGain_g'), self.get_value('Mlk_Arg_g'), 
    #                     self.get_value('Trg_Mlk_Arg_g'), self.get_value('An_ArgUse_g'), self.get_value('Trg_ArgUse_g'), None, 
    #                     self.get_value('AnNPxArg_AbsArg'), self.get_value('AnNPxArgUser_AbsArg')],
    #             'His': [self.get_value('Ur_HisEnd_g'), self.get_value('Fe_HisMet_g'), self.get_value('Scrf_His_g'), 
    #                     self.get_value('Gest_His_g'), self.get_value('Body_HisGain_g'), self.get_value('Mlk_His_g'), 
    #                     self.get_value('Trg_Mlk_His_g'), self.get_value('An_HisUse_g'), self.get_value('Trg_HisUse_g'), 
    #                     self.get_value('Trg_AbsHis_NPxprtHis'), self.get_value('AnNPxHis_AbsHis'), self.get_value('AnNPxHisUser_AbsHis')],
    #             'Ile': [self.get_value('Ur_IleEnd_g'), self.get_value('Fe_IleMet_g'), self.get_value('Scrf_Ile_g'), 
    #                     self.get_value('Gest_Ile_g'), self.get_value('Body_IleGain_g'), self.get_value('Mlk_Ile_g'), 
    #                     self.get_value('Trg_Mlk_Ile_g'), self.get_value('An_IleUse_g'), self.get_value('Trg_IleUse_g'), 
    #                     self.get_value('Trg_AbsIle_NPxprtIle'), self.get_value('AnNPxIle_AbsIle'), self.get_value('AnNPxIleUser_AbsIle')],
    #             'Leu': [self.get_value('Ur_LeuEnd_g'), self.get_value('Fe_LeuMet_g'), self.get_value('Scrf_Leu_g'), 
    #                     self.get_value('Gest_Leu_g'), self.get_value('Body_LeuGain_g'), self.get_value('Mlk_Leu_g'), 
    #                     self.get_value('Trg_Mlk_Leu_g'), self.get_value('An_LeuUse_g'), self.get_value('Trg_LeuUse_g'), 
    #                     self.get_value('Trg_AbsLeu_NPxprtLeu'), self.get_value('AnNPxLeu_AbsLeu'), self.get_value('AnNPxLeuUser_AbsLeu')],
    #             'Lys': [self.get_value('Ur_LysEnd_g'), self.get_value('Fe_LysMet_g'), self.get_value('Scrf_Lys_g'), 
    #                     self.get_value('Gest_Lys_g'), self.get_value('Body_LysGain_g'), self.get_value('Mlk_Lys_g'), 
    #                     self.get_value('Trg_Mlk_Lys_g'), self.get_value('An_LysUse_g'), self.get_value('Trg_LysUse_g'), 
    #                     self.get_value('Trg_AbsLys_NPxprtLys'), self.get_value('AnNPxLys_AbsLys'), self.get_value('AnNPxLysUser_AbsLys')],
    #             'Met': [self.get_value('Ur_MetEnd_g'), self.get_value('Fe_MetMet_g'), self.get_value('Scrf_Met_g'), 
    #                     self.get_value('Gest_Met_g'), self.get_value('Body_MetGain_g'), self.get_value('Mlk_Met_g'), 
    #                     self.get_value('Trg_Mlk_Met_g'), self.get_value('An_MetUse_g'), self.get_value('Trg_MetUse_g'), 
    #                     self.get_value('Trg_AbsMet_NPxprtMet'), self.get_value('AnNPxMet_AbsMet'), self.get_value('AnNPxMetUser_AbsMet')],
    #             'Phe': [self.get_value('Ur_PheEnd_g'), self.get_value('Fe_PheMet_g'), self.get_value('Scrf_Phe_g'), 
    #                     self.get_value('Gest_Phe_g'), self.get_value('Body_PheGain_g'), self.get_value('Mlk_Phe_g'), 
    #                     self.get_value('Trg_Mlk_Phe_g'), self.get_value('An_PheUse_g'), self.get_value('Trg_PheUse_g'), 
    #                     self.get_value('Trg_AbsPhe_NPxprtPhe'), self.get_value('AnNPxPhe_AbsPhe'), self.get_value('AnNPxPheUser_AbsPhe')],
    #             'Thr': [self.get_value('Ur_ThrEnd_g'), self.get_value('Fe_ThrMet_g'), self.get_value('Scrf_Thr_g'), 
    #                     self.get_value('Gest_Thr_g'), self.get_value('Body_ThrGain_g'), self.get_value('Mlk_Thr_g'), 
    #                     self.get_value('Trg_Mlk_Thr_g'), self.get_value('An_ThrUse_g'), self.get_value('Trg_ThrUse_g'), 
    #                     self.get_value('Trg_AbsThr_NPxprtThr'), self.get_value('AnNPxThr_AbsThr'), self.get_value('AnNPxThrUser_AbsThr')],
    #             'Trp': [self.get_value('Ur_TrpEnd_g'), self.get_value('Fe_TrpMet_g'), self.get_value('Scrf_Trp_g'), 
    #                     self.get_value('Gest_Trp_g'), self.get_value('Body_TrpGain_g'), self.get_value('Mlk_Trp_g'), 
    #                     self.get_value('Trg_Mlk_Trp_g'), self.get_value('An_TrpUse_g'), self.get_value('Trg_TrpUse_g'), 
    #                     self.get_value('Trg_AbsTrp_NPxprtTrp'), self.get_value('AnNPxTrp_AbsTrp'), self.get_value('AnNPxTrpUser_AbsTrp')],
    #             'Val': [self.get_value('Ur_ValEnd_g'), self.get_value('Fe_ValMet_g'), self.get_value('Scrf_Val_g'), 
    #                     self.get_value('Gest_Val_g'), self.get_value('Body_ValGain_g'), self.get_value('Mlk_Val_g'), 
    #                     self.get_value('Trg_Mlk_Val_g'), self.get_value('An_ValUse_g'), self.get_value('Trg_ValUse_g'), 
    #                     self.get_value('Trg_AbsVal_NPxprtVal'), self.get_value('AnNPxVal_AbsVal'), self.get_value('AnNPxValUser_AbsVal')]
    #         }

    #         index_names = ["Diet (a)", "Duod RUP (b)", "Duod Micr (b)", "Duod Endog (b)", "Duod Tot, True (b)", 
    #                     "Duod Tot, 24h Hydr (a)", "Met RUP (b,c)", "Met Micr (b,c)", "Met Total (b,c)", 
    #                     "Targ Supp at User Enter (b,d)"]
    #         df_aa_flows = pd.DataFrame(data, index=index_names).T

    #         # Footnotes for Tbl6_4
    #         footnotes = {
    #             'a': ["not corrected for incomplete recovery of AA during a 24-h acid hydrolysis"],
    #             'b': ["corrected for incomplete recovery of AA during a 24-h acid hydrolysis."],
    #             'c': ["mEAA: metabolized EAA."],
    #             'd': ["Calculated using target efficiencies and net use pre Table 6.5 and user entered milk protein production"]
    #         }
    #         df_footnotes = pd.DataFrame(footnotes).T

    #         return df_aa_flows, df_footnotes

    #     def create_aa_partitioning_dataframe(self):
    #         # Data for Tbl6_5
    #         data = {
    #             'Arg': [self.get_value('Ur_ArgEnd_g'), self.get_value('Fe_ArgMet_g'), self.get_value('Scrf_Arg_g'), 
    #                     self.get_value('Gest_Arg_g'), self.get_value('Body_ArgGain_g'), self.get_value('Mlk_Arg_g'), 
    #                     self.get_value('Trg_Mlk_Arg_g'), self.get_value('An_ArgUse_g'), self.get_value('Trg_ArgUse_g'), None, 
    #                     self.get_value('AnNPxArg_AbsArg'), self.get_value('AnNPxArgUser_AbsArg')],
    #             # Add other amino acids similarly
    #         }
    #         index_names = ["Uri. Endo.", "Metab. Fecal", "Scurf", "Gestation", "Body Gain", "Milk, Nutr. Allow.", 
    #                     "Milk, User Enter.", "Total, Nutr. Allow.", "Total, User Enter.", "Target Eff (b)", 
    #                     "Nutr Allow Eff (b)", "User Enter Eff (b)"]
    #         df_aa_partitioning = pd.DataFrame(data, index=index_names).T

    #         # Footnotes for Tbl6_5
    #         footnote_text = "Corrected for incomplete recovery of AA during a 24-h hydrolysis. Efficiencies for Uri. Endo. and gestation are 1 and 0.33. Combined efficiencies calculated from MP supply for other functions. A target efficiency was not estimated for Arg due to semi-essentiality."
    #         df_partitioning_footnotes = pd.DataFrame([footnote_text], columns=['b']).T

    #         return df_aa_partitioning, df_partitioning_footnotes

    #     # Usage
    #     df_aa_flows, df_footnotes = create_aa_flows_dataframe(self)
    #     df_aa_partitioning, df_partitioning_footnotes = create_aa_partitioning_dataframe(self)

    #     return {'AA_flow': df_aa_flows, 'AA_partitioning': df_aa_partitioning }
    