import math
from nasem_dairy.ration_balancer.ration_balancer_functions import check_coeffs_in_coeff_dict

def calculate_Mlk_NP_g(df, Dt_idRUPIn, Du_idMiCP_g, An_DEIn, An_DETPIn, An_DENPNCPIn, An_DigNDFIn, An_DEStIn, An_DEFAIn, An_DErOMIn, An_DENDFIn, An_BW, Dt_DMIn, An_StatePhys, coeff_dict):
    """
    Predicts net protein output in milk 

    Paramters:
        df (Dataframe): A dataframe with indivual amino acid intakes and flows, AA_values in the model
        Dt_idRUPIn (Number): Intestinally digested rumen undegradable protein intake, kg/d
        Du_idMiCP_g (Number): Intestinally digested microbial crude protein, g/d
        An_DEIn (Number): Digestible energy intake in Mcal/d
        An_DETPIn (Number): Digestible energy from true protein, Mcal/d
        An_DENPNCPIn (Number): Digestible energy crud eprotein synthesized from non protein nitrogen (NPN), Mcal/d
        An_DigNDFIn (Number): Digestable neutral detergent fiber (NDF) intake, Mcal/d
        An_DEStIn (Number): Digestible energy from starch, Mcal/d
        An_DEFAIn (Number): Digestible energy from fatty acids, Mcal/d
        An_DErOMIn (Number): Digestible energy from residual organic matter, Mcal/d
        An_DENDFIn (Number): Digestible energy from neutral detergent fiber (NDF), Mcal
        An_BW (Number): Animal bodyweight, kg
        Dt_DMIn (Number): Dry matter intake, kg/d
        coeff_dict (Dict): Dictionary containing all coefficients for the model

    Returns:
        Mlk_NP_g (Number): Net protein in milk, g/d
        An_DigNDF (Number): Total tract digested neutral detergent fiber
        An_MPIn (Number): Metabolizlable protein intake, kg/d
    """
    req_coeffs = ['mPrt_Int', 'fMiTP_MiCP', 'mPrt_k_NEAA', 'mPrt_k_OthAA', 
                  'mPrt_k_DEInp', 'mPrt_k_DigNDF', 'mPrt_k_DEIn_StFA', 'mPrt_k_DEIn_NDF', 'mPrt_k_BW']     
    check_coeffs_in_coeff_dict(coeff_dict, req_coeffs)

    An_DigNDF = An_DigNDFIn / Dt_DMIn * 100
    # Unpack the AA_values dataframe into dictionaries
    AA_list = ['Arg', 'His', 'Ile', 'Leu', 'Lys', 'Met', 'Phe', 'Thr', 'Trp', 'Val']
    Abs_AA_g = {}
    mPrt_k_AA = {}

    for AA in AA_list:
        Abs_AA_g[AA] = df.loc[AA, 'Abs_AA_g']
        mPrt_k_AA[AA] = df.loc[AA, 'mPrt_k_AA']

    # Calculate Mlk_NP_g
    Abs_EAA_g = Abs_AA_g['Arg'] + Abs_AA_g['His'] + Abs_AA_g['Ile'] + Abs_AA_g['Leu'] + Abs_AA_g['Lys'] \
                + Abs_AA_g['Met'] + Abs_AA_g['Phe'] + Abs_AA_g['Thr'] + Abs_AA_g['Trp'] + Abs_AA_g['Val']

    Du_idMiTP_g = coeff_dict['fMiTP_MiCP'] * Du_idMiCP_g              # Line 1182
    Du_idMiTP = Du_idMiTP_g / 1000
    An_MPIn = Dt_idRUPIn + Du_idMiTP                    # Line 1236 (Equation 20-136 p. 432 - without infused TP)
    An_MPIn_g = An_MPIn * 1000                          # Line 1238 
    Abs_neAA_g = An_MPIn_g * 1.15 - Abs_EAA_g           # Line 1771 (Equation 20-150 p. 433)
    Abs_OthAA_g = Abs_neAA_g + Abs_AA_g['Arg'] + Abs_AA_g['Phe'] + Abs_AA_g['Thr'] + Abs_AA_g['Trp'] + Abs_AA_g['Val'] #Equation 20-186a, p. 436
    Abs_EAA2b_g = Abs_AA_g['His']**2 + Abs_AA_g['Ile']**2 + Abs_AA_g['Leu']**2 + Abs_AA_g['Lys']**2 + Abs_AA_g['Met']**2        # Line 2106, 1778; (Equation 20-186b p. 436)
    mPrtmx_Met2 = df.loc['Met', 'mPrtmx_AA2']
    mPrt_Met_0_1 = df.loc['Met', 'mPrt_AA_0.1']
    # Cannot call the variable mPrt_Met_0.1 in python, this is the only variable not consistent with R code
    Met_mPrtmx = df.loc['Met', 'AA_mPrtmx']
    An_DEInp = An_DEIn - An_DETPIn - An_DENPNCPIn

    #Scale the quadratic; can be calculated from any of the AA included in the squared term. All give the same answer
    mPrt_k_EAA2 = (2 * math.sqrt(mPrtmx_Met2**2 - mPrt_Met_0_1 * mPrtmx_Met2) - 2 * mPrtmx_Met2 + mPrt_Met_0_1) / (Met_mPrtmx * 0.1)**2
   

    Mlk_NP_g = coeff_dict['mPrt_Int'] + Abs_AA_g['Arg'] * mPrt_k_AA['Arg'] + Abs_AA_g['His'] * mPrt_k_AA['His'] \
                + Abs_AA_g['Ile'] * mPrt_k_AA['Ile'] + Abs_AA_g['Leu'] * mPrt_k_AA['Leu'] \
                + Abs_AA_g['Lys'] * mPrt_k_AA['Lys'] + Abs_AA_g['Met'] * mPrt_k_AA['Met'] \
                + Abs_AA_g['Phe'] * mPrt_k_AA['Phe'] + Abs_AA_g['Thr'] * mPrt_k_AA['Thr'] \
                + Abs_AA_g['Trp'] * mPrt_k_AA['Trp'] + Abs_AA_g['Val'] * mPrt_k_AA['Val'] \
                + Abs_neAA_g * coeff_dict['mPrt_k_NEAA'] + Abs_OthAA_g * coeff_dict['mPrt_k_OthAA'] + Abs_EAA2b_g * mPrt_k_EAA2 \
                + An_DEInp * coeff_dict['mPrt_k_DEInp'] + (An_DigNDF - 17.06) * coeff_dict['mPrt_k_DigNDF'] + (An_DEStIn + An_DEFAIn + An_DErOMIn) \
                * coeff_dict['mPrt_k_DEIn_StFA'] + An_DENDFIn * coeff_dict['mPrt_k_DEIn_NDF'] + (An_BW - 612) * coeff_dict['mPrt_k_BW'] 

    if An_StatePhys != "Lactating Cow":                 # Line 2204
        Mlk_NP_g = 0

    return Mlk_NP_g, An_DigNDF, An_MPIn, An_DEInp


