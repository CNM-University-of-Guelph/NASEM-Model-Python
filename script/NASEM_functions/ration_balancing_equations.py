import math


def calculate_Dt_DMIn_Lact1(An_Parity_rl, Trg_MilkProd, An_BW, An_BCS, An_LactDay, Trg_MilkFatp, Trg_MilkTPp, Trg_MilkLacp):
    
    Trg_NEmilk_Milk = 9.29*Trg_MilkFatp/100 + 5.85*Trg_MilkTPp/100 + 3.95*Trg_MilkLacp/100
    Trg_NEmilkOut = Trg_NEmilk_Milk * Trg_MilkProd                                         # Line 386
    
    term1 = (3.7 + 5.7 * (An_Parity_rl - 1) + 0.305 * Trg_NEmilkOut + 0.022 * An_BW +       # Line 389
             (-0.689 - 1.87 * (An_Parity_rl - 1)) * An_BCS)
    term2 = 1 - (0.212 + 0.136 * (An_Parity_rl - 1)) * math.exp(-0.053 * An_LactDay)
    Dt_DMIn_Lact1 = term1 * term2
    return Dt_DMIn_Lact1


def calculate_Du_MiCP_g(Dt_NDFIn, Dt_DMIn, Dt_StIn, Dt_CPIn, Dt_ADFIn, Dt_ForWet, Dt_RUPIn, Dt_ForNDF):
    # There are 3 equations for predicting microbial N, all 3 will be included and the MCP prediction from each will be displayed
    # Ask Dave and John which should be used or if we keep all 3

    # This will take the inputs and call all three fucntions

    # Calculate Rum_DigNDFIn
    Rum_dcNDF = -31.9 + 0.721 * (Dt_NDFIn / Dt_DMIn) * 100                                  # Line 976-982
    - 0.247 * (Dt_StIn / Dt_DMIn) * 100 
    + 6.63 * (Dt_CPIn / Dt_DMIn) * 100 
    - 0.211 * ((Dt_CPIn / Dt_DMIn) * 100) ** 2 
    - 0.387 * (Dt_ADFIn / Dt_DMIn) / (Dt_NDFIn / Dt_DMIn) * 100 
    - 0.121 * Dt_ForWet + 1.51 * Dt_DMIn
    if Rum_dcNDF < 0.1 or Rum_dcNDF is None:                                                # Line 984
        Rum_dcNDF = 0.1
    Rum_DigNDFIn = Rum_dcNDF / 100 * Dt_NDFIn

    # Calculate An_RDPIn
    An_RDPIn = Dt_CPIn - Dt_RUPIn                                                           # Line 1107, 1102

    # Calculate Rum_DigStIn
    Rum_dcSt = 70.6 - 1.45 * Dt_DMIn + 0.424 * Dt_ForNDF                                    # Line 988-991
    + 1.39 * (Dt_StIn / Dt_DMIn) * 100 
    - 0.0219 * ((Dt_StIn / Dt_DMIn) * 100) ** 2 
    - 0.154 * Dt_ForWet 
    if Rum_dcSt < 0.1:                                                                      # Line 992
        Rum_dcSt = 0.1              
    elif Rum_dcSt > 100:                                                                    # Line 993
        Rum_dcSt = 100 
    Rum_DigStIn = Rum_dcSt / 100 * Dt_StIn                                                  # Line 998 


    Du_MiN_NRC2021_g = calculate_Du_MiN_NRC2021_g(An_RDP, An_RDPIn, Dt_DMIn, Rum_DigNDFIn, Rum_DigStIn)
    Du_MiN_VTln_g = calculate_Du_MiN_VTln_g(Dt_DMIn, Dt_AshIn, Dt_NDFIn, Dt_StIn, Dt_FAhydrIn, Dt_TPIn, Dt_NPNDMIn, Rum_DigStIn,
                                            Rum_DigNDFIn, An_RDPIn, Dt_ForNDFIn)
    Du_MiN_VTnln_g = calculate_Du_MiN_VTnln_g(An_RDPIn, Rum_DigNDFIn, Rum_DigStIn)

    return Du_MiN_NRC2021_g, Du_MiN_VTln_g, Du_MiN_VTnln_g


def calculate_Du_MiN_NRC2021_g(An_RDP, An_RDPIn, Dt_DMIn, Rum_DigNDFIn, Rum_DigStIn): 
    VmMiNInt = 100.8                                                                        # Line 1117
    VmMiNRDPSlp = 81.56                                                                     # Line 1118
    KmMiNRDNDF = 0.0939                                                                     # Line 1119
    KmMiNRDSt = 0.0274                                                                      # Line 1120
    
    if An_RDP <= 12:                                                                        # Line 1124
        RDPIn_MiNmax = An_RDPIn
    else:
        RDPIn_MiNmax = Dt_DMIn * 0.12
        # RDP intake capped at 12% DM from Firkins paper
    MiN_Vm = VmMiNInt + VmMiNRDPSlp * RDPIn_MiNmax                                            # Line 1125            

    Du_MiN_NRC2021_g = MiN_Vm / (1 + KmMiNRDNDF / Rum_DigNDFIn + KmMiNRDSt / Rum_DigStIn)       # Line 1126

    return Du_MiN_NRC2021_g


