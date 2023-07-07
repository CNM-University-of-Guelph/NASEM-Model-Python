import math


def calculate_Dt_DMIn_Lact1(An_Parity_rl, Trg_MilkProd, An_BW, An_BCS, An_LactDay, Trg_MilkFatp, Trg_MilkTPp, Trg_MilkLacp):
    
    Trg_NEmilk_Milk = 9.29*Trg_MilkFatp/100 + 5.85*Trg_MilkTPp/100 + 3.95*Trg_MilkLacp/100
    Trg_NEmilkOut = Trg_NEmilk_Milk * Trg_MilkProd                                         # Line 386
    
    term1 = (3.7 + 5.7 * (An_Parity_rl - 1) + 0.305 * Trg_NEmilkOut + 0.022 * An_BW +       # Line 389
             (-0.689 - 1.87 * (An_Parity_rl - 1)) * An_BCS)
    term2 = 1 - (0.212 + 0.136 * (An_Parity_rl - 1)) * math.exp(-0.053 * An_LactDay)
    Dt_DMIn_Lact1 = term1 * term2
    return Dt_DMIn_Lact1


def calculate_Du_MiCP_g(Dt_NDFIn, Dt_DMIn, Dt_StIn, Dt_CPIn, Dt_ADFIn, Dt_ForWet, Dt_RUPIn, Dt_ForNDF, An_RDP):
    # This has been tested and works
   
    # There are 3 equations for predicting microbial N, all 3 will be included and the MCP prediction from each will be displayed
    # Currently the default is the only one used

    # This will take the inputs and call the default NRC function fucntions

    # Calculate Rum_DigNDFIn
    Rum_dcNDF = -31.9 + 0.721 * Dt_NDFIn / Dt_DMIn * 100 - \
            0.247 * Dt_StIn / Dt_DMIn * 100 + \
            6.63 * Dt_CPIn / Dt_DMIn * 100 - \
            0.211 * (Dt_CPIn / Dt_DMIn * 100) ** 2 - \
            0.387 * Dt_ADFIn / Dt_DMIn / (Dt_NDFIn / Dt_DMIn) * 100 - \
            0.121 * Dt_ForWet + 1.51 * Dt_DMIn

    if Rum_dcNDF < 0.1 or Rum_dcNDF is None:                                                # Line 984
        Rum_dcNDF = 0.1
        
    Rum_DigNDFIn = Rum_dcNDF / 100 * Dt_NDFIn

    # Calculate An_RDPIn
    An_RDPIn = Dt_CPIn - Dt_RUPIn                                                           # Line 1107, 1102

    # Calculate Rum_DigStIn
    Rum_dcSt = 70.6 - 1.45*(Dt_DMIn) + 0.424*Dt_ForNDF + \
            1.39*(Dt_StIn)/(Dt_DMIn)*100 - \
            0.0219*((Dt_StIn)/(Dt_DMIn)*100)**2 - \
            0.154*Dt_ForWet

    if Rum_dcSt < 0.1:                                                                      # Line 992
        Rum_dcSt = 0.1            

    elif Rum_dcSt > 100:                                                                    # Line 993
        Rum_dcSt = 100 

    Rum_DigStIn = Rum_dcSt / 100 * Dt_StIn                                                   # Line 998


    Du_MiN_NRC2021_g = calculate_Du_MiN_NRC2021_g(An_RDP, An_RDPIn, Dt_DMIn, Rum_DigNDFIn, Rum_DigStIn)
    # Du_MiN_VTln_g = calculate_Du_MiN_VTln_g(Dt_DMIn, Dt_AshIn, Dt_NDFIn, Dt_StIn, Dt_FAhydrIn, Dt_TPIn, Dt_NPNDMIn, Rum_DigStIn,
    #                                         Rum_DigNDFIn, An_RDPIn, Dt_ForNDFIn)
    # Du_MiN_VTnln_g = calculate_Du_MiN_VTnln_g(An_RDPIn, Rum_DigNDFIn, Rum_DigStIn)

    # return Du_MiN_NRC2021_g, Du_MiN_VTln_g, Du_MiN_VTnln_g
    return Du_MiN_NRC2021_g


def calculate_Du_MiN_NRC2021_g(An_RDP, An_RDPIn, Dt_DMIn, Rum_DigNDFIn, Rum_DigStIn): 
    # This has been tested and works

    VmMiNInt = 100.8                                                                        # Line 1117
    VmMiNRDPSlp = 81.56                                                                     # Line 1118
    KmMiNRDNDF = 0.0939                                                                     # Line 1119
    KmMiNRDSt = 0.0274                                                                      # Line 1120
    
    if An_RDP <= 12:                                                                        # Line 1124
        RDPIn_MiNmax = An_RDPIn
    else:
        RDPIn_MiNmax = Dt_DMIn * 0.12
        # RDP intake capped at 12% DM from Firkins paper
    MiN_Vm = VmMiNInt + VmMiNRDPSlp * RDPIn_MiNmax                                          # Line 1125            

    Du_MiN_NRC2021_g = MiN_Vm / (1 + KmMiNRDNDF / Rum_DigNDFIn + KmMiNRDSt / Rum_DigStIn)   # Line 1126

    return Du_MiN_NRC2021_g


