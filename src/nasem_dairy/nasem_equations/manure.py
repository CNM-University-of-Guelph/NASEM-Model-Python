"""Manure production and composition calculations.

This module includes functions to estimate the production and composition of 
manure, including volatile solids, nitrogen, and minerals.
"""

import numpy as np

def calculate_Man_out(An_StatePhys: str, An_DMIn: float, Dt_K: float) -> float:
    """
    Man_out: kg wet manure production
    """
    Man_out = (-28.3 + 3.6 * An_DMIn + 12.4 * Dt_K if An_StatePhys != "Calf" 
               else None)  # kg wet manure/d, Line 3246-3247
    return Man_out


def calculate_Man_Milk(Man_out: float, Mlk_Prod: float) -> float:
    """
    Man_Milk: kg wet manure / kg milk production
    """
    Man_Milk = Man_out / Mlk_Prod  # kg wet manure/kg milk, Line 3248
    return Man_Milk


def calculate_Man_VolSld(
    Dt_DMIn: float, 
    InfRum_DMIn: float, 
    InfSI_DMIn: float,
    An_NDF: float, 
    An_CP: float
) -> float:
    """
    Man_VolSld: Volatile solids in manure (kg/d)
    """
    # Empirical prediction from Ch 14 of NRC. NDF and CP should exclude arterial Infusions
    Man_VolSld = (0.364 * (Dt_DMIn + InfRum_DMIn + InfSI_DMIn) + 
                  0.026 * An_NDF - 0.078 * An_CP)  # Line 3251
    return Man_VolSld


def calculate_Man_VolSld2(
    Fe_OM: float, 
    Dt_LgIn: float,
    Ur_Nout_g: float
) -> float:
    """
    Man_VolSld: Volatile solids in manure (kg/d)
    """
    # Mass balance based volatile solids output in manure; Ur slightly overestimated by CP
    Man_VolSld2 = Fe_OM - Dt_LgIn + Ur_Nout_g / 0.16 / 1000  # Line 3252
    return Man_VolSld2


def calculate_VolSlds_Milk(Man_VolSld: float, Mlk_Prod: float) -> float:
    """
    VolSlds_Milk: kg manure volatile solids / kg milk production
    """
    VolSlds_Milk = Man_VolSld / Mlk_Prod  # kg/kg, Line 3253
    return VolSlds_Milk


def calculate_VolSlds_Milk2(Man_VolSld2: float, Mlk_Prod: float) -> float:
    """
    VolSlds_Milk2: kg manure volatile solids / kg milk production
    """
    VolSlds_Milk2 = Man_VolSld2 / Mlk_Prod  # kg/kg;  mass balance derived, Line 3254
    return VolSlds_Milk2


def calculate_Man_Nout_g(
    Ur_Nout_g: float, 
    Fe_N_g: float,
    Scrf_N_g: float
) -> float:
    """
    Man_Nout_g: Manure nitrogen by summation of fecal, urinary, and scurf predictions (g/d)
    """
    Man_Nout_g = Ur_Nout_g + Fe_N_g + Scrf_N_g  
    # g/d; direct by summation of fecal, urinary, and scurf predictions, Line 3257
    return Man_Nout_g


def calculate_Man_Nout2_g(An_NIn_g: float, An_Nprod_g: float) -> float:
    """
    Man_Nout2_g: Manure nitrogen from difference in intake and productive N use (g/d)
    """
    Man_Nout2_g = An_NIn_g - An_Nprod_g  
    # g/d; by difference from intake and productive NP use, Line 3258
    return Man_Nout2_g


def calculate_ManN_Milk(Man_Nout_g: float, Mlk_Prod: float) -> float:
    """
    ManN_Milk: g manure N / kg milk production (g/kg)
    """
    if Mlk_Prod != 0 and not np.isnan(Mlk_Prod):
        ManN_Milk = Man_Nout_g / Mlk_Prod # g N / kg of milk, Line 3259
    else:
        ManN_Milk = None
    return ManN_Milk


def calculate_Man_Ca_out(Dt_CaIn: float, An_Ca_prod: float) -> float:
    """
    Man_Ca_out: Manure calcium (g/d)
    """
    Man_Ca_out = Dt_CaIn - An_Ca_prod  # Line 3262
    return Man_Ca_out


def calculate_Man_P_out(Dt_PIn: float, An_P_prod: float) -> float:
    """
    Man_P_out: Manure phosphorus (g/d)
    """
    Man_P_out = Dt_PIn - An_P_prod  # Line 3263
    return Man_P_out


def calculate_Man_Mg_out(Dt_MgIn: float, An_Mg_prod: float) -> float:
    """
    Man_Mg_out: Manure magnesium (g/d)
    """
    Man_Mg_out = Dt_MgIn - An_Mg_prod  # Line 3264
    return Man_Mg_out


