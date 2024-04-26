# Amino Acid equations

from nasem_dairy.ration_balancer.ration_balancer_functions import check_coeffs_in_coeff_dict
import numpy as np
import math
import pandas as pd


def calculate_Du_AAMic(Du_MiTP_g, AA_list, coeff_dict):
    req_coeffs = ['MiTPArgProf', 'MiTPHisProf', 'MiTPIleProf', 'MiTPLeuProf',
                  'MiTPLysProf', 'MiTPMetProf', 'MiTPPheProf', 'MiTPThrProf',
                  'MiTPTrpProf', 'MiTPValProf']
    check_coeffs_in_coeff_dict(coeff_dict, req_coeffs)
    AA_coeffs = np.array([coeff_dict[f"MiTP{AA}Prof"] for AA in AA_list])
    Du_AAMic = Du_MiTP_g * AA_coeffs / 100   # Line 1573-1582
    return Du_AAMic


def calculate_Du_IdAAMic(Du_AAMic, coeff_dict):
    req_coeffs = ['SI_dcMiCP']
    check_coeffs_in_coeff_dict(coeff_dict, req_coeffs)
    Du_IdAAMic = Du_AAMic * coeff_dict['SI_dcMiCP'] / 100
    return Du_IdAAMic


def calculate_Abs_AA_g(AA_list, An_data, infusion_data, Inf_Art):
    # An_data and infusion_data are dictionaries, convert to Series so that Abs_AA_g
    # can be added to AA_values dataframe
    # Entire dictionaries are arguments as need to extract 10 values from each
    An_IdAAIn = pd.Series([An_data[f'An_Id{AA}In'] for AA in AA_list], index=AA_list)
    Inf_AA_g = pd.Series([infusion_data[f'Inf_{AA}_g'] for AA in AA_list], index=AA_list)
    Abs_AA_g = An_IdAAIn + Inf_AA_g * Inf_Art
    return Abs_AA_g


def calculate_mPrtmx_AA(mPrt_k_AA: np.array, mPrt_coeff: dict) -> np.array:
    """
    mPrtmx_AA: Maximum milk protein responses from each AA
    """
    mPrtmx_AA = -(mPrt_k_AA**2) / (4 * mPrt_coeff['mPrt_k_EAA2_src'])   # maximum milk protein responses from each AA, Line 2117-2126
    return mPrtmx_AA


def calculate_mPrtmx_AA2(mPrtmx_AA, f_mPrt_max):
    mPrtmx_AA2 = mPrtmx_AA * f_mPrt_max     # Line 2149-2158
    return mPrtmx_AA2


def calculate_AA_mPrtmx(mPrt_k_AA: np.array, mPrt_coeff: dict) -> np.array:
    """
    AA_mPrtmx: AA input at maximum milk protein response for each AA
    """
    AA_mPrtmx = -mPrt_k_AA / (2 * mPrt_coeff['mPrt_k_EAA2_src'])    # AA input at maximum milk protein response for each AA, Line 2127-2136
    return AA_mPrtmx


def calculate_mPrt_AA_01(AA_mPrtmx: np.array, mPrt_k_AA: np.array, mPrt_coeff: dict) -> np.array:
    """
    mPrt_AA_01: Milk protein from each EAA at 10% of max response
    """
    mPrt_AA_01 = AA_mPrtmx * 0.1 * mPrt_k_AA + (AA_mPrtmx * 0.1)**2 * mPrt_coeff['mPrt_k_EAA2_src'] # Milk prt from each EAA at 10% of Max response, Line 2138-2147
    return mPrt_AA_01


def calculate_mPrt_k_AA(mPrtmx_AA2, mPrt_AA_01, AA_mPrtmx):
    condition = (mPrtmx_AA2**2 - mPrt_AA_01 * mPrtmx_AA2 <= 0) | (AA_mPrtmx == 0)
    # Check for sqrt of 0 or divide by 0 errors and set value to 0 if encountered
    mPrt_k_AA = np.where(condition,
                         0,
                         -(2 * np.sqrt(mPrtmx_AA2**2 - mPrt_AA_01 * mPrtmx_AA2) -
                           2 * mPrtmx_AA2) / (AA_mPrtmx * 0.1))
    return mPrt_k_AA


