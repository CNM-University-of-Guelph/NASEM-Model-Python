# dev_animal_equations
# import nasem_dairy.NASEM_equations.animal_equations as animal

import numpy as np

import nasem_dairy.ration_balancer.ration_balancer_functions as ration_funcs

####################
# Functions for Animal Level Intakes in Wrappers
####################
# An_DMIn_BW is calculated seperately after DMI selection to use in calculate_diet_data


def calculate_An_DMIn_BW(An_BW, Dt_DMIn):
    An_DMIn_BW = Dt_DMIn / An_BW  # Line 935
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
    # Line 1063, should consider SI and LI infusions as well, but no predictions
    # of LI NDF digestion available.
    An_DigNDFIn = Dt_DigNDFIn + InfRum_NDFIn * TT_dcNDF / 100
    return An_DigNDFIn


def calculate_An_DENDFIn(An_DigNDFIn, coeff_dict):
    req_coeff = ['En_NDF']
    ration_funcs.check_coeffs_in_coeff_dict(coeff_dict, req_coeff)
    An_DENDFIn = An_DigNDFIn * coeff_dict['En_NDF']  # Line 1353
    return An_DENDFIn


def calculate_An_DigStIn(Dt_DigStIn, Inf_StIn, Inf_ttdcSt):
    # Line 1033, Glc considered as WSC and thus with rOM
    An_DigStIn = Dt_DigStIn + Inf_StIn * Inf_ttdcSt / 100
    return An_DigStIn


def calculate_An_DEStIn(An_DigStIn, coeff_dict):
    req_coeff = ['En_St']
    ration_funcs.check_coeffs_in_coeff_dict(coeff_dict, req_coeff)
    An_DEStIn = An_DigStIn * coeff_dict['En_St']  # Line 1351
    return An_DEStIn


def calculate_An_DigrOMaIn(Dt_DigrOMaIn, InfRum_GlcIn, InfRum_AcetIn,
                           InfRum_PropIn, InfRum_ButrIn, InfSI_GlcIn,
                           InfSI_AcetIn, InfSI_PropIn, InfSI_ButrIn):
    An_DigrOMaIn = (Dt_DigrOMaIn + InfRum_GlcIn + InfRum_AcetIn +
                    InfRum_PropIn + InfRum_ButrIn + InfSI_GlcIn + 
                    InfSI_AcetIn + InfSI_PropIn + InfSI_ButrIn) # Line 1023-1024
    return An_DigrOMaIn


def calculate_An_DErOMIn(An_DigrOMaIn, coeff_dict):
    req_coeff = ['En_rOM']
    ration_funcs.check_coeffs_in_coeff_dict(coeff_dict, req_coeff)
    An_DErOMIn = An_DigrOMaIn * coeff_dict['En_rOM']  # Line 1351
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
    An_CPIn = Dt_CPIn + Inf_CPIn  # Line 947
    return An_CPIn


def calculate_An_DigNDF(An_DigNDFIn, Dt_DMIn, InfRum_DMIn, InfSI_DMIn):
    # Line 1066, should add LI infusions
    An_DigNDF = An_DigNDFIn / (Dt_DMIn + InfRum_DMIn + InfSI_DMIn) * 100
    return An_DigNDF


def calculate_An_GEIn(Dt_GEIn, Inf_NDFIn, Inf_StIn, Inf_FAIn, Inf_TPIn,
                      Inf_NPNCPIn, Inf_AcetIn, Inf_PropIn, Inf_ButrIn,
                      coeff_dict):
    req_coeff = [
        'En_NDF', 'En_St', 'En_FA', 'En_CP', 'En_NPNCP', 'En_Acet', 'En_Prop',
        'En_Butr'
    ]
    ration_funcs.check_coeffs_in_coeff_dict(coeff_dict, req_coeff)
    An_GEIn = (Dt_GEIn + Inf_NDFIn * coeff_dict['En_NDF'] + 
               Inf_StIn * coeff_dict['En_St'] +
               Inf_FAIn * coeff_dict['En_FA'] +
               Inf_TPIn * coeff_dict['En_CP'] + 
               Inf_NPNCPIn * coeff_dict['En_NPNCP'] + 
               Inf_AcetIn * coeff_dict['En_Acet'] + 
               Inf_PropIn * coeff_dict['En_Prop'] + 
               Inf_ButrIn * coeff_dict['En_Butr'])
    return An_GEIn


def calculate_An_GasEOut_Dry(Dt_DMIn, Dt_FAIn, InfRum_FAIn, InfRum_DMIn,
                             An_GEIn):
    An_GasEOut_Dry = (0.69 + 0.053 * An_GEIn - 0.07 * (Dt_FAIn + InfRum_FAIn) / 
                      (Dt_DMIn + InfRum_DMIn) * 100)   # Line 1407, Dry Cows
    return An_GasEOut_Dry


def calculate_An_GasEOut_Lact(Dt_DMIn, Dt_FAIn, InfRum_FAIn, InfRum_DMIn,
                              An_DigNDF):
    An_GasEOut_Lact = (0.294 * (Dt_DMIn + InfRum_DMIn) - 
                       (0.347 * (Dt_FAIn + InfRum_FAIn) / 
                        (Dt_DMIn + InfRum_DMIn)) * 100 + 0.0409 * An_DigNDF)
    # Line 1404-1405
    return An_GasEOut_Lact


def calculate_An_GasEOut_Heif(An_GEIn, An_NDF):
    An_GasEOut_Heif = -0.038 + 0.051 * An_GEIn + 0.0091 * An_NDF  
    # Line 1406, Heifers/Bulls
    return An_GasEOut_Heif


def calculate_An_GasEOut(An_StatePhys, Monensin_eqn, An_GasEOut_Dry,
                         An_GasEOut_Lact, An_GasEOut_Heif):
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
    ration_funcs.check_coeffs_in_coeff_dict(coeff_dict, req_coeff)
    An_DECPIn = An_DigCPaIn * coeff_dict['En_CP']
    return An_DECPIn


def calculate_An_DENPNCPIn(Dt_NPNCPIn, coeff_dict):
    req_coeff = ['dcNPNCP', 'En_NPNCP']
    ration_funcs.check_coeffs_in_coeff_dict(coeff_dict, req_coeff)
    An_DENPNCPIn = (Dt_NPNCPIn * coeff_dict['dcNPNCP'] / 
                    100 * coeff_dict['En_NPNCP'])
    return An_DENPNCPIn


def calculate_An_DETPIn(An_DECPIn, An_DENPNCPIn, coeff_dict):
    req_coeff = ['En_NPNCP', 'En_CP']
    ration_funcs.check_coeffs_in_coeff_dict(coeff_dict, req_coeff)
    # Line 1355, Caution! DigTPaIn not clean so subtracted DE for CP equiv of
    # NPN to correct. Not a true DE_TP.
    An_DETPIn = (An_DECPIn - An_DENPNCPIn / 
                 coeff_dict['En_NPNCP'] * coeff_dict['En_CP'])
    return An_DETPIn


def calculate_An_DigFAIn(Dt_DigFAIn, Inf_DigFAIn):
    An_DigFAIn = Dt_DigFAIn + Inf_DigFAIn  # Line 1308
    return An_DigFAIn


def calculate_An_DEFAIn(An_DigFAIn, coeff_dict):
    req_coeff = ['En_FA']
    ration_funcs.check_coeffs_in_coeff_dict(coeff_dict, req_coeff)
    An_DEFAIn = An_DigFAIn * coeff_dict['En_FA']  # Line 1361
    return An_DEFAIn


def calculate_An_DEIn(An_StatePhys, An_DENDFIn, An_DEStIn, An_DErOMIn,
                      An_DETPIn, An_DENPNCPIn, An_DEFAIn, Inf_DEAcetIn,
                      Inf_DEPropIn, Inf_DEButrIn, Dt_DMIn_ClfLiq, Dt_DEIn,
                      Monensin_eqn):
    An_DEIn = (An_DENDFIn + An_DEStIn + An_DErOMIn + An_DETPIn + An_DENPNCPIn +
               An_DEFAIn + Inf_DEAcetIn + Inf_DEPropIn + Inf_DEButrIn)
    # Infusion DE not considered for milk-fed calves
    condition = (An_StatePhys == "Calf") and (Dt_DMIn_ClfLiq > 0)   
    An_DEIn = Dt_DEIn if condition else An_DEIn     
    An_DEIn = An_DEIn * 1.02 if Monensin_eqn == 1 else An_DEIn
    return An_DEIn


def calculate_An_DEInp(An_DEIn, An_DETPIn, An_DENPNCPIn):
    # Line 1385, Create a nonprotein DEIn for milk protein predictions.
    An_DEInp = An_DEIn - An_DETPIn - An_DENPNCPIn
    return An_DEInp


