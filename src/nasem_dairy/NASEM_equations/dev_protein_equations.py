# Protein equations

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
