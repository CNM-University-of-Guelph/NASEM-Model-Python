# Amino Acid equations

from nasem_dairy.ration_balancer.ration_balancer_functions import check_coeffs_in_coeff_dict
import numpy as np


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


def calculate_Abs_AA_g(diet_data, Du_IdAAMic, AA_list):
    AA_coeffs = np.array([diet_data[f"Dt_Id{AA}_RUPIn"] for AA in AA_list])
    Abs_AA_g = Du_IdAAMic + AA_coeffs
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
    condition = (mPrtmx_AA2**2 - mPrt_AA_01 *
                 mPrtmx_AA2 <= 0) | (AA_mPrtmx == 0)
    # Check for sqrt of 0 or divide by 0 errors and set value to 0 if encountered
    mPrt_k_AA = np.where(condition,
                         0,
                         -(2 * np.sqrt(mPrtmx_AA2**2 - mPrt_AA_01 * mPrtmx_AA2) -
                           2 * mPrtmx_AA2) / (AA_mPrtmx * 0.1))
    return mPrt_k_AA
