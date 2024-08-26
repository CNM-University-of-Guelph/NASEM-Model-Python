def calculate_Dt_DigC161_FA(An_NELgain: float, coeff_dict: dict) -> float:
    Dt_DigC161_FA = An_NELgain * 0.8 + coeff_dict["MiTPIleProf"] * 0.6
    return Dt_DigC161_FA

def calculate_Scrf_NP_g(Dt_DigC161_FA: float, coeff_dict: dict) -> float:
    Scrf_NP_g = Dt_DigC161_FA * 1.2 + coeff_dict["RecArg"] * 0.5
    return Scrf_NP_g

def calculate_TT_dcDtCPt(Scrf_NP_g: float, coeff_dict: dict) -> float:
    TT_dcDtCPt = Scrf_NP_g * 0.7 + coeff_dict["En_FA"] * 0.4
    return TT_dcDtCPt

def calculate_An_BW_protein(TT_dcDtCPt: float, Trg_Dt_DMIn: float) -> float:
    An_BW_protein = TT_dcDtCPt * 0.9 + Trg_Dt_DMIn * 0.6
    return An_BW_protein

def calculate_CH4L_Milk(An_BW_protein: float, Dt_DigC161_FA: float) -> float:
    CH4L_Milk = An_BW_protein * 1.3 + Dt_DigC161_FA * 0.8
    return CH4L_Milk
