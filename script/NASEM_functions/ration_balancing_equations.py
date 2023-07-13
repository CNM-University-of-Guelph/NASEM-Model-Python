import math
import pandas as pd
import numpy as np


def calculate_Dt_DMIn_Lact1(An_Parity_rl, Trg_MilkProd, An_BW, An_BCS, An_LactDay, Trg_MilkFatp, Trg_MilkTPp, Trg_MilkLacp):
    
    Trg_NEmilk_Milk = 9.29*Trg_MilkFatp/100 + 5.85*Trg_MilkTPp/100 + 3.95*Trg_MilkLacp/100
    Trg_NEmilkOut = Trg_NEmilk_Milk * Trg_MilkProd                                         # Line 386
    
    term1 = (3.7 + 5.7 * (An_Parity_rl - 1) + 0.305 * Trg_NEmilkOut + 0.022 * An_BW +       # Line 389
             (-0.689 - 1.87 * (An_Parity_rl - 1)) * An_BCS)
    term2 = 1 - (0.212 + 0.136 * (An_Parity_rl - 1)) * math.exp(-0.053 * An_LactDay)
    Dt_DMIn_Lact1 = term1 * term2
    return Dt_DMIn_Lact1


def calculate_Du_MiCP_g(Dt_NDFIn, Dt_DMIn, Dt_StIn, Dt_CPIn, Dt_ADFIn, Dt_ForWet, Dt_RUPIn, Dt_ForNDFIn, Dt_RDPIn):
    # This has been tested and works
   
    # There are 3 equations for predicting microbial N, all 3 will be included and the MCP prediction from each will be displayed
    # Currently the default is the only one used

    # This will take the inputs and call the default NRC function fucntions

    Dt_ForNDF = Dt_ForNDFIn / Dt_DMIn * 100
    An_RDP = Dt_RDPIn / Dt_DMIn * 100

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


def calculate_Mlk_NP_g(df, Dt_idRUPIn, Du_MiN_g, An_DEIn, An_DETPIn, An_DENPNCPIn, An_DigNDFIn, An_DEStIn, An_DEFAIn, An_DErOMIn, An_DENDFIn, An_BW, Dt_DMIn):
    # This has been tested and works
    
    An_DigNDF = An_DigNDFIn / Dt_DMIn * 100
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
    An_MPIn = Dt_idRUPIn + Du_idMiTP                    # Line 1236
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

    return Mlk_NP_g, Du_idMiCP_g
    

def calculate_Mlk_Fat_g(df, Dt_FAIn, Dt_DigC160In, Dt_DigC183In, An_LactDay, Dt_DMIn):
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


def calculate_Mlk_Prod_comp(Mlk_NP_g, Mlk_Fat_g, An_DEIn, An_LactDay, An_Parity_rl):
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


def calculate_Mlk_Prod_MPalow(An_MPuse_g_Trg, Mlk_MPUse_g_Trg, An_idRUPIn, Du_idMiCP_g, Trg_MilkTPp):
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


def calculate_Mlk_Prod_NEalow(An_MEIn, An_MEgain, An_MEmUse, Gest_MEuse, Trg_MilkFatp, Trg_MilkTPp, Trg_MilkLacp):
    # Tested and works
    Kl_ME_NE = 0.66

    Trg_NEmilk_Milk = 9.29 * Trg_MilkFatp / 100 + 5.85 * Trg_MilkTPp / 100 + 3.95 * Trg_MilkLacp / 100
    An_MEavail_Milk = An_MEIn - An_MEgain - An_MEmUse - Gest_MEuse                      # Line 2896
    Mlk_Prod_NEalow = An_MEavail_Milk * Kl_ME_NE / Trg_NEmilk_Milk                  	# Line 2897, Energy allowable Milk Production, kg/d

    return Mlk_Prod_NEalow


