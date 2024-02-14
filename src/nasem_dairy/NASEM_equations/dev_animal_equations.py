# dev_animal_equations
import numpy as np
from nasem_dairy.ration_balancer.ration_balancer_functions import check_coeffs_in_coeff_dict

####################
# Functions for Animal Level Intakes in Wrappers
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
    An_DENDFIn = An_DigNDFIn * coeff_dict['En_NDF']                   # Line 1353
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


def calculate_An_DigNDF(An_DigNDFIn, Dt_DMIn, InfRum_DMIn, InfSI_DMIn):
    # Line 1066, should add LI infusions
    An_DigNDF = An_DigNDFIn / (Dt_DMIn + InfRum_DMIn + InfSI_DMIn) * 100
    return An_DigNDF


def calculate_An_GEIn(Dt_GEIn, Inf_NDFIn, Inf_StIn, Inf_FAIn, Inf_TPIn, Inf_NPNCPIn, Inf_AcetIn, Inf_PropIn, Inf_ButrIn, coeff_dict):
    req_coeff = ['En_NDF', 'En_St', 'En_FA', 'En_CP',
                 'En_NPNCP', 'En_Acet', 'En_Prop', 'En_Butr']
    check_coeffs_in_coeff_dict(coeff_dict, req_coeff)
    An_GEIn = Dt_GEIn + Inf_NDFIn * coeff_dict['En_NDF'] + Inf_StIn * coeff_dict['En_St'] \
        + Inf_FAIn * coeff_dict['En_FA'] + Inf_TPIn * coeff_dict['En_CP'] \
        + Inf_NPNCPIn * coeff_dict['En_NPNCP'] + Inf_AcetIn * coeff_dict['En_Acet'] \
        + Inf_PropIn * coeff_dict['En_Prop'] + \
        Inf_ButrIn * coeff_dict['En_Butr']
    return An_GEIn


def calculate_An_GasEOut_Dry(Dt_DMIn, Dt_FAIn, InfRum_FAIn, InfRum_DMIn, An_GEIn):
    An_GasEOut_Dry = 0.69 + 0.053 * An_GEIn - 0.07 * \
        (Dt_FAIn + InfRum_FAIn) / (Dt_DMIn + InfRum_DMIn) * 100   # Line 1407, Dry Cows
    return An_GasEOut_Dry


def calculate_An_GasEOut_Lact(Dt_DMIn, Dt_FAIn, InfRum_FAIn, InfRum_DMIn, An_DigNDF):
    An_GasEOut_Lact = (0.294 * (Dt_DMIn + InfRum_DMIn) -      # Line 1404-1405
                       (0.347 * (Dt_FAIn + InfRum_FAIn) / (Dt_DMIn + InfRum_DMIn)) * 100 +
                       0.0409 * An_DigNDF)
    return An_GasEOut_Lact


def calculate_An_GasEOut_Heif(An_GEIn, An_NDF):
    An_GasEOut_Heif = -0.038 + 0.051 * An_GEIn + 0.0091 * An_NDF   # Line 1406, Heifers/Bulls
    return An_GasEOut_Heif


def calculate_An_GasEOut(An_StatePhys, Monensin_eqn, An_GasEOut_Dry, An_GasEOut_Lact, An_GasEOut_Heif):
    if An_StatePhys == 'Dry Cow':
        An_GasEOut = An_GasEOut_Dry
    elif An_StatePhys == 'Calf':
        An_GasEOut = 0  # Line 1408, An_GasEOut_Clf = 0
    elif An_StatePhys == 'Lactating Cow':
        An_GasEOut = An_GasEOut_Lact
    else:
        An_GasEOut = An_GasEOut_Heif

    if Monensin_eqn == 1:
        An_GasEOut = An_GasEOut * 0.95
    else:
        An_GasEOut = An_GasEOut

    return An_GasEOut


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
    An_DENPNCPIn = Dt_NPNCPIn * coeff_dict['dcNPNCP'] / 100 * coeff_dict['En_NPNCP']
    return An_DENPNCPIn


def calculate_An_DETPIn(An_DECPIn, An_DENPNCPIn, coeff_dict):
    req_coeff = ['En_NPNCP', 'En_CP']
    check_coeffs_in_coeff_dict(coeff_dict, req_coeff)
    # Line 1355, Caution! DigTPaIn not clean so subtracted DE for CP equiv of NPN to correct. Not a true DE_TP.
    An_DETPIn = An_DECPIn - An_DENPNCPIn / coeff_dict['En_NPNCP'] * coeff_dict['En_CP']
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


def calculate_An_DEInp(An_DEIn, An_DETPIn, An_DENPNCPIn):
    # Line 1385, Create a nonprotein DEIn for milk protein predictions.
    An_DEInp = An_DEIn - An_DETPIn - An_DENPNCPIn
    return An_DEInp


