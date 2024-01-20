# dev_infusion_equations
import numpy as np
from nasem_dairy.ration_balancer.ration_balancer_functions import check_coeffs_in_coeff_dict


def calculate_Inf_TPIn(Inf_CPIn, Inf_NPNCPIn):
    Inf_TPIn = Inf_CPIn - Inf_NPNCPIn    # Line 848
    return Inf_TPIn


def calculate_Inf_OMIn(Inf_DMIn, Inf_AshIn):
    Inf_OMIn = Inf_DMIn - Inf_AshIn     # Line 853
    return Inf_OMIn


def calculate_Inf_Rum(Inf_Location):
    Inf_Rum = np.where(Inf_Location == "Rumen", 1, 0)   # Line 874
    return Inf_Rum


def calculate_Inf_SI(Inf_Location):
    condition = (Inf_Location == "Abomasum") | (
        Inf_Location == "Duodenum") | (Inf_Location == "Duodenal")
    Inf_SI = np.where(condition, 1, 0)      # Line 875
    return Inf_SI


def calculate_Inf_Art(Inf_Location):
    condition = (Inf_Location == "Jugular") | (Inf_Location == "Arterial") | (
        Inf_Location == "Iliac Artery") | (Inf_Location == "Blood")
    Inf_Art = np.where(condition, 1, 0)     # Line 876
    return Inf_Art


def calculate_InfRum_TPIn(InfRum_CPIn, InfRum_NPNCPIn):
    InfRum_TPIn = InfRum_CPIn - InfRum_NPNCPIn  # Line 884
    return InfRum_TPIn


def calculate_InfSI_TPIn(InfSI_CPIn, InfSI_NPNCPIn):
    InfSI_TPIn = InfSI_CPIn - InfSI_NPNCPIn
    return InfSI_TPIn


def calculate_InfRum_RUPIn(InfRum_CPAIn, InfRum_CPBIn, InfRum_CPCIn, InfRum_NPNCPIn, Inf_KdCPB, coeff_dict):
    req_coeff = ['fCPAdu', 'KpConc']
    check_coeffs_in_coeff_dict(coeff_dict, req_coeff)
    InfRum_RUPIn = (InfRum_CPAIn - InfRum_NPNCPIn) * coeff_dict['fCPAdu'] + InfRum_CPBIn * coeff_dict['KpConc'] / (
        Inf_KdCPB + coeff_dict['KpConc']) + InfRum_CPCIn     # Line 1084
    return InfRum_RUPIn


def calculate_InfRum_RUP_CP(InfRum_CPIn, InfRum_RUPIn):
    if InfRum_CPIn == 0:
        InfRum_RUP_CP = 0
    else:
        InfRum_RUP_CP = InfRum_RUPIn / InfRum_CPIn * 100    # Line 1088
    return InfRum_RUP_CP


def calculate_InfRum_idRUPIn(InfRum_RUPIn, Inf_dcRUP):
    InfRum_idRUPIn = InfRum_RUPIn * Inf_dcRUP / 100  # RUP, Line 1089
    return InfRum_idRUPIn


def calculate_InfSI_idTPIn(InfSI_TPIn, Inf_dcRUP):
    InfSI_idTPIn = InfSI_TPIn * Inf_dcRUP / 100  # intestinally infused, Line 1090
    return InfSI_idTPIn


def calculate_InfSI_idCPIn(InfSI_idTPIn, InfSI_NPNCPIn, coeff_dict):
    req_coeff = ['dcNPNCP']
    check_coeffs_in_coeff_dict(coeff_dict, req_coeff)
    # SI infused idTP + urea or ammonia, Line 1092
    InfSI_idCPIn = InfSI_idTPIn + InfSI_NPNCPIn * coeff_dict['dcNPNCP'] / 100
    return InfSI_idCPIn


def calculate_Inf_idCPIn(InfRum_idRUPIn, InfSI_idCPIn):
    # RUP + intestinally infused, Line 1093
    Inf_idCPIn = InfRum_idRUPIn + InfSI_idCPIn
    return Inf_idCPIn


def calculate_InfRum_RDPIn(InfRum_CPIn, InfRum_RUPIn):
    InfRum_RDPIn = InfRum_CPIn - InfRum_RUPIn   # Line 1105
    return InfRum_RDPIn


