"""Functions to calculate various amino acid-related parameters.

These calculations include amino acid absorption, utilization, and metabolism.
"""

import math

import numpy as np
import pandas as pd


def calculate_MiTPAAProf(aa_list: list, coeff_dict: dict) -> np.ndarray:
    """
    Examples
    --------

    ```
    coeff_dict = {
        "MiTPArgProf": 5.47, "MiTPHisProf": 2.21, "MiTPIleProf": 6.99, 
        "MiTPLeuProf": 9.23, "MiTPLysProf": 9.44, "MiTPMetProf": 2.63, 
        "MiTPPheProf": 6.30, "MiTPThrProf": 6.23, "MiTPTrpProf": 1.37, 
        "MiTPValProf": 6.88
    }
    
    calculate_MiTPAAProf(
        aa_list = ["Arg", "His", "Ile", "Leu", "Lys", 
                   "Met", "Phe", "Thr", "Trp", "Val"]
        coeff_dict = coeff_dict
    )
    ```
    """
    MiTPAAProf = np.array([coeff_dict[f"MiTP{aa}Prof"] for aa in aa_list])
    return MiTPAAProf


def calculate_Du_AAMic(Du_MiTP_g: float, MiTPAAProf: np.ndarray) -> np.ndarray:
    Du_AAMic = Du_MiTP_g * MiTPAAProf / 100  # Line 1573-1582
    return Du_AAMic


def calculate_Du_IdAAMic(Du_AAMic: float, coeff_dict: dict) -> float:
    """
    Examples
    --------

    ```
    coeff_dict = {
        "SI_dcMiCP": 80
    }
    
    calculate_MiTPAAProf(
        Du_AAMic = 12.8,
        coeff_dict = coeff_dict
    )
    ```
    """
    Du_IdAAMic = Du_AAMic * coeff_dict['SI_dcMiCP'] / 100
    return Du_IdAAMic


def calculate_mPrt_k_AA_array(mPrt_coeff: dict, aa_list: list) -> np.ndarray:
    mPrt_k_AA_array = np.array([mPrt_coeff[f"mPrt_k_{aa}"] for aa in aa_list])
    return mPrt_k_AA_array


def calculate_An_IdAAIn_array(an_data: dict, aa_list: list) -> np.ndarray:
    An_IdAAIn = pd.Series([an_data[f"An_Id{aa}In"] for aa in aa_list],
                          index=aa_list)
    return An_IdAAIn


def calculate_Inf_AA_g(infusion_data: dict, aa_list: list) -> np.ndarray:
    Inf_AA_g = pd.Series([infusion_data[f"Inf_{aa}_g"] for aa in aa_list],
                         index=aa_list)
    return Inf_AA_g


def calculate_Abs_AA_g(
    An_IdAAIn: np.ndarray,
    Inf_AA_g: np.ndarray, 
    Inf_Art: float
) -> pd.Series:
    Abs_AA_g = An_IdAAIn + Inf_AA_g * Inf_Art
    return Abs_AA_g


def calculate_mPrtmx_AA(mPrt_k_AA_array: np.array, mPrt_coeff: dict) -> np.array:
    """
    mPrtmx_AA: Maximum milk protein responses from each aa
    """
    mPrtmx_AA = -(mPrt_k_AA_array**2) / (4 * mPrt_coeff['mPrt_k_EAA2_coeff'])
    # maximum milk protein responses from each aa, Line 2117-2126
    return mPrtmx_AA


def calculate_mPrtmx_AA2(mPrtmx_AA: pd.Series, f_mPrt_max: float) -> pd.Series:
    mPrtmx_AA2 = mPrtmx_AA * f_mPrt_max  # Line 2149-2158
    return mPrtmx_AA2


def calculate_AA_mPrtmx(mPrt_k_AA_array: np.array, mPrt_coeff: dict) -> np.array:
    """
    AA_mPrtmx: aa input at maximum milk protein response for each aa
    """
    AA_mPrtmx = -mPrt_k_AA_array / (2 * mPrt_coeff['mPrt_k_EAA2_coeff'])  
    # aa input at maximum milk protein response for each aa, Line 2127-2136
    return AA_mPrtmx