def calculate_An_GutFill_BW(An_BW, An_BW_mature, An_StatePhys, An_Parity_rl,
                            Dt_DMIn_ClfLiq, Dt_DMIn_ClfStrt, coeff_dict):
    """
    see page 34 for comments, gut fill is default 0.18 for cows
    Weaned calf == heifer, which is based on equations 11-1a/b using 85% (inverse of 0.15)
    Comments in book suggest this is not always a suitable assumption (that gut fill is 15% of BW), consider making this a coeff that can be changed in coeff_dict?
    """
    req_coeff = ['An_GutFill_BWmature']
    ration_funcs.check_coeffs_in_coeff_dict(coeff_dict, req_coeff)
    An_GutFill_BW = 0.06  # Line 2402, Milk fed calf, kg/kg BW
    if (
        (An_StatePhys == "Calf") 
        and (Dt_DMIn_ClfLiq > 0.01) 
        and (Dt_DMIn_ClfStrt <= 0.01) 
        and (An_BW > 0.16 * An_BW_mature)
    ):
        An_GutFill_BW = 0.09  # Line 2403, Heavy milk fed veal calf
    elif (
        (An_StatePhys == "Calf") 
        and (Dt_DMIn_ClfLiq > 0.01) 
        and (Dt_DMIn_ClfStrt > 0.01)
    ):
        An_GutFill_BW = 0.07  # Line 2405, Milk plus starter fed calf
    elif (
        (An_StatePhys == "Calf") 
        and (Dt_DMIn_ClfLiq < 0.01)
    ):
        An_GutFill_BW = 0.15  # Line 2407, Weaned calf
    elif (
        (An_StatePhys == "Dry Cow" 
         or An_StatePhys == "Lactating Cow")
         and (An_Parity_rl > 0)
    ):
        An_GutFill_BW = coeff_dict['An_GutFill_BWmature']  # Line 2410, cow
    elif An_StatePhys == "Heifer":
        An_GutFill_BW = 0.15    # Line 2408 
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
    An_GutFill_Wt = An_GutFill_BW * An_BWnp  # Line 2413
    return An_GutFill_Wt


def calculate_An_BW_empty(An_BW, An_GutFill_Wt):
    '''
    Equation 20-242
    '''
    An_BW_empty = An_BW - An_GutFill_Wt  # Line 2414
    return An_BW_empty


def calculate_An_REgain_Calf(Body_Gain_empty, An_BW_empty):
    An_REgain_Calf = Body_Gain_empty**1.10 * An_BW_empty**0.205  
    # Line 2445, calf RE gain needed here for fat gain, mcal/d
    return An_REgain_Calf


def calculate_An_MEIn_approx(An_DEInp: float, An_DENPNCPIn: float,
                             An_DigTPaIn: float, Body_NPgain: float,
                             An_GasEOut: float, coeff_dict: dict
) -> float:
    """
    An_MEIn_approx: Approximate ME intake, see note:
        Adjust heifer MPuse target if the MP:ME ratio is below optimum for development.
        Can't calculate ME before MP, thus estimated ME in the MP:ME ratio using the target NPgain. Will be incorrect
        if the animal is lactating or gestating.
    This is used by Equation 11-11
    """
    An_MEIn_approx = (An_DEInp + An_DENPNCPIn + (An_DigTPaIn - Body_NPgain) * 4.0 
                      + Body_NPgain * coeff_dict['En_CP'] - An_GasEOut)
    # Line 2685
    return An_MEIn_approx


def calculate_An_MEIn(An_StatePhys, An_BW, An_DEIn, An_GasEOut, Ur_DEout,
                      Dt_DMIn_CflLiq, Dt_DEIn_base_ClfLiq, Dt_DEIn_base_ClfDry,
                      RumDevDisc_Clf):
    condition = ((An_StatePhys == "Calf") 
                 and (Dt_DMIn_CflLiq > 0.015 * An_BW) 
                 and (RumDevDisc_Clf > 0))
    K_DE_ME_ClfDry = 0.93 * 0.9 if condition else 0.93 # Line 2755   
    
    An_MEIn = An_DEIn - An_GasEOut - Ur_DEout  # Line 2753
    An_MEIn = (Dt_DEIn_base_ClfLiq * 0.96 + Dt_DEIn_base_ClfDry * K_DE_ME_ClfDry
               if (An_StatePhys == "Calf") and (Dt_DMIn_CflLiq > 0) 
               else An_MEIn) 
    return An_MEIn


def calculate_An_NEIn(An_MEIn):
    An_NEIn = An_MEIn * 0.66  # Line 2762
    return An_NEIn


def calculate_An_NE(An_NEIn, An_DMIn):
    An_NE = An_NEIn / An_DMIn  # Line 2763
    return An_NE


def calculate_An_MBW(An_BW: float) -> float:
    """
    An_MBW: Metabolic body weight, kg
    """
    An_MBW = An_BW**0.75  # Line 223
    return An_MBW


def calculate_An_TPIn(Dt_TPIn: float, Inf_TPIn: float) -> float:
    """
    Dt_TPIn: Diet true protein intake kg/d
    Inf_TPIn: Infused true protein intake kg/d
    """
    An_TPIn = Dt_TPIn + Inf_TPIn  # Line 952
    return An_TPIn


def calculate_An_DigTPaIn(An_TPIn: float, 
                          InfArt_CPIn: float,
                          Fe_CP: float
) -> float:
    """
    An_DigTPaIn: Total tract digestable true protein intake kg CP/d
    """
    An_DigTPaIn = An_TPIn - InfArt_CPIn - Fe_CP  
    # Very messy. Some Fe_MiTP derived from NPN and some MiNPN from Dt_TP, 
    # thus Fe_CP, Line 1229
    return An_DigTPaIn


def calculate_An_DMIn_MBW(An_DMIn: float, An_MBW: float) -> float:
    """
    An_DMIn_MBW: kg Dry matter intake per kg metabolic body weight, kg/kg
    """
    An_DMIn_MBW = An_DMIn / An_MBW  # Line 936
    return An_DMIn_MBW


def calculate_An_StIn(Dt_StIn: float, 
                      InfRum_StIn: float,
                      InfSI_StIn: float
) -> float:
    """
    An_StIn: Dietary + infused starch intake, kg
    """
    An_StIn = Dt_StIn + InfRum_StIn + InfSI_StIn  # Line 937
    return An_StIn


def calculate_An_St(An_StIn: float, 
                    Dt_DMIn: float, 
                    InfRum_DMIn: float,
                    InfSI_DMIn: float
) -> float:
    """
    An_St: Starch % of diet + infusions
    """
    An_St = An_StIn / (Dt_DMIn + InfRum_DMIn + InfSI_DMIn) * 100  # Line 938
    return An_St


def calculate_An_rOMIn(Dt_rOMIn: float, InfRum_GlcIn: float,
                       InfRum_AcetIn: float, InfRum_PropIn: float,
                       InfRum_ButrIn: float, InfSI_AcetIn: float,
                       InfSI_PropIn: float, InfSI_ButrIn: float
) -> float:
    """
    An_rOMIn: Residual organic matter intake from diet + infusions, kg
    """
    An_rOMIn = (Dt_rOMIn + InfRum_GlcIn + InfRum_AcetIn + InfRum_PropIn +
                InfRum_ButrIn + InfSI_AcetIn + InfSI_PropIn + InfSI_ButrIn)   
    # Line 939-940
    return An_rOMIn


def calculate_An_rOM(An_rOMIn: float, 
                     Dt_DMIn: float, 
                     InfRum_DMIn: float,
                     InfSI_DMIn: float
) -> float:
    """
    An_rOM: Residual organic matter % of diet + infusions
    """
    An_rOM = An_rOMIn / (Dt_DMIn + InfRum_DMIn + InfSI_DMIn) * 100  # Line 941
    return An_rOM


def calculate_An_NDFIn(Dt_NDFIn: float, 
                       InfRum_NDFIn: float,
                       InfSI_NDFIn: float
) -> float:
    """
    An_NDFIn: NDF intake from diet and infusions, kg
    """
    An_NDFIn = (Dt_NDFIn + InfRum_NDFIn + InfSI_NDFIn)  # Line 942
    return An_NDFIn


def calculate_An_NDFIn_BW(An_NDFIn: float, An_BW: float) -> float:
    """
    An_NDFIn_BW: NDF over bodyweight, kg/kg
    """
    An_NDFIn_BW = An_NDFIn / An_BW * 100  # Line 943
    return An_NDFIn_BW


def calculate_An_NDF(An_NDFIn: float, 
                     Dt_DMIn: float, 
                     InfRum_DMIn: float,
                     InfSI_DMIn: float
) -> float:
    """
    An_NDF: NDF % of diet + infusion intake
    """
    An_NDF = An_NDFIn / (Dt_DMIn + InfRum_DMIn + InfSI_DMIn) * 100  # Line 944
    return An_NDF


