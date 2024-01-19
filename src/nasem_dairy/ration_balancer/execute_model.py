# NASEM model - EXECUTE

# from nasem_dairy.ration_balancer.coeff_dict import coeff_dict
from nasem_dairy.ration_balancer.ration_balancer_functions import fl_get_feed_rows, get_nutrient_intakes
from nasem_dairy.NASEM_equations.dev_gestation_equations import calculate_GrUter_BWgain
from nasem_dairy.NASEM_equations.Animal_supply_equations import calculate_An_DEIn, calculate_An_NE
from nasem_dairy.NASEM_equations.Milk_equations import calculate_Mlk_Fat_g, calculate_Mlk_NP_g, calculate_Mlk_Prod_comp, calculate_Mlk_Prod_MPalow, calculate_Mlk_Prod_NEalow, check_animal_lactation_day, calculate_An_MPIn_g
from nasem_dairy.NASEM_equations.ME_equations import calculate_ME_requirement
from nasem_dairy.NASEM_equations.MP_equations import calculate_MP_requirement
from nasem_dairy.NASEM_equations.micronutrient_equations import mineral_requirements
from nasem_dairy.NASEM_equations.temporary_functions import temp_MlkNP_Milk, temp_calc_An_GasEOut, temp_calc_An_DigTPaIn, calculate_Mlk_Prod, calculate_MlkNE_Milk, calculate_Mlk_MEout

# Import statements for updated functions
from nasem_dairy.NASEM_equations.dev_DMI_equations import (
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
    calculate_Dt_DMIn_DryCow2
)
from nasem_dairy.NASEM_equations.dev_milk_equations import calculate_Trg_NEmilk_Milk
from nasem_dairy.NASEM_equations.dev_nutrient_intakes import (
    calculate_TT_dcFdNDF_Lg,
    calculate_Fd_DNDF48,
    calculate_TT_dcFdNDF_48h,
    calculate_TT_dcFdNDF_Base,
    calculate_Fd_GE,
    calculate_Fd_DMIn,
    calculate_Fd_AFIn,
    calculate_Fd_For,
    calculate_Fd_ForWet,
    calculate_Fd_ForDry,
    calculate_Fd_Past,
    calculate_Fd_LiqClf,
    calculate_Fd_ForNDF,
    calculate_Fd_NDFnf,
    calculate_Fd_NPNCP,
    calculate_Fd_NPN,
    calculate_Fd_NPNDM,
    calculate_Fd_TP,
    calculate_Fd_fHydr_FA,
    calculate_Fd_FAhydr,
    calculate_Fd_NFC,
    calculate_Fd_rOM,
    calculate_Fd_DigNDFIn_Base,
    calculate_Fd_NPNCPIn,
    calculate_Fd_NPNIn,
    calculate_Fd_NPNDMIn,
    calculate_Fd_CPAIn,
    calculate_Fd_CPBIn,
    calculate_Fd_CPBIn_For,
    calculate_Fd_CPBIn_Conc,
    calculate_Fd_CPCIn,
    calculate_Fd_CPIn_ClfLiq,
    calculate_Fd_CPIn_ClfDry,
    calculate_Fd_rdcRUPB,
    calculate_Fd_RUPBIn,
    calculate_Fd_RUPIn,
    calculate_Fd_RUP_CP,
    calculate_Fd_RUP,
    calculate_Fd_RDP,
    calculate_Fd_OMIn,
    calculate_Fd_DE_base_1,
    calculate_Fd_DE_base_2,
    calculate_Fd_DE_base,
    calculate_Fd_DEIn_base,
    calculate_Fd_DEIn_base_ClfLiq,
    calculate_Fd_DEIn_base_ClfDry,
    calculate_Fd_DMIn_ClfLiq,
    calculate_Fd_DE_ClfLiq,
    calculate_Fd_ME_ClfLiq,
    calculate_Fd_DMIn_ClfFor,
    calculate_Fd_PinorgIn,
    calculate_Fd_PorgIn,
    calculate_Fd_MgIn_min,
    calculate_Fd_acCa,
    calculate_Fd_acPtot,
    calculate_Fd_acMg,
    calculate_Fd_acNa,
    calculate_Fd_acK,
    calculate_Fd_acCl,
    calculate_Fd_absCaIn,
    calculate_Fd_absPIn,
    calculate_Fd_absMgIn_base,
    calculate_Fd_absNaIn,
    calculate_Fd_absKIn,
    calculate_Fd_absClIn,
    calculate_Fd_acCo,
    calculate_Fd_acCu,
    calculate_Fd_acFe,
    calculate_Fd_acMn,
    calculate_Fd_acZn,
    calculate_Fd_DigSt,
    calculate_Fd_DigStIn_Base,
    calculate_Fd_DigrOMt,
    calculate_Fd_idRUPIn,
    calculate_TT_dcFdFA,
    calculate_Fd_DigFAIn,
    calculate_Dt_ForDNDF48,
    calculate_Dt_ForDNDF48_ForNDF,
    calculate_Dt_ADF_NDF,
    calculate_Dt_DE_ClfLiq,
    calculate_Dt_ME_ClfLiq,
    calculate_Dt_NDFnfIn,
    calculate_Dt_Lg_NDF,
    calculate_Dt_ForNDFIn,
    calculate_Dt_PastSupplIn,
    calculate_Dt_NIn,
    calculate_Dt_RUPIn,
    calculate_Dt_RUP_CP,
    calculate_Dt_fCPBdu,
    calculate_Dt_UFAIn,
    calculate_Dt_MUFAIn,
    calculate_Dt_PUFAIn,
    calculate_Dt_SatFAIn,
    calculate_Dt_OMIn,
    calculate_Dt_rOMIn,
    calculate_Dt_DM,
    calculate_Dt_NDFIn_BW,
    calculate_Dt_ForNDF_NDF,
    calculate_Dt_ForNDFIn_BW,
    calculate_Dt_DMInSum,
    calculate_Dt_DEIn_ClfLiq,
    calculate_Dt_MEIn_ClfLiq,
    calculate_Dt_CPA_CP,
    calculate_Dt_CPB_CP,
    calculate_Dt_CPC_CP,
    calculate_Dt_DigNDFIn,
    calculate_Dt_DigStIn,
    calculate_Dt_DigrOMaIn,
    calculate_Dt_dcCP_ClfDry,
    calculate_Dt_DENDFIn,
    calculate_Dt_DEStIn,
    calculate_Dt_DErOMIn,
    calculate_Dt_DigCPaIn,
    calculate_Dt_DECPIn,
    calculate_Dt_DENPNCPIn,
    calculate_Dt_DETPIn,
    calculate_Dt_DEFAIn,
    calculate_Dt_DEIn,
    calculate_TT_dcNDF_Base,
    calculate_TT_dcNDF,
    calculate_TT_dcSt_Base,
    calculate_TT_dcSt,
    calculate_diet_info,
    calculate_diet_data_initial,
    calculate_diet_data_complete
)

