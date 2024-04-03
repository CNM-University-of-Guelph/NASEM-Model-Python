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
    """
    see page 34 for comments, gut fill is default 0.18 for cows
    Weaned calf == heifer, which is based on equations 11-1a/b using 85% (inverse of 0.15)
    Comments in book suggest this is not always a suitable assumption (that gut fill is 15% of BW), consider making this a coeff that can be changed in coeff_dict?
    """
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


def calculate_An_MEIn_approx(An_DEInp: float, An_DENPNCPIn: float, An_DigTPaIn: float, Body_NPgain: float, An_GasEOut: float, coeff_dict: dict) -> float:
    """
    An_MEIn_approx: Approximate ME intake, see note:
        Adjust heifer MPuse target if the MP:ME ratio is below optimum for development.
        Can't calculate ME before MP, thus estimated ME in the MP:ME ratio using the target NPgain.  Will be incorrect
        if the animal is lactating or gestating.
    This is used by Equation 11-11
    """
    An_MEIn_approx = An_DEInp + An_DENPNCPIn + (An_DigTPaIn - Body_NPgain) * 4.0 + Body_NPgain * coeff_dict['En_CP'] - An_GasEOut   # Line 2685
    return An_MEIn_approx


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


def calculate_An_DMIn_MBW(An_DMIn: float, An_MBW: float) -> float:
    """
    An_DMIn_MBW: kg Dry matter intake per kg metabolic body weight, kg/kg
    """
    An_DMIn_MBW = An_DMIn / An_MBW  # Line 936
    return An_DMIn_MBW 


def calculate_An_StIn(Dt_StIn: float, InfRum_StIn: float, InfSI_StIn: float) -> float:
    """
    An_StIn: Dietary + infused starch intake, kg
    """
    An_StIn = Dt_StIn + InfRum_StIn + InfSI_StIn    # Line 937
    return An_StIn 


def calculate_An_St(An_StIn: float, Dt_DMIn: float, InfRum_DMIn: float, InfSI_DMIn: float) -> float:
    """
    An_St: Starch % of diet + infusions
    """
    An_St = An_StIn / (Dt_DMIn + InfRum_DMIn + InfSI_DMIn) * 100    # Line 938
    return An_St


def calculate_An_rOMIn(Dt_rOMIn: float, InfRum_GlcIn: float, InfRum_AcetIn: float, InfRum_PropIn: float, InfRum_ButrIn: float, InfSI_AcetIn: float, InfSI_PropIn: float, InfSI_ButrIn: float) -> float:
    """
    An_rOMIn: Residual organic matter intake from diet + infusions, kg
    """
    An_rOMIn = Dt_rOMIn + InfRum_GlcIn + InfRum_AcetIn \
    + InfRum_PropIn + InfRum_ButrIn + InfSI_AcetIn \
    + InfSI_PropIn + InfSI_ButrIn   # Line 939-940
    return An_rOMIn


def calculate_An_rOM(An_rOMIn: float, Dt_DMIn: float, InfRum_DMIn: float, InfSI_DMIn: float) -> float:
    """
    An_rOM: Residual organic matter % of diet + infusions
    """
    An_rOM = An_rOMIn / (Dt_DMIn + InfRum_DMIn + InfSI_DMIn) * 100  # Line 941
    return An_rOM


def calculate_An_NDFIn(Dt_NDFIn: float, InfRum_NDFIn: float, InfSI_NDFIn: float) -> float:
    """
    An_NDFIn: NDF intake from diet and infusions, kg
    """
    An_NDFIn = (Dt_NDFIn + InfRum_NDFIn + InfSI_NDFIn)  # Line 942
    return An_NDFIn


def calculate_An_NDFIn_BW(An_NDFIn: float, An_BW: float) -> float: 
    """
    An_NDFIn_BW: NDF over bodyweight, kg/kg
    """    
    An_NDFIn_BW = An_NDFIn / An_BW * 100    # Line 943
    return An_NDFIn_BW


