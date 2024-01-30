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


def calculate_mPrtmx_AA(AA_list, coeff_dict):
    req_coeffs = ['mPrt_k_Arg_src', 'mPrt_k_His_src', 'mPrt_k_Ile_src', 'mPrt_k_Leu_src',
                  'mPrt_k_Lys_src', 'mPrt_k_Met_src', 'mPrt_k_Phe_src', 'mPrt_k_Thr_src',
                  'mPrt_k_Trp_src', 'mPrt_k_Val_src', 'mPrt_k_EAA2_src']
    check_coeffs_in_coeff_dict(coeff_dict, req_coeffs)
    AA_coeffs = np.array([coeff_dict[f'mPrt_k_{AA}_src'] for AA in AA_list])
    mPrtmx_AA = -(AA_coeffs**2) / (4 * coeff_dict['mPrt_k_EAA2_src'])
    return mPrtmx_AA


def calculate_mPrtmx_AA2(mPrtmx_AA, f_mPrt_max):
    mPrtmx_AA2 = mPrtmx_AA * f_mPrt_max     # Line 2149-2158
    return mPrtmx_AA2


def calculate_AA_mPrtmx(AA_list, coeff_dict):
    req_coeffs = ['mPrt_k_Arg_src', 'mPrt_k_His_src', 'mPrt_k_Ile_src', 'mPrt_k_Leu_src',
                  'mPrt_k_Lys_src', 'mPrt_k_Met_src', 'mPrt_k_Phe_src', 'mPrt_k_Thr_src',
                  'mPrt_k_Trp_src', 'mPrt_k_Val_src', 'mPrt_k_EAA2_src']
    check_coeffs_in_coeff_dict(coeff_dict, req_coeffs)
    AA_coeffs = np.array([coeff_dict[f"mPrt_k_{AA}_src"] for AA in AA_list])
    AA_mPrtmx = -AA_coeffs / (2 * coeff_dict['mPrt_k_EAA2_src'])
    return AA_mPrtmx


def calculate_mPrt_AA_01(AA_mPrtmx, AA_list, coeff_dict):
    req_coeffs = ['mPrt_k_Arg_src', 'mPrt_k_His_src', 'mPrt_k_Ile_src', 'mPrt_k_Leu_src',
                  'mPrt_k_Lys_src', 'mPrt_k_Met_src', 'mPrt_k_Phe_src', 'mPrt_k_Thr_src',
                  'mPrt_k_Trp_src', 'mPrt_k_Val_src', 'mPrt_k_EAA2_src']
    check_coeffs_in_coeff_dict(coeff_dict, req_coeffs)
    AA_coeffs = np.array([coeff_dict[f"mPrt_k_{AA}_src"] for AA in AA_list])
    mPrt_AA_01 = AA_mPrtmx * 0.1 * AA_coeffs + \
        (AA_mPrtmx * 0.1)**2 * coeff_dict['mPrt_k_EAA2_src']
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