def calculate_An_ADFIn(Dt_ADFIn: float, 
                       InfRum_ADFIn: float,
                       InfSI_ADFIn: float
) -> float:
    """
    An_ADFIn: ADF intake from diet + infusions, kg
    """
    An_ADFIn = (Dt_ADFIn + InfRum_ADFIn + InfSI_ADFIn)  # Line 945
    return An_ADFIn


def calculate_An_ADF(An_ADFIn: float, 
                     Dt_DMIn: float, 
                     InfRum_DMIn: float,
                     InfSI_DMIn: float
) -> float:
    """
    An_ADF: ADF % of diet + infusion intake
    """
    An_ADF = An_ADFIn / (Dt_DMIn + InfRum_DMIn + InfSI_DMIn) * 100  # Line 946
    return An_ADF


def calculate_An_CPIn_g(An_CPIn: float) -> float:
    """
    An_CPIn_g: Crude protein intake from diet + infusions, g
    """
    An_CPIn_g = An_CPIn * 1000  # Line 948
    return An_CPIn_g


def calculate_An_CP(An_CPIn: float, 
                    Dt_DMIn: float, 
                    InfRum_DMIn: float,
                    InfSI_DMIn: float
) -> float:
    """
    An_CP: Crude protein % of diet + infusion intake
    """
    An_CP = An_CPIn / (Dt_DMIn + InfRum_DMIn + InfSI_DMIn) * 100  # Line 949
    return An_CP


def calculate_An_NIn_g(An_CPIn: float) -> float:
    """
    An_NIn_g: Nitrogen intake from diet + infusions, g
    """
    An_NIn_g = An_CPIn * 0.16 * 1000  # Line 950
    return An_NIn_g


def calculate_An_FAhydrIn(Dt_FAhydrIn: float, Inf_FAIn: float) -> float:
    An_FAhydrIn = Dt_FAhydrIn + Inf_FAIn  
    # Line 954, need to specify FA vs TAG in the infusion matrix to account
    # for differences there. MDH
    return An_FAhydrIn


def calculate_An_FA(An_FAIn: float, 
                    Dt_DMIn: float, 
                    InfRum_DMIn: float,
                    InfSI_DMIn: float
) -> float:
    """
    An_FA: Fatty acid % of diet + infusions
    """
    An_FA = An_FAIn / (Dt_DMIn + InfRum_DMIn + InfSI_DMIn) * 100  # Line 955
    return An_FA


def calculate_An_AshIn(Dt_AshIn: float, 
                       InfRum_AshIn: float,
                       InfSI_AshIn: float
) -> float:
    """
    An_AshIn: Ash intake from diet + infusions, kg
    """
    An_AshIn = (Dt_AshIn + InfRum_AshIn + InfSI_AshIn)  # Line 956
    return An_AshIn


def calculate_An_Ash(An_AshIn: float, 
                     Dt_DMIn: float, 
                     InfRum_DMIn: float,
                     InfSI_DMIn: float
) -> float:
    """
    An_Ash: Ash % of diet + infusions intake
    """
    An_Ash = An_AshIn / (Dt_DMIn + InfRum_DMIn + InfSI_DMIn) * 100  # Line 957
    return An_Ash


def calculate_An_DigStIn_Base(Dt_DigStIn_Base: float, 
                              Inf_StIn: float,
                              Inf_ttdcSt: float
) -> float:
    """
    An_DigStIn_Base: 
    """
    An_DigStIn_Base = Dt_DigStIn_Base + Inf_StIn * Inf_ttdcSt / 100  
    # Glc considered as WSC and thus with rOM, Line 1017
    return An_DigStIn_Base


def calculate_An_DigWSCIn(Dt_DigWSCIn: float, 
                          InfRum_GlcIn: float,
                          InfSI_GlcIn: float
) -> float:
    """
    Digestable water soluble carbohydrate intake, kg/d
    """
    An_DigWSCIn = Dt_DigWSCIn + InfRum_GlcIn + InfSI_GlcIn  # Line 1022
    return An_DigWSCIn


def calculate_An_DigrOMtIn(Dt_DigrOMtIn: float, InfRum_GlcIn: float,
                           InfRum_AcetIn: float, InfRum_PropIn: float,
                           InfRum_ButrIn: float, InfSI_GlcIn: float,
                           InfSI_AcetIn: float, InfSI_PropIn: float,
                           InfSI_ButrIn: float
) -> float:
    """
    An_DigrOMtIn: truly digestable residual organic matter intake, kg/d
    """
    An_DigrOMtIn = (Dt_DigrOMtIn + InfRum_GlcIn + InfRum_AcetIn + 
                    InfRum_PropIn + InfRum_ButrIn + InfSI_GlcIn + 
                    InfSI_AcetIn + InfSI_PropIn + InfSI_ButrIn) # Line 1025-1026
    # Possibly missing a small amount of rOM when ingredients are infused.
    # Should infusions also drive endogenous rOM??
    return An_DigrOMtIn


def calculate_An_DigSt(An_DigStIn: float, 
                       Dt_DMIn: float, 
                       InfRum_DMIn: float,
                       InfSI_DMIn: float
) -> float:
    """
    An_DigSt: Digestable starch intake, kg/d
    """
    An_DigSt = An_DigStIn / (Dt_DMIn + InfRum_DMIn + InfSI_DMIn) * 100 # Line 1037
    return An_DigSt


def calculate_An_DigWSC(An_DigWSCIn: float, 
                        Dt_DMIn: float, 
                        InfRum_DMIn: float,
                        InfSI_DMIn: float
) -> float:
    """
    An_DigWSC: Digestable water soluble carbohydrates, % DM
    """
    An_DigWSC = An_DigWSCIn / (Dt_DMIn + InfRum_DMIn + InfSI_DMIn) * 100 
    # Line 1039
    return An_DigWSC


def calculate_An_DigrOMa(An_DigrOMaIn: float, 
                         Dt_DMIn: float,
                         InfRum_DMIn: float, 
                         InfSI_DMIn: float
) -> float:
    """
    Apparent digestable residual organic matter, % DM
    """
    An_DigrOMa = An_DigrOMaIn / (Dt_DMIn + InfRum_DMIn + InfSI_DMIn) * 100
    # Line 1043
    return An_DigrOMa


def calculate_An_DigrOMt(An_DigrOMtIn: float, 
                         Dt_DMIn: float,
                         InfRum_DMIn: float, 
                         InfSI_DMIn: float
) -> float:
    """
    An_DigrOMt: Truly digestable residual organic matter, % DM
    """
    An_DigrOMt = An_DigrOMtIn / (Dt_DMIn + InfRum_DMIn + InfSI_DMIn) * 100 
    # Line 1044
    return An_DigrOMt


def calculate_An_DigNDFIn_Base(Dt_NDFIn: float, 
                               InfRum_NDFIn: float,
                               TT_dcNDF_Base: float
) -> float:
    """
    An_DigNDFIn_Base: Base Digestable NDF Intake, kg/d
    """
    An_DigNDFIn_Base = (Dt_NDFIn + InfRum_NDFIn) * TT_dcNDF_Base / 100  
    # Line 1057
    return An_DigNDFIn_Base


def calculate_An_RDNPNCPIn(Dt_NPNCPIn: float, InfRum_NPNCPIn: float) -> float:
    """
    An_RDNPNCPIn: Rumen degradable CP from NPN Intake?, kg/d
    """
    An_RDNPNCPIn = Dt_NPNCPIn + InfRum_NPNCPIn  # Line 1094
    return An_RDNPNCPIn


def calculate_An_RUP(An_RUPIn: float, 
                     Dt_DMIn: float,
                     InfRum_DMIn: float
) -> float:
    """
    An_RUP: Rumen undegradable protein from diet + infusions, % DM
    """
    An_RUP = An_RUPIn / (Dt_DMIn + InfRum_DMIn) * 100  # Line 1096
    return An_RUP


def calculate_An_RUP_CP(An_RUPIn: float, 
                        Dt_CPIn: float,
                        InfRum_CPIn: float
) -> float:
    """
    An_RUP_CP: Rumen undegradable protein % of crude protein
    """
    An_RUP_CP = An_RUPIn / (Dt_CPIn + InfRum_CPIn) * 100  # Line 1097
    return An_RUP_CP


def calculate_An_idRUCPIn(Dt_idRUPIn: float, 
                          InfRum_idRUPIn: float,
                          InfSI_idCPIn: float
) -> float:
    """
    An_idRUCPIn: Intestinally digested rumen undegradable crude protein intake, kg/d
    """
    An_idRUCPIn = Dt_idRUPIn + InfRum_idRUPIn + InfSI_idCPIn  # RUP + infused idCP, Line 1099
    return An_idRUCPIn