def calculate_mPrt_AA_01(
    AA_mPrtmx: np.array, 
    mPrt_k_AA_array: np.array,
    mPrt_coeff: dict
) -> np.array:
    """
    mPrt_AA_01: Milk protein from each EAA at 10% of max response
    """
    mPrt_AA_01 = (AA_mPrtmx * 0.1 * mPrt_k_AA_array + 
                  (AA_mPrtmx * 0.1)**2 * mPrt_coeff['mPrt_k_EAA2_coeff'])  
    # Milk prt from each EAA at 10% of Max response, Line 2138-2147
    return mPrt_AA_01


def calculate_mPrt_k_AA(
    mPrtmx_AA2: pd.Series, 
    mPrt_AA_01: pd.Series, 
    AA_mPrtmx: pd.Series
) -> pd.Series:
    mPrt_k_AA = np.zeros_like(mPrtmx_AA2)
    for i in range(len(mPrtmx_AA2)):
        inner_value = (
            mPrtmx_AA2.iloc[i]**2 - mPrt_AA_01.iloc[i] * mPrtmx_AA2.iloc[i]
            )
        if inner_value <= 0 or AA_mPrtmx.iloc[i] == 0:
            mPrt_k_AA[i] = 0
        else:
            mPrt_k_AA[i] = (-(2 * np.sqrt(inner_value) - 2 * mPrtmx_AA2.iloc[i]) 
                            / (AA_mPrtmx.iloc[i] * 0.1))
    return mPrt_k_AA


def calculate_Abs_EAA_g(Abs_AA_g: pd.Series) -> float:
    Abs_EAA_g = Abs_AA_g.sum()  # Line 1769
    return Abs_EAA_g


def calculate_Abs_neAA_g(An_MPIn_g: float, Abs_EAA_g: float) -> float:
    # Line 1771, Absorbed NEAA (Equation 20-150 p. 433)
    Abs_neAA_g = An_MPIn_g * 1.15 - Abs_EAA_g
    return Abs_neAA_g


def calculate_Abs_OthAA_g(Abs_neAA_g: float, Abs_AA_g: pd.Series) -> float:
    Abs_OthAA_g = (Abs_neAA_g + Abs_AA_g['Arg'] + Abs_AA_g['Phe'] + 
                   Abs_AA_g['Thr'] + Abs_AA_g['Trp'] + Abs_AA_g['Val'])  
    # Line 2110, NRC eqn only, Equation 20-186a, p. 436
    return Abs_OthAA_g


def calculate_Abs_EAA2_g(Abs_AA_g: pd.Series) -> float:
    """
    Abs_EAA2_g: Sum of all squared EAA
    """
    Abs_EAA2_g = (Abs_AA_g['Arg']**2 + Abs_AA_g['His']**2 + Abs_AA_g['Ile']**2 +
                  Abs_AA_g['Leu']**2 + Abs_AA_g['Lys']**2 + Abs_AA_g['Met']**2 +
                  Abs_AA_g['Phe']**2 + Abs_AA_g['Thr']**2 + Abs_AA_g['Trp']**2 + 
                  Abs_AA_g['Val']**2) # Line 1775-1776
    return Abs_EAA2_g


def calculate_Abs_EAA2_HILKM_g(Abs_AA_g: pd.Series) -> float:
    Abs_EAA2_HILKM_g = (Abs_AA_g['His']**2 + Abs_AA_g['Ile']**2 + 
                        Abs_AA_g['Leu']**2 + Abs_AA_g['Lys']**2 + 
                        Abs_AA_g['Met']**2)  
    # Line 1778, NRC 2020 (no Arg, Phe, Thr, Trp, or Val)
    return Abs_EAA2_HILKM_g


def calculate_Abs_EAA2_RHILKM_g(Abs_AA_g: pd.Series) -> float:
    Abs_EAA2_RHILKM_g = (Abs_AA_g['Arg']**2 + Abs_AA_g['His']**2 + 
                         Abs_AA_g['Ile']**2 + Abs_AA_g['Leu']**2 + 
                         Abs_AA_g['Lys']**2 + Abs_AA_g['Met']**2)  
    # Line 1780, Virginia Tech 1 (no Phe, Thr, Trp, or Val)
    return Abs_EAA2_RHILKM_g


def calculate_Abs_EAA2_HILKMT_g(Abs_AA_g: pd.Series) -> float:
    Abs_EAA2_HILKMT_g = (Abs_AA_g['His']**2 + Abs_AA_g['Ile']**2 + 
                         Abs_AA_g['Leu']**2 + Abs_AA_g['Lys']**2 + 
                         Abs_AA_g['Met']**2 + Abs_AA_g['Thr']**2)
    return Abs_EAA2_HILKMT_g