from nasem_dairy.NASEM_equations.dev_rumen_equations import (
    calculate_Rum_dcNDF,
    calculate_Rum_dcSt,
    calculate_Rum_DigNDFIn,
    calculate_Rum_DigStIn
)

from nasem_dairy.NASEM_equations.dev_microbial_protein_equations import (
    calculate_RDPIn_MiNmax,
    calculate_MiN_Vm,
    calculate_Du_MiN_NRC2021_g,
    calculate_Du_MiN_VTln_g,
    calculate_Du_MiN_VTnln_g,
    calculate_Du_MiCP,
    calculate_Du_idMiCP_g,
    calculate_Du_idMiCP
)

from nasem_dairy.NASEM_equations.dev_protein_equations import calculate_f_mPrt_max, calculate_Du_MiCP_g, calculate_Du_MiTP_g
from nasem_dairy.NASEM_equations.dev_amino_acid_equations import (
    calculate_Du_AAMic,
    calculate_Du_IdAAMic,
    calculate_Abs_AA_g,
    calculate_mPrtmx_AA,
    calculate_mPrtmx_AA2,
    calculate_AA_mPrtmx,
    calculate_mPrt_AA_01,
    calculate_mPrt_k_AA
)

from nasem_dairy.NASEM_equations.dev_infusion_equations import (
    calculate_Inf_TPIn,
    calculate_Inf_OMIn,
    calculate_Inf_Rum,
    calculate_Inf_SI,
    calculate_Inf_Art,
    calculate_InfRum_TPIn,
    calculate_InfSI_TPIn,
    calculate_InfRum_RUPIn,
    calculate_InfRum_RUP_CP,
    calculate_InfRum_idRUPIn,
    calculate_InfSI_idTPIn,
    calculate_InfSI_idCPIn,
    calculate_Inf_idCPIn,
    calculate_InfRum_RDPIn,
    calculate_Inf_DigFAIn,
    calculate_Inf_DEAcetIn,
    calculate_Inf_DEPropIn,
    calculate_Inf_DEButrIn,
    calculate_infusion_data
)