def calculate_An_NDF(An_NDFIn: float, Dt_DMIn: float, InfRum_DMIn: float, InfSI_DMIn: float) -> float:
    """
    An_NDF: NDF % of diet + infusion intake
    """
    An_NDF = An_NDFIn / (Dt_DMIn + InfRum_DMIn + InfSI_DMIn) * 100  # Line 944
    return An_NDF


def calculate_An_ADFIn(Dt_ADFIn: float, InfRum_ADFIn: float, InfSI_ADFIn: float) -> float:
    """
    An_ADFIn: ADF intake from diet + infusions, kg
    """    
    An_ADFIn = (Dt_ADFIn + InfRum_ADFIn + InfSI_ADFIn)  # Line 945
    return An_ADFIn


def calculate_An_ADF(An_ADFIn: float, Dt_DMIn: float, InfRum_DMIn: float, InfSI_DMIn: float) -> float:
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


def calculate_An_CP(An_CPIn: float, Dt_DMIn: float, InfRum_DMIn: float, InfSI_DMIn: float) -> float:
    """
    An_CP: Crude protein % of diet + infusion intake
    """
    An_CP = An_CPIn / (Dt_DMIn + InfRum_DMIn + InfSI_DMIn) * 100    # Line 949
    return An_CP


def calculate_An_NIn_g(An_CPIn: float) -> float:
    """
    An_NIn_g: Nitrogen intake from diet + infusions, g
    """
    An_NIn_g = An_CPIn * 0.16 * 1000    # Line 950
    return An_NIn_g


def calculate_An_FAhydrIn(Dt_FAhydrIn: float, Inf_FAIn: float) -> float:
    An_FAhydrIn = Dt_FAhydrIn + Inf_FAIn  # Line 954, need to specify FA vs TAG in the infusion matrix to account for differences there. MDH
    return An_FAhydrIn


def calculate_An_FA(An_FAIn: float, Dt_DMIn: float, InfRum_DMIn: float, InfSI_DMIn: float) -> float:
    """
    An_FA: Fatty acid % of diet + infusions
    """
    An_FA = An_FAIn / (Dt_DMIn + InfRum_DMIn + InfSI_DMIn) * 100    # Line 955
    return An_FA


def calculate_An_AshIn(Dt_AshIn: float, InfRum_AshIn: float, InfSI_AshIn: float) -> float:
    """
    An_AshIn: Ash intake from diet + infusions, kg
    """
    An_AshIn = (Dt_AshIn + InfRum_AshIn + InfSI_AshIn)  # Line 956
    return An_AshIn


def calculate_An_Ash(An_AshIn: float, Dt_DMIn: float, InfRum_DMIn: float, InfSI_DMIn: float) -> float:
    """
    An_Ash: Ash % of diet + infusions intake
    """
    An_Ash = An_AshIn / (Dt_DMIn + InfRum_DMIn + InfSI_DMIn) * 100  # Line 957
    return An_Ash


def calculate_An_DigStIn_Base(Dt_DigStIn_Base: float, Inf_StIn: float, Inf_ttdcSt: float) -> float:
    """
    An_DigStIn_Base: 
    """
    An_DigStIn_Base = Dt_DigStIn_Base + Inf_StIn * Inf_ttdcSt / 100	# Glc considered as WSC and thus with rOM, Line 1017
    return An_DigStIn_Base


def calculate_An_DigWSCIn(Dt_DigWSCIn: float, InfRum_GlcIn: float, InfSI_GlcIn: float) -> float:
    """
    Digestable water soluble carbohydrate intake, kg/d
    """
    An_DigWSCIn = Dt_DigWSCIn + InfRum_GlcIn + InfSI_GlcIn  # Line 1022
    return An_DigWSCIn


def calculate_An_DigrOMtIn(Dt_DigrOMtIn: float, InfRum_GlcIn: float, InfRum_AcetIn: float, InfRum_PropIn: float, InfRum_ButrIn: float, InfSI_GlcIn: float, InfSI_AcetIn: float, InfSI_PropIn: float, InfSI_ButrIn: float) -> float:
    """
    An_DigrOMtIn: truly digestable residual organic matter intake, kg/d
    """
    An_DigrOMtIn = Dt_DigrOMtIn + InfRum_GlcIn + InfRum_AcetIn + InfRum_PropIn \
                   + InfRum_ButrIn + InfSI_GlcIn + InfSI_AcetIn + InfSI_PropIn + InfSI_ButrIn   # Line 1025-1026
    # Possibly missing a small amount of rOM when ingredients are infused. 
    # Should infusions also drive endogenous rOM??
    return An_DigrOMtIn