def calculate_Man_K_out(Dt_KIn: float, An_K_prod: float) -> float:
    """
    Man_K_out: Manure potassium (g/d)
    """
    Man_K_out = Dt_KIn - An_K_prod  # Line 3265
    return Man_K_out


def calculate_Man_Na_out(Dt_NaIn: float, An_Na_prod: float) -> float:
    """
    Man_Na_out: Manure sodium (g/d)
    """
    Man_Na_out = Dt_NaIn - An_Na_prod  # Line 3266
    return Man_Na_out


def calculate_Man_Cl_out(Dt_ClIn: float, An_Cl_prod: float) -> float:
    """
    Man_Cl_out: Manure chloride (g/d)
    """
    Man_Cl_out = Dt_ClIn - An_Cl_prod  # Line 3267
    return Man_Cl_out


def calculate_Man_MacMin_out(
    Man_Ca_out: float, 
    Man_P_out: float,
    Man_Mg_out: float, 
    Man_K_out: float,
    Man_Na_out: float, 
    Man_Cl_out: float
) -> float:
    """
    Man_MacMin_out: Macrominerals in manure (g/d)
    """
    Man_MacMin_out = (Man_Ca_out + Man_P_out + Man_Mg_out +
                      Man_K_out + Man_Na_out + Man_Cl_out)  # Line 3268
    return Man_MacMin_out


def calculate_Man_Cu_out(Dt_CuIn: float, An_Cu_prod: float) -> float:
    """
    Man_Cu_out: Manure copper (g/d)
    """
    Man_Cu_out = Dt_CuIn - An_Cu_prod  # Line 3272
    return Man_Cu_out


def calculate_Man_Fe_out(Dt_FeIn: float, An_Fe_prod: float) -> float:
    """
    Man_Fe_out: Manure iron (g/d)
    """
    Man_Fe_out = Dt_FeIn - An_Fe_prod  # Line 3273
    return Man_Fe_out


def calculate_Man_Mn_out(Dt_MnIn: float, An_Mn_prod: float) -> float:
    """
    Man_Mn_out: Manure manganese (g/d)
    """
    Man_Mn_out = Dt_MnIn - An_Mn_prod  # Line 3274
    return Man_Mn_out


def calculate_Man_Zn_out(Dt_ZnIn: float, An_Zn_prod: float) -> float:
    """
    Man_Zn_out: Manure zinc (g/d)
    """
    Man_Zn_out = Dt_ZnIn - An_Zn_prod  # Line 3275
    return Man_Zn_out


def calculate_Man_MicMin_out(
    Man_Cu_out: float, 
    Man_Fe_out: float,
    Man_Mn_out: float, 
    Man_Zn_out: float
) -> float:
    """
    Man_MicMin_out: Microminerals in manure (g/d)
    """
    Man_MicMin_out = Man_Cu_out + Man_Fe_out + Man_Mn_out + Man_Zn_out  
    # Not a complete accounting. Many other micros also present, Line 3276
    return Man_MicMin_out


def calculate_Man_Min_out_g(
    Man_MacMin_out: float,
    Man_MicMin_out: float
) -> float:
    """
    Man_Min_out_g: Minerals in manure (g/d)
    """
    Man_Min_out_g = Man_MacMin_out + Man_MicMin_out / 1000  
    # also an incomplete summation as many micros are not represented, Line 3278
    return Man_Min_out_g


def calculate_Man_Wa_out(
    An_StatePhys: str, 
    Man_out: float, 
    Fe_OM: float,
    Ur_Nout_g: float, 
    Man_Min_out_g: float
) -> float:
    """
    Man_Wa_out: Estimated water in manure (L/d)
    """
    if An_StatePhys == "Calf":  # Line 3336
        Man_Wa_out = 0
    else:
        Man_Wa_out = (Man_out - Fe_OM - Ur_Nout_g / 0.45 / 1000 - 
                      Man_Min_out_g / 1000) # Manure Water estimate, L/d, Line 3332
    return Man_Wa_out


def calculate_ManWa_Milk(Man_Wa_out: float, Mlk_Prod: float) -> float:
    """
    ManWa_Milk: Water lost in manure per kg milk production (L/kg)
    """
    ManWa_Milk = Man_Wa_out / Mlk_Prod  # L/kg, Line 3335
    return ManWa_Milk


def calculate_VolSlds2_Milk(Man_VolSld2: float, Mlk_Prod: float) -> float:
    if Mlk_Prod != 0 and not np.isnan(Mlk_Prod):
        VolSlds2_Milk = Man_VolSld2 / Mlk_Prod # kg/kg; mass balance derived
    else:
        VolSlds2_Milk = np.nan 
    return VolSlds2_Milk