from nasem_dairy.NASEM_equations.dev_animal_equations import (
    calculate_An_DMIn_BW,
    calculate_An_RDPIn,
    calculate_An_RDP,
    calculate_An_RDPIn_g,
    calculate_An_DMIn_BW,
    calculate_An_NDFIn,
    calculate_An_NDF,
    calculate_An_DigNDFIn,
    calculate_An_DENDFIn,
    calculate_An_DigStIn,
    calculate_An_DEStIn,
    calculate_An_DigrOMaIn,
    calculate_An_DErOMIn,
    calculate_An_idRUPIn,
    calculate_An_RUPIn,
    calculate_An_DMIn,
    calculate_An_CPIn,
    calculate_An_DigCPaIn,
    calculate_An_DECPIn,
    calculate_An_DENPNCPIn,
    calculate_An_DETPIn,
    calculate_An_DigFAIn,
    calculate_An_DEFAIn,
    calculate_An_DEIn,
    calculate_An_data_initial,
    calculate_An_data_complete
)

from nasem_dairy.NASEM_equations.dev_gestation_equations import (
    calculate_Uter_Wtpart,
    calculate_Uter_Wt,
    calculate_GrUter_Wtpart,
    calculate_GrUter_Wt,
    calculate_Uter_BWgain,
    calculate_GrUter_BWgain
)

from nasem_dairy.NASEM_equations.dev_fecal_equations import (
    calculate_Fe_rOMend,
    calculate_Fe_RUP,
    calculate_Fe_RumMiCP,
    calculate_Fe_CPend_g,
    calculate_Fe_CPend,
    calculate_Fe_CP
)

from nasem_dairy.NASEM_equations.dev_calf_equations import (
    calculate_K_FeCPend_ClfLiq
)


def NASEM_model(diet_info, animal_input, equation_selection, feed_library_df, coeff_dict):
    """Execute NASEM functions. 
    This will take all inputs and execute functions in order to return model outputs

    Args:
        diet_info (_type_): _description_
        animal_input (_type_): _description_
        equation_selection (_type_): _description_
        feed_library_df (pd.DataFrame): A df which contains the NASEM 2021 feed library
        coeff_dict (dict): A dictionary of coefficients needed by model, in coeff_dict.py

    Returns:
        A list of model outputs
    """
    ########################################
    # Step 1: Read User Input
    ########################################

    # prevent mutable changes outside of expected scope (especially for Shiny):
    diet_info = diet_info.copy()
    animal_input = animal_input.copy()

    # list_of_feeds is used to query the database and retrieve the ingredient composition, stored in feed_data
    list_of_feeds = diet_info['Feedstuff'].tolist()
    # feed_data = fl_get_rows(list_of_feeds, path_to_db)
    feed_data = fl_get_feed_rows(list_of_feeds, feed_library_df)

    # Set feed inclusion percentages
    Fd_DMInp_Sum = diet_info['kg_user'].sum()  # Total intake, kg
    diet_info['Fd_DMInp'] = diet_info['kg_user'] / Fd_DMInp_Sum

    # Calculate additional physiology values
    animal_input['An_PrePartDay'] = animal_input['An_GestDay'] - \
        animal_input['An_GestLength']
    animal_input['An_PrePartWk'] = animal_input['An_PrePartDay'] / 7

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

    # if animal_input['An_StatePhys'] != 'Lactating Cow':
    #     animal_input['Trg_MilkProd'] = None