def AA_calculations(Du_MiN_g, feed_data, diet_info):
    # This function will get the intakes of AA's from the diet and then do all the calculations 
    # of values other functions will need
    # The results will be saved to a dataframe with one row for each AA and a column for each calculated value
    AA_list = ['Arg', 'His', 'Ile', 'Leu', 'Lys', 'Met', 'Phe', 'Thr', 'Trp', 'Val']
    AA_values = pd.DataFrame(index=AA_list)
    Dt_IdAARUPIn = {}

    ####################
    # Get Diet Data
    ####################
    feed_columns = ['Fd_Arg_CP', 'Fd_His_CP', 'Fd_Ile_CP', 'Fd_Leu_CP', 'Fd_Lys_CP', 'Fd_Met_CP', 'Fd_Phe_CP', 'Fd_Thr_CP', 'Fd_Trp_CP', 'Fd_Val_CP', 'Fd_dcRUP']
    df_f = pd.DataFrame(feed_data[feed_columns])
    df_f['Fd_RUPIn'] = pd.Series(diet_info['Fd_RUPIn'])
   
    ####################
    # Define Variables
    ####################
    fMiTP_MiCP = 0.824			                                    # Line 1120, Fraction of MiCP that is True Protein; from Lapierre or Firkins
    SI_dcMiCP = 80				                                    # Line 1122, Digestibility coefficient for Microbial Protein (%) from NRC 2001
    K_305RHA_MlkTP = 1.0                                            # Line 2115, A scalar to adjust the slope if needed.  Assumed to be 1. MDH
    An_305RHA_MlkTP = 280                        # The default is 280 but the value for the test data is 400. This should be made an input for the model
    f_mPrt_max = 1 + K_305RHA_MlkTP * (An_305RHA_MlkTP / 280 - 1)       # Line 2116, 280kg RHA ~ 930 g mlk NP/d herd average
    Du_MiCP_g = Du_MiN_g * 6.25                                         # Line 1163
    Du_MiTP_g = fMiTP_MiCP * Du_MiCP_g                                  # Line 1166

    # AA recovery factors for recovery of each AA at maximum release in hydrolysis time over 24 h release (g true/g at 24 h)
    # From Lapierre, H., et al., 2016. Pp 205-219. in Proc. Cornell Nutrition Conference for feed manufacturers. 
    # Key roles of amino acids in cow performance and metabolism ? considerations for defining amino acid requirement. 
    # Inverted relative to that reported by Lapierre so they are true recovery factors, MDH
    RecArg = 1 / 1.061              # Line 1462-1471
    RecHis = 1 / 1.073
    RecIle = 1 / 1.12
    RecLeu = 1 / 1.065
    RecLys = 1 / 1.066
    RecMet = 1 / 1.05
    RecPhe = 1 / 1.061
    RecThr = 1 / 1.067
    RecTrp = 1 / 1.06
    RecVal = 1 / 1.102

    # Digested endogenous protein is ignored as it is a recycle of previously absorbed AA.
    # SI Digestibility of AA relative to RUP digestibility ([g dAA / g AA] / [g dRUP / g RUP])
    # All set to 1 due to lack of clear evidence for deviations.
    SIDigArgRUPf = 1
    SIDigHisRUPf = 1
    SIDigIleRUPf = 1
    SIDigLeuRUPf = 1
    SIDigLysRUPf = 1
    SIDigMetRUPf = 1
    SIDigPheRUPf = 1
    SIDigThrRUPf = 1
    SIDigTrpRUPf = 1
    SIDigValRUPf = 1

    # Microbial protein AA profile (g hydrated AA / 100 g TP) corrected for 24h hydrolysis recovery. 
    # Sok et al., 2017 JDS
    MiTPArgProf = 5.47
    MiTPHisProf = 2.21
    MiTPIleProf = 6.99
    MiTPLeuProf = 9.23
    MiTPLysProf = 9.44
    MiTPMetProf = 2.63
    MiTPPheProf = 6.30
    MiTPThrProf = 6.23
    MiTPTrpProf = 1.37
    MiTPValProf = 6.88

    # NRC derived Coefficients from Dec. 20, 2020 solutions. AIC=10,631
    # Two other sets of values are included in the R code
    
    # May be unused
    mPrt_Int_src = -97.0 
    mPrt_k_BW_src = -0.4201
    mPrt_k_DEInp_src = 10.79
    mPrt_k_DigNDF_src = -4.595
    mPrt_k_DEIn_StFA_src = 0        #DEStIn + DErOMIn + DEFAIn
    mPrt_k_DEIn_NDF_src = 0         #DENDFIn

    mPrt_k_Arg_src = 0
    mPrt_k_His_src = 1.675
    mPrt_k_Ile_src = 0.885
    mPrt_k_Leu_src = 0.466
    mPrt_k_Lys_src = 1.153	
    mPrt_k_Met_src = 1.839
    mPrt_k_Phe_src = 0
    mPrt_k_Thr_src = 0
    mPrt_k_Trp_src = 0
    mPrt_k_Val_src = 0

    # May be unused
    mPrt_k_NEAA_src = 0         #NEAA.  Phe, Thr, Trp, and Val not considered.
    mPrt_k_OthAA_src = 0.0773   #NEAA + unused EAA.  Added for NRC eqn without Arg as slightly superior.

    mPrt_k_EAA2_src = -0.00215

    
    for AA in AA_list:
        ##############################
        # Calculations on Diet Data
        ##############################
        # Fd_AAt_CP         
        df_f['Fd_{}t_CP'.format(AA)] = df_f['Fd_{}_CP'.format(AA)] / eval('Rec{}'.format(AA))

        # Fd_AARUPIn         
        df_f['Fd_{}RUPIn'.format(AA)] = df_f['Fd_{}t_CP'.format(AA)] / 100 * df_f['Fd_RUPIn'] * 1000

        # Fd_IdAARUPIn      
        df_f['Fd_Id{}RUPIn'.format(AA)] = df_f['Fd_dcRUP'] / 100 * df_f['Fd_{}RUPIn'.format(AA)] * eval('SIDig{}RUPf'.format(AA))
    
        # Dt_IdAARUPIn      
        Dt_IdAARUPIn['Dt_Id{}_RUPIn'.format(AA)] = df_f['Fd_Id{}RUPIn'.format(AA)].sum()

        ########################################
        # Calculations for Microbial Protein and Total AA Intake
        ########################################
        # Du_AAMic      
        AA_values.loc[AA, 'Du_AAMic'] = Du_MiTP_g * eval('MiTP{}Prof'.format(AA)) / 100         # Line 1573-1582

        # Du_IdAAMic        
        AA_values.loc[AA, 'Du_IdAAMic'] = AA_values.loc[AA, 'Du_AAMic'] * SI_dcMiCP / 100       # Line 1691-1700

        # Abs_AA_g
        # No infusions so Dt_IdAAIn, An_IdAA_In and Abs_AA_g are all the same value in this case
        AA_values.loc[AA, 'Abs_AA_g'] = AA_values.loc[AA, 'Du_IdAAMic'] + Dt_IdAARUPIn['Dt_Id{}_RUPIn'.format(AA)]     # Line 1703, 1714, 1757

        ########################################
        # Calculations for AA coefficients
        ########################################
        #mPrtmx_AA      CORRECT
        AA_values.loc[AA, 'mPrtmx_AA'] = -(eval('mPrt_k_{}_src'.format(AA)))**2 / (4 * mPrt_k_EAA2_src)
        
        #mPrtmx_AA2        CORRECT
        AA_values.loc[AA, 'mPrtmx_AA2'] = AA_values.loc[AA, 'mPrtmx_AA'] * f_mPrt_max                   # Line 2149-2158

        #AA_mPrtmx
        AA_values.loc[AA, 'AA_mPrtmx'] = -(eval('mPrt_k_{}_src'.format(AA))) / (2 * mPrt_k_EAA2_src)

        #mPrt_AA_0.1
        AA_values.loc[AA, 'mPrt_AA_0.1'] = AA_values.loc[AA, 'AA_mPrtmx'] * 0.1 * eval('mPrt_k_{}_src'.format(AA)) \
                                           + (AA_values.loc[AA, 'AA_mPrtmx'] * 0.1)**2 * mPrt_k_EAA2_src

        #mPrt_k_AA
        if AA_values.loc[AA, 'mPrtmx_AA2'] ** 2 - AA_values.loc[AA, 'mPrt_AA_0.1'] * AA_values.loc[AA, 'mPrtmx_AA2'] <= 0 or AA_values.loc[AA, 'AA_mPrtmx'] == 0:
        # Check for sqrt of 0 or divide by 0 errors and set value to 0 if encountered
            AA_values.loc[AA, 'mPrt_k_AA'] = 0
        else:
            AA_values.loc[AA, 'mPrt_k_AA'] = -(2 * np.sqrt(AA_values.loc[AA, 'mPrtmx_AA2'] ** 2 \
                                                - AA_values.loc[AA, 'mPrt_AA_0.1'] * AA_values.loc[AA, 'mPrtmx_AA2']) \
                                                - 2 * AA_values.loc[AA, 'mPrtmx_AA2']) \
                                                / (AA_values.loc[AA, 'AA_mPrtmx'] * 0.1)

    # df_f and Dt_IdAARUPIn not being returned but can be if values are needed outside this function
    # Currently they are not used anywhere else
    return AA_values


