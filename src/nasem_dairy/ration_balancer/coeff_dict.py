# This dictionary contains the coefficients used by the model
# The dictionary will be parsed to various functions which will check for that the required coeffs are present
# before proceeding with the rest of the function. 

coeff_dict = {
# From calculate_Du_MiN_NRC2021_g
    'VmMiNInt': 100.8,                                    # Line 1117
    'VmMiNRDPSlp': 81.56,                                 # Line 1118
    'KmMiNRDNDF': 0.0939,                                 # Line 1119
    'KmMiNRDSt': 0.0274,                                  # Line 1120

# From calculate_Du_MiN_VTLn_g
    'Int_MiN_VT': 18.686,                                 # Line 1134
    'KrdSt_MiN_VT': 10.214,                               # Line 1135
    'KrdNDF_MiN_VT': 28.976,                              # Line 1136
    'KRDP_MiN_VT': 43.405,                                # Line 1137
    'KrOM_MiN_VT': -11.731,                               # Line 1138
    'KForNDF_MiN_VT': 8.895,                              # Line 1139
    'KrOM2_MiN_VT': 2.861,                                # Line 1140
    'KrdStxrOM_MiN_VT': 5.637,                            # Line 1141
    'KrdNDFxForNDF_MiN_VT': -2.22,                        # Line 1142

# From calculate_Mlk_NP_g
    'mPrt_Int': -97,                                      # Line 2097, 2078
    'fMiTP_MiCP': 0.824,                      			  # Line 1120, Fraction of MiCP that is True Protein; from Lapierre or Firkins
    'SI_dcMiCP': 80,				                      # Line 1122, Digestibility coefficient for Microbial Protein (%) from NRC 2001
    'mPrt_k_NEAA': 0,                                     # Line 2103, 2094
    'mPrt_k_OthAA': 0.0773,                               # Line 2014, 2095
    'mPrt_k_DEInp': 10.79,                                # Line 2099, 2080
    'mPrt_k_DigNDF': -4.595,                              # Line 2100, 2081
    'mPrt_k_DEIn_StFA': 0,                                # Line 2101, 2082
    'mPrt_k_DEIn_NDF': 0,                                 # Line 2102, 2083
    'mPrt_k_BW': -0.4201,                                 # Line 2098, 2079

# From calculate_Mlk_Prod_MPalow
    'Kx_MP_NP_Trg': 0.69,                                 # Line 2651, 2596
    'fMiTP_MiCP': 0.824,                                  # Line 1120, Fraction of MiCP that is True Protein; from Lapierre or Firkins

# From calculate_Mlk_Prod_NEalow
    'Kl_ME_NE': 0.66,

# From AA_calculations
    'fMiTP_MiCP': 0.824,			                                    # Line 1120, Fraction of MiCP that is True Protein; from Lapierre or Firkins
    'SI_dcMiCP': 80,				                                    # Line 1122, Digestibility coefficient for Microbial Protein (%) from NRC 2001
    'K_305RHA_MlkTP': 1.0,                                            # Line 2115, A scalar to adjust the slope if needed.  Assumed to be 1. MDH
    
    # AA recovery factors for recovery of each AA at maximum release in hydrolysis time over 24 h release (g true/g at 24 h)
    # From Lapierre, H., et al., 2016. Pp 205-219. in Proc. Cornell Nutrition Conference for feed manufacturers. 
    # Key roles of amino acids in cow performance and metabolism ? considerations for defining amino acid requirement. 
    # Inverted relative to that reported by Lapierre so they are true recovery factors, MDH
    'RecArg': 1 / 1.061,              # Line 1462-1471
    'RecHis': 1 / 1.073,
    'RecIle': 1 / 1.12,
    'RecLeu': 1 / 1.065,
    'RecLys': 1 / 1.066,
    'RecMet': 1 / 1.05,
    'RecPhe': 1 / 1.061,
    'RecThr': 1 / 1.067,
    'RecTrp': 1 / 1.06,
    'RecVal': 1 / 1.102,
    
    # Microbial protein AA profile (g hydrated AA / 100 g TP) corrected for 24h hydrolysis recovery. 
    # Sok et al., 2017 JDS
    'MiTPArgProf': 5.47,
    'MiTPHisProf': 2.21,
    'MiTPIleProf': 6.99,
    'MiTPLeuProf': 9.23,
    'MiTPLysProf': 9.44,
    'MiTPMetProf': 2.63,
    'MiTPPheProf': 6.30,
    'MiTPThrProf': 6.23,
    'MiTPTrpProf': 1.37,
    'MiTPValProf': 6.88,

    # NRC derived Coefficients from Dec. 20, 2020 solutions. AIC=10,631
    # Two other sets of values are included in the R code
    'mPrt_k_Arg_src': 0,
    'mPrt_k_His_src': 1.675,
    'mPrt_k_Ile_src': 0.885,
    'mPrt_k_Leu_src': 0.466,
    'mPrt_k_Lys_src': 1.153,
    'mPrt_k_Met_src': 1.839,
    'mPrt_k_Phe_src': 0,
    'mPrt_k_Thr_src': 0,
    'mPrt_k_Trp_src': 0,
    'mPrt_k_Val_src': 0,

    'mPrt_k_EAA2_src': -0.00215,

# From calculate_An_NE
    'Body_NP_CP': 0.86,                                             # Line 1964
    'An_GutFill_BW': 0.18,                                          # Line 2400 and 2411
    'CPGain_RsrvGain': 0.068,                                       # Line 2466
    'GrUter_BWgain': 0,                                             # Line 2341-2345
    'CP_GrUtWt': 0.123,                                             # Line 2298, kg CP/kg fresh Gr Uterus weight
    'Gest_NPother_g': 0,                                            # Line 2353, Net protein gain in other maternal tissues during late gestation: mammary, intestine, liver, and blood. This should be replaced with a growth funncton such as Dijkstra's mammary growth equation. MDH.

# From calculate_An_DEIn
    'En_NDF': 4.2,
    'En_St': 4.23,
    'En_rOM': 4.0,                                                                    # Line 271
    'Fe_rOMend_DMI': 3.43,                                                            # Line 1005, 3.43% of DMI
    'SI_dcMiCP': 80,			                                                    	# Line 1123, Digestibility coefficient for Microbial Protein (%) from NRC 2001 
    'En_CP': 5.65,                                                                    # Line 266
    'dcNPNCP': 100,	                                                                # Line 1092, urea and ammonium salt digestibility
    'En_NPNCP': 0.89,                                                                 # Line 270
    'En_FA': 9.4,                                                                      # Line 265

# From calculate GrUter_BWgain
    'GrUter_Ksyn': 2.43e-2,                                         # Line 2302
    'GrUter_KsynDecay': 2.45e-5,                                    # Line 2303
    'UterWt_FetBWbrth': 0.2311,                                     # Line 2296
    'Uter_Ksyn': 2.42e-2,                                           # Line 2306
    'Uter_KsynDecay': 3.53e-5,                                      # Line 2307
    'Uter_Kdeg': 0.20,                                              # Line 2308
    'Uter_Wt': 0.204,                                               # Line 2312-2318
    'GrUterWt_FetBWbrth': 1.816,                                    # Line 2295
    'Uter_BWgain': 0,                                                # Open and nonregressing animal

# From calculate_An_MEmUse
    'An_NEmUse_Env': 0,                                               # Line 2785
    'Km_ME_NE': 0.66,

# From calculate_An_MEgain
    'FatGain_RsrvGain': 0.622,                       # Line 2451
    'Kr_ME_RE': 0.60,                                # Line 2834
    'Body_NP_CP': 0.86,                              # Line 1963
    'Kf_ME_RE': 0.4,                                 # Line 2831

# From calculate_Gest_MEuse
    'NE_GrUtWt': 0.95,                                # Line 2297

# From calculate_Trg_Mlk_MEout
    'Kl_ME_NE': 0.66,                                   # Line 2823

# From calculate_An_MPm_g_Trg
    'Km_MP_NP_Trg': 0.69,                            # Line 54, 2596, 2651 and 2652
    'Body_NP_CP': 0.86,                              # Line 1963

# From calculate_Body_MPuse_g_Trg
    'Kg_MP_NP_Trg': 0.69,                            # Line 54, 2665

# From calculate_Gest_MPuse_g_Trg
    'Ky_MP_NP_Trg': 0.33,                               # Line 2656
    'Ky_NP_MP_Trg': 1.0,                                # Line 2657

# From calculate_Mlk_MPuse_g_Trg
    'Kl_MP_NP_Trg': 0.69,                                # Line 54, 2596, 2651, 2654

# From get_nutrient_intakes
    'Fd_dcrOM': 96,                                     # Line 1005, this is a true digestbility.  There is a neg intercept of -3.43% of DM
    'fCPAdu': 0.064,
    'KpFor': 4.87,                                      #%/h
    'KpConc': 5.28,                                     #From Bayesian fit to Digesta Flow data with Seo Kp as priors, eqn. 26 in Hanigan et al.
    'IntRUP': -0.086,                                   #Intercept, kg/d
    'refCPIn': 3.39,                                    #average CPIn for the DigestaFlow dataset, kg/d.  3/21/18, MDH
    'TT_dcFA_Base': 73,
    'TT_dcFat_Base': 68
}