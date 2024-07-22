# import nasem_dairy.nasem_equations.infusion as infusion

import numpy as np

import nasem_dairy.model.utilities as ration_funcs

def calculate_Inf_TPIn(Inf_CPIn: float, Inf_NPNCPIn: float) -> float:
    Inf_TPIn = Inf_CPIn - Inf_NPNCPIn  # Line 848
    return Inf_TPIn


def calculate_Inf_OMIn(Inf_DMIn: float, Inf_AshIn: float) -> float:
    Inf_OMIn = Inf_DMIn - Inf_AshIn  # Line 853
    return Inf_OMIn


def calculate_Inf_Rum(Inf_Location: str) -> int:
    if Inf_Location == "Rumen": # Line 874
        Inf_Rum = 1
        return Inf_Rum
    Inf_Rum = 0
    return Inf_Rum


def calculate_Inf_SI(Inf_Location: str) -> int:
    if Inf_Location in ["Abomasum", "Duodenum", "Duodenal"]: # Line 875
        Inf_SI = 1
        return Inf_SI
    Inf_SI = 0 
    return Inf_SI


def calculate_Inf_Art(Inf_Location: str) -> int:
    if Inf_Location in ["Jugular", "Arterial", "Iliac Artery", "Blood"]:
        Inf_Art = 1 # Line 876
        return Inf_Art
    else:
        Inf_Art = 0
        return Inf_Art 


def calculate_InfRum_TPIn(InfRum_CPIn: float, InfRum_NPNCPIn: float) -> float:
    InfRum_TPIn = InfRum_CPIn - InfRum_NPNCPIn  # Line 884
    return InfRum_TPIn


def calculate_InfSI_TPIn(InfSI_CPIn: float, InfSI_NPNCPIn: float) -> float:
    InfSI_TPIn = InfSI_CPIn - InfSI_NPNCPIn
    return InfSI_TPIn


def calculate_InfRum_RUPIn(InfRum_CPAIn: float, 
                           InfRum_CPBIn: float, 
                           InfRum_CPCIn: float,
                           InfRum_NPNCPIn: float, 
                           Inf_KdCPB: float, 
                           coeff_dict: dict
) -> float:
    req_coeff = ['fCPAdu', 'KpConc']
    ration_funcs.check_coeffs_in_coeff_dict(coeff_dict, req_coeff)
    InfRum_RUPIn = ((InfRum_CPAIn - InfRum_NPNCPIn) * coeff_dict['fCPAdu'] + 
                    InfRum_CPBIn * coeff_dict['KpConc'] / 
                    (Inf_KdCPB + coeff_dict['KpConc']) + InfRum_CPCIn) # Line 1084
    return InfRum_RUPIn


def calculate_InfRum_RUP_CP(InfRum_CPIn: float, InfRum_RUPIn: float) -> float:
    if InfRum_CPIn == 0:
        InfRum_RUP_CP = 0
    else:
        InfRum_RUP_CP = InfRum_RUPIn / InfRum_CPIn * 100  # Line 1088
    return InfRum_RUP_CP


def calculate_InfRum_idRUPIn(InfRum_RUPIn: float, Inf_dcRUP: float) -> float:
    InfRum_idRUPIn = InfRum_RUPIn * Inf_dcRUP / 100  # RUP, Line 1089
    return InfRum_idRUPIn


def calculate_InfSI_idTPIn(InfSI_TPIn: float, Inf_dcRUP: float) -> float:
    InfSI_idTPIn = InfSI_TPIn * Inf_dcRUP / 100 # intestinally infused, Line 1090
    return InfSI_idTPIn


def calculate_InfSI_idCPIn(InfSI_idTPIn: float, 
                           InfSI_NPNCPIn: float, 
                           coeff_dict: dict
) -> float:
    req_coeff = ['dcNPNCP']
    ration_funcs.check_coeffs_in_coeff_dict(coeff_dict, req_coeff)
    # SI infused idTP + urea or ammonia, Line 1092
    InfSI_idCPIn = InfSI_idTPIn + InfSI_NPNCPIn * coeff_dict['dcNPNCP'] / 100
    return InfSI_idCPIn


def calculate_Inf_idCPIn(InfRum_idRUPIn: float, InfSI_idCPIn: float) -> float:
    # RUP + intestinally infused, Line 1093
    Inf_idCPIn = InfRum_idRUPIn + InfSI_idCPIn
    return Inf_idCPIn


def calculate_InfRum_RDPIn(InfRum_CPIn: float, InfRum_RUPIn: float) -> float:
    InfRum_RDPIn = InfRum_CPIn - InfRum_RUPIn  # Line 1105
    return InfRum_RDPIn


def calculate_Inf_DigFAIn(Inf_FAIn: float, coeff_dict: dict) -> float:
    req_coeff = ['TT_dcFA_Base']
    ration_funcs.check_coeffs_in_coeff_dict(coeff_dict, req_coeff)
    # Line 1306, used dcFA which is similar to oil, but should define for each infusate
    Inf_DigFAIn = Inf_FAIn * coeff_dict['TT_dcFA_Base']
    return Inf_DigFAIn