def calculate_Inf_DigFAIn(Inf_FAIn, coeff_dict):
    req_coeff = ['TT_dcFA_Base']
    check_coeffs_in_coeff_dict(coeff_dict, req_coeff)
    # Line 1306, used dcFA which is similar to oil, but should define for each infusate
    Inf_DigFAIn = Inf_FAIn * coeff_dict['TT_dcFA_Base']
    return Inf_DigFAIn


def calculate_Inf_DEAcetIn(Inf_AcetIn, coeff_dict):
    req_coeffs = ['En_Acet']
    check_coeffs_in_coeff_dict(coeff_dict, req_coeffs)
    Inf_DEAcetIn = Inf_AcetIn * coeff_dict['En_Acet']
    return Inf_DEAcetIn


def calculate_Inf_DEPropIn(Inf_PropIn, coeff_dict):
    req_coeff = ['En_Prop']
    check_coeffs_in_coeff_dict(coeff_dict, req_coeff)
    Inf_DEPropIn = Inf_PropIn * coeff_dict['En_Prop']      # Line 1363
    return Inf_DEPropIn


def calculate_Inf_DEButrIn(Inf_ButrIn, coeff_dict):
    req_coeff = ['En_Butr']
    check_coeffs_in_coeff_dict(coeff_dict, req_coeff)
    Inf_DEButrIn = Inf_ButrIn * coeff_dict['En_Butr']
    return Inf_DEButrIn


