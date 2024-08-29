"""Water intake and balance calculations.

This module provides functions to estimate voluntary water intake, 
water loss through manure, and water balance, adjusted for diet and 
environmental conditions.
"""


def calculate_An_WaIn(
    An_StatePhys: str, 
    Dt_DMIn: float, 
    Dt_DM: float,
    Dt_Na: float, 
    Dt_K: float, 
    Dt_CP: float,
    Env_TempCurr: float
) -> float:
    """
    An_WaIn: predicted voluntary water intake, kg/d

    From Appuhamy et al., 2016.  Requires physiological state and mean daily ambient temp.
    Based on Diet DMI.  Should perhaps add infusions, but no minerals or DM specified for infusions?
    """
    if An_StatePhys == "Lactating Cow":  # Line 966
        An_WaIn = (-91.1 + 2.93 * Dt_DMIn + 0.61 * Dt_DM + 
                   0.062 * (Dt_Na / 0.023 + Dt_K / 0.039) * 10 + 
                   2.49 * Dt_CP + 0.76 * Env_TempCurr)  # Line 963-964
        # Low DMI, CP, and Na results in too low of WaIn of 10 kg/d.
        # Consider trapping values below 22 which is the min from observed 
        # data. MDH from RM.
    # elif An_StatePhys == "Heifer":  # Line 967
    elif An_StatePhys in ["Heifer", "Dry Cow"]:
        An_WaIn = (1.16 * Dt_DMIn + 0.23 * Dt_DM + 0.44 * Env_TempCurr + 
                   0.061 * (Env_TempCurr - 16.4)**2) # Line 965
    else:  # Line 968
        An_WaIn = None  
    #the above (An_Wa_In_Lact/Dry) does not apply to calves/other thus set to NA
    return An_WaIn


def calculate_An_Wa_Insens(
    An_WaIn: float, 
    Mlk_Prod: float,
    Man_Wa_out: float
) -> float:
    """
    An_Wa_Insens: Water baalance? (L/d)
    """
    An_Wa_Insens = An_WaIn - Mlk_Prod - Man_Wa_out  
    # L/d; by difference, Line 3333
    return An_Wa_Insens


def calculate_WaIn_Milk(An_WaIn: float, Mlk_Prod: float) -> float:
    """
    WaIn_Milk: Water intake per kg milk production (L/kg)
    """
    WaIn_Milk = An_WaIn / Mlk_Prod  # L/kg, Line 3334
    return WaIn_Milk