def calculate_Abs_EAA2b_g(mPrt_eqn: int, Abs_AA_g: pd.Series) -> float:
    if mPrt_eqn == 2:
        Abs_EAA2b_g = calculate_Abs_EAA2_RHILKM_g(Abs_AA_g) # Line 2108, VT1 eqn.
    elif mPrt_eqn == 3:
        Abs_EAA2b_g = calculate_Abs_EAA2_HILKMT_g(Abs_AA_g) # Line 2106, VT2 eqn.
    else:
        Abs_EAA2b_g = calculate_Abs_EAA2_HILKM_g(Abs_AA_g) # Line 2107, NRC eqn.
    return Abs_EAA2b_g


def calculate_mPrt_k_EAA2(
    mPrtmx_AA2: float, 
    mPrt_AA_01: float, 
    AA_mPrtmx: float
) -> float:
    # Scale the quadratic; can be calculated from any of the aa included in the 
    # squared term. All give the same answer. Line 2184
    # Methionine used to be consistent with R code
    mPrt_k_EAA2 = (2 * math.sqrt(mPrtmx_AA2["Met"]**2 - mPrt_AA_01["Met"] * 
                                 mPrtmx_AA2["Met"]) - 2 * mPrtmx_AA2["Met"] + 
                                 mPrt_AA_01["Met"]) / (AA_mPrtmx["Met"] * 0.1)**2
    return mPrt_k_EAA2


def calculate_EndAAProf(aa_list: list, coeff_dict: dict) -> np.ndarray:
    """
    Examples
    --------

    ```
    coeff_dict = {
        "EndArgProf":" 4.61, "EndHisProf":" 2.90, "EndIleProf":" 4.09, 
        "EndLeuProf":" 7.67, "EndLysProf":" 6.23"EndMetProf":" 1.26, 
        "EndPheProf":" 3.98, "EndThrProf":" 5.18, "EndTrpProf":" 1.29, 
        "EndValProf":" 5.29
    }
    
    calculate_EndAAProf(
        aa_list = ["Arg", "His", "Ile", "Leu", "Lys", 
                   "Met", "Phe", "Thr", "Trp", "Val"],
        coeff_dict = coeff_dict
    )
    ```
    """
    EndAAProf = np.array([coeff_dict[f"End{aa}Prof"] for aa in aa_list])
    return EndAAProf


def calculate_Du_AAEndP(
    Du_EndCP_g: float,
    EndAAProf: np.ndarray
) -> pd.Series:
    """
    Du_AAEndP: Duodenal EndPAA, g hydrated true aa/d 
    """
    # Duodenal EndPAA, g hydrated true aa/d
    Du_AAEndP = Du_EndCP_g * EndAAProf / 100  # Lines 1585-1594
    return Du_AAEndP


def calculate_Dt_AARUPIn(aa_list: list, diet_data: dict) -> np.ndarray:
    Dt_AARUPIn = np.array([diet_data[f"Dt_{aa}RUPIn"] for aa in aa_list])
    return Dt_AARUPIn


def calculate_Inf_AARUPIn(aa_list: list, infusion_data: dict) -> np.ndarray:
    Inf_AARUPIn = np.array([infusion_data[f"Inf_{aa}RUPIn"] for aa in aa_list])
    return Inf_AARUPIn


def calculate_Du_AA(
    Dt_AARUPIn: np.ndarray,
    Inf_AARUPIn: np.ndarray,
    Du_AAMic: float,
    Du_AAEndP: float
) -> pd.Series:
    """
    Du_AA: Total ruminal aa outflows, g hydr, fully recovered aa/d (true protein bound aa flows)
    """
    # Total ruminal aa outflows, g hydr, fully recovered aa/d (true protein bound aa flows)
    # These should have _g at the end of each
    Du_AA = Dt_AARUPIn + Inf_AARUPIn + Du_AAMic + Du_AAEndP  # Line 1597-1606
    return Du_AA


def calculate_Dt_AAIn(aa_list: list, diet_data: dict) -> np.ndarray:
    Dt_AAIn = np.array([diet_data[f"Dt_{aa}In"] for aa in aa_list])
    return Dt_AAIn