def calculate_An_GutFill_BW(An_BW, An_BW_mature, An_StatePhys, An_Parity_rl, Dt_DMIn_ClfLiq, Dt_DMIn_ClfStrt, coeff_dict):
    req_coeff = ['An_GutFill_BWmature']
    check_coeffs_in_coeff_dict(coeff_dict, req_coeff)
    An_GutFill_BW = 0.06 # Line 2402, Milk fed calf, kg/kg BW
    if (An_StatePhys == "Calf") and (Dt_DMIn_ClfLiq > 0.01) and (Dt_DMIn_ClfStrt <= 0.01) and (An_BW > 0.16 * An_BW_mature):
        An_GutFill_BW = 0.09       # Line 2403, Heavy milk fed veal calf 
    elif (An_StatePhys == "Calf") and (Dt_DMIn_ClfLiq > 0.01) and (Dt_DMIn_ClfStrt > 0.01):
        An_GutFill_BW = 0.07       # Line 2405, Milk plus starter fed calf
    elif (An_StatePhys == "Calf") and (Dt_DMIn_ClfLiq < 0.01):
        An_GutFill_BW = 0.15       # Line 2407, Weaned calf
    elif ((An_StatePhys=="Dry Cow" or An_StatePhys=="Lactating Cow")) and (An_Parity_rl > 0):
        An_GutFill_BW = coeff_dict['An_GutFill_BWmature'] # Line 2410, cow
    else:
        An_GutFill_BW = An_GutFill_BW  
    return An_GutFill_BW


def calculate_An_BWnp(An_BW, GrUter_Wt):
    '''
    Equation 20-230
    '''
    An_BWnp = An_BW - GrUter_Wt  # Line 2396, Non-pregnant BW
    return An_BWnp


def calculate_An_GutFill_Wt(An_GutFill_BW, An_BWnp):
    An_GutFill_Wt = An_GutFill_BW * An_BWnp # Line 2413
    return An_GutFill_Wt


def calculate_An_BW_empty(An_BW, An_GutFill_Wt):
    '''
    Equation 20-242
    '''
    An_BW_empty = An_BW - An_GutFill_Wt # Line 2414
    return An_BW_empty


def calculate_An_REgain_Calf(Body_Gain_empty, An_BW_empty):
    An_REgain_Calf = Body_Gain_empty**1.10 * An_BW_empty**0.205    # Line 2445, calf RE gain needed here for fat gain, mcal/d    
    return An_REgain_Calf


def calculate_An_MEIn(An_StatePhys, An_BW, An_DEIn, An_GasEOut, Ur_DEout, Dt_DMIn_CflLiq, Dt_DEIn_base_ClfLiq, Dt_DEIn_base_ClfDry, RumDevDisc_Clf):
    condition = (An_StatePhys == "Calf") and (Dt_DMIn_CflLiq > 0.015 * An_BW) and (RumDevDisc_Clf > 0)
    K_DE_ME_ClfDry = np.where(condition,    # Line 2755
                              0.93 * 0.9,
                              0.93)
    An_MEIn = An_DEIn - An_GasEOut - Ur_DEout   # Line 2753
    condition2 = (An_StatePhys == "Calf") and (Dt_DMIn_CflLiq > 0)
    An_MEIn = np.where(condition2,
                       Dt_DEIn_base_ClfLiq * 0.96 + Dt_DEIn_base_ClfDry * K_DE_ME_ClfDry, # Line 2757, no consideration of infusions for calves.
                       An_MEIn)
    return An_MEIn


def calculate_An_NEIn(An_MEIn):
    An_NEIn = An_MEIn * 0.66    # Line 2762
    return An_NEIn


def calculate_An_NE(An_NEIn, An_DMIn):
    An_NE = An_NEIn / An_DMIn   # Line 2763
    return An_NE


def calculate_An_MBW(An_BW: float) -> float:
    """
    An_MBW: Metabolic body weight, kg
    """
    An_MBW = An_BW ** 0.75  # Line 223
    return An_MBW


def calculate_An_TPIn(Dt_TPIn: float, Inf_TPIn: float) -> float:
    """
    Dt_TPIn: Diet true protein intake kg/d
    Inf_TPIn: Infused true protein intake kg/d
    """
    An_TPIn = Dt_TPIn + Inf_TPIn    # Line 952
    return An_TPIn


def calculate_An_DigTPaIn(An_TPIn: float, InfArt_CPIn: float, Fe_CP: float) -> float:
    """
    An_DigTPaIn: Total tract digestable true protein intake kg CP/d
    """
    An_DigTPaIn = An_TPIn - InfArt_CPIn - Fe_CP # Very messy. Some Fe_MiTP derived from NPN and some MiNPN from Dt_TP, thus Fe_CP, Line 1229
    return An_DigTPaIn

