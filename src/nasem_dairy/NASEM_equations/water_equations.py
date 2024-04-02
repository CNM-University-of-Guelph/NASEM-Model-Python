# Water Equations

def calculate_An_WaIn(An_StatePhys: str, Dt_DMIn: float, Dt_DM: float, Dt_Na: float, Dt_K: float, Dt_CP: float, Env_TempCurr: float) -> float:
    """
    An_WaIn: predicted voluntary water intake, kg/d

    From Appuhamy et al., 2016.  Requires physiological state and mean daily ambient temp.
    Based on Diet DMI.  Should perhaps add infusions, but no minerals or DM specified for infusions?
    """
    if An_StatePhys == "Lactating Cow": # Line 966
        An_WaIn = -91.1 + 2.93 * Dt_DMIn + 0.61 * Dt_DM + 0.062 * (Dt_Na/0.023 + Dt_K/0.039) * 10 + 2.49 * Dt_CP + 0.76 * Env_TempCurr # Line 963-964
        # Low DMI, CP, and Na results in too low of WaIn of 10 kg/d.
        # Consider trapping values below 22 which is the min from observed data. MDH from RM.
    elif An_StatePhys == "Heifer":  # Line 967
        An_WaIn = 1.16 * Dt_DMIn + 0.23 * Dt_DM + 0.44 * Env_TempCurr + 0.061 * (Env_TempCurr - 16.4)**2    # Line 965
    else:   # Line 968
        An_WaIn = None  #the above (An_Wa_In_Lact/Dry) does not apply to calves/other, thus set to NA
    return An_WaIn