def calculate_DuAA_AArg(
    Du_AA: pd.Series, 
    Dt_AAIn: np.ndarray
) -> pd.Series:
    """
    DuAA_DtAA: Duodenal aa flow expressed as a fraction of dietary aa
    """
    # Duodenal aa flow expressed as a fraction of dietary aa, 
    # ruminally infused included in Du but not Dt
    DuAA_DtAA = Du_AA / Dt_AAIn  # Line 1610-1619
    return DuAA_DtAA


def calculate_RecAA(aa_list: list, coeff_dict: dict) -> np.ndarray:
    RecAA = np.array([coeff_dict[f"Rec{aa}"] for aa in aa_list])
    return RecAA


def calculate_Du_AA24h(
    Du_AA: pd.Series, 
    RecAA: np.ndarray
) -> pd.Series:
    """
    Du_AA24h: g hydrat 24h recovered aa/d
    """
    # The following predicted aa flows are for comparison to observed 
    # Duod aa flows, g hydrat 24h recovered aa/d
    Du_AA24h = Du_AA * RecAA  # Line 1622-1631
    return Du_AA24h


def calculate_IdAA_DtAA(Dt_AAIn: np.ndarray, An_IdAAIn: np.ndarray) -> np.array:
    """
    IdAA_DtAA: Intestinally Digested aa flow expressed as a fraction of dietary aa
    """
    # Intestinally Digested aa flow expressed as a fraction of dietary aa
    # ruminally and intesntinally infused included in id but not Dt
    IdAA_DtAA = An_IdAAIn / Dt_AAIn  # Lines 1728-1737
    return IdAA_DtAA


def calculate_Abs_AA_MPp(Abs_AA_g: pd.Series, An_MPIn_g: float) -> pd.Series:
    """
    Abs_AA_MPp: aa as a percent of metabolizable protein
    """
    Abs_AA_MPp = Abs_AA_g / An_MPIn_g * 100  # Lines 1787-1796
    return Abs_AA_MPp


def calculate_Abs_AA_p(Abs_AA_g: pd.Series, Abs_EAA_g: float) -> pd.Series:
    """
    Abs_AA_p: Absorbed aa as a percent of total absorbed EAA
    """
    Abs_AA_p = Abs_AA_g / Abs_EAA_g * 100  # Lines 1799-1808
    return Abs_AA_p


def calculate_Abs_AA_DEI(Abs_AA_g: pd.Series, An_DEIn: float) -> pd.Series:
    """
    Abs_AA_DEI: Absorbed aa per Mcal digestable energy intake (g/Mcal)?
    """
    Abs_AA_DEI = Abs_AA_g / An_DEIn  # Lines 1811-1820
    return Abs_AA_DEI


def calculate_MWAA(aa_list: list, coeff_dict: dict) -> np.ndarray:
    MWAA = np.array([coeff_dict[f"MW{aa}"] for aa in aa_list])
    return MWAA


def calculate_Abs_AA_mol(Abs_AA_g: pd.Series, MWAA: np.ndarray) -> np.array:
    """
    Abs_AA_mol: moles of absorbed aa (mol/d)
    """
    Abs_AA_mol = Abs_AA_g / MWAA  # Line 1823-1832
    return Abs_AA_mol


def calculate_Body_AA_TP(aa_list: list, coeff_dict: dict) -> np.ndarray:
    Body_AA_TP = np.array([coeff_dict[f"Body_{aa}_TP"] for aa in aa_list])
    return Body_AA_TP


def calculate_Body_AAGain_g(
    Body_NPgain_g: float,
    Body_AA_TP: np.ndarray
) -> np.array:
    """
    Body_AAGain_g: Body aa gain (g/d)
    """
    Body_AAGain_g = Body_NPgain_g * Body_AA_TP / 100  # Line 2497-2506
    return Body_AAGain_g


def calculate_Body_EAAGain_g(Body_AAGain_g: pd.Series) -> float:
    """
    Body_EAAGain_g: Body EAA gain (g/d)
    """
    Body_EAAGain_g = Body_AAGain_g.sum()  # Line 2507-2508
    return Body_EAAGain_g


def calculate_BodyAA_AbsAA(
    Body_AAGain_g: pd.Series,
    Abs_AA_g: pd.Series
) -> pd.Series:
    """
    BodyAA_AbsAA: Body aa gain as a fraction of absolute aa intake
    """
    BodyAA_AbsAA = Body_AAGain_g / Abs_AA_g  # Line 2510-2519
    return BodyAA_AbsAA