def calculate_An_idRUP(An_idRUPIn: float, 
                       Dt_DMIn: float, 
                       InfRum_DMIn: float,
                       InfSI_DMIn: float
) -> float:
    """
    An_idRUP: Intestinally digestable rumen undegradable protein, % DM
    """
    An_idRUP = An_idRUPIn / (Dt_DMIn + InfRum_DMIn + InfSI_DMIn)  # Line 1100
    return An_idRUP


def calculate_An_RDTPIn(Dt_RDTPIn: float, 
                        InfRum_RDPIn: float,
                        InfRum_NPNCPIn: float, 
                        coeff_dict: dict
) -> float:
    """
    An_RDTPIn: Rumen degradable true protein intake, kg/d
    """
    req_coeff = ['dcNPNCP']
    ration_funcs.check_coeffs_in_coeff_dict(coeff_dict, req_coeff)
    An_RDTPIn = (Dt_RDTPIn + 
                 (InfRum_RDPIn - InfRum_NPNCPIn * coeff_dict['dcNPNCP'] / 100))  
    # Line 1107
    return An_RDTPIn


def calculate_An_RDP_CP(An_RDPIn: float, 
                        Dt_CPIn: float,
                        InfRum_CPIn: float
) -> float:
    """
    An_RDP_CP: Rumen degradable protein % of crude protein
    """
    An_RDP_CP = An_RDPIn / (Dt_CPIn + InfRum_CPIn) * 100  # Line 1109
    return An_RDP_CP


def calculate_An_DigCPa(An_DigCPaIn: float, 
                        An_DMIn: float,
                        InfArt_DMIn: float
) -> float:
    """
    An_DigCPa: Apparent total tract digested CP, % DM
    """
    An_DigCPa = An_DigCPaIn / (An_DMIn - InfArt_DMIn) * 100 # % of DM, Line 1222
    return An_DigCPa


def calculate_TT_dcAnCPa(An_DigCPaIn: float, 
                         An_CPIn: float,
                         InfArt_CPIn: float
) -> float:
    """
    TT_dcAnCPa: Digestability coefficient apparent total tract CP, % CP
    """
    TT_dcAnCPa = An_DigCPaIn / (An_CPIn - InfArt_CPIn) * 100 # % of CP, Line 1223
    return TT_dcAnCPa


def calculate_An_DigCPtIn(An_StatePhys: str, Dt_DigCPtIn: float,
                          Inf_idCPIn: float, An_RDPIn: float,
                          An_idRUPIn: float
) -> float:
    """
    An_DigCPtIn: True total tract digested CP intake, kg/d
    """
    if An_StatePhys == "Calf":
        An_DigCPtIn = Dt_DigCPtIn + Inf_idCPIn  
    # This may need more work depending on infusion type and protein source, Line 1226
    else:
        An_DigCPtIn = An_RDPIn + An_idRUPIn  # true CP total tract, Line 1225
    return An_DigCPtIn


def calculate_An_DigNtIn_g(An_DigCPtIn: float) -> float:
    """
    An_DigNtIn_g: True total tract digested N intake, g/d
    """
    An_DigNtIn_g = An_DigCPtIn / 6.25 * 1000  
    # some of the following are not valid for calves, Line 1227
    return An_DigNtIn_g


def calculate_An_DigTPtIn(An_RDTPIn: float, 
                          Fe_MiTP: float, 
                          An_idRUPIn: float,
                          Fe_NPend: float
) -> float:
    """
    An_DigTPtIn: True total tract digested true protein intake, kg/d
    """
    An_DigTPtIn = An_RDTPIn - Fe_MiTP + An_idRUPIn - Fe_NPend  # Line 1228
    return An_DigTPtIn


def calculate_An_DigCPt(An_DigCPtIn: float, 
                        An_DMIn: float,
                        InfArt_DMIn: float
) -> float:
    """
    An_DigCPt: True total tract digested CP, % DMI
    """
    An_DigCPt = An_DigCPtIn / (An_DMIn - InfArt_DMIn) * 100 # % of DMIn, Line 1230
    return An_DigCPt


def calculate_An_DigTPt(An_DigTPtIn: float, 
                        An_DMIn: float,
                        InfArt_DMIn: float
) -> float:
    """
    An_DigTPt: True digested total tract true protein, % DMI
    """
    An_DigTPt = An_DigTPtIn / (An_DMIn - InfArt_DMIn) * 100 # % of DMIn, Line 1231
    return An_DigTPt


def calculate_TT_dcAnCPt(An_DigCPtIn: float, 
                         An_CPIn: float,
                         InfArt_CPIn: float
) -> float:
    """
    TT_dcAnCPt: Digestability coefficient true total tract CP intake, % CP
    """
    TT_dcAnCPt = An_DigCPtIn / (An_CPIn - InfArt_CPIn) * 100 # % of CP, Line 1232
    return TT_dcAnCPt


def calculate_TT_dcAnTPt(An_DigTPtIn: float, An_TPIn: float, 
                         InfArt_CPIn: float, InfRum_NPNCPIn: float, 
                         InfSI_NPNCPIn: float
) -> float:
    """
    TT_dcAnTPt: Digestabgility coefficient apparent total tract true protein, % TP
    """
    TT_dcAnTPt = (An_DigTPtIn / 
                  (An_TPIn + InfArt_CPIn - InfRum_NPNCPIn - InfSI_NPNCPIn) * 100)  
    # % of TP, Line 1233
    return TT_dcAnTPt


def calculate_SI_dcAnRUP(An_idRUPIn: float, An_RUPIn: float) -> float:
    """
    SI_dcAnRUP: ?, doesn't get used anywhere in the model, reported in table
    """
    SI_dcAnRUP = An_idRUPIn / An_RUPIn * 100  # Line 1234
    return SI_dcAnRUP


def calculate_An_idCPIn(An_idRUPIn: float, Du_idMiCP: float) -> float:
    """
    An_idCPIn: Intestinally digested CP intake, kg/d
    """
    An_idCPIn = An_idRUPIn + Du_idMiCP  
    # not a true value as ignores recycled endCP, line 1235
    return An_idCPIn


def calculate_An_DigFA(An_DigFAIn: float, 
                       Dt_DMIn: float, 
                       InfRum_DMIn: float,
                       InfSI_DMIn: float
) -> float:
    """
    An_DigFA: Digestable FA, dietary and infusions, % of DMI
    """
    An_DigFA = An_DigFAIn / (Dt_DMIn + InfRum_DMIn + InfSI_DMIn) * 100 # Line 1309
    return An_DigFA


def calculate_TT_dcAnFA(Dt_DigFAIn: float, 
                        Inf_DigFAIn: float, 
                        Dt_FAIn: float,
                        Inf_FAIn: float
) -> float:
    """
    TT_dcAnFA: Digestability coefficient for total tract FA
    """
    TT_dcAnFA = (Dt_DigFAIn + Inf_DigFAIn) / (Dt_FAIn + Inf_FAIn) * 100  
    # this should be just gut infusions, but don't have those calculated as 
    # ruminal and SI DC will not be the same, Line 1312
    return TT_dcAnFA


def calculate_An_OMIn(Dt_OMIn: float, Inf_OMIn: float) -> float:
    """
    An_OMIn: Organic matter intake, dietary and infusions (kg/d)
    """
    An_OMIn = Dt_OMIn + Inf_OMIn  # Line 1317
    return An_OMIn


def calculate_An_DigOMaIn_Base(An_DigNDFIn_Base: float, An_DigStIn_Base: float,
                               An_DigFAIn: float, An_DigrOMaIn: float,
                               An_DigCPaIn: float
) -> float:
    """
    An_DigOMaIn_Base: Base apparent digested organic matter intake? (kg/d) 
    """
    An_DigOMaIn_Base = (An_DigNDFIn_Base + An_DigStIn_Base + An_DigFAIn + 
                        An_DigrOMaIn + An_DigCPaIn) # Line 1318
    return An_DigOMaIn_Base


def calculate_An_DigOMtIn_Base(An_DigNDFIn_Base: float, An_DigStIn_Base: float,
                               An_DigFAIn: float, An_DigrOMtIn: float,
                               An_DigCPtIn: float
) -> float:
    """
    An_DigOMtIn_Base: Base true digested organic matter intake? (kg/d)
    """
    An_DigOMtIn_Base = (An_DigNDFIn_Base + An_DigStIn_Base + An_DigFAIn + 
                        An_DigrOMtIn + An_DigCPtIn) # Line 1319
    return An_DigOMtIn_Base


def calculate_An_DigOMaIn(An_DigNDFIn: float, An_DigStIn: float,
                          An_DigFAIn: float, An_DigrOMaIn: float,
                          An_DigCPaIn: float
) -> float:
    """
    An_DigOMaIn: Apparent digested organic matter intake (kg/d)
    """
    An_DigOMaIn = (An_DigNDFIn + An_DigStIn + An_DigFAIn + 
                   An_DigrOMaIn + An_DigCPaIn)  # Line 1322
    return An_DigOMaIn


