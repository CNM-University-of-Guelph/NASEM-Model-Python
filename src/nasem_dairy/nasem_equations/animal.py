"""Functions for values related to nutrient intakes from infusions and diet.

This module also include various calculations related to protein and energy
efficiency and physiological state.
"""

####################
# Functions for Animal Level Intakes in Wrappers
####################
# An_DMIn_BW is calculated seperately after DMI selection to use in calculate_diet_data
def calculate_An_DMIn_BW(An_BW: float, Dt_DMIn: float) -> float:
    An_DMIn_BW = Dt_DMIn / An_BW  # Line 935
    return An_DMIn_BW


def calculate_An_RDPIn(Dt_RDPIn: float, InfRum_RDPIn: float) -> float:
    An_RDPIn = Dt_RDPIn + InfRum_RDPIn
    return An_RDPIn


def calculate_An_RDP(
    An_RDPIn: float, 
    Dt_DMIn: float, 
    InfRum_DMIn: float
) -> float:
    An_RDP = An_RDPIn / (Dt_DMIn + InfRum_DMIn) * 100
    return An_RDP


def calculate_An_RDPIn_g(An_RDPIn: float) -> float:
    An_RDPIn_g = An_RDPIn * 1000
    return An_RDPIn_g


def calculate_An_DigNDFIn(
    Dt_DigNDFIn: float, 
    InfRum_NDFIn: float, 
    TT_dcNDF: float
) -> float:
    # Line 1063, should consider SI and LI infusions as well, but no predictions
    # of LI NDF digestion available.
    An_DigNDFIn = Dt_DigNDFIn + InfRum_NDFIn * TT_dcNDF / 100
    return An_DigNDFIn


def calculate_An_DENDFIn(An_DigNDFIn: float, coeff_dict: dict) -> float:
    """
    Examples
    --------
    ```
    coeff_dict = {"En_NDF": 0.45}
    
    calculate_An_DENDFIn(
        An_DigNDFIn = 200.0, coeff_dict = coeff_dict
    )
    ```
    """
    An_DENDFIn = An_DigNDFIn * coeff_dict["En_NDF"]  # Line 1353
    return An_DENDFIn


def calculate_An_DigStIn(
    Dt_DigStIn: float, 
    Inf_StIn: float, 
    Inf_ttdcSt: float
) -> float:
    # Line 1033, Glc considered as WSC and thus with rOM
    An_DigStIn = Dt_DigStIn + Inf_StIn * Inf_ttdcSt / 100
    return An_DigStIn


def calculate_An_DEStIn(An_DigStIn: float, coeff_dict: dict) -> float:
    """
    Examples
    --------
    ```
    coeff_dict = {"En_St": 4.23}
    
    calculate_An_DEStIn(
        An_DigStIn = 250.0, coeff_dict = coeff_dict
    )
    ```
    """
    An_DEStIn = An_DigStIn * coeff_dict["En_St"]  # Line 1351
    return An_DEStIn


def calculate_An_DigrOMaIn(
    Dt_DigrOMaIn: float, 
    InfRum_GlcIn: float, 
    InfRum_AcetIn: float,
    InfRum_PropIn: float, 
    InfRum_ButrIn: float, 
    InfSI_GlcIn: float,
    InfSI_AcetIn: float, 
    InfSI_PropIn: float, 
    InfSI_ButrIn: float
) -> float:
    An_DigrOMaIn = (Dt_DigrOMaIn + InfRum_GlcIn + InfRum_AcetIn +
                    InfRum_PropIn + InfRum_ButrIn + InfSI_GlcIn + 
                    InfSI_AcetIn + InfSI_PropIn + InfSI_ButrIn) # Line 1023-1024
    return An_DigrOMaIn


def calculate_An_DErOMIn(An_DigrOMaIn: float, coeff_dict: dict) -> float:
    """
    Examples
    --------
    ```
    coeff_dict = {"En_rOM": 4.0}
    
    calculate_An_DErOMIn(
        An_DigrOMaIn = 300.0, coeff_dict = coeff_dict
    )
    ```
    """
    An_DErOMIn = An_DigrOMaIn * coeff_dict["En_rOM"]  # Line 1351
    return An_DErOMIn


def calculate_An_idRUPIn(
    Dt_idRUPIn: float, 
    InfRum_idRUPIn: float, 
    InfSI_idTPIn: float
) -> float:
    # Line 1099, SI infusions considered here
    An_idRUPIn = Dt_idRUPIn + InfRum_idRUPIn + InfSI_idTPIn
    return An_idRUPIn


def calculate_An_RUPIn(Dt_RUPIn: float, InfRum_RUPIn: float) -> float:
    An_RUPIn = Dt_RUPIn + InfRum_RUPIn
    return An_RUPIn


def calculate_An_DMIn(Dt_DMIn: float, Inf_DMIn: float) -> float:
    An_DMIn = Dt_DMIn + Inf_DMIn
    return An_DMIn


def calculate_An_CPIn(Dt_CPIn: float, Inf_CPIn: float) -> float:
    An_CPIn = Dt_CPIn + Inf_CPIn  # Line 947
    return An_CPIn


def calculate_An_DigNDF(
    An_DigNDFIn: float, 
    Dt_DMIn: float, 
    InfRum_DMIn: float, 
    InfSI_DMIn: float
) -> float:
    # Line 1066, should add LI infusions
    An_DigNDF = An_DigNDFIn / (Dt_DMIn + InfRum_DMIn + InfSI_DMIn) * 100
    return An_DigNDF


def calculate_An_GasEOut_Dry(
    Dt_DMIn: float, 
    Dt_FAIn: float, 
    InfRum_FAIn: float, 
    InfRum_DMIn: float,
    An_GEIn: float
) -> float:
    An_GasEOut_Dry = (0.69 + 0.053 * An_GEIn - 0.07 * (Dt_FAIn + InfRum_FAIn) / 
                      (Dt_DMIn + InfRum_DMIn) * 100)   # Line 1407, Dry Cows
    return An_GasEOut_Dry


def calculate_An_GasEOut_Lact(
    Dt_DMIn: float, 
    Dt_FAIn: float, 
    InfRum_FAIn: float, 
    InfRum_DMIn: float,
    An_DigNDF: float
) -> float:
    An_GasEOut_Lact = (0.294 * (Dt_DMIn + InfRum_DMIn) - 
                       (0.347 * (Dt_FAIn + InfRum_FAIn) / 
                        (Dt_DMIn + InfRum_DMIn)) * 100 + 0.0409 * An_DigNDF)
    # Line 1404-1405
    return An_GasEOut_Lact


def calculate_An_GasEOut_Heif(An_GEIn: float, An_NDF: float) -> float:
    An_GasEOut_Heif = -0.038 + 0.051 * An_GEIn + 0.0091 * An_NDF  
    # Line 1406, Heifers/Bulls
    return An_GasEOut_Heif


def calculate_An_GasEOut(
    An_StatePhys: str, 
    Monensin_eqn: int, 
    An_GasEOut_Dry: float,
    An_GasEOut_Lact: float, 
    An_GasEOut_Heif: float
) -> float:
    if An_StatePhys == "Dry Cow":
        An_GasEOut = An_GasEOut_Dry
    elif An_StatePhys == "Calf":
        An_GasEOut = 0  # Line 1408, An_GasEOut_Clf = 0
    elif An_StatePhys == "Lactating Cow":
        An_GasEOut = An_GasEOut_Lact
    else:
        An_GasEOut = An_GasEOut_Heif

    if Monensin_eqn == 1:
        An_GasEOut = An_GasEOut * 0.95
    else:
        An_GasEOut = An_GasEOut

    return An_GasEOut


def calculate_An_DigCPaIn(
    An_CPIn: float, 
    InfArt_CPIn: float, 
    Fe_CP: float
) -> float:
    An_DigCPaIn = An_CPIn - InfArt_CPIn - Fe_CP  # apparent total tract
    return An_DigCPaIn


