"""Miscellaneous reporting calculations.

This module includes various functions for calculating ratios, percentages, 
and other derived metrics that are part of the NASEM model but are not 
used directly in the core calculations.
"""

import pandas as pd


def calculate_Dt_DMIn_BW(Dt_DMIn: float, An_BW: float) -> float:
    """
    Dt_DMIn_BW: Ratio of DMI to bodyweight
    """
    Dt_DMIn_BW = Dt_DMIn / An_BW  # Line 437
    return Dt_DMIn_BW


def calculate_Dt_DMIn_MBW(Dt_DMIn: float, An_BW: float) -> float:
    """
    Dt_DMIn_MBW: Ratio of DMI to metabolic BW
    """
    Dt_DMIn_MBW = Dt_DMIn / An_BW**0.75  # Line 438
    return Dt_DMIn_MBW


def calculate_percent_first_parity(An_Parity_rl: float) -> float:
    percent_first_parity = (2 - An_Parity_rl) * 100
    return percent_first_parity


def calculate_age_first_calving(An_AgeConcept1st: int) -> int:
    age_first_calving = An_AgeConcept1st + 280
    return age_first_calving  
  

def calculate_milk_lactose_percent(
    Trg_MilkProd: float, 
    Trg_MilkLacp: float
) -> float:
    milk_lactose_percent = Trg_MilkProd * Trg_MilkLacp / 100
    return milk_lactose_percent


def calculate_dmi_percent_bodyweight(An_DMIn_BW: float) -> float:
    dmi_percent_bodyweight = An_DMIn_BW * 100
    return dmi_percent_bodyweight


def calculate_adf_per_ndf(An_ADF: float, An_NDF: float) -> float:
    adf_per_ndf = An_ADF / An_NDF
    return adf_per_ndf


def calculate_digestable_rup(An_idRUP: float) -> float:
    digestable_rup = An_idRUP * 100
    return digestable_rup


def calculate_Fd_AFIn_sum(Fd_AFInp: pd.Series) -> float:
    Fd_AFIn_sum = Fd_AFInp.sum()
    return Fd_AFIn_sum


def calculate_Fd_DMIn_sum(Fd_DMInp: pd.Series) -> float:
    Fd_DMIn_sum = Fd_DMInp.sum()
    return Fd_DMIn_sum


def calculate_Fe_DE_GE_percent(Fe_DE_GE: float) -> float:
    Fe_DE_GE_percent = Fe_DE_GE * 100
    return Fe_DE_GE_percent


def calculate_An_DE_GE_percent(An_DE_GE: float) -> float:
    An_DE_GE_percent = An_DE_GE * 100
    return An_DE_GE_percent


def calculate_UrDE_GEIn_percent(UrDE_GEIn: float) -> float:
    UrDE_GEIn_percent = UrDE_GEIn * 100
    return UrDE_GEIn_percent


def calculate_GasE_GEIn_percent(GasE_GEIn: float) -> float:
    GasE_GEIn_percent = GasE_GEIn * 100
    return GasE_GEIn_percent


def calculate_An_ME_GE_percent(An_ME_GE: float) -> float:
    An_ME_GE_percent = An_ME_GE * 100
    return An_ME_GE_percent


def calculate_An_NE_GE_percent(An_NE_GE: float) -> float:
    An_NE_GE_percent = An_NE_GE * 100
    return An_NE_GE_percent


def calculate_UrDE_DEIn_percent(UrDE_DEIn: float) -> float:
    UrDE_DEIn_percent = UrDE_DEIn * 100
    return UrDE_DEIn_percent


def calculate_GasE_DEIn_percent(GasE_DEIn: float) -> float:
    GasE_DEIn_percent = GasE_DEIn * 100
    return GasE_DEIn_percent


def calculate_An_ME_DE_percent(An_ME_DE: float) -> float:
    An_ME_DE_percent = An_ME_DE * 100
    return An_ME_DE_percent


def calculate_An_NE_DE_percent(An_NE_DE: float) -> float:
    An_NE_DE_percent = An_NE_DE * 100
    return An_NE_DE_percent


def calculate_An_NE_ME_percent(An_NE_ME: float) -> float:
    An_NE_ME_percent = An_NE_ME * 100
    return An_NE_ME_percent


def calculate_An_DEIn_percent(An_DEIn: float) -> float:
    An_DEIn_percent = An_DEIn / An_DEIn * 100
    return An_DEIn_percent


def calculate_An_MEIn_percent(An_MEIn: float) -> float:
    An_MEIn_percent = An_MEIn / An_MEIn * 100
    return An_MEIn_percent


def calculate_Dt_C120In_g(Dt_C120In: float) -> float:
    Dt_C120In_g = Dt_C120In * 1000
    return Dt_C120In_g


def calculate_Dt_C140In_g(Dt_C140In: float) -> float:
    Dt_C140In_g = Dt_C140In * 1000
    return Dt_C140In_g


def calculate_Dt_C160In_g(Dt_C160In: float) -> float:
    Dt_C160In_g = Dt_C160In * 1000
    return Dt_C160In_g


def calculate_Dt_C161In_g(Dt_C161In: float) -> float:
    Dt_C161In_g = Dt_C161In * 1000
    return Dt_C161In_g


def calculate_Dt_C180In_g(Dt_C180In: float) -> float:
    Dt_C180In_g = Dt_C180In * 1000
    return Dt_C180In_g