def calculate_Inf_DEAcetIn(Inf_AcetIn: float, coeff_dict: dict) -> float:
    req_coeffs = ['En_Acet']
    ration_funcs.check_coeffs_in_coeff_dict(coeff_dict, req_coeffs)
    Inf_DEAcetIn = Inf_AcetIn * coeff_dict['En_Acet']
    return Inf_DEAcetIn


def calculate_Inf_DEPropIn(Inf_PropIn: float, coeff_dict: dict) -> float:
    req_coeff = ['En_Prop']
    ration_funcs.check_coeffs_in_coeff_dict(coeff_dict, req_coeff)
    Inf_DEPropIn = Inf_PropIn * coeff_dict['En_Prop']  # Line 1363
    return Inf_DEPropIn


def calculate_Inf_DEButrIn(Inf_ButrIn: float, coeff_dict: dict) -> float:
    req_coeff = ['En_Butr']
    ration_funcs.check_coeffs_in_coeff_dict(coeff_dict, req_coeff)
    Inf_DEButrIn = Inf_ButrIn * coeff_dict['En_Butr']
    return Inf_DEButrIn


def calculate_XIn(infusion_data: dict, variables: list) -> dict:
    # Line 838-857
    # Inf_NPNCP_g is expressed as g CP/d and should only be urea and Amm
    for name in variables:
        infusion_data[f"{name}In"] = infusion_data[f"{name}_g"] / 1000
    return infusion_data


def calculate_CPXIn(infusion_data: dict, variables: list) -> dict:
    for name in variables:
        infusion_data[f"{name}In"] = (infusion_data['Inf_CP_g'] / 1000 * 
                                      infusion_data[f"{name}Rum_CP"] / 100)
    return infusion_data


def calculate_DMXIn(infusion_data: dict, 
                    variables: list, 
                    Dt_DMIn: float
) -> dict:
    # Line 860-871
    for name in variables:
        infusion_data[f"{name}"] = (infusion_data[f"{name}In"] / 
                                    (Dt_DMIn + infusion_data['Inf_DMIn']) * 100)
    return infusion_data


def calculate_InfRum_X(infusion_data: dict, variables: list) -> dict:
    # Line 880-897
    for name in variables:
        infusion_data[f"InfRum_{name}In"] = (infusion_data['Inf_Rum'] * 
                                             infusion_data[f"Inf_{name}In"])         
    return infusion_data


def calculate_InfSI_X(infusion_data: dict, variables: list) -> dict:
    # Line 900-914
    for name in variables:
        infusion_data[f"InfSI_{name}In"] = (infusion_data['Inf_SI'] * 
                                            infusion_data[f"Inf_{name}In"])
    return infusion_data


def calculate_InfArt_X(infusion_data: dict, variables: list) -> dict:
    # Line 917-931
    for name in variables:
        infusion_data[f"InfArt_{name}In"] = (infusion_data['Inf_Art'] * 
                                             infusion_data[f"Inf_{name}In"])
    return infusion_data


def calculate_Inf_IdAARUPIn(infusion_data: dict, AA_list: list) -> dict:
    # Line 1561-1570
    for AA in AA_list:
        infusion_data[f"Inf_{AA}RUPIn"] = (infusion_data['Inf_Rum'] * 
                                           infusion_data[f"Inf_{AA}_g"] * 
                                           infusion_data['InfRum_RUP_CP'] / 100) 
    return infusion_data


def calculate_Inf_IdAAIn(infusion_data: dict, AA_list: list) -> dict:
    # Line 1678-1687
    for AA in AA_list:
        infusion_data[f"Inf_Id{AA}In"] = ((infusion_data[f"Inf_{AA}_g"] * 
                                           infusion_data['Inf_SI'] + 
                                           infusion_data[f"Inf_{AA}RUPIn"]) * 
                                           infusion_data['Inf_dcRUP'] / 100) 
    return infusion_data