def calculate_An_DECPIn(An_DigCPaIn: float, coeff_dict: dict) -> float:
    """
    Examples
    --------
    ```
    coeff_dict = {"En_CP": 5.65}
    
    calculate_An_DECPIn(
        An_DigCPaIn = 100.0, coeff_dict = coeff_dict
    )
    ```
    """
    An_DECPIn = An_DigCPaIn * coeff_dict["En_CP"]
    return An_DECPIn


def calculate_An_DENPNCPIn(Dt_NPNCPIn: float, coeff_dict: dict) -> float:
    """
    Examples
    --------
    ```
    coeff_dict = {"dcNPNCP": 100, "En_NPNCP": 0.89}
    
    calculate_An_DENPNCPIn(
        Dt_NPNCPIn = 50.0, coeff_dict = coeff_dict
    )
    ```
    """
    An_DENPNCPIn = (Dt_NPNCPIn * coeff_dict["dcNPNCP"] / 
                    100 * coeff_dict["En_NPNCP"])
    return An_DENPNCPIn


def calculate_An_DETPIn(
    An_DECPIn: float, 
    An_DENPNCPIn: float, 
    coeff_dict: dict
) -> float:
    """
    Examples
    --------
    ```
    coeff_dict = {"En_NPNCP": 0.89, "En_CP": 5.65}
    
    calculate_An_DETPIn(
        An_DECPIn = 100.0, An_DENPNCPIn = 40.0, coeff_dict = coeff_dict
    )
    ```
    """    
    # Line 1355, Caution! DigTPaIn not clean so subtracted DE for CP equiv of
    # NPN to correct. Not a true DE_TP.
    An_DETPIn = (An_DECPIn - An_DENPNCPIn / 
                 coeff_dict["En_NPNCP"] * coeff_dict["En_CP"])
    return An_DETPIn


def calculate_An_DigFAIn(Dt_DigFAIn: float, Inf_DigFAIn: float) -> float:
    An_DigFAIn = Dt_DigFAIn + Inf_DigFAIn  # Line 1308
    return An_DigFAIn


def calculate_An_DEFAIn(An_DigFAIn: float, coeff_dict: dict) -> float:
    """
    Examples
    --------
    ```
    coeff_dict = {"En_FA": 9.4}
    
    calculate_An_DEFAIn(
        An_DigFAIn = 150.0, coeff_dict = coeff_dict
    )
    ```
    """
    An_DEFAIn = An_DigFAIn * coeff_dict["En_FA"]  # Line 1361
    return An_DEFAIn


def calculate_An_DEIn(
    An_StatePhys: str, 
    An_DENDFIn: float, 
    An_DEStIn: float, 
    An_DErOMIn: float,
    An_DETPIn: float, 
    An_DENPNCPIn: float, 
    An_DEFAIn: float, 
    Inf_DEAcetIn: float,
    Inf_DEPropIn: float, 
    Inf_DEButrIn: float, 
    Dt_DMIn_ClfLiq: float, 
    Dt_DEIn: float,
    Monensin_eqn: int
) -> float:
    An_DEIn = (An_DENDFIn + An_DEStIn + An_DErOMIn + An_DETPIn + An_DENPNCPIn +
               An_DEFAIn + Inf_DEAcetIn + Inf_DEPropIn + Inf_DEButrIn)
    # Infusion DE not considered for milk-fed calves
    condition = (An_StatePhys == "Calf") and (Dt_DMIn_ClfLiq > 0)   
    An_DEIn = Dt_DEIn if condition else An_DEIn     
    An_DEIn = An_DEIn * 1.02 if Monensin_eqn == 1 else An_DEIn
    return An_DEIn


def calculate_An_DEInp(
    An_DEIn: float, 
    An_DETPIn: float, 
    An_DENPNCPIn: float
) -> float:
    # Line 1385, Create a nonprotein DEIn for milk protein predictions.
    An_DEInp = An_DEIn - An_DETPIn - An_DENPNCPIn
    return An_DEInp


def calculate_An_GutFill_BW(
    An_BW: float, 
    An_BW_mature: float, 
    An_StatePhys: str, 
    An_Parity_rl: int,
    Dt_DMIn_ClfLiq: float, 
    Dt_DMIn_ClfStrt: float, 
    coeff_dict: dict
) -> float:
    """
    see page 34 for comments, gut fill is default 0.18 for cows
    Weaned calf == heifer, which is based on equations 11-1a/b using 85% (inverse of 0.15)
    Comments in book suggest this is not always a suitable assumption (that gut fill is 15% of BW), 
    consider making this a coeff that can be changed in coeff_dict?
    
    Examples
    --------
    ```
    coeff_dict = {"An_GutFill_BWmature": 0.18}
    
    calculate_An_GutFill_BW(
        An_BW = 500.0, An_BW_mature = 600.0, An_StatePhys = "Lactating Cow", 
        An_Parity_rl = 2, Dt_DMIn_ClfLiq = 0.0, Dt_DMIn_ClfStrt = 0.0, 
        coeff_dict = coeff_dict
    )
    ```
    """
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
        An_GutFill_BW = coeff_dict["An_GutFill_BWmature"]  # Line 2410, cow
    elif An_StatePhys == "Heifer":
        An_GutFill_BW = 0.15    # Line 2408 
    else:
        An_GutFill_BW = An_GutFill_BW
    return An_GutFill_BW


def calculate_An_BWnp(An_BW: float, GrUter_Wt: float) -> float:
    """
    Equation 20-230
    """
    An_BWnp = An_BW - GrUter_Wt  # Line 2396, Non-pregnant BW
    return An_BWnp


def calculate_An_GutFill_Wt(An_GutFill_BW: float, An_BWnp: float) -> float:
    An_GutFill_Wt = An_GutFill_BW * An_BWnp  # Line 2413
    return An_GutFill_Wt


def calculate_An_BW_empty(An_BW: float, An_GutFill_Wt: float) -> float:
    """
    Equation 20-242
    """
    An_BW_empty = An_BW - An_GutFill_Wt  # Line 2414
    return An_BW_empty


def calculate_An_REgain_Calf(
    Body_Gain_empty: float, 
    An_BW_empty: float
) -> float:
    An_REgain_Calf = Body_Gain_empty**1.10 * An_BW_empty**0.205  
    # Line 2445, calf RE gain needed here for fat gain, mcal/d
    return An_REgain_Calf


def calculate_An_MEIn_approx(
    An_DEInp: float, 
    An_DENPNCPIn: float,
    An_DigTPaIn: float, 
    Body_NPgain: float,
    An_GasEOut: float, 
    coeff_dict: dict
) -> float:
    """
    An_MEIn_approx: Approximate ME intake, see note:
        Adjust heifer MPuse target if the MP:ME ratio is below optimum for development.
        Can"t calculate ME before MP, thus estimated ME in the MP:ME ratio using the target NPgain. Will be incorrect
        if the animal is lactating or gestating.
    This is used by Equation 11-11
    """
    An_MEIn_approx = (An_DEInp + An_DENPNCPIn + (An_DigTPaIn - Body_NPgain) * 4.0 
                      + Body_NPgain * coeff_dict["En_CP"] - An_GasEOut)
    # Line 2685
    return An_MEIn_approx


def calculate_An_MEIn(
    An_StatePhys: str, 
    An_BW: float, 
    An_DEIn: float, 
    An_GasEOut: float, 
    Ur_DEout: float,
    Dt_DMIn_ClfLiq: float, 
    Dt_DEIn_base_ClfLiq: float, 
    Dt_DEIn_base_ClfDry: float,
    RumDevDisc_Clf: float
) -> float:
    condition = ((An_StatePhys == "Calf") 
                 and (Dt_DMIn_ClfLiq > 0.015 * An_BW) 
                 and (RumDevDisc_Clf > 0))
    K_DE_ME_ClfDry = 0.93 * 0.9 if condition else 0.93 # Line 2755   
    
    An_MEIn = An_DEIn - An_GasEOut - Ur_DEout  # Line 2753
    An_MEIn = (Dt_DEIn_base_ClfLiq * 0.96 + Dt_DEIn_base_ClfDry * K_DE_ME_ClfDry
               if (An_StatePhys == "Calf") and (Dt_DMIn_ClfLiq > 0) 
               else An_MEIn) 
    return An_MEIn