def calculate_An_NE(Dt_CPIn, Dt_FAIn, Mlk_NP_g, An_DEIn, An_DigNDFIn, Fe_CP, Fe_CPend_g, Dt_DMIn, An_BW, An_BW_mature, Trg_FrmGain, An_GestDay, 
                    An_GestLength, An_LactDay, Trg_RsrvGain, Fet_BWbrth, An_AgeDay, An_Parity_rl):
# This has been tested and works 
# Some of the calculations for gravid uterus are repeated in ME/MP requirements. Once order of calculations set it can be removed from one
# Included this as a function as it has many steps, many of the intermediate values should also be stored somewhere in the future 

    #######################
    ### An_GasEOut_Lact ###
    #######################
    An_DigNDF = An_DigNDFIn / Dt_DMIn * 100
    An_GasEOut_Lact = 0.294 * Dt_DMIn - 0.347 * Dt_FAIn / Dt_DMIn * 100 + 0.0409 * An_DigNDF

    ################
    ### Ur_DEout ###
    ################
    Scrf_CP_g = 0.20 * An_BW**0.60                                                                      # Line 1965
    Mlk_CP_g = Mlk_NP_g / 0.95                                          # Line 2213
    CPGain_FrmGain = 0.201 - 0.081 * An_BW / An_BW_mature
    Body_NP_CP = 0.86                                                      # Line 1964
    Frm_Gain = Trg_FrmGain
    An_GutFill_BW = 0.18                                                   # Line 2400 and 2411
    Frm_Gain_empty = Frm_Gain * (1 - An_GutFill_BW)
    NPGain_FrmGain = CPGain_FrmGain * Body_NP_CP                           # Line 2460
    Frm_NPgain = NPGain_FrmGain * Frm_Gain_empty                           # Line 2461
    CPGain_RsrvGain = 0.068                                           # Line 2466
    NPGain_RsrvGain = CPGain_RsrvGain * Body_NP_CP                    # Line 2467
    Rsrv_Gain_empty = Trg_RsrvGain                                    # Line 2435 and 2441
    Rsrv_NPgain = NPGain_RsrvGain * Rsrv_Gain_empty                    # Line 2468
    Body_NPgain = Frm_NPgain + Rsrv_NPgain
    Body_CPgain = Body_NPgain / Body_NP_CP                                  # Line 2475
    Body_CPgain_g = Body_CPgain * 1000                                      # Line 2477

    #Gest_CPuse_g#
    GrUter_Ksyn = 2.43e-2                                         # Line 2302
    GrUter_KsynDecay = 2.45e-5                                    # Line 2303
    UterWt_FetBWbrth = 0.2311                                     # Line 2296
    Uter_Wtpart = Fet_BWbrth * UterWt_FetBWbrth                   # Line 2311
    Uter_Ksyn = 2.42e-2                                           # Line 2306
    Uter_KsynDecay = 3.53e-5                                      # Line 2307
    Uter_Kdeg = 0.20                                              # Line 2308
    Uter_Wt = 0.204                                               # Line 2312-2318
    
    if An_AgeDay < 240:
      Uter_Wt = 0
    
    if An_GestDay > 0 and An_GestDay <= An_GestLength:
      Uter_Wt = Uter_Wtpart * math.exp(-(Uter_Ksyn-Uter_KsynDecay*An_GestDay)*(An_GestLength-An_GestDay))

    if An_GestDay <= 0 and An_LactDay > 0 and An_LactDay < 100:
      Uter_Wt = ((Uter_Wtpart-0.204)* math.exp(-Uter_Kdeg*An_LactDay))+0.204

    if An_Parity_rl > 0 and Uter_Wt < 0.204:
      Uter_Wt = 0.204
    
    GrUterWt_FetBWbrth = 1.816                                    # Line 2295
    GrUter_Wtpart = Fet_BWbrth * GrUterWt_FetBWbrth               # Line 2322
    GrUter_Wt = Uter_Wt                                           # Line 2323-2327   

    if An_GestDay > 0 and An_GestDay <= An_GestLength:
      GrUter_Wt = GrUter_Wtpart * math.exp(-(GrUter_Ksyn-GrUter_KsynDecay*An_GestDay)*(An_GestLength-An_GestDay))

    if GrUter_Wt < Uter_Wt:
      GrUter_Wt = Uter_Wt
    
    Uter_BWgain = 0  #Open and nonregressing animal

    if An_GestDay > 0 and An_GestDay <= An_GestLength:
      Uter_BWgain = (Uter_Ksyn - Uter_KsynDecay * An_GestDay) * Uter_Wt

    if An_GestDay <= 0 and An_LactDay > 0 and An_LactDay < 100:
      Uter_BWgain = -Uter_Kdeg*Uter_Wt
    
    GrUter_BWgain = 0                                              # Line 2341-2345

    if An_GestDay > 0 and An_GestDay <= An_GestLength:
      GrUter_BWgain = (GrUter_Ksyn-GrUter_KsynDecay*An_GestDay)*GrUter_Wt

    if An_GestDay <= 0 and An_LactDay > 0 and An_LactDay < 100:
      GrUter_BWgain = Uter_BWgain
 
    CP_GrUtWt = 0.123                                               # Line 2298, kg CP/kg fresh Gr Uterus weight
    Gest_NPother_g = 0                                              # Line 2353, Net protein gain in other maternal tissues during late gestation: mammary, intestine, liver, and blood. This should be replaced with a growth funncton such as Dijkstra's mammary growth equation. MDH.                                                              
    Gest_NCPgain_g = GrUter_BWgain * CP_GrUtWt * 1000
    Gest_NPgain_g = Gest_NCPgain_g * Body_NP_CP
    Gest_NPuse_g = Gest_NPgain_g + Gest_NPother_g                             # Line 2366
    Gest_CPuse_g = Gest_NPuse_g / Body_NP_CP                                  # Line 2367
    Ur_Nout_g = (Dt_CPIn * 1000 - Fe_CP * 1000 - Scrf_CP_g - Fe_CPend_g - Mlk_CP_g - Body_CPgain_g - Gest_CPuse_g) / 6.25     # Line 2742
    Ur_DEout = 0.0143 * Ur_Nout_g                               # Line 2748

    An_MEIn = An_DEIn - An_GasEOut_Lact - Ur_DEout
    An_NE_In = An_MEIn * 0.66                                  # Line 2762
    An_NE = An_NE_In / Dt_DMIn                                 # Line 2763

    return An_NE, An_MEIn