def calculate_An_DigOMtIn(An_DigNDFIn: float, An_DigStIn: float,
                          An_DigFAIn: float, An_DigrOMtIn: float,
                          An_DigCPtIn: float
) -> float:
    """
    An_DigOMtIn: True digested organic matter intake (kg/d)
    """
    An_DigOMtIn = (An_DigNDFIn + An_DigStIn + An_DigFAIn + 
                   An_DigrOMtIn + An_DigCPtIn)  # Line 1323
    return An_DigOMtIn


def calculate_TT_dcOMa(An_DigOMaIn: float, An_OMIn: float) -> float:
    """
    TT_dcOMa: Digestability coefficient apparent total tract organic matter 
    """
    TT_dcOMa = An_DigOMaIn / An_OMIn * 100  # Line 1324
    return TT_dcOMa


def calculate_TT_dcOMt(An_DigOMtIn: float, An_OMIn: float) -> float:
    """
    TT_dcOMt: Digestability coefficient true total tract organic matter
    """
    TT_dcOMt = An_DigOMtIn / An_OMIn * 100  # Line 1325
    return TT_dcOMt


def calculate_TT_dcOMt_Base(An_DigOMtIn_Base: float, An_OMIn: float) -> float:
    """
    TT_dcOMt_Base: Digestability coefficient base true total tract organic matter? 
    """
    TT_dcOMt_Base = An_DigOMtIn_Base / An_OMIn * 100  # Line 1326
    return TT_dcOMt_Base


def calculate_An_DigOMa(An_DigOMaIn: float, 
                        Dt_DMIn: float, 
                        InfRum_DMIn: float,
                        InfSI_DMIn: float
) -> float:
    """
    An_DigOMa: Apparent digested organic matter, dietary + infusions, % DMI
    """
    An_DigOMa = An_DigOMaIn / (Dt_DMIn + InfRum_DMIn + InfSI_DMIn) * 100 
    # Line 1329
    return An_DigOMa


def calculate_An_DigOMt(An_DigOMtIn: float, 
                        Dt_DMIn: float, 
                        InfRum_DMIn: float,
                        InfSI_DMIn: float
) -> float:
    """
    An_DigOMt: True digested organic matter, dietary + infusions, % DMI
    """
    An_DigOMt = An_DigOMtIn / (Dt_DMIn + InfRum_DMIn + InfSI_DMIn) * 100
    # Line 1330
    return An_DigOMt


def calculate_An_GEIn(Dt_GEIn: float, Inf_NDFIn: float, Inf_StIn: float,
                      Inf_FAIn: float, Inf_TPIn: float, Inf_NPNCPIn: float,
                      Inf_AcetIn: float, Inf_PropIn: float, Inf_ButrIn: float,
                      coeff_dict: dict
) -> float:
    """
    An_GEIn: Gross energy intake (Mcal/d)
    """
    req_coeff = [
        'En_NDF', 'En_St', 'En_FA', 'En_CP', 'En_NPNCP', 'En_Acet', 'En_Prop',
        'En_Butr'
    ]
    ration_funcs.check_coeffs_in_coeff_dict(coeff_dict, req_coeff)
    An_GEIn = (Dt_GEIn + 
               Inf_NDFIn * coeff_dict['En_NDF'] + 
               Inf_StIn * coeff_dict['En_St'] + 
               Inf_FAIn * coeff_dict['En_FA'] + 
               Inf_TPIn * coeff_dict['En_CP'] + 
               Inf_NPNCPIn * coeff_dict['En_NPNCP'] + 
               Inf_AcetIn * coeff_dict['En_Acet'] + 
               Inf_PropIn * coeff_dict['En_Prop'] + 
               Inf_ButrIn * coeff_dict['En_Butr']) # Line 1338-1339
    return An_GEIn


def calculate_An_GE(An_GEIn: float, An_DMIn: float) -> float:
    """
    An_GE: Gross energy intake, including infusions (Mcal/kg diet)
    """
    An_GE = An_GEIn / An_DMIn  # included all infusions in DMIn, Line 1341
    return An_GE


def calculate_An_DERDTPIn(An_RDTPIn: float, 
                          Fe_DEMiCPend: float,
                          Fe_DERDPend: float, 
                          coeff_dict: dict
) -> float:
    """
    An_DERDTPIn: Digestable energy in rumen degradable true protein (Mcal/d)
    """
    req_coeff = ['En_CP']
    ration_funcs.check_coeffs_in_coeff_dict(coeff_dict, req_coeff)
    An_DERDTPIn = An_RDTPIn * coeff_dict['En_CP'] - Fe_DEMiCPend - Fe_DERDPend  
    # Line 1359
    return An_DERDTPIn


def calculate_An_DEidRUPIn(An_idRUPIn: float, 
                           Fe_DERUPend: float,
                           coeff_dict: dict
) -> float:
    """
    An_DEidRUPIn: Digestable energy in intestinally digested RUP (Mcal/d)
    """
    req_coeff = ['En_CP']
    ration_funcs.check_coeffs_in_coeff_dict(coeff_dict, req_coeff)
    An_DEidRUPIn = An_idRUPIn * coeff_dict['En_CP'] - Fe_DERUPend  # Line 1360
    return An_DEidRUPIn


def calculate_An_DE(An_DEIn: float, An_DMIn: float) -> float:
    """
    An_DE: Digestable energy, diet + infusions (Mcal/d)
    """
    An_DE = An_DEIn / An_DMIn  # Line 1378
    return An_DE


def calculate_An_DE_GE(An_DEIn: float, An_GEIn: float) -> float:
    """
    An_DE_GE: Ratio of DE to GE
    """
    An_DE_GE = An_DEIn / An_GEIn  # Line 1379
    return An_DE_GE


def calculate_An_DEnp(An_DEInp: float, An_DMIn: float) -> float:
    """
    An_DEnp: Nonprotein digestable energy intake (Mcal/kg)
    """
    An_DEnp = An_DEInp / An_DMIn * 100  # Line 1386
    return An_DEnp


def calculate_An_GasE_IPCC2(An_GEIn: float) -> float:
    """
    An_GasE_IPCC2: ? (Mcal/d)
    """
    An_GasE_IPCC2 = 0.065 * An_GEIn  
    # but it reflects the whole farm not individual animal types, Line 1393
    return An_GasE_IPCC2


def calculate_GasE_DMIn(An_GasEOut: float, An_DMIn: float) -> float:
    """
    GasE_DMIn: Gaseous energy loss per kg DMI (Mcal/kg)
    """
    GasE_DMIn = An_GasEOut / An_DMIn  # Line 1413
    return GasE_DMIn


def calculate_GasE_GEIn(An_GasEOut: float, An_GEIn: float) -> float:
    """
    GasE_GEIn: Gaseous energy loss per Mcal gross energy intake
    """
    GasE_GEIn = An_GasEOut / An_GEIn  # Line 1414
    return GasE_GEIn


def calculate_GasE_DEIn(An_GasEOut: float, An_DEIn: float) -> float:
    """
    GasE_DEIn: Gaseous energy loss per Mcal digestable energy intake
    """
    GasE_DEIn = An_GasEOut / An_DEIn  # Line 1415
    return GasE_DEIn


def calculate_An_MEIn_ClfDry(An_MEIn: float, Dt_MEIn_ClfLiq: float) -> float:
    """Calf ME intake from dry feed"""
    An_MEIn_ClfDry = An_MEIn - Dt_MEIn_ClfLiq
    return An_MEIn_ClfDry


def calculate_An_ME_ClfDry(An_MEIn_ClfDry: float, 
                           An_DMIn: float, 
                           Dt_DMIn_ClfLiq: float
) -> float:
    An_ME_ClfDry = An_MEIn_ClfDry / (An_DMIn - Dt_DMIn_ClfLiq)
    return An_ME_ClfDry


def calculate_An_NE_ClfDry(An_ME_ClfDry: float) -> float:
    An_NE_ClfDry = (1.1104 * An_ME_ClfDry - 0.0946 * An_ME_ClfDry**2 + 
                    0.0065 * An_ME_ClfDry**3 - 0.7783)
    return An_NE_ClfDry


def calculate_An_IdAAIn(diet_data: dict, 
                        infusion_data: dict, 
                        AA_list: list, 
                        complete_An_data: dict
) -> dict:
    for AA in AA_list:
        complete_An_data[f'An_Id{AA}In'] = (diet_data[f'Dt_Id{AA}In'] + 
                                            infusion_data[f'Inf_Id{AA}In'])
    return complete_An_data


def calculate_An_XIn(diet_data: dict, 
                     infusion_data: dict,
                     variables: list, 
                     complete_An_data: dict
) -> dict:
    for var in variables:
        complete_An_data[f'An_{var}'] = (diet_data[f'Dt_{var}'] + 
                                         infusion_data[f'Inf_{var}'])
    return complete_An_data

####################
# Animal Warpper Functions
####################


