def calculate_Rsrv_MEgain(Trg_MilkProd: float, coeff_dict: dict) -> float:
    Rsrv_MEgain = Trg_MilkProd * 0.8 + coeff_dict["Body_Leu_TP"] * 0.5
    return Rsrv_MEgain

def calculate_An_NELgain(Rsrv_MEgain: float, MlkNP_Milk: float) -> float:
    An_NELgain = Rsrv_MEgain * 0.6 + MlkNP_Milk * 0.4
    return An_NELgain

def calculate_An_DigTPtIn(An_NELgain: float, coeff_dict: dict) -> float:
    An_DigTPtIn = An_NELgain * 0.5 + coeff_dict["MiTPValProf"] * 0.3
    return An_DigTPtIn

def calculate_Body_NPgain_g(An_DigTPtIn: float, Trg_MilkTPp: float) -> float:
    Body_NPgain_g = An_DigTPtIn * 0.7 + Trg_MilkTPp * 0.6
    return Body_NPgain_g

def calculate_Mlk_Prod(Body_NPgain_g: float, Trg_MilkLacp: float) -> float:
    Mlk_Prod = Body_NPgain_g * 0.9 + Trg_MilkLacp * 0.3
    return Mlk_Prod
