import pandas as pd
from nasem_dairy.ration_balancer.ModelOutput import ModelOutput
from nasem_dairy.ration_balancer.ration_balancer_functions import get_feed_rows_feedlibrary #, check_coeffs_in_coeff_dict, read_csv_input, read_infusion_input
from nasem_dairy.ration_balancer.default_values_dictionaries import coeff_dict, infusion_dict, MP_NP_efficiency_dict
from nasem_dairy.NASEM_equations.DMI_equations import (
    calculate_Kb_LateGest_DMIn,
    calculate_An_PrePartWklim,
    calculate_Dt_DMIn_Heif_LateGestInd,
    calculate_Dt_DMIn_Heif_LateGestPen,
    calculate_Dt_NDFdev_DMI,
    calculate_Dt_DMIn_Heif_NRCa,
    calculate_Dt_DMIn_Heif_NRCad,
    calculate_Dt_DMIn_Heif_H1,
    calculate_Dt_DMIn_Heif_H2,
    calculate_Dt_DMIn_Heif_HJ1,
    calculate_Dt_DMIn_Heif_HJ2,
    calculate_Dt_DMIn_Lact1,
    calculate_Dt_DMIn_BW_LateGest_i,
    calculate_Dt_DMIn_BW_LateGest_p,
    calculate_Dt_DMIn_DryCow1_FarOff,
    calculate_Dt_DMIn_DryCow1_Close,
    calculate_Dt_DMIn_DryCow2,
    calculate_Dt_DMIn_Calf1
)

from nasem_dairy.NASEM_equations.milk_equations import (
    calculate_Trg_NEmilk_Milk,
    calculate_Mlk_NP_g,
    calculate_Mlk_CP_g,
    calculate_An_LactDay_MlkPred,
    calculate_Trg_Mlk_Fat,
    calculate_Trg_Mlk_Fat_g,
    calculate_Mlk_Fatemp_g,
    calculate_Mlk_Fat_g,
    calculate_Mlk_Fat,
    calculate_Mlk_NP,
    calculate_Mlk_Prod_comp,
    calculate_An_MPavail_Milk_Trg,
    calculate_Mlk_NP_MPalow_Trg_g,
    calculate_Mlk_Prod_MPalow,
    calculate_An_MEavail_Milk,
    calculate_Mlk_Prod_NEalow,
    calculate_MlkNP_Milk,
    calculate_Mlk_Prod,
    calculate_MlkFat_Milk,
    calculate_MlkNE_Milk,
    calculate_Mlk_NEout,
    calculate_Mlk_MEout
)

from nasem_dairy.NASEM_equations.nutrient_intakes import (
    calculate_diet_info,
    calculate_diet_data_initial,
    calculate_diet_data_complete,
    calculate_TT_dcAnSt,
    calculate_TT_dcrOMa,
    calculate_TT_dcrOMt,
)

from nasem_dairy.NASEM_equations.rumen_equations import (
    calculate_Rum_dcNDF,
    calculate_Rum_dcSt,
    calculate_Rum_DigNDFIn,
    calculate_Rum_DigStIn,
    calculate_Rum_DigNDFnfIn,
    calculate_Du_StPas,
    calculate_Du_NDFPas
)

from nasem_dairy.NASEM_equations.microbial_protein_equations import (
    calculate_RDPIn_MiNmax,
    calculate_MiN_Vm,
    calculate_Du_MiN_NRC2021_g,
    calculate_Du_MiN_VTln_g,
    calculate_Du_MiN_VTnln_g,
    calculate_Du_MiCP,
    calculate_Du_idMiCP_g,
    calculate_Du_idMiCP,
    calculate_Du_idMiTP_g,
    calculate_Du_idMiTP,
    calculate_Du_idMiTP,
    calculate_Du_MiTP,
    calculate_Du_EndCP_g,
    calculate_Du_EndN_g,
    calculate_Du_EndCP,
    calculate_Du_EndN,
    calculate_Du_NAN_g,
    calculate_Du_NANMN_g,
    calculate_Du_MiN_NRC2001_g
)

from nasem_dairy.NASEM_equations.protein_equations import (
    calculate_f_mPrt_max, 
    calculate_Du_MiCP_g, 
    calculate_Du_MiTP_g,
    calculate_Scrf_CP_g,
    calculate_Scrf_NP_g,
    calculate_Scrf_MPUse_g_Trg
)

from nasem_dairy.NASEM_equations.amino_acid_equations import (
    calculate_Du_AAMic,
    calculate_Du_IdAAMic,
    calculate_Abs_AA_g,
    calculate_mPrtmx_AA,
    calculate_mPrtmx_AA2,
    calculate_AA_mPrtmx,
    calculate_mPrt_AA_01,
    calculate_mPrt_k_AA,
    calculate_Abs_EAA_g,
    calculate_Abs_neAA_g,
    calculate_Abs_OthAA_g,
    calculate_Abs_EAA2b_g,
    calculate_mPrt_k_EAA2,
    calculate_Du_AAEndP,
    calculate_Du_AA,
    calculate_DuAA_AArg,
    calculate_Du_AA24h,
    calculate_IdAA_DtAA
)

from nasem_dairy.NASEM_equations.infusion_equations import calculate_infusion_data

from nasem_dairy.NASEM_equations.animal_equations import (
    calculate_An_DMIn_BW,
    calculate_An_REgain_Calf,
    calculate_An_MEIn_approx,
    calculate_An_MEIn,
    calculate_An_NEIn,
    calculate_An_NE,
    calculate_An_data_initial,
    calculate_An_data_complete,
    calculate_An_MPIn,
    calculate_An_MPIn_g,
    calculate_An_RDPbal_g,
    calculate_An_MP_CP,
    calculate_An_MP
)

from nasem_dairy.NASEM_equations.gestation_equations import (
    calculate_Uter_Wtpart,
    calculate_Uter_Wt,
    calculate_GrUter_Wtpart,
    calculate_GrUter_Wt,
    calculate_Uter_BWgain,
    calculate_GrUter_BWgain,
    calculate_Gest_NCPgain_g,
    calculate_Gest_NPgain_g,
    calculate_Gest_NPuse_g,
    calculate_Gest_CPuse_g,
    calculate_An_PostPartDay
)

from nasem_dairy.NASEM_equations.fecal_equations import (
    calculate_Fe_rOMend,
    calculate_Fe_RUP,
    calculate_Fe_RumMiCP,
    calculate_Fe_CPend_g,
    calculate_Fe_CPend,
    calculate_Fe_CP,
    calculate_Fe_NPend,
    calculate_Fe_NPend_g,
    calculate_Fe_MPendUse_g_Trg,
    calculate_Fe_rOM,
    calculate_Fe_St,
    calculate_Fe_NDF,
    calculate_Fe_NDFnf,   
    calculate_Fe_Nend,
    calculate_Fe_RDPend,
    calculate_Fe_RUPend,
    calculate_Fe_MiTP,
    calculate_Fe_InfCP,
    calculate_Fe_TP,
    calculate_Fe_N,
    calculate_Fe_N_g,
    calculate_Fe_FA,
    calculate_Fe_OM,
    calculate_Fe_OM_end,
    calculate_Fe_DEMiCPend,
    calculate_Fe_DERDPend,
    calculate_Fe_DERUPend,
    calculate_Fe_DEout,
    calculate_Fe_DE_GE,
    calculate_Fe_DE
)

from nasem_dairy.NASEM_equations.body_composition_equations import (
    calculate_CPGain_FrmGain,
    calculate_Frm_Gain,
    calculate_Frm_Gain_empty,
    calculate_NPGain_FrmGain,
    calculate_Rsrv_Gain,
    calculate_Rsrv_Gain_empty,
    calculate_Body_Gain_empty,
    calculate_Frm_NPgain,
    calculate_NPGain_RsrvGain,
    calculate_Rsrv_NPgain,
    calculate_Body_NPgain,
    calculate_Body_CPgain,
    calculate_Body_CPgain_g,
    calculate_Rsrv_Gain,
    calculate_Rsrv_Gain_empty,
    calculate_Rsrv_Fatgain,
    calculate_CPGain_FrmGain,
    calculate_Rsrv_CPgain,
    calculate_FatGain_FrmGain,
    calculate_Frm_Gain,
    calculate_Frm_Gain_empty,
    calculate_Frm_Fatgain,
    calculate_NPGain_FrmGain,
    calculate_Frm_NPgain,
    calculate_Frm_CPgain,
    calculate_Body_NPgain_g,
    calculate_An_BWmature_empty,
    calculate_Body_Gain,
    calculate_Trg_BWgain,
    calculate_Trg_BWgain_g
)

from nasem_dairy.NASEM_equations.urine_equations import (
    calculate_Ur_Nout_g,
    calculate_Ur_DEout,
    calculate_Ur_Nend_g,
    calculate_Ur_NPend_g,
    calculate_Ur_MPendUse_g
)

from nasem_dairy.NASEM_equations.energy_requirement_equations import (
    calculate_An_NEmUse_NS,
    calculate_An_NEm_Act_Graze,
    calculate_An_NEm_Act_Parlor,
    calculate_An_NEm_Act_Topo,
    calculate_An_NEmUse_Act,
    calculate_An_NEmUse,
    calculate_An_MEmUse,
    calculate_Rsrv_NEgain,
    calculate_Kr_ME_RE,
    calculate_Rsrv_MEgain,
    calculate_Frm_NEgain,
    calculate_Frm_MEgain,
    calculate_An_MEgain,
    calculate_Gest_REgain,
    calculate_Gest_MEuse,
    calculate_Trg_Mlk_NEout,
    calculate_Trg_Mlk_MEout,
    calculate_Trg_MEuse
)

from nasem_dairy.NASEM_equations.protein_requirement_equations import (
    calculate_An_MPm_g_Trg,
    calculate_Body_MPUse_g_Trg_initial,
    calculate_Gest_MPUse_g_Trg,
    calculate_Trg_Mlk_NP_g,
    calculate_Mlk_MPUse_g_Trg,
    calculate_An_MPuse_g_Trg_initial,
    calculate_Min_MPuse_g,
    calculate_Diff_MPuse_g,
    calculate_Frm_MPUse_g_Trg,
    calculate_Frm_NPgain_g,
    calculate_Kg_MP_NP_Trg,
    calculate_Rsrv_NPgain_g,
    calculate_Rsrv_MPUse_g_Trg,
    calculate_Body_MPUse_g_Trg,
    calculate_An_MPuse_g_Trg
)

