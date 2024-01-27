# dev_gestation_equations

from nasem_dairy.ration_balancer.ration_balancer_functions import check_coeffs_in_coeff_dict
import math


def calculate_Uter_Wtpart(Fet_BWbrth, coeff_dict):
    req_coeff = ['UterWt_FetBWbrth']
    check_coeffs_in_coeff_dict(coeff_dict, req_coeff)
    Uter_Wtpart = Fet_BWbrth * coeff_dict['UterWt_FetBWbrth']
    return Uter_Wtpart


def calculate_Uter_Wt(An_Parity_rl, An_AgeDay, An_LactDay, An_GestDay, An_GestLength, Uter_Wtpart, coeff_dict):
    req_coeff = ['Uter_Wt', 'Uter_Ksyn', 'Uter_KsynDecay', 'Uter_Kdeg']
    check_coeffs_in_coeff_dict(coeff_dict, req_coeff)
    Uter_Wt = coeff_dict['Uter_Wt']     # Line 2312
    if An_AgeDay < 240:                 # Line 2313
        Uter_Wt = 0

    if An_GestDay > 0 and An_GestDay <= An_GestLength:  # Line 2314
        Uter_Wt = Uter_Wtpart * \
            math.exp(-(coeff_dict['Uter_Ksyn'] - coeff_dict['Uter_KsynDecay']
                     * An_GestDay) * (An_GestLength - An_GestDay))

    if An_GestDay <= 0 and An_LactDay > 0 and An_LactDay < 100:     # Line 2316
        Uter_Wt = (Uter_Wtpart-0.204) * \
            math.exp(-coeff_dict['Uter_Kdeg'] * An_LactDay) + 0.204

    if An_Parity_rl > 0 and Uter_Wt < 0.204:    # Line 2318
        Uter_Wt = 0.204
    return Uter_Wt


def calculate_GrUter_Wtpart(Fet_BWbrth, coeff_dict):
    req_coeff = ['GrUterWt_FetBWbrth']
    check_coeffs_in_coeff_dict(coeff_dict, req_coeff)
    GrUter_Wtpart = Fet_BWbrth * \
        coeff_dict['GrUterWt_FetBWbrth']    # Line 2322
    return GrUter_Wtpart


def calculate_GrUter_Wt(An_GestDay, An_GestLength, Uter_Wt, GrUter_Wtpart, coeff_dict):
    req_coeff = ['GrUter_Ksyn', 'GrUter_KsynDecay']
    check_coeffs_in_coeff_dict(coeff_dict, req_coeff)
    GrUter_Wt = Uter_Wt
    if An_GestDay > 0 and An_GestDay <= An_GestLength:      # Line 2323-2327
        GrUter_Wt = GrUter_Wtpart * math.exp(-(coeff_dict['GrUter_Ksyn'] -
                                               coeff_dict['GrUter_KsynDecay'] * An_GestDay)*(An_GestLength-An_GestDay))
    if GrUter_Wt < Uter_Wt:
        GrUter_Wt = Uter_Wt
    return GrUter_Wt


def calculate_Uter_BWgain(An_LactDay, An_GestDay, An_GestLength, Uter_Wt, coeff_dict):
    req_coeff = ['Uter_BWgain', 'Uter_Ksyn', 'Uter_KsynDecay', 'Uter_Kdeg']
    check_coeffs_in_coeff_dict(coeff_dict, req_coeff)
    Uter_BWgain = coeff_dict['Uter_BWgain']
    if An_GestDay > 0 and An_GestDay <= An_GestLength:
        Uter_BWgain = (
            coeff_dict['Uter_Ksyn'] - coeff_dict['Uter_KsynDecay'] * An_GestDay) * Uter_Wt
    if An_GestDay <= 0 and An_LactDay > 0 and An_LactDay < 100:  # uterine involution after calving
        Uter_BWgain = -coeff_dict['Uter_Kdeg'] * Uter_Wt
    return Uter_BWgain


def calculate_GrUter_BWgain(An_LactDay, An_GestDay, An_GestLength, GrUter_Wt, Uter_BWgain, coeff_dict):
    req_coeff = ['GrUter_BWgain', 'GrUter_Ksyn', 'GrUter_KsynDecay']
    check_coeffs_in_coeff_dict(coeff_dict, req_coeff)
    GrUter_BWgain = coeff_dict['GrUter_BWgain']     # Line 2341-2345
    if An_GestDay > 0 and An_GestDay <= An_GestLength:
        GrUter_BWgain = (
            coeff_dict['GrUter_Ksyn'] - coeff_dict['GrUter_KsynDecay'] * An_GestDay) * GrUter_Wt
    if An_GestDay <= 0 and An_LactDay > 0 and An_LactDay < 100:
        GrUter_BWgain = Uter_BWgain
    return GrUter_BWgain


def calculate_Gest_NCPgain_g(GrUter_BWgain, coeff_dict):
    req_coeff = ['CP_GrUtWt']
    check_coeffs_in_coeff_dict(coeff_dict, req_coeff)
    Gest_NCPgain_g = GrUter_BWgain * coeff_dict['CP_GrUtWt'] * 1000
    return Gest_NCPgain_g


def calculate_Gest_NPgain_g(Gest_NCPgain_g, coeff_dict):
    req_coeff = ['Body_NP_CP']
    check_coeffs_in_coeff_dict(coeff_dict, req_coeff)
    Gest_NPgain_g = Gest_NCPgain_g * coeff_dict['Body_NP_CP']
    return Gest_NPgain_g


def calculate_Gest_NPuse_g(Gest_NPgain_g, coeff_dict):
    req_coeff = ['Gest_NPother_g']
    check_coeffs_in_coeff_dict(coeff_dict, req_coeff)
    Gest_NPuse_g = Gest_NPgain_g + coeff_dict['Gest_NPother_g']   # Line 2366
    return Gest_NPuse_g


def calculate_Gest_CPuse_g(Gest_NPuse_g, coeff_dict):
    req_coeff = ['Body_NP_CP']
    check_coeffs_in_coeff_dict(coeff_dict, req_coeff)
    Gest_CPuse_g = Gest_NPuse_g / coeff_dict['Body_NP_CP']   # Line 2367
    return Gest_CPuse_g