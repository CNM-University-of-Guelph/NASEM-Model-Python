import math


def calculate_Dt_DMIn_Lact1(An_Parity_rl, Trg_MilkProd, An_BW, An_BCS, An_LactDay, Trg_MilkFatp, Trg_MilkTPp, Trg_MilkLacp):
    
    Trg_NEmilk_Milk = 9.29*Trg_MilkFatp/100 + 5.85*Trg_MilkTPp/100 + 3.95*Trg_MilkLacp/100
    Trg_NEmilkOut = Trg_NEmilk_Milk * Trg_MilkProd                                         # Line 386
    
    term1 = (3.7 + 5.7 * (An_Parity_rl - 1) + 0.305 * Trg_NEmilkOut + 0.022 * An_BW +       # Line 389
             (-0.689 - 1.87 * (An_Parity_rl - 1)) * An_BCS)
    term2 = 1 - (0.212 + 0.136 * (An_Parity_rl - 1)) * math.exp(-0.053 * An_LactDay)
    Dt_DMIn_Lact1 = term1 * term2
    return Dt_DMIn_Lact1


def calculate_Du_MiCP_g():
    # There are 3 equations for predicting microbial N, all 3 will be included and the MCP prediction from each will be displayed
    # Ask Dave and John which should be used or if we keep all 3

    # This will take the inputs and call all three fucntions



def calculate_Du_MiN_NRC2021_g(An_RDP, Dt_CPIn, Dt_RUPIn, Dt_DMIn, Dt_NDFIn, Dt_StIn, Dt_ADFIn, Dt_ForWet):
    VmMiNInt = 100.8                                                                        # Line 1117
    VmMiNRDPSlp = 81.56                                                                     # Line 1118
    KmMiNRDNDF = 0.0939                                         
    
    An_RDPIn = Dt_CPIn - Dt_RUPIn                                                           # Line 1107, 1102
    if An_RDP <= 12:                                                                        # Line 1124
        RDPIn_MiNmax = An_RDPIn
    else:
        RDPIn_MiNmax = Dt_DMIn * 0.12
        # RDP intake capped at 12% DM from Firkins paper
    MiN_Vm = VmMiNInt + VmMiNRDPSlp*RDPIn_MiNmax                                            # Line 1125            


    Rum_dcNDF = -31.9 + 0.721 * (Dt_NDFIn / Dt_DMIn) * 100 -                                # Line 976-982
    0.247 * (Dt_StIn / Dt_DMIn) * 100 +
    6.63 * (Dt_CPIn / Dt_DMIn) * 100 - 
    0.211 * ((Dt_CPIn / Dt_DMIn) * 100) ** 2 - 
    0.387 * (Dt_ADFIn / Dt_DMIn) / (Dt_NDFIn / Dt_DMIn) * 100 - 
    0.121 * Dt_ForWet + 1.51 * Dt_DMIn
    
    Rum_DigNDFIn = Rum_dcNDF / 100 * Dt_NDFIn


    Du_MiN_NRC2021_g = MiN_Vm / (1 + KmMiNRDNDF/Rum_DigNDFIn + KmMiNRDSt/Rum_DigStIn)       # Line 1126

    return Du_MiN_NRC2021_g