from nasem_dairy.NASEM_equations.micronutrient_requirement_equations import (
    calculate_Ca_Mlk,
    calculate_Fe_Ca_m,
    calculate_An_Ca_g,
    calculate_An_Ca_y,
    calculate_An_Ca_l,
    calculate_An_Ca_Clf,
    calculate_An_Ca_req,
    calculate_An_Ca_bal,
    calculate_An_Ca_prod,
    calculate_Ur_P_m,
    calculate_Fe_P_m,
    calculate_An_P_m,
    calculate_An_P_g,
    calculate_An_P_y,
    calculate_An_P_l,
    calculate_An_P_Clf,
    calculate_An_P_req,
    calculate_An_P_bal,
    calculate_Fe_P_g,
    calculate_An_P_prod,
    calculate_An_Mg_Clf,
    calculate_Ur_Mg_m,
    calculate_Fe_Mg_m,
    calculate_An_Mg_m,
    calculate_An_Mg_g,
    calculate_An_Mg_y,
    calculate_An_Mg_l,
    calculate_An_Mg_req,
    calculate_An_Mg_bal,
    calculate_An_Mg_prod,
    calculate_An_Na_Clf,
    calculate_Fe_Na_m,
    calculate_An_Na_g,
    calculate_An_Na_y,
    calculate_An_Na_l,
    calculate_An_Na_req,
    calculate_An_Na_bal,
    calculate_An_Na_prod,
    calculate_An_Cl_Clf,
    calculate_Fe_Cl_m,
    calculate_An_Cl_g,
    calculate_An_Cl_y,
    calculate_An_Cl_l,
    calculate_An_Cl_req,
    calculate_An_Cl_bal,
    calculate_An_Cl_prod,
    calculate_An_K_Clf,
    calculate_Ur_K_m,
    calculate_Fe_K_m,
    calculate_An_K_m,
    calculate_An_K_g,
    calculate_An_K_y,
    calculate_An_K_l,
    calculate_An_K_req,
    calculate_An_K_bal,
    calculate_An_K_prod,
    calculate_An_S_req,
    calculate_An_S_bal,
    calculate_An_Co_req,
    calculate_An_Co_bal,
    calculate_An_Cu_Clf,
    calculate_An_Cu_m,
    calculate_An_Cu_g,
    calculate_An_Cu_y,
    calculate_An_Cu_l,
    calculate_An_Cu_req,
    calculate_An_Cu_bal,
    calculate_An_Cu_prod,
    calculate_An_I_req,
    calculate_An_I_bal,
    calculate_An_Fe_Clf,
    calculate_An_Fe_g,
    calculate_An_Fe_y,
    calculate_An_Fe_l,
    calculate_An_Fe_req,
    calculate_An_Fe_bal,
    calculate_An_Fe_prod,
    calculate_An_Mn_Clf,
    calculate_An_Mn_m,
    calculate_An_Mn_g,
    calculate_An_Mn_y,
    calculate_An_Mn_l,
    calculate_An_Mn_req,
    calculate_An_Mn_bal,
    calculate_An_Mn_prod,
    calculate_An_Se_req,
    calculate_An_Se_bal,
    calculate_An_Zn_Clf,
    calculate_An_Zn_m,
    calculate_An_Zn_g,
    calculate_An_Zn_y,
    calculate_An_Zn_l,
    calculate_An_Zn_req,
    calculate_An_Zn_bal,
    calculate_An_Zn_prod,
    calculate_An_DCADmeq
)

from nasem_dairy.NASEM_equations.coefficient_adjustment import adjust_LCT
from nasem_dairy.NASEM_equations.unused_equations import (
    calculate_Dt_DMIn_BW,
    calculate_Dt_DMIn_MBW
)

from nasem_dairy.NASEM_equations.water_equations import calculate_An_WaIn