def calculate_Dt_C181tIn_g(Dt_C181tIn: float) -> float:
    Dt_C181tIn_g = Dt_C181tIn * 1000
    return Dt_C181tIn_g


def calculate_Dt_C181cIn_g(Dt_C181cIn: float) -> float:
    Dt_C181cIn_g = Dt_C181cIn * 1000
    return Dt_C181cIn_g


def calculate_Dt_C182In_g(Dt_C182In: float) -> float:
    Dt_C182In_g = Dt_C182In * 1000
    return Dt_C182In_g


def calculate_Dt_C183In_g(Dt_C183In: float) -> float:
    Dt_C183In_g = Dt_C183In * 1000
    return Dt_C183In_g


def calculate_Dt_OtherFAIn_g(Dt_OtherFAIn: float) -> float:
    Dt_OtherFAIn_g = Dt_OtherFAIn * 1000
    return Dt_OtherFAIn_g


def calculate_Dt_FAIn_g(Dt_FAIn: float) -> float:
    Dt_FAIn_g = Dt_FAIn * 1000
    return Dt_FAIn_g


def calculate_Dt_SatFAIn_g(Dt_SatFAIn: float) -> float:
    Dt_SatFAIn_g = Dt_SatFAIn * 1000
    return Dt_SatFAIn_g


def calculate_Dt_UFAIn_g(Dt_UFAIn: float) -> float:
    Dt_UFAIn_g = Dt_UFAIn * 1000
    return Dt_UFAIn_g


def calculate_Dt_MUFAIn_g(Dt_MUFAIn: float) -> float:
    Dt_MUFAIn_g = Dt_MUFAIn * 1000
    return Dt_MUFAIn_g


def calculate_Dt_PUFAIn_g(Dt_PUFAIn: float) -> float:
    Dt_PUFAIn_g = Dt_PUFAIn * 1000
    return Dt_PUFAIn_g


def calculate_Dt_DigFAIn_g(Dt_DigFAIn: float) -> float:
    Dt_DigFAIn_g = Dt_DigFAIn * 1000
    return Dt_DigFAIn_g


def calculate_An_RDPbal_kg(An_RDPbal_g: float) -> float:
    An_RDPbal_kg = An_RDPbal_g / 1000
    return An_RDPbal_kg


def calculate_MP_from_body(Body_MPUse_g_Trg: float) -> float:
    MP_from_body = -Body_MPUse_g_Trg / 1000 if Body_MPUse_g_Trg < 0 else 0
    return MP_from_body


def calculate_An_BW_centered(An_BW: float) -> float:
    An_BW_centered = An_BW - 612
    return An_BW_centered


def calculate_An_DigNDF_centered(An_DigNDF: float) -> float:
    An_DigNDF_centered = An_DigNDF - 17.06
    return An_DigNDF_centered


def calculate_An_BW_protein(An_BW: float, mPrt_coeff: dict) -> float:
    An_BW_protein = (An_BW - 612) * mPrt_coeff["mPrt_k_BW"]
    return An_BW_protein


def calculate_Dt_acCa_per_100g(Dt_acCa: float) -> float:
    Dt_acCa_per_100g = Dt_acCa * 100
    return Dt_acCa_per_100g


def calculate_Dt_acP_per_100g(Dt_acP: float) -> float:
    Dt_acP_per_100g = Dt_acP * 100
    return Dt_acP_per_100g


def calculate_Dt_acMg_per_100g(Dt_acMg: float) -> float:
    Dt_acMg_per_100g = Dt_acMg * 100
    return Dt_acMg_per_100g


def calculate_Dt_acCl_per_100g(Dt_acCl: float) -> float:
    Dt_acCl_per_100g = Dt_acCl * 100
    return Dt_acCl_per_100g


def calculate_Dt_acK_per_100g(Dt_acK: float) -> float:
    Dt_acK_per_100g = Dt_acK * 100
    return Dt_acK_per_100g


def calculate_Dt_acNa_per_100g(Dt_acNa: float) -> float:
    Dt_acNa_per_100g = Dt_acNa * 100
    return Dt_acNa_per_100g


def calculate_Dt_acCo_per_100g(Dt_acCo: float) -> float:
    Dt_acCo_per_100g = Dt_acCo * 100 if Dt_acCo is not None else 0
    return Dt_acCo_per_100g


def calculate_Dt_acCu_per_100g(Dt_acCu: float) -> float:
    Dt_acCu_per_100g = Dt_acCu * 100
    return Dt_acCu_per_100g


def calculate_Dt_acFe_per_100g(Dt_acFe: float) -> float:
    Dt_acFe_per_100g = Dt_acFe * 100
    return Dt_acFe_per_100g


def calculate_Dt_acMn_per_100g(Dt_acMn: float) -> float:
    Dt_acMn_per_100g = Dt_acMn * 100
    return Dt_acMn_per_100g


def calculate_Dt_acZn_per_100g(Dt_acZn: float) -> float:
    Dt_acZn_per_100g = Dt_acZn * 100
    return Dt_acZn_per_100g


def calculate_An_MPuse_kg_Trg(An_MPuse_g_Trg: float) -> float:
    An_MPuse_kg_Trg = An_MPuse_g_Trg / 1000
    return An_MPuse_kg_Trg


def calculate_Dt_ForNDFIn_percNDF(Dt_ForNDFIn: float, Dt_NDFIn: float) -> float:
    Dt_ForNDFIn_percNDF = Dt_ForNDFIn / Dt_NDFIn * 100
    return Dt_ForNDFIn_percNDF