def calculate_infusion_data(infusion_input, Dt_DMIn, coeff_dict):
    '''
    Infusion input is a dictionary
    '''
    # Calculate all infusion values "Inf_" and store in a dictionary
    infusion_data = {}
    infused_nutrient_list = ['Inf_DM',
                             'Inf_St',
                             'Inf_NDF',
                             'Inf_ADF',
                             'Inf_Glc',
                             'Inf_CP',
                             'Inf_NPNCP',
                             'Inf_FA',
                             'Inf_Ash',
                             'Inf_VFA',
                             'Inf_Acet',
                             'Inf_Prop',
                             'Inf_Butr']
    for name in infused_nutrient_list:
        infusion_data[f"{name}In"] = infusion_input[f"{name}_g"] / 1000
    # Line 838-857
    # Inf_NPNCP_g is expressed as g CP/d and should only be urea and Amm

    infused_CP_fraction = ['Inf_CPA',
                           'Inf_CPB',
                           'Inf_CPC']
    for name in infused_CP_fraction:
        infusion_data[f"{name}In"] = infusion_input['Inf_CP_g'] / \
            1000 * infusion_input[f"{name}Rum_CP"] / 100

    infusion_data['Inf_TPIn'] = calculate_Inf_TPIn(infusion_data['Inf_CPIn'],
                                                   infusion_data['Inf_NPNCPIn'])
    infusion_data['Inf_OMIn'] = calculate_Inf_OMIn(infusion_data['Inf_DMIn'],
                                                   infusion_data['Inf_AshIn'])
    infused_DM_list = [
        'Inf_DM',
        'Inf_OM',
        'Inf_St',
        'Inf_NDF',
        'Inf_ADF',
        'Inf_Glc',
        'Inf_CP',
        'Inf_FA',
        'Inf_VFA',
        'Inf_Acet',
        'Inf_Prop',
        'Inf_Butr']
    for name in infused_DM_list:
        infusion_data[f"{name}"] = infusion_data[f"{name}In"] / \
            (Dt_DMIn + infusion_data['Inf_DMIn']) * 100
    # Line 860-871

    infusion_data['Inf_Rum'] = calculate_Inf_Rum(infusion_input['Inf_Location'])
    infusion_data['Inf_SI'] = calculate_Inf_SI(infusion_input['Inf_Location'])
    infusion_data['Inf_Art'] = calculate_Inf_Art(
        infusion_input['Inf_Location'])

    infused_Rum = ['DM',
                   'OM',
                   'CP',
                   'NPNCP',
                   'CPA',
                   'CPB',
                   'CPC',
                   'St',
                   'NDF',
                   'ADF',
                   'FA',
                   'Glc',
                   'VFA',
                   'Acet',
                   'Prop',
                   'Butr',
                   'Ash']
    for name in infused_Rum:
        infusion_data[f"InfRum_{name}In"] = infusion_data['Inf_Rum'] * \
            infusion_data[f"Inf_{name}In"]   # Line 880-897

    infusion_data['InfRum_TPIn'] = calculate_InfRum_TPIn(infusion_data['InfRum_CPIn'],
                                                         infusion_data['InfRum_NPNCPIn'])
    infused_SI = ['DM',
                  'OM',
                  'CP',
                  'NPNCP',
                  'St',
                  'Glc',
                  'NDF',
                  'ADF',
                  'FA',
                  'VFA',
                  'Acet',
                  'Prop',
                  'Butr',
                  'Ash']
    for name in infused_SI:
        infusion_data[f"InfSI_{name}In"] = infusion_data['Inf_SI'] * \
            infusion_data[f"Inf_{name}In"]  # Line 900-914

    infusion_data['InfSI_TPIn'] = calculate_InfSI_TPIn(infusion_data['InfSI_CPIn'],
                                                       infusion_data['InfSI_NPNCPIn'])
    infused_Art = ['DM',
                   'OM',
                   'CP',
                   'NPNCP',
                   'TP',
                   'St',
                   'Glc',
                   'NDF',
                   'ADF',
                   'FA',
                   'VFA',
                   'Acet',
                   'Prop',
                   'Butr',
                   'Ash']
    for name in infused_Art:
        infusion_data[f"InfArt_{name}In"] = infusion_data['Inf_Art'] + \
            infusion_data[f"Inf_{name}In"]   # Line 917-931

    # RUP does not include CP infused into the SI
        # In general, CPB for infused proteins, which are generally soluble, has been set to 0.
        # Abo/Duod infusions only considered at absorption.
    infusion_data['InfRum_RUPIn'] = calculate_InfRum_RUPIn(infusion_data['InfRum_CPAIn'],
                                                           infusion_data['InfRum_CPBIn'],
                                                           infusion_data['InfRum_CPCIn'],
                                                           infusion_data['InfRum_NPNCPIn'],
                                                           infusion_input['Inf_KdCPB'],
                                                           coeff_dict)
    infusion_data['InfRum_RUP_CP'] = calculate_InfRum_RUP_CP(infusion_data['InfRum_CPIn'],
                                                             infusion_data['InfRum_RUPIn'])
    infusion_data['InfRum_idRUPIn'] = calculate_InfRum_idRUPIn(infusion_data['InfRum_RUPIn'],
                                                               infusion_input['Inf_dcRUP'])
    infusion_data['InfSI_idTPIn'] = calculate_InfSI_idTPIn(infusion_data['InfSI_TPIn'],
                                                           infusion_input['Inf_dcRUP'])
    infusion_data['InfSI_idCPIn'] = calculate_InfSI_idCPIn(infusion_data['InfSI_idTPIn'],
                                                           infusion_data['InfSI_NPNCPIn'],
                                                           coeff_dict)
    infusion_data['Inf_idCPIn'] = calculate_Inf_idCPIn(infusion_data['InfRum_idRUPIn'],
                                                       infusion_data['InfSI_idCPIn'])
    infusion_data['InfRum_RDPIn'] = calculate_InfRum_RDPIn(infusion_data['InfRum_CPIn'],
                                                           infusion_data['InfRum_RUPIn'])
    # Infused individual FA should be calculated here if they are to be considered.  Requires a change to the infusion table. MDH
    infusion_data['Inf_DigFAIn'] = calculate_Inf_DigFAIn(infusion_data['Inf_FAIn'],
                                                         coeff_dict)
    infusion_data['Inf_DEAcetIn'] = calculate_Inf_DEAcetIn(infusion_data['Inf_AcetIn'],
                                                           coeff_dict)
    infusion_data['Inf_DEPropIn'] = calculate_Inf_DEPropIn(infusion_data['Inf_PropIn'],
                                                           coeff_dict)
    infusion_data['Inf_DEButrIn'] = calculate_Inf_DEButrIn(infusion_data['Inf_ButrIn'],
                                                           coeff_dict)

    infusion_AA = ['Arg',
                   'His',
                   'Ile',
                   'Leu',
                   'Lys',
                   'Met',
                   'Phe',
                   'Thr',
                   'Trp',
                   'Val']
    for AA in infusion_AA:
        infusion_data[f"Inf_{AA}RUPIn"] = infusion_data['Inf_Rum'] * \
            infusion_input[f"Inf_{AA}_g"] * \
            infusion_data['InfRum_RUP_CP'] / 100   # Line 1561-1570
        infusion_data[f"Inf_Id{AA}In"] = (infusion_input[f"Inf_{AA}_g"] * infusion_data['Inf_SI'] +
                                          infusion_data[f"Inf_{AA}RUPIn"]) * infusion_input['Inf_dcRUP'] / 100    # Line 1678-1687

    infusion_data['Inf_ttdcSt'] = infusion_input['Inf_ttdcSt']

    return infusion_data
