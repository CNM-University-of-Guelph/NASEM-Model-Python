# Protein equations
import numpy as np
import pandas as pd
from nasem_dairy.ration_balancer.ration_balancer_functions import check_coeffs_in_coeff_dict


def calculate_f_mPrt_max(An_305RHA_MlkTP, coeff_dict):
    req_coeffs = ['K_305RHA_MlkTP']
    check_coeffs_in_coeff_dict(coeff_dict, req_coeffs)
    # Line 2116, 280kg RHA ~ 930 g mlk NP/d herd average
    f_mPrt_max = 1 + coeff_dict['K_305RHA_MlkTP'] * (An_305RHA_MlkTP / 280 - 1)
    return f_mPrt_max


def calculate_Du_MiCP_g(Du_MiN_g):
    Du_MiCP_g = Du_MiN_g * 6.25     # Line 1163
    return Du_MiCP_g


def calculate_Du_MiTP_g(Du_MiCP_g, coeff_dict):
    req_coeffs = ['fMiTP_MiCP']
    check_coeffs_in_coeff_dict(coeff_dict, req_coeffs)
    Du_MiTP_g = coeff_dict['fMiTP_MiCP'] * Du_MiCP_g     # Line 1166
    return Du_MiTP_g


def calculate_Scrf_CP_g(An_StatePhys: str, An_BW: float) -> float:
    """
    Scrf_CP_g: Scurf CP, g
    """
    if An_StatePhys == "Calf":
        Scrf_CP_g = 0.219 * An_BW**0.60 # Line 1965
    else:
        Scrf_CP_g = 0.20 * An_BW**0.60   # Line 1964
    return Scrf_CP_g


def calculate_Scrf_NP_g(Scrf_CP_g: float, coeff_dict: dict) -> float:
    """
    Scrf_NP_g: Scurf Net Protein, g
    """
    req_coeff = ['Body_NP_CP']
    check_coeffs_in_coeff_dict(coeff_dict, req_coeff)
    Scrf_NP_g = Scrf_CP_g * coeff_dict['Body_NP_CP']    # Line 1966
    return Scrf_NP_g


def calculate_Scrf_MPUse_g_Trg(An_StatePhys: str, Scrf_CP_g: float, Scrf_NP_g: float, coeff_dict: dict) -> float:
    """
    Scrf_MPuse_g_Trg: Scurf Metabolizable protein, g
    """
    req_coeff = ['Km_MP_NP_Trg']
    check_coeffs_in_coeff_dict(coeff_dict, req_coeff)
    if An_StatePhys == "Calf" or An_StatePhys == "Heifer":
        Scrf_MPUse_g_Trg = Scrf_CP_g / coeff_dict['Km_MP_NP_Trg']   # calves and heifers are CP based., Line 2671
    else:
        Scrf_MPUse_g_Trg = Scrf_NP_g / coeff_dict['Km_MP_NP_Trg']   # Line 2670
    return Scrf_MPUse_g_Trg


def calculate_Scrf_NP(Scrf_NP_g: float) -> float:
    """
    Scrf_NP: Scurf net protein (kg/d)
    """
    Scrf_NP = Scrf_NP_g * 0.001 # Line 1967
    return Scrf_NP


def calculate_Scrf_N_g(Scrf_CP_g: float) -> float:
    """
    Scrf_N_g: Scurf N (g/d)
    """
    Scrf_N_g = Scrf_CP_g * 0.16    # Line 1968
    return Scrf_N_g


def calculate_Scrf_AA_g(Scrf_NP_g: float, coeff_dict: dict, AA_list: list) -> np.array:
    """
    Scrf_AA_g: AA in scurf (g/d)
    """
    Scrf_AA_TP = np.array([coeff_dict[f"Scrf_{AA}_TP"] for AA in AA_list])
    Scrf_AA_g = Scrf_NP_g * Scrf_AA_TP / 100    # Lines 1969-1978
    return Scrf_AA_g


def calculate_ScrfAA_AbsAA(Scrf_AA_g: pd.Series, Abs_AA_g: pd.Series) -> np.array:
    """
    ScrfAA_AbsAA: Scurf AA as a fraction of absorbed AA
    """
    ScrfAA_AbsAA = Scrf_AA_g / Abs_AA_g # Line 1981-1990
    return ScrfAA_AbsAA