def calculate_Du_MiN_VTln_g(Dt_DMIn, Dt_AshIn, Dt_NDFIn, Dt_StIn, Dt_FAhydrIn, Dt_TPIn, Dt_NPNDMIn, Rum_DigStIn,
                            Rum_DigNDFIn, An_RDPIn, Dt_ForNDFIn):
    # *** NEED TO TEST ***
    
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
    # *** NEED TO TEST ***

    Du_MiN_VTnln_g = 7.47 + 0.574 * An_RDPIn * 1000 / (1 + 3.60 / Rum_DigNDFIn + 12.3 / Rum_DigStIn)    # Line 1147

    return Du_MiN_VTnln_g


def calc_Mlk_NP_g(df, An_idRUPIn, Du_MiN_g, An_DEIn, An_DETPIn, An_DENPNCPIn, An_DigNDF, An_DEStIn, An_DEFAIn, An_DErOMIn, An_DENDFIn, An_BW):
    # This has been tested and works
    
    # Unpack the AA_values dataframe into dictionaries
    AA_list = ['Arg', 'His', 'Ile', 'Leu', 'Lys', 'Met', 'Phe', 'Thr', 'Trp', 'Val']
    Abs_AA_g = {}
    mPrt_k_AA = {}

    for AA in AA_list:
        Abs_AA_g[AA] = df.loc[AA, 'Abs_AA_g']
        mPrt_k_AA[AA] = df.loc[AA, 'mPrt_k_AA']

    # Calculate Mlk_NP_g
    mPrt_Int = -97                                      # Line 2097, 2078
    fMiTP_MiCP = 0.824                      			# Line 1120, Fraction of MiCP that is True Protein; from Lapierre or Firkins
    SI_dcMiCP = 80				                        # Line 1122, Digestibility coefficient for Microbial Protein (%) from NRC 2001
    mPrt_k_NEAA = 0                                     # Line 2103, 2094
    mPrt_k_OthAA = 0.0773                               # Line 2014, 2095
    mPrt_k_DEInp = 10.79                                # Line 2099, 2080
    mPrt_k_DigNDF = -4.595                              # Line 2100, 2081
    mPrt_k_DEIn_StFA = 0                                # Line 2101, 2082
    mPrt_k_DEIn_NDF = 0                                 # Line 2102, 2083
    mPrt_k_BW = -0.4201                                 # Line 2098, 2079

    Abs_EAA_g = Abs_AA_g['Arg'] + Abs_AA_g['His'] + Abs_AA_g['Ile'] + Abs_AA_g['Leu'] + Abs_AA_g['Lys'] \
                + Abs_AA_g['Met'] + Abs_AA_g['Phe'] + Abs_AA_g['Thr'] + Abs_AA_g['Trp'] + Abs_AA_g['Val']

    Du_MiCP_g = Du_MiN_g * 6.25                         # Line 1163
    Du_idMiCP_g =  SI_dcMiCP / 100 * Du_MiCP_g          # Line 1180 
    Du_idMiTP_g = fMiTP_MiCP * Du_idMiCP_g              # Line 1182
    Du_idMiTP = Du_idMiTP_g / 1000
    An_MPIn = An_idRUPIn + Du_idMiTP                    # Line 1236
    An_MPIn_g = An_MPIn * 1000                          # Line 1238
    Abs_neAA_g = An_MPIn_g * 1.15 - Abs_EAA_g           # Line 1771
    Abs_OthAA_g = Abs_neAA_g + Abs_AA_g['Arg'] + Abs_AA_g['Phe'] + Abs_AA_g['Thr'] + Abs_AA_g['Trp'] + Abs_AA_g['Val']
    Abs_EAA2b_g = Abs_AA_g['His']**2 + Abs_AA_g['Ile']**2 + Abs_AA_g['Leu']**2 + Abs_AA_g['Lys']**2 + Abs_AA_g['Met']**2        # Line 2106, 1778
    mPrtmx_Met2 = df.loc['Met', 'mPrtmx_AA2']
    mPrt_Met_0_1 = df.loc['Met', 'mPrt_AA_0.1']
    # Cannot call the variable mPrt_Met_0.1 in python, this is the only variable not consistent with R code
    Met_mPrtmx = df.loc['Met', 'AA_mPrtmx']
    An_DEInp = An_DEIn - An_DETPIn - An_DENPNCPIn

    #Scale the quadratic; can be calculated from any of the AA included in the squared term. All give the same answer
    mPrt_k_EAA2 = (2 * math.sqrt(mPrtmx_Met2**2 - mPrt_Met_0_1 * mPrtmx_Met2) - 2 * mPrtmx_Met2 + mPrt_Met_0_1) / (Met_mPrtmx * 0.1)**2
   

    Mlk_NP_g = mPrt_Int + Abs_AA_g['Arg'] * mPrt_k_AA['Arg'] + Abs_AA_g['His'] * mPrt_k_AA['His'] \
                + Abs_AA_g['Ile'] * mPrt_k_AA['Ile'] + Abs_AA_g['Leu'] * mPrt_k_AA['Leu'] \
                + Abs_AA_g['Lys'] * mPrt_k_AA['Lys'] + Abs_AA_g['Met'] * mPrt_k_AA['Met'] \
                + Abs_AA_g['Phe'] * mPrt_k_AA['Phe'] + Abs_AA_g['Thr'] * mPrt_k_AA['Thr'] \
                + Abs_AA_g['Trp'] * mPrt_k_AA['Trp'] + Abs_AA_g['Val'] * mPrt_k_AA['Val'] \
                + Abs_neAA_g * mPrt_k_NEAA + Abs_OthAA_g * mPrt_k_OthAA + Abs_EAA2b_g * mPrt_k_EAA2 \
                + An_DEInp * mPrt_k_DEInp + (An_DigNDF - 17.06) * mPrt_k_DigNDF + (An_DEStIn + An_DEFAIn + An_DErOMIn) \
                * mPrt_k_DEIn_StFA + An_DENDFIn * mPrt_k_DEIn_NDF + (An_BW - 612) * mPrt_k_BW 

    return Mlk_NP_g
    