def calculate_Abs_EAA_g(Abs_AA_g):
    Abs_EAA_g = Abs_AA_g.sum()  # Line 1769, in R written as line below
    # Abs_EAA_g = Abs_AA_g['Arg'] + Abs_AA_g['His'] + Abs_AA_g['Ile'] + Abs_AA_g['Leu'] + Abs_AA_g['Lys'] \
    #             + Abs_AA_g['Met'] + Abs_AA_g['Phe'] + Abs_AA_g['Thr'] + Abs_AA_g['Trp'] + Abs_AA_g['Val']
    return Abs_EAA_g


def calculate_Abs_neAA_g(An_MPIn_g, Abs_EAA_g):
    # Line 1771, Absorbed NEAA (Equation 20-150 p. 433)
    Abs_neAA_g = An_MPIn_g * 1.15 - Abs_EAA_g
    return Abs_neAA_g


def calculate_Abs_OthAA_g(Abs_neAA_g, Abs_AA_g):
    Abs_OthAA_g = Abs_neAA_g + Abs_AA_g['Arg'] + Abs_AA_g['Phe'] + \
        Abs_AA_g['Thr'] + Abs_AA_g['Trp'] + \
        Abs_AA_g['Val']  # Line 2110, NRC eqn only
    # Equation 20-186a, p. 436
    return Abs_OthAA_g


def calculate_Abs_EAA2_g(Abs_AA_g: pd.Series) -> float:
    """
    Abs_EAA2_g: Sum of all squared EAA
    """
    Abs_EAA2_g = Abs_AA_g['Arg']**2 + Abs_AA_g['His']**2 + Abs_AA_g['Ile']**2 + Abs_AA_g['Leu']**2 + Abs_AA_g['Lys']**2 + \
                 Abs_AA_g['Met']**2 + Abs_AA_g['Phe']**2 + Abs_AA_g['Thr']**2 + Abs_AA_g['Trp']**2 + Abs_AA_g['Val']**2 # Line 1775-1776
    return Abs_EAA2_g


def calculate_Abs_EAA2_HILKM_g(Abs_AA_g):
    Abs_EAA2_HILKM_g = Abs_AA_g['His']**2 + Abs_AA_g['Ile']**2 + Abs_AA_g['Leu']**2 + \
        Abs_AA_g['Lys']**2 + \
        Abs_AA_g['Met']**2  # Line 1778, NRC 2020 (no Arg, Phe, Thr, Trp, or Val)
    return Abs_EAA2_HILKM_g


def calculate_Abs_EAA2_RHILKM_g(Abs_AA_g):
    Abs_EAA2_RHILKM_g = Abs_AA_g['Arg']**2 + Abs_AA_g['His']**2 + Abs_AA_g['Ile']**2 + \
        Abs_AA_g['Leu']**2 + \
        Abs_AA_g['Lys']**2 + \
        Abs_AA_g['Met']**2  # Line 1780, Virginia Tech 1 (no Phe, Thr, Trp, or Val)
    return Abs_EAA2_RHILKM_g


def calculate_Abs_EAA2_HILKMT_g(Abs_AA_g):
    Abs_EAA2_HILKMT_g = Abs_AA_g['His']**2 + Abs_AA_g['Ile']**2 + \
        Abs_AA_g['Leu']**2 + Abs_AA_g['Lys']**2 + \
        Abs_AA_g['Met']**2 + Abs_AA_g['Thr']**2
    return Abs_EAA2_HILKMT_g


def calculate_Abs_EAA2b_g(mPrt_eqn, Abs_AA_g):
    if mPrt_eqn == 2:
        # Line 2107, NRC eqn.
        Abs_EAA2b_g = calculate_Abs_EAA2_RHILKM_g(Abs_AA_g)
    elif mPrt_eqn == 3:
        # Line 2108, VT1 eqn.
        Abs_EAA2b_g = calculate_Abs_EAA2_HILKMT_g(Abs_AA_g)
    else:
        # Line 2106, VT2 eqn.
        Abs_EAA2b_g = calculate_Abs_EAA2_HILKM_g(Abs_AA_g)
    return Abs_EAA2b_g