def execute_model(user_diet: pd.DataFrame, 
                  animal_input: dict, 
                  equation_selection: dict, 
                  feed_library_df: pd.DataFrame, 
                  coeff_dict: dict = coeff_dict,
                  infusion_input: dict = infusion_dict,
                  MP_NP_efficiency_input: dict = MP_NP_efficiency_dict
                  ):
    """
    Run the NASEM (National Academies of Sciences, Engineering, and Medicine) Nutrient Requirements of Dairy Cattle model.

    Parameters
    ----------
    user_diet : pd.DataFrame
        DataFrame containing user-defined diet composition in kg of feed ingredient. Expects two columns, 'Feedstuff' as a string with the name from the feed library and 'kg_user' as a float with the kg of the ingredient to feed.
    animal_input : dict
        Dictionary containing animal-specific input values.
    equation_selection : dict
        Dictionary containing equation selection criteria.
    feed_library_df : pd.DataFrame
        DataFrame containing the feed library data.
    coeff_dict : dict, optional
        Dictionary containing coefficients for the model, by default `nd.coeff_dict`.
    infusion_input : dict, optional
        Dictionary containing infusion input data, by default `nd.infusion_dict`.
    MP_NP_efficiency_input : dict, optional
        Dictionary containing amino acid conversion efficiencies, by default `nd.MP_NP_efficiency_dict`.

    Returns
    -------
    Multiple
        Currently returns animal_input, diet_info, equation_selection, diet_data, AA_values, infusion_data, An_data, model_out_dict
        To be updated

    Notes
    -----
    - user_diet, animal_input an equation_selection can be generated from a CSV file using nd.read_csv_input
    - The default feed_library_df can be read from NASEM_feed_library.csv
    
    Examples
    --------
    Run the NASEM dairy model with user-defined inputs:

    ```python
    import nasem_dairy as nd
    nd.dev_run_NASEM_model(
        user_diet=user_diet_df,
        animal_input=animal_input_dict,
        equation_selection=equation_selection_dict,
        feed_library_df=feed_library_df
    )
    ```
    """
    ########################################
    # Step 1: Read User Input
    ########################################
    # prevent mutable changes outside of expected scope (especially for Shiny):
    user_diet = user_diet.copy()
    animal_input = animal_input.copy()

    # retrieve user's feeds from feed library
    feed_data = get_feed_rows_feedlibrary(
        feeds_to_get=user_diet['Feedstuff'].tolist(), 
        feed_lib_df=feed_library_df)

    # Calculate Fd_DMInp (percentage inclusion as sum of kg_user column)
    # Then, use the percentages to calculate the DMIn for each ingredient, and merge feed data on
    diet_info_initial = (
        user_diet
        .assign(
            Fd_DMInp = lambda df: df['kg_user'] / df['kg_user'].sum(),
            Fd_DMIn = lambda df: df['Fd_DMInp'] * animal_input['DMI']
            )
        .merge(feed_data, how='left', on='Feedstuff')
    )
    
    # Add Fd_DNDF48 column, need to add to the database
    # diet_info_initial['Fd_DNDF48'] = 0

    # Calculate additional physiology values
    animal_input['An_PrePartDay'] = animal_input['An_GestDay'] - animal_input['An_GestLength']
    animal_input['An_PrePartWk'] = animal_input['An_PrePartDay'] / 7

    animal_input['An_PostPartDay'] = calculate_An_PostPartDay(animal_input['An_LactDay'])

    animal_input['An_PostPartDay'] = calculate_An_PostPartDay(animal_input['An_LactDay'])



    # Check equation_selection to make sure they are integers.
    # This is especially important for Shiny, which may return strings
    # It's important they are correct for if statements below.
    equation_selection_in = equation_selection.copy()
    equation_selection = {}

    for key, value in equation_selection_in.items():
        try:
            num_value = int(value)
            equation_selection[key] = num_value
        except ValueError:
            print(f"Unable to convert '{value}' to an integer for key '{key}'")
    
    del(equation_selection_in)
    Scrf_CP_g = calculate_Scrf_CP_g(animal_input['An_StatePhys'],
                                       animal_input['An_BW'])
    CPGain_FrmGain = calculate_CPGain_FrmGain(animal_input['An_BW'], 
                                                 animal_input['An_BW_mature'])
    NPGain_FrmGain = calculate_NPGain_FrmGain(CPGain_FrmGain,
                                                 coeff_dict)
    Frm_Gain = calculate_Frm_Gain(animal_input['Trg_FrmGain'])
    Rsrv_Gain = calculate_Rsrv_Gain(animal_input['Trg_RsrvGain'])
    Rsrv_Gain_empty = calculate_Rsrv_Gain_empty(Rsrv_Gain)
    NPGain_RsrvGain = calculate_NPGain_RsrvGain(coeff_dict)
    Rsrv_NPgain = calculate_Rsrv_NPgain(NPGain_RsrvGain,
                                           Rsrv_Gain_empty)

    coeff_dict['LCT'] = adjust_LCT(animal_input['An_AgeDay'])
    animal_input['Trg_BWgain'] = calculate_Trg_BWgain(animal_input['Trg_FrmGain'],
                                      animal_input['Trg_RsrvGain'])

    animal_input['Trg_BWgain_g'] = calculate_Trg_BWgain_g(animal_input['Trg_BWgain'])

    # if animal_input['An_StatePhys'] != 'Lactating Cow':
    #     animal_input['Trg_MilkProd'] = None

    ########################################
    # Step 2: DMI Equations
    ########################################
    # pre calculations for DMI:
    ###########################
    # Calculate Target milk net energy
    Trg_NEmilk_Milk = calculate_Trg_NEmilk_Milk(animal_input['Trg_MilkTPp'],
                                                animal_input['Trg_MilkFatp'],
                                                animal_input['Trg_MilkLacp'])
    
    # # Need to precalculate Dt_NDF for DMI predicitons, this will be based on the user entered DMI (animal_input['DMI])
    Dt_NDF = (diet_info_initial['Fd_NDF'] * diet_info_initial['Fd_DMInp']).sum()
    # Predict DMI for heifers
    Kb_LateGest_DMIn = calculate_Kb_LateGest_DMIn(Dt_NDF)
    An_PrePartWklim = calculate_An_PrePartWklim(animal_input['An_PrePartWk'])
    An_PrePartWkDurat = An_PrePartWklim * 2


    if equation_selection['DMIn_eqn'] == 0:
        # print('Using user input DMI')
        pass

    # Predict DMI for lactating cow
    elif equation_selection['DMIn_eqn'] == 8:
        # print("using DMIn_eqn: 8")
        animal_input['DMI'] = calculate_Dt_DMIn_Lact1(
            animal_input['Trg_MilkProd'],
            animal_input['An_BW'],
            animal_input['An_BCS'],
            animal_input['An_LactDay'],
            animal_input['An_Parity_rl'],
            Trg_NEmilk_Milk
            )

    # Individual Heifer DMI Predictions
    elif equation_selection['DMIn_eqn'] in [2, 3, 4, 5, 6, 7]:
        Dt_DMIn_BW_LateGest_i = calculate_Dt_DMIn_BW_LateGest_i(An_PrePartWklim, Kb_LateGest_DMIn, coeff_dict)

        # All the individual DMI predictions require this value
        Dt_DMIn_Heif_LateGestInd = calculate_Dt_DMIn_Heif_LateGestInd(animal_input['An_BW'], Dt_DMIn_BW_LateGest_i)

        if equation_selection['DMIn_eqn'] == 2:
            if animal_input['An_PrePartWk'] > An_PrePartWkDurat:
                animal_input['DMI'] = min(
                    calculate_Dt_DMIn_Heif_NRCa(animal_input['An_BW'], animal_input['An_BW_mature']), 
                    Dt_DMIn_Heif_LateGestInd
                    )
            else:
                animal_input['DMI'] = calculate_Dt_DMIn_Heif_NRCa(animal_input['An_BW'], animal_input['An_BW_mature'])

        if equation_selection['DMIn_eqn'] == 3:
            if animal_input['An_PrePartWk'] > An_PrePartWkDurat:
                animal_input['DMI'] = min(
                    calculate_Dt_DMIn_Heif_NRCad(animal_input['An_BW'], animal_input['An_BW_mature'], Dt_NDF),
                    Dt_DMIn_Heif_LateGestInd
                    )
            else:
                animal_input['DMI'] = calculate_Dt_DMIn_Heif_NRCad(animal_input['An_BW'], animal_input['An_BW_mature'], Dt_NDF)

        if equation_selection['DMIn_eqn'] == 4:
            if animal_input['An_PrePartWk'] > An_PrePartWkDurat:
                animal_input['DMI'] = min(
                    calculate_Dt_DMIn_Heif_H1(animal_input['An_BW']),
                    Dt_DMIn_Heif_LateGestInd
                    )
            else:
                animal_input['DMI'] = calculate_Dt_DMIn_Heif_H1(animal_input['An_BW'])

        if equation_selection['DMIn_eqn'] == 5:
            Dt_NDFdev_DMI = calculate_Dt_NDFdev_DMI(animal_input['An_BW'], Dt_NDF)

            if animal_input['An_PrePartWk'] > An_PrePartWkDurat:
                animal_input['DMI'] = min(
                    calculate_Dt_DMIn_Heif_H2(animal_input['An_BW'], Dt_NDFdev_DMI),
                    Dt_DMIn_Heif_LateGestInd
                    )
            else:
                animal_input['DMI'] = calculate_Dt_DMIn_Heif_H2(animal_input['An_BW'],Dt_NDFdev_DMI)

        if equation_selection['DMIn_eqn'] == 6:
            if animal_input['An_PrePartWk'] > An_PrePartWkDurat:
                animal_input['DMI'] = min(
                    calculate_Dt_DMIn_Heif_HJ1(animal_input['An_BW']),
                    Dt_DMIn_Heif_LateGestInd
                    )
            else:
                animal_input['DMI'] = calculate_Dt_DMIn_Heif_HJ1(animal_input['An_BW'])

        if equation_selection['DMIn_eqn'] == 7:
            Dt_NDFdev_DMI = calculate_Dt_NDFdev_DMI(animal_input['An_BW'],Dt_NDF)

            if animal_input['An_PrePartWk'] > An_PrePartWkDurat:
                animal_input['DMI'] = min(
                    calculate_Dt_DMIn_Heif_HJ2(animal_input['An_BW'],Dt_NDFdev_DMI),
                    Dt_DMIn_Heif_LateGestInd
                    )
            else:
                animal_input['DMI'] = calculate_Dt_DMIn_Heif_HJ2(animal_input['An_BW'], Dt_NDFdev_DMI)

    # Group Heifer DMI Predictions
    elif equation_selection['DMIn_eqn'] in [12, 13, 14, 15, 16, 17]:
        Dt_DMIn_BW_LateGest_p = calculate_Dt_DMIn_BW_LateGest_p(An_PrePartWkDurat, Kb_LateGest_DMIn, coeff_dict)

        # All group DMI predicitons require this value
        Dt_DMIn_Heif_LateGestPen = calculate_Dt_DMIn_Heif_LateGestPen(animal_input['An_BW'], Dt_DMIn_BW_LateGest_p)

        if equation_selection['DMIn_eqn'] == 12:
            if animal_input['An_PrePartWk'] > An_PrePartWkDurat:
                animal_input['DMI'] = min(
                    calculate_Dt_DMIn_Heif_NRCa(animal_input['An_BW'], animal_input['An_BW_mature']),
                    Dt_DMIn_Heif_LateGestPen
                    )
            else:
                animal_input['DMI'] = calculate_Dt_DMIn_Heif_NRCa(animal_input['An_BW'], animal_input['An_BW_mature'])

        if equation_selection['DMIn_eqn'] == 13:
            if animal_input['An_PrePartWk'] > An_PrePartWkDurat:
                animal_input['DMI'] = min(
                    calculate_Dt_DMIn_Heif_NRCad(animal_input['An_BW'], animal_input['An_BW_mature'], Dt_NDF),
                    Dt_DMIn_Heif_LateGestPen
                    )
            else:
                animal_input['DMI'] = calculate_Dt_DMIn_Heif_NRCad(animal_input['An_BW'], animal_input['An_BW_mature'], Dt_NDF)

        if equation_selection['DMIn_eqn'] == 14:
            if animal_input['An_PrePartWk'] > An_PrePartWkDurat:
                animal_input['DMI'] = min(
                    calculate_Dt_DMIn_Heif_H1(animal_input['An_BW']), 
                    Dt_DMIn_Heif_LateGestPen
                    )
            else:
                animal_input['DMI'] = calculate_Dt_DMIn_Heif_H1(animal_input['An_BW'])

        if equation_selection['DMIn_eqn'] == 15:
            Dt_NDFdev_DMI = calculate_Dt_NDFdev_DMI(animal_input['An_BW'],Dt_NDF)

            if animal_input['An_PrePartWk'] > An_PrePartWkDurat:
                animal_input['DMI'] = min(
                    calculate_Dt_DMIn_Heif_H2(animal_input['An_BW'], Dt_NDFdev_DMI),
                    Dt_DMIn_Heif_LateGestPen
                    )
            else:
                animal_input['DMI'] = calculate_Dt_DMIn_Heif_H2(animal_input['An_BW'],Dt_NDFdev_DMI)

        if equation_selection['DMIn_eqn'] == 16:
            if animal_input['An_PrePartWk'] > An_PrePartWkDurat:
                animal_input['DMI'] = min(
                    calculate_Dt_DMIn_Heif_HJ1(animal_input['An_BW']), 
                    Dt_DMIn_Heif_LateGestPen
                    )
            else:
                animal_input['DMI'] = calculate_Dt_DMIn_Heif_HJ1(animal_input['An_BW'])

        if equation_selection['DMIn_eqn'] == 17:
            Dt_NDFdev_DMI = calculate_Dt_NDFdev_DMI(animal_input['An_BW'],Dt_NDF)

            if animal_input['An_PrePartWk'] > An_PrePartWkDurat:
                animal_input['DMI'] = min(
                    calculate_Dt_DMIn_Heif_HJ2(animal_input['An_BW'],Dt_NDFdev_DMI),
                    Dt_DMIn_Heif_LateGestPen
                    )
            else:
                animal_input['DMI'] = calculate_Dt_DMIn_Heif_HJ2(animal_input['An_BW'], Dt_NDFdev_DMI)

    elif equation_selection['DMIn_eqn'] == 10:
        Dt_DMIn_BW_LateGest_i = calculate_Dt_DMIn_BW_LateGest_i(An_PrePartWklim, Kb_LateGest_DMIn, coeff_dict)

        Dt_DMIn_BW_LateGest_p = calculate_Dt_DMIn_BW_LateGest_p(An_PrePartWkDurat, Kb_LateGest_DMIn, coeff_dict)

        if animal_input['An_PrePartWk'] > An_PrePartWkDurat:
            animal_input['DMI'] = min(
                calculate_Dt_DMIn_DryCow1_FarOff(animal_input['An_BW'], Dt_DMIn_BW_LateGest_i),
                calculate_Dt_DMIn_DryCow1_Close(animal_input['An_BW'], Dt_DMIn_BW_LateGest_p)
                )
        else:
            animal_input['DMI'] = calculate_Dt_DMIn_DryCow1_FarOff(animal_input['An_BW'], Dt_DMIn_BW_LateGest_i)

    elif equation_selection['DMIn_eqn'] == 11:
        animal_input['DMI'] = calculate_Dt_DMIn_DryCow2(animal_input['An_BW'], animal_input['An_GestDay'], animal_input['An_GestLength'])

    else:
        # It needs to catch all possible solutions, otherwise it's possible that it stays unchanged without warning
        print("DMIn_eqn uncaught - DMI not changed. equation_selection[DMIn_eqn]: " + str(equation_selection['DMIn_eqn']))

    # Calculated again as part of diet_data, value may change depending on DMIn_eqn selections
    del (Dt_NDF)

    ########################################
    # Step 3: Feed Based Calculations
    ########################################
    # Calculate An_DMIn_BW with the final DMI value; required for calculating diet_data_initial
    Dt_DMIn_BW = calculate_Dt_DMIn_BW(animal_input["DMI"],
                                      animal_input['An_BW'])
    Dt_DMIn_MBW = calculate_Dt_DMIn_MBW(animal_input['DMI'],
                                        animal_input['An_BW'])
    An_DMIn_BW = calculate_An_DMIn_BW(animal_input['An_BW'],
                                         animal_input['DMI'])
    Fe_rOMend = calculate_Fe_rOMend(animal_input['DMI'],
                                       coeff_dict)

    diet_info = calculate_diet_info(animal_input['DMI'],
                                       animal_input['An_StatePhys'],
                                       equation_selection['Use_DNDF_IV'],
                                       diet_info=diet_info_initial,
                                       coeff_dict=coeff_dict)
    # All equations in the f dataframe go into calculate_diet_info()
    # This includes micronutrient calculations which are no longer handled by seperate functions

    diet_data_initial = calculate_diet_data_initial(diet_info,
                                                       animal_input['DMI'],
                                                       animal_input['An_BW'],
                                                       animal_input['An_StatePhys'],
                                                       An_DMIn_BW,
                                                       animal_input['An_AgeDryFdStart'],
                                                       animal_input['Env_TempCurr'],
                                                       equation_selection['DMIn_eqn'],
                                                       equation_selection['Monensin_eqn'],
                                                       Fe_rOMend,
                                                       coeff_dict)
    # diet_data contains everything starting with "Dt_"

    ########################################
    # Step 4: Infusion Calculations
    ########################################

    infusion_data = calculate_infusion_data(infusion_input, animal_input['DMI'], coeff_dict)

