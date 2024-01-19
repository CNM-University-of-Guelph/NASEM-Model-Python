# dev_animal_equations
import numpy as np
from nasem_dairy.ration_balancer.ration_balancer_functions import check_coeffs_in_coeff_dict

####################
# Functions for Animal Level Intakes
####################

# An_DMIn_BW is calculated seperately after DMI selection to use in calculate_diet_data
def calculate_An_DMIn_BW(An_BW, Dt_DMIn):
    An_DMIn_BW = Dt_DMIn / An_BW        # Line 935
    return An_DMIn_BW


def calculate_An_RDPIn(Dt_RDPIn, InfRum_RDPIn):
    An_RDPIn = Dt_RDPIn + InfRum_RDPIn
    return An_RDPIn


def calculate_An_RDP(An_RDPIn, Dt_DMIn, InfRum_DMIn):
    An_RDP = An_RDPIn / (Dt_DMIn + InfRum_DMIn) * 100
    return An_RDP


def calculate_An_RDPIn_g(An_RDPIn):
    An_RDPIn_g = An_RDPIn * 1000
    return An_RDPIn_g


def calculate_An_NDFIn(Dt_NDFIn, InfRum_NDFIn, InfSI_NDFIn):
    An_NDFIn = Dt_NDFIn + InfRum_NDFIn + InfSI_NDFIn  # Line 942
    return An_NDFIn


def calculate_An_NDF(An_NDFIn, Dt_DMIn, InfRum_DMIn, InfSI_DMIn):
    An_NDF = An_NDFIn / (Dt_DMIn + InfRum_DMIn + InfSI_DMIn) * 100  # Line 944
    return An_NDF


def calculate_An_DigNDFIn(Dt_DigNDFIn, InfRum_NDFIn, TT_dcNDF):
    # Line 1063, should consider SI and LI infusions as well, but no predictions of LI NDF digestion available.
    An_DigNDFIn = Dt_DigNDFIn + InfRum_NDFIn * TT_dcNDF / 100
    return An_DigNDFIn


def calculate_An_DENDFIn(An_DigNDFIn, coeff_dict):
    req_coeff = ['En_NDF']
    check_coeffs_in_coeff_dict(coeff_dict, req_coeff)
    An_DENDFIn = An_DigNDFIn * \
        coeff_dict['En_NDF']                   # Line 1353
    return An_DENDFIn


def calculate_An_DigStIn(Dt_DigStIn, Inf_StIn, Inf_ttdcSt):
    # Line 1033, Glc considered as WSC and thus with rOM
    An_DigStIn = Dt_DigStIn + Inf_StIn * Inf_ttdcSt / 100
    return An_DigStIn


def calculate_An_DEStIn(An_DigStIn, coeff_dict):
    req_coeff = ['En_St']
    check_coeffs_in_coeff_dict(coeff_dict, req_coeff)
    An_DEStIn = An_DigStIn * coeff_dict['En_St']               # Line 1351
    return An_DEStIn


def calculate_An_DigrOMaIn(Dt_DigrOMaIn, InfRum_GlcIn, InfRum_AcetIn, InfRum_PropIn, InfRum_ButrIn, InfSI_GlcIn, InfSI_AcetIn, InfSI_PropIn, InfSI_ButrIn):
    An_DigrOMaIn = (Dt_DigrOMaIn + InfRum_GlcIn + InfRum_AcetIn + InfRum_PropIn +
                    InfRum_ButrIn + InfSI_GlcIn + InfSI_AcetIn + InfSI_PropIn + InfSI_ButrIn)   # Line 1023-1024
    return An_DigrOMaIn


def calculate_An_DErOMIn(An_DigrOMaIn, coeff_dict):
    req_coeff = ['En_rOM']
    check_coeffs_in_coeff_dict(coeff_dict, req_coeff)
    An_DErOMIn = An_DigrOMaIn * coeff_dict['En_rOM']   # Line 1351
    return An_DErOMIn


def calculate_An_idRUPIn(Dt_idRUPIn, InfRum_idRUPIn, InfSI_idTPIn):
    # Line 1099, SI infusions considered here
    An_idRUPIn = Dt_idRUPIn + InfRum_idRUPIn + InfSI_idTPIn
    return An_idRUPIn


def calculate_An_RUPIn(Dt_RUPIn, InfRum_RUPIn):
    An_RUPIn = Dt_RUPIn + InfRum_RUPIn
    return An_RUPIn


