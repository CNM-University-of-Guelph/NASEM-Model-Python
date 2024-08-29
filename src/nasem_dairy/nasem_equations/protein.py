"""Protein metabolism and utilization calculations.

This module includes functions to estimate the utilization, synthesis, and 
degradation of protein.
"""

import numpy as np
import pandas as pd


def calculate_f_mPrt_max(An_305RHA_MlkTP: float, coeff_dict: dict) -> float:
    """
    Examples
    --------
    ```
    coeff_dict = {'K_305RHA_MlkTP': 1.0}

    calculate_f_mPrt_max(
        An_305RHA_MlkTP = 400.0, coeff_dict = coeff_dict
    )
    ```
    """
    # Line 2116, 280kg RHA ~ 930 g mlk NP/d herd average
    f_mPrt_max = 1 + coeff_dict['K_305RHA_MlkTP'] * (An_305RHA_MlkTP / 280 - 1)
    return f_mPrt_max


def calculate_Du_MiCP_g(Du_MiN_g: float) -> float:
    Du_MiCP_g = Du_MiN_g * 6.25  # Line 1163
    return Du_MiCP_g


def calculate_Du_MiTP_g(Du_MiCP_g: float, coeff_dict: dict) -> float:
    """
    Examples
    --------
    ```
    coeff_dict = {'fMiTP_MiCP': 0.824}

    calculate_Du_MiTP_g(
        Du_MiCP_g = 100.0, coeff_dict = coeff_dict
    )
    ```
    """
    Du_MiTP_g = coeff_dict['fMiTP_MiCP'] * Du_MiCP_g  # Line 1166
    return Du_MiTP_g


def calculate_Scrf_CP_g(An_StatePhys: str, An_BW: float) -> float:
    """
    Scrf_CP_g: Scurf CP, g
    """
    if An_StatePhys == "Calf":
        Scrf_CP_g = 0.219 * An_BW**0.60  # Line 1965
    else:
        Scrf_CP_g = 0.20 * An_BW**0.60  # Line 1964
    return Scrf_CP_g


def calculate_Scrf_NP_g(Scrf_CP_g: float, coeff_dict: dict) -> float:
    """
    Scrf_NP_g: Scurf Net Protein, g
    
    Examples
    --------
    ```
    coeff_dict = {'Body_NP_CP': 0.86}

    calculate_Scrf_NP_g(
        Scrf_CP_g = 150.0, coeff_dict = coeff_dict
    )
    ```
    """
    Scrf_NP_g = Scrf_CP_g * coeff_dict['Body_NP_CP']  # Line 1966
    return Scrf_NP_g


def calculate_Scrf_MPUse_g_Trg(
    An_StatePhys: str, 
    Scrf_CP_g: float,
    Scrf_NP_g: float, 
    Km_MP_NP_Trg: float
) -> float:
    """
    Scrf_MPUse_g_Trg: Scurf Metabolizable protein, g
    """
    if An_StatePhys in ["Calf", "Heifer"]:
        Scrf_MPUse_g_Trg = Scrf_CP_g / Km_MP_NP_Trg  
        # calves and heifers are CP based., Line 2671
    else:
        Scrf_MPUse_g_Trg = Scrf_NP_g / Km_MP_NP_Trg  # Line 2670
    return Scrf_MPUse_g_Trg


def calculate_Scrf_NP(Scrf_NP_g: float) -> float:
    """
    Scrf_NP: Scurf net protein (kg/d)
    """
    Scrf_NP = Scrf_NP_g * 0.001  # Line 1967
    return Scrf_NP


def calculate_Scrf_N_g(Scrf_CP_g: float) -> float:
    """
    Scrf_N_g: Scurf N (g/d)
    """
    Scrf_N_g = Scrf_CP_g * 0.16  # Line 1968
    return Scrf_N_g


def calculate_Scrf_AA_TP(aa_list: list, coeff_dict: dict) -> np.ndarray:
    Scrf_AA_TP = np.array([coeff_dict[f"Scrf_{aa}_TP"] for aa in aa_list])
    return Scrf_AA_TP


def calculate_Scrf_AA_g(Scrf_NP_g: float, Scrf_AA_TP: np.ndarray) -> np.ndarray:
    """
    Scrf_AA_g: AA in scurf (g/d)
    """
    Scrf_AA_g = Scrf_NP_g * Scrf_AA_TP / 100  # Lines 1969-1978
    return Scrf_AA_g


