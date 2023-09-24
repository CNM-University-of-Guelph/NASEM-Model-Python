import math
import pandas as pd
import numpy as np
from nasem_dairy.ration_balancer.ration_balancer_functions import check_coeffs_in_coeff_dict

def calculate_Dt_DMIn_Lact1(An_Parity_rl, Trg_MilkProd, An_BW, An_BCS, An_LactDay, Trg_MilkFatp, Trg_MilkTPp, Trg_MilkLacp):
    """
    Animal based dry matter intake (DMI) prediction for lactating cows

    This function predicts the DMI using animal factors only. This is equation 2-1 in the NASEM 8 textbook. In the model
    this prediction can be can be selected by setting DMI_pred to 0 in the 'input.txt'. In :py:func:`NASEM_model` Dt_DMIn_Lact1
    will be returned to the animal_input dictionary with the key 'DMI'.

    Parameters:
        An_Parity_rl (Number): Animal Parity where 1 = Primiparous and 2 = Multiparous.
        Trg_MilkProd (Number): Animal Milk Production in kg/day.
        An_BW (Number): Animal Body Weight in kg.
        An_BCS (Number): Body condition score, from 1-5
        An_LactDay (Number): Day of Lactation.
        Trg_MilkFatp (Percentage): Animal Milk Fat percentage.
        Trg_MilkTPp (Percentage): Animal Milk True Protein percentage.
        Trg_MilkLacp (Percentage): Animal Milk Lactose percentage.

    Returns:
        Dt_DMIn_Lact1 (Number): Dry matter intake, kg/d
    """
    Trg_NEmilk_Milk = 9.29*Trg_MilkFatp/100 + 5.85*Trg_MilkTPp/100 + 3.95*Trg_MilkLacp/100
    Trg_NEmilkOut = Trg_NEmilk_Milk * Trg_MilkProd                                         # Line 386
    
    term1 = (3.7 + 5.7 * (An_Parity_rl - 1) + 0.305 * Trg_NEmilkOut + 0.022 * An_BW +       # Line 389
             (-0.689 - 1.87 * (An_Parity_rl - 1)) * An_BCS)
    term2 = 1 - (0.212 + 0.136 * (An_Parity_rl - 1)) * math.exp(-0.053 * An_LactDay)
    Dt_DMIn_Lact1 = term1 * term2                                                           
    return Dt_DMIn_Lact1


