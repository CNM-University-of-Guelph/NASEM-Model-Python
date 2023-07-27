# NASEM model - EXECUTE

# from nasem_dairy.ration_balancer.coeff_dict import coeff_dict
from nasem_dairy.ration_balancer.ration_balancer_functions import fl_get_rows, get_nutrient_intakes
from nasem_dairy.NASEM_equations.misc_equations import calculate_Dt_DMIn_Lact1, AA_calculations, calculate_GrUter_BWgain
from nasem_dairy.NASEM_equations.Du_microbial_equations import calculate_Du_MiN_g
from nasem_dairy.NASEM_equations.Animal_supply_equations import calculate_An_DEIn, calculate_An_NE
from nasem_dairy.NASEM_equations.Milk_equations import calculate_Mlk_Fat_g, calculate_Mlk_NP_g, calculate_Mlk_Prod_comp, calculate_Mlk_Prod_MPalow, calculate_Mlk_Prod_NEalow
from nasem_dairy.NASEM_equations.ME_equations import calculate_ME_requirement
from nasem_dairy.NASEM_equations.MP_equations import calculate_MP_requirement



def NASEM_model(diet_info, animal_input, equation_selection, path_to_db, coeff_dict):
    """Execute NASEM functions. 
    This will take all inputs and execute functions in order to return model outputs

    Args:
        diet_info (_type_): _description_
        animal_input (_type_): _description_
        equation_selection (_type_): _description_
        path_to_db (str): A string of filepath (including file name) of sqlite3 database with feed library
        coeff_dict (dict): A dictionary of coefficients needed by model, in coeff_dict.py
    
    Returns:
        A list of model outputs
    """
########################################
# Step 1: Read User Input
########################################
   
    diet_info = diet_info.copy()
    
    # list_of_feeds is used to query the database and retrieve the ingredient composition, stored in feed_data
    list_of_feeds = diet_info['Feedstuff'].tolist()
    feed_data = fl_get_rows(list_of_feeds, path_to_db)

    # Scale %_DM_intake to 100%
    user_perc = diet_info['%_DM_user'].sum()
    scaling_factor = 100 / user_perc

    # Should be called 'Fd_DMInp' instead of %_DM_intake
    diet_info['%_DM_intake'] = diet_info['%_DM_user'] * scaling_factor
    # Adjust so sum is exactly 100
    adjustment = 100 - diet_info['%_DM_intake'].sum()
    diet_info['%_DM_intake'] += adjustment / len(diet_info)

    # Predict DMI
    if equation_selection['DMI_pred'] == 0:
        animal_input['DMI'] = calculate_Dt_DMIn_Lact1(
            animal_input['An_Parity_rl'], 
            animal_input['Trg_MilkProd'], 
            animal_input['An_BW'], 
            animal_input['An_BCS'],
            animal_input['An_LactDay'], 
            animal_input['Trg_MilkFatp'], 
            animal_input['Trg_MilkTPp'], 
            animal_input['Trg_MilkLacp'])
    
    # Should be called 'Fd_DMIn' for consistency with R code
    diet_info['kg_intake'] = diet_info['%_DM_intake'] / 100 * animal_input['DMI']

########################################
# Step 2: Feed Based Calculations
########################################
    diet_info = get_nutrient_intakes(diet_info, feed_data, animal_input, equation_selection, coeff_dict)