def calculate_Mlk_Fat_g(df, Dt_FAIn, Dt_DigC160In, Dt_DigC183In, An_LactDay, Dt_DMIn):
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

    # An_LactDay_MlkPred
    if An_LactDay <= 375:
        An_LactDay_MlkPred = An_LactDay
    elif An_LactDay > 375:
        An_LactDay_MlkPred = 375

    # (Equation 20-215, p. 440)
    Mlk_Fat_g = 453 - 1.42 * An_LactDay_MlkPred + 24.52 * (Dt_DMIn - Dt_FAIn) + 0.41 * Dt_DigC160In * 1000 + 1.80 * Dt_DigC183In * 1000 + 1.45 * Abs_Ile_g + 1.34 * Abs_Met_g

    return Mlk_Fat_g, An_LactDay_MlkPred


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

    """
    req_coeffs = ['Kl_ME_NE']
    check_coeffs_in_coeff_dict(coeff_dict, req_coeffs)

    An_MEavail_Milk = An_MEIn - An_MEgain - An_MEmUse - Gest_MEuse                      # Line 2896
    Mlk_Prod_NEalow = An_MEavail_Milk * coeff_dict['Kl_ME_NE'] / Trg_NEmilk_Milk                  	# Line 2897, Energy allowable Milk Production, kg/d

    return Mlk_Prod_NEalow