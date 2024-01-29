import math
from nasem_dairy.ration_balancer.ration_balancer_functions import check_coeffs_in_coeff_dict

def check_animal_lactation_day(An_LactDay):
    '''
    #Cap DIM at 375 d to prevent the polynomial from getting out of range. Line 2259 

    Returns An_LactDay_MlkPred which is the animal lactation day corrected to be <= 375 DIM
    '''
    # An_LactDay_MlkPred
    if An_LactDay <= 375:
        An_LactDay_MlkPred = An_LactDay
    elif An_LactDay > 375:
        An_LactDay_MlkPred = 375
    
    return An_LactDay_MlkPred


def calculate_Mlk_Fat_g(df, Dt_FAIn, Dt_DigC160In, Dt_DigC183In, An_LactDay_MlkPred, Dt_DMIn, An_StatePhys) -> float:
    """
    Predicts milk fat production

    Parameters:
        df (Dataframe): A dataframe with indivual amino acid intakes and flows, AA_values in the model
        Dt_FAIn (Number): Fatty acid intake, kg/d
        Dt_DigC160In (Number): Digestable C16:0 fatty acid intake, kg/d
        Dt_DigC183In (Number): Digestable C18:3 fatty acid intake, kg/d 
        An_LactDay (Number): Day of lactation
        Dt_DMIn (Number): Dry matter intake, kg/d
    
    Returns:
        Mlk_Fat_g (Number): Predicted milk fat, g
        An_LactDay_MlkPred (Number): A variable to max the days in milk at 375 to prevent polynomial from getting out of range
    """
    Abs_Ile_g = df.loc['Ile', 'Abs_AA_g']
    Abs_Met_g = df.loc['Met', 'Abs_AA_g']

    # (Equation 20-215, p. 440)
    Mlk_Fat_g = 453 - 1.42 * An_LactDay_MlkPred + 24.52 * (Dt_DMIn - Dt_FAIn) + 0.41 * Dt_DigC160In * 1000 + 1.80 * Dt_DigC183In * 1000 + 1.45 * Abs_Ile_g + 1.34 * Abs_Met_g

    if An_StatePhys != "Lactating Cow":                 # Line 2910
        Mlk_Fat_g = 0

    return Mlk_Fat_g





def calculate_Mlk_Prod_comp(Mlk_NP_g, Mlk_Fat_g, An_DEIn, An_LactDay_MlkPred, An_Parity_rl):
    """
    Predict milk production based on components 

    Parameters:
        Mlk_NP_g (Number): Net protein in milk, g/d
        Mlk_Fat_g (Number): Predicted milk fat, g
        An_DEIn (Number): Digestible energy intake in Mcal/d
        An_LactDay_MlkPred (Number): A variable to max the days in milk at 375 to prevent polynomial from getting out of range
        An_Parity_rl (Number): Animal Parity where 1 = Primiparous and 2 = Multiparous.

    Returns: 
        Mlk_Prod_comp (Number): Predicted milk production, kg/d
    """
    Mlk_NP = Mlk_NP_g / 1000                    # Line 2210, kg NP/d
    Mlk_Fat = Mlk_Fat_g / 1000

    Mlk_Prod_comp = 4.541 + 11.13 * Mlk_NP + 2.648 * Mlk_Fat + 0.1829 * An_DEIn - 0.06257 * (An_LactDay_MlkPred - 137.1) + 2.766e-4 * (An_LactDay_MlkPred - 137.1)**2 \
                    + 1.603e-6 * (An_LactDay_MlkPred - 137.1)**3 - 7.397e-9 * (An_LactDay_MlkPred - 137.1)**4 + 1.567 * (An_Parity_rl - 1)
    return Mlk_Prod_comp


def calculate_Mlk_Prod_MPalow(An_MPuse_g_Trg, Mlk_MPuse_g_Trg, An_MPIn, Trg_MilkTPp, coeff_dict):
    """
    Metabolizalbe protein allowable milk production

    Parameters:
        An_MPuse_g_Trg (Number): Metabolizable protein requirement, g/d
        Mlk_MPuse_g_Trg (Number): Metabolizable protein requirement for milk, g/d
        An_MPIn (Number): Metabolizlable protein intake, kg/d 
        Trg_MilkTPp (Percentage): Animal Milk True Protein percentage
        coeff_dict (Dict): Dictionary containing all coefficients for the model

    Returns:
        Mlk_Prod_MPalow (Number): Metabolizable protein allowable milk production, kg/d
    """
    req_coeffs = ['Kx_MP_NP_Trg']
    check_coeffs_in_coeff_dict(coeff_dict, req_coeffs)

    An_MPavail_Milk_Trg = An_MPIn - An_MPuse_g_Trg / 1000 + Mlk_MPuse_g_Trg / 1000          # Line 2706
    Mlk_NP_MPalow_Trg_g = An_MPavail_Milk_Trg * coeff_dict['Kx_MP_NP_Trg'] * 1000                         # Line 2707, g milk NP/d

    Mlk_Prod_MPalow = Mlk_NP_MPalow_Trg_g / (Trg_MilkTPp / 100) / 1000                      # Line 2708, kg milk/d using Trg milk protein % to predict volume

    return Mlk_Prod_MPalow


def calculate_Mlk_Prod_NEalow(An_MEIn, An_MEgain, An_MEmUse, Gest_MEuse, Trg_NEmilk_Milk, coeff_dict):
    """
    Net energy allowable milk production

    Parameters:
        An_MEIn (Number): Metabolizable energy intake, Mcal/d
        An_MEgain (Number): Metabolizble energy requirement for frame and reserve gain, Mcal/d
        An_MEmUse (Number): Metabolizable energy requirement for maintenance, Mcal/d
        Gest_MEuse (Number): Metabolizable energy requirement for gestation, Mcal/d
        Trg_NEmilk_Milk (Number): Net energy concentration of milk, Mcal/kg
        coeff_dict (Dict): Dictionary containing all coefficients for the model

    Returns:
        Mlk_Prod_NEalow (Number): Net energy allowable milk production, kg/d
        An_MEavail_Milk (Number): Metabolisable energy avaiable milk production, Mcal/d

    """
    req_coeffs = ['Kl_ME_NE']
    check_coeffs_in_coeff_dict(coeff_dict, req_coeffs)

    An_MEavail_Milk = An_MEIn - An_MEgain - An_MEmUse - Gest_MEuse                      # Line 2896
    Mlk_Prod_NEalow = An_MEavail_Milk * coeff_dict['Kl_ME_NE'] / Trg_NEmilk_Milk                  	# Line 2897, Energy allowable Milk Production, kg/d

    return Mlk_Prod_NEalow, An_MEavail_Milk