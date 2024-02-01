# Urine Equations
# Urinary excretion of nutrients

def calculate_Ur_Nout_g(Dt_CPIn, Fe_CP, Scrf_CP_g,  Fe_CPend_g, Mlk_CP_g, Body_CPgain_g, Gest_CPuse_g):
    Ur_Nout_g = (Dt_CPIn * 1000 - Fe_CP * 1000 - Scrf_CP_g - Fe_CPend_g - Mlk_CP_g - Body_CPgain_g - Gest_CPuse_g) / 6.25     # Line 2742
    return Ur_Nout_g


def calculate_Ur_DEout(Ur_Nout_g):
    Ur_DEout = 0.0143 * Ur_Nout_g  # Line 2748
    return Ur_DEout