def calculate_mPrt_k_EAA2(mPrtmx_Met2, mPrt_Met_0_1, Met_mPrtmx):
    # Scale the quadratic; can be calculated from any of the AA included in the squared term. All give the same answer
    # Methionine used to be consistent with R code
    mPrt_k_EAA2 = (2 * math.sqrt(mPrtmx_Met2**2 - mPrt_Met_0_1 * mPrtmx_Met2) -
                   2 * mPrtmx_Met2 + mPrt_Met_0_1) / (Met_mPrtmx * 0.1)**2  # Line 2184
    return mPrt_k_EAA2


def calculate_Du_AAEndP(Du_EndCP_g: float, AA_list: list, coeff_dict: dict) -> pd.Series:
    """
    Du_AAEndP: Duodenal EndPAA, g hydrated true AA/d 
    """
    # Duodenal EndPAA, g hydrated true AA/d 
    req_coeffs = ['EndArgProf', 'EndHisProf', 'EndIleProf', 'EndLeuProf', 'EndLysProf', 
                  'EndMetProf', 'EndPheProf', 'EndThrProf', 'EndTrpProf', 'EndValProf']
    check_coeffs_in_coeff_dict(coeff_dict, req_coeffs)
    AA_coeffs = np.array([coeff_dict[f"End{AA}Prof"] for AA in AA_list])
    Du_AAEndP = Du_EndCP_g * AA_coeffs / 100  # Lines 1585-1594
    return Du_AAEndP


def calculate_Du_AA(diet_data, infusion_data, Du_AAMic, Du_AAEndP, AA_list) -> pd.Series:
    """
    Du_AA: Total ruminal AA outflows, g hydr, fully recovered AA/d (true protein bound AA flows)
    """
    # Total ruminal AA outflows, g hydr, fully recovered AA/d (true protein bound AA flows)
    # These should have _g at the end of each
    Dt_AARUPIn = np.array([diet_data[f"Dt_{AA}RUPIn"] for AA in AA_list])
    Inf_AARUPIn = np.array([infusion_data[f"Inf_{AA}RUPIn"] for AA in AA_list])
    Du_AA = Dt_AARUPIn + Inf_AARUPIn + Du_AAMic + Du_AAEndP # Line 1597-1606
    return Du_AA


def calculate_DuAA_AArg(Du_AA, diet_data, AA_list) -> pd.Series:
    """
    DuAA_DtAA: Duodenal AA flow expressed as a fraction of dietary AA
    """
    # Duodenal AA flow expressed as a fraction of dietary AA, ruminally infused included in Du but not Dt
    Dt_AAIn = np.array([diet_data[f"Dt_{AA}In"] for AA in AA_list])
    DuAA_DtAA = Du_AA / Dt_AAIn # Line 1610-1619
    return DuAA_DtAA


def calculate_Du_AA24h(Du_AA, AA_list, coeff_dict) -> pd.Series:
    """
    Du_AA24h: g hydrat 24h recovered AA/d
    """
    # The following predicted AA flows are for comparison to observed Duod AA flows, g hydrat 24h recovered AA/d
    RecAA = np.array([coeff_dict[f"Rec{AA}"] for AA in AA_list])
    Du_AA24h = Du_AA * RecAA    # Line 1622-1631
    return Du_AA24h


def calculate_IdAA_DtAA(diet_data: dict, An_data: dict, AA_list: list) -> np.array:
    """
    IdAA_DtAA: Intestinally Digested AA flow expressed as a fraction of dietary AA
    """
    #Intestinally Digested AA flow expressed as a fraction of dietary AA
    #ruminally and intesntinally infused included in id but not Dt
    Dt_AAIn = np.array([diet_data[f"Dt_{AA}In"] for AA in AA_list])
    An_IdAAIn = np.array([An_data[f'An_Id{AA}In'] for AA in AA_list])
    IdAA_DtAA = An_IdAAIn / Dt_AAIn # Lines 1728-1737
    return IdAA_DtAA


def calculate_Abs_AA_MPp(Abs_AA_g: pd.Series, An_MPIn_g: float) -> pd.Series:
    """
    Abs_AA_MPp: AA as a percent of metabolizable protein
    """
    Abs_AA_MPp = Abs_AA_g / An_MPIn_g * 100   # Lines 1787-1796
    return Abs_AA_MPp
    