def calculate_ScrfAA_AbsAA(
    Scrf_AA_g: pd.Series,
    Abs_AA_g: pd.Series
) -> np.array:
    """
    ScrfAA_AbsAA: Scurf aa as a fraction of absorbed aa
    """
    ScrfAA_AbsAA = Scrf_AA_g / Abs_AA_g  # Line 1981-1990
    return ScrfAA_AbsAA


def calculate_An_CPxprt_g(
    Scrf_CP_g: float, 
    Fe_CPend_g: float, 
    Mlk_CP_g: float,
    Body_CPgain_g: float
) -> float:
    """
    An_CPxprt_g: CP used for export protein (g/d)
    """
    An_CPxprt_g = Scrf_CP_g + Fe_CPend_g + Mlk_CP_g + Body_CPgain_g  
    # Initially defined only as true export protein, but it has migrated to 
    # include other prod proteins, Line 2525
    return An_CPxprt_g


def calculate_An_NPxprt_g(
    Scrf_NP_g: float, 
    Fe_NPend_g: float, 
    Mlk_NP_g: float,
    Body_NPgain_g: float
) -> float:
    """
    An_NPxprt_g: NP used for export protein (g/d)
    """
    An_NPxprt_g = Scrf_NP_g + Fe_NPend_g + Mlk_NP_g + Body_NPgain_g  
    # Should have changed the name, Line 2526
    return An_NPxprt_g


def calculate_Trg_NPxprt_g(
    Scrf_NP_g: float, 
    Fe_NPend_g: float,
    Trg_Mlk_NP_g: float, 
    Body_NPgain_g: float
) -> float:
    """
    Trg_NPxprt_g: NP used for export protein (g/d)
    """
    Trg_NPxprt_g = Scrf_NP_g + Fe_NPend_g + Trg_Mlk_NP_g + Body_NPgain_g  
    # Shouldn't these also include Gest??, Line 2527
    return Trg_NPxprt_g


def calculate_An_CPprod_g(
    Mlk_CP_g: float, 
    Gest_NCPgain_g: float,
    Body_CPgain_g: float
) -> float:
    """
    An_CPprod_g: CP use for production (g/d)
    """
    An_CPprod_g = Mlk_CP_g + Gest_NCPgain_g + Body_CPgain_g  
    # CP use for production. Be careful not to double count Gain. Line 2529
    return An_CPprod_g


def calculate_An_NPprod_g(
    Mlk_NP_g: float, 
    Gest_NPgain_g: float,
    Body_NPgain_g: float
) -> float:
    """
    An_NPprod_g: NP use for production (g/d)
    """
    An_NPprod_g = Mlk_NP_g + Gest_NPgain_g + Body_NPgain_g  
    # NP use for production, Line 2530
    return An_NPprod_g


def calculate_Trg_NPprod_g(
    Trg_Mlk_NP_g: float, 
    Gest_NPgain_g: float,
    Body_NPgain_g: float
) -> float:
    """
    Trg_NPprod_g: NP used fpr production (g/d)
    """
    Trg_NPprod_g = Trg_Mlk_NP_g + Gest_NPgain_g + Body_NPgain_g  
    # NP needed for production target, Line 2531
    return Trg_NPprod_g


def calculate_An_NPprod_MPIn(An_NPprod_g: float, An_MPIn_g: float) -> float:
    """
    An_NPprod_MPIn: NP used for produciton as fraction of metabolizable protein
    """
    An_NPprod_MPIn = An_NPprod_g / An_MPIn_g  # Line 2532
    return An_NPprod_MPIn


def calculate_Trg_NPuse_g(
    Scrf_NP_g: float, 
    Fe_NPend_g: float,
    Ur_NPend_g: float, 
    Trg_Mlk_NP_g: float,
    Body_NPgain_g: float, 
    Gest_NPgain_g: float
) -> float:
    """
    Trg_NPuse_g: Target NP use (g/d)
    """
    Trg_NPuse_g = (Scrf_NP_g + Fe_NPend_g + Ur_NPend_g + 
                   Trg_Mlk_NP_g + Body_NPgain_g + Gest_NPgain_g) # Line 2535
    return Trg_NPuse_g