def calc_Mlk_Fat_g(df, An_LactDay, Dt_DMIn, Dt_FAIn, Dt_DigC160In, Dt_DigC183In):
    # This has been tested and works
    Abs_Ile_g = df.loc['Ile', 'Abs_AA_g']
    Abs_Met_g = df.loc['Met', 'Abs_AA_g']

    # An_LactDay_MlkPred
    if An_LactDay <= 375:
        An_LactDay_MlkPred = An_LactDay
    elif An_LactDay > 375:
        An_LactDay_MlkPred = 375

    Mlk_Fat_g = 453 - 1.42 * An_LactDay_MlkPred + 24.52 * (Dt_DMIn - Dt_FAIn) + 0.41 * Dt_DigC160In * 1000 + 1.80 * Dt_DigC183In * 1000 + 1.45 * Abs_Ile_g + 1.34 * Abs_Met_g

    return Mlk_Fat_g


def calc_Mlk_Prod_comp(Mlk_NP_g, Mlk_Fat_g, An_DEIn, An_LactDay, An_Parity_rl):
    # This has been tested and works
    Mlk_NP = Mlk_NP_g / 1000                    # Line 2210, kg NP/d
    Mlk_Fat = Mlk_Fat_g / 1000

    # An_LactDay_MlkPred
    if An_LactDay <= 375:
        An_LactDay_MlkPred = An_LactDay
    elif An_LactDay > 375:
        An_LactDay_MlkPred = 375

    Mlk_Prod_comp = 4.541 + 11.13 * Mlk_NP + 2.648 * Mlk_Fat + 0.1829 * An_DEIn - 0.06257 * (An_LactDay_MlkPred - 137.1) + 2.766e-4 * (An_LactDay_MlkPred - 137.1)**2 \
                    + 1.603e-6 * (An_LactDay_MlkPred - 137.1)**3 - 7.397e-9 * (An_LactDay_MlkPred - 137.1)**4 + 1.567 * (An_Parity_rl - 1)
    return Mlk_Prod_comp


def calc_Mlk_Prod_MPalow(An_MPuse_g_Trg, Mlk_MPUse_g_Trg, An_idRUPIn, Du_idMiCP_g, Trg_MilkTPp):
    # Tested and works
    Kx_MP_NP_Trg = 0.69                                                                     # Line 2651, 2596
    fMiTP_MiCP = 0.824                                                          			# Line 1120, Fraction of MiCP that is True Protein; from Lapierre or Firkins

    Du_idMiTP_g = fMiTP_MiCP * Du_idMiCP_g                                                  # Line 1182
    Du_idMiTP = Du_idMiTP_g / 1000                                                          # Line 1183
    An_MPIn = An_idRUPIn + Du_idMiTP 


    An_MPavail_Milk_Trg = An_MPIn - An_MPuse_g_Trg / 1000 + Mlk_MPUse_g_Trg / 1000          # Line 2706
    Mlk_NP_MPalow_Trg_g = An_MPavail_Milk_Trg * Kx_MP_NP_Trg * 1000                         # Line 2707, g milk NP/d

    Mlk_Prod_MPalow = Mlk_NP_MPalow_Trg_g / (Trg_MilkTPp / 100) / 1000                      # Line 2708, kg milk/d using Trg milk protein % to predict volume

    return Mlk_Prod_MPalow


def calc_Mlk_Prod_NEalow(An_MEIn, An_MEgain, An_MEmUse, Gest_MEuse, Trg_NEmilk_Milk):
    # Tested and works
    Kl_ME_NE = 0.66

    An_MEavail_Milk = An_MEIn - An_MEgain - An_MEmUse - Gest_MEuse                      # Line 2896
    Mlk_Prod_NEalow = An_MEavail_Milk * Kl_ME_NE / Trg_NEmilk_Milk                  	# Line 2897, Energy allowable Milk Production, kg/d

    return Mlk_Prod_NEalow