########################################
# # Step 4.1: Uterine Bodyweight Calculations
# ########################################
    Uter_Wtpart = calculate_Uter_Wtpart(animal_input['Fet_BWbrth'], coeff_dict)
    Uter_Wt = calculate_Uter_Wt(animal_input['An_Parity_rl'],
                                   animal_input['An_AgeDay'],
                                   animal_input['An_LactDay'],
                                   animal_input['An_GestDay'],
                                   animal_input['An_GestLength'],
                                   Uter_Wtpart,
                                   coeff_dict)
                                   
    GrUter_Wtpart = calculate_GrUter_Wtpart(animal_input['Fet_BWbrth'], coeff_dict)
    GrUter_Wt = calculate_GrUter_Wt(animal_input['An_GestDay'],
                                       animal_input['An_GestLength'],
                                       Uter_Wt,
                                       GrUter_Wtpart,
                                       coeff_dict)

    Uter_BWgain = calculate_Uter_BWgain(animal_input['An_LactDay'],
                                           animal_input['An_GestDay'],
                                           animal_input['An_GestLength'],
                                           Uter_Wt,
                                           coeff_dict)

    GrUter_BWgain = calculate_GrUter_BWgain(animal_input['An_LactDay'],
                                               animal_input['An_GestDay'],
                                               animal_input['An_GestLength'],
                                               GrUter_Wt,
                                               Uter_BWgain,
                                               coeff_dict)

    ########################################
    # Step 5: Animal Level Calculations
    ########################################
    # Combine Diet and Infusion nutrient supplies
    An_data_initial = calculate_An_data_initial(animal_input,
                                                   diet_data_initial,
                                                   infusion_data,
                                                   equation_selection['Monensin_eqn'],
                                                   GrUter_Wt,
                                                   coeff_dict)

    ########################################
    # Step 6: Rumen Digestion Calculations
    ########################################
    # Rumen Digestability Coefficients
    Rum_dcNDF = calculate_Rum_dcNDF(animal_input['DMI'],
                                       diet_data_initial['Dt_NDFIn'],
                                       diet_data_initial['Dt_StIn'],
                                       diet_data_initial['Dt_CPIn'],
                                       diet_data_initial['Dt_ADFIn'],
                                       diet_data_initial['Dt_ForWet'])

    Rum_dcSt = calculate_Rum_dcSt(animal_input['DMI'],
                                     diet_data_initial['Dt_ForNDF'],
                                     diet_data_initial['Dt_StIn'],
                                     diet_data_initial['Dt_ForWet'])

    # Rumen Digestable Intakes
    Rum_DigNDFIn = calculate_Rum_DigNDFIn(Rum_dcNDF,
                                             diet_data_initial['Dt_NDFIn'])

    Rum_DigStIn = calculate_Rum_DigStIn(Rum_dcSt,
                                           diet_data_initial['Dt_StIn'])
    
    Rum_DigNDFnfIn = calculate_Rum_DigNDFnfIn(Rum_dcNDF,
                                              diet_data_initial['Dt_NDFnfIn'])
    
    # Duodenal Passage?
    Du_StPas = calculate_Du_StPas(diet_data_initial['Dt_StIn'],
                                  infusion_data['InfRum_StIn'],
                                  Rum_DigStIn)
    
    Du_NDFPas = calculate_Du_NDFPas(diet_data_initial['Dt_NDFIn'],
                                    infusion_data['Inf_NDFIn'],
                                    Rum_DigNDFIn)

    ########################################
    # Step 7: Microbial Protein Calculations
    ########################################
    if equation_selection['MiN_eqn'] == 1:
        RDPIn_MiNmax = calculate_RDPIn_MiNmax(animal_input['DMI'],
                                                 An_data_initial['An_RDP'],
                                                 An_data_initial['An_RDPIn'])
        
        MiN_Vm = calculate_MiN_Vm(RDPIn_MiNmax, coeff_dict)
        
        Du_MiN_g = calculate_Du_MiN_NRC2021_g(MiN_Vm,
                                                 Rum_DigNDFIn,
                                                 Rum_DigStIn,
                                                 An_data_initial['An_RDPIn_g'],
                                                 coeff_dict)
    elif equation_selection['MiN_eqn'] == 2:
        Du_MiN_g = calculate_Du_MiN_VTln_g(diet_data_initial['Dt_rOMIn'],
                                              diet_data_initial['Dt_ForNDFIn'],
                                              An_data_initial['An_RDPIn'],
                                              Rum_DigStIn,
                                              Rum_DigNDFIn,
                                              coeff_dict)
    elif equation_selection['MiN_eqn'] == 3:
        Du_MiN_g = calculate_Du_MiN_VTnln_g(An_data_initial['An_RDPIn'],
                                               Rum_DigNDFIn,
                                               Rum_DigStIn)
    else:
        raise ValueError(
            f"Invalid MiN_eqn: {equation_selection['MiN_eqn']} was entered. Must choose 1, 2 or 3.")

    Du_MiCP_g = calculate_Du_MiCP_g(Du_MiN_g)
    Du_MiTP_g = calculate_Du_MiTP_g(Du_MiCP_g, coeff_dict)
    Du_MiCP = calculate_Du_MiCP(Du_MiCP_g)
    Du_idMiCP_g = calculate_Du_idMiCP_g(Du_MiCP_g,
                                        coeff_dict)
    Du_idMiCP = calculate_Du_idMiCP(Du_idMiCP_g)
    Du_MiTP = calculate_Du_MiTP(Du_MiTP_g)
    Du_EndCP_g = calculate_Du_EndCP_g(animal_input['DMI'],
                                      infusion_data['InfRum_DMIn'])
    Du_EndN_g = calculate_Du_EndN_g(animal_input['DMI'],
                                    infusion_data['InfRum_DMIn'])
    Du_EndCP = calculate_Du_EndCP(Du_EndCP_g)
    Du_EndN = calculate_Du_EndN(Du_EndN_g)
    Du_NAN_g = calculate_Du_NAN_g(Du_MiN_g,
                                  An_data_initial['An_RUPIn'],
                                  Du_EndN_g)
    Du_NANMN_g = calculate_Du_NANMN_g(An_data_initial['An_RUPIn'],
                                      Du_EndN_g)
    An_RDPbal_g = calculate_An_RDPbal_g(An_data_initial['An_RDPIn_g'],
                                        Du_MiCP_g)
    Du_idMiTP_g = calculate_Du_idMiTP_g(Du_idMiCP_g,
                                           coeff_dict)
    Du_idMiTP = calculate_Du_idMiTP(Du_idMiTP_g)

    ########################################
    # Step 7.1: Fe_CP Calculation /  Finish Dt_ and An_ calculations
    ########################################
    # Required to finish Dt_ and An_ calculations
    Fe_RUP = calculate_Fe_RUP(An_data_initial['An_RUPIn'],
                                 infusion_data['InfSI_TPIn'],
                                 An_data_initial['An_idRUPIn'])
    Fe_RumMiCP = calculate_Fe_RumMiCP(Du_MiCP,
                                         Du_idMiCP)
    
    Fe_CPend_g = calculate_Fe_CPend_g(animal_input['An_StatePhys'],
                                         An_data_initial['An_DMIn'],
                                         An_data_initial['An_NDF'],
                                         animal_input['DMI'],
                                         diet_data_initial['Dt_DMIn_ClfLiq'],
                                         equation_selection["NonMilkCP_ClfLiq"])
    
    Fe_CPend = calculate_Fe_CPend(Fe_CPend_g)
    Fe_CP = calculate_Fe_CP(animal_input['An_StatePhys'],
                               diet_data_initial['Dt_CPIn_ClfLiq'],
                               diet_data_initial['Dt_dcCP_ClfDry'],
                               An_data_initial['An_CPIn'],
                               Fe_RUP,
                               Fe_RumMiCP,
                               Fe_CPend,
                               infusion_data['InfSI_NPNCPIn'],
                               coeff_dict)
    Fe_Nend = calculate_Fe_Nend(Fe_CPend)
    Fe_NPend = calculate_Fe_NPend(Fe_CPend)
    Fe_NPend_g = calculate_Fe_NPend_g(Fe_NPend)
    Fe_MPendUse_g_Trg = calculate_Fe_MPendUse_g_Trg(animal_input['An_StatePhys'],
                                                    Fe_CPend_g,
                                                    Fe_NPend_g,
                                                    coeff_dict)
    Fe_RDPend = calculate_Fe_RDPend(Fe_CPend,
                                    An_data_initial['An_RDPIn'],
                                    An_data_initial['An_CPIn'])
    Fe_RUPend = calculate_Fe_RUPend(Fe_CPend,
                                    An_data_initial['An_RUPIn'],
                                    An_data_initial['An_CPIn'])
    Fe_MiTP = calculate_Fe_MiTP(Du_MiTP,
                                Du_idMiTP)
    Fe_InfCP = calculate_Fe_InfCP(infusion_data['InfRum_RUPIn'],
                                  infusion_data['InfSI_CPIn'],
                                  infusion_data['InfRum_idRUPIn'],
                                  infusion_data['InfSI_idCPIn'])
    Fe_TP = calculate_Fe_TP(Fe_RUP,
                            Fe_MiTP,
                            Fe_NPend)
    Fe_N = calculate_Fe_N(Fe_CP)
    Fe_N_g = calculate_Fe_N_g(Fe_N)    
    Fe_FA = calculate_Fe_FA(diet_data_initial['Dt_FAIn'],
                            infusion_data['InfRum_FAIn'],
                            infusion_data['InfSI_FAIn'],
                            diet_data_initial['Dt_DigFAIn'],
                            infusion_data['Inf_DigFAIn'])
    Fe_OM_end = calculate_Fe_OM_end(Fe_rOMend,
                                    Fe_CPend)
    Fe_DEMiCPend = calculate_Fe_DEMiCPend(Fe_RumMiCP, coeff_dict)
    Fe_DERDPend = calculate_Fe_DERDPend(Fe_RDPend, coeff_dict)
    Fe_DERUPend = calculate_Fe_DERUPend(Fe_RUPend, coeff_dict)

