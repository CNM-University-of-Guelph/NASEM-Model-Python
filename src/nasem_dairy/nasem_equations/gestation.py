"""Gestation-related calculations for fetal growth and uterine changes.

This module covers the estimation of fetal growth, uterine weight changes, and 
nutrient requirements during pregnancy.
"""

import math

import numpy as np
import pandas as pd


def calculate_Uter_Wtpart(Fet_BWbrth: float, coeff_dict: dict) -> float:
    """
    Examples
    --------
    ```
    coeff_dict = {"UterWt_FetBWbrth": 1.816}
    
    calculate_Uter_Wtpart(
        Fet_BWbrth = 30.0, coeff_dict = coeff_dict
    )
    ```
    """
    Uter_Wtpart = Fet_BWbrth * coeff_dict['UterWt_FetBWbrth']
    return Uter_Wtpart


def calculate_Uter_Wt(
    An_Parity_rl: int, 
    An_AgeDay: int, 
    An_LactDay: int, 
    An_GestDay: int,
    An_GestLength: int, 
    Uter_Wtpart: float, 
    coeff_dict: dict
) -> float:
    """
    Examples
    --------
    ```
    coeff_dict = {
        "Uter_Wt": 0.204, "Uter_Ksyn": 2.42e-2, "Uter_KsynDecay": 3.53e-5, 
        "Uter_Kdeg": 0.20
    }
    
    calculate_Uter_Wt(
        An_Parity_rl = 1, An_AgeDay = 250, An_LactDay = 50, An_GestDay = 150, 
        An_GestLength = 280, Uter_Wtpart = 45.0, coeff_dict = coeff_dict
    )
    ```
    """
    Uter_Wt = coeff_dict['Uter_Wt_coeff']  # Line 2312
    if An_AgeDay < 240:  # Line 2313
        Uter_Wt = 0

    if An_GestDay > 0 and An_GestDay <= An_GestLength:  # Line 2314
        Uter_Wt = (Uter_Wtpart * 
                   math.exp(-(coeff_dict['Uter_Ksyn'] - 
                              coeff_dict['Uter_KsynDecay'] * An_GestDay) * 
                              (An_GestLength - An_GestDay)))
    
    if An_GestDay <= 0 and An_LactDay > 0 and An_LactDay < 100:  # Line 2316
        Uter_Wt = ((Uter_Wtpart-0.204) * 
                   math.exp(-coeff_dict['Uter_Kdeg'] * An_LactDay) + 0.204)

    if An_Parity_rl > 0 and Uter_Wt < 0.204:  # Line 2318
        Uter_Wt = 0.204
    return Uter_Wt


def calculate_GrUter_Wtpart(Fet_BWbrth: float, coeff_dict: dict) -> float:
    """
    GrUterWt_FetBWbrth default 1.816 based on equation 20-225
    See Equation 3-15a, supposed to be 1.825?
    
    Examples
    --------
    ```
    coeff_dict = {"GrUterWt_FetBWbrth": 1.816}
    
    calculate_GrUter_Wtpart(
        Fet_BWbrth = 30.0, coeff_dict = coeff_dict
    )
    ```
    """
    GrUter_Wtpart = Fet_BWbrth * coeff_dict['GrUterWt_FetBWbrth'] # Line 2322
    return GrUter_Wtpart


def calculate_GrUter_Wt(
    An_GestDay: int, 
    An_GestLength: int, 
    Uter_Wt: float, 
    GrUter_Wtpart: float,
    coeff_dict: dict
) -> float:
    """
    Examples
    --------
    ```
    coeff_dict = {
        "GrUter_Ksyn": 2.43e-2, "GrUter_KsynDecay": 2.45e-5
    }
    
    calculate_GrUter_Wt(
        An_GestDay = 150, An_GestLength = 280, Uter_Wt = 40.0, 
        GrUter_Wtpart = 55.0, coeff_dict = coeff_dict
    )
    ```
    """
    GrUter_Wt = Uter_Wt
    if An_GestDay > 0 and An_GestDay <= An_GestLength:  # Line 2323-2327
        GrUter_Wt = (GrUter_Wtpart * 
                     math.exp(-(coeff_dict['GrUter_Ksyn'] - 
                                coeff_dict['GrUter_KsynDecay'] * An_GestDay) * 
                                (An_GestLength - An_GestDay)))
    if GrUter_Wt < Uter_Wt:
        GrUter_Wt = Uter_Wt
    return GrUter_Wt