def calculate_An_DigSt(An_DigStIn: float, Dt_DMIn: float, InfRum_DMIn: float, InfSI_DMIn: float) -> float:
    """
    An_DigSt: Digestable starch intake, kg/d
    """
    An_DigSt = An_DigStIn / (Dt_DMIn + InfRum_DMIn + InfSI_DMIn) * 100  # Line 1037
    return An_DigSt


def calculate_An_DigWSC(An_DigWSCIn: float, Dt_DMIn: float, InfRum_DMIn: float, InfSI_DMIn: float) -> float:
    """
    An_DigWSC: Digestable water soluble carbohydrates, % DM
    """
    An_DigWSC = An_DigWSCIn / (Dt_DMIn + InfRum_DMIn + InfSI_DMIn) * 100    # Line 1039
    return An_DigWSC


def calculate_An_DigrOMa(An_DigrOMaIn: float, Dt_DMIn: float, InfRum_DMIn: float, InfSI_DMIn: float) -> float:
    """
    Apparent digestable residual organic matter, % DM
    """
    An_DigrOMa = An_DigrOMaIn / (Dt_DMIn + InfRum_DMIn + InfSI_DMIn) * 100  # Line 1043
    return An_DigrOMa


def calculate_An_DigrOMt(An_DigrOMtIn: float, Dt_DMIn: float, InfRum_DMIn: float, InfSI_DMIn: float) -> float:
    """
    An_DigrOMt: Truly digestable residual organic matter, % DM
    """
    An_DigrOMt = An_DigrOMtIn / (Dt_DMIn + InfRum_DMIn + InfSI_DMIn) * 100  # Line 1044
    return An_DigrOMt

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
        An_BW: float,
        DMI: float,
        Fe_CP: float, 
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

    nutrient_list = ['CPIn', 'NPNCPIn', 'TPIn', 'FAIn']
    for nutrient in nutrient_list:
        complete_An_data[f'An_{nutrient}'] = diet_data[f'Dt_{nutrient}'] + infusion_data[f'Inf_{nutrient}']

    complete_An_data['An_DMIn_MBW'] = calculate_An_DMIn_MBW(complete_An_data['An_DMIn'],
                                                            complete_An_data['An_MBW'])
    complete_An_data['An_StIn'] = calculate_An_StIn(diet_data['Dt_StIn'],
                                                    infusion_data['InfRum_StIn'],
                                                    infusion_data['InfSI_StIn'])
    complete_An_data['An_St'] = calculate_An_St(complete_An_data['An_StIn'],
                                                DMI,
                                                infusion_data['InfRum_DMIn'],
                                                infusion_data['InfSI_DMIn'])
    complete_An_data['An_rOMIn'] = calculate_An_rOMIn(diet_data['Dt_rOMIn'],
                                                      infusion_data['InfRum_GlcIn'],
                                                      infusion_data['InfRum_AcetIn'],
                                                      infusion_data['InfRum_PropIn'],
                                                      infusion_data['InfRum_ButrIn'],
                                                      infusion_data['InfSI_AcetIn'],
                                                      infusion_data['InfSI_PropIn'],
                                                      infusion_data['InfSI_ButrIn'])
    complete_An_data['An_rOM'] = calculate_An_rOM(complete_An_data['An_rOMIn'],
                                                  DMI,
                                                  infusion_data['InfRum_DMIn'],
                                                  infusion_data['InfSI_DMIn'])
    complete_An_data['An_NDFIn'] = calculate_An_NDFIn(diet_data['Dt_NDFIn'],
                                                      infusion_data['InfRum_NDFIn'],
                                                      infusion_data['InfSI_NDFIn'])
    complete_An_data['An_NDFIn_BW'] = calculate_An_NDFIn_BW(complete_An_data['An_NDFIn'],
                                                            An_BW)
    complete_An_data['An_NDF'] = calculate_An_NDF(complete_An_data['An_NDFIn'],
                                                  DMI,
                                                  infusion_data['InfRum_DMIn'],
                                                  infusion_data['InfSI_DMIn'])
    complete_An_data['An_ADFIn'] = calculate_An_ADFIn(diet_data['Dt_ADFIn'],
                                                      infusion_data['InfRum_ADFIn'],
                                                      infusion_data['InfSI_ADFIn'])
    complete_An_data['An_ADF'] = calculate_An_ADF(complete_An_data['An_ADFIn'],
                                                  DMI,
                                                  infusion_data['InfRum_DMIn'],
                                                  infusion_data['InfSI_DMIn'])
    complete_An_data['An_CPIn_g'] = calculate_An_CPIn_g(complete_An_data['An_CPIn'])
    complete_An_data['An_CP'] = calculate_An_CP(complete_An_data['An_CPIn'],
                                                DMI,
                                                infusion_data['InfRum_DMIn'],
                                                infusion_data['InfSI_DMIn'])
    complete_An_data['An_NIn_g'] = calculate_An_NIn_g(complete_An_data['An_CPIn'])
    complete_An_data['An_FAhydrIn'] = calculate_An_FAhydrIn(diet_data['Dt_FAhydrIn'],
                                                            infusion_data['Inf_FAIn'])
    complete_An_data['An_FA'] = calculate_An_FA(complete_An_data['An_FAIn'],
                                                DMI,
                                                infusion_data['InfRum_DMIn'],
                                                infusion_data['InfSI_DMIn'])
    complete_An_data['An_AshIn'] = calculate_An_AshIn(diet_data['Dt_AshIn'],
                                                      infusion_data['InfRum_AshIn'],
                                                      infusion_data['InfSI_AshIn'])
    complete_An_data['An_Ash'] = calculate_An_Ash(complete_An_data['An_AshIn'],
                                                  DMI,
                                                  infusion_data['InfRum_DMIn'],
                                                  infusion_data['InfSI_DMIn'])
    complete_An_data['An_DigStIn_Base'] = calculate_An_DigStIn_Base(diet_data['Dt_DigStIn_Base'],
                                                                    infusion_data['Inf_StIn'],
                                                                    infusion_data['Inf_ttdcSt'])
    complete_An_data['An_DigWSCIn'] = calculate_An_DigWSCIn(diet_data['Dt_DigWSCIn'],
                                                            infusion_data['InfRum_GlcIn'],
                                                            infusion_data['InfSI_GlcIn'])
    complete_An_data['An_DigrOMtIn'] = calculate_An_DigrOMtIn(diet_data['Dt_DigrOMtIn'],
                                                              infusion_data['InfRum_GlcIn'],
                                                              infusion_data['InfRum_AcetIn'],
                                                              infusion_data['InfRum_PropIn'],
                                                              infusion_data['InfRum_ButrIn'],
                                                              infusion_data['InfSI_GlcIn'],
                                                              infusion_data['InfSI_AcetIn'],
                                                              infusion_data['InfSI_PropIn'],
                                                              infusion_data['InfSI_ButrIn'])
    complete_An_data['An_DigSt'] = calculate_An_DigSt(complete_An_data['An_DigStIn'],
                                                      DMI,
                                                      infusion_data['InfRum_DMIn'],
                                                      infusion_data['InfSI_DMIn'])
    complete_An_data['An_DigWSC'] = calculate_An_DigWSC(complete_An_data['An_DigWSCIn'],
                                                        DMI,
                                                        infusion_data['InfRum_DMIn'],
                                                        infusion_data['InfSI_DMIn'])
    complete_An_data['An_DigrOMa'] = calculate_An_DigrOMa(complete_An_data['An_DigrOMaIn'],
                                                          DMI,
                                                          infusion_data['InfRum_DMIn'],
                                                          infusion_data['InfSI_DMIn'])
    complete_An_data['An_DigrOMt'] = calculate_An_DigrOMt(complete_An_data['An_DigrOMtIn'],
                                                          DMI,
                                                          infusion_data['InfRum_DMIn'],
                                                          infusion_data['InfSI_DMIn'])    
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
