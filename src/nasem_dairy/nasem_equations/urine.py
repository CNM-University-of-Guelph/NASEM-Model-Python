"""Urinary excretion calculations.

This module contains functions to estimate the excretion of nitrogen and other 
components in urine.
"""

import numpy as np
import pandas as pd


def calculate_Ur_Nout_g(
    Dt_CPIn: float, 
    Fe_CP: float, 
    Scrf_CP_g: float, 
    Fe_CPend_g: float, 
    Mlk_CP_g: float,
    Body_CPgain_g: float, 
    Gest_CPuse_g: float
) -> float:
    Ur_Nout_g = (Dt_CPIn * 1000 - Fe_CP * 1000 - Scrf_CP_g - Fe_CPend_g -
                 Mlk_CP_g - Body_CPgain_g - Gest_CPuse_g) / 6.25  # Line 2742
    return Ur_Nout_g


def calculate_Ur_DEout(Ur_Nout_g: float) -> float:
    Ur_DEout = 0.0143 * Ur_Nout_g  # Line 2748
    return Ur_DEout


def calculate_Ur_Nend_g(An_BW: float) -> float:
    """
    Ur_Nend_g: Urinary endogenous N, g
    """
    Ur_Nend_g = 0.053 * An_BW  # approximates Ur_Nend_sum, Line 2029
    return Ur_Nend_g


def calculate_Ur_NPend_g(
    An_StatePhys: str, 
    An_BW: float, 
    Ur_Nend_g: float
) -> float:
    """
    Ur_NPend_g: Urinary endogenous Net protein, g
    """
    if An_StatePhys == "Calf":
        Ur_NPend_g = 2.75 * An_BW**0.50
    else:    
        Ur_NPend_g = Ur_Nend_g * 6.25  # Line 2030
    return Ur_NPend_g


def calculate_Ur_MPendUse_g(Ur_NPend_g: float) -> float:
    """
    Ur_MPendUse_g: Urinary endogenous Metabolizable protein, g
    """
    Ur_MPendUse_g = Ur_NPend_g  # Line 2672
    return Ur_MPendUse_g


def calculate_Ur_Nend_Urea_g(An_BW: float) -> float:
    """
    Ur_Nend_Urea_g: endogenous urea N (g/d)
    """
    Ur_Nend_Urea_g = 0.010 * An_BW  # endogenous urea N, g/d, Line 2018
    return Ur_Nend_Urea_g


def calculate_Ur_Nend_Creatn_g(An_BW: float) -> float:
    """
    Ur_Nend_Creatn_g: ndogenous creatinine N (g/d)
    """
    Ur_Nend_Creatn_g = 0.00946 * An_BW # endogenous creatinine N, g/d, Line 2019
    return Ur_Nend_Creatn_g


def calculate_Ur_Nend_Creat_g(Ur_Nend_Creatn_g: float) -> float:
    """
    Ur_Nend_Creat_g: endogenous creatine N (g/d)
    """
    Ur_Nend_Creat_g = Ur_Nend_Creatn_g * 0.37  
    # endogenous creatine N, g/d, Line 2020
    return Ur_Nend_Creat_g


def calculate_Ur_Nend_PD_g(An_BW: float) -> float:
    """
    Ur_Nend_PD_g: endogenous purine derivative N g/d
    """
    Ur_Nend_PD_g = 0.0271 * An_BW**0.75  
    # endogenous purine derivative N, g/d, Line 2021
    return Ur_Nend_PD_g


def calculate_Ur_NPend_3MH_g(An_BW: float) -> float:
    """
    Ur_NPend_3MH_g: endogenous 3-methyl-histidine NP (g/d)
    """
    Ur_NPend_3MH_g = (7.84 + 0.55 * An_BW) / 1000  
    # endogenous 3-methyl-histidine NP, g/d, Line 2023
    return Ur_NPend_3MH_g


def calculate_Ur_Nend_3MH_g(Ur_NPend_3MH_g: float, coeff_dict: dict) -> float:
    """
    Ur_Nend_3MH_g: endogenous 3-methyl-histidine N (g/d)
    
    Examples
    --------
    ```
    coeff_dict = {'fN_3MH': 0.249}

    calculate_Ur_Nend_3MH_g(
        Ur_NPend_3MH_g = 200.0, coeff_dict = coeff_dict
    )
    ```
    """
    Ur_Nend_3MH_g = Ur_NPend_3MH_g * coeff_dict['fN_3MH']  # Line 2024
    return Ur_Nend_3MH_g


def calculate_Ur_Nend_sum_g(
    Ur_Nend_Urea_g: float, 
    Ur_Nend_Creatn_g: float,
    Ur_Nend_Creat_g: float, 
    Ur_Nend_PD_g: float,
    Ur_Nend_3MH_g: float
) -> float:
    """
    Ur_Nend_sum_g: Total urinary endogenous N (g/d)
    """
    Ur_Nend_sum_g = (Ur_Nend_Urea_g + Ur_Nend_Creatn_g + Ur_Nend_Creat_g + 
                     Ur_Nend_PD_g + Ur_Nend_3MH_g) / (1 - 0.46) # Line 2025-2026
    return Ur_Nend_sum_g