####################
# Animal Warpper Functions
####################


def calculate_An_data_initial(animal_input, diet_data, infusion_data, Monensin_eqn, GrUter_Wt, coeff_dict):
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
    An_data['An_DigNDF'] = calculate_An_DigNDF(An_data['An_DigNDFIn'],
                                               animal_input['DMI'],
                                               infusion_data['InfRum_DMIn'],
                                               infusion_data['InfSI_DMIn'])
    An_data['An_GEIn'] = calculate_An_GEIn(diet_data['Dt_GEIn'],
                                           infusion_data['Inf_NDFIn'],
                                           infusion_data['Inf_StIn'],
                                           infusion_data['Inf_FAIn'],
                                           infusion_data['Inf_TPIn'],
                                           infusion_data['Inf_NPNCPIn'],
                                           infusion_data['Inf_AcetIn'],
                                           infusion_data['Inf_PropIn'],
                                           infusion_data['Inf_ButrIn'],
                                           coeff_dict)
    # Next three values are passed to calculate_An_GasEOut which will assign An_GasEOut
    # the correct value
    An_GasEOut_Dry = calculate_An_GasEOut_Dry(animal_input['DMI'],
                                              diet_data['Dt_FAIn'],
                                              infusion_data['InfRum_FAIn'],
                                              infusion_data['InfRum_DMIn'],
                                              An_data['An_GEIn'])
    An_GasEOut_Lact = calculate_An_GasEOut_Lact(animal_input['DMI'],
                                                diet_data['Dt_FAIn'],
                                                infusion_data['InfRum_FAIn'],
                                                infusion_data['InfRum_DMIn'],
                                                An_data['An_DigNDF'])
    An_GasEOut_Heif = calculate_An_GasEOut_Heif(An_data['An_GEIn'],
                                                An_data['An_NDF'])
    An_data['An_GasEOut'] = calculate_An_GasEOut(animal_input['An_StatePhys'],
                                                 Monensin_eqn,
                                                 An_GasEOut_Dry,
                                                 An_GasEOut_Lact,
                                                 An_GasEOut_Heif)
    
    
    An_data['An_GutFill_BW'] = calculate_An_GutFill_BW(animal_input['An_BW'],
                                                       animal_input['An_BW_mature'],
                                                       animal_input['An_StatePhys'],
                                                       animal_input['An_Parity_rl'],
                                                       diet_data['Dt_DMIn_ClfLiq'],
                                                       diet_data['Dt_DMIn_ClfStrt'],
                                                       coeff_dict)
    An_data['An_BWnp'] = calculate_An_BWnp(animal_input['An_BW'],
                                           GrUter_Wt)
    An_data['An_GutFill_Wt'] = calculate_An_GutFill_Wt(An_data['An_GutFill_BW'],
                                                       An_data['An_BWnp'])
    An_data['An_BW_empty'] = calculate_An_BW_empty(animal_input['An_BW'],
                                                   An_data['An_GutFill_Wt'])
    An_data['An_MBW'] = calculate_An_MBW(animal_input['An_BW'])
    return An_data


def calculate_An_data_complete(
        An_data_initial: dict, 
        diet_data: dict, 
        An_StatePhys: str, 
        Fe_CP, 
        infusion_data: dict, 
        Monensin_eqn: int, #equation_selection['Monensin_eqn']
        coeff_dict: dict
        ):
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
                                                    Monensin_eqn)
    complete_An_data['An_DEInp'] = calculate_An_DEInp(complete_An_data['An_DEIn'],
                                                      complete_An_data['An_DETPIn'],
                                                      complete_An_data['An_DENPNCPIn'])
    complete_An_data['An_TPIn'] = calculate_An_TPIn(diet_data['Dt_TPIn'], 
                                                    infusion_data['Inf_TPIn']) 
    complete_An_data['An_DigTPaIn'] = calculate_An_DigTPaIn(complete_An_data['An_TPIn'],
                                                            infusion_data['InfArt_CPIn'],
                                                            Fe_CP)
    AA_list = ['Arg', 'His', 'Ile', 'Leu','Lys', 'Met', 'Phe', 'Thr', 'Trp', 'Val']
    for AA in AA_list:
        complete_An_data[f'An_Id{AA}In'] = diet_data[f'Dt_Id{AA}In'] + infusion_data[f'Inf_Id{AA}In']
    return complete_An_data

####################
# Animal Functions not in Wrapper
####################


def calculate_An_MPIn(Dt_idRUPIn, Du_idMiTP):
    # Line 1236 (Equation 20-136 p. 432 - without infused TP)
    An_MPIn = Dt_idRUPIn + Du_idMiTP
    return An_MPIn


def calculate_An_MPIn_g(An_MPIn):
    An_MPIn_g = An_MPIn * 1000                      # Line 1238
    return An_MPIn_g