def calculate_An_DMIn(Dt_DMIn, Inf_DMIn):
    An_DMIn = Dt_DMIn + Inf_DMIn
    return An_DMIn


def calculate_An_CPIn(Dt_CPIn, Inf_CPIn):
    An_CPIn = Dt_CPIn + Inf_CPIn      # Line 947
    return An_CPIn


def calculate_An_DigCPaIn(An_CPIn, InfArt_CPIn, Fe_CP):
    An_DigCPaIn = An_CPIn - InfArt_CPIn - Fe_CP  # apparent total tract
    return An_DigCPaIn


def calculate_An_DECPIn(An_DigCPaIn, coeff_dict):
    req_coeff = ['En_CP']
    check_coeffs_in_coeff_dict(coeff_dict, req_coeff)
    An_DECPIn = An_DigCPaIn * coeff_dict['En_CP']
    return An_DECPIn


def calculate_An_DENPNCPIn(Dt_NPNCPIn, coeff_dict):
    req_coeff = ['dcNPNCP', 'En_NPNCP']
    check_coeffs_in_coeff_dict(coeff_dict, req_coeff)
    An_DENPNCPIn = Dt_NPNCPIn * \
        coeff_dict['dcNPNCP'] / 100 * coeff_dict['En_NPNCP']
    return An_DENPNCPIn


def calculate_An_DETPIn(An_DECPIn, An_DENPNCPIn, coeff_dict):
    req_coeff = ['En_NPNCP', 'En_CP']
    check_coeffs_in_coeff_dict(coeff_dict, req_coeff)
    # Line 1355, Caution! DigTPaIn not clean so subtracted DE for CP equiv of NPN to correct. Not a true DE_TP.
    An_DETPIn = An_DECPIn - An_DENPNCPIn / \
        coeff_dict['En_NPNCP'] * coeff_dict['En_CP']
    return An_DETPIn


def calculate_An_DigFAIn(Dt_DigFAIn, Inf_DigFAIn):
    An_DigFAIn = Dt_DigFAIn + Inf_DigFAIn       # Line 1308
    return An_DigFAIn


def calculate_An_DEFAIn(An_DigFAIn, coeff_dict):
    req_coeff = ['En_FA']
    check_coeffs_in_coeff_dict(coeff_dict, req_coeff)
    An_DEFAIn = An_DigFAIn * coeff_dict['En_FA']    # Line 1361
    return An_DEFAIn


def calculate_An_DEIn(An_StatePhys, An_DENDFIn, An_DEStIn, An_DErOMIn, An_DETPIn, An_DENPNCPIn, An_DEFAIn, Inf_DEAcetIn, Inf_DEPropIn, Inf_DEButrIn, Dt_DMIn_ClfLiq, Dt_DEIn, Monensin_eqn):
    An_DEIn = (An_DENDFIn + An_DEStIn + An_DErOMIn + An_DETPIn +
               An_DENPNCPIn + An_DEFAIn + Inf_DEAcetIn +
               Inf_DEPropIn + Inf_DEButrIn)
    condition = (An_StatePhys == "Calf") and (Dt_DMIn_ClfLiq > 0)
    # Infusion DE not considered for milk-fed calves
    An_DEIn = np.where(condition, Dt_DEIn, An_DEIn)
    An_DEIn = np.where(Monensin_eqn == 1, An_DEIn * 1.02, An_DEIn)
    return An_DEIn

####################
# Animal Warpper Functions
####################


