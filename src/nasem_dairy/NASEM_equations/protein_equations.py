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


def calculate_An_CPxprt_g(Scrf_CP_g: float, Fe_CPend_g: float, Mlk_CP_g: float, Body_CPgain_g: float) -> float:
    """
    An_CPxprt_g: CP used for export protein (g/d)
    """
    An_CPxprt_g = Scrf_CP_g + Fe_CPend_g + Mlk_CP_g + Body_CPgain_g  # Initially defined only as true export protein, but it has migrated to include other prod proteins, Line 2525
    return An_CPxprt_g


def calculate_An_NPxprt_g(Scrf_NP_g: float, Fe_NPend_g: float, Mlk_NP_g: float, Body_NPgain_g: float) -> float:
    """
    An_NPxprt_g: NP used for export protein (g/d)
    """
    An_NPxprt_g = Scrf_NP_g + Fe_NPend_g + Mlk_NP_g + Body_NPgain_g  # Should have changed the name, Line 2526
    return An_NPxprt_g


def calculate_Trg_NPxprt_g(Scrf_NP_g: float, Fe_NPend_g: float, Trg_Mlk_NP_g: float, Body_NPgain_g: float) -> float:
    """
    Trg_NPxprt_g: NP used for export protein (g/d)
    """
    Trg_NPxprt_g = Scrf_NP_g + Fe_NPend_g + Trg_Mlk_NP_g + Body_NPgain_g  # Shouldn't these also include Gest??, Line 2527
    return Trg_NPxprt_g


def calculate_An_CPprod_g(Mlk_CP_g: float, Gest_NCPgain_g: float, Body_CPgain_g: float) -> float:
    """
    An_CPprod_g: CP use for production (g/d)
    """
    An_CPprod_g = Mlk_CP_g + Gest_NCPgain_g + Body_CPgain_g # CP use for production.  Be careful not to double count Gain. Line 2529
    return An_CPprod_g


def calculate_An_NPprod_g(Mlk_NP_g: float, Gest_NPgain_g: float, Body_NPgain_g: float) -> float:
    """
    An_NPprod_g: NP use for production (g/d)
    """
    An_NPprod_g = Mlk_NP_g + Gest_NPgain_g + Body_NPgain_g # NP use for production, Line 2530
    return An_NPprod_g


def calculate_Trg_NPprod_g(Trg_Mlk_NP_g: float, Gest_NPgain_g: float, Body_NPgain_g: float) -> float:
    """
    Trg_NPprod_g: NP used fpr production (g/d)
    """
    Trg_NPprod_g = Trg_Mlk_NP_g + Gest_NPgain_g + Body_NPgain_g # NP needed for production target, Line 2531
    return Trg_NPprod_g


def calculate_An_NPprod_MPIn(An_NPprod_g: float, An_MPIn_g: float) -> float:
    """
    An_NPprod_MPIn: NP used for produciton as fraction of metabolizable protein
    """
    An_NPprod_MPIn = An_NPprod_g / An_MPIn_g    # Line 2532
    return An_NPprod_MPIn


def calculate_Trg_NPuse_g(Scrf_NP_g: float, Fe_NPend_g: float, Ur_NPend_g: float, Trg_Mlk_NP_g: float, Body_NPgain_g: float, Gest_NPgain_g: float) -> float:
    """
    Trg_NPuse_g: Target NP use (g/d)
    """
    Trg_NPuse_g = Scrf_NP_g + Fe_NPend_g + Ur_NPend_g + Trg_Mlk_NP_g + Body_NPgain_g + Gest_NPgain_g    # Line 2535
    return Trg_NPuse_g


def calculate_An_NPuse_g(Scrf_NP_g: float, Fe_NPend_g: float, Ur_NPend_g: float, Mlk_NP_g: float, Body_NPgain_g: float, Gest_NPgain_g: float) -> float:
    """
    An_NPuse_g: NP use (g/d)
    """
    An_NPuse_g = Scrf_NP_g + Fe_NPend_g + Ur_NPend_g + Mlk_NP_g + Body_NPgain_g + Gest_NPgain_g  # includes only net use of true protein.  Excludes non-protein maintenance use, Line 2536 
    return An_NPuse_g


def calculate_An_NCPuse_g(Scrf_CP_g: float, Fe_CPend_g: float, Ur_NPend_g: float, Mlk_CP_g: float, Body_CPgain_g: float, Gest_NCPgain_g: float) -> float:
    """
    An_NCPuse_g: Net CP use (g/d)
    """
    An_NCPuse_g = Scrf_CP_g + Fe_CPend_g + Ur_NPend_g + Mlk_CP_g + Body_CPgain_g + Gest_NCPgain_g  # Net CP use, Line 2537
    return An_NCPuse_g


def calculate_An_Nprod_g(Gest_NCPgain_g: float, Body_CPgain_g: float, Mlk_CP_g: float) -> float:
    """
    An_Nprod_g: N used for production (g/d)
    """
    An_Nprod_g = (Gest_NCPgain_g + Body_CPgain_g) / 6.25 + Mlk_CP_g / 6.34  # Line 2539
    return An_Nprod_g


def calculate_An_Nprod_NIn(An_Nprod_g: float, An_NIn_g: float) -> float:
    """
    An_Nprod_NIn: N used for production as fraction of N intake
    """
    An_Nprod_NIn = An_Nprod_g / An_NIn_g    # Line 2540
    return An_Nprod_NIn


def calculate_An_Nprod_DigNIn(An_Nprod_g: float, An_DigNtIn_g: float) -> float:
    """
    An_Nprod_DigNIn: N used for production as fraction of digestable N intake (g/d)
    """
    An_Nprod_DigNIn = An_Nprod_g / An_DigNtIn_g # Line 2541
    return An_Nprod_DigNIn
