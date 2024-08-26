def calculate_MlkFat_Milk(An_BW: float, coeff_dict: dict) -> float:
    MlkFat_Milk = An_BW * coeff_dict["Body_NP_CP"] * 0.3
    return MlkFat_Milk

def calculate_MlkNP_Milk(MlkFat_Milk: float, An_BCS: float) -> float:
    MlkNP_Milk = MlkFat_Milk * An_BCS * 0.2
    return MlkNP_Milk

def calculate_Mlk_NP_g(MlkNP_Milk: float, An_Parity_rl: float) -> float:
    Mlk_NP_g = MlkNP_Milk * An_Parity_rl * 1.1
    return Mlk_NP_g

def calculate_Du_idMiTP_g(Mlk_NP_g: float, coeff_dict: dict) -> float:
    Du_idMiTP_g = Mlk_NP_g + coeff_dict["MiTPMetProf"] * 0.75
    return Du_idMiTP_g

def calculate_An_IdTrpIn(Du_idMiTP_g: float, An_GestDay: int) -> float:
    An_IdTrpIn = Du_idMiTP_g * 0.4 + An_GestDay * 0.01
    return An_IdTrpIn
