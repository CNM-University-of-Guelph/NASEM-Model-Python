import re
from typing import Any, Dict, List, Union

import numpy as np
import pandas as pd


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
        
        search(search_string, dictionaries_to_search=None, case_sensitive: bool = False)
            Recursive search through all outputs and return a dataframe with name, value and path of parent object. 
            The search is not case_sensitive by default, but can be by setting case_sensitive to True. The default of None for
            dictionaries_to_search will search all outputs.


    Example:
        # Create an instance of ModelOutput
        model_output = ModelOutput(locals_input=my_locals_input_dict)

        # Retrieve a specific group of variables
        requirements_group = model_output.get_value('Requirements')
    """

    def __init__(self, locals_input: dict) -> None:
        # Dictionary with all variables from execute_model
        self.locals_input = locals_input
        self.dev_out = {}
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
        self.__calculate_additional_variables()

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

    def __populate_category(self, 
                            category_name: str, 
                            group_names: List[str], 
                            *variable_lists: List[str]
) -> None:
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
                    getattr(
                        self,
                        category_name)[name][var] = self.locals_input.pop(var)

    def __populate_uncategorized(self) -> None:
        """
        Store all remaining values in the Uncategorized category and pop them from locals_input.
        """
        setattr(self, 'Uncategorized', {})
        self.Uncategorized.update(self.locals_input)
        self.locals_input.clear()

    def __filter_locals_input(self) -> None:
        """
        Remove specified variables from locals_input.
        Add to dev output for easier development. Not included in search or get_value methods.
        """
        setattr(self, 'dev_out', {})
        variables_to_remove = [
            'key', 'value', 'num_value', 'feed_library_df', 'feed_data',
            'diet_info_initial', 'diet_data_initial', 'AA_list',
            'An_data_initial', 'mPrt_coeff_list', 'mPrt_k_AA'
        ]
        for key in variables_to_remove:
            # Add to the dev Category
            self.dev_out[key] = self.locals_input[key]
            # Remove values that should be excluded from output
            self.locals_input.pop(key, None)

    def __sort_Input(self) -> None:
        """
        Sort and store specific variables related to model inputs in the Inputs category.
        """
        setattr(self, 'Inputs', {})
        variables_to_add = [
            'user_diet', 'animal_input', 'equation_selection', 'coeff_dict',
            'infusion_input', 'MP_NP_efficiency_input', 'mPrt_coeff', 'f_Imb'
        ]
        for key in variables_to_add:
            # Add to the Inputs Category
            self.Inputs[key] = self.locals_input[key]
            # Remove so that values are only stored in one place
            self.locals_input.pop(key, None)

    def __sort_Intakes(self) -> None:
        """
        Sort and store specific variables related to nutrient intakes in the Intakes category.
        """
        setattr(self, 'Intakes', {})
        variables_to_add = [
            'diet_info', 'infusion_data', 'diet_data', 'An_data'
        ]
        for key in variables_to_add:
            self.Intakes[key] = self.locals_input[key]
            self.locals_input.pop(key, None)

        # Name intake groups
        group_names = [
            'energy', 'protein', 'AA', 'FA', 'rumen_digestable', 'water'
        ]
        # Lists of variables to store
        energy_variables = [
            'An_MEIn', 'An_NEIn', 'An_NE', 'An_MEIn_approx', 'An_ME',
            'An_ME_GE', 'An_ME_DE', 'An_NE_GE', 'An_NE_DE', 'An_NE_ME'
        ]
        protein_variables = [
            'An_MPIn', 'An_MPIn_g', 'An_MP', 'An_MP_CP', 'An_MPIn_MEIn',
            'An_RUPIn_g'
        ]
        AA_variables = [
            'AA_values', 'Abs_EAA_g', 'Abs_neAA_g', 'Abs_OthAA_g',
            'Abs_EAA2b_g', 'Du_EAA_g', 'Abs_EAA2_g', 'Abs_EAA2_HILKM_g',
            'Abs_EAA2_RHILKM_g', 'Abs_EAA2_HILKMT_g', 'An_IdEAAIn',
            'Dt_IdEAARUPIn'
        ]
        FA_variables = []
        rumen_digestable_variables = [
            'Rum_DigNDFIn', 'Rum_DigStIn', 'Rum_DigNDFnfIn', 'Du_StPas',
            'Du_NDFPas'
        ]
        water_variables = ['An_WaIn', 'An_Wa_Insens', 'WaIn_Milk']
        # Store variables
        self.__populate_category('Intakes', group_names, energy_variables,
                                 protein_variables, AA_variables, FA_variables,
                                 rumen_digestable_variables, water_variables)

    def __sort_Requirements(self) -> None:
        """
        Sort and store specific variables related to required intakes in the Requirements category.
        """
        # Name digestability groups
        group_names = ['energy', 'protein', 'vitamin', 'mineral']
        # Lists of variables to store
        energy_variables = [
            'An_NEmUse_NS', 'An_NEm_Act_Graze', 'An_NEm_Act_Parlor',
            'An_NEm_Act_Topo', 'An_NEmUse_Act', 'An_NEmUse', 'An_MEmUse',
            'Gest_MEuse', 'Trg_Mlk_NEout', 'Trg_Mlk_MEout', 'Trg_MEuse',
            'An_MEmUse_NS', 'An_MEmUse_Act', 'An_MEmUse_Env', 'An_NEm_ME',
            'An_NEm_DE', 'An_NEmNS_DE', 'An_NEmAct_DE', 'An_NEmEnv_DE',
            'An_NEprod_Avail', 'An_MEprod_Avail', 'Gest_NELuse', 'Gest_NE_ME',
            'Gest_NE_DE', 'An_REgain', 'Rsrv_NE_DE', 'Frm_NE_DE',
            'Body_NEgain_BWgain', 'An_ME_NEg', 'Rsrv_NELgain', 'Frm_NELgain',
            'An_NELgain', 'An_NEgain_DE', 'An_NEgain_ME', 'An_MEuse',
            'An_NEuse', 'Trg_NEuse', 'An_NELuse', 'Trg_NELuse', 'An_NEprod_GE',
            'Trg_NEprod_GE', 'An_NEmlk_GE', 'Trg_NEmlk_GE', 'An_MEbal',
            'An_NELbal', 'An_NEbal', 'Trg_MEbal', 'Trg_NELbal', 'Trg_NEbal',
            'An_MPuse_MEuse', 'Trg_MPuse_MEuse', 'An_MEavail_Grw', 'Kg_ME_NE',
            'Km_ME_NE', 'Kf_ME_RE_ClfDry', 'Kf_ME_RE'
        ]
        protein_variables = [
            'Gest_NCPgain_g', 'Gest_NPgain_g', 'Gest_NPuse_g', 'Gest_CPuse_g',
            'An_MPm_g_Trg', 'Body_NPgain_g', 'Body_MPUse_g_Trg',
            'Gest_MPUse_g_Trg', 'Trg_Mlk_NP_g', 'Mlk_MPUse_g_Trg',
            'An_MPuse_g_Trg', 'Min_MPuse_g', 'Diff_MPuse_g', 'Frm_NPgain_g',
            'Frm_MPUse_g_Trg', 'Rsrv_NPgain_g', 'Rsrv_MPUse_g_Trg',
            'An_NPm_Use', 'An_CPm_Use', 'Gest_EAA_g', 'Trg_AbsAA_NPxprtAA',
            'An_CPxprt_g', 'An_NPxprt_g', 'Trg_NPxprt_g', 'An_CPprod_g',
            'An_NPprod_g', 'Trg_NPprod_g', 'An_NPprod_MPIn', 'Trg_NPuse_g',
            'An_NPuse_g', 'An_NCPuse_g', 'An_Nprod_g', 'An_Nprod_NIn',
            'An_Nprod_DigNIn', 'An_EAAUse_g', 'AnEAAUse_AbsEAA', 'An_EAABal_g',
            'Trg_AbsEAA_NPxprtEAA', 'Trg_AbsArg_NPxprtArg', 'Trg_AAEff_EAAEff',
            'Imb_EAA', 'An_MPBal_g_Trg', 'Xprt_NP_MP_Trg', 'Trg_MPIn_req',
            'An_MPavail_Gain_Trg', 'Xprt_NP_MP', 'Km_MP_NP', 'Kl_MP_NP',
            'An_MPuse_g', 'An_MPuse', 'An_MPBal_g', 'An_MP_NP', 'An_NPxprt_MP',
            'An_CP_NP', 'An_NPBal_g', 'An_NPBal'
        ]
        vitamin_variables = [
            'An_VitA_req', 'An_VitA_bal', 'An_VitD_req', 'An_VitD_bal',
            'An_VitE_req', 'An_VitE_bal', 'Dt_VitAReq_DMI', 'Dt_VitDReq_DMI',
            'Dt_VitEReq_DMI'
        ]
        mineral_variables = [
            'Dt_CaReq_DMI', 'Dt_PReq_DMI', 'Dt_MgReq_DMI', 'Dt_KReq_DMI',
            'Dt_NaReq_DMI', 'Dt_ClReq_DMI', 'Dt_SReq_DMI', 'Dt_CoReq_DMI',
            'Dt_CuReq_DMI', 'Dt_FeReq_DMI', 'Dt_IReq_DMI', 'Dt_MnReq_DMI',
            'Dt_SeReq_DMI', 'Dt_ZnReq_DMI'
        ]
        # Store variables
        self.__populate_category('Requirements', group_names, energy_variables,
                                 protein_variables, vitamin_variables,
                                 mineral_variables)

        ### Store mineral requirements in nested dictionaries ###
        mineral_abbreviations = [
            'Ca', 'P', 'Mg', 'Na', 'Cl', 'K', 'S', 'Co', 'Cu', 'I', 'Fe', 'Mn',
            'Se', 'Zn'
        ]
        mineral_variable_lists = [
            [
                'Ca_Mlk', 'Fe_Ca_m', 'An_Ca_g', 'An_Ca_y', 'An_Ca_l',
                'An_Ca_Clf', 'An_Ca_req', 'An_Ca_bal', 'An_Ca_prod' 
            ],
            [
                'Ur_P_m', 'Fe_P_m', 'An_P_m', 'An_P_g', 'An_P_y', 'An_P_l',
                'An_P_Clf', 'An_P_req', 'An_P_bal', 'Fe_P_g', 'An_P_prod'
            ],
            [
                'An_Mg_Clf', 'Ur_Mg_m', 'Fe_Mg_m', 'An_Mg_m', 'An_Mg_g',
                'An_Mg_y', 'An_Mg_l', 'An_Mg_req', 'An_Mg_bal', 'An_Mg_prod'
            ],
            [
                'An_Na_Clf', 'Fe_Na_m', 'An_Na_g', 'An_Na_y', 'An_Na_l',
                'An_Na_req', 'An_Na_bal', 'An_Na_prod'
            ],
            [
                'An_Cl_Clf', 'Fe_Cl_m', 'An_Cl_g', 'An_Cl_y', 'An_Cl_l',
                'An_Cl_req', 'An_Cl_bal', 'An_Cl_prod'
            ],
            [
                'An_K_Clf', 'Ur_K_m', 'Fe_K_m', 'An_K_m', 'An_K_g', 'An_K_y',
                'An_K_l', 'An_K_req', 'An_K_bal', 'An_K_prod'
            ], ['An_S_req', 'An_S_bal'], ['An_Co_req', 'An_Co_bal'],
            [
                'An_Cu_Clf', 'An_Cu_m', 'An_Cu_g', 'An_Cu_y', 'An_Cu_l',
                'An_Cu_req', 'An_Cu_bal', 'An_Cu_prod'
            ], ['An_I_req', 'An_I_bal'],
            [
                'An_Fe_Clf', 'An_Fe_g', 'An_Fe_y', 'An_Fe_l', 'An_Fe_req',
                'An_Fe_bal', 'An_Fe_prod'
            ],
            [
                'An_Mn_Clf', 'An_Mn_m', 'An_Mn_g', 'An_Mn_y', 'An_Mn_l',
                'An_Mn_req', 'An_Mn_bal', 'An_Mn_prod'
            ], ['An_Se_req', 'An_Se_bal'],
            [
                'An_Zn_Clf', 'An_Zn_m', 'An_Zn_g', 'An_Zn_y', 'An_Zn_l',
                'An_Zn_req', 'An_Zn_bal', 'An_Zn_prod'
            ]
        ]
        mineral_requirements = {}
        # NOTE Since all the mineral requirements are nested within 
        # mineral_requirements can't use populate_category()
        for mineral, variable_list in zip(mineral_abbreviations,
                                               mineral_variable_lists):
            mineral_requirements[mineral] = {}  
            # Initialize the dictionary for the current mineral
            for variable in variable_list:
                if variable in self.locals_input:
                    mineral_requirements[mineral][
                        variable] = self.locals_input.pop(variable)
        self.Requirements['mineral_requirements'] = mineral_requirements

    def __sort_Production(self) -> None:
        """
        Sort and store specific variables related to production, including body composition changes and gestation, in the Production category.
        """
        # Name production groups
        group_names = ['milk', 'body_composition', 'gestation', 'MiCP']
        # List variables to store
        milk_variables = [
            'Trg_NEmilk_Milk', 'Mlk_NP_g', 'Mlk_CP_g', 'Trg_Mlk_Fat',
            'Trg_Mlk_Fat_g', 'Mlk_Fatemp_g', 'Mlk_Fat_g', 'Mlk_Fat', 'Mlk_NP',
            'Mlk_Prod_comp', 'An_MPavail_Milk_Trg', 'Mlk_NP_MPalow_Trg_g',
            'Mlk_Prod_MPalow', 'An_MEavail_Milk', 'Mlk_Prod_NEalow', 'Mlk_Prod',
            'MlkNP_Milk', 'MlkFat_Milk', 'MlkNE_Milk', 'Mlk_NEout', 'Mlk_MEout',
            'Mlk_NPmx', 'MlkNP_MlkNPmx', 'Mlk_CP', 'Mlk_EAA_g', 'MlkNP_AnMP',
            'MlkEAA_AbsEAA', 'MlkNP_AnCP', 'Mlk_MPUse_g', 'Trg_MilkLac',
            'Trg_NEmilk_DEIn', 'Trg_MilkProd_EPcor', 'Mlk_Prod_NEalow_EPcor',
            'Mlk_EPcorNEalow_DMIn', 'MlkNP_Milk_p', 'MlkFat_Milk_p',
            'Mlk_NE_DE', 'Trg_Mlk_EAA_g', 'Trg_MlkEAA_AbsEAA', 'MlkNP_Int',
            'MlkNP_DEInp', 'MlkNP_NDF', 'MlkNP_AbsEAA', 'MlkNP_AbsNEAA',
            'MlkNP_AbsOthAA', "Trg_Mlk_NP"
        ]
        composition_variables = [
            'CPGain_FrmGain', 'NPGain_FrmGain', 'Frm_Gain', 'Rsrv_Gain',
            'Rsrv_Gain_empty', 'NPGain_RsrvGain', 'Rsrv_NPgain',
            'Frm_Gain_empty', 'Body_Gain_empty', 'Frm_NPgain', 'Body_NPgain',
            'Body_CPgain', 'Body_CPgain_g', 'Rsrv_Fatgain', 'Rsrv_CPgain',
            'Rsrv_NEgain', 'An_BWmature_empty', 'Body_Gain', 'Conc_BWgain',
            'BW_BCS', 'Body_Fat_EBW', 'Body_NonFat_EBW', 'Body_CP_EBW',
            'Body_Ash_EBW', 'Body_Wat_EBW', 'Body_Fat', 'Body_NonFat',
            'Body_CP', 'Body_Ash', 'Body_Wat', 'An_BodConcgain',
            'NonFatGain_FrmGain', 'Body_Fatgain', 'Body_NonFatGain',
            'Frm_CPgain_g', 'Rsrv_CPgain_g', 'Body_AshGain', 'Frm_AshGain',
            'WatGain_RsrvGain', 'Rsrv_WatGain', 'Body_WatGain', 'Frm_WatGain',
            'Body_EAAGain_g', 'Body_NPgain_MPalowTrg_g',
            'Body_CPgain_MPalowTrg_g', 'Body_Gain_MPalowTrg_g',
            'Body_Gain_MPalowTrg', 'Body_Gain_NEalow', 'An_BodConcgain_NEalow',
            'Body_Fatgain_NEalow', 'Body_NPgain_NEalow', 'An_Days_BCSdelta1',
            "Rsrv_AshGain"
        ]
        gestation_variables = [
            'Uter_Wtpart', 'Uter_Wt', 'GrUter_Wtpart', 'GrUter_Wt',
            'Uter_BWgain', 'GrUter_BWgain', 'Rsrv_MEgain', 'FatGain_FrmGain',
            'Frm_Fatgain', 'Frm_CPgain', 'Frm_NEgain', 'Frm_MEgain',
            'An_MEgain', 'Gest_REgain', 'An_Preg', 'Fet_Wt', 'Fet_BWgain'
        ]
        MiCP_variables = [
            'RDPIn_MiNmax', 'MiN_Vm', 'Du_MiN_g', 'Du_MiCP_g', 'Du_MiTP_g',
            'Du_MiCP', 'Du_idMiCP_g', 'Du_idMiCP', 'Du_idMiTP_g', 'Du_idMiTP',
            'Du_MiTP', 'Du_EndCP_g', 'Du_EndN_g', 'Du_EndCP', 'Du_EndN',
            'Du_NAN_g', 'Du_NANMN_g', 'Du_MiN_NRC2001_g', 'Rum_MiCP_DigCHO',
            'Du_IdEAAMic'
        ]
        # Store variables
        self.__populate_category('Production', group_names, milk_variables,
                                 composition_variables, gestation_variables,
                                 MiCP_variables)

    def __sort_Excretion(self) -> None:
        """
        Sort and store specific variables related to excreted nutrients in the Excretion category.
        """
        # Name excretion groups
        group_names = ['fecal', 'urinary', 'gaseous', 'scurf']
        # Lists of variables to store
        fecal_variables = [
            'Fe_rOMend', 'Fe_RUP', 'Fe_RumMiCP', 'Fe_CPend_g', 'Fe_CPend',
            'Fe_CP', 'Fe_NPend', 'Fe_NPend_g', 'Fe_MPendUse_g_Trg', 'Fe_rOM',
            'Fe_St', 'Fe_NDF', 'Fe_NDFnf', 'Fe_Nend', 'Fe_RDPend', 'Fe_RUPend',
            'Fe_MiTP', 'Fe_InfCP', 'Fe_TP', 'Fe_N', 'Fe_N_g', 'Fe_FA',
            'Fe_OM_end', 'Fe_OM', 'Fe_DEMiCPend', 'Fe_DERDPend', 'Fe_DERUPend',
            'Fe_DEout', 'Fe_DE_GE', 'Fe_DE', 'Fe_AAMet_g', 'Fe_AAMet_AbsAA',
            'Fe_MPendUse_g', 'Man_out', 'Man_Milk', 'Man_VolSld', 'Man_VolSld2',
            'VolSlds_Milk', 'VolSlds_Milk2', 'Man_Nout_g', 'Man_Nout2_g',
            'ManN_Milk', 'Man_Ca_out', 'Man_P_out', 'Man_Mg_out', 'Man_K_out',
            'Man_Na_out', 'Man_Cl_out', 'Man_MacMin_out', 'Man_Cu_out',
            'Man_Fe_out', 'Man_Mn_out', 'Man_Zn_out', 'Man_MicMin_out',
            'Man_Min_out_g', 'Man_Wa_out', 'ManWa_Milk', "VolSlds2_Milk"
        ]
        urinary_variables = [
            'Ur_Nout_g', 'Ur_DEout', 'Ur_Nend_g', 'Ur_NPend_g', 'Ur_MPendUse_g',
            'Ur_Nend_Urea_g', 'Ur_Nend_Creatn_g', 'Ur_Nend_Creat_g',
            'Ur_Nend_PD_g', 'Ur_NPend_3MH_g', 'Ur_Nend_3MH_g', 'Ur_Nend_sum_g',
            'Ur_Nend_Hipp_g', 'Ur_NPend', 'Ur_MPend', 'Ur_EAAend_g',
            'Ur_AAEnd_g', 'Ur_AAEnd_AbsAA', 'Ur_EAAEnd_g', "Ur_Nout_DigNIn",
            "Ur_Nout_CPcatab", "UrDE_DMIn", "UrDE_GEIn", "UrDE_DEIn"
        ]
        gaseous_variables = ['CH4out_g', 'CH4out_L', 'CH4g_Milk', 'CH4L_Milk']
        scurf_variables = [
            'Scrf_CP_g', 'Scrf_NP_g', 'Scrf_MPUse_g_Trg', 'Scrf_NP', 'Scrf_N_g',
            'Scrf_AA_g', 'ScrfAA_AbsAA', 'Scrf_MPUse_g'
        ]
        # Store variables
        self.__populate_category('Excretion', group_names, fecal_variables,
                                 urinary_variables, gaseous_variables,
                                 scurf_variables)

    def __sort_Digestibility(self) -> None:
        """
        Sort and store specific variables related to digestability in the Digestability category.
        """
        # Name digestability groups
        group_names = ['rumen', 'TT']
        # Lists of variables to store
        rumen_variables = ['Rum_dcNDF', 'Rum_dcSt']
        TT_variables = []
        # Store variables
        self.__populate_category('Digestibility', group_names, rumen_variables,
                                 TT_variables)

    def __sort_Efficiencies(self) -> None:
        """
        Sort and store specific variables related to conversion efficiencies in the Efficiencies category.
        """
        # Name digestability groups
        group_names = ['energy', 'protein', 'mineral']
        # Lists of variables to store
        energy_variables = ['Kr_ME_RE']
        protein_variables = [
            'Kg_MP_NP_Trg', 'AnNPxEAA_AbsEAA', 'AnNPxEAAUser_AbsEAA', 
            "Km_MP_NP_Trg"
        ]
        mineral_variables = [
            'Dt_acCa', 'Dt_acP', 'Dt_acNa', 'Dt_acMg', 'Dt_acK', 'Dt_acCl',
            'Dt_acCo', 'Dt_acCu', 'Dt_acFe', 'Dt_acMn', 'Dt_acZn',
            'CaProd_CaIn', 'PProd_PIn', 'MgProd_MgIn', 'KProd_KIn',
            'NaProd_NaIn', 'ClProd_ClIn', 'CuProd_CuIn', 'FeProd_FeIn',
            'MnProd_MnIn', 'ZnProd_ZnIn', 'CaProd_CaAbs', 'PProd_PAbs',
            'MgProd_MgAbs', 'KProd_KAbs', 'NaProd_NaAbs', 'ClProd_ClAbs',
            'CuProd_CuAbs', 'FeProd_FeAbs', 'MnProd_MnAbs', 'ZnProd_ZnAbs'
        ]
        # Store variables
        self.__populate_category('Efficiencies', group_names, energy_variables,
                                 protein_variables, mineral_variables)

    def __sort_Miscellaneous(self) -> None:
        """
        Sort and store specific miscellaneous variables that need a final location in the Miscellaneous category.
        """
        # These variables need to be given a storage location
        group_names = ['misc']
        # Lists of variables to store
        misc_variables = [
            'Kb_LateGest_DMIn', 'An_PrePartWklim', 'An_PrePartWkDurat',
            'An_DMIn_BW', 'f_mPrt_max', 'mPrt_k_EAA2', 'An_REgain_Calf',
            'An_LactDay_MlkPred', 'An_DCADmeq', 'Dt_DMIn_BW', 'Dt_DMIn_MBW',
            'An_RDPbal_g', 'Trg_EAAUse_g', 'Trg_AbsEAA_g', "An_Grazing", "En_OM"
        ]
        # Store variables
        self.__populate_category('Miscellaneous', group_names, misc_variables)   

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
    