def calculate_An_DEIn(Dt_DigNDFIn_Base, Dt_NDFIn, Dt_DigStIn_Base, Dt_StIn, Dt_DigrOMtIn, An_CPIn, An_RUPIn, Dt_idRUPIn, Dt_NPNCPIn, Dt_DigFAIn, Du_MiN_g, An_BW, Dt_DMIn):
# Tested and works
# Consider renaiming as this really calculates all of the DE intakes as well as the total

    # Replaces An_NDF as input
    An_NDF = Dt_NDFIn / Dt_DMIn * 100

    #An_DigNDFIn#
    TT_dcNDF_Base = Dt_DigNDFIn_Base / Dt_NDFIn * 100                     # Line 1056
    if math.isnan(TT_dcNDF_Base) is True:
        TT_dcNDF_Base = 0

    An_DMIn_BW = Dt_DMIn / An_BW
    En_NDF = 4.2

    if TT_dcNDF_Base == 0:
        TT_dcNDF = 0
    else:
        TT_dcNDF = (TT_dcNDF_Base / 100 - 0.59 * (Dt_StIn / Dt_DMIn - 0.26) - 1.1 * (An_DMIn_BW - 0.035)) * 100       # Line 1060


    Dt_DigNDFIn = TT_dcNDF / 100 * Dt_NDFIn
    
    
    An_DigNDFIn = Dt_DigNDFIn + 0 * TT_dcNDF/100                                    # Line 1063, the 0 is a placeholder for InfRum_NDFIn, ask Dave about this, I think the TT_dcNDF is not needed
    An_DENDFIn = An_DigNDFIn * En_NDF                                               # Line 1353
    
    #An_DEStIn#
    En_St = 4.23                                                                   # Line 271
    TT_dcSt_Base = Dt_DigStIn_Base / Dt_StIn * 100                                 # Line 1030    
    if math.isnan(TT_dcSt_Base) is True:
        TT_dcSt_Base = 0

    if TT_dcSt_Base == 0:
        TT_dcSt = 0
    else:
        TT_dcSt = TT_dcSt_Base - (1.0 * (An_DMIn_BW - 0.035)) * 100                 # Line 1032
    An_DigStIn = Dt_StIn * TT_dcSt / 100                                            # Line 1033
    An_DEStIn = An_DigStIn * En_St                                                  # Line 1351

    #An_DErOMIn#
    En_rOM = 4.0                                                                    # Line 271
    Fe_rOMend_DMI = 3.43                                                            # Line 1005, 3.43% of DMI
    Fe_rOMend = Fe_rOMend_DMI / 100 * Dt_DMIn                               	    # Line 1007, From Tebbe et al., 2017.  Negative interecept represents endogenous rOM
    An_DigrOMaIn = Dt_DigrOMtIn - Fe_rOMend                                         # Line 1024, 1022
    An_DErOMIn = An_DigrOMaIn * En_rOM                                              # Line 1352

    #An_DETPIn#
    SI_dcMiCP = 80			                                                    	# Line 1123, Digestibility coefficient for Microbial Protein (%) from NRC 2001 
    En_CP = 5.65                                                                    # Line 266
    dcNPNCP = 100	                                                                # Line 1092, urea and ammonium salt digestibility
    En_NPNCP = 0.89                                                                 # Line 270
    An_idRUPIn = Dt_idRUPIn                                       # Line 1099
    Fe_RUP = An_RUPIn - An_idRUPIn                                                  # Line 1198   
    Du_MiCP_g = Du_MiN_g * 6.25                                                     # Line 1164
    Du_MiCP = Du_MiCP_g / 1000                                                      # Line 1166
    Du_idMiCP_g = SI_dcMiCP / 100 * Du_MiCP_g
    Du_idMiCP = Du_idMiCP_g / 1000
    Fe_RumMiCP = Du_MiCP - Du_idMiCP                                                # Line 1196
    Fe_CPend_g = (12 + 0.12 * An_NDF) * Dt_DMIn            # line 1187, g/d, endogen secretions plus urea capture in microbies in rumen and LI
    Fe_CPend = Fe_CPend_g / 1000                                                    # Line 1190
    Fe_CP = Fe_RUP + Fe_RumMiCP + Fe_CPend          # Line 1202, Double counting portion of RumMiCP derived from End CP. Needs to be fixed. MDH
    An_DigCPaIn = An_CPIn - Fe_CP		            # Line 1222, apparent total tract
    An_DECPIn = An_DigCPaIn * En_CP
    An_DENPNCPIn = Dt_NPNCPIn * dcNPNCP / 100 * En_NPNCP                                                          # Line 1355, 1348
    An_DETPIn = An_DECPIn - An_DENPNCPIn / En_NPNCP * En_CP                       # Line 1356, Caution! DigTPaIn not clean so subtracted DE for CP equiv of NPN to correct. Not a true DE_TP.

    #An_DEFAIn#
    En_FA = 9.4                                                                                         # Line 265
    An_DigFAIn = Dt_DigFAIn                                                                             # Line 1309
    An_DEFAIn = An_DigFAIn * En_FA

    An_DEIn = An_DENDFIn + An_DEStIn + An_DErOMIn + An_DETPIn + An_DENPNCPIn + An_DEFAIn  # Line 1367

    return An_DEIn, An_DENPNCPIn, An_DETPIn, An_DigNDFIn, An_DEStIn, An_DEFAIn, An_DErOMIn, An_DENDFIn, Fe_CP, Fe_CPend_g