########################################
# Step 7.2: Microbial Amino Acid Calculations
########################################
    AA_list = ['Arg', 'His', 'Ile', 'Leu',
               'Lys', 'Met', 'Phe', 'Thr', 'Trp', 'Val']
    AA_values = pd.DataFrame(index=AA_list)
    # Dataframe for storing all individual amino acid values
    AA_values['Du_AAMic'] = calculate_Du_AAMic(Du_MiTP_g,
                                                  AA_list,
                                                  coeff_dict)
    AA_values['Du_IdAAMic'] = calculate_Du_IdAAMic(AA_values['Du_AAMic'],
                                                      coeff_dict)
    AA_values['Du_AAEndP'] = calculate_Du_AAEndP(Du_EndCP_g, AA_list, coeff_dict)
    AA_values['Du_AA'] = calculate_Du_AA(diet_data_initial,
                                         infusion_data,
                                         AA_values['Du_AAMic'],
                                         AA_values['Du_AAEndP'],
                                         AA_list)
    Du_EAA_g = AA_values['Du_AA'].sum()
    AA_values['DuAA_DtAA'] = calculate_DuAA_AArg(AA_values['Du_AA'],
                                                 diet_data_initial,
                                                 AA_list)
    AA_values['Du_AA24h'] = calculate_Du_AA24h(AA_values['Du_AA'],
                                               AA_list,
                                               coeff_dict)
    # AA_values['IdAA_DtAA'] = calculate_IdAA_DtAA(diet_data_initial, An_data_initial, AA_list)

    ########################################
    # Step 7.3: Complete diet_data and An_data
    ########################################
    diet_data = calculate_diet_data_complete(diet_data_initial,
                                             animal_input['An_StatePhys'],
                                             animal_input['DMI'],
                                             Fe_CP,
                                             Fe_CPend,
                                             Fe_MiTP,
                                             Fe_NPend,
                                             equation_selection['Monensin_eqn'],
                                             AA_values['Du_IdAAMic'],
                                             Du_idMiTP,
                                             coeff_dict)
    
    An_data = calculate_An_data_complete(An_data_initial,
                                         diet_data,
                                         animal_input['An_StatePhys'],
                                         animal_input['An_BW'],
                                         animal_input['DMI'],
                                         Fe_CP,
                                         Fe_MiTP,
                                         Fe_NPend,
                                         Fe_DEMiCPend,
                                         Fe_DERDPend,
                                         Fe_DERUPend,
                                         Du_idMiCP,
                                         infusion_data,
                                         equation_selection['Monensin_eqn'],
                                         coeff_dict)

    # Calculate remaining digestability coefficients
    diet_data['TT_dcAnSt'] = calculate_TT_dcAnSt(An_data['An_DigStIn'],
                                                 diet_data['Dt_StIn'],
                                                 infusion_data['Inf_StIn'])
    diet_data['TT_dcrOMa'] = calculate_TT_dcrOMa(An_data['An_DigrOMaIn'],
                                                 diet_data['Dt_rOMIn'],
                                                 infusion_data['InfRum_GlcIn'],
                                                 infusion_data['InfRum_AcetIn'],
                                                 infusion_data['InfRum_PropIn'],
                                                 infusion_data['InfRum_ButrIn'],
                                                 infusion_data['InfSI_GlcIn'],
                                                 infusion_data['InfSI_AcetIn'],
                                                 infusion_data['InfSI_PropIn'],
                                                 infusion_data['InfSI_ButrIn'])
    diet_data['TT_dcrOMt'] = calculate_TT_dcrOMt(An_data['An_DigrOMtIn'],
                                                 diet_data['Dt_rOMIn'],
                                                 infusion_data['InfRum_GlcIn'],
                                                 infusion_data['InfRum_AcetIn'],
                                                 infusion_data['InfRum_PropIn'],
                                                 infusion_data['InfRum_ButrIn'],
                                                 infusion_data['InfSI_GlcIn'],
                                                 infusion_data['InfSI_AcetIn'],
                                                 infusion_data['InfSI_PropIn'],
                                                 infusion_data['InfSI_ButrIn'])

    # NRC 2001 Microbial N flow
    Du_MiN_NRC2001_g = calculate_Du_MiN_NRC2001_g(diet_data['Dt_TDNIn'], An_data['An_RDPIn'])

    # Fecal loss
    Fe_rOM = calculate_Fe_rOM(An_data['An_rOMIn'],
                              An_data['An_DigrOMaIn'])
    Fe_St = calculate_Fe_St(diet_data['Dt_StIn'],
                            infusion_data['Inf_StIn'],
                            An_data['An_DigStIn'])
    Fe_NDF = calculate_Fe_NDF(diet_data['Dt_NDFIn'],
                              diet_data['Dt_DigNDFIn'])
    Fe_NDFnf = calculate_Fe_NDFnf(diet_data['Dt_NDFnfIn'],
                                  diet_data['Dt_DigNDFnfIn'])
    Fe_OM = calculate_Fe_OM(Fe_CP,
                            Fe_NDF,
                            Fe_St,
                            Fe_rOM,
                            Fe_FA)
    Fe_DEout = calculate_Fe_DEout(An_data['An_GEIn'], An_data['An_DEIn'])
    Fe_DE_GE = calculate_Fe_DE_GE(Fe_DEout, An_data['An_GEIn'])
    Fe_DE = calculate_Fe_DE(Fe_DEout, An_data['An_DMIn'])

    ########################################
    # Step 10: Metabolizable Protein Intake
    ########################################
    An_MPIn = calculate_An_MPIn(diet_data['Dt_idRUPIn'],
                                   Du_idMiTP)
    An_MPIn_g = calculate_An_MPIn_g(An_MPIn)
    An_MP = calculate_An_MP(An_MPIn,
                            animal_input['DMI'],
                            infusion_data['InfRum_DMIn'],
                            infusion_data['InfSI_DMIn'])
    An_MP_CP = calculate_An_MP_CP(An_MPIn, An_data['An_CPIn'])

    ########################################
    # Step 8: Amino Acid Calculations
    ########################################
    AA_values['Abs_AA_g'] = calculate_Abs_AA_g(AA_list,
                                                  An_data,
                                                  infusion_data,
                                                  infusion_data['Inf_Art'])

    AA_values['mPrtmx_AA'] = calculate_mPrtmx_AA(AA_list,
                                                    coeff_dict)
    f_mPrt_max = calculate_f_mPrt_max(animal_input['An_305RHA_MlkTP'],
                                         coeff_dict)
    AA_values['mPrtmx_AA2'] = calculate_mPrtmx_AA2(AA_values['mPrtmx_AA'],
                                                      f_mPrt_max)
    AA_values['AA_mPrtmx'] = calculate_AA_mPrtmx(AA_list,
                                                    coeff_dict)
    AA_values['mPrt_AA_01'] = calculate_mPrt_AA_01(AA_values['AA_mPrtmx'],
                                                      AA_list,
                                                      coeff_dict)
    AA_values['mPrt_k_AA'] = calculate_mPrt_k_AA(AA_values['mPrtmx_AA2'],
                                                    AA_values['mPrt_AA_01'],
                                                    AA_values['AA_mPrtmx'])
    AA_values['IdAA_DtAA'] = calculate_IdAA_DtAA(diet_data, An_data, AA_list)
    
    Abs_EAA_g = calculate_Abs_EAA_g(AA_values['Abs_AA_g'])
    Abs_neAA_g = calculate_Abs_neAA_g(An_MPIn_g,
                                         Abs_EAA_g)
    Abs_OthAA_g = calculate_Abs_OthAA_g(Abs_neAA_g,
                                           AA_values['Abs_AA_g'])
    Abs_EAA2b_g = calculate_Abs_EAA2b_g(equation_selection['mPrt_eqn'],
                                           AA_values['Abs_AA_g'])
    mPrt_k_EAA2 = calculate_mPrt_k_EAA2(AA_values.loc['Met', 'mPrtmx_AA2'],
                                           AA_values.loc['Met', 'mPrt_AA_01'],
                                           AA_values.loc['Met', 'AA_mPrtmx'])


    ########################################
    # Step 11: Milk Production Prediciton
    ########################################
    Mlk_NP_g = calculate_Mlk_NP_g(animal_input['An_StatePhys'],
                                     animal_input['An_BW'],
                                     AA_values['Abs_AA_g'],
                                     AA_values['mPrt_k_AA'],
                                     Abs_neAA_g,
                                     Abs_OthAA_g,
                                     Abs_EAA2b_g,
                                     mPrt_k_EAA2,
                                     An_data['An_DigNDF'],
                                     An_data['An_DEInp'],
                                     An_data['An_DEStIn'],
                                     An_data['An_DEFAIn'],
                                     An_data['An_DErOMIn'],
                                     An_data['An_DENDFIn'],
                                     coeff_dict)
                                     
    Mlk_CP_g = calculate_Mlk_CP_g(Mlk_NP_g)
        
    ########################################
    # Step 12: Body Frame and Reserve Gain
    ########################################
    Frm_Gain_empty = calculate_Frm_Gain_empty(Frm_Gain,
                                                diet_data['Dt_DMIn_ClfLiq'],
                                                diet_data['Dt_DMIn_ClfStrt'], 
                                                coeff_dict)

    Body_Gain_empty = calculate_Body_Gain_empty(Frm_Gain_empty, Rsrv_Gain_empty)

    An_REgain_Calf = calculate_An_REgain_Calf(Body_Gain_empty, An_data['An_BW_empty'])

    Frm_NPgain = calculate_Frm_NPgain(animal_input['An_StatePhys'],
                                        NPGain_FrmGain,
                                        Frm_Gain_empty,
                                        Body_Gain_empty,
                                        An_REgain_Calf)

    Body_NPgain = calculate_Body_NPgain(Frm_NPgain, Rsrv_NPgain)
    Body_CPgain = calculate_Body_CPgain(Body_NPgain, coeff_dict)
    Body_CPgain_g = calculate_Body_CPgain_g(Body_CPgain)