def calculate_An_data_initial(animal_input, diet_data, infusion_data, coeff_dict):
    # Could use a better name, An_data for now
    An_data = {}
    An_data['An_RDPIn'] = calculate_An_RDPIn(diet_data['Dt_RDPIn'],
                                             infusion_data['InfRum_RDPIn'])
    An_data['An_RDP'] = calculate_An_RDP(An_data['An_RDPIn'],
                                         animal_input['DMI'],
                                         infusion_data['InfRum_DMIn'])
    An_data['An_RDPIn_g'] = calculate_An_RDPIn_g(An_data['An_RDPIn'])
    An_data['An_NDFIn'] = calculate_An_NDFIn(diet_data['Dt_NDFIn'],
                                             infusion_data['InfRum_NDFIn'],
                                             infusion_data['InfSI_NDFIn'])
    An_data['An_NDF'] = calculate_An_NDF(An_data['An_NDFIn'],
                                         animal_input['DMI'],
                                         infusion_data['InfRum_DMIn'],
                                         infusion_data['InfSI_DMIn'])
    An_data['An_DigNDFIn'] = calculate_An_DigNDFIn(diet_data['Dt_DigNDFIn'],
                                                   infusion_data['InfRum_NDFIn'],
                                                   diet_data['TT_dcNDF'])
    An_data['An_DENDFIn'] = calculate_An_DENDFIn(An_data['An_DigNDFIn'],
                                                 coeff_dict)
    An_data['An_DigStIn'] = calculate_An_DigStIn(diet_data['Dt_DigStIn'],
                                                 infusion_data['Inf_StIn'],
                                                 infusion_data['Inf_ttdcSt'])
    An_data['An_DEStIn'] = calculate_An_DEStIn(An_data['An_DigStIn'],
                                               coeff_dict)
    An_data['An_DigrOMaIn'] = calculate_An_DigrOMaIn(diet_data['Dt_DigrOMaIn'],
                                                     infusion_data['InfRum_GlcIn'],
                                                     infusion_data['InfRum_AcetIn'],
                                                     infusion_data['InfRum_PropIn'],
                                                     infusion_data['InfRum_ButrIn'],
                                                     infusion_data['InfSI_GlcIn'],
                                                     infusion_data['InfSI_AcetIn'],
                                                     infusion_data['InfSI_PropIn'],
                                                     infusion_data['InfSI_ButrIn'])
    An_data['An_DErOMIn'] = calculate_An_DErOMIn(An_data['An_DigrOMaIn'],
                                                 coeff_dict)
    An_data['An_idRUPIn'] = calculate_An_idRUPIn(diet_data['Dt_idRUPIn'],
                                                 infusion_data['InfRum_idRUPIn'],
                                                 infusion_data['InfSI_idTPIn'])
    An_data['An_RUPIn'] = calculate_An_RUPIn(diet_data['Dt_RUPIn'],
                                             infusion_data['InfRum_RUPIn'])
    An_data['An_DMIn'] = calculate_An_DMIn(animal_input['DMI'],
                                           infusion_data['Inf_DMIn'])
    An_data['An_CPIn'] = calculate_An_CPIn(diet_data['Dt_CPIn'],
                                           infusion_data['Inf_CPIn'])
    return An_data


def calculate_An_data_complete(An_data_initial, diet_data, An_StatePhys, Fe_CP, infusion_data, equation_selection, coeff_dict):
    complete_An_data = An_data_initial.copy()

    complete_An_data['An_DigCPaIn'] = calculate_An_DigCPaIn(complete_An_data['An_CPIn'],
                                                            infusion_data['InfArt_CPIn'],
                                                            Fe_CP)
    complete_An_data['An_DECPIn'] = calculate_An_DECPIn(complete_An_data['An_DigCPaIn'],
                                                        coeff_dict)
    complete_An_data['An_DENPNCPIn'] = calculate_An_DENPNCPIn(diet_data['Dt_NPNCPIn'],
                                                              coeff_dict)
    complete_An_data['An_DETPIn'] = calculate_An_DETPIn(complete_An_data['An_DECPIn'],
                                                        complete_An_data['An_DENPNCPIn'],
                                                        coeff_dict)
    complete_An_data['An_DigFAIn'] = calculate_An_DigFAIn(diet_data['Dt_DigFAIn'],
                                                          infusion_data['Inf_DigFAIn'])
    complete_An_data['An_DEFAIn'] = calculate_An_DEFAIn(complete_An_data['An_DigFAIn'],
                                                        coeff_dict)
    complete_An_data['An_DEIn'] = calculate_An_DEIn(An_StatePhys,
                                                    complete_An_data['An_DENDFIn'],
                                                    complete_An_data['An_DEStIn'],
                                                    complete_An_data['An_DErOMIn'],
                                                    complete_An_data['An_DETPIn'],
                                                    complete_An_data['An_DENPNCPIn'],
                                                    complete_An_data['An_DEFAIn'],
                                                    infusion_data['Inf_DEAcetIn'],
                                                    infusion_data['Inf_DEPropIn'],
                                                    infusion_data['Inf_DEPropIn'],
                                                    diet_data['Dt_DMIn_ClfLiq'],
                                                    diet_data['Dt_DEIn'],
                                                    equation_selection['Monensin_eqn'])
    return complete_An_data