def AA_calculations(Du_MiN_g, feed_data, diet_info, animal_input, coeff_dict):
    """
    Takes the amino acid (AA) supply from the diet and calculates total AA intake

    This takes the AA supply from each feed based on % crude protein and the predicted AA supply from microbial nitrogen (N) 
    and uses this to calculate individual AA flows through the body. 

    Parameters:
        Du_MiN_g (Number): Microbial N supply in g, Du_MiN_NRC2021_g in the model
        feed_data (Dataframe): A dataframe with the composition of each feed ingredient
        diet_info (Dataframe): A dataframe with nutrient supply from the diet
        animal_input (Dictionary): All the user entered animal parameters
        coeff_dict (Dict): Dictionary containing all coefficients for the model
        
    Returns:
        AA_values (Dataframe): Contains all the AA intakes and any values calculated for individual AAs
        Du_MiCP_g (Number): Microbial crude proetin, g
    """
    # This function will get the intakes of AA's from the diet and then do all the calculations of values other functions will need
    # The results will be saved to a dataframe with one row for each AA and a column for each calculated value
    AA_list = ['Arg', 'His', 'Ile', 'Leu', 'Lys', 'Met', 'Phe', 'Thr', 'Trp', 'Val']
    AA_values = pd.DataFrame(index=AA_list)
    Dt_IdAARUPIn = {}

    ####################
    # Get Diet Data
    ####################
    feed_columns = ['Fd_Arg_CP', 'Fd_His_CP', 'Fd_Ile_CP', 'Fd_Leu_CP', 'Fd_Lys_CP', 'Fd_Met_CP', 'Fd_Phe_CP', 'Fd_Thr_CP', 'Fd_Trp_CP', 'Fd_Val_CP', 'Fd_dcRUP']
    df_f = pd.DataFrame(feed_data[feed_columns])
    df_f['Fd_RUPIn'] = pd.Series(diet_info['Fd_RUPIn'])
   
    ####################
    # Define Variables
    ####################
    
    req_coeffs = ['fMiTP_MiCP', 'SI_dcMiCP', 'K_305RHA_MlkTP', 'RecArg', 'RecHis',
    'RecIle', 'RecLeu', 'RecLys', 'RecMet', 'RecPhe',
    'RecThr', 'RecTrp', 'RecVal', 'MiTPArgProf', 'MiTPHisProf',
    'MiTPIleProf', 'MiTPLeuProf', 'MiTPLysProf', 'MiTPMetProf', 'MiTPPheProf',
    'MiTPThrProf', 'MiTPTrpProf', 'MiTPValProf', 'mPrt_k_Arg_src', 'mPrt_k_His_src',
    'mPrt_k_Ile_src', 'mPrt_k_Leu_src', 'mPrt_k_Lys_src', 'mPrt_k_Met_src', 'mPrt_k_Phe_src',
    'mPrt_k_Thr_src', 'mPrt_k_Trp_src', 'mPrt_k_Val_src', 'mPrt_k_EAA2_src']
    check_coeffs_in_coeff_dict(coeff_dict, req_coeffs)
    
    An_305RHA_MlkTP = animal_input['An_305RHA_MlkTP']
    f_mPrt_max = 1 + coeff_dict['K_305RHA_MlkTP'] * (An_305RHA_MlkTP / 280 - 1)       # Line 2116, 280kg RHA ~ 930 g mlk NP/d herd average
    Du_MiCP_g = Du_MiN_g * 6.25                                         # Line 1163
    Du_MiTP_g = coeff_dict['fMiTP_MiCP'] * Du_MiCP_g                                  # Line 1166

    # Digested endogenous protein is ignored as it is a recycle of previously absorbed AA.
    # SI Digestibility of AA relative to RUP digestibility ([g dAA / g AA] / [g dRUP / g RUP])
    # All set to 1 due to lack of clear evidence for deviations.
    SIDigArgRUPf = 1
    SIDigHisRUPf = 1
    SIDigIleRUPf = 1
    SIDigLeuRUPf = 1
    SIDigLysRUPf = 1
    SIDigMetRUPf = 1
    SIDigPheRUPf = 1
    SIDigThrRUPf = 1
    SIDigTrpRUPf = 1
    SIDigValRUPf = 1

    for AA in AA_list:
        ##############################
        # Calculations on Diet Data
        ##############################
        # Fd_AAt_CP         
        df_f['Fd_{}t_CP'.format(AA)] = df_f['Fd_{}_CP'.format(AA)] / coeff_dict['Rec{}'.format(AA)]

        # Fd_AARUPIn         
        df_f['Fd_{}RUPIn'.format(AA)] = df_f['Fd_{}t_CP'.format(AA)] / 100 * df_f['Fd_RUPIn'] * 1000

        # Fd_IdAARUPIn      
        # Note: eval() is used to access SIDig__ values defined above
        df_f['Fd_Id{}RUPIn'.format(AA)] = df_f['Fd_dcRUP'] / 100 * df_f['Fd_{}RUPIn'.format(AA)] * eval('SIDig{}RUPf'.format(AA))
    
        # Dt_IdAARUPIn      
        Dt_IdAARUPIn['Dt_Id{}_RUPIn'.format(AA)] = df_f['Fd_Id{}RUPIn'.format(AA)].sum()

        ########################################
        # Calculations for Microbial Protein and Total AA Intake
        ########################################
        # Du_AAMic      
        AA_values.loc[AA, 'Du_AAMic'] = Du_MiTP_g * coeff_dict['MiTP{}Prof'.format(AA)] / 100         # Line 1573-1582

        # Du_IdAAMic        
        AA_values.loc[AA, 'Du_IdAAMic'] = AA_values.loc[AA, 'Du_AAMic'] * coeff_dict['SI_dcMiCP'] / 100       # Line 1691-1700

        # Abs_AA_g
        # No infusions so Dt_IdAAIn, An_IdAA_In and Abs_AA_g are all the same value in this case
        AA_values.loc[AA, 'Abs_AA_g'] = AA_values.loc[AA, 'Du_IdAAMic'] + Dt_IdAARUPIn['Dt_Id{}_RUPIn'.format(AA)]     # Line 1703, 1714, 1757

        ########################################
        # Calculations for AA coefficients
        ########################################
        #mPrtmx_AA      
        AA_values.loc[AA, 'mPrtmx_AA'] = -(coeff_dict['mPrt_k_{}_src'.format(AA)])**2 / (4 * coeff_dict['mPrt_k_EAA2_src'])
        
        #mPrtmx_AA2        
        AA_values.loc[AA, 'mPrtmx_AA2'] = AA_values.loc[AA, 'mPrtmx_AA'] * f_mPrt_max                   # Line 2149-2158

        #AA_mPrtmx
        AA_values.loc[AA, 'AA_mPrtmx'] = -(coeff_dict['mPrt_k_{}_src'.format(AA)]) / (2 * coeff_dict['mPrt_k_EAA2_src'])

        #mPrt_AA_0.1
        AA_values.loc[AA, 'mPrt_AA_0.1'] = AA_values.loc[AA, 'AA_mPrtmx'] * 0.1 * coeff_dict['mPrt_k_{}_src'.format(AA)] \
                                           + (AA_values.loc[AA, 'AA_mPrtmx'] * 0.1)**2 * coeff_dict['mPrt_k_EAA2_src']

        #mPrt_k_AA
        if AA_values.loc[AA, 'mPrtmx_AA2'] ** 2 - AA_values.loc[AA, 'mPrt_AA_0.1'] * AA_values.loc[AA, 'mPrtmx_AA2'] <= 0 or AA_values.loc[AA, 'AA_mPrtmx'] == 0:
        # Check for sqrt of 0 or divide by 0 errors and set value to 0 if encountered
            AA_values.loc[AA, 'mPrt_k_AA'] = 0
        else:
            AA_values.loc[AA, 'mPrt_k_AA'] = -(2 * np.sqrt(AA_values.loc[AA, 'mPrtmx_AA2'] ** 2 \
                                                - AA_values.loc[AA, 'mPrt_AA_0.1'] * AA_values.loc[AA, 'mPrtmx_AA2']) \
                                                - 2 * AA_values.loc[AA, 'mPrtmx_AA2']) \
                                                / (AA_values.loc[AA, 'AA_mPrtmx'] * 0.1)

    # df_f and Dt_IdAARUPIn not being returned but can be if values are needed outside this function
    # Currently they are not used anywhere else
    return AA_values, Du_MiCP_g