def calculate_An_data_initial(animal_input, diet_data, infusion_data,
                              Monensin_eqn, GrUter_Wt, coeff_dict):
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
    An_data['An_DigNDFIn'] = calculate_An_DigNDFIn(
        diet_data['Dt_DigNDFIn'], infusion_data['InfRum_NDFIn'],
        diet_data['TT_dcNDF'])
    An_data['An_DENDFIn'] = calculate_An_DENDFIn(An_data['An_DigNDFIn'],
                                                 coeff_dict)
    An_data['An_DigStIn'] = calculate_An_DigStIn(diet_data['Dt_DigStIn'],
                                                 infusion_data['Inf_StIn'],
                                                 infusion_data['Inf_ttdcSt'])
    An_data['An_DEStIn'] = calculate_An_DEStIn(An_data['An_DigStIn'],
                                               coeff_dict)
    An_data['An_DigrOMaIn'] = calculate_An_DigrOMaIn(
        diet_data['Dt_DigrOMaIn'], infusion_data['InfRum_GlcIn'],
        infusion_data['InfRum_AcetIn'], infusion_data['InfRum_PropIn'],
        infusion_data['InfRum_ButrIn'], infusion_data['InfSI_GlcIn'],
        infusion_data['InfSI_AcetIn'], infusion_data['InfSI_PropIn'],
        infusion_data['InfSI_ButrIn'])
    An_data['An_DErOMIn'] = calculate_An_DErOMIn(An_data['An_DigrOMaIn'],
                                                 coeff_dict)
    An_data['An_idRUPIn'] = calculate_An_idRUPIn(
        diet_data['Dt_idRUPIn'], infusion_data['InfRum_idRUPIn'],
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
    An_data['An_GEIn'] = calculate_An_GEIn(
        diet_data['Dt_GEIn'], infusion_data['Inf_NDFIn'],
        infusion_data['Inf_StIn'], infusion_data['Inf_FAIn'],
        infusion_data['Inf_TPIn'], infusion_data['Inf_NPNCPIn'],
        infusion_data['Inf_AcetIn'], infusion_data['Inf_PropIn'],
        infusion_data['Inf_ButrIn'], coeff_dict)
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
                                                 Monensin_eqn, An_GasEOut_Dry,
                                                 An_GasEOut_Lact,
                                                 An_GasEOut_Heif)

    An_data['An_GutFill_BW'] = calculate_An_GutFill_BW(
        animal_input['An_BW'], animal_input['An_BW_mature'],
        animal_input['An_StatePhys'], animal_input['An_Parity_rl'],
        diet_data['Dt_DMIn_ClfLiq'], diet_data['Dt_DMIn_ClfStrt'], coeff_dict)
    An_data['An_BWnp'] = calculate_An_BWnp(animal_input['An_BW'], GrUter_Wt)
    An_data['An_GutFill_Wt'] = calculate_An_GutFill_Wt(An_data['An_GutFill_BW'],
                                                       An_data['An_BWnp'])
    An_data['An_BW_empty'] = calculate_An_BW_empty(animal_input['An_BW'],
                                                   An_data['An_GutFill_Wt'])
    An_data['An_MBW'] = calculate_An_MBW(animal_input['An_BW'])

    An_data['An_RDNPNCPIn'] = calculate_An_RDNPNCPIn(
        diet_data['Dt_NPNCPIn'], infusion_data['InfRum_NPNCPIn'])
    An_data['An_RUP'] = calculate_An_RUP(An_data['An_RUPIn'],
                                         animal_input['DMI'],
                                         infusion_data['InfRum_DMIn'])
    An_data['An_RUP_CP'] = calculate_An_RUP_CP(An_data['An_RUPIn'],
                                               diet_data['Dt_CPIn'],
                                               infusion_data['InfRum_CPIn'])
    An_data['An_idRUCPIn'] = calculate_An_idRUCPIn(
        diet_data['Dt_idRUPIn'], infusion_data['InfRum_idRUPIn'],
        infusion_data['InfSI_idCPIn'])
    An_data['An_idRUP'] = calculate_An_idRUP(An_data['An_idRUPIn'],
                                             animal_input["DMI"],
                                             infusion_data['InfRum_DMIn'],
                                             infusion_data['InfSI_DMIn'])
    An_data['An_RDTPIn'] = calculate_An_RDTPIn(diet_data['Dt_RDTPIn'],
                                               infusion_data['InfRum_RDPIn'],
                                               infusion_data['InfRum_NPNCPIn'],
                                               coeff_dict)
    An_data['An_RDP_CP'] = calculate_An_RDP_CP(An_data['An_RDPIn'],
                                               diet_data['Dt_CPIn'],
                                               infusion_data['InfRum_CPIn'])
    An_data['An_GasE_IPCC2'] = calculate_An_GasE_IPCC2(An_data['An_GEIn'])
    return An_data