def calculate_Ur_Nend_Hipp_g(Ur_Nend_sum_g: float) -> float:
    """
    Ur_Nend_Hipp_g: Urinary N in hippuric acid (g/d)
    """
    Ur_Nend_Hipp_g = Ur_Nend_sum_g * 0.46  
    # 46% of the total end is hippuric acid, Line 2027
    return Ur_Nend_Hipp_g


def calculate_Ur_NPend(Ur_NPend_g: float) -> float:
    """
    Ur_NPend: Endogenous net protein in urine (kg/d)
    """
    Ur_NPend = Ur_NPend_g * 0.001  # Line 2032
    return Ur_NPend


def calculate_Ur_MPend(Ur_NPend: float) -> float:
    """
    Ur_MPend: Endogenous metabolizable protein in urine
    """
    Ur_MPend = Ur_NPend  # Line 2033
    return Ur_MPend


def calculate_Ur_EAAend_g(An_BW: float) -> float:
    """
    Ur_EAAend_g: Endogenous EAA in urine (g/d)
    """
    Ur_EAAend_g = 0.010 * 6.25 * An_BW  
    # includes only the MP-EAA used for urea and 3-MHis, Line 2034
    return Ur_EAAend_g


def calculate_Ur_AAEnd_TP(aa_list: list, coeff_dict: dict) -> np.ndarray:
    Ur_AAEnd_TP = np.array([coeff_dict[f"Ur_{aa}End_TP"] for aa in aa_list])
    return Ur_AAEnd_TP


def calculate_Ur_AAEnd_g(
    Ur_EAAend_g: float, 
    Ur_NPend_3MH_g: float,
    Ur_AAEnd_TP: np.ndarray
) -> pd.Series:
    """
    Ur_AAEnd_g: Endogenous AA in urine (g/d)
    """
    Ur_AAEnd_g = Ur_EAAend_g * Ur_AAEnd_TP / 100  # Line 2036-2045
    Ur_AAEnd_g[1] += Ur_NPend_3MH_g  # Urea plus 3-MHis, Line 2037
    return Ur_AAEnd_g


def calculate_Ur_AAEnd_AbsAA(
    Ur_AAEnd_g: np.array,
    Abs_AA_g: pd.Series
) -> np.array:
    """
    Ur_AAEnd_AbsAA: Endogenous AA in urine as fraction of absorbed AA
    """
    Ur_AAEnd_AbsAA = Ur_AAEnd_g / Abs_AA_g  # Line 2048-2057
    return Ur_AAEnd_AbsAA


def calculate_Ur_EAAEnd_g(Ur_AAEnd_g: np.array) -> float:
    """
    Ur_EAAEnd_g: Total EAA in urine (g/d) 
    """
    Ur_EAAEnd_g = Ur_AAEnd_g.sum()  # Line 2059-2061
    return Ur_EAAEnd_g


def calculate_Ur_Nout_DigNIn(Ur_Nout_g: float, An_DigCPtIn: float) -> float:
    """
    Ur_Nout_DigNIn: % of digestable N lost in urine
    """
    Ur_Nout_DigNIn = Ur_Nout_g / (An_DigCPtIn * 1000 / 6.25) * 100  # Line 2744
    return Ur_Nout_DigNIn


def calculate_Ur_Nout_CPcatab(Ur_Nout_g: float, Ur_Nend_g: float) -> float:
    """
    Ur_Nout_CPcatab: Urinary loss of N from CP catabolism? (g/d)
    """
    Ur_Nout_CPcatab = Ur_Nout_g - Ur_Nend_g  
    # primarily AA catab, but also absorbed non-MP N such as PD, Line 2745
    return Ur_Nout_CPcatab


def calculate_UrDE_DMIn(Ur_DEout: float, An_DMIn: float) -> float:
    """
    UrDE_DMIn: Urinary DE loss as a fraction of DMI (Mcal/kg)
    """
    UrDE_DMIn = Ur_DEout / An_DMIn  # Line 2748
    return UrDE_DMIn


def calculate_UrDE_GEIn(Ur_DEout: float, An_GEIn: float) -> float:
    """
    UrDE_GEIn: Urinary DE loss as a fraction of GE intake (Mcal/Mcal)
    """
    UrDE_GEIn = Ur_DEout / An_GEIn  # Line 2749
    return UrDE_GEIn


def calculate_UrDE_DEIn(Ur_DEout: float, An_DEIn: float) -> float:
    """
    UrDE_DEIn: Urinary DE loss as a fraction of DE intake (Mcal/Mcal)
    """
    UrDE_DEIn = Ur_DEout / An_DEIn  # Line 2750
    return UrDE_DEIn