def calculate_infusion_data(infusion_input: dict, 
                            Dt_DMIn: float, 
                            coeff_dict: dict
) -> dict:
    '''
    Infusion input is a dictionary
    '''
    # Calculate all infusion values "Inf_" and store in a dictionary
    infusion_data = infusion_input.copy()
    infused_nutrient_list = [
        'Inf_DM', 'Inf_St', 'Inf_NDF', 'Inf_ADF', 'Inf_Glc', 'Inf_CP',
        'Inf_NPNCP', 'Inf_FA', 'Inf_Ash', 'Inf_VFA', 'Inf_Acet', 'Inf_Prop',
        'Inf_Butr'
    ]
    infusion_data = calculate_XIn(infusion_data, infused_nutrient_list)

    infused_CP_fraction = ['Inf_CPA', 'Inf_CPB', 'Inf_CPC']
    infusion_data = calculate_CPXIn(infusion_data, infused_CP_fraction)

    infusion_data['Inf_TPIn'] = calculate_Inf_TPIn(infusion_data['Inf_CPIn'],
                                                   infusion_data['Inf_NPNCPIn'])
    infusion_data['Inf_OMIn'] = calculate_Inf_OMIn(infusion_data['Inf_DMIn'],
                                                   infusion_data['Inf_AshIn'])
    infused_DM_list = [
        'Inf_DM', 'Inf_OM', 'Inf_St', 'Inf_NDF', 'Inf_ADF', 'Inf_Glc', 'Inf_CP',
        'Inf_FA', 'Inf_VFA', 'Inf_Acet', 'Inf_Prop', 'Inf_Butr'
    ]
    infusion_data = calculate_DMXIn(infusion_data, infused_DM_list, Dt_DMIn)

    infusion_data['Inf_Rum'] = calculate_Inf_Rum(infusion_input['Inf_Location'])
    infusion_data['Inf_SI'] = calculate_Inf_SI(infusion_input['Inf_Location'])
    infusion_data['Inf_Art'] = calculate_Inf_Art(infusion_input['Inf_Location'])

    infused_Rum = [
        'DM', 'OM', 'CP', 'NPNCP', 'CPA', 'CPB', 'CPC', 'St', 'NDF', 'ADF',
        'FA', 'Glc', 'VFA', 'Acet', 'Prop', 'Butr', 'Ash'
    ]
    infusion_data = calculate_InfRum_X(infusion_data, infused_Rum)  

    infusion_data['InfRum_TPIn'] = calculate_InfRum_TPIn(
        infusion_data['InfRum_CPIn'], infusion_data['InfRum_NPNCPIn'])
    infused_SI = [
        'DM', 'OM', 'CP', 'NPNCP', 'St', 'Glc', 'NDF', 'ADF', 'FA', 'VFA',
        'Acet', 'Prop', 'Butr', 'Ash'
    ]
    infusion_data = calculate_InfSI_X(infusion_data, infused_SI)

    infusion_data['InfSI_TPIn'] = calculate_InfSI_TPIn(
        infusion_data['InfSI_CPIn'], infusion_data['InfSI_NPNCPIn'])
    infused_Art = [
        'DM', 'OM', 'CP', 'NPNCP', 'TP', 'St', 'Glc', 'NDF', 'ADF', 'FA', 'VFA',
        'Acet', 'Prop', 'Butr', 'Ash'
    ]
    infusion_data = calculate_InfArt_X(infusion_data, infused_Art)

    # RUP does not include CP infused into the SI
    # In general, CPB for infused proteins, which are generally soluble, has been set to 0.
    # Abo/Duod infusions only considered at absorption.
    infusion_data['InfRum_RUPIn'] = calculate_InfRum_RUPIn(
        infusion_data['InfRum_CPAIn'], infusion_data['InfRum_CPBIn'],
        infusion_data['InfRum_CPCIn'], infusion_data['InfRum_NPNCPIn'],
        infusion_input['Inf_KdCPB'], coeff_dict)
    infusion_data['InfRum_RUP_CP'] = calculate_InfRum_RUP_CP(
        infusion_data['InfRum_CPIn'], infusion_data['InfRum_RUPIn'])
    infusion_data['InfRum_idRUPIn'] = calculate_InfRum_idRUPIn(
        infusion_data['InfRum_RUPIn'], infusion_input['Inf_dcRUP'])
    infusion_data['InfSI_idTPIn'] = calculate_InfSI_idTPIn(
        infusion_data['InfSI_TPIn'], infusion_input['Inf_dcRUP'])
    infusion_data['InfSI_idCPIn'] = calculate_InfSI_idCPIn(
        infusion_data['InfSI_idTPIn'], infusion_data['InfSI_NPNCPIn'],
        coeff_dict)
    infusion_data['Inf_idCPIn'] = calculate_Inf_idCPIn(
        infusion_data['InfRum_idRUPIn'], infusion_data['InfSI_idCPIn'])
    infusion_data['InfRum_RDPIn'] = calculate_InfRum_RDPIn(
        infusion_data['InfRum_CPIn'], infusion_data['InfRum_RUPIn'])
    # Infused individual FA should be calculated here if they are to be considered.  
    # Requires a change to the infusion table. MDH
    infusion_data['Inf_DigFAIn'] = calculate_Inf_DigFAIn(
        infusion_data['Inf_FAIn'], coeff_dict)
    infusion_data['Inf_DEAcetIn'] = calculate_Inf_DEAcetIn(
        infusion_data['Inf_AcetIn'], coeff_dict)
    infusion_data['Inf_DEPropIn'] = calculate_Inf_DEPropIn(
        infusion_data['Inf_PropIn'], coeff_dict)
    infusion_data['Inf_DEButrIn'] = calculate_Inf_DEButrIn(
        infusion_data['Inf_ButrIn'], coeff_dict)

    infusion_AA = [
        'Arg', 'His', 'Ile', 'Leu', 'Lys', 'Met', 'Phe', 'Thr', 'Trp', 'Val'
    ]
    infusion_data = calculate_Inf_IdAARUPIn(infusion_data, infusion_AA)
    infusion_data = calculate_Inf_IdAAIn(infusion_data, infusion_AA)
    infusion_data['Inf_ttdcSt'] = infusion_input['Inf_ttdcSt']
    return infusion_data
