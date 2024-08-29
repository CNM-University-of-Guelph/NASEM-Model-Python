"""Rumen digestion calculations.

This module provides functions to estimate the digestibility of different 
dietary components in the rumen, including neutral detergent fiber (NDF) 
and starch, and their passage through the digestive system.
"""


def calculate_Rum_dcNDF(
    Dt_DMIn: float, 
    Dt_NDFIn: float, 
    Dt_StIn: float, 
    Dt_CPIn: float, 
    Dt_ADFIn: float,
    Dt_ForWet: float
) -> float:
    Rum_dcNDF = (-31.9 + 0.721 * Dt_NDFIn / 
                 Dt_DMIn * 100 - 0.247 * Dt_StIn / 
                 Dt_DMIn * 100 + 6.63 * Dt_CPIn / 
                 Dt_DMIn * 100 - 0.211 * (Dt_CPIn / Dt_DMIn * 100)**2 - 
                 0.387 * Dt_ADFIn / Dt_DMIn / (Dt_NDFIn / Dt_DMIn) * 100 - 
                 0.121 * Dt_ForWet + 1.51 * Dt_DMIn)

    if Rum_dcNDF < 0.1 or Rum_dcNDF is None:  # Line 984
        Rum_dcNDF = 0.1
    return Rum_dcNDF


def calculate_Rum_dcSt(
    Dt_DMIn: float, 
    Dt_ForNDF: float, 
    Dt_StIn: float, 
    Dt_ForWet: float
) -> float:
    Rum_dcSt = (70.6 - 1.45 * Dt_DMIn + 0.424 * Dt_ForNDF + 1.39 * Dt_StIn / 
                Dt_DMIn * 100 - 0.0219 * (Dt_StIn / Dt_DMIn * 100)**2 - 
                0.154 * Dt_ForWet)
    if Rum_dcSt < 0.1:  # Line 992
        Rum_dcSt = 0.1
    elif Rum_dcSt > 100:  # Line 993
        Rum_dcSt = 100
    return Rum_dcSt


def calculate_Rum_DigNDFIn(Rum_dcNDF: float, Dt_NDFIn: float) -> float:
    Rum_DigNDFIn = Rum_dcNDF / 100 * Dt_NDFIn
    return Rum_DigNDFIn


def calculate_Rum_DigStIn(Rum_dcSt: float, Dt_StIn: float) -> float:
    Rum_DigStIn = Rum_dcSt / 100 * Dt_StIn # Line 998
    return Rum_DigStIn


def calculate_Rum_DigNDFnfIn(Rum_dcNDF: float, Dt_NDFnfIn: float) -> float:
    """
    Rum_DigNDFnfIn: Rumen digested Nitrogen free NDF intake, kg
    """
    Rum_DigNDFnfIn = Rum_dcNDF / 100 * Dt_NDFnfIn  
    # Not used.  IF used, should consider infusions, Line 996
    return Rum_DigNDFnfIn


def calculate_Du_StPas(
    Dt_StIn: float, 
    InfRum_StIn: float,
    Rum_DigStIn: float
) -> float:
    """
    Du_StPas: Duodenal starch passage?, kg?
    """
    Du_StPas = Dt_StIn + InfRum_StIn - Rum_DigStIn  # Line 999
    if Du_StPas < 0:  
        # All grass diets predicted to be very slightly negative, Line 1000
        Du_StPas = 0
    return Du_StPas


def calculate_Du_NDFPas(
    Dt_NDFIn: float, 
    Inf_NDFIn: float,
    Rum_DigNDFIn: float
) -> float:
    """
    Du_NDFPas: Duodenal NDF passage?, kg?
    """
    Du_NDFPas = Dt_NDFIn + Inf_NDFIn - Rum_DigNDFIn  # Line 1001
    return Du_NDFPas