########################################
# Step 3: Microbial Protein Calculations
########################################
    Du_MiN_NRC2021_g = calculate_Du_MiN_g(
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
# Step 4: Amino Acid Calculations
########################################
    AA_values, Du_MiCP_g = AA_calculations(Du_MiN_NRC2021_g, feed_data, diet_info, animal_input, coeff_dict)

########################################
# Step 5: Other Calculations
########################################
# Intake calculations that require additional steps, need results from other calculations or values that need to be calculated for other functions

    GrUter_BWgain = calculate_GrUter_BWgain(
        animal_input['Fet_BWbrth'], 
        animal_input['An_AgeDay'], 
        animal_input['An_GestDay'], 
        animal_input['An_GestLength'], 
        animal_input['An_LactDay'], 
        animal_input['An_Parity_rl'], 
        coeff_dict)

    # This function could be renamed as it is doing all the DE intake calculations
    An_DEIn, An_DENPNCPIn, An_DETPIn, An_DigNDFIn, An_DEStIn, An_DEFAIn, An_DErOMIn, An_DENDFIn, Fe_CP, Fe_CPend_g, Du_idMiCP_g = calculate_An_DEIn(
        diet_info.loc['Diet', 'Fd_DigNDFIn_Base'], 
        diet_info.loc['Diet', 'Fd_NDFIn'], 
        diet_info.loc['Diet', 'Fd_DigStIn_Base'], 
        diet_info.loc['Diet', 'Fd_St_kg/d'], 
        diet_info.loc['Diet','Fd_DigrOMtIn'],
        diet_info.loc['Diet', 'Fd_CPIn'], 
        diet_info.loc['Diet', 'Fd_RUPIn'],
        diet_info.loc['Diet', 'Fd_idRUPIn'], 
        diet_info.loc['Diet', 'Fd_NPNCPIn'], 
        diet_info.loc['Diet', 'Fd_DigFAIn'], 
        Du_MiCP_g, 
        animal_input['An_BW'], 
        animal_input['DMI'], 
        coeff_dict)

    # Predicted milk protein
    Mlk_NP_g, An_DigNDF, An_MPIn = calculate_Mlk_NP_g(
        AA_values, 
        diet_info.loc['Diet', 'Fd_idRUPIn'], 
        Du_idMiCP_g, 
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
        coeff_dict)

    # Net energy/Metabolizable energy
    An_NE, An_MEIn = calculate_An_NE(diet_info.loc['Diet', 'Fd_CPIn'], 
                                     diet_info.loc['Diet', 'Fd_FAIn'], 
                                     Mlk_NP_g, An_DEIn, An_DigNDF, Fe_CP, Fe_CPend_g, 
                                     animal_input['DMI'], 
                                     animal_input['An_BW'], 
                                     animal_input['An_BW_mature'], 
                                     animal_input['Trg_FrmGain'], 
                                     animal_input['Trg_RsrvGain'], 
                                     GrUter_BWgain, 
                                     coeff_dict)
 
########################################
# Step 6: Requirement Calculations
########################################

    # Metabolizable Energy Requirements
    Trg_MEuse, An_MEmUse, An_MEgain, Gest_MEuse, Trg_Mlk_MEout, Trg_NEmilk_Milk = calculate_ME_requirement(animal_input['An_BW'], 
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
    # Metabolizable Protein Requirements
    An_MPuse_g_Trg, An_MPm_g_Trg, Body_MPUse_g_Trg, Gest_MPUse_g_Trg, Mlk_MPUse_g_Trg = calculate_MP_requirement(diet_info.loc['Diet', 'Fd_NDFIn'], 
                                                                                                                 animal_input['DMI'], 
                                                                                                                 animal_input['An_BW'], 
                                                                                                                 animal_input['An_BW_mature'], 
                                                                                                                 animal_input['Trg_FrmGain'],
                                                                                                                 animal_input['Trg_RsrvGain'], 
                                                                                                                 animal_input['Trg_MilkProd'], 
                                                                                                                 animal_input['Trg_MilkTPp'], 
                                                                                                                 GrUter_BWgain, 
                                                                                                                 coeff_dict)    

########################################
# Step 7: Performance Calculations
########################################

    # Predicted milk fat
    Mlk_Fat_g, An_LactDay_MlkPred = calculate_Mlk_Fat_g(AA_values, 
                                                        diet_info.loc['Diet', 'Fd_FAIn'], 
                                                        diet_info.loc['Diet', 'Fd_DigC160In'], 
                                                        diet_info.loc['Diet', 'Fd_DigC183In'], 
                                                        animal_input['An_LactDay'], 
                                                        animal_input['DMI'])

    # Predicted milk yield
    Mlk_Prod_comp = calculate_Mlk_Prod_comp(Mlk_NP_g, Mlk_Fat_g, An_DEIn, An_LactDay_MlkPred, animal_input['An_Parity_rl']) 
  
    # MP Allowable Milk
    Mlk_Prod_MPalow = calculate_Mlk_Prod_MPalow(An_MPuse_g_Trg, Mlk_MPUse_g_Trg, An_MPIn, animal_input['Trg_MilkTPp'], coeff_dict)

    # NE Allowable Milk
    Mlk_Prod_NEalow = calculate_Mlk_Prod_NEalow(An_MEIn, An_MEgain, An_MEmUse, Gest_MEuse, Trg_NEmilk_Milk, coeff_dict)

########################################
# Step 8: Return values of interest
########################################
    # Milk Fat %
    milk_fat = (Mlk_Fat_g / 1000) / Mlk_Prod_comp *100
    # Milk Protein %
    milk_protein = (Mlk_NP_g / 1000) / Mlk_Prod_comp *100 


    model_results = {
    'milk_fat': milk_fat,
    'milk_protein': milk_protein,
    'Mlk_Prod_comp': Mlk_Prod_comp,
    'Mlk_Prod_MPalow': Mlk_Prod_MPalow,
    'Mlk_Prod_NEalow': Mlk_Prod_NEalow,
    'Trg_MEuse': Trg_MEuse,
    'An_MPuse_g_Trg': An_MPuse_g_Trg
    }

    output = {
    'diet_info': diet_info,
    'animal_input': animal_input,
    'feed_data': feed_data,
    'equation_selection': equation_selection,
    'AA_values': AA_values,
    'model_results': model_results
}
    # Return so they can be viewed in environment
    return output