def calculate_An_NPuse_g(
    Scrf_NP_g: float, 
    Fe_NPend_g: float, 
    Ur_NPend_g: float,
    Mlk_NP_g: float, 
    Body_NPgain_g: float,
    Gest_NPgain_g: float
) -> float:
    """
    An_NPuse_g: NP use (g/d)
    """
    An_NPuse_g = (Scrf_NP_g + Fe_NPend_g + Ur_NPend_g + 
                  Mlk_NP_g + Body_NPgain_g + Gest_NPgain_g)  
    # includes only net use of true protein. Excludes non-protein maintenance
    # use, Line 2536
    return An_NPuse_g


def calculate_An_NCPuse_g(
    Scrf_CP_g: float, 
    Fe_CPend_g: float,
    Ur_NPend_g: float, 
    Mlk_CP_g: float,
    Body_CPgain_g: float, 
    Gest_NCPgain_g: float
) -> float:
    """
    An_NCPuse_g: Net CP use (g/d)
    """
    An_NCPuse_g = (Scrf_CP_g + Fe_CPend_g + Ur_NPend_g + 
                   Mlk_CP_g + Body_CPgain_g + Gest_NCPgain_g)  
    # Net CP use, Line 2537
    return An_NCPuse_g


def calculate_An_Nprod_g(
    Gest_NCPgain_g: float, 
    Body_CPgain_g: float,
    Mlk_CP_g: float
) -> float:
    """
    An_Nprod_g: N used for production (g/d)
    """
    An_Nprod_g = (Gest_NCPgain_g + Body_CPgain_g) / 6.25 + Mlk_CP_g / 6.34  
    # Line 2539
    return An_Nprod_g


def calculate_An_Nprod_NIn(An_Nprod_g: float, An_NIn_g: float) -> float:
    """
    An_Nprod_NIn: N used for production as fraction of N intake
    """
    An_Nprod_NIn = An_Nprod_g / An_NIn_g  # Line 2540
    return An_Nprod_NIn


def calculate_An_Nprod_DigNIn(An_Nprod_g: float, An_DigNtIn_g: float) -> float:
    """
    An_Nprod_DigNIn: N used for production as fraction of digestable N intake (g/d)
    """
    An_Nprod_DigNIn = An_Nprod_g / An_DigNtIn_g  # Line 2541
    return An_Nprod_DigNIn


def calculate_An_MPBal_g_Trg(An_MPIn_g: float, An_MPuse_g_Trg: float) -> float:
    """
    An_MPBal_g_Trg: Target MP balance (g/d)
    """
    An_MPBal_g_Trg = An_MPIn_g - An_MPuse_g_Trg  # Line 2700
    return An_MPBal_g_Trg


def calculate_Xprt_NP_MP_Trg(
    Scrf_NP_g: float, 
    Fe_NPend_g: float,
    Trg_Mlk_NP_g: float, 
    Body_NPgain_g: float,
    An_MPIn_g: float, 
    Ur_NPend_g: float,
    Gest_MPUse_g_Trg: float
) -> float:
    """
    Xprt_NP_MP_Trg: Export NP to MP efficiency
    """
    Xprt_NP_MP_Trg = ((Scrf_NP_g + Fe_NPend_g + Trg_Mlk_NP_g + Body_NPgain_g) / 
                      (An_MPIn_g - Ur_NPend_g - Gest_MPUse_g_Trg))
    # Predicted An_NP_MP using Target Milk NP, g/g, Line 2701
    # The above excludes Ur_NPend and Gest_NPgain from the denominator and the 
    # numerator as that is how Helene and Roger derived target efficiencies.
    # Seems incorrect unless one does not consider Urinary endogenous as NP 
    # which is inconsistent with the definition. Not a true, total MP efficiency
    return Xprt_NP_MP_Trg


def calculate_Xprt_NP_MP(
    Scrf_NP_g: float, 
    Fe_NPend_g: float, 
    Mlk_NP_g: float,
    Body_NPgain_g: float, 
    An_MPIn_g: float,
    Ur_NPend_g: float, 
    Gest_MPUse_g_Trg: float
) -> float:
    """
    Xprt_NP_MP: Export efficiency NP to MP
    """
    Xprt_NP_MP = ((Scrf_NP_g + Fe_NPend_g + Mlk_NP_g + Body_NPgain_g) / 
                  (An_MPIn_g - Ur_NPend_g - Gest_MPUse_g_Trg))  # Line 2720
    return Xprt_NP_MP