def calculate_An_data_complete(
        An_data_initial: dict,
        diet_data: dict,
        An_StatePhys: str,
        An_BW: float,
        DMI: float,
        Fe_CP: float,
        Fe_MiTP: float,
        Fe_NPend: float,
        Fe_DEMiCPend: float,
        Fe_DERDPend: float,
        Fe_DERUPend: float,
        Du_idMiCP: float,
        infusion_data: dict,
        Monensin_eqn: int,  #equation_selection['Monensin_eqn']
        coeff_dict: dict):
    complete_An_data = An_data_initial.copy()

    complete_An_data['An_DigCPaIn'] = calculate_An_DigCPaIn(
        complete_An_data['An_CPIn'], infusion_data['InfArt_CPIn'], Fe_CP)
    complete_An_data['An_DECPIn'] = calculate_An_DECPIn(
        complete_An_data['An_DigCPaIn'], coeff_dict)
    complete_An_data['An_DENPNCPIn'] = calculate_An_DENPNCPIn(
        diet_data['Dt_NPNCPIn'], coeff_dict)
    complete_An_data['An_DETPIn'] = calculate_An_DETPIn(
        complete_An_data['An_DECPIn'], complete_An_data['An_DENPNCPIn'],
        coeff_dict)
    complete_An_data['An_DigFAIn'] = calculate_An_DigFAIn(
        diet_data['Dt_DigFAIn'], infusion_data['Inf_DigFAIn'])
    complete_An_data['An_DEFAIn'] = calculate_An_DEFAIn(
        complete_An_data['An_DigFAIn'], coeff_dict)
    complete_An_data['An_DEIn'] = calculate_An_DEIn(
        An_StatePhys, complete_An_data['An_DENDFIn'],
        complete_An_data['An_DEStIn'], complete_An_data['An_DErOMIn'],
        complete_An_data['An_DETPIn'], complete_An_data['An_DENPNCPIn'],
        complete_An_data['An_DEFAIn'], infusion_data['Inf_DEAcetIn'],
        infusion_data['Inf_DEPropIn'], infusion_data['Inf_DEPropIn'],
        diet_data['Dt_DMIn_ClfLiq'], diet_data['Dt_DEIn'], Monensin_eqn)
    complete_An_data['An_DEInp'] = calculate_An_DEInp(
        complete_An_data['An_DEIn'], complete_An_data['An_DETPIn'],
        complete_An_data['An_DENPNCPIn'])
    complete_An_data['An_TPIn'] = calculate_An_TPIn(diet_data['Dt_TPIn'],
                                                    infusion_data['Inf_TPIn'])
    complete_An_data['An_DigTPaIn'] = calculate_An_DigTPaIn(
        complete_An_data['An_TPIn'], infusion_data['InfArt_CPIn'], Fe_CP)
    AA_list = [
        'Arg', 'His', 'Ile', 'Leu', 'Lys', 'Met', 'Phe', 'Thr', 'Trp', 'Val'
    ]
    complete_An_data = calculate_An_IdAAIn(
        diet_data, infusion_data, AA_list, complete_An_data
        )

    nutrient_list = ['CPIn', 'NPNCPIn', 'TPIn', 'FAIn']
    complete_An_data = calculate_An_XIn(
        diet_data, infusion_data, nutrient_list, complete_An_data
        )
    complete_An_data['An_DMIn_MBW'] = calculate_An_DMIn_MBW(
        complete_An_data['An_DMIn'], complete_An_data['An_MBW'])
    complete_An_data['An_StIn'] = calculate_An_StIn(
        diet_data['Dt_StIn'], infusion_data['InfRum_StIn'],
        infusion_data['InfSI_StIn'])
    complete_An_data['An_St'] = calculate_An_St(complete_An_data['An_StIn'],
                                                DMI,
                                                infusion_data['InfRum_DMIn'],
                                                infusion_data['InfSI_DMIn'])
    complete_An_data['An_rOMIn'] = calculate_An_rOMIn(
        diet_data['Dt_rOMIn'], infusion_data['InfRum_GlcIn'],
        infusion_data['InfRum_AcetIn'], infusion_data['InfRum_PropIn'],
        infusion_data['InfRum_ButrIn'], infusion_data['InfSI_AcetIn'],
        infusion_data['InfSI_PropIn'], infusion_data['InfSI_ButrIn'])
    complete_An_data['An_rOM'] = calculate_An_rOM(complete_An_data['An_rOMIn'],
                                                  DMI,
                                                  infusion_data['InfRum_DMIn'],
                                                  infusion_data['InfSI_DMIn'])
    complete_An_data['An_NDFIn'] = calculate_An_NDFIn(
        diet_data['Dt_NDFIn'], infusion_data['InfRum_NDFIn'],
        infusion_data['InfSI_NDFIn'])
    complete_An_data['An_NDFIn_BW'] = calculate_An_NDFIn_BW(
        complete_An_data['An_NDFIn'], An_BW)
    complete_An_data['An_NDF'] = calculate_An_NDF(complete_An_data['An_NDFIn'],
                                                  DMI,
                                                  infusion_data['InfRum_DMIn'],
                                                  infusion_data['InfSI_DMIn'])
    complete_An_data['An_ADFIn'] = calculate_An_ADFIn(
        diet_data['Dt_ADFIn'], infusion_data['InfRum_ADFIn'],
        infusion_data['InfSI_ADFIn'])
    complete_An_data['An_ADF'] = calculate_An_ADF(complete_An_data['An_ADFIn'],
                                                  DMI,
                                                  infusion_data['InfRum_DMIn'],
                                                  infusion_data['InfSI_DMIn'])
    complete_An_data['An_CPIn_g'] = calculate_An_CPIn_g(
        complete_An_data['An_CPIn'])
    complete_An_data['An_CP'] = calculate_An_CP(complete_An_data['An_CPIn'],
                                                DMI,
                                                infusion_data['InfRum_DMIn'],
                                                infusion_data['InfSI_DMIn'])
    complete_An_data['An_NIn_g'] = calculate_An_NIn_g(
        complete_An_data['An_CPIn'])
    complete_An_data['An_FAhydrIn'] = calculate_An_FAhydrIn(
        diet_data['Dt_FAhydrIn'], infusion_data['Inf_FAIn'])
    complete_An_data['An_FA'] = calculate_An_FA(complete_An_data['An_FAIn'],
                                                DMI,
                                                infusion_data['InfRum_DMIn'],
                                                infusion_data['InfSI_DMIn'])
    complete_An_data['An_AshIn'] = calculate_An_AshIn(
        diet_data['Dt_AshIn'], infusion_data['InfRum_AshIn'],
        infusion_data['InfSI_AshIn'])
    complete_An_data['An_Ash'] = calculate_An_Ash(complete_An_data['An_AshIn'],
                                                  DMI,
                                                  infusion_data['InfRum_DMIn'],
                                                  infusion_data['InfSI_DMIn'])
    complete_An_data['An_DigStIn_Base'] = calculate_An_DigStIn_Base(
        diet_data['Dt_DigStIn_Base'], infusion_data['Inf_StIn'],
        infusion_data['Inf_ttdcSt'])
    complete_An_data['An_DigWSCIn'] = calculate_An_DigWSCIn(
        diet_data['Dt_DigWSCIn'], infusion_data['InfRum_GlcIn'],
        infusion_data['InfSI_GlcIn'])
    complete_An_data['An_DigrOMtIn'] = calculate_An_DigrOMtIn(
        diet_data['Dt_DigrOMtIn'], infusion_data['InfRum_GlcIn'],
        infusion_data['InfRum_AcetIn'], infusion_data['InfRum_PropIn'],
        infusion_data['InfRum_ButrIn'], infusion_data['InfSI_GlcIn'],
        infusion_data['InfSI_AcetIn'], infusion_data['InfSI_PropIn'],
        infusion_data['InfSI_ButrIn'])
    complete_An_data['An_DigSt'] = calculate_An_DigSt(
        complete_An_data['An_DigStIn'], DMI, infusion_data['InfRum_DMIn'],
        infusion_data['InfSI_DMIn'])
    complete_An_data['An_DigWSC'] = calculate_An_DigWSC(
        complete_An_data['An_DigWSCIn'], DMI, infusion_data['InfRum_DMIn'],
        infusion_data['InfSI_DMIn'])
    complete_An_data['An_DigrOMa'] = calculate_An_DigrOMa(
        complete_An_data['An_DigrOMaIn'], DMI, infusion_data['InfRum_DMIn'],
        infusion_data['InfSI_DMIn'])
    complete_An_data['An_DigrOMt'] = calculate_An_DigrOMt(
        complete_An_data['An_DigrOMtIn'], DMI, infusion_data['InfRum_DMIn'],
        infusion_data['InfSI_DMIn'])
    complete_An_data['An_DigNDFIn_Base'] = calculate_An_DigNDFIn_Base(
        diet_data['Dt_NDFIn'], infusion_data['InfRum_NDFIn'],
        diet_data['TT_dcNDF_Base'])
    complete_An_data['An_DigCPa'] = calculate_An_DigCPa(
        complete_An_data['An_DigCPaIn'], complete_An_data['An_DMIn'],
        infusion_data['InfArt_DMIn'])
    complete_An_data['TT_dcAnCPa'] = calculate_TT_dcAnCPa(
        complete_An_data['An_DigCPaIn'], complete_An_data['An_CPIn'],
        infusion_data['InfArt_CPIn'])
    complete_An_data['An_DigCPtIn'] = calculate_An_DigCPtIn(
        An_StatePhys, diet_data['Dt_DigCPtIn'], infusion_data['Inf_idCPIn'],
        complete_An_data['An_RDPIn'], complete_An_data['An_idRUPIn'])
    complete_An_data['An_DigNtIn_g'] = calculate_An_DigNtIn_g(
        complete_An_data['An_DigCPtIn'])
    complete_An_data['An_DigTPtIn'] = calculate_An_DigTPtIn(
        complete_An_data['An_RDTPIn'], Fe_MiTP, complete_An_data['An_idRUPIn'],
        Fe_NPend)
    complete_An_data['An_DigCPt'] = calculate_An_DigCPt(
        complete_An_data['An_DigCPtIn'], complete_An_data['An_DMIn'],
        infusion_data['InfArt_DMIn'])
    complete_An_data['An_DigTPt'] = calculate_An_DigTPt(
        complete_An_data['An_DigTPtIn'], complete_An_data['An_DMIn'],
        infusion_data['InfArt_DMIn'])
    complete_An_data['TT_dcAnCPt'] = calculate_TT_dcAnCPt(
        complete_An_data['An_DigCPtIn'], complete_An_data['An_CPIn'],
        infusion_data['InfArt_CPIn'])
    complete_An_data['TT_dcAnTPt'] = calculate_TT_dcAnTPt(
        complete_An_data['An_DigTPtIn'], complete_An_data['An_TPIn'],
        infusion_data['InfArt_CPIn'], infusion_data['InfRum_NPNCPIn'],
        infusion_data['InfSI_NPNCPIn'])
    complete_An_data['SI_dcAnRUP'] = calculate_SI_dcAnRUP(
        complete_An_data['An_idRUPIn'], complete_An_data['An_RUPIn'])
    complete_An_data['An_idCPIn'] = calculate_An_idCPIn(
        complete_An_data['An_idRUPIn'], Du_idMiCP)
    complete_An_data['An_DigFA'] = calculate_An_DigFA(
        complete_An_data['An_DigFAIn'], DMI, infusion_data['InfRum_DMIn'],
        infusion_data['InfSI_DMIn'])
    complete_An_data['TT_dcAnFA'] = calculate_TT_dcAnFA(
        diet_data['Dt_DigFAIn'], infusion_data['Inf_DigFAIn'],
        diet_data['Dt_FAIn'], infusion_data['Inf_FAIn'])
    complete_An_data['An_OMIn'] = calculate_An_OMIn(diet_data['Dt_OMIn'],
                                                    infusion_data['Inf_OMIn'])
    complete_An_data['An_DigOMaIn_Base'] = calculate_An_DigOMaIn_Base(
        complete_An_data['An_DigNDFIn_Base'],
        complete_An_data['An_DigStIn_Base'], complete_An_data['An_DigFAIn'],
        complete_An_data['An_DigrOMaIn'], complete_An_data['An_DigCPaIn'])
    complete_An_data['An_DigOMtIn_Base'] = calculate_An_DigOMtIn_Base(
        complete_An_data['An_DigNDFIn_Base'],
        complete_An_data['An_DigStIn_Base'], complete_An_data['An_DigFAIn'],
        complete_An_data['An_DigrOMtIn'], complete_An_data['An_DigCPtIn'])
    complete_An_data['An_DigOMaIn'] = calculate_An_DigOMaIn(
        complete_An_data['An_DigNDFIn'], complete_An_data['An_DigStIn'],
        complete_An_data['An_DigFAIn'], complete_An_data['An_DigrOMaIn'],
        complete_An_data['An_DigCPaIn'])
    complete_An_data['An_DigOMtIn'] = calculate_An_DigOMtIn(
        complete_An_data['An_DigNDFIn'], complete_An_data['An_DigStIn'],
        complete_An_data['An_DigFAIn'], complete_An_data['An_DigrOMtIn'],
        complete_An_data['An_DigCPtIn'])
    complete_An_data['TT_dcOMa'] = calculate_TT_dcOMa(
        complete_An_data['An_DigOMaIn'], complete_An_data['An_OMIn'])
    complete_An_data['TT_dcOMt'] = calculate_TT_dcOMt(
        complete_An_data['An_DigOMtIn'], complete_An_data['An_OMIn'])
    complete_An_data['TT_dcOMt_Base'] = calculate_TT_dcOMt_Base(
        complete_An_data['An_DigOMtIn_Base'], complete_An_data['An_OMIn'])
    complete_An_data['An_DigOMa'] = calculate_An_DigOMa(
        complete_An_data['An_DigOMaIn'], DMI, infusion_data['InfRum_DMIn'],
        infusion_data['InfSI_DMIn'])
    complete_An_data['An_DigOMt'] = calculate_An_DigOMt(
        complete_An_data['An_DigOMtIn'], DMI, infusion_data['InfRum_DMIn'],
        infusion_data['InfSI_DMIn'])
    complete_An_data['An_GEIn'] = calculate_An_GEIn(
        diet_data['Dt_GEIn'], infusion_data['Inf_NDFIn'],
        infusion_data['Inf_StIn'], infusion_data['Inf_FAIn'],
        infusion_data['Inf_TPIn'], infusion_data['Inf_NPNCPIn'],
        infusion_data['Inf_AcetIn'], infusion_data['Inf_PropIn'],
        infusion_data['Inf_ButrIn'], coeff_dict)
    complete_An_data['An_GE'] = calculate_An_GE(complete_An_data['An_GEIn'],
                                                complete_An_data['An_DMIn'])
    complete_An_data['An_DERDTPIn'] = calculate_An_DERDTPIn(
        complete_An_data['An_RDTPIn'], Fe_DEMiCPend, Fe_DERDPend, coeff_dict)
    complete_An_data['An_DEidRUPIn'] = calculate_An_DEidRUPIn(
        complete_An_data['An_idRUPIn'], Fe_DERUPend, coeff_dict)
    complete_An_data['An_DE'] = calculate_An_DE(complete_An_data['An_DEIn'],
                                                complete_An_data['An_DMIn'])
    complete_An_data['An_DE_GE'] = calculate_An_DE_GE(
        complete_An_data['An_DEIn'], complete_An_data['An_GEIn'])
    complete_An_data['An_DEnp'] = calculate_An_DEnp(
        complete_An_data['An_DEInp'], complete_An_data['An_DMIn'])
    complete_An_data['GasE_DMIn'] = calculate_GasE_DMIn(
        complete_An_data['An_GasEOut'], complete_An_data['An_DMIn'])
    complete_An_data['GasE_GEIn'] = calculate_GasE_GEIn(
        complete_An_data['An_GasEOut'], complete_An_data['An_GEIn'])
    complete_An_data['GasE_DEIn'] = calculate_GasE_DEIn(
        complete_An_data['An_GasEOut'], complete_An_data['An_DEIn'])

    return complete_An_data


