# Urine Equations
# Urinary excretion of nutrients

def calculate_Ur_Nout_g(Dt_CPIn, Fe_CP, Scrf_CP_g,  Fe_CPend_g, Mlk_CP_g, Body_CPgain_g, Gest_CPuse_g):
    Ur_Nout_g = (Dt_CPIn * 1000 - Fe_CP * 1000 - Scrf_CP_g - Fe_CPend_g - Mlk_CP_g - Body_CPgain_g - Gest_CPuse_g) / 6.25     # Line 2742
    return Ur_Nout_g


def calculate_Ur_DEout(Ur_Nout_g):
    Ur_DEout = 0.0143 * Ur_Nout_g  # Line 2748
    return Ur_DEout


def calculate_Ur_Nend_g(An_BW: float) -> float:
    """
    Ur_Nend_g: Urinary endogenous N, g
    """
    Ur_Nend_g = 0.053 * An_BW   # approximates Ur_Nend_sum, Line 2029
    return Ur_Nend_g


def calculate_Ur_NPend_g(Ur_Nend_g: float) -> float:
    """
    Ur_NPend_g: Urinary endogenous Net protein, g
    """
    Ur_NPend_g = Ur_Nend_g * 6.25   # Line 2030
    return Ur_NPend_g


def calculate_Ur_MPendUse_g(Ur_NPend_g: float) -> float:
    """
    Ur_MPendUse_g: Urinary endogenous Metabolizable protein, g
    """
    Ur_MPendUse_g = Ur_NPend_g  # Line 2672
    return Ur_MPendUse_g