def calculate_Uter_BWgain(
    An_LactDay: int, 
    An_GestDay: int, 
    An_GestLength: int, 
    Uter_Wt: float,
    coeff_dict: dict
) -> float:
    """
    Examples
    --------
    ```
    coeff_dict = {
        "Uter_BWgain": 0, "Uter_Ksyn": 2.42e-2, "Uter_KsynDecay": 3.53e-5, 
        "Uter_Kdeg": 0.20
    }
    
    calculate_Uter_BWgain(
        An_LactDay = 50, An_GestDay = 150, An_GestLength = 280, Uter_Wt = 45.0, 
        coeff_dict = coeff_dict
    )
    ```
    """
    Uter_BWgain = coeff_dict['Uter_BWgain_coeff']
    if An_GestDay > 0 and An_GestDay <= An_GestLength:
        Uter_BWgain = (coeff_dict['Uter_Ksyn'] -
                       coeff_dict['Uter_KsynDecay'] * An_GestDay) * Uter_Wt
    if An_GestDay <= 0 and An_LactDay > 0 and An_LactDay < 100: 
        # uterine involution after calving
        Uter_BWgain = -coeff_dict['Uter_Kdeg'] * Uter_Wt
    return Uter_BWgain


def calculate_GrUter_BWgain(
    An_LactDay: int, 
    An_GestDay: int, 
    An_GestLength: int, 
    GrUter_Wt: float,
    Uter_BWgain: float, 
    coeff_dict: dict
) -> float:
    """
    Equation 3-17a
    
    Examples
    --------
    ```
    coeff_dict = {
        "GrUter_BWgain": 0, "GrUter_Ksyn": 2.43e-2, "GrUter_KsynDecay": 2.45e-5
    }
    
    calculate_GrUter_BWgain(
        An_LactDay = 50, An_GestDay = 150, An_GestLength = 280, 
        GrUter_Wt = 50.0, Uter_BWgain = 0.5, coeff_dict = coeff_dict
    )
    ```
    """
    GrUter_BWgain = coeff_dict['GrUter_BWgain_coeff']  # Line 2341-2345
    if An_GestDay > 0 and An_GestDay <= An_GestLength:
        GrUter_BWgain = (
            coeff_dict['GrUter_Ksyn'] -
            coeff_dict['GrUter_KsynDecay'] * An_GestDay) * GrUter_Wt
    if An_GestDay <= 0 and An_LactDay > 0 and An_LactDay < 100:
        GrUter_BWgain = Uter_BWgain
    return GrUter_BWgain


def calculate_Gest_NCPgain_g(
    GrUter_BWgain: float, 
    coeff_dict: dict
) -> float:
    """
    Examples
    --------
    ```
    coeff_dict = {"CP_GrUtWt": 0.123}
    
    calculate_Gest_NCPgain_g(
        GrUter_BWgain = 50.0, coeff_dict = coeff_dict
    )
    ```
    """
    Gest_NCPgain_g = GrUter_BWgain * coeff_dict['CP_GrUtWt'] * 1000
    return Gest_NCPgain_g


def calculate_Gest_NPgain_g(Gest_NCPgain_g: float, coeff_dict: dict) -> float:
    """
    Examples
    --------
    ```
    coeff_dict = {"Body_NP_CP": 0.86}
    
    calculate_Gest_NPgain_g(
        Gest_NCPgain_g = 2.5, coeff_dict = coeff_dict
    )
    ```
    """
    Gest_NPgain_g = Gest_NCPgain_g * coeff_dict['Body_NP_CP']
    return Gest_NPgain_g


def calculate_Gest_NPuse_g(Gest_NPgain_g: float, coeff_dict: dict) -> float:
    """
    Examples
    --------
    ```
    coeff_dict = {"Gest_NPother_g": 0}
    
    calculate_Gest_NPuse_g(
        Gest_NPgain_g = 2.0, coeff_dict = coeff_dict
    )
    ```
    """
    Gest_NPuse_g = Gest_NPgain_g + coeff_dict['Gest_NPother_g']  # Line 2366
    return Gest_NPuse_g