####################
# Animal Functions not in Wrapper
####################


def calculate_An_MPIn(An_StatePhys: str,
                      An_DigCPtIn: float,
                      Dt_idRUPIn: float, 
                      Du_idMiTP: float, 
                      InfArt_TPIn: float
) -> float:
    if An_StatePhys == "Calf":
        An_MPIn = An_DigCPtIn # Line 1237
    else:    
        # Line 1236 (Equation 20-136 p. 432 - without infused TP)
        An_MPIn = Dt_idRUPIn + Du_idMiTP + InfArt_TPIn
    return An_MPIn


def calculate_An_MPIn_g(An_MPIn):
    An_MPIn_g = An_MPIn * 1000  # Line 1238
    return An_MPIn_g


def calculate_An_RDPbal_g(An_RDPIn_g: float, Du_MiCP_g: float) -> float:
    """
    An_RDPbal_g: Rumen degradable protein balance, g/d
    """
    An_RDPbal_g = An_RDPIn_g - Du_MiCP_g  # Line 1168
    return An_RDPbal_g


def calculate_An_MP_CP(An_MPIn: float, An_CPIn: float) -> float:
    """
    An_MP_CP: Metabolizable protein % of CP

    NOTE: This gets calculated twice, first at line 1240 and again at line 3123
    An_MP_CP is not used in any caclulations. I've set it to the second equation so
    the Python and R outputs match - Braeden 
    """
    # An_MP_CP = An_MPIn / An_CPIn * 100  # Line 1240
    An_MP_CP = An_MPIn / An_CPIn  # Line 3123
    return An_MP_CP


def calculate_An_MP(An_MPIn: float, 
                    Dt_DMIn: float, 
                    InfRum_DMIn: float,
                    InfSI_DMIn: float
) -> float:
    """
    An_MP: Metabolizable protein, % DMI
    """
    An_MP = An_MPIn / (Dt_DMIn + InfRum_DMIn + InfSI_DMIn) * 100  # Line 1239
    return An_MP


def calculate_An_NPm_Use(Scrf_NP_g: float, 
                         Fe_NPend_g: float,
                         Ur_NPend_g: float
) -> float:
    """
    An_NPm_Use: Net protein used for maintenance? (g/d)
    """
    An_NPm_Use = Scrf_NP_g + Fe_NPend_g + Ur_NPend_g  # Line 2063
    return An_NPm_Use


def calculate_An_CPm_Use(Scrf_CP_g: float, 
                         Fe_CPend_g: float,
                         Ur_NPend_g: float
) -> float:
    """
    An_CPm_Use: Crude protein used for maintenance? (g/d)
    """
    An_CPm_Use = Scrf_CP_g + Fe_CPend_g + Ur_NPend_g  # Line 2064
    return An_CPm_Use


def calculate_An_ME(An_MEIn: float, An_DMIn: float) -> float:
    """
    An_ME: ME intake as a fraction of DMI (Mcal/kg)
    """
    An_ME = An_MEIn / An_DMIn  # Line 2759
    return An_ME


def calculate_An_ME_GE(An_MEIn: float, An_GEIn: float) -> float:
    """
    An_ME_GE: ME intake as a fraction of GE intake (Mcal/Mcal)
    """
    An_ME_GE = An_MEIn / An_GEIn  # Line 2760
    return An_ME_GE


def calculate_An_ME_DE(An_MEIn: float, An_DEIn: float) -> float:
    """
    An_ME_DE: ME intake as a fraction of DE intake (Mcal/Mcal)
    """
    An_ME_DE = An_MEIn / An_DEIn  # Line 2761
    return An_ME_DE


def calculate_An_NE_GE(An_NEIn: float, An_GEIn: float) -> float:
    """
    An_NE_GE: NE intake as a fraction of GE intake (Mcal/Mcal)
    """
    An_NE_GE = An_NEIn / An_GEIn  # Line 2764
    return An_NE_GE


def calculate_An_NE_DE(An_NEIn: float, An_DEIn: float) -> float:
    """
    An_NE_DE: NE intake as a fraction of DE intake (Mcal/Mcal)
    """
    An_NE_DE = An_NEIn / An_DEIn  # Line 2765
    return An_NE_DE


def calculate_An_NE_ME(An_NEIn: float, An_MEIn: float) -> float:
    """
    An_NE_ME: NE intake as a fraction of ME intake (Mcal/Mcal)
    """
    An_NE_ME = An_NEIn / An_MEIn  # Line 2766
    return An_NE_ME


def calculate_An_MPIn_MEIn(An_MPIn_g: float, An_MEIn: float) -> float:
    """
    An_MPIn_MEIn: MP intake as a fraction of ME intake (g/Mcal)
    """
    An_MPIn_MEIn = An_MPIn_g / An_MEIn  # g/Mcal, Line 2767
    return An_MPIn_MEIn


def calculate_An_RUPIn_g(An_RUPIn: float) -> float:
    """
    An_RUPIn_g: RUP intake (g/d)
    """
    An_RUPIn_g = An_RUPIn * 1000  # Line 3132
    return An_RUPIn_g


def calculate_An_Grazing(Dt_PastIn: float, Dt_DMIn: float) -> float:
    if Dt_PastIn / Dt_DMIn < 0.005:
        An_Grazing = 0
        return An_Grazing
    return 1


def calculate_En_OM(An_DEIn: float, An_DigOMtIn: float) -> float:
    En_OM = An_DEIn / An_DigOMtIn   # Line 1375
    return En_OM