def calculate_GrUter_BWgain(Fet_BWbrth, An_AgeDay, An_GestDay, An_GestLength, An_LactDay, An_Parity_rl, coeff_dict):
    """
    Rate of fresh tissue growth for the gravid uterus

    Parameters:
        Fet_BWbrth (Number): Target calf birth weight in kg
        An_AgeDay (Number): Animal Age in days
        An_GestDay (Number): Day of Gestation
        An_GestLength (Number): Normal Gestation Length in days
        An_LactDay (Number): Day of Lactation
        An_Parity_rl (Number): Animal Parity where 1 = Primiparous and 2 = Multiparous
        coeff_dict (Dict): Dictionary containing all coefficients for the model

    Returns:
        GrUter_BWgain (Number): The rate of fresh tissue growth for the gravid uterus, kg fresh wt/d
    """
    req_coeffs = ['GrUter_Ksyn', 'GrUter_KsynDecay', 'UterWt_FetBWbrth','Uter_Ksyn', 'Uter_KsynDecay', 'Uter_Kdeg',
                  'Uter_Wt', 'GrUterWt_FetBWbrth', 'Uter_BWgain']
    check_coeffs_in_coeff_dict(coeff_dict, req_coeffs)
    
    # Ksyn: Constant for synthesis
    # GrUter_Ksyn: Gravid uterus synthesis rate constant
    # GrUter_KsynDecay: Rate of decay of gravid uterus synthesis approaching parturition
    
    # GrUter_Ksyn = 2.43e-2                                         # Line 2302
    # GrUter_KsynDecay = 2.45e-5                                    # Line 2303
    
    #########################
    # Uter_Wt Calculation
    #########################
    # UterWt_FetBWbrth: kg maternal tissue/kg calf weight at parturition
    # Uter_Wtpart: Maternal tissue weight (uterus plus caruncles) at parturition
    # Uter_Ksyn: Uterus synthesis rate
    # Uter_KsynDecay: Rate of decay of uterus synthesis approaching parturition
    # Uter_Kdeg: Rate of uterine degradation
    # Uter_Wt: Weight of maternal tissue
    
    # UterWt_FetBWbrth = 0.2311                                     # Line 2296
    Uter_Wtpart = Fet_BWbrth * coeff_dict['UterWt_FetBWbrth']                   # Line 2311
    # Uter_Ksyn = 2.42e-2                                           # Line 2306
    # Uter_KsynDecay = 3.53e-5                                      # Line 2307
    # Uter_Kdeg = 0.20                                              # Line 2308
    
    # DI - uncommenting this first assignment of Uter_Wt to avoid error where
    # last if statement is checking Uter_Wt which may not have been defined yet in some cases and can fail
    Uter_Wt = 0.204                                               # Line 2312-2318

    if An_AgeDay < 240:
        Uter_Wt = 0 

    if An_GestDay > 0 and An_GestDay <= An_GestLength:
        Uter_Wt = Uter_Wtpart * math.exp(-(coeff_dict['Uter_Ksyn'] - coeff_dict['Uter_KsynDecay'] * An_GestDay) * (An_GestLength - An_GestDay))  

    if An_GestDay <= 0 and An_LactDay > 0 and An_LactDay < 100:
        Uter_Wt = (Uter_Wtpart-0.204) * math.exp(-coeff_dict['Uter_Kdeg'] * An_LactDay)+0.204

    if An_Parity_rl > 0 and Uter_Wt < 0.204:
        Uter_Wt = 0.204
    
    #########################
    # GrUter_Wt Calculation
    ######################### 
    # GrUterWt_FetBWbrth: kg of gravid uterus/ kg of calf birth weight
    # GrUter_Wtpart: Gravid uterus weight at parturition
    # GrUter_Wt: Gravid uterine weight
    
    # GrUterWt_FetBWbrth = 1.816                                    # Line 2295
    GrUter_Wtpart = Fet_BWbrth * coeff_dict['GrUterWt_FetBWbrth']               # Line 2322
    GrUter_Wt = Uter_Wt                                           # Line 2323-2327   
    
    if An_GestDay > 0 and An_GestDay <= An_GestLength:
        GrUter_Wt = GrUter_Wtpart * math.exp(-(coeff_dict['GrUter_Ksyn'] - coeff_dict['GrUter_KsynDecay'] * An_GestDay)*(An_GestLength-An_GestDay))
    
    if GrUter_Wt < Uter_Wt:
        GrUter_Wt = Uter_Wt
    
    #########################
    # ME Gestation Calculation
    #########################
    # Uter_BWgain: Rate of fresh tissue growth for maternal reproductive tissue
    # GrUter_BWgain: Rate of fresh tissue growth for gravid uterus
    # NE_GrUtWt: mcal NE/kg of fresh gravid uterus weight at birth
    # Gest_REgain: NE for gestation
    # Ky_ME_NE: Conversion of NE to ME for gestation
    
    # Uter_BWgain = 0  #Open and nonregressing animal

    if An_GestDay > 0 and An_GestDay <= An_GestLength:
        Uter_BWgain = (coeff_dict['Uter_Ksyn'] - coeff_dict['Uter_KsynDecay'] * An_GestDay) * Uter_Wt

    if An_GestDay <= 0 and An_LactDay > 0 and An_LactDay < 100:                 #uterine involution after calving
        Uter_BWgain = -coeff_dict['Uter_Kdeg'] * Uter_Wt
    GrUter_BWgain = 0                                              # Line 2341-2345

    if An_GestDay > 0 and An_GestDay <= An_GestLength:
        GrUter_BWgain = (coeff_dict['GrUter_Ksyn'] - coeff_dict['GrUter_KsynDecay'] * An_GestDay) * GrUter_Wt

    if An_GestDay <= 0 and An_LactDay > 0 and An_LactDay < 100:
        GrUter_BWgain = Uter_BWgain

    return GrUter_BWgain, GrUter_Wt