### START of updated equations ###
    ########################################
    # Step 2: DMI Equations
    ########################################
    # Calculate Target milk net energy
    Trg_NEmilk_Milk = calculate_Trg_NEmilk_Milk(animal_input['Trg_MilkTPp'],
                                                animal_input['Trg_MilkFatp'],
                                                animal_input['Trg_MilkLacp'])

    # TODO: where is 0, 1 and 9 ?

    # Need to precalculate Dt_NDF for DMI predicitons, this will be based on the user entered DMI (animal_input['DMI])

    # Dt_NDF = NDF_precalculation(diet_info, feed_data)
    # Need to update this

    # Predict DMI for heifers
    Kb_LateGest_DMIn = calculate_Kb_LateGest_DMIn(Dt_NDF)
    An_PrePartWklim = calculate_An_PrePartWklim(animal_input['An_PrePartWk'])
    An_PrePartWkDurat = An_PrePartWklim * 2

    if equation_selection['DMIn_eqn'] == 0:
        # print('Using user input DMI')
        pass

    # Predict DMI for lactating cow
    elif equation_selection['DMIn_eqn'] == 8:
        animal_input['DMI'] = calculate_Dt_DMIn_Lact1(animal_input['Trg_MilkProd'],
                                                      animal_input['An_BW'],
                                                      animal_input['An_BCS'],
                                                      animal_input['An_LactDay'],
                                                      animal_input['An_Parity_rl'],
                                                      Trg_NEmilk_Milk)

    # Individual Heifer DMI Predictions
    elif equation_selection['DMIn_eqn'] in [2, 3, 4, 5, 6, 7]:
        Dt_DMIn_BW_LateGest_i = calculate_Dt_DMIn_BW_LateGest_i(
            An_PrePartWklim, Kb_LateGest_DMIn, coeff_dict)
        # All the individual DMI predictions require this value
        Dt_DMIn_Heif_LateGestInd = calculate_Dt_DMIn_Heif_LateGestInd(animal_input['An_BW'],
                                                                      Dt_DMIn_BW_LateGest_i)

        if equation_selection['DMIn_eqn'] == 2:
            if animal_input['An_PrePartWk'] > An_PrePartWkDurat:
                animal_input['DMI'] = min(calculate_Dt_DMIn_Heif_NRCa(animal_input['An_BW'],
                                                                      animal_input['An_BW_mature']
                                                                      ),
                                          Dt_DMIn_Heif_LateGestInd)
            else:
                animal_input['DMI'] = calculate_Dt_DMIn_Heif_NRCa(animal_input['An_BW'],
                                                                  animal_input['An_BW_mature'])

        if equation_selection['DMIn_eqn'] == 3:
            if animal_input['An_PrePartWk'] > An_PrePartWkDurat:
                animal_input['DMI'] = min(calculate_Dt_DMIn_Heif_NRCad(animal_input['An_BW'],
                                                                       animal_input['An_BW_mature'],
                                                                       Dt_NDF
                                                                       ),
                                          Dt_DMIn_Heif_LateGestInd)
            else:
                animal_input['DMI'] = calculate_Dt_DMIn_Heif_NRCad(animal_input['An_BW'],
                                                                   animal_input['An_BW_mature'],
                                                                   Dt_NDF)

        if equation_selection['DMIn_eqn'] == 4:
            if animal_input['An_PrePartWk'] > An_PrePartWkDurat:
                animal_input['DMI'] = min(calculate_Dt_DMIn_Heif_H1(animal_input['An_BW']),
                                          Dt_DMIn_Heif_LateGestInd)
            else:
                animal_input['DMI'] = calculate_Dt_DMIn_Heif_H1(
                    animal_input['An_BW'])

        if equation_selection['DMIn_eqn'] == 5:
            Dt_NDFdev_DMI = calculate_Dt_NDFdev_DMI(animal_input['An_BW'],
                                                    Dt_NDF)
            if animal_input['An_PrePartWk'] > An_PrePartWkDurat:
                animal_input['DMI'] = min(calculate_Dt_DMIn_Heif_H2(animal_input['An_BW'],
                                                                    Dt_NDFdev_DMI),
                                          Dt_DMIn_Heif_LateGestInd)
            else:
                animal_input['DMI'] = calculate_Dt_DMIn_Heif_H2(animal_input['An_BW'],
                                                                Dt_NDFdev_DMI)

        if equation_selection['DMIn_eqn'] == 6:
            if animal_input['An_PrePartWk'] > An_PrePartWkDurat:
                animal_input['DMI'] = min(calculate_Dt_DMIn_Heif_HJ1(animal_input['An_BW']),
                                          Dt_DMIn_Heif_LateGestInd)
            else:
                animal_input['DMI'] = calculate_Dt_DMIn_Heif_HJ1(
                    animal_input['An_BW'])

        if equation_selection['DMIn_eqn'] == 7:
            Dt_NDFdev_DMI = calculate_Dt_NDFdev_DMI(animal_input['An_BW'],
                                                    Dt_NDF)
            if animal_input['An_PrePartWk'] > An_PrePartWkDurat:
                animal_input['DMI'] = min(calculate_Dt_DMIn_Heif_HJ2(animal_input['An_BW'],
                                                                     Dt_NDFdev_DMI),
                                          Dt_DMIn_Heif_LateGestInd)
            else:
                animal_input['DMI'] = calculate_Dt_DMIn_Heif_HJ2(animal_input['An_BW'],
                                                                 Dt_NDFdev_DMI)

    # Group Heifer DMI Predictions
    elif equation_selection['DMIn_eqn'] in [12, 13, 14, 15, 16, 17]:
        Dt_DMIn_BW_LateGest_p = calculate_Dt_DMIn_BW_LateGest_p(
            An_PrePartWkDurat, Kb_LateGest_DMIn, coeff_dict)
        # All group DMI predicitons require this value
        Dt_DMIn_Heif_LateGestPen = calculate_Dt_DMIn_Heif_LateGestPen(animal_input['An_BW'],
                                                                      Dt_DMIn_BW_LateGest_p)

        if equation_selection['DMIn_eqn'] == 12:
            if animal_input['An_PrePartWk'] > An_PrePartWkDurat:
                animal_input['DMI'] = min(calculate_Dt_DMIn_Heif_NRCa(animal_input['An_BW'],
                                                                      animal_input['An_BW_mature']
                                                                      ),
                                          Dt_DMIn_Heif_LateGestPen)
            else:
                animal_input['DMI'] = calculate_Dt_DMIn_Heif_NRCa(animal_input['An_BW'],
                                                                  animal_input['An_BW_mature'])

        if equation_selection['DMIn_eqn'] == 13:
            if animal_input['An_PrePartWk'] > An_PrePartWkDurat:
                animal_input['DMI'] = min(calculate_Dt_DMIn_Heif_NRCad(animal_input['An_BW'],
                                                                       animal_input['An_BW_mature'],
                                                                       Dt_NDF
                                                                       ),
                                          Dt_DMIn_Heif_LateGestPen)
            else:
                animal_input['DMI'] = calculate_Dt_DMIn_Heif_NRCad(animal_input['An_BW'],
                                                                   animal_input['An_BW_mature'],
                                                                   Dt_NDF)

        if equation_selection['DMIn_eqn'] == 14:
            if animal_input['An_PrePartWk'] > An_PrePartWkDurat:
                animal_input['DMI'] = min(calculate_Dt_DMIn_Heif_H1(animal_input['An_BW']),
                                          Dt_DMIn_Heif_LateGestPen)
            else:
                animal_input['DMI'] = calculate_Dt_DMIn_Heif_H1(
                    animal_input['An_BW'])

        if equation_selection['DMIn_eqn'] == 15:
            Dt_NDFdev_DMI = calculate_Dt_NDFdev_DMI(animal_input['An_BW'],
                                                    Dt_NDF)
            if animal_input['An_PrePartWk'] > An_PrePartWkDurat:
                animal_input['DMI'] = min(calculate_Dt_DMIn_Heif_H2(animal_input['An_BW'],
                                                                    Dt_NDFdev_DMI),
                                          Dt_DMIn_Heif_LateGestPen)
            else:
                animal_input['DMI'] = calculate_Dt_DMIn_Heif_H2(animal_input['An_BW'],
                                                                Dt_NDFdev_DMI)

        if equation_selection['DMIn_eqn'] == 16:
            if animal_input['An_PrePartWk'] > An_PrePartWkDurat:
                animal_input['DMI'] = min(calculate_Dt_DMIn_Heif_HJ1(animal_input['An_BW']),
                                          Dt_DMIn_Heif_LateGestPen)
            else:
                animal_input['DMI'] = calculate_Dt_DMIn_Heif_HJ1(
                    animal_input['An_BW'])

        if equation_selection['DMIn_eqn'] == 17:
            Dt_NDFdev_DMI = calculate_Dt_NDFdev_DMI(animal_input['An_BW'],
                                                    Dt_NDF)
            if animal_input['An_PrePartWk'] > An_PrePartWkDurat:
                animal_input['DMI'] = min(calculate_Dt_DMIn_Heif_HJ2(animal_input['An_BW'],
                                                                     Dt_NDFdev_DMI),
                                          Dt_DMIn_Heif_LateGestPen)
            else:
                animal_input['DMI'] = calculate_Dt_DMIn_Heif_HJ2(animal_input['An_BW'],
                                                                 Dt_NDFdev_DMI)

    elif equation_selection['DMIn_eqn'] == 10:
        Dt_DMIn_BW_LateGest_i = calculate_Dt_DMIn_BW_LateGest_i(
            An_PrePartWklim, Kb_LateGest_DMIn, coeff_dict)
        Dt_DMIn_BW_LateGest_p = calculate_Dt_DMIn_BW_LateGest_p(
            An_PrePartWkDurat, Kb_LateGest_DMIn, coeff_dict)

        if animal_input['An_PrePartWk'] > An_PrePartWkDurat:
            animal_input['DMI'] = min(calculate_Dt_DMIn_DryCow1_FarOff(animal_input['An_BW'],
                                                                       Dt_DMIn_BW_LateGest_i),
                                      calculate_Dt_DMIn_DryCow1_Close(animal_input['An_BW'],
                                                                      Dt_DMIn_BW_LateGest_p)
                                      )
        else:
            animal_input['DMI'] = calculate_Dt_DMIn_DryCow1_FarOff(animal_input['An_BW'],
                                                                   Dt_DMIn_BW_LateGest_i)

    elif equation_selection['DMIn_eqn'] == 11:
        animal_input['DMI'] = calculate_Dt_DMIn_DryCow2(
            animal_input['An_BW'], animal_input['An_GestDay'], animal_input['An_GestLength'])

    else:
        # It needs to catch all possible solutions, otherwise it's possible that it stays unchanged without warning
        print("DMIn_eqn uncaught - DMI not changed. equation_selection[DMIn_eqn]: " + str(
            equation_selection['DMIn_eqn']))

