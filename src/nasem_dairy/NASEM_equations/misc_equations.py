import math
import pandas as pd
import numpy as np
from nasem_dairy.ration_balancer.ration_balancer_functions import check_coeffs_in_coeff_dict

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