def calculate_Abs_AA_p(Abs_AA_g: pd.Series, Abs_EAA_g: float) -> pd.Series:
    """
    Abs_AA_p: Absorbed AA as a percent of total absorbed EAA
    """
    Abs_AA_p = Abs_AA_g / Abs_EAA_g * 100   # Lines 1799-1808
    return Abs_AA_p
    

def calculate_Abs_AA_DEI(Abs_AA_g: pd.Series, An_DEIn: float) -> pd.Series:
    """
    Abs_AA_DEI: Absorbed AA per Mcal digestable energy intake (g/Mcal)?
    """
    Abs_AA_DEI = Abs_AA_g / An_DEIn # Lines 1811-1820
    return Abs_AA_DEI
    

def calculate_Abs_AA_mol(Abs_AA_g: pd.Series, coeff_dict: dict, AA_list: list) -> np.array:
    """
    Abs_AA_mol: moles of absorbed AA (mol/d)
    """
    MWAA = np.array([coeff_dict[f"MW{AA}"] for AA in AA_list])
    Abs_AA_mol = Abs_AA_g / MWAA    # Line 1823-1832
    return Abs_AA_mol   


def calculate_Body_AAGain_g(Body_NPgain_g: float, coeff_dict: dict, AA_list: list) -> np.array:
    """
    Body_AAGain_g: Body AA gain (g/d)
    """
    Body_AA_TP = np.array([coeff_dict[f"Body_{AA}_TP"] for AA in AA_list])
    Body_AAGain_g = Body_NPgain_g * Body_AA_TP / 100    # Line 2497-2506
    return Body_AAGain_g
    

def calculate_Body_EAAGain_g(Body_AAGain_g: pd.Series) -> float:
    """
    Body_EAAGain_g: Body EAA gain (g/d)
    """
    Body_EAAGain_g = Body_AAGain_g.sum()    # Line 2507-2508
    return Body_EAAGain_g
    

def calculate_BodyAA_AbsAA(Body_AAGain_g: pd.Series, Abs_AA_g: pd.Series) -> pd.Series:
    """
    BodyAA_AbsAA: Body AA gain as a fraction of absolute AA intake
    """
    BodyAA_AbsAA = Body_AAGain_g / Abs_AA_g # Line 2510-2519
    return BodyAA_AbsAA
    

def calculate_An_AAUse_g(Gest_AA_g: pd.Series, Mlk_AA_g: pd.Series, Body_AAGain_g: pd.Series, Scrf_AA_g: pd.Series, Fe_AAMet_g: pd.Series, Ur_AAEnd_g: pd.Series) -> pd.Series:
    """
    An_AAUse_g: Total net AA use (g/d)
    """
    An_AAUse_g = Gest_AA_g + Mlk_AA_g + Body_AAGain_g + Scrf_AA_g + Fe_AAMet_g + Ur_AAEnd_g # Total Net AA use (Nutrient Allowable), g/d, Line 2544-2553
    return An_AAUse_g


def calculate_An_EAAUse_g(An_AAUse_g: pd.Series) -> float:
    """
    An_EAAUse_g: Total net EAA use (g/d)
    """
    An_EAAUse_g = An_AAUse_g.sum()  # Line 2554-2555
    return An_EAAUse_g


def calculate_AnAAUse_AbsAA(An_AAUse_g: pd.Series, Abs_AA_g: pd.Series) -> pd.Series:
    """
    AnAAUse_AbsAA: Total net AA efficieny (g/g)
    """
    AnAAUse_AbsAA = An_AAUse_g / Abs_AA_g   # Total Net AA efficiency, g/g absorbed, Line 2558-2567
    return AnAAUse_AbsAA


def calculate_AnEAAUse_AbsEAA(An_EAAUse_g: float, Abs_EAA_g: float) -> float:
    """
    AnEAAUse_AbsEAA: Total net EAA efficieny (g/g)
    """
    AnEAAUse_AbsEAA = An_EAAUse_g / Abs_EAA_g   # Line 2568
    return AnEAAUse_AbsEAA


