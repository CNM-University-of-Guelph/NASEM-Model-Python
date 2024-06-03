import re

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

    Example:
        # Create an instance of ModelOutput
        model_output = ModelOutput(locals_input=my_locals_input_dict)

        # Retrieve a specific group of variables
        requirements_group = model_output.get_value('Requirements')
    """

    def __init__(self, locals_input):
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

    def _repr_html_(self):
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
            <p>The following list shows which dictionaries are within each category:</p>
            <ul>
        """

        categories = self.__categories_dict()
        # Adding categories and keys to the accordion content as bullet points
        for category, keys in categories.items():
            accordion_html += f"<li><b>{category}:</b> {', '.join(keys.keys())}</li>"

        accordion_html += """
            </ul>
            <div>
                <p>These outputs can be accessed by name, e.g., <code>output.Production['milk']['Mlk_Prod']</code>.</p>
                <p>There is also a <code>.search()</code> method which takes a string and will return a dataframe of all outputs with that string (case insensitive), e.g., <code>output.search('Mlk')</code>.</p>
                <p>An individual output can be retrieved directly by providing its exact name to the <code>.get_value()</code> method, e.g., <code>output.get_value('Mlk_Prod')</code>.</p>
            </div>
        </details>
        """

        # Combining everything into the final HTML
        # {summary_sentence}
        # {df_diet_html}
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

    def __str__(self):
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

    def __categories_dict(self):
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

    def __snapshot_data(self):
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
            elif isinstance(raw_value, (np.ndarray)) and raw_value.size == 1:
                # This is required for any numbers handled by np.where() that 
                # return arrays instead of floats - needs cleaning up
                value = round(float(raw_value), 3)
            else:
                value = raw_value

            snapshot_data.append({'Description': description, 'Value': value})

        return snapshot_data

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
                    getattr(
                        self,
                        category_name)[name][var] = self.locals_input.pop(var)

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
        Add to dev output for easier development. Not included in search or get_value methods.
        """
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

    def __sort_Input(self):
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

    def __sort_Intakes(self):
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

    def __sort_Requirements(self):
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
        for abbreviation, variable_list in zip(mineral_abbreviations,
                                               mineral_variable_lists):
            mineral_requirements[abbreviation] = {}  
            # Initialize the dictionary for the current mineral
            for variable in variable_list:
                if variable in self.locals_input:
                    mineral_requirements[abbreviation][
                        variable] = self.locals_input.pop(variable)
        self.Requirements['mineral_requirements'] = mineral_requirements

    def __sort_Production(self):
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
            'MlkNP_AbsOthAA'
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
            'Body_Fatgain_NEalow', 'Body_NPgain_NEalow', 'An_Days_BCSdelta1'
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

    def __sort_Excretion(self):
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
            'Man_Min_out_g', 'Man_Wa_out', 'ManWa_Milk'
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
        self.__populate_category('Digestibility', group_names, rumen_variables,
                                 TT_variables)

    def __sort_Efficiencies(self):
        """
        Sort and store specific variables related to conversion efficiencies in the Efficiencies category.
        """
        # Name digestability groups
        group_names = ['energy', 'protein', 'mineral']
        # Lists of variables to store
        energy_variables = ['Kr_ME_RE']
        protein_variables = [
            'Kg_MP_NP_Trg', 'AnNPxEAA_AbsEAA', 'AnNPxEAAUser_AbsEAA'
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

    def __sort_Miscellaneous(self):
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
            'An_RDPbal_g', 'Trg_EAAUse_g', 'Trg_AbsEAA_g'
        ]
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

        # Return None if not found
        return None

    def search(self, search_string, dictionaries_to_search=None):
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

        def recursive_search(d, path=''):
            for key, value in d.items():
                full_key = path + key
                if ((re.search(search_string, str(full_key))) and 
                    full_key not in visited_keys
                    ):
                    result[full_key] = value
                    visited_keys.add(full_key)
                if isinstance(value, dict):
                    recursive_search(value, full_key + '.')
                elif isinstance(value, pd.DataFrame):
                    matching_columns = [
                        col for col in value.columns
                        if re.search(search_string, col)
                    ]
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
                table_rows.extend(
                    [extract_dataframe_and_column(key, col) for col in value])
            elif isinstance(value, list):
                value_display = 'list'
            else:
                value_display = value
            # Add the current row to the list
            if not (isinstance(value, list) and key.endswith('_columns')):
                table_rows.append({
                    'Name': variable_name,
                    'Value': value_display
                })

        output_table = pd.DataFrame(table_rows)
        return output_table

    def export_to_dict(self):
        data_dict = {}
        special_keys = {
            'dataframe': [],
            'series': [],
            'ndarray': [],
            'dict': [],
            'list': []
        }

        def recursive_extract(value, parent_key=''):
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

        def categorize_key(key, value):
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