##### END OF UPDATED CODE #####

    ########################################
    # Step 3: Feed Based Calculations
    ########################################
    diet_info = get_nutrient_intakes(
        diet_info,
        feed_data,
        animal_input['DMI'],  # What if we want predicted equations?
        equation_selection,
        coeff_dict)

    ########################################
    # Step 4: Micronutrient Calculations
    ########################################
    df_mineral_intakes, mineral_values = mineral_intakes(
        animal_input['An_StatePhys'],
        feed_data,
        diet_info)

    df_vitamins = vitamin_supply(feed_data, diet_info)

    ########################################
    # Step 5: Microbial Protein Calculations
    ########################################
    Du_MiN_NRC2021_g, Rum_DigNDFIn, Rum_DigStIn, An_RDPIn_g = calculate_Du_MiN_g(
        diet_info.loc['Diet', 'Fd_NDFIn'],
        animal_input['DMI'],
        diet_info.loc['Diet', 'Fd_St_kg/d'],
        diet_info.loc['Diet', 'Fd_CP_kg/d'],
        diet_info.loc['Diet', 'Fd_ADF_kg/d'],
        diet_info.loc['Diet', 'Fd_ForWetIn'],
        diet_info.loc['Diet', 'Fd_RUPIn'],
        diet_info.loc['Diet', 'Fd_ForNDFIn'],
        diet_info.loc['Diet', 'Dt_RDPIn'],
        coeff_dict)

    ########################################
    # Step 6: Amino Acid Calculations
    ########################################
    AA_values, Du_MiCP_g = AA_calculations(
        Du_MiN_NRC2021_g,
        feed_data,
        diet_info,
        animal_input,
        coeff_dict)

    # RDP - MiCP Balance (or Rumen_RDPbal equation 20-78; line 1168)
    An_RDPbal_g = An_RDPIn_g - Du_MiCP_g

    ########################################
    # Step 7: Other Calculations
    ########################################
    # Intake calculations that require additional steps, need results from other calculations or values that need to be calculated for other functions

    GrUter_BWgain, GrUter_Wt = calculate_GrUter_BWgain(
        animal_input['Fet_BWbrth'],
        animal_input['An_AgeDay'],
        animal_input['An_GestDay'],
        animal_input['An_GestLength'],
        animal_input['An_LactDay'],
        animal_input['An_Parity_rl'],
        coeff_dict)

    # This function could be renamed as it is doing all the DE intake calculations
    (An_DEIn, An_DENPNCPIn, An_DETPIn, An_DigNDFIn, An_DEStIn,
     An_DEFAIn, An_DErOMIn, An_DENDFIn, Fe_CP, Fe_CPend_g,
     Du_idMiCP_g) = calculate_An_DEIn(
        diet_info.loc['Diet', 'Fd_DigNDFIn_Base'],
        diet_info.loc['Diet', 'Fd_NDFIn'],
        diet_info.loc['Diet', 'Fd_DigStIn_Base'],
        diet_info.loc['Diet', 'Fd_St_kg/d'],
        diet_info.loc['Diet', 'Fd_DigrOMtIn'],
        diet_info.loc['Diet', 'Fd_CPIn'],
        diet_info.loc['Diet', 'Fd_RUPIn'],
        diet_info.loc['Diet', 'Fd_idRUPIn'],
        diet_info.loc['Diet', 'Fd_NPNCPIn'],
        diet_info.loc['Diet', 'Fd_DigFAIn'],
        Du_MiCP_g,
        animal_input['An_BW'],
        animal_input['DMI'],
        equation_selection['Monensin_eqn'],
        coeff_dict)

    # Metabolizable Protein Intake
    An_MPIn, An_MPIn_g = calculate_An_MPIn_g(
        diet_info.loc['Diet', 'Fd_idRUPIn'], Du_idMiCP_g, coeff_dict)

    # Predicted milk protein
    Mlk_NP_g, An_DigNDF, An_DEInp = calculate_Mlk_NP_g(
        AA_values,
        An_MPIn_g,
        An_DEIn,
        An_DETPIn,
        An_DENPNCPIn,
        An_DigNDFIn,
        An_DEStIn,
        An_DEFAIn,
        An_DErOMIn,
        An_DENDFIn,
        animal_input['An_BW'],
        animal_input['DMI'],
        animal_input['An_StatePhys'],
        coeff_dict)

    # Gaseous energy loss
    An_GasEOut = temp_calc_An_GasEOut(An_DigNDF,
                                      animal_input['An_StatePhys'],
                                      diet_info,
                                      animal_input['DMI'],
                                      equation_selection['Monensin_eqn'])

    # Net energy/Metabolizable energy
    An_NE, An_NE_In, An_MEIn, Frm_NPgain = calculate_An_NE(
        diet_info.loc['Diet', 'Fd_CPIn'],
        diet_info.loc['Diet', 'Fd_FAIn'],
        Mlk_NP_g,
        An_DEIn,
        An_DigNDF,
        Fe_CP,
        Fe_CPend_g,
        animal_input['DMI'],
        animal_input['An_BW'],
        animal_input['An_BW_mature'],
        animal_input['Trg_FrmGain'],
        animal_input['Trg_RsrvGain'],
        GrUter_BWgain,
        An_GasEOut,
        coeff_dict)

    ########################################
    # Step 8: Requirement Calculations
    ########################################

    # Metabolizable Energy Requirements
    (Trg_MEuse, An_MEmUse, An_MEgain, Gest_MEuse,
     Trg_Mlk_MEout, Trg_NEmilk_Milk, Frm_NEgain, Rsrv_NEgain) = calculate_ME_requirement(
        animal_input['An_BW'],
        animal_input['DMI'],
        animal_input['Trg_MilkProd'],
        animal_input['An_BW_mature'],
        animal_input['Trg_FrmGain'],
        animal_input['Trg_MilkFatp'],
        animal_input['Trg_MilkTPp'],
        animal_input['Trg_MilkLacp'],
        animal_input['Trg_RsrvGain'],
        GrUter_BWgain,
        coeff_dict)

    # Calculate some values for the heifer adjustment to MP requirement,
    # this will be changed in the future and is placed here to avoid cluttering the calculate_MP_requirement function
    An_DigTPaIn = temp_calc_An_DigTPaIn(Fe_CP, diet_info)

    # Metabolizable Protein Requirements
    (An_MPuse_g_Trg, An_MPm_g_Trg, Body_MPUse_g_Trg,
     Gest_MPUse_g_Trg, Mlk_MPUse_g_Trg, An_MPuse_kg_Trg) = calculate_MP_requirement(
         An_DEInp,
         An_DENPNCPIn,
         An_DigTPaIn,
         An_GasEOut,
         Frm_NPgain,
         diet_info.loc['Diet', 'Fd_NDFIn'],
         animal_input['DMI'],
         animal_input['An_BW'],
         animal_input['An_BW_mature'],
         animal_input['Trg_FrmGain'],
         animal_input['Trg_RsrvGain'],
         animal_input['Trg_MilkProd'],
         animal_input['Trg_MilkTPp'],
         GrUter_BWgain,
         animal_input['An_StatePhys'],
         coeff_dict)

    ########################################
    # Step 9: Performance Calculations
    ########################################
    # if animal_input['An_StatePhys'] == 'Lactating Cow':
    # Correct An_lactDay
    if animal_input['An_StatePhys'] == 'Lactating Cow':
        An_LactDay_MlkPred = check_animal_lactation_day(
            animal_input['An_LactDay'])

        # Predicted milk fat
        Mlk_Fat_g = calculate_Mlk_Fat_g(
            AA_values,
            diet_info.loc['Diet', 'Fd_FAIn'],
            diet_info.loc['Diet', 'Fd_DigC160In'],
            diet_info.loc['Diet', 'Fd_DigC183In'],
            An_LactDay_MlkPred,
            animal_input['DMI'],
            animal_input['An_StatePhys'])

        # Predicted milk yield
        Mlk_Prod_comp = calculate_Mlk_Prod_comp(
            Mlk_NP_g,
            Mlk_Fat_g,
            An_DEIn,
            An_LactDay_MlkPred,
            animal_input['An_Parity_rl'])

        # MP Allowable Milk
        Mlk_Prod_MPalow = calculate_Mlk_Prod_MPalow(
            An_MPuse_g_Trg,
            Mlk_MPUse_g_Trg,
            An_MPIn,
            animal_input['Trg_MilkTPp'],
            coeff_dict)

        # NE Allowable Milk
        Mlk_Prod_NEalow, An_MEavail_Milk = calculate_Mlk_Prod_NEalow(
            An_MEIn,
            An_MEgain,
            An_MEmUse,
            Gest_MEuse,
            Trg_NEmilk_Milk,
            coeff_dict)
    else:
        An_LactDay_MlkPred = 0  # Default to 0 for non lactating animals
        Mlk_Fat_g = 0
        Mlk_Prod_comp = 0
        Mlk_Prod_MPalow = 0
        Mlk_Prod_NEalow = 0

    ########################################
    # Step 10: Calculations Requiring Milk Production Values
    ########################################

    if animal_input['An_StatePhys'] == 'Lactating Cow':
        MlkNP_Milk = temp_MlkNP_Milk(
            animal_input['An_StatePhys'],
            Mlk_NP_g,
            Mlk_Prod_comp,
            animal_input['Trg_MilkProd'])
    else:
        MlkNP_Milk = 0

    # Mineral Requirements
    mineral_requirements_dict, mineral_balance_dict, An_DCADmeq = mineral_requirements(
        animal_input['An_StatePhys'],
        animal_input['An_Parity_rl'],
        animal_input['An_Breed'],
        animal_input['DMI'],
        animal_input['An_BW_mature'],
        animal_input['An_BW'],
        animal_input['Trg_FrmGain'],
        animal_input['Trg_RsrvGain'],
        animal_input['An_GestDay'],
        GrUter_Wt,
        Mlk_NP_g,
        animal_input['Trg_MilkProd'],
        animal_input['Trg_MilkTPp'],
        mineral_values.loc['Ca', 'Abs_mineralIn'],
        MlkNP_Milk,
        mineral_values.loc['P', 'Abs_mineralIn'],
        mineral_values.loc['P', 'Dt_mineralIn'],
        mineral_values.loc['Mg', 'Abs_mineralIn'],
        mineral_values.loc['Na', 'Abs_mineralIn'],
        mineral_values.loc['Cl', 'Abs_mineralIn'],
        mineral_values.loc['K', 'Abs_mineralIn'],
        mineral_values.loc['S', 'Dt_mineralIn'],
        mineral_values.loc['Co', 'Abs_mineralIn'],
        mineral_values.loc['Cu', 'Abs_mineralIn'],
        mineral_values.loc['I', 'Dt_mineralIn'],
        mineral_values.loc['Fe', 'Abs_mineralIn'],
        mineral_values.loc['Mn', 'Abs_mineralIn'],
        mineral_values.loc['Se', 'Dt_mineralIn'],
        mineral_values.loc['Zn', 'Abs_mineralIn'],
        mineral_values.loc['K', 'Dt_macro'],
        mineral_values.loc['Na', 'Dt_macro'],
        mineral_values.loc['Cl', 'Dt_macro'],
        mineral_values.loc['S', 'Dt_macro'])

    Mlk_Prod = calculate_Mlk_Prod(
        animal_input['An_StatePhys'],
        equation_selection['mProd_eqn'],
        Mlk_Prod_comp,
        Mlk_Prod_NEalow,
        Mlk_Prod_MPalow,
        animal_input['Trg_MilkProd']
    )

    MlkNE_Milk = calculate_MlkNE_Milk(Mlk_Prod,  # either target or predicted depending on mProd_eqn
                                      Mlk_Fat_g,  # predicted
                                      MlkNP_Milk,  # predicted
                                      # Always uses the target (user input) as no prediction possible
                                      animal_input['Trg_MilkLacp']
                                      )

    Mlk_MEout = calculate_Mlk_MEout(Mlk_Prod,
                                    MlkNE_Milk,
                                    coeff_dict
                                    )

    ########################################
    # Step 11: Return values of interest
    ########################################
    if animal_input['An_StatePhys'] == 'Lactating Cow':
        # Milk Fat %
        milk_fat = (Mlk_Fat_g / 1000) / Mlk_Prod_comp * 100
        # Milk Protein %
        milk_protein = (Mlk_NP_g / 1000) / Mlk_Prod_comp * 100
    else:
        milk_fat = None
        milk_protein = None

    # Metabolizable Protein Balance
    An_MPBal_g_Trg = An_MPIn_g - An_MPuse_g_Trg

    # Energy Balance
    # An_MEuse = An_MEmUse + An_MEgain + Gest_MEuse + Mlk_MEout #ME use with predicted milk NP
    # An_MEbal = An_MEIn - An_MEuse

    # Use Target ME calculation instead of predicted, to match that MP balance is based on target not predicted
    An_MEbal = An_MEIn - Trg_MEuse

    model_results_short = {
        'Mlk_Prod_comp': Mlk_Prod_comp,
        'milk_fat': milk_fat,
        'milk_protein': milk_protein,

        'Mlk_Prod_MPalow': Mlk_Prod_MPalow,
        'Mlk_Prod_NEalow': Mlk_Prod_NEalow,

        'An_MEIn': An_MEIn,
        # This is Target req - i.e. from user input fat, protein, lactose
        'Trg_MEuse': Trg_MEuse,
        # 'An_MEuse': An_MEuse,

        'An_MPIn_g': An_MPIn_g,
        'An_MPuse_g_Trg': An_MPuse_g_Trg,
        # Protein and Energy balance
        'An_MPBal_g_Trg': An_MPBal_g_Trg,
        'An_MEbal': An_MEbal,

        # Rumen MCP balance
        'An_RDPbal_g': An_RDPbal_g
    }

    # filter locals() to return only floats and ints
    model_results_numeric = {var_name: var_value for var_name, var_value in locals(
    ).items() if isinstance(var_value, (int, float))}

    output = {
        'diet_info': diet_info,
        'animal_input': animal_input,
        'feed_data': feed_data,
        'equation_selection': equation_selection,
        'AA_values': AA_values,
        'model_results_short': model_results_short,
        'model_results_full': model_results_numeric,
        'mineral_requirements_dict': mineral_requirements_dict,
        'mineral_intakes': mineral_values,
        'mineral_balance_dict': mineral_balance_dict,
        'vitamin_intakes': df_vitamins
    }

    # Return so they can be viewed in environment
    return output