########################################
# Step 13: Gestation Protein Use
########################################
    Gest_NCPgain_g = calculate_Gest_NCPgain_g(GrUter_BWgain,coeff_dict)

    Gest_NPgain_g = calculate_Gest_NPgain_g(Gest_NCPgain_g, coeff_dict)

    Gest_NPuse_g = calculate_Gest_NPuse_g(Gest_NPgain_g, coeff_dict)


    Gest_CPuse_g = calculate_Gest_CPuse_g(Gest_NPuse_g, coeff_dict)
    
########################################
# Step 14: Urinary Loss
########################################
    Ur_Nout_g = calculate_Ur_Nout_g(diet_data['Dt_CPIn'],
                                    Fe_CP,
                                    Scrf_CP_g,
                                    Fe_CPend_g,
                                    Mlk_CP_g,
                                    Body_CPgain_g,
                                    Gest_CPuse_g)

    Ur_DEout = calculate_Ur_DEout(Ur_Nout_g)

########################################
# Step 15: Energy Intake
########################################
    An_MEIn = calculate_An_MEIn(animal_input['An_StatePhys'],
                                animal_input['An_BW'],
                                An_data['An_DEIn'],
                                An_data['An_GasEOut'],
                                Ur_DEout,
                                diet_data['Dt_DMIn_ClfLiq'],
                                diet_data['Dt_DEIn_base_ClfLiq'],
                                diet_data['Dt_DEIn_base_ClfDry'],
                                equation_selection['RumDevDisc_Clf'])
    An_NEIn = calculate_An_NEIn(An_MEIn)
    An_NE = calculate_An_NE(An_NEIn,An_data['An_DMIn'])