def calculate_Du_MiN_VTln_g(Dt_DMIn, Dt_AshIn, Dt_NDFIn, Dt_StIn, Dt_FAhydrIn, Dt_TPIn, Dt_NPNDMIn, Rum_DigStIn,
                            Rum_DigNDFIn, An_RDPIn, Dt_ForNDFIn):
    # MiN (g/d) Parms for eqn. 52 (linear) from Hanigan et al, RUP paper
    # Derived using RUP with no KdAdjust
    Int_MiN_VT = 18.686                                                                     # Line 1134
    KrdSt_MiN_VT = 10.214                                                                   # Line 1135
    KrdNDF_MiN_VT = 28.976                                                                  # Line 1136
    KRDP_MiN_VT = 43.405                                                                    # Line 1137
    KrOM_MiN_VT = -11.731                                                                   # Line 1138
    KForNDF_MiN_VT = 8.895                                                                  # Line 1139
    KrOM2_MiN_VT = 2.861                                                                    # Line 1140
    KrdStxrOM_MiN_VT = 5.637                                                                # Line 1141
    KrdNDFxForNDF_MiN_VT = -2.22                                                            # Line 1142

    Dt_rOMIn = Dt_DMIn-Dt_AshIn-Dt_NDFIn-Dt_StIn-Dt_FAhydrIn-Dt_TPIn-Dt_NPNDMIn             # Line 647
    if Dt_rOMIn < 0:                                                                        # Line 648
        Dt_rOMIn = 0                                                                        

    Du_MiN_VTln_g = Int_MiN_VT + KrdSt_MiN_VT * Rum_DigStIn + KrdNDF_MiN_VT * Rum_DigNDFIn        # Line 1144-1146
    + KRDP_MiN_VT * An_RDPIn + KrOM_MiN_VT * Dt_rOMIn + KForNDF_MiN_VT * Dt_ForNDFIn + KrOM2_MiN_VT * Dt_rOMIn ** 2 
    + KrdStxrOM_MiN_VT * Rum_DigStIn * Dt_rOMIn + KrdNDFxForNDF_MiN_VT * Rum_DigNDFIn * Dt_ForNDFIn

    return Du_MiN_VTln_g


def calculate_Du_MiN_VTnln_g(An_RDPIn, Rum_DigNDFIn, Rum_DigStIn):
    
    Du_MiN_VTnln_g = 7.47 + 0.574 * An_RDPIn * 1000 / (1 + 3.60 / Rum_DigNDFIn + 12.3 / Rum_DigStIn)    # Line 1147

    return Du_MiN_VTnln_g


# def calculate_Mlk_Prod_comp():

#     Mlk_NP_g = mPrt_Int + Abs_Arg_g*mPrt_k_Arg + Abs_His_g*mPrt_k_His + Abs_Ile_g*mPrt_k_Ile + 
# 	Abs_Leu_g*mPrt_k_Leu + Abs_Lys_g*mPrt_k_Lys + Abs_Met_g*mPrt_k_Met + Abs_Phe_g*mPrt_k_Phe +
# 	Abs_Thr_g*mPrt_k_Thr + Abs_Trp_g*mPrt_k_Trp + Abs_Val_g*mPrt_k_Val + Abs_neAA_g*mPrt_k_NEAA +
#      Abs_OthAA_g*mPrt_k_OthAA + Abs_EAA2b_g*mPrt_k_EAA2 + An_DEInp*mPrt_k_DEInp + (An_DigNDF-17.06)*mPrt_k_DigNDF + 
#      (An_DEStIn+An_DEFAIn+An_DErOMIn)*mPrt_k_DEIn_StFA + An_DENDFIn*mPrt_k_DEIn_NDF + (An_BW-612)*mPrt_k_BW
    
#     Mlk_NP = Mlk_NP_g / 1000                                                                # Line 2211

#     Mlk_Prod_comp = 4.541 + 11.13*Mlk_NP + 2.648*Mlk_Fat + 0.1829 * An_DEIn - 0.06257*(An_LactDay_MlkPred-137.1) 
#     + 2.766e-4*(An_LactDay_MlkPred-137.1)^2 + 1.603e-6*(An_LactDay_MlkPred-137.1)^3 - 7.397e-9*(An_LactDay_MlkPred-137.1)^4 
#     + 1.567*(An_Parity_rl-1)    

#     return Mlk_Prod_comp





