import math


def calculate_Dt_DMIn_Lact1(An_Parity_rl, Trg_MilkProd, An_BW, An_BCS, An_LactDay, Trg_MilkFatp, Trg_MilkTPp, Trg_MilkLacp):
    
    Trg_NEmilk_Milk = 9.29*Trg_MilkFatp/100 + 5.85*Trg_MilkTPp/100 + 3.95*Trg_MilkLacp/100
    Trg_NEmilkOut = Trg_NEmilk_Milk * Trg_MilkProd                                         # Line 386
    
    term1 = (3.7 + 5.7 * (An_Parity_rl - 1) + 0.305 * Trg_NEmilkOut + 0.022 * An_BW +       # Line 389
             (-0.689 - 1.87 * (An_Parity_rl - 1)) * An_BCS)
    term2 = 1 - (0.212 + 0.136 * (An_Parity_rl - 1)) * math.exp(-0.053 * An_LactDay)
    Dt_DMIn_Lact1 = term1 * term2
    return Dt_DMIn_Lact1