def calculate_An_AABal_g(Abs_AA_g: pd.Series, An_AAUse_g: pd.Series) -> pd.Series:
    """
    An_AABal_g: Total net AA balance (g/d)
    """
    An_AABal_g = Abs_AA_g - An_AAUse_g    # Total Net AA Balance, g/d, Line 2571-2580
    return An_AABal_g


def calculate_An_EAABal_g(Abs_EAA_g: float, An_EAAUse_g: float) -> float:
    """
    An_EAABal_g: Total net EAA balance (g/d)
    """
    An_EAABal_g = Abs_EAA_g - An_EAAUse_g   # Line 2581
    return An_EAABal_g


def calculate_Trg_AbsEAA_NPxprtEAA(Trg_AbsAA_NPxprtAA: np.array) -> np.array:
    """
    Trg_AbsEAA_NPxprtEAA: Target postabsorptive EAA efficiencies based on maximum obsreved efficiencies from Martineau and LaPiere as listed in NRC, Ch. 6.
    """
    Trg_AbsEAA_NPxprtEAA = Trg_AbsAA_NPxprtAA.sum() / 9 # Should be weighted or derived directly from total EAA, Line 2593-2594
    return Trg_AbsEAA_NPxprtEAA


def calculate_Trg_AbsArg_NPxprtArg(Trg_AbsEAA_NPxprtEAA) -> float:
    """
    Trg_AbsArg_NPxprtArg: Target postabsorptive efficiencies based on maximum obsreved efficiencies from Martineau and LaPiere as listed in NRC, Ch. 6.
    """
    Trg_AbsArg_NPxprtArg = Trg_AbsEAA_NPxprtEAA # none provided thus assumed to be the same as for EAA, Line 2595
    return Trg_AbsArg_NPxprtArg


def calculate_Trg_AAEff_EAAEff(Trg_AbsAA_NPxprtAA: pd.Series, Trg_AbsEAA_NPxprtEAA: float) -> pd.Series:
    """
    Trg_AAEff_EAAEff: Estimate the degree of AA imbalance within the EAA as ratios of each Eff to the total EAA Eff.
    """
    # Estimate the degree of AA imbalance within the EAA as ratios of each Eff to the total EAA Eff.
    # These "Target" ratios are calculated as efficiency target (NRC 2021 Ch. 6) / total EAA eff.
    # Thus they are scaled to Ch. 6 targets.  Ch. 6 values should not be used directly here. Ratio first.
    # The target eff from Ch. 6 are likely not true maximum efficiencies.
    # ratio to the mean Trg for each EAA / total EAA Trg of 70.6%, e.g. Ile Trg is 97.3% of 70.6%
    Trg_AAEff_EAAEff = Trg_AbsAA_NPxprtAA / Trg_AbsEAA_NPxprtEAA    # Line 2602-2611
    return Trg_AAEff_EAAEff


def calculate_An_AAEff_EAAEff(An_AAUse_AbsAA: pd.Series, AnEAAUse_AbsEAA: pd.Series) -> pd.Series:
    """
    An_AAEff_EAAEff: AA efficiency as ratio of EAA efficiency
    """
    # Calculate the current ratios for the diet.  This centers the ratio to the prevailing EAA Efficiency   
    An_AAEff_EAAEff = An_AAUse_AbsAA / AnEAAUse_AbsEAA  # Line 2614-2623
    return An_AAEff_EAAEff


def calculate_Imb_AA(An_AAEff_EAAEff: pd.Series, Trg_AAEff_EAAEff: float, f_Imb: np.array) -> pd.Series:
    """
    Imb_AA: Calculate a relative penalty for each EAA to reflect the degree of imbalance for each
    """
    # Calculate a relative penalty for each EAA to reflect the degree of imbalance for each.
    # if the diet eff = Trg_eff then no penalty. f_Imb is a vector of penalty costs for each EAA.
    # f_Imb should be passed to the model fn rather than handled as a global variable.
    Imb_AA = ((An_AAEff_EAAEff - Trg_AAEff_EAAEff) * f_Imb)**2
    return Imb_AA


def calculate_Imb_EAA(Imb_AA) -> float:
    """
    Imb_EAA: Sum the penalty to get a relative imbalance value for the optimizer 
    """
    # Sum the penalty to get a relative imbalance value for the optimizer
    Imb_EAA = Imb_AA.sum()
    return Imb_EAA