########################################
# Step 16: Energy Requirement
########################################
    # Maintenance Requirements
    An_NEmUse_NS = calculate_An_NEmUse_NS(animal_input['An_StatePhys'],
                                             animal_input['An_BW'],
                                             An_data['An_BW_empty'],
                                             animal_input['An_Parity_rl'],
                                             diet_data['Dt_DMIn_ClfLiq'])
    
    An_NEm_Act_Graze = calculate_An_NEm_Act_Graze(diet_data['Dt_PastIn'],
                                                     animal_input['DMI'],
                                                     diet_data['Dt_PastSupplIn'],
                                                     An_data['An_MBW'])

    An_NEm_Act_Parlor = calculate_An_NEm_Act_Parlor(animal_input['An_BW'],
                                                       animal_input['Env_DistParlor'],
                                                       animal_input['Env_TripsParlor'])

    An_NEm_Act_Topo = calculate_An_NEm_Act_Topo(animal_input['An_BW'],
                                                   animal_input['Env_Topo'])

    An_NEmUse_Act = calculate_An_NEmUse_Act(An_NEm_Act_Graze,
                                               An_NEm_Act_Parlor,
                                               An_NEm_Act_Topo)

    An_NEmUse = calculate_An_NEmUse(An_NEmUse_NS,
                                       An_NEmUse_Act,
                                       coeff_dict)

    An_MEmUse = calculate_An_MEmUse(An_NEmUse,
                                       coeff_dict)

    # Gain Requirements
    Rsrv_Gain = calculate_Rsrv_Gain(animal_input['Trg_RsrvGain'])

    Rsrv_Gain_empty = calculate_Rsrv_Gain_empty(Rsrv_Gain)

    Rsrv_Fatgain = calculate_Rsrv_Fatgain(Rsrv_Gain_empty,
                                             coeff_dict)

    CPGain_FrmGain = calculate_CPGain_FrmGain(animal_input['An_BW'],
                                                 animal_input['An_BW_mature'])

    Rsrv_CPgain = calculate_Rsrv_CPgain(CPGain_FrmGain,
                                           Rsrv_Gain_empty)

    Rsrv_NEgain = calculate_Rsrv_NEgain(Rsrv_Fatgain,
                                           Rsrv_CPgain)

    Kr_ME_RE = calculate_Kr_ME_RE(animal_input['Trg_MilkProd'],
                                     animal_input['Trg_RsrvGain'])

    Rsrv_MEgain = calculate_Rsrv_MEgain(Rsrv_NEgain,
                                           Kr_ME_RE)

    FatGain_FrmGain = calculate_FatGain_FrmGain(animal_input['An_StatePhys'],
                                                   An_REgain_Calf,
                                                   animal_input['An_BW'],
                                                   animal_input['An_BW_mature'])

    Frm_Gain = calculate_Frm_Gain(animal_input['Trg_FrmGain'])

    Frm_Gain_empty = calculate_Frm_Gain_empty(Frm_Gain,
                                                 diet_data['Dt_DMIn_ClfLiq'],
                                                 diet_data['Dt_DMIn_ClfStrt'],
                                                 coeff_dict)

    Frm_Fatgain = calculate_Frm_Fatgain(FatGain_FrmGain,
                                           Frm_Gain_empty)

    NPGain_FrmGain = calculate_NPGain_FrmGain(CPGain_FrmGain,
                                                 coeff_dict)

    Frm_NPgain = calculate_Frm_NPgain(animal_input['An_StatePhys'],
                                         NPGain_FrmGain,
                                         Frm_Gain_empty,
                                         Body_Gain_empty,
                                         An_REgain_Calf)

    Frm_CPgain = calculate_Frm_CPgain(Frm_NPgain,
                                         coeff_dict)

    Frm_NEgain = calculate_Frm_NEgain(Frm_Fatgain,
                                         Frm_CPgain)

    Frm_MEgain = calculate_Frm_MEgain(Frm_NEgain,
                                         coeff_dict)

    An_MEgain = calculate_An_MEgain(Rsrv_MEgain,
                                       Frm_MEgain)

    # Gestation Requirement
    Gest_REgain = calculate_Gest_REgain(GrUter_BWgain,
                                           coeff_dict)

    Gest_MEuse = calculate_Gest_MEuse(Gest_REgain)

    # Milk Production Requirement
    Trg_NEmilk_Milk = calculate_Trg_NEmilk_Milk(animal_input['Trg_MilkFatp'],
                                                   animal_input['Trg_MilkTPp'],
                                                   animal_input['Trg_MilkLacp'])

    Trg_Mlk_NEout = calculate_Trg_Mlk_NEout(animal_input['Trg_MilkProd'],
                                               Trg_NEmilk_Milk)

    Trg_Mlk_MEout = calculate_Trg_Mlk_MEout(Trg_Mlk_NEout,
                                               coeff_dict)

    # Total Metabolizalbe Energy Requirement
    Trg_MEuse = calculate_Trg_MEuse(An_MEmUse,
                                       An_MEgain,
                                       Gest_MEuse,
                                       Trg_Mlk_MEout)

    ########################################
    # Step 17: Protein Requirement
    ########################################
    # Maintenance Requirement     
    Scrf_NP_g = calculate_Scrf_NP_g(Scrf_CP_g,
                                       coeff_dict)
        
    Scrf_MPUse_g_Trg = calculate_Scrf_MPUse_g_Trg(animal_input['An_StatePhys'],
                                                     Scrf_CP_g,
                                                     Scrf_NP_g,
                                                     coeff_dict)
        
    Ur_Nend_g = calculate_Ur_Nend_g(animal_input['An_BW'])
    
    Ur_NPend_g = calculate_Ur_NPend_g(Ur_Nend_g)
    
    Ur_MPendUse_g = calculate_Ur_MPendUse_g(Ur_NPend_g)
    
    An_MPm_g_Trg = calculate_An_MPm_g_Trg(Fe_MPendUse_g_Trg,
                                             Scrf_MPUse_g_Trg,
                                             Ur_MPendUse_g)
    
    # Gain Requirement
    Body_NPgain_g = calculate_Body_NPgain_g(Body_NPgain)
    
    Body_MPUse_g_Trg = calculate_Body_MPUse_g_Trg_initial(Body_NPgain_g,
                                                             coeff_dict)

    # Gestation Requirement
    Gest_MPUse_g_Trg = calculate_Gest_MPUse_g_Trg(Gest_NPuse_g,
                                                     coeff_dict)
    
    # Milk Requirement
    Trg_Mlk_NP_g = calculate_Trg_Mlk_NP_g(animal_input['Trg_MilkProd'],
                                             animal_input['Trg_MilkTPp'])
    
    Mlk_MPUse_g_Trg = calculate_Mlk_MPUse_g_Trg(Trg_Mlk_NP_g,
                                                    coeff_dict)

    # Total Protein Requirement
    # NOTE This initial protein requirement is the final value in most cases. There is an
    #      adjustment made when An_StatePhys == "Heifer" and Diff_MPuse_g > 0
    #      Some of the values used to make this adjustment are used elsewhere so it can't just 
    #      be put behind an if statement 
    An_MPuse_g_Trg = calculate_An_MPuse_g_Trg_initial(An_MPm_g_Trg,
                                                         Body_MPUse_g_Trg,
                                                         Gest_MPUse_g_Trg,
                                                         Mlk_MPUse_g_Trg)
    
    An_MEIn_approx = calculate_An_MEIn_approx(An_data['An_DEInp'],
                                                 An_data['An_DENPNCPIn'],
                                                 An_data['An_DigTPaIn'],
                                                 Body_NPgain,
                                                 An_data['An_GasEOut'],
                                                 coeff_dict)
    
    Min_MPuse_g = calculate_Min_MPuse_g(animal_input['An_StatePhys'],
                                           An_MPuse_g_Trg,
                                           animal_input['An_BW'],
                                           animal_input['An_BW_mature'],
                                           An_MEIn_approx)
    
    Diff_MPuse_g = calculate_Diff_MPuse_g(Min_MPuse_g,
                                             An_MPuse_g_Trg)
    
    Frm_NPgain_g = calculate_Frm_NPgain_g(Frm_NPgain)
    
    An_BWmature_empty = calculate_An_BWmature_empty(animal_input['An_BW_mature'],
                                                       coeff_dict)
    

    Kg_MP_NP_Trg = calculate_Kg_MP_NP_Trg(animal_input['An_StatePhys'],
                                             animal_input['An_Parity_rl'],
                                             animal_input['An_BW'],
                                             An_data['An_BW_empty'],
                                             animal_input['An_BW_mature'],
                                             An_BWmature_empty,
                                             MP_NP_efficiency_input,
                                             coeff_dict)

    Frm_MPUse_g_Trg = calculate_Frm_MPUse_g_Trg(animal_input['An_StatePhys'],
                                                   Frm_NPgain_g,
                                                   Kg_MP_NP_Trg,
                                                   Diff_MPuse_g)
            
    Rsrv_NPgain_g = calculate_Rsrv_NPgain_g(Rsrv_NPgain)
    
    Rsrv_MPUse_g_Trg = calculate_Rsrv_MPUse_g_Trg(animal_input['An_StatePhys'],
                                                     Diff_MPuse_g,
                                                     Rsrv_NPgain_g,
                                                     Kg_MP_NP_Trg)
    
    # Recalculate 
    Body_MPUse_g_Trg = calculate_Body_MPUse_g_Trg(animal_input['An_StatePhys'],
                                                     Diff_MPuse_g,
                                                     Body_NPgain_g,
                                                     Body_MPUse_g_Trg,
                                                     Kg_MP_NP_Trg)
    # Recalculate
    An_MPuse_g_Trg = calculate_An_MPuse_g_Trg(An_MPm_g_Trg,
                                                 Frm_MPUse_g_Trg,
                                                 Rsrv_MPUse_g_Trg,
                                                 Gest_MPUse_g_Trg,
                                                 Mlk_MPUse_g_Trg)
    
    ########################################
    # Milk Production Calculations
    ########################################
    An_LactDay_MlkPred = calculate_An_LactDay_MlkPred(animal_input['An_LactDay'])

    Trg_Mlk_Fat = calculate_Trg_Mlk_Fat(animal_input['Trg_MilkProd'],
                                        animal_input['Trg_MilkFatp'])

    Trg_Mlk_Fat_g = calculate_Trg_Mlk_Fat_g(Trg_Mlk_Fat)

    Mlk_Fatemp_g = calculate_Mlk_Fatemp_g(animal_input['An_StatePhys'],
                                          An_LactDay_MlkPred,
                                          animal_input['DMI'],
                                          diet_data['Dt_FAIn'],
                                          diet_data['Dt_DigC160In'],
                                          diet_data['Dt_DigC183In'],
                                          AA_values.loc['Ile', 'Abs_AA_g'],
                                          AA_values.loc['Met', 'Abs_AA_g'])

    Mlk_Fat_g = calculate_Mlk_Fat_g(equation_selection['mFat_eqn'],
                                    Trg_Mlk_Fat_g,
                                    Mlk_Fatemp_g)

    Mlk_Fat = calculate_Mlk_Fat(Mlk_Fat_g)

    Mlk_NP = calculate_Mlk_NP(Mlk_NP_g)

    Mlk_Prod_comp = calculate_Mlk_Prod_comp(animal_input['An_Breed'],
                                            Mlk_NP,
                                            Mlk_Fat,
                                            An_data['An_DEIn'],
                                            An_LactDay_MlkPred,
                                            animal_input['An_Parity_rl'])

    An_MPavail_Milk_Trg = calculate_An_MPavail_Milk_Trg(An_MPIn,
                                                        An_MPuse_g_Trg,
                                                        Mlk_MPUse_g_Trg)    

    Mlk_NP_MPalow_Trg_g = calculate_Mlk_NP_MPalow_Trg_g(An_MPavail_Milk_Trg,
                                                        coeff_dict)

    Mlk_Prod_MPalow = calculate_Mlk_Prod_MPalow(Mlk_NP_MPalow_Trg_g,
                                                animal_input['Trg_MilkTPp'])

    An_MEavail_Milk = calculate_An_MEavail_Milk(An_MEIn,
                                                An_MEgain,
                                                An_MEmUse,
                                                Gest_MEuse)

    Mlk_Prod_NEalow = calculate_Mlk_Prod_NEalow(An_MEavail_Milk,
                                                Trg_NEmilk_Milk,
                                                coeff_dict)

    Mlk_Prod = calculate_Mlk_Prod(animal_input['An_StatePhys'],
                                  equation_selection['mProd_eqn'],
                                  Mlk_Prod_comp,
                                  Mlk_Prod_NEalow,
                                  Mlk_Prod_MPalow,
                                  animal_input['Trg_MilkProd'])

    MlkNP_Milk = calculate_MlkNP_Milk(animal_input['An_StatePhys'],
                                      Mlk_NP_g,
                                      Mlk_Prod)
    
    MlkFat_Milk = calculate_MlkFat_Milk(animal_input['An_StatePhys'],
                                        Mlk_Fat,
                                        Mlk_Prod)
    
    MlkNE_Milk = calculate_MlkNE_Milk(MlkFat_Milk,
                                      MlkNP_Milk,
                                      animal_input['Trg_MilkLacp'])
    
    Mlk_NEout = calculate_Mlk_NEout(MlkNE_Milk,
                                    Mlk_Prod)

    Mlk_MEout = calculate_Mlk_MEout(Mlk_NEout,
                                       coeff_dict)

    ########################################
    # Mineral Requirement Calculations
    ########################################
    Body_Gain = calculate_Body_Gain(Frm_Gain,
                                    Rsrv_Gain)

    ### Calcium ###
    Ca_Mlk = calculate_Ca_Mlk(animal_input['An_Breed'])

    Fe_Ca_m = calculate_Fe_Ca_m(An_data['An_DMIn'])

    An_Ca_g = calculate_An_Ca_g(animal_input['An_BW_mature'],
                                animal_input['An_BW'],
                                Body_Gain)

    An_Ca_y = calculate_An_Ca_y(animal_input['An_GestDay'],
                                animal_input['An_BW'])

    An_Ca_l = calculate_An_Ca_l(Mlk_NP_g,
                                Ca_Mlk,
                                animal_input['Trg_MilkProd'],
                                animal_input['Trg_MilkTPp'])

    An_Ca_Clf = calculate_An_Ca_Clf(An_data['An_BW_empty'],
                                    Body_Gain_empty)

    An_Ca_req = calculate_An_Ca_req(animal_input['An_StatePhys'],
                                    diet_data['Dt_DMIn_ClfLiq'],
                                    An_Ca_Clf,
                                    Fe_Ca_m,
                                    An_Ca_g,
                                    An_Ca_y,
                                    An_Ca_l)

    An_Ca_bal = calculate_An_Ca_bal(diet_data['Abs_CaIn'],
                                    An_Ca_req)

    An_Ca_prod = calculate_An_Ca_prod(An_Ca_y,
                                      An_Ca_l,
                                      An_Ca_g)

    ### Phosphorus ###
    Ur_P_m = calculate_Ur_P_m(animal_input['An_BW']) 

    Fe_P_m = calculate_Fe_P_m(animal_input['An_Parity_rl'],
                              An_data['An_DMIn'])

    An_P_m = calculate_An_P_m(Ur_P_m,
                              Fe_P_m)

    An_P_g = calculate_An_P_g(animal_input['An_BW_mature'],
                              animal_input['An_BW'],
                              Body_Gain)

    An_P_y = calculate_An_P_y(animal_input['An_GestDay'],
                              animal_input['An_BW'])

    An_P_l = calculate_An_P_l(animal_input['Trg_MilkProd'],
                              MlkNP_Milk)

    An_P_Clf = calculate_An_P_Clf(An_data['An_BW_empty'],
                                  Body_Gain_empty)    

    An_P_req = calculate_An_P_req(animal_input['An_StatePhys'],
                                  diet_data['Dt_DMIn_ClfLiq'],
                                  An_P_Clf,
                                  An_P_m,
                                  An_P_g,
                                  An_P_y,
                                  An_P_l)

    An_P_bal = calculate_An_P_bal(diet_data['Abs_PIn'],
                                  An_P_req)

    Fe_P_g = calculate_Fe_P_g(diet_data['Dt_PIn'],
                              An_P_l,
                              An_P_y,
                              An_P_g,
                              Ur_P_m)

    An_P_prod = calculate_An_P_prod(An_P_y,
                                    An_P_l,
                                    An_P_g)

    ### Magnesium ###
    An_Mg_Clf = calculate_An_Mg_Clf(An_data['An_BW_empty'],
                                    Body_Gain_empty)

    Ur_Mg_m = calculate_Ur_Mg_m(animal_input['An_BW'])

    Fe_Mg_m = calculate_Fe_Mg_m(An_data['An_DMIn'])

    An_Mg_m = calculate_An_Mg_m(Ur_Mg_m,
                                Fe_Mg_m)

    An_Mg_g = calculate_An_Mg_g(Body_Gain)

    An_Mg_y = calculate_An_Mg_y(animal_input['An_GestDay'],
                                animal_input['An_BW'])

    An_Mg_l = calculate_An_Mg_l(animal_input['Trg_MilkProd'])

    An_Mg_req = calculate_An_Mg_req(animal_input['An_StatePhys'],
                                    diet_data['Dt_DMIn_ClfLiq'],
                                    An_Mg_Clf,
                                    An_Mg_m,
                                    An_Mg_g,
                                    An_Mg_y,
                                    An_Mg_l)

    An_Mg_bal = calculate_An_Mg_bal(diet_data['Abs_MgIn'],
                                    An_Mg_req)

    An_Mg_prod = calculate_An_Mg_prod(An_Mg_y,
                                      An_Mg_l,
                                      An_Mg_g)

    ### Sodium ###
    An_Na_Clf = calculate_An_Na_Clf(An_data['An_BW_empty'],
                                    Body_Gain_empty)

    Fe_Na_m = calculate_Fe_Na_m(An_data['An_DMIn'])

    An_Na_g = calculate_An_Na_g(Body_Gain)

    An_Na_y = calculate_An_Na_y(animal_input['An_GestDay'],
                                animal_input['An_BW'])

    An_Na_l = calculate_An_Na_l(animal_input['Trg_MilkProd'])

    An_Na_req = calculate_An_Na_req(animal_input['An_StatePhys'],
                                    diet_data['Dt_DMIn_ClfLiq'],
                                    An_Na_Clf,
                                    Fe_Na_m,
                                    An_Na_g,
                                    An_Na_y,
                                    An_Na_l)

    An_Na_bal = calculate_An_Na_bal(diet_data['Abs_NaIn'],
                                    An_Na_req)

    An_Na_prod = calculate_An_Na_prod(An_Na_y,
                                      An_Na_l,
                                      An_Na_g)

    ### Chlorine ###
    An_Cl_Clf = calculate_An_Cl_Clf(An_data['An_BW_empty'],
                                    Body_Gain_empty)
    
    Fe_Cl_m = calculate_Fe_Cl_m(An_data['An_DMIn'])

    An_Cl_g = calculate_An_Cl_g(Body_Gain)

    An_Cl_y = calculate_An_Cl_y(animal_input['An_GestDay'],
                                animal_input['An_BW'])

    An_Cl_l = calculate_An_Cl_l(animal_input['Trg_MilkProd'])

    An_Cl_req = calculate_An_Cl_req(animal_input['An_StatePhys'],
                                    diet_data['Dt_DMIn_ClfLiq'],
                                    An_Cl_Clf,
                                    Fe_Cl_m,
                                    An_Cl_g,
                                    An_Cl_y,
                                    An_Cl_l)

    An_Cl_bal = calculate_An_Cl_bal(diet_data['Abs_ClIn'],
                                    An_Cl_req)

    An_Cl_prod = calculate_An_Cl_prod(An_Cl_y,
                                      An_Cl_l,
                                      An_Cl_g)

    ### Potassium ###
    An_K_Clf = calculate_An_K_Clf(An_data['An_BW_empty'],
                                  Body_Gain_empty)

    Ur_K_m = calculate_Ur_K_m(animal_input['Trg_MilkProd'],
                              animal_input['An_BW'])

    Fe_K_m = calculate_Fe_K_m(An_data['An_DMIn'])

    An_K_m = calculate_An_K_m(Ur_K_m,
                              Fe_K_m)

    An_K_g = calculate_An_K_g(Body_Gain)

    An_K_y = calculate_An_K_y(animal_input['An_GestDay'],
                              animal_input['An_BW'])

    An_K_l = calculate_An_K_l(animal_input['Trg_MilkProd'])

    An_K_req = calculate_An_K_req(animal_input['An_StatePhys'],
                                  diet_data['Dt_DMIn_ClfLiq'],
                                  An_K_Clf,
                                  An_K_m,
                                  An_K_g,
                                  An_K_y,
                                  An_K_l)

    An_K_bal = calculate_An_K_bal(diet_data['Abs_KIn'],
                                  An_K_req)

    An_K_prod = calculate_An_K_prod(An_K_y,
                                    An_K_l,
                                    An_K_g)

    ### Sulphur ###
    An_S_req = calculate_An_S_req(An_data['An_DMIn'])

    An_S_bal = calculate_An_S_bal(diet_data['Dt_SIn'],
                                  An_S_req)

    ### Cobalt ###
    An_Co_req = calculate_An_Co_req(An_data['An_DMIn'])

    An_Co_bal = calculate_An_Co_bal(diet_data['Abs_CoIn'],
                                    An_Co_req)

    ### Copper ###
    An_Cu_Clf = calculate_An_Cu_Clf(animal_input['An_BW'],
                                    Body_Gain_empty)

    An_Cu_m = calculate_An_Cu_m(animal_input['An_BW'])

    An_Cu_g = calculate_An_Cu_g(Body_Gain)

    An_Cu_y = calculate_An_Cu_y(animal_input['An_GestDay'],
                                animal_input['An_BW'])

    An_Cu_l = calculate_An_Cu_l(animal_input['Trg_MilkProd'])

    An_Cu_req = calculate_An_Cu_req(animal_input['An_StatePhys'],
                                    diet_data['Dt_DMIn_ClfLiq'],
                                    An_Cu_Clf,
                                    An_Cu_m,
                                    An_Cu_g,
                                    An_Cu_y,
                                    An_Cu_l)

    An_Cu_bal = calculate_An_Cu_bal(diet_data['Abs_CuIn'],
                                    An_Cu_req)

    An_Cu_prod = calculate_An_Cu_prod(An_Cu_y,
                                      An_Cu_l,
                                      An_Cu_g)

    ### Iodine ###
    An_I_req = calculate_An_I_req(animal_input['An_StatePhys'],
                                  An_data['An_DMIn'],
                                  animal_input['An_BW'],
                                  animal_input['Trg_MilkProd'])

    An_I_bal = calculate_An_I_bal(diet_data['Dt_IIn'],
                                  An_I_req)

    ### Iron ###
    An_Fe_Clf = calculate_An_Fe_Clf(Body_Gain)

    An_Fe_g = calculate_An_Fe_g(Body_Gain)

    An_Fe_y = calculate_An_Fe_y(animal_input['An_GestDay'],
                                animal_input['An_BW'])

    An_Fe_l = calculate_An_Fe_l(animal_input['Trg_MilkProd'])

    An_Fe_req = calculate_An_Fe_req(animal_input['An_StatePhys'],
                                    diet_data['Dt_DMIn_ClfLiq'],
                                    An_Fe_Clf,
                                    An_Fe_g,
                                    An_Fe_y,
                                    An_Fe_l)

    An_Fe_bal = calculate_An_Fe_bal(diet_data['Abs_FeIn'],
                                    An_Fe_req)

    An_Fe_prod = calculate_An_Fe_prod(An_Fe_y,
                                      An_Fe_l,
                                      An_Fe_g)

    ### Maganese ###
    An_Mn_Clf = calculate_An_Mn_Clf(animal_input['An_BW'],
                                    Body_Gain)

    An_Mn_m = calculate_An_Mn_m(animal_input['An_BW'])
    
    An_Mn_g = calculate_An_Mn_g(Body_Gain)
    
    An_Mn_y = calculate_An_Mn_y(animal_input['An_GestDay'],
                                animal_input['An_BW'])
    
    An_Mn_l = calculate_An_Mn_l(animal_input['Trg_MilkProd'])
    
    An_Mn_req = calculate_An_Mn_req(animal_input['An_StatePhys'],
                                    diet_data['Dt_DMIn_ClfLiq'],
                                    An_Mn_Clf,
                                    An_Mn_m,
                                    An_Mn_g,
                                    An_Mn_y,
                                    An_Mn_l)
    
    An_Mn_bal = calculate_An_Mn_bal(diet_data['Abs_MnIn'],
                                    An_Mn_req)
    
    An_Mn_prod = calculate_An_Mn_prod(An_Mn_y,
                                      An_Mn_l,
                                      An_Mn_g)

    ### Selenium ###  
    An_Se_req = calculate_An_Se_req(An_data['An_DMIn'])

    An_Se_bal = calculate_An_Se_bal(diet_data['Dt_SeIn'],
                                    An_Se_req)

    ### Zinc ###
    An_Zn_Clf = calculate_An_Zn_Clf(An_data['An_DMIn'],
                                    Body_Gain)

    An_Zn_m = calculate_An_Zn_m(An_data['An_DMIn'])

    An_Zn_g = calculate_An_Zn_g(Body_Gain)

    An_Zn_y = calculate_An_Zn_y(animal_input['An_GestDay'],
                                animal_input['An_BW'])

    An_Zn_l = calculate_An_Zn_l(animal_input['Trg_MilkProd'])

    An_Zn_req = calculate_An_Zn_req(animal_input['An_StatePhys'],
                                       diet_data['Dt_DMIn_ClfLiq'],
                                       An_Zn_Clf,
                                       An_Zn_m,
                                       An_Zn_g,
                                       An_Zn_y,
                                       An_Zn_l)

    An_Zn_bal = calculate_An_Zn_bal(diet_data['Abs_ZnIn'],
                                       An_Zn_req)

    An_Zn_prod = calculate_An_Zn_prod(An_Zn_y, 
                                         An_Zn_l,
                                         An_Zn_g)

    ### DCAD ###
    An_DCADmeq = calculate_An_DCADmeq(diet_data['Dt_K'],
                                         diet_data['Dt_Na'],
                                         diet_data['Dt_Cl'],
                                         diet_data['Dt_S'])

    ########################################
    # Water Calculations
    ########################################
    An_WaIn = calculate_An_WaIn(animal_input['An_StatePhys'],
                                animal_input['DMI'],
                                diet_data['Dt_DM'],
                                diet_data['Dt_Na'],
                                diet_data['Dt_K'],
                                diet_data['Dt_CP'],
                                animal_input['Env_TempCurr'])

    ########################################
    # Capture Outputs
    ########################################
    locals_dict = locals()
    output = ModelOutput(locals_input=locals_dict)
    
    return output