def calculate_An_NEIn(An_MEIn: float) -> float:
    An_NEIn = An_MEIn * 0.66  # Line 2762
    return An_NEIn


def calculate_An_NE(An_NEIn: float, An_DMIn: float) -> float:
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


def calculate_An_DigTPaIn(
    An_TPIn: float, 
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


def calculate_An_StIn(
    Dt_StIn: float, 
    InfRum_StIn: float,
    InfSI_StIn: float
) -> float:
    """
    An_StIn: Dietary + infused starch intake, kg
    """
    An_StIn = Dt_StIn + InfRum_StIn + InfSI_StIn  # Line 937
    return An_StIn


def calculate_An_St(
    An_StIn: float, 
    Dt_DMIn: float, 
    InfRum_DMIn: float,
    InfSI_DMIn: float
) -> float:
    """
    An_St: Starch % of diet + infusions
    """
    An_St = An_StIn / (Dt_DMIn + InfRum_DMIn + InfSI_DMIn) * 100  # Line 938
    return An_St


def calculate_An_rOMIn(
    Dt_rOMIn: float, 
    InfRum_GlcIn: float,
    InfRum_AcetIn: float, 
    InfRum_PropIn: float,
    InfRum_ButrIn: float, 
    InfSI_AcetIn: float,
    InfSI_PropIn: float, 
    InfSI_ButrIn: float
) -> float:
    """
    An_rOMIn: Residual organic matter intake from diet + infusions, kg
    """
    An_rOMIn = (Dt_rOMIn + InfRum_GlcIn + InfRum_AcetIn + InfRum_PropIn +
                InfRum_ButrIn + InfSI_AcetIn + InfSI_PropIn + InfSI_ButrIn)   
    # Line 939-940
    return An_rOMIn


def calculate_An_rOM(
    An_rOMIn: float, 
    Dt_DMIn: float, 
    InfRum_DMIn: float,
    InfSI_DMIn: float
) -> float:
    """
    An_rOM: Residual organic matter % of diet + infusions
    """
    An_rOM = An_rOMIn / (Dt_DMIn + InfRum_DMIn + InfSI_DMIn) * 100  # Line 941
    return An_rOM


def calculate_An_NDFIn(
    Dt_NDFIn: float, 
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


def calculate_An_NDF(
    An_NDFIn: float, 
    Dt_DMIn: float, 
    InfRum_DMIn: float,
    InfSI_DMIn: float
) -> float:
    """
    An_NDF: NDF % of diet + infusion intake
    """
    An_NDF = An_NDFIn / (Dt_DMIn + InfRum_DMIn + InfSI_DMIn) * 100  # Line 944
    return An_NDF


def calculate_An_ADFIn(
    Dt_ADFIn: float, 
    InfRum_ADFIn: float,
    InfSI_ADFIn: float
) -> float:
    """
    An_ADFIn: ADF intake from diet + infusions, kg
    """
    An_ADFIn = (Dt_ADFIn + InfRum_ADFIn + InfSI_ADFIn)  # Line 945
    return An_ADFIn


def calculate_An_ADF(
    An_ADFIn: float, 
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


def calculate_An_CP(
    An_CPIn: float, 
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


def calculate_An_FA(
    An_FAIn: float, 
    Dt_DMIn: float, 
    InfRum_DMIn: float,
    InfSI_DMIn: float
) -> float:
    """
    An_FA: Fatty acid % of diet + infusions
    """
    An_FA = An_FAIn / (Dt_DMIn + InfRum_DMIn + InfSI_DMIn) * 100  # Line 955
    return An_FA


def calculate_An_AshIn(
    Dt_AshIn: float, 
    InfRum_AshIn: float,
    InfSI_AshIn: float
) -> float:
    """
    An_AshIn: Ash intake from diet + infusions, kg
    """
    An_AshIn = (Dt_AshIn + InfRum_AshIn + InfSI_AshIn)  # Line 956
    return An_AshIn


def calculate_An_Ash(
    An_AshIn: float, 
    Dt_DMIn: float, 
    InfRum_DMIn: float,
    InfSI_DMIn: float
) -> float:
    """
    An_Ash: Ash % of diet + infusions intake
    """
    An_Ash = An_AshIn / (Dt_DMIn + InfRum_DMIn + InfSI_DMIn) * 100  # Line 957
    return An_Ash


def calculate_An_DigStIn_Base(
    Dt_DigStIn_Base: float, 
    Inf_StIn: float,
    Inf_ttdcSt: float
) -> float:
    """
    An_DigStIn_Base: 
    """
    An_DigStIn_Base = Dt_DigStIn_Base + Inf_StIn * Inf_ttdcSt / 100  
    # Glc considered as WSC and thus with rOM, Line 1017
    return An_DigStIn_Base


def calculate_An_DigWSCIn(
    Dt_DigWSCIn: float, 
    InfRum_GlcIn: float,
    InfSI_GlcIn: float
) -> float:
    """
    Digestable water soluble carbohydrate intake, kg/d
    """
    An_DigWSCIn = Dt_DigWSCIn + InfRum_GlcIn + InfSI_GlcIn  # Line 1022
    return An_DigWSCIn


def calculate_An_DigrOMtIn(
    Dt_DigrOMtIn: float, 
    InfRum_GlcIn: float,
    InfRum_AcetIn: float, 
    InfRum_PropIn: float,
    InfRum_ButrIn: float, 
    InfSI_GlcIn: float,
    InfSI_AcetIn: float, 
    InfSI_PropIn: float,
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


def calculate_An_DigSt(
    An_DigStIn: float, 
    Dt_DMIn: float, 
    InfRum_DMIn: float,
    InfSI_DMIn: float
) -> float:
    """
    An_DigSt: Digestable starch intake, kg/d
    """
    An_DigSt = An_DigStIn / (Dt_DMIn + InfRum_DMIn + InfSI_DMIn) * 100 # Line 1037
    return An_DigSt


def calculate_An_DigWSC(
    An_DigWSCIn: float, 
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


def calculate_An_DigrOMa(
    An_DigrOMaIn: float, 
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


def calculate_An_DigrOMt(
    An_DigrOMtIn: float, 
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


def calculate_An_DigNDFIn_Base(
    Dt_NDFIn: float, 
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


def calculate_An_RUP(
    An_RUPIn: float, 
    Dt_DMIn: float,
    InfRum_DMIn: float
) -> float:
    """
    An_RUP: Rumen undegradable protein from diet + infusions, % DM
    """
    An_RUP = An_RUPIn / (Dt_DMIn + InfRum_DMIn) * 100  # Line 1096
    return An_RUP


def calculate_An_RUP_CP(
    An_RUPIn: float, 
    Dt_CPIn: float,
    InfRum_CPIn: float
) -> float:
    """
    An_RUP_CP: Rumen undegradable protein % of crude protein
    """
    An_RUP_CP = An_RUPIn / (Dt_CPIn + InfRum_CPIn) * 100  # Line 1097
    return An_RUP_CP


def calculate_An_idRUCPIn(
    Dt_idRUPIn: float, 
    InfRum_idRUPIn: float,
    InfSI_idCPIn: float
) -> float:
    """
    An_idRUCPIn: Intestinally digested rumen undegradable crude protein intake, kg/d
    """
    An_idRUCPIn = Dt_idRUPIn + InfRum_idRUPIn + InfSI_idCPIn  # RUP + infused idCP, Line 1099
    return An_idRUCPIn


def calculate_An_idRUP(
    An_idRUPIn: float, 
    Dt_DMIn: float, 
    InfRum_DMIn: float,
    InfSI_DMIn: float
) -> float:
    """
    An_idRUP: Intestinally digestable rumen undegradable protein, % DM
    """
    An_idRUP = An_idRUPIn / (Dt_DMIn + InfRum_DMIn + InfSI_DMIn)  # Line 1100
    return An_idRUP


def calculate_An_RDTPIn(
    Dt_RDTPIn: float, 
    InfRum_RDPIn: float,
    InfRum_NPNCPIn: float, 
    coeff_dict: dict
) -> float:
    """
    An_RDTPIn: Rumen degradable true protein intake, kg/d
    
    Examples
    --------
    ```
    coeff_dict = {"dcNPNCP": 100}
    
    calculate_An_RDTPIn(
        Dt_RDTPIn = 200.0, InfRum_RDPIn = 150.0, InfRum_NPNCPIn = 30.0, 
        coeff_dict = coeff_dict
    )
    ```
    """
    An_RDTPIn = (Dt_RDTPIn + 
                 (InfRum_RDPIn - InfRum_NPNCPIn * coeff_dict["dcNPNCP"] / 100))  
    # Line 1107
    return An_RDTPIn


def calculate_An_RDP_CP(
    An_RDPIn: float, 
    Dt_CPIn: float,
    InfRum_CPIn: float
) -> float:
    """
    An_RDP_CP: Rumen degradable protein % of crude protein
    """
    An_RDP_CP = An_RDPIn / (Dt_CPIn + InfRum_CPIn) * 100  # Line 1109
    return An_RDP_CP


def calculate_An_DigCPa(
    An_DigCPaIn: float, 
    An_DMIn: float,
    InfArt_DMIn: float
) -> float:
    """
    An_DigCPa: Apparent total tract digested CP, % DM
    """
    An_DigCPa = An_DigCPaIn / (An_DMIn - InfArt_DMIn) * 100 # % of DM, Line 1222
    return An_DigCPa


def calculate_TT_dcAnCPa(
    An_DigCPaIn: float, 
    An_CPIn: float,
    InfArt_CPIn: float
) -> float:
    """
    TT_dcAnCPa: Digestability coefficient apparent total tract CP, % CP
    """
    TT_dcAnCPa = An_DigCPaIn / (An_CPIn - InfArt_CPIn) * 100 # % of CP, Line 1223
    return TT_dcAnCPa


def calculate_An_DigCPtIn(
    An_StatePhys: str, 
    Dt_DigCPtIn: float,
    Inf_idCPIn: float, 
    An_RDPIn: float,
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


def calculate_An_DigTPtIn(
    An_RDTPIn: float, 
    Fe_MiTP: float, 
    An_idRUPIn: float,
    Fe_NPend: float
) -> float:
    """
    An_DigTPtIn: True total tract digested true protein intake, kg/d
    """
    An_DigTPtIn = An_RDTPIn - Fe_MiTP + An_idRUPIn - Fe_NPend  # Line 1228
    return An_DigTPtIn


def calculate_An_DigCPt(
    An_DigCPtIn: float, 
    An_DMIn: float,
    InfArt_DMIn: float
) -> float:
    """
    An_DigCPt: True total tract digested CP, % DMI
    """
    An_DigCPt = An_DigCPtIn / (An_DMIn - InfArt_DMIn) * 100 # % of DMIn, Line 1230
    return An_DigCPt


def calculate_An_DigTPt(
    An_DigTPtIn: float, 
    An_DMIn: float,
    InfArt_DMIn: float
) -> float:
    """
    An_DigTPt: True digested total tract true protein, % DMI
    """
    An_DigTPt = An_DigTPtIn / (An_DMIn - InfArt_DMIn) * 100 # % of DMIn, Line 1231
    return An_DigTPt


def calculate_TT_dcAnCPt(
    An_DigCPtIn: float, 
    An_CPIn: float,
    InfArt_CPIn: float
) -> float:
    """
    TT_dcAnCPt: Digestability coefficient true total tract CP intake, % CP
    """
    TT_dcAnCPt = An_DigCPtIn / (An_CPIn - InfArt_CPIn) * 100 # % of CP, Line 1232
    return TT_dcAnCPt


def calculate_TT_dcAnTPt(
    An_DigTPtIn: float, 
    An_TPIn: float, 
    InfArt_CPIn: float, 
    InfRum_NPNCPIn: float, 
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
    SI_dcAnRUP: ?, doesn"t get used anywhere in the model, reported in table
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


def calculate_An_DigFA(
    An_DigFAIn: float, 
    Dt_DMIn: float, 
    InfRum_DMIn: float,
    InfSI_DMIn: float
) -> float:
    """
    An_DigFA: Digestable FA, dietary and infusions, % of DMI
    """
    An_DigFA = An_DigFAIn / (Dt_DMIn + InfRum_DMIn + InfSI_DMIn) * 100 # Line 1309
    return An_DigFA


def calculate_TT_dcAnFA(
    Dt_DigFAIn: float, 
    Inf_DigFAIn: float, 
    Dt_FAIn: float,
    Inf_FAIn: float
) -> float:
    """
    TT_dcAnFA: Digestability coefficient for total tract FA
    """
    TT_dcAnFA = (Dt_DigFAIn + Inf_DigFAIn) / (Dt_FAIn + Inf_FAIn) * 100  
    # this should be just gut infusions, but don"t have those calculated as 
    # ruminal and SI DC will not be the same, Line 1312
    return TT_dcAnFA


def calculate_An_OMIn(Dt_OMIn: float, Inf_OMIn: float) -> float:
    """
    An_OMIn: Organic matter intake, dietary and infusions (kg/d)
    """
    An_OMIn = Dt_OMIn + Inf_OMIn  # Line 1317
    return An_OMIn


def calculate_An_DigOMaIn_Base(
    An_DigNDFIn_Base: float, 
    An_DigStIn_Base: float,
    An_DigFAIn: float, 
    An_DigrOMaIn: float,
    An_DigCPaIn: float
) -> float:
    """
    An_DigOMaIn_Base: Base apparent digested organic matter intake? (kg/d) 
    """
    An_DigOMaIn_Base = (An_DigNDFIn_Base + An_DigStIn_Base + An_DigFAIn + 
                        An_DigrOMaIn + An_DigCPaIn) # Line 1318
    return An_DigOMaIn_Base


def calculate_An_DigOMtIn_Base(
    An_DigNDFIn_Base: float, 
    An_DigStIn_Base: float,
    An_DigFAIn: float, 
    An_DigrOMtIn: float,
    An_DigCPtIn: float
) -> float:
    """
    An_DigOMtIn_Base: Base true digested organic matter intake? (kg/d)
    """
    An_DigOMtIn_Base = (An_DigNDFIn_Base + An_DigStIn_Base + An_DigFAIn + 
                        An_DigrOMtIn + An_DigCPtIn) # Line 1319
    return An_DigOMtIn_Base


def calculate_An_DigOMaIn(
    An_DigNDFIn: float, 
    An_DigStIn: float,
    An_DigFAIn: float, 
    An_DigrOMaIn: float,
    An_DigCPaIn: float
) -> float:
    """
    An_DigOMaIn: Apparent digested organic matter intake (kg/d)
    """
    An_DigOMaIn = (An_DigNDFIn + An_DigStIn + An_DigFAIn + 
                   An_DigrOMaIn + An_DigCPaIn)  # Line 1322
    return An_DigOMaIn


def calculate_An_DigOMtIn(
    An_DigNDFIn: float, 
    An_DigStIn: float,
    An_DigFAIn: float, 
    An_DigrOMtIn: float,
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


def calculate_An_DigOMa(
    An_DigOMaIn: float, 
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


def calculate_An_DigOMt(
    An_DigOMtIn: float, 
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


def calculate_An_GEIn(
    Dt_GEIn: float, 
    Inf_NDFIn: float, 
    Inf_StIn: float,
    Inf_FAIn: float, 
    Inf_TPIn: float, 
    Inf_NPNCPIn: float,
    Inf_AcetIn: float, 
    Inf_PropIn: float, 
    Inf_ButrIn: float,
    coeff_dict: dict
) -> float:
    """
    An_GEIn: Gross energy intake (Mcal/d)

    Examples
    --------
    ```
    coeff_dict = {
        "En_NDF": 0.45, "En_St": 0.50, "En_FA": 0.85, "En_CP": 0.75, 
        "En_NPNCP": 0.55, "En_Acet": 0.90, "En_Prop": 1.05, "En_Butr": 1.10
    }
    
    calculate_An_GEIn(
        Dt_GEIn = 100.0, Inf_NDFIn = 20.0, Inf_StIn = 15.0, Inf_FAIn = 10.0, 
        Inf_TPIn = 25.0, Inf_NPNCPIn = 5.0, Inf_AcetIn = 8.0, Inf_PropIn = 12.0, 
        Inf_ButrIn = 6.0, coeff_dict = coeff_dict
    )
    ```
    """
    An_GEIn = (Dt_GEIn + 
               Inf_NDFIn * coeff_dict["En_NDF"] + 
               Inf_StIn * coeff_dict["En_St"] + 
               Inf_FAIn * coeff_dict["En_FA"] + 
               Inf_TPIn * coeff_dict["En_CP"] + 
               Inf_NPNCPIn * coeff_dict["En_NPNCP"] + 
               Inf_AcetIn * coeff_dict["En_Acet"] + 
               Inf_PropIn * coeff_dict["En_Prop"] + 
               Inf_ButrIn * coeff_dict["En_Butr"]) # Line 1338-1339
    return An_GEIn


def calculate_An_GE(An_GEIn: float, An_DMIn: float) -> float:
    """
    An_GE: Gross energy intake, including infusions (Mcal/kg diet)
    """
    An_GE = An_GEIn / An_DMIn  # included all infusions in DMIn, Line 1341
    return An_GE


def calculate_An_DERDTPIn(
    An_RDTPIn: float, 
    Fe_DEMiCPend: float,
    Fe_DERDPend: float, 
    coeff_dict: dict
) -> float:
    """
    An_DERDTPIn: Digestable energy in rumen degradable true protein (Mcal/d)

    Examples
    --------
    ```
    coeff_dict = {"En_CP": 5.65}
    
    calculate_An_DERDTPIn(
        An_RDTPIn = 100.0, Fe_DEMiCPend = 10.0, Fe_DERDPend = 5.0, 
        coeff_dict = coeff_dict
    )
    ```
    """
    An_DERDTPIn = An_RDTPIn * coeff_dict["En_CP"] - Fe_DEMiCPend - Fe_DERDPend  
    # Line 1359
    return An_DERDTPIn


def calculate_An_DEidRUPIn(
    An_idRUPIn: float, 
    Fe_DERUPend: float,
    coeff_dict: dict
) -> float:
    """
    An_DEidRUPIn: Digestable energy in intestinally digested RUP (Mcal/d)
    
    Examples
    --------
    ```
    coeff_dict = {"En_CP": 5.65}
    
    calculate_An_DEidRUPIn(
        An_idRUPIn = 80.0, Fe_DERUPend = 15.0, coeff_dict = coeff_dict
    )
    ```
    """
    An_DEidRUPIn = An_idRUPIn * coeff_dict["En_CP"] - Fe_DERUPend  # Line 1360
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


def calculate_An_ME_ClfDry(
    An_MEIn_ClfDry: float, 
    An_DMIn: float, 
    Dt_DMIn_ClfLiq: float
) -> float:
    An_ME_ClfDry = An_MEIn_ClfDry / (An_DMIn - Dt_DMIn_ClfLiq)
    return An_ME_ClfDry


def calculate_An_NE_ClfDry(An_ME_ClfDry: float) -> float:
    An_NE_ClfDry = (1.1104 * An_ME_ClfDry - 0.0946 * An_ME_ClfDry**2 + 
                    0.0065 * An_ME_ClfDry**3 - 0.7783)
    return An_NE_ClfDry


def calculate_An_IdArgIn(Dt_IdArgIn: float, Inf_IdArgIn: float) -> float:
    An_IdArgIn = Dt_IdArgIn + Inf_IdArgIn
    return An_IdArgIn


def calculate_An_IdHisIn(Dt_IdHisIn: float, Inf_IdHisIn: float) -> float:
    An_IdHisIn = Dt_IdHisIn + Inf_IdHisIn
    return An_IdHisIn


def calculate_An_IdIleIn(Dt_IdIleIn: float, Inf_IdIleIn: float) -> float:
    An_IdIleIn = Dt_IdIleIn + Inf_IdIleIn
    return An_IdIleIn


def calculate_An_IdLeuIn(Dt_IdLeuIn: float, Inf_IdLeuIn: float) -> float:
    An_IdLeuIn = Dt_IdLeuIn + Inf_IdLeuIn
    return An_IdLeuIn


def calculate_An_IdLysIn(Dt_IdLysIn: float, Inf_IdLysIn: float) -> float:
    An_IdLysIn = Dt_IdLysIn + Inf_IdLysIn
    return An_IdLysIn


def calculate_An_IdMetIn(Dt_IdMetIn: float, Inf_IdMetIn: float) -> float:
    An_IdMetIn = Dt_IdMetIn + Inf_IdMetIn
    return An_IdMetIn


def calculate_An_IdPheIn(Dt_IdPheIn: float, Inf_IdPheIn: float) -> float:
    An_IdPheIn = Dt_IdPheIn + Inf_IdPheIn
    return An_IdPheIn


def calculate_An_IdThrIn(Dt_IdThrIn: float, Inf_IdThrIn: float) -> float:
    An_IdThrIn = Dt_IdThrIn + Inf_IdThrIn
    return An_IdThrIn


def calculate_An_IdTrpIn(Dt_IdTrpIn: float, Inf_IdTrpIn: float) -> float:
    An_IdTrpIn = Dt_IdTrpIn + Inf_IdTrpIn
    return An_IdTrpIn


def calculate_An_IdValIn(Dt_IdValIn: float, Inf_IdValIn: float) -> float:
    An_IdValIn = Dt_IdValIn + Inf_IdValIn
    return An_IdValIn


def calculate_An_NPNCPIn(Dt_NPNCPIn: float, Inf_NPNCPIn: float) -> float:
    An_NPNCPIn = Dt_NPNCPIn + Inf_NPNCPIn
    return An_NPNCPIn


def calculate_An_FAIn(Dt_FAIn: float, Inf_FAIn: float) -> float:
    An_FAIn = Dt_FAIn + Inf_FAIn
    return An_FAIn


####################
# Animal Warpper Functions
####################
def calculate_an_data(
    an_data: dict,
    diet_data: dict, 
    infusion_data: dict,
    Monensin_eqn: int, 
    GrUter_Wt: float, 
    Dt_DMIn: float,
    Fe_CP: float,
    An_StatePhys: str,
    An_BW: float,
    An_BW_mature: float,
    An_Parity_rl: int,
    Fe_MiTP: float,
    Fe_NPend: float,
    Fe_DEMiCPend: float,
    Fe_DERDPend: float,
    Fe_DERUPend: float,
    Du_idMiCP: float,
    coeff_dict: dict
) -> dict:
    # Could use a better name, an_data for now
    an_data["An_RDPIn"] = calculate_An_RDPIn(
        diet_data["Dt_RDPIn"], infusion_data["InfRum_RDPIn"]
        )
    an_data["An_RDP"] = calculate_An_RDP(
        an_data["An_RDPIn"], Dt_DMIn, infusion_data["InfRum_DMIn"]
        )
    an_data["An_RDPIn_g"] = calculate_An_RDPIn_g(an_data["An_RDPIn"])
    an_data["An_NDFIn"] = calculate_An_NDFIn(
        diet_data["Dt_NDFIn"], infusion_data["InfRum_NDFIn"], 
        infusion_data["InfSI_NDFIn"]
        )
    an_data["An_NDF"] = calculate_An_NDF(
        an_data["An_NDFIn"], Dt_DMIn, infusion_data["InfRum_DMIn"], 
        infusion_data["InfSI_DMIn"]
        )
    an_data["An_DigNDFIn"] = calculate_An_DigNDFIn(
        diet_data["Dt_DigNDFIn"], infusion_data["InfRum_NDFIn"],
        diet_data["TT_dcNDF"])
    an_data["An_DENDFIn"] = calculate_An_DENDFIn(
        an_data["An_DigNDFIn"], coeff_dict
        )
    an_data["An_DigStIn"] = calculate_An_DigStIn(
        diet_data["Dt_DigStIn"], infusion_data["Inf_StIn"], 
        infusion_data["Inf_ttdcSt"]
        )
    an_data["An_DEStIn"] = calculate_An_DEStIn(
        an_data["An_DigStIn"], coeff_dict
        )
    an_data["An_DigrOMaIn"] = calculate_An_DigrOMaIn(
        diet_data["Dt_DigrOMaIn"], infusion_data["InfRum_GlcIn"],
        infusion_data["InfRum_AcetIn"], infusion_data["InfRum_PropIn"],
        infusion_data["InfRum_ButrIn"], infusion_data["InfSI_GlcIn"],
        infusion_data["InfSI_AcetIn"], infusion_data["InfSI_PropIn"],
        infusion_data["InfSI_ButrIn"]
        )
    an_data["An_DErOMIn"] = calculate_An_DErOMIn(
        an_data["An_DigrOMaIn"], coeff_dict
        )
    an_data["An_idRUPIn"] = calculate_An_idRUPIn(
        diet_data["Dt_idRUPIn"], infusion_data["InfRum_idRUPIn"],
        infusion_data["InfSI_idTPIn"]
        )
    an_data["An_RUPIn"] = calculate_An_RUPIn(
        diet_data["Dt_RUPIn"], infusion_data["InfRum_RUPIn"]
        )
    an_data["An_DMIn"] = calculate_An_DMIn(
        Dt_DMIn, infusion_data["Inf_DMIn"]
        )
    an_data["An_CPIn"] = calculate_An_CPIn(
        diet_data["Dt_CPIn"], infusion_data["Inf_CPIn"]
        )
    an_data["An_DigNDF"] = calculate_An_DigNDF(
        an_data["An_DigNDFIn"], Dt_DMIn, infusion_data["InfRum_DMIn"], 
        infusion_data["InfSI_DMIn"]
        )
    an_data["An_GEIn"] = calculate_An_GEIn(
        diet_data["Dt_GEIn"], infusion_data["Inf_NDFIn"],
        infusion_data["Inf_StIn"], infusion_data["Inf_FAIn"],
        infusion_data["Inf_TPIn"], infusion_data["Inf_NPNCPIn"],
        infusion_data["Inf_AcetIn"], infusion_data["Inf_PropIn"],
        infusion_data["Inf_ButrIn"], coeff_dict
        )
    # Next three values are passed to calculate_An_GasEOut which will assign 
    # An_GasEOut the correct value
    An_GasEOut_Dry = calculate_An_GasEOut_Dry(
        Dt_DMIn, diet_data["Dt_FAIn"], infusion_data["InfRum_FAIn"], 
        infusion_data["InfRum_DMIn"], an_data["An_GEIn"]
        )
    An_GasEOut_Lact = calculate_An_GasEOut_Lact(
        Dt_DMIn, diet_data["Dt_FAIn"], infusion_data["InfRum_FAIn"], 
        infusion_data["InfRum_DMIn"], an_data["An_DigNDF"]
        )
    An_GasEOut_Heif = calculate_An_GasEOut_Heif(
        an_data["An_GEIn"], an_data["An_NDF"]
        )
    an_data["An_GasEOut"] = calculate_An_GasEOut(
        An_StatePhys, Monensin_eqn, An_GasEOut_Dry, 
        An_GasEOut_Lact, An_GasEOut_Heif
        )
    an_data["An_GutFill_BW"] = calculate_An_GutFill_BW(
        An_BW, An_BW_mature,
        An_StatePhys, An_Parity_rl,
        diet_data["Dt_DMIn_ClfLiq"], diet_data["Dt_DMIn_ClfStrt"], coeff_dict
        )
    an_data["An_BWnp"] = calculate_An_BWnp(An_BW, GrUter_Wt)
    an_data["An_GutFill_Wt"] = calculate_An_GutFill_Wt(
        an_data["An_GutFill_BW"], an_data["An_BWnp"]
        )
    an_data["An_BW_empty"] = calculate_An_BW_empty(
        An_BW, an_data["An_GutFill_Wt"]
        )
    an_data["An_MBW"] = calculate_An_MBW(An_BW)
    an_data["An_RDNPNCPIn"] = calculate_An_RDNPNCPIn(
        diet_data["Dt_NPNCPIn"], infusion_data["InfRum_NPNCPIn"]
        )
    an_data["An_RUP"] = calculate_An_RUP(
        an_data["An_RUPIn"], Dt_DMIn, infusion_data["InfRum_DMIn"]
        )
    an_data["An_RUP_CP"] = calculate_An_RUP_CP(
        an_data["An_RUPIn"], diet_data["Dt_CPIn"], infusion_data["InfRum_CPIn"]
        )
    an_data["An_idRUCPIn"] = calculate_An_idRUCPIn(
        diet_data["Dt_idRUPIn"], infusion_data["InfRum_idRUPIn"],
        infusion_data["InfSI_idCPIn"]
        )
    an_data["An_idRUP"] = calculate_An_idRUP(
        an_data["An_idRUPIn"], Dt_DMIn, infusion_data["InfRum_DMIn"], 
        infusion_data["InfSI_DMIn"]
        )
    an_data["An_RDTPIn"] = calculate_An_RDTPIn(
        diet_data["Dt_RDTPIn"], infusion_data["InfRum_RDPIn"], 
        infusion_data["InfRum_NPNCPIn"], coeff_dict
        )
    an_data["An_RDP_CP"] = calculate_An_RDP_CP(
        an_data["An_RDPIn"], diet_data["Dt_CPIn"], infusion_data["InfRum_CPIn"]
        )
    an_data["An_GasE_IPCC2"] = calculate_An_GasE_IPCC2(an_data["An_GEIn"])
    an_data["An_DigCPaIn"] = calculate_An_DigCPaIn(
        an_data["An_CPIn"], infusion_data["InfArt_CPIn"], Fe_CP
        )
    an_data["An_DECPIn"] = calculate_An_DECPIn(
        an_data["An_DigCPaIn"], coeff_dict
        )
    an_data["An_DENPNCPIn"] = calculate_An_DENPNCPIn(
        diet_data["Dt_NPNCPIn"], coeff_dict
        )
    an_data["An_DETPIn"] = calculate_An_DETPIn(
        an_data["An_DECPIn"], an_data["An_DENPNCPIn"],
        coeff_dict
        )
    an_data["An_DigFAIn"] = calculate_An_DigFAIn(
        diet_data["Dt_DigFAIn"], infusion_data["Inf_DigFAIn"]
        )
    an_data["An_DEFAIn"] = calculate_An_DEFAIn(
        an_data["An_DigFAIn"], coeff_dict
        )
    an_data["An_DEIn"] = calculate_An_DEIn(
        An_StatePhys, an_data["An_DENDFIn"],
        an_data["An_DEStIn"], an_data["An_DErOMIn"],
        an_data["An_DETPIn"], an_data["An_DENPNCPIn"],
        an_data["An_DEFAIn"], infusion_data["Inf_DEAcetIn"],
        infusion_data["Inf_DEPropIn"], infusion_data["Inf_DEPropIn"],
        diet_data["Dt_DMIn_ClfLiq"], diet_data["Dt_DEIn"], Monensin_eqn
        )
    an_data["An_DEInp"] = calculate_An_DEInp(
        an_data["An_DEIn"], an_data["An_DETPIn"], an_data["An_DENPNCPIn"]
        )
    an_data["An_TPIn"] = calculate_An_TPIn(
        diet_data["Dt_TPIn"], infusion_data["Inf_TPIn"]
        )
    an_data["An_DigTPaIn"] = calculate_An_DigTPaIn(
        an_data["An_TPIn"], infusion_data["InfArt_CPIn"], Fe_CP
        )
    an_data["An_IdArgIn"] = calculate_An_IdArgIn(
        diet_data["Dt_IdArgIn"], infusion_data["Inf_IdArgIn"]
        )
    an_data["An_IdHisIn"] = calculate_An_IdHisIn(
        diet_data["Dt_IdHisIn"], infusion_data["Inf_IdHisIn"]
        )
    an_data["An_IdIleIn"] = calculate_An_IdIleIn(
        diet_data["Dt_IdIleIn"], infusion_data["Inf_IdIleIn"]
        )
    an_data["An_IdLeuIn"] = calculate_An_IdLeuIn(
        diet_data["Dt_IdLeuIn"], infusion_data["Inf_IdLeuIn"]
        )
    an_data["An_IdLysIn"] = calculate_An_IdLysIn(
        diet_data["Dt_IdLysIn"], infusion_data["Inf_IdLysIn"]
        )
    an_data["An_IdMetIn"] = calculate_An_IdMetIn(
        diet_data["Dt_IdMetIn"], infusion_data["Inf_IdMetIn"]
        )
    an_data["An_IdPheIn"] = calculate_An_IdPheIn(
        diet_data["Dt_IdPheIn"], infusion_data["Inf_IdPheIn"]
        )
    an_data["An_IdThrIn"] = calculate_An_IdThrIn(
        diet_data["Dt_IdThrIn"], infusion_data["Inf_IdThrIn"]
        )
    an_data["An_IdTrpIn"] = calculate_An_IdTrpIn(
        diet_data["Dt_IdTrpIn"], infusion_data["Inf_IdTrpIn"]
        )
    an_data["An_IdValIn"] = calculate_An_IdValIn(
        diet_data["Dt_IdValIn"], infusion_data["Inf_IdValIn"]
        )
    an_data["An_NPNCPIn"] = calculate_An_NPNCPIn(
        diet_data["Dt_NPNCPIn"], infusion_data["Inf_NPNCPIn"]
        )
    an_data["An_FAIn"] = calculate_An_FAIn(
        diet_data["Dt_FAIn"], infusion_data["Inf_FAIn"]
        )
    an_data["An_DMIn_MBW"] = calculate_An_DMIn_MBW(
        an_data["An_DMIn"], an_data["An_MBW"]
        )
    an_data["An_StIn"] = calculate_An_StIn(
        diet_data["Dt_StIn"], infusion_data["InfRum_StIn"],
        infusion_data["InfSI_StIn"]
        )
    an_data["An_St"] = calculate_An_St(
        an_data["An_StIn"], Dt_DMIn, infusion_data["InfRum_DMIn"], 
        infusion_data["InfSI_DMIn"]
        )
    an_data["An_rOMIn"] = calculate_An_rOMIn(
        diet_data["Dt_rOMIn"], infusion_data["InfRum_GlcIn"],
        infusion_data["InfRum_AcetIn"], infusion_data["InfRum_PropIn"],
        infusion_data["InfRum_ButrIn"], infusion_data["InfSI_AcetIn"],
        infusion_data["InfSI_PropIn"], infusion_data["InfSI_ButrIn"]
        )
    an_data["An_rOM"] = calculate_An_rOM(
        an_data["An_rOMIn"], Dt_DMIn, infusion_data["InfRum_DMIn"], 
        infusion_data["InfSI_DMIn"]
        )
    an_data["An_NDFIn"] = calculate_An_NDFIn(
        diet_data["Dt_NDFIn"], infusion_data["InfRum_NDFIn"],
        infusion_data["InfSI_NDFIn"]
        )
    an_data["An_NDFIn_BW"] = calculate_An_NDFIn_BW(
        an_data["An_NDFIn"], An_BW
        )
    an_data["An_NDF"] = calculate_An_NDF(
        an_data["An_NDFIn"], Dt_DMIn, infusion_data["InfRum_DMIn"], 
        infusion_data["InfSI_DMIn"]
        )
    an_data["An_ADFIn"] = calculate_An_ADFIn(
        diet_data["Dt_ADFIn"], infusion_data["InfRum_ADFIn"],
        infusion_data["InfSI_ADFIn"]
        )
    an_data["An_ADF"] = calculate_An_ADF(
        an_data["An_ADFIn"], Dt_DMIn, infusion_data["InfRum_DMIn"], 
        infusion_data["InfSI_DMIn"]
        )
    an_data["An_CPIn_g"] = calculate_An_CPIn_g(an_data["An_CPIn"])
    an_data["An_CP"] = calculate_An_CP(
        an_data["An_CPIn"], Dt_DMIn, infusion_data["InfRum_DMIn"], 
        infusion_data["InfSI_DMIn"]
        )
    an_data["An_NIn_g"] = calculate_An_NIn_g(an_data["An_CPIn"])
    an_data["An_FAhydrIn"] = calculate_An_FAhydrIn(
        diet_data["Dt_FAhydrIn"], infusion_data["Inf_FAIn"]
        )
    an_data["An_FA"] = calculate_An_FA(
        an_data["An_FAIn"], Dt_DMIn, infusion_data["InfRum_DMIn"], 
        infusion_data["InfSI_DMIn"]
        )
    an_data["An_AshIn"] = calculate_An_AshIn(
        diet_data["Dt_AshIn"], infusion_data["InfRum_AshIn"],
        infusion_data["InfSI_AshIn"]
        )
    an_data["An_Ash"] = calculate_An_Ash(
        an_data["An_AshIn"], Dt_DMIn, infusion_data["InfRum_DMIn"], 
        infusion_data["InfSI_DMIn"]
        )
    an_data["An_DigStIn_Base"] = calculate_An_DigStIn_Base(
        diet_data["Dt_DigStIn_Base"], infusion_data["Inf_StIn"],
        infusion_data["Inf_ttdcSt"]
        )
    an_data["An_DigWSCIn"] = calculate_An_DigWSCIn(
        diet_data["Dt_DigWSCIn"], infusion_data["InfRum_GlcIn"],
        infusion_data["InfSI_GlcIn"]
        )
    an_data["An_DigrOMtIn"] = calculate_An_DigrOMtIn(
        diet_data["Dt_DigrOMtIn"], infusion_data["InfRum_GlcIn"],
        infusion_data["InfRum_AcetIn"], infusion_data["InfRum_PropIn"],
        infusion_data["InfRum_ButrIn"], infusion_data["InfSI_GlcIn"],
        infusion_data["InfSI_AcetIn"], infusion_data["InfSI_PropIn"],
        infusion_data["InfSI_ButrIn"]
        )
    an_data["An_DigSt"] = calculate_An_DigSt(
        an_data["An_DigStIn"], Dt_DMIn, infusion_data["InfRum_DMIn"],
        infusion_data["InfSI_DMIn"]
        )
    an_data["An_DigWSC"] = calculate_An_DigWSC(
        an_data["An_DigWSCIn"], Dt_DMIn, infusion_data["InfRum_DMIn"],
        infusion_data["InfSI_DMIn"]
        )
    an_data["An_DigrOMa"] = calculate_An_DigrOMa(
        an_data["An_DigrOMaIn"], Dt_DMIn, infusion_data["InfRum_DMIn"],
        infusion_data["InfSI_DMIn"]
        )
    an_data["An_DigrOMt"] = calculate_An_DigrOMt(
        an_data["An_DigrOMtIn"], Dt_DMIn, infusion_data["InfRum_DMIn"],
        infusion_data["InfSI_DMIn"]
        )
    an_data["An_DigNDFIn_Base"] = calculate_An_DigNDFIn_Base(
        diet_data["Dt_NDFIn"], infusion_data["InfRum_NDFIn"],
        diet_data["TT_dcNDF_Base"]
        )
    an_data["An_DigCPa"] = calculate_An_DigCPa(
        an_data["An_DigCPaIn"], an_data["An_DMIn"], infusion_data["InfArt_DMIn"]
        )
    an_data["TT_dcAnCPa"] = calculate_TT_dcAnCPa(
        an_data["An_DigCPaIn"], an_data["An_CPIn"], infusion_data["InfArt_CPIn"]
        )
    an_data["An_DigCPtIn"] = calculate_An_DigCPtIn(
        An_StatePhys, diet_data["Dt_DigCPtIn"], infusion_data["Inf_idCPIn"],
        an_data["An_RDPIn"], an_data["An_idRUPIn"]
        )
    an_data["An_DigNtIn_g"] = calculate_An_DigNtIn_g(an_data["An_DigCPtIn"])
    an_data["An_DigTPtIn"] = calculate_An_DigTPtIn(
        an_data["An_RDTPIn"], Fe_MiTP, an_data["An_idRUPIn"], Fe_NPend
        )
    an_data["An_DigCPt"] = calculate_An_DigCPt(
        an_data["An_DigCPtIn"], an_data["An_DMIn"], infusion_data["InfArt_DMIn"]
        )
    an_data["An_DigTPt"] = calculate_An_DigTPt(
        an_data["An_DigTPtIn"], an_data["An_DMIn"], infusion_data["InfArt_DMIn"]
        )
    an_data["TT_dcAnCPt"] = calculate_TT_dcAnCPt(
        an_data["An_DigCPtIn"], an_data["An_CPIn"], infusion_data["InfArt_CPIn"]
        )
    an_data["TT_dcAnTPt"] = calculate_TT_dcAnTPt(
        an_data["An_DigTPtIn"], an_data["An_TPIn"], infusion_data["InfArt_CPIn"], 
        infusion_data["InfRum_NPNCPIn"], infusion_data["InfSI_NPNCPIn"]
        )
    an_data["SI_dcAnRUP"] = calculate_SI_dcAnRUP(
        an_data["An_idRUPIn"], an_data["An_RUPIn"]
        )
    an_data["An_idCPIn"] = calculate_An_idCPIn(an_data["An_idRUPIn"], Du_idMiCP)
    an_data["An_DigFA"] = calculate_An_DigFA(
        an_data["An_DigFAIn"], Dt_DMIn, infusion_data["InfRum_DMIn"],
        infusion_data["InfSI_DMIn"]
        )
    an_data["TT_dcAnFA"] = calculate_TT_dcAnFA(
        diet_data["Dt_DigFAIn"], infusion_data["Inf_DigFAIn"],
        diet_data["Dt_FAIn"], infusion_data["Inf_FAIn"]
        )
    an_data["An_OMIn"] = calculate_An_OMIn(
        diet_data["Dt_OMIn"], infusion_data["Inf_OMIn"]
        )
    an_data["An_DigOMaIn_Base"] = calculate_An_DigOMaIn_Base(
        an_data["An_DigNDFIn_Base"], an_data["An_DigStIn_Base"], 
        an_data["An_DigFAIn"], an_data["An_DigrOMaIn"], an_data["An_DigCPaIn"]
        )
    an_data["An_DigOMtIn_Base"] = calculate_An_DigOMtIn_Base(
        an_data["An_DigNDFIn_Base"], an_data["An_DigStIn_Base"], 
        an_data["An_DigFAIn"], an_data["An_DigrOMtIn"], an_data["An_DigCPtIn"]
        )
    an_data["An_DigOMaIn"] = calculate_An_DigOMaIn(
        an_data["An_DigNDFIn"], an_data["An_DigStIn"], an_data["An_DigFAIn"], 
        an_data["An_DigrOMaIn"], an_data["An_DigCPaIn"]
        )
    an_data["An_DigOMtIn"] = calculate_An_DigOMtIn(
        an_data["An_DigNDFIn"], an_data["An_DigStIn"], an_data["An_DigFAIn"], 
        an_data["An_DigrOMtIn"], an_data["An_DigCPtIn"]
        )
    an_data["TT_dcOMa"] = calculate_TT_dcOMa(
        an_data["An_DigOMaIn"], an_data["An_OMIn"]
        )
    an_data["TT_dcOMt"] = calculate_TT_dcOMt(
        an_data["An_DigOMtIn"], an_data["An_OMIn"]
        )
    an_data["TT_dcOMt_Base"] = calculate_TT_dcOMt_Base(
        an_data["An_DigOMtIn_Base"], an_data["An_OMIn"]
        )
    an_data["An_DigOMa"] = calculate_An_DigOMa(
        an_data["An_DigOMaIn"], Dt_DMIn, infusion_data["InfRum_DMIn"],
        infusion_data["InfSI_DMIn"]
        )
    an_data["An_DigOMt"] = calculate_An_DigOMt(
        an_data["An_DigOMtIn"], Dt_DMIn, infusion_data["InfRum_DMIn"],
        infusion_data["InfSI_DMIn"]
        )
    an_data["An_GEIn"] = calculate_An_GEIn(
        diet_data["Dt_GEIn"], infusion_data["Inf_NDFIn"],
        infusion_data["Inf_StIn"], infusion_data["Inf_FAIn"],
        infusion_data["Inf_TPIn"], infusion_data["Inf_NPNCPIn"],
        infusion_data["Inf_AcetIn"], infusion_data["Inf_PropIn"],
        infusion_data["Inf_ButrIn"], coeff_dict
        )
    an_data["An_GE"] = calculate_An_GE(an_data["An_GEIn"], an_data["An_DMIn"])
    an_data["An_DERDTPIn"] = calculate_An_DERDTPIn(
        an_data["An_RDTPIn"], Fe_DEMiCPend, Fe_DERDPend, coeff_dict
        )
    an_data["An_DEidRUPIn"] = calculate_An_DEidRUPIn(
        an_data["An_idRUPIn"], Fe_DERUPend, coeff_dict
        )
    an_data["An_DE"] = calculate_An_DE(an_data["An_DEIn"], an_data["An_DMIn"])
    an_data["An_DE_GE"] = calculate_An_DE_GE(
        an_data["An_DEIn"], an_data["An_GEIn"]
        )
    an_data["An_DEnp"] = calculate_An_DEnp(
        an_data["An_DEInp"], an_data["An_DMIn"]
        )
    an_data["GasE_DMIn"] = calculate_GasE_DMIn(
        an_data["An_GasEOut"], an_data["An_DMIn"]
        )
    an_data["GasE_GEIn"] = calculate_GasE_GEIn(
        an_data["An_GasEOut"], an_data["An_GEIn"]
        )
    an_data["GasE_DEIn"] = calculate_GasE_DEIn(
        an_data["An_GasEOut"], an_data["An_DEIn"]
        )
    an_data["An_RUPIn_g"] = calculate_An_RUPIn_g(an_data["An_RUPIn"])
    an_data["An_Grazing"] = calculate_An_Grazing(
        diet_data["Dt_PastIn"], Dt_DMIn
        )
    return an_data


####################
# Animal Functions not in Wrapper
####################
def calculate_An_MPIn(
    An_StatePhys: str,
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


def calculate_An_MPIn_g(An_MPIn: float) -> float:
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
    An_MP_CP is not used in any caclulations. I"ve set it to the second equation so
    the Python and R outputs match - Braeden 
    """
    # An_MP_CP = An_MPIn / An_CPIn * 100  # Line 1240
    An_MP_CP = An_MPIn / An_CPIn  # Line 3123
    return An_MP_CP


def calculate_An_MP(
    An_MPIn: float, 
    Dt_DMIn: float, 
    InfRum_DMIn: float,
    InfSI_DMIn: float
) -> float:
    """
    An_MP: Metabolizable protein, % DMI
    """
    An_MP = An_MPIn / (Dt_DMIn + InfRum_DMIn + InfSI_DMIn) * 100  # Line 1239
    return An_MP


def calculate_An_NPm_Use(
    Scrf_NP_g: float, 
    Fe_NPend_g: float,
    Ur_NPend_g: float
) -> float:
    """
    An_NPm_Use: Net protein used for maintenance? (g/d)
    """
    An_NPm_Use = Scrf_NP_g + Fe_NPend_g + Ur_NPend_g  # Line 2063
    return An_NPm_Use


def calculate_An_CPm_Use(
    Scrf_CP_g: float, 
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


def calculate_An_PrePartDay(An_GestDay: int, An_GestLength: int) -> int:
    An_PrePartDay = An_GestDay - An_GestLength
    return An_PrePartDay

    
def calculate_An_PrePartWk(An_PrePartDay: int) -> float:
    An_PrePartWk = An_PrePartDay / 7
    return An_PrePartWk

    
def calculate_An_PrePartWkDurat(An_PrePartWklim: float) -> float:
    An_PrePartWkDurat = An_PrePartWklim * 2
    return An_PrePartWkDurat
