import pandas as pd
import re
import numpy as np

class ModelOutput:
    """
    A class for storing the output from run_NASEM

    Attributes:
        locals_input (dict): Dictionary with all variables calculated in the run_NASEM function

    Methods:
        __init__(locals_input):
            Initalizes the ModelOutput instance. Runs sorting methods when initalized to sort locals_input.

        __populate_category(category_name, group_names, *variable_lists):
            Creates and populates a nested dictionary using lists of variable names
        
        __populate_uncategorized():
            Stores all remaining values in locals_input in the Uncategorized category and pops them from locals_input.

        get_value(name):
            Retrieves a value, dictionary or dataframe with a given name from the ModelOutput instance.

    Example:
        # Create an instance of ModelOutput
        model_output = ModelOutput(locals_input=my_locals_input_dict)

        # Retrieve a specific group of variables
        requirements_group = model_output.get_value('Requirements')
    """
    def __init__(self, locals_input):
        # Dictionary with all variables from execute_model
        self.locals_input = locals_input
        # Take locals_input and store variables in different Categories
        self.__filter_locals_input()
        self.__sort_Input()
        self.__sort_Intakes()
        self.__sort_Requirements()
        self.__sort_Production()
        self.__sort_Excretion()
        self.__sort_Digestibility()
        self.__sort_Efficiencies()
        self.__sort_Miscellaneous()
        self.__populate_uncategorized()

    
    def __repr__(self):
        summary_intro = "This is a snapshot of the model outputs, followed by instructions for accessing all outputs.\n\n"
        summary_intro += "=====================\n"
        summary_intro += "Model Output Snapshot\n"
        summary_intro += "=====================\n"
               
        snapshot_vars = {
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

        for description, key in snapshot_vars.items():
            raw_value = self.get_value(key)
            if isinstance(raw_value, (float, int)):  # Check if the value is numeric
                value = round(raw_value, 3)  
            elif isinstance(raw_value, (np.ndarray)) and raw_value.size == 1:
                # This is required for any numbers handled by np.where() that return arrays instead of floats - needs cleaning up
                value = round(float(raw_value),3)
            else:
                value = raw_value  
            summary_intro += f"{description}: {value}\n" 

        object_intro = "\n" 
        object_intro += "=====================\n"
        object_intro += "Access Model Outputs\n"
        object_intro += "=====================\n"

        object_intro += "This is a `ModelOutput` object returned by `nd.execute_model()`.\n"
        object_intro += "Each of the following categories can be called directly as methods, \n"
        object_intro += "e.g. if the name of my object is `output`, I would call `output.Production` to see the contents of Production. \n\n"
        
        object_intro += "The following list shows which dictionaries are within each category.\n\n"
        object_intro += "Categories\n---------------------\n"
        
        categories = {
            'Inputs': self.Inputs,
            'Intakes': self.Intakes,
            'Requirements': self.Requirements,
            'Production': self.Production,
            'Excretion': self.Excretion,
            'Digestibility': self.Digestibility,
            'Efficiencies': self.Efficiencies,
            'Miscellaneous': self.Miscellaneous
        }

        for category, keys in categories.items():
            object_intro += f"{category}: {', '.join(keys.keys())}\n"

        object_intro += "\n\nThese outputs can be accessed by name, e.g. `output.Production['milk']['Mlk_Prod']"
        object_intro += "\n\nThere is also a `.search()` method which takes a string and will return a df of all outputs with that string (case insensitive).\n"
        object_intro += "e.g. `output.search('Mlk')`\n"
        object_intro += "An individual output can be retrieved directly by providing its exact name to the  `.get_value()` method.\n"
        object_intro += "e.g. `output.get_value('Mlk_Prod')\n"

        object_intro += "=====================\n"
        return summary_intro + object_intro

        # summary = "=====================\n"
        # summary += "Model Output Summary\n"
        # summary += "=====================\n"
        # summary += f"Predicted Milk Production: {self.Production['milk']['Mlk_Prod']} kg/d\n"
        # summary += f"Metabolizable Energy Requirement: {self.Requirements['energy']['Trg_MEuse']} Mcal/d\n\n"
        # summary += "Categories\n"
        # summary += "---------------------\n"
        # summary += "Inputs: " + ", ".join(self.Inputs.keys()) + "\n"
        # summary += "Intakes: " + ", ".join(self.Intakes.keys()) + "\n"
        # summary += "Requirements: " + ", ".join(self.Requirements.keys()) + "\n"
        # summary += "Production: " + ", ".join(self.Production.keys()) + "\n"
        # summary += "Excretion: " + ", ".join(self.Excretion.keys()) + "\n"
        # summary += "Digestibility: " + ", ".join(self.Digestibility.keys()) + "\n"
        # summary += "Efficiencies: " + ", ".join(self.Efficiencies.keys()) + "\n"
        # summary += "Miscellaneous: " + ", ".join(self.Miscellaneous.keys()) + "\n"
        # summary += "=====================\n"
        # return summary


    def __populate_category(self, category_name, group_names, *variable_lists):
        """
        Creates and populates nested dictionaries using lists of variable names.

        Notes:
            The varaiable_lists must be passed in the same order as listed in group_names
        
        Parameters:
            category_name (str): Name of the dictionary to populate.
            group_names (list): Names of the nested dictionaries to create.
            variable_lists (list): List of variable names, one list for each nested dictionary.
        """ 
        # Check if the Category exists, and create it if it does not
        if not hasattr(self, category_name):
            setattr(self, category_name, {})
        # Populate the category with variables
        for name, var_list in zip(group_names, variable_lists):
            # Create a nested dictionary for the current name if it doesn't exist
            if name not in getattr(self, category_name):
                getattr(self, category_name)[name] = {}
            # Populate the nested dictionary with variables from the corresponding list
            for var in var_list:
                if var in self.locals_input:
                    getattr(self, category_name)[name][var] = self.locals_input.pop(var)


    def __populate_uncategorized(self):
        """
        Store all remaining values in the Uncategorized category and pop them from locals_input.
        """
        setattr(self, 'Uncategorized', {})
        self.Uncategorized.update(self.locals_input)
        self.locals_input.clear()


    def __filter_locals_input(self):
        """
        Remove specified variables from locals_input.
        """
        variables_to_remove = ['key', 'value', 'num_value', 'feed_library_df', 
                               'feed_data', 'diet_info_initial', 'diet_data_initial',
                                'AA_list', 'An_data_initial']
        for key in variables_to_remove:
            # Remove values that should be excluded from output
            self.locals_input.pop(key, None)


    def __sort_Input(self):
        """
        Sort and store specific variables related to model inputs in the Inputs category.
        """
        setattr(self, 'Inputs', {})
        variables_to_add = ['user_diet', 'animal_input', 'equation_selection', 'coeff_dict', 'infusion_input', 'MP_NP_efficiency_input']
        for key in variables_to_add:
            # Add to the Inputs Category
            self.Inputs[key] = self.locals_input[key]
            # Remove so that values are only stored in one place
            self.locals_input.pop(key, None)


    def __sort_Intakes(self):
        """
        Sort and store specific variables related to nutrient intakes in the Intakes category.
        """
        setattr(self, 'Intakes', {})
        variables_to_add = ['diet_info', 'infusion_data', 'diet_data', 'An_data']
        for key in variables_to_add:
            self.Intakes[key] = self.locals_input[key]
            self.locals_input.pop(key, None)

        # Name intake groups
        group_names = ['energy', 'protein', 'AA', 'FA', 'rumen_digestable'] 
        # Lists of variables to store
        energy_variables = ['An_MEIn', 'An_NEIn', 'An_NE', 'An_MEIn_approx']
        protein_variables = ['An_MPIn', 'An_MPIn_g']
        AA_variables = ['AA_values', 'Abs_EAA_g', 'Abs_neAA_g', 'Abs_OthAA_g', 'Abs_EAA2b_g']
        FA_variables = []
        rumen_digestable_variables = ['Rum_DigNDFIn', 'Rum_DigStIn']
        # Store variables
        self.__populate_category('Intakes', group_names, energy_variables, protein_variables, AA_variables, FA_variables, rumen_digestable_variables)


    def __sort_Requirements(self):
        """
        Sort and store specific variables related to required intakes in the Requirements category.
        """
        # Name digestability groups
        group_names = ['energy', 'protein']
        # Lists of variables to store
        energy_variables = ['An_NEmUse_NS', 'An_NEm_Act_Graze', 'An_NEm_Act_Parlor', 'An_NEm_Act_Topo',
                            'An_NEmUse_Act', 'An_NEmUse', 'An_MEmUse', 'Gest_MEuse', 'Trg_Mlk_NEout', 'Trg_Mlk_MEout', 'Trg_MEuse']
        protein_variables = ['Gest_NCPgain_g', 'Gest_NPgain_g', 'Gest_NPuse_g', 'Gest_CPuse_g', 'An_MPm_g_Trg', 'Body_NPgain_g', 'Body_MPUse_g_Trg', 'Gest_MPUse_g_Trg', 'Trg_Mlk_NP_g', 'Mlk_MPUse_g_Trg', 'An_MPuse_g_Trg', 'Min_MPuse_g',
                             'Diff_MPuse_g', 'Frm_NPgain_g', 'Frm_MPUse_g_Trg', 'Rsrv_NPgain_g', 'Rsrv_MPUse_g_Trg']
        # Store variables
        self.__populate_category('Requirements', group_names, energy_variables, protein_variables)


        ### Store mineral requirements in nested dictionaries ###
        mineral_abbreviations = ['Ca', 'P', 'Mg', 'Na', 'Cl', 'K', 'S', 'Co', 'Cu', 'I', 'Fe', 'Mn', 'Se', 'Zn']
        mineral_variable_lists = [
            ['Ca_Mlk', 'Fe_Ca_m', 'An_Ca_g', 'An_Ca_y', 'An_Ca_l', 'An_Ca_Clf', 'An_Ca_req', 'An_Ca_bal', 'An_Ca_prod'],
            ['Ur_P_m', 'Fe_P_m', 'An_P_m', 'An_P_g', 'An_P_y', 'An_P_l', 'An_P_Clf', 'An_P_req', 'An_P_bal', 'Fe_P_g', 'An_P_prod'],
            ['An_Mg_Clf', 'Ur_Mg_m', 'Fe_Mg_m', 'An_Mg_m', 'An_Mg_g', 'An_Mg_y', 'An_Mg_l', 'An_Mg_req', 'An_Mg_bal', 'An_Mg_prod'],
            ['An_Na_Clf', 'Fe_Na_m', 'An_Na_g', 'An_Na_y', 'An_Na_l', 'An_Na_req', 'An_Na_bal', 'An_Na_prod'],
            ['An_Cl_Clf', 'Fe_Cl_m', 'An_Cl_g', 'An_Cl_y', 'An_Cl_l', 'An_Cl_req', 'An_Cl_bal', 'An_Cl_prod'],
            ['An_K_Clf', 'Ur_K_m', 'Fe_K_m', 'An_K_m', 'An_K_g', 'An_K_y', 'An_K_l', 'An_K_req', 'An_K_bal', 'An_K_prod'],
            ['An_S_req', 'An_S_bal'],
            ['An_Co_req', 'An_Co_bal'],
            ['An_Cu_Clf', 'An_Cu_m', 'An_Cu_g', 'An_Cu_y', 'An_Cu_l', 'An_Cu_req', 'An_Cu_bal', 'An_Cu_prod'],
            ['An_I_req', 'An_I_bal'],
            ['An_Fe_Clf', 'An_Fe_g', 'An_Fe_y', 'An_Fe_l', 'An_Fe_req', 'An_Fe_bal', 'An_Fe_prod'],
            ['An_Mn_Clf', 'An_Mn_m', 'An_Mn_g', 'An_Mn_y', 'An_Mn_l', 'An_Mn_req', 'An_Mn_bal', 'An_Mn_prod'],
            ['An_Se_req', 'An_Se_bal'],
            ['An_Zn_Clf', 'An_Zn_m', 'An_Zn_g', 'An_Zn_y', 'An_Zn_l', 'An_Zn_req', 'An_Zn_bal', 'An_Zn_prod']
        ]
        mineral_requirements = {}
        # NOTE Since all the mineral requirements are nested within mineral_requirements can't use populate_category()
        for abbreviation, variable_list in zip(mineral_abbreviations, mineral_variable_lists):
            mineral_requirements[abbreviation] = {}  # Initialize the dictionary for the current mineral
            for variable in variable_list:
                if variable in self.locals_input:
                    mineral_requirements[abbreviation][variable] = self.locals_input.pop(variable)
        self.Requirements['mineral_requirements'] = mineral_requirements


    def __sort_Production(self):
        """
        Sort and store specific variables related to production, including body composition changes and gestation, in the Production category.
        """
        # Name production groups
        group_names = ['milk', 'body_composition', 'gestation', 'MiCP']
        # List variables to store
        milk_variables = ['Trg_NEmilk_Milk', 'Mlk_NP_g', 'Mlk_CP_g', 'Trg_Mlk_Fat' ,'Trg_Mlk_Fat_g', 'Mlk_Fatemp_g', 'Mlk_Fat_g', 'Mlk_Fat', 'Mlk_NP', 'Mlk_Prod_comp',
                          'An_MPavail_Milk_Trg', 'Mlk_NP_MPalow_Trg_g', 'Mlk_Prod_MPalow', 'An_MEavail_Milk', 'Mlk_Prod_NEalow', 'Mlk_Prod', 'MlkNP_Milk', 'MlkFat_Milk', 'MlkNE_Milk', 'Mlk_NEout', 'Mlk_MEout']
        composition_variables = ['CPGain_FrmGain', 'NPGain_FrmGain', 'Frm_Gain', 'Rsrv_Gain', 'Rsrv_Gain_empty', 'NPGain_RsrvGain', 'Rsrv_NPgain',
                                 'Frm_Gain_empty', 'Body_Gain_empty', 'Frm_NPgain', 'Body_NPgain', 'Body_CPgain', 'Body_CPgain_g', 'Rsrv_Fatgain', 'Rsrv_CPgain', 'Rsrv_NEgain', 'An_BWmature_empty', 'Body_Gain']
        gestation_variables = ['Uter_Wtpart', 'Uter_Wt', 'GrUter_Wtpart', 'GrUter_Wt', 'Uter_BWgain', 'GrUter_BWgain', 'Rsrv_MEgain', 'FatGain_FrmGain', 'Frm_Fatgain',
                               'Frm_CPgain', 'Frm_NEgain', 'Frm_MEgain', 'An_MEgain', 'Gest_REgain']
        MiCP_variables = ['RDPIn_MiNmax', 'MiN_Vm', 'Du_MiN_g', 'Du_MiCP_g', 'Du_MiTP_g', 'Du_MiCP', 'Du_idMiCP_g', 'Du_idMiCP', 'Du_idMiTP_g', 'Du_idMiTP']
        # Store variables
        self.__populate_category('Production', group_names, milk_variables, composition_variables, gestation_variables, MiCP_variables)


    def __sort_Excretion(self):
        """
        Sort and store specific variables related to excreted nutrients in the Excretion category.
        """
        # Name excretion groups
        group_names = ['fecal', 'urinary', 'gaseous', 'scurf'] 
        # Lists of variables to store
        fecal_variables = ['Fe_rOMend', 'Fe_RUP', 'Fe_RumMiCP', 'Fe_CPend_g', 'Fe_CPend', 'Fe_CP', 'Fe_NPend', 'Fe_NPend_g', 'Fe_MPendUse_g_Trg']
        urinary_variables = ['Ur_Nout_g', 'Ur_DEout', 'Ur_Nend_g', 'Ur_NPend_g', 'Ur_MPendUse_g']
        gaseous_variables = []
        scurf_variables = ['Scrf_CP_g', 'Scrf_NP_g', 'Scrf_MPUse_g_Trg']
        # Store variables
        self.__populate_category('Excretion', group_names, fecal_variables, urinary_variables, gaseous_variables, scurf_variables)


    def __sort_Digestibility(self):
        """
        Sort and store specific variables related to digestability in the Digestability category.
        """
        # Name digestability groups
        group_names = ['rumen', 'TT']
        # Lists of variables to store
        rumen_variables = ['Rum_dcNDF', 'Rum_dcSt']
        TT_variables = []
        # Store variables
        self.__populate_category('Digestibility', group_names, rumen_variables, TT_variables)


    def __sort_Efficiencies(self):
        """
        Sort and store specific variables related to conversion efficiencies in the Efficiencies category.
        """
        # Name digestability groups
        group_names = ['energy', 'protein']
        # Lists of variables to store
        energy_variables = ['Kr_ME_RE']
        protein_variables = ['Kg_MP_NP_Trg']
        # Store variables
        self.__populate_category('Efficiencies', group_names, energy_variables, protein_variables)


    def __sort_Miscellaneous(self):
        """
        Sort and store specific miscellaneous variables that need a final location in the Miscellaneous category.
        """
        # These variables need to be given a storage location
        group_names = ['misc']
        # Lists of variables to store
        misc_variables = ['Kb_LateGest_DMIn', 'An_PrePartWklim', 'An_PrePartWkDurat', 'An_DMIn_BW', 'f_mPrt_max', 'mPrt_k_EAA2', 'An_REgain_Calf', 'An_LactDay_MlkPred', 'An_DCADmeq', 'Dt_DMIn_BW', 'Dt_DMIn_MBW']
        # Store variables
        self.__populate_category('Miscellaneous', group_names, misc_variables)
   

    def get_value(self, name):
        """
        Retrieve a value, dictionary or dataframe with a given name from the ModelOutput instance.

        Parameters:
        name (str): The name of the group to retrieve.

        Returns:
        str or int or float or dict or pd.DataFrame or None: The object with the given name, or None if not found.
        """
        # Helper function to recursively search for a group in a nested dictionary
        def recursive_search(dictionary, target_name):
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
                if isinstance(category, dict) and category_name == name:
                    return category
                elif isinstance(category, pd.DataFrame) and category_name == name:
                    return category
                elif isinstance(category, dict):
                    result = recursive_search(category, name)
                    if result is not None:
                        return result

        # Return None if not found
        return None
       

    def search(self, search_string, dictionaries_to_search=None):
        # Define the dictionaries to search within, by default all dictionaries where outputs are stored
        if dictionaries_to_search is None:
            dictionaries_to_search = ['Inputs', 'Intakes', 'Requirements', 'Production',
                                      'Excretion', 'Digestibility', 'Efficiencies',
                                      'Miscellaneous', 'Uncategorized']
        result = {}
        visited_keys = set()
        table_rows = []

        def recursive_search(d, path=''):
            for key, value in d.items():
                full_key = path + key
                if re.search(search_string, str(full_key), flags=re.IGNORECASE) and full_key not in visited_keys:
                    result[full_key] = value
                    visited_keys.add(full_key)
                if isinstance(value, dict):
                    recursive_search(value, full_key + '.')
                elif isinstance(value, pd.DataFrame):
                    matching_columns = [col for col in value.columns if re.search(search_string, col, flags=re.IGNORECASE)]
                    if matching_columns:
                        columns_key = full_key + '_columns'
                        if columns_key not in visited_keys:
                            result[columns_key] = matching_columns
                            visited_keys.add(columns_key)

        def extract_dataframe_and_column(key, value):
            parts = key.split('.')[-1].rsplit('_', 1)
            # variable_name = parts[0]
            dataframe_name, column_name = parts[-1], "column"
            return {'Name': value, 'Value': f'{parts[0]}[{column_name}]'}

        # Iterate over specified dictionaries
        for dictionary_name in dictionaries_to_search:
            dictionary = getattr(self, dictionary_name, None)
            if dictionary is not None and isinstance(dictionary, dict):
                recursive_search(dictionary, dictionary_name + '.')

        # Create output dataframe
        for key, value in result.items():
            variable_name = key.split('.')[-1]
            if isinstance(value, dict):
                value_display = 'dict'
            elif isinstance(value, pd.DataFrame):
                value_display = 'Dataframe'
            elif isinstance(value, list) and key.endswith('_columns'):
                table_rows.extend([extract_dataframe_and_column(key, col) for col in value])
            elif isinstance(value, list):
                value_display = 'list'
            else:
                value_display = value  
            # Add the current row to the list
            if not (isinstance(value, list) and key.endswith('_columns')):
                table_rows.append({'Name': variable_name, 'Value': value_display})

        output_table = pd.DataFrame(table_rows)
        return output_table
    