def calculate_An_AAUse_g(
    Gest_AA_g: pd.Series, 
    Mlk_AA_g: pd.Series,
    Body_AAGain_g: pd.Series,
    Scrf_AA_g: pd.Series,
    Fe_AAMet_g: pd.Series,
    Ur_AAEnd_g: pd.Series
) -> pd.Series:
    """
    An_AAUse_g: Total net aa use (g/d)
    """
    An_AAUse_g = (Gest_AA_g + Mlk_AA_g + Body_AAGain_g + 
                  Scrf_AA_g + Fe_AAMet_g + Ur_AAEnd_g)  
    # Total Net aa use (Nutrient Allowable), g/d, Line 2544-2553
    return An_AAUse_g


def calculate_An_EAAUse_g(An_AAUse_g: pd.Series) -> float:
    """
    An_EAAUse_g: Total net EAA use (g/d)
    """
    An_EAAUse_g = An_AAUse_g.sum()  # Line 2554-2555
    return An_EAAUse_g


def calculate_AnAAUse_AbsAA(
    An_AAUse_g: pd.Series,
    Abs_AA_g: pd.Series
) -> pd.Series:
    """
    AnAAUse_AbsAA: Total net aa efficieny (g/g)
    """
    AnAAUse_AbsAA = An_AAUse_g / Abs_AA_g  
    # Total Net aa efficiency, g/g absorbed, Line 2558-2567
    return AnAAUse_AbsAA


def calculate_AnEAAUse_AbsEAA(An_EAAUse_g: float, Abs_EAA_g: float) -> float:
    """
    AnEAAUse_AbsEAA: Total net EAA efficieny (g/g)
    """
    AnEAAUse_AbsEAA = An_EAAUse_g / Abs_EAA_g  # Line 2568
    return AnEAAUse_AbsEAA


def calculate_An_AABal_g(
    Abs_AA_g: pd.Series,
    An_AAUse_g: pd.Series
) -> pd.Series:
    """
    An_AABal_g: Total net aa balance (g/d)
    """
    An_AABal_g = Abs_AA_g - An_AAUse_g  
    # Total Net aa Balance, g/d, Line 2571-2580
    return An_AABal_g


def calculate_An_EAABal_g(Abs_EAA_g: float, An_EAAUse_g: float) -> float:
    """
    An_EAABal_g: Total net EAA balance (g/d)
    """
    An_EAABal_g = Abs_EAA_g - An_EAAUse_g  # Line 2581
    return An_EAABal_g


def calculate_Trg_AbsEAA_NPxprtEAA(Trg_AbsAA_NPxprtAA: np.array) -> np.array:
    """
    Trg_AbsEAA_NPxprtEAA: Target postabsorptive EAA efficiencies based on maximum 
                          obsreved efficiencies from Martineau and LaPiere as 
                          listed in NRC, Ch. 6.
    """
    Trg_AbsEAA_NPxprtEAA = Trg_AbsAA_NPxprtAA.sum() / 9  
    # Should be weighted or derived directly from total EAA, Line 2593-2594
    return Trg_AbsEAA_NPxprtEAA


def calculate_Trg_AbsArg_NPxprtArg(Trg_AbsEAA_NPxprtEAA: float) -> float:
    """
    Trg_AbsArg_NPxprtArg: Target postabsorptive efficiencies based on maximum 
                          obsreved efficiencies from Martineau and LaPiere as 
                          listed in NRC, Ch. 6.
    """
    Trg_AbsArg_NPxprtArg = Trg_AbsEAA_NPxprtEAA  
    # none provided thus assumed to be the same as for EAA, Line 2595
    return Trg_AbsArg_NPxprtArg


def calculate_Trg_AAEff_EAAEff(
    Trg_AbsAA_NPxprtAA: pd.Series,
    Trg_AbsEAA_NPxprtEAA: float
) -> pd.Series:
    """
    Trg_AAEff_EAAEff: Estimate the degree of aa imbalance within the EAA as 
                      ratios of each Eff to the total EAA Eff.
    """
    # Estimate the degree of aa imbalance within the EAA as ratios of each Eff to the total EAA Eff.
    # These "Target" ratios are calculated as efficiency target (NRC 2021 Ch. 6) / total EAA eff.
    # Thus they are scaled to Ch. 6 targets.  Ch. 6 values should not be used directly here. Ratio first.
    # The target eff from Ch. 6 are likely not true maximum efficiencies.
    # ratio to the mean Trg for each EAA / total EAA Trg of 70.6%, e.g. Ile Trg is 97.3% of 70.6%
    Trg_AAEff_EAAEff = Trg_AbsAA_NPxprtAA / Trg_AbsEAA_NPxprtEAA  # Line 2602-2611
    return Trg_AAEff_EAAEff


def calculate_An_AAEff_EAAEff(
    AnAAUse_AbsAA: pd.Series,
    AnEAAUse_AbsEAA: pd.Series
) -> pd.Series:
    """
    An_AAEff_EAAEff: aa efficiency as ratio of EAA efficiency
    """
    # Calculate the current ratios for the diet.
    # This centers the ratio to the prevailing EAA Efficiency
    An_AAEff_EAAEff = AnAAUse_AbsAA / AnEAAUse_AbsEAA  # Line 2614-2623
    return An_AAEff_EAAEff


def calculate_Imb_AA(
    An_AAEff_EAAEff: pd.Series, 
    Trg_AAEff_EAAEff: float,
    f_Imb: np.array
) -> pd.Series:
    """
    Imb_AA: Calculate a relative penalty for each EAA to reflect the degree of imbalance for each
    """
    # Calculate a relative penalty for each EAA to reflect the degree of imbalance for each.
    # if the diet eff = Trg_eff then no penalty. f_Imb is a vector of penalty costs for each EAA.
    # f_Imb should be passed to the model fn rather than handled as a global variable.
    Imb_AA = ((An_AAEff_EAAEff - Trg_AAEff_EAAEff) * f_Imb)**2
    return Imb_AA


def calculate_Imb_EAA(Imb_AA: pd.Series) -> float:
    """
    Imb_EAA: Sum the penalty to get a relative imbalance value for the optimizer 
    """
    # Sum the penalty to get a relative imbalance value for the optimizer
    Imb_EAA = Imb_AA.sum()
    return Imb_EAA


def calculate_An_IdEAAIn(An_IdAAIn: pd.Series) -> float:
    """
    An_IdEAAIn: Intestinally digested EAA intake
    """
    An_IdEAAIn = An_IdAAIn.sum()  # Line 3126-3127
    return An_IdEAAIn


def calculate_Du_IdEAAMic(Du_IdAAMic: pd.Series) -> float:
    """
    Du_IdEAAMic: Intestinally digested microbial EAA
    """
    Du_IdEAAMic = Du_IdAAMic.sum()  # LIne 3128-3129
    return Du_IdEAAMic


def calculate_Dt_IdEAARUPIn(Dt_IdAARUPIn: pd.Series) -> float:
    """
    Dt_IdEAARUPIn: Intestinally digested EAA RUP intake
    """
    Dt_IdEAARUPIn = Dt_IdAARUPIn.sum()  # Line 3130
    return Dt_IdEAARUPIn


def calculate_Trg_Mlk_AA_g(
    Trg_Mlk_NP_g: float,
    Mlk_AA_TP: pd.Series
) -> pd.Series:
    """
    Trg_Mlk_AA_g: Target Milk individual aa Outputs (g/d)
    """
    Trg_Mlk_AA_g = Trg_Mlk_NP_g * Mlk_AA_TP / 100  
    # Target Milk EAA Outputs, g/d, Line 3136-3145
    return Trg_Mlk_AA_g


def calculate_Trg_Mlk_EAA_g(Trg_Mlk_AA_g: pd.Series) -> float:
    """
    Trg_Mlk_EAA_g: Target milk EAA output (g/d)
    """
    Trg_Mlk_EAA_g = Trg_Mlk_AA_g.sum()
    return Trg_Mlk_EAA_g


def calculate_Trg_AAUse_g(
    Trg_Mlk_AA_g: pd.Series, 
    Scrf_AA_g: pd.Series,
    Fe_AAMet_g: pd.Series,
    Ur_AAEnd_g: pd.Series,
    Gest_AA_g: pd.Series,
    Body_AAGain_g: pd.Series
) -> pd.Series:
    """
    Trg_AAUse_g: Net individual aa use at user entered production (g/d)
    """
    # Net EAA Use at User Entered Production, g/d
    Trg_AAUse_g = (Trg_Mlk_AA_g + Scrf_AA_g + Fe_AAMet_g +
                   Ur_AAEnd_g + Gest_AA_g + Body_AAGain_g) # Line 3151-3160
    return Trg_AAUse_g


