"""Methane production and emission calculations.

This module provides functions to calculate methane emissions, expressed in 
grams or liters per day, and per unit of milk produced.
"""


def calculate_CH4out_g(An_GasEOut: float, coeff_dict: dict) -> float:
    """
    CH4out_g: Methane production (g/d)
    """
    CH4out_g = An_GasEOut / coeff_dict['En_CH4'] * 1000  # g methane/d, Line 3240
    return CH4out_g


def calculate_CH4out_L(CH4out_g: float, coeff_dict: dict) -> float:
    """
    CH4out_L: Methane production (L/d)
    """
    CH4out_L = CH4out_g / 1000 * coeff_dict['CH4vol_kg']  # L/d, Line 3241
    return CH4out_L


def calculate_CH4g_Milk(CH4out_g: float, Mlk_Prod: float) -> float:
    """
    CH4g_Milk: Methane intensity (g CH4 / kg milk)
    """
    CH4g_Milk = CH4out_g / Mlk_Prod  # g/kg, Line 3242
    return CH4g_Milk


def calculate_CH4L_Milk(CH4out_L: float, Mlk_Prod: float) -> float:
    """
    CH4L_Milk: Methane intensity (g CH4 / kg milk)
    """
    CH4L_Milk = CH4out_L / Mlk_Prod  # L/kg, Line 3243
    return CH4L_Milk
