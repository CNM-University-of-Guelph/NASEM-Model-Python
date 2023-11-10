# dev_DMI_equations
# This file contains all the calculations for dry matter intake (DMI)
# Calculations are in the order coresponding to their DMIn_eqn value

import math

# DMIn_eqn == 8
def calculate_Dt_DMIn_Lact1(Trg_MilkProd, 
                            An_BW, 
                            An_BCS, 
                            An_LactDay, 
                            An_Parity_rl, 
                            Trg_NEmilk_Milk):
    """
    Animal based dry matter intake (DMI) prediction for lactating cows

    This function predicts the DMI using animal factors only. This is equation 2-1 in the NASEM 8 textbook. In the model
    this prediction can be can be selected by setting DMI_pred to 0 in the 'input.txt'. In :py:func:`NASEM_model` Dt_DMIn_Lact1
    will be returned to the animal_input dictionary with the key 'DMI'.

    Parameters:
        An_Parity_rl (Number): Animal Parity where 1 = Primiparous and 2 = Multiparous.
        Trg_MilkProd (Number): Animal Milk Production in kg/day.
        An_BW (Number): Animal Body Weight in kg.
        An_BCS (Number): Body condition score, from 1-5
        An_LactDay (Number): Day of Lactation.

    Returns:
        Dt_DMIn_Lact1 (Number): Dry matter intake, kg/d
    """
    Trg_NEmilkOut = Trg_NEmilk_Milk * Trg_MilkProd  # Line 386
    # Trg_NEmilkOut is only used for this DMI calculation
    Dt_DMIn_Lact1 = (
    3.7 +
    5.7 * (An_Parity_rl - 1) +
    0.305 * Trg_NEmilkOut +
    0.022 * An_BW +
    (-0.689 - 1.87 * (An_Parity_rl - 1)) * An_BCS
    ) * (
    1 - (0.212 + 0.136 * (An_Parity_rl - 1)) * math.exp(-0.053 * An_LactDay)
    )  # Line 389                                                
    return Dt_DMIn_Lact1
    