def calculate_Trg_EAAUse_g(Trg_AAUse_g: pd.Series) -> float:
    """
    Trg_EAAUse_g: Net EAA use at user entered production (g/d)
    """
    Trg_EAAUse_g = Trg_AAUse_g.sum()
    return Trg_EAAUse_g


def calculate_Trg_AbsAA_g(
    Trg_Mlk_AA_g: pd.Series, 
    Scrf_AA_g: pd.Series,
    Fe_AAMet_g: pd.Series,
    Trg_AbsAA_NPxprtAA: pd.Series,
    Ur_AAEnd_g: pd.Series, 
    Gest_AA_g: pd.Series,
    Body_AAGain_g: pd.Series, 
    Kg_MP_NP_Trg: float,
    coeff_dict: dict
) -> pd.Series:
    """
    Trg_AbsAA_g: Absorbed aa at user entered production (g/d)

    Examples
    --------

    ```
    coeff_dict = {"Ky_MP_NP_Trg": 0.33}

    calculate_Trg_AbsAA_g(
        Trg_Mlk_AA_g = pd.Series([10, 20, 30]), Scrf_AA_g = pd.Series([1, 2, 3]),
        Fe_AAMet_g = pd.Series([5, 10, 15]), Trg_AbsAA_NPxprtAA = pd.Series([0.5, 1.0, 1.5])
        Ur_AAEnd_g = pd.Series([2, 4, 6]), Gest_AA_g = pd.Series([3, 6, 9]),
        Body_AAGain_g = pd.Series([7, 14, 21]), Kg_MP_NP_Trg = 0.33, coeff_dict = coeff_dict
    )
    ```
    """
    Trg_AbsAA_g = ((Trg_Mlk_AA_g + Scrf_AA_g + Fe_AAMet_g) / 
                   Trg_AbsAA_NPxprtAA + Ur_AAEnd_g + Gest_AA_g / 
                   coeff_dict['Ky_MP_NP_Trg'] + Body_AAGain_g / Kg_MP_NP_Trg)  
    # Line 3165-3173
    if 'Arg' in Trg_AbsAA_g.index:  # Arg not included in this calculation
        Trg_AbsAA_g['Arg'] = np.nan
    return Trg_AbsAA_g


def calculate_Trg_AbsEAA_g(Trg_AbsAA_g: pd.Series) -> float:
    """
    Trg_AbsEAA_g: Absorbed EAA at user entered production (g/d)
    """
    Trg_AbsEAA_g = Trg_AbsAA_g.sum(
    )  # Arg not considered as partially synthesized, Line 3174-3175
    return Trg_AbsEAA_g


def calculate_Trg_MlkEAA_AbsEAA(
    Mlk_EAA_g: float, 
    Mlk_AA_g: pd.Series,
    Trg_AbsEAA_g: float
) -> float:
    """
    Trg_MlkEAA_AbsEAA: Milk EAA as a fraction of absorbed EAA at user entered production
    """
    Trg_MlkEAA_AbsEAA = (Mlk_EAA_g - Mlk_AA_g["Arg"]) / Trg_AbsEAA_g  # Line 3176
    return Trg_MlkEAA_AbsEAA


def calculate_AnNPxAA_AbsAA(
    An_AAUse_g: pd.Series, 
    Gest_AA_g: pd.Series,
    Ur_AAEnd_g: pd.Series, 
    Abs_AA_g: pd.Series,
    coeff_dict: dict
) -> pd.Series:
    """
    AnNPxAA_AbsAA: Predicted Efficiency of AbsAA to export and gain NPAA using 
                   Nutrient Allowable milk protein, g NPAA/g absorbed aa

    Examples
    --------

    ```
    coeff_dict = {"Ky_MP_NP_Trg": 0.33}
    
    calculate_EndAAProf(
        An_AAUse_g = pd.Series([50, 100, 150]), Gest_AA_g = pd.Series([10, 20, 30]),
        Ur_AAEnd_g = pd.Series([5, 10, 15]), Abs_AA_g = pd.Series([60, 120, 180]),
        coeff_dict = coeff_dict
    )
    ```
    """
    # Predicted Efficiency of AbsAA to export and gain NPAA using Nutrient Allowable
    # milk protein, g NPAA/g absorbed aa (Ur_AAend use set to an efficiency of 1).
    # These are for comparison to Trg aa Eff.
    AnNPxAA_AbsAA = (An_AAUse_g - Gest_AA_g - Ur_AAEnd_g) / (
        Abs_AA_g - Ur_AAEnd_g - Gest_AA_g / coeff_dict['Ky_MP_NP_Trg']
    )  # Subtract Gest_AA and UrEnd for use and supply, Line 3197-3206
    return AnNPxAA_AbsAA