def calculate_Gest_CPuse_g(Gest_NPuse_g: float, coeff_dict: dict) -> float:
    """
    Examples
    --------
    ```
    coeff_dict = {"Body_NP_CP": 0.86}
    
    calculate_Gest_CPuse_g(
        Gest_NPuse_g = 2.1, coeff_dict = coeff_dict
    )
    ```
    """
    Gest_CPuse_g = Gest_NPuse_g / coeff_dict['Body_NP_CP']  # Line 2367
    return Gest_CPuse_g


def calculate_An_PostPartDay(An_LactDay: int) -> int:
    """
    An_LactDay: Day of lactation
    An_PostPartDay: Days postpartum 
    """
    # Calculate day postpartum and trap nonsense values
    if An_LactDay <= 0:  # Line 220
        An_PostPartDay = 0
    elif An_LactDay > 100:  # Line 221
        An_PostPartDay = 100
    else:
        An_PostPartDay = An_LactDay
    return An_PostPartDay


def calculate_An_Preg(An_GestDay: int, An_GestLength: int) -> int:
    """
    An_Preg: 0 if not pregnant, 1 if pregnant
    """
    #Create a pregnancy switch for use in calculations.
    if (An_GestDay > 0) & (An_GestDay <= An_GestLength):  # Line 2293
        An_Preg = 1
    else:
        An_Preg = 0
    return An_Preg


def calculate_Fet_Wt(
    An_GestDay: int, 
    An_GestLength: int, 
    Fet_BWbrth: float,
    coeff_dict: dict
) -> float:
    """
    Fet_Wt: Fetal weight at any time (kg)
    
    Examples
    --------
    ```
    coeff_dict = {"Fet_Ksyn": 5.16e-2, "Fet_KsynDecay": 7.59e-5}
    
    calculate_Fet_Wt(
        An_GestDay = 150, An_GestLength = 280, Fet_BWbrth = 40.0, 
        coeff_dict = coeff_dict
    )
    ```
    """
    if (An_GestDay > 0) & (An_GestDay <= An_GestLength):  # Line 2231-2232
        Fet_Wt = (Fet_BWbrth * 
                  np.exp(-(coeff_dict['Fet_Ksyn'] - 
                           coeff_dict['Fet_KsynDecay'] * An_GestDay) * 
                           (An_GestLength - An_GestDay))) # gestating animal
    else:
        Fet_Wt = 0  # open animal
    return Fet_Wt


def calculate_Fet_BWgain(
    An_GestDay: int, 
    An_GestLength: int, 
    Fet_Wt: float,
    coeff_dict: dict
) -> float:
    """
    Fet_BWgain: Fetal bodyweight gain (kg/d)
    """
    if (An_GestDay > 0) & (An_GestDay <= An_GestLength): # gestating animal
        Fet_BWgain = (coeff_dict['Fet_Ksyn'] - 
                      coeff_dict['Fet_KsynDecay'] * An_GestDay) * Fet_Wt 
    else:
        Fet_BWgain = 0  # open animal, kg/d
    return Fet_BWgain


def calculate_Gest_AA_g(
    Gest_NPuse_g: float, 
    Body_AA_TP: np.ndarray
) -> np.ndarray:
    """
    Gest_AA_g: AA deposited in gravid uterus (g/d)
    """
    Gest_AA_g = Gest_NPuse_g * Body_AA_TP / 100  # Line 2367-2376
    return Gest_AA_g


def calculate_Gest_EAA_g(Gest_AA_g: pd.Series) -> float:
    """
    Gest_EAA_g: EAA deposited in gravid uterus (g/d)
    """
    Gest_EAA_g = Gest_AA_g.sum()  # Line 2377-2378
    return Gest_EAA_g


def calculate_GestAA_AbsAA(
    Gest_AA_g: pd.Series,
    Abs_AA_g: pd.Series
) -> pd.Series:
    """
    GestAA_AbsAA: AA debosited in gravid uterus as a fraction of absorbed AA 
    """
    GestAA_AbsAA = Gest_AA_g / Abs_AA_g  # Line 2381-2390
    return GestAA_AbsAA