def calculate_Km_MP_NP(An_StatePhys: str, Xprt_NP_MP: float) -> float:
    """
    Km_MP_NP: MP to NP conversion efficiency
    """
    # MP to NP conversion efficiency assuming 100% efficiency of Ur_NPend.  
    # Should not be named as a K as it is not a constant. 
    # This is apparent efficiency. Assumed equal to efficiency for total
    # proteins except for heifers.
    if An_StatePhys == "Heifer":  # Line 2722
        Km_MP_NP = 0.69
    else:
        Km_MP_NP = Xprt_NP_MP
    return Km_MP_NP


def calculate_Kl_MP_NP(Xprt_NP_MP: float) -> float:
    """
    Kl_MP_NP: MP to NP conversion efficiency
    """
    Kl_MP_NP = Xprt_NP_MP  # Line 2723
    return Kl_MP_NP


def calculate_Scrf_MPUse_g(Scrf_NP_g: float, Km_MP_NP: float) -> float:
    """
    Scrf_MPUse_g: Endogenous MP in scurf (g/d)
    """
    Scrf_MPUse_g = Scrf_NP_g / Km_MP_NP  # Line 2727
    return Scrf_MPUse_g


def calculate_An_MPuse_g(
    Fe_MPendUse_g: float, 
    Scrf_MPUse_g: float, 
    Ur_MPendUse_g: float, 
    Body_MPUse_g_Trg: float, 
    Gest_MPUse_g_Trg: float, 
    Mlk_MPUse_g: float,
) -> float:
    """
    An_MPuse_g: Total MP use (g/d)
    """
    An_MPuse_g = (Fe_MPendUse_g + Scrf_MPUse_g + Ur_MPendUse_g + 
                  Body_MPUse_g_Trg + Gest_MPUse_g_Trg + Mlk_MPUse_g)
    return An_MPuse_g


def calculate_An_MPuse(An_MPuse_g: float):
    """
    An_MPuse: Total MP use (kg/d)
    """
    An_MPuse = An_MPuse_g / 1000  # Line 2730
    return An_MPuse


def calculate_An_MPBal_g(An_MPIn_g: float, An_MPuse_g: float) -> float:
    """
    An_MPBal_g: Metabolizable protein balance (g/d)
    """
    An_MPBal_g = An_MPIn_g - An_MPuse_g  
    # This will always be 0 given how the efficiencies are calculated. 
    # Not informative, Line 2731
    return An_MPBal_g


def calculate_An_MP_NP(An_NPuse_g: float, An_MPuse_g: float) -> float:
    """
    An_MP_NP: Conversion of MP to NP 
    """
    An_MP_NP = An_NPuse_g / An_MPuse_g  #Total MP Efficiency, g/g, Line 2734
    return An_MP_NP


def calculate_An_NPxprt_MP(
    An_NPuse_g: float, 
    Ur_NPend_g: float,
    Gest_NPuse_g: float, 
    An_MPIn_g: float,
    Gest_MPUse_g_Trg: float
) -> float:
    """
    An_NPxprt_MP: NP to MP conversion efficiency
    """
    An_NPxprt_MP = ((An_NPuse_g - Ur_NPend_g - Gest_NPuse_g) / 
                    (An_MPIn_g - Ur_NPend_g - Gest_MPUse_g_Trg))
    # g/g. For comparison to target efficiency, but a duplicate of Xprt_NP_MP
    # Line 2735
    return An_NPxprt_MP


def calculate_An_CP_NP(An_NPuse_g: float, An_CPIn: float) -> float:
    """
    An_CP_NP: CP to NP conversion efficiency 
    """
    An_CP_NP = An_NPuse_g / (An_CPIn * 1000)
    # Total CP efficiency, g/g, Line 2736
    return An_CP_NP


def calculate_An_NPBal_g(
    An_MPIn_g: float, 
    An_MP_NP: float,
    An_NPuse_g: float
) -> float:
    """
    An_NPBal_g: Net protein balance (g/d)
    """
    An_NPBal_g = An_MPIn_g * An_MP_NP - An_NPuse_g  
    # Also always 0, thus non-informative, Line 2738
    return An_NPBal_g


def calculate_An_NPBal(An_NPBal_g: float) -> float:
    """
    An_NPBal: Net protein balance (kg/d)
    """
    An_NPBal = An_NPBal_g / 1000  # Line 2739
    return An_NPBal