def calculate_AnNPxEAA_AbsEAA(
    An_EAAUse_g: float, 
    Gest_EAA_g: float,
    Ur_EAAEnd_g: float, 
    Abs_EAA_g: float,
    coeff_dict: dict
) -> float:
    """
    AnNPxEAA_AbsEAA: Predicted Efficiency of AbsEAA to export and gain NPEAA 
                     using Nutrient Allowable milk protein, g NPEAA/g absorbed EAA
       
    Examples
    --------

    ```
    coeff_dict = {"Ky_MP_NP_Trg": 0.33}
    
    calculate_AnNPxEAA_AbsEAA(
        An_EAAUse_g = 150.0, Gest_EAA_g = 30.0, Ur_EAAEnd_g = 15.0, 
        Abs_EAA_g = 180.0, coeff_dict = coeff_dict
    )
    ```
    """
    AnNPxEAA_AbsEAA = (An_EAAUse_g - Gest_EAA_g - Ur_EAAEnd_g) / (
        Abs_EAA_g - Ur_EAAEnd_g - Gest_EAA_g / coeff_dict['Ky_MP_NP_Trg']
    )  # Line 3207
    return AnNPxEAA_AbsEAA


def calculate_AnNPxAAUser_AbsAA(
    Trg_AAUse_g: pd.Series, 
    Gest_AA_g: pd.Series,
    Ur_AAEnd_g: pd.Series, 
    Abs_AA_g: pd.Series,
    coeff_dict: dict
) -> pd.Series:
    """
    AnNPxAAUser_AbsAA: Efficiency of AbsAA to export and gain NPAA at User 
                       Entered milk protein, g NPAA/g absorbed aa
    
    Examples
    --------

    ```
    coeff_dict = {"Ky_MP_NP_Trg": 0.33}
    
    calculate_AnNPxAAUser_AbsAA(
        Trg_AAUse_g = pd.Series([50, 100, 150]), Gest_AA_g = pd.Series([10, 20, 30]), 
        Ur_AAEnd_g = pd.Series([5, 10, 15]), Abs_AA_g = pd.Series([60, 120, 180]),
        coeff_dict = coeff_dict
    )
    ```
    """
    # Efficiency of AbsAA to export and gain NPAA at User Entered milk protein, 
    # g NPAA/g absorbed aa (Ur_AAend use set to an efficiency of 1).
    AnNPxAAUser_AbsAA = (Trg_AAUse_g - Gest_AA_g - Ur_AAEnd_g) / (
        Abs_AA_g - Ur_AAEnd_g - Gest_AA_g / coeff_dict['Ky_MP_NP_Trg']
    )  # Subtract Gest_AA and UrEnd for use and supply, Line 3210-3219
    return AnNPxAAUser_AbsAA


def calculate_AnNPxEAAUser_AbsEAA(
    Trg_EAAUse_g: float, 
    Gest_EAA_g: float,
    Ur_EAAEnd_g: float, 
    Abs_EAA_g: float,
    coeff_dict: dict
) -> float:
    """
    AnNPxEAAUser_AbsEAA: Efficiency of AbsEAA to export and gain NPEAA at 
                         User Entered milk protein, g NPEAA/g absorbed EAA
    """
    AnNPxEAAUser_AbsEAA = (Trg_EAAUse_g - Gest_EAA_g - Ur_EAAEnd_g) / (
        Abs_EAA_g - Ur_EAAEnd_g - Gest_EAA_g / coeff_dict['Ky_MP_NP_Trg']
    )  # Line 3220
    return AnNPxEAAUser_AbsEAA


def calculate_Trg_AbsAA_NPxprtAA_array(
    MP_NP_efficiency_dict: dict, 
    aa_list: list
) -> np.ndarray: 
    Trg_AbsAA_NPxprtAA = np.array([
        MP_NP_efficiency_dict[f"Trg_Abs{aa}_NP{aa}"]
        for aa in aa_list
        if aa != "Arg"
    ])
    return Trg_AbsAA_NPxprtAA

def calculate_Du_EAA_g(Du_AA: pd.Series) -> float:
    Du_EAA_g = Du_AA.sum()
    return Du_EAA_g
