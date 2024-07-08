"""
This module contains two default dictionaries that are imported with nasem_dairy package. 
These default values are from the original R Code version of the model and most users would not change. 
However, they parsed to functions that need any of these values, so users can alter this dictionary and give to functions as needed.

- `coeff_dict` - coefficients used throughout the model.
- `infusion_dict` - All required infusion values set to 0, for when no infusions are used. Normally only used by researchers familiar with infusion techniques.
- `MP_NP_efficiency_dict` - coefficients (efficiencies) for conversions of MP to NP for individual AA
- `mPrt_coeff_list` - a list of dictionaries with coefficients for microbial protein equations
- `f_Imb` - an array of 1's for individual AA, currently all are 1 but could be a relative penalty provided by user

Examples
--------
```{python}
import nasem_dairy as nd

nd.coeff_dict
```

```{python}
nd.infusion_dict
```

"""
import pandas as pd

# This dictionary contains the coefficients used by the model
# The dictionary will be parsed to various functions which will check for that the required coeffs are present
# before proceeding with the rest of the function.

coeff_dict = {
    # From calculate_Du_MiN_NRC2021_g
    'VmMiNInt': 100.8,  # Line 1117
    'VmMiNRDPSlp': 81.56,  # Line 1118
    'KmMiNRDNDF': 0.0939,  # Line 1119
    'KmMiNRDSt': 0.0274,  # Line 1120

    # From calculate_Du_MiN_VTLn_g
    'Int_MiN_VT': 18.686,  # Line 1134
    'KrdSt_MiN_VT': 10.214,  # Line 1135
    'KrdNDF_MiN_VT': 28.976,  # Line 1136
    'KRDP_MiN_VT': 43.405,  # Line 1137
    'KrOM_MiN_VT': -11.731,  # Line 1138
    'KForNDF_MiN_VT': 8.895,  # Line 1139
    'KrOM2_MiN_VT': 2.861,  # Line 1140
    'KrdStxrOM_MiN_VT': 5.637,  # Line 1141
    'KrdNDFxForNDF_MiN_VT': -2.22,  # Line 1142

    # Line 1120, Fraction of MiCP that is True Protein; from Lapierre or Firkins
    'fMiTP_MiCP': 0.824,
    # Line 1122, Digestibility coefficient for Microbial Protein (%) from NRC 2001
    'SI_dcMiCP': 80,
    # 'mPrt_k_NEAA': 0,  # Line 2103, 2094
    # 'mPrt_k_OthAA': 0.0773,  # Line 2014, 2095
    # 'mPrt_k_DEInp': 10.79,  # Line 2099, 2080
    # 'mPrt_k_DigNDF': -4.595,  # Line 2100, 2081
    # 'mPrt_k_DEIn_StFA': 0,  # Line 2101, 2082
    # 'mPrt_k_DEIn_NDF': 0,  # Line 2102, 2083
    # 'mPrt_k_BW': -0.4201,  # Line 2098, 2079

    # From calculate_Mlk_Prod_MPalow
    'Kx_MP_NP_Trg': 0.69,  # Line 2651, 2596
    # Line 1120, Fraction of MiCP that is True Protein; from Lapierre or Firkins
    'fMiTP_MiCP': 0.824,

    # From calculate_Mlk_Prod_NEalow
    'Kl_ME_NE': 0.66,

    # From AA_calculations
    # Line 1120, Fraction of MiCP that is True Protein; from Lapierre or Firkins
    'fMiTP_MiCP': 0.824,
    # Line 1122, Digestibility coefficient for Microbial Protein (%) from NRC 2001
    'SI_dcMiCP': 80,
    # Line 2115, A scalar to adjust the slope if needed.  Assumed to be 1. MDH
    'K_305RHA_MlkTP': 1.0,

    # AA recovery factors for recovery of each AA at maximum release in hydrolysis time over 24 h release (g true/g at 24 h)
    # From Lapierre, H., et al., 2016. Pp 205-219. in Proc. Cornell Nutrition Conference for feed manufacturers.
    # Key roles of amino acids in cow performance and metabolism ? considerations for defining amino acid requirement.
    # Inverted relative to that reported by Lapierre so they are true recovery factors, MDH
    'RecArg': 1 / 1.061,  # Line 1462-1471
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
    # Two other sets of values are included in the R
    # NOTE added to their own dictionary
    # 'mPrt_k_Arg_src': 0,
    # 'mPrt_k_His_src': 1.675,
    # 'mPrt_k_Ile_src': 0.885,
    # 'mPrt_k_Leu_src': 0.466,
    # 'mPrt_k_Lys_src': 1.153,
    # 'mPrt_k_Met_src': 1.839,
    # 'mPrt_k_Phe_src': 0,
    # 'mPrt_k_Thr_src': 0,
    # 'mPrt_k_Trp_src': 0,
    # 'mPrt_k_Val_src': 0,
    # 'mPrt_k_EAA2_src': -0.00215,

    # From calculate_An_NE
    'Body_NP_CP': 0.86,  # Line 1964
    'CPGain_RsrvGain': 0.068,  # Line 2466
    # Line 2341-2345
    'GrUter_BWgain': 0,
    # Line 2298, kg CP/kg fresh Gr Uterus weight
    'CP_GrUtWt': 0.123,
    # Line 2353, Net protein gain in other maternal tissues during late gestation: mammary, intestine, liver, and blood. This should be replaced with a growth funncton such as Dijkstra's mammary growth equation. MDH.
    'Gest_NPother_g': 0,

    # From calculate_An_DEIn
    'En_NDF': 4.2,
    'En_St': 4.23,
    # Line 271
    'En_rOM': 4.0,
    # Line 1005, 3.43% of DMI
    'Fe_rOMend_DMI': 3.43,
    # Line 1123, Digestibility coefficient for Microbial Protein (%) from NRC 2001
    'SI_dcMiCP': 80,
    # Line 266
    'En_CP': 5.65,
    # Line 1092, urea and ammonium salt digestibility
    'dcNPNCP': 100,
    # Line 270
    'En_NPNCP': 0.89,
    # Line 265
    'En_FA': 9.4,

    # From calculate GrUter_BWgain
    'GrUter_Ksyn': 2.43e-2,  # Line 2302
    'GrUter_KsynDecay': 2.45e-5,  # Line 2303
    'UterWt_FetBWbrth': 0.2311,  # Line 2296
    'Uter_Ksyn': 2.42e-2,  # Line 2306
    'Uter_KsynDecay': 3.53e-5,  # Line 2307
    'Uter_Kdeg': 0.20,  # Line 2308
    # Line 2312-2318
    'Uter_Wt': 0.204,
    'GrUterWt_FetBWbrth': 1.816,  # Line 2295
    # Open and nonregressing animal
    'Uter_BWgain': 0,

    # From calculate_An_MEmUse
    'An_NEmUse_Env': 0,  # Line 2785

    # From calculate_An_MEgain
    'FatGain_RsrvGain': 0.622,  # Line 2451

    # From calculate_Gest_MEuse
    'NE_GrUtWt': 0.95,  # Line 2297

    # From calculate_Trg_Mlk_MEout
    'Kl_ME_NE': 0.66,  # Line 2823

    # From calculate_An_MPm_g_Trg
    'Km_MP_NP_Trg': 0.69,  # Line 54, 2596, 2651 and 2652

    # From calculate_Body_MPuse_g_Trg
    'Kg_MP_NP_Trg': 0.69,  # Line 54, 2665

    # From calculate_Gest_MPuse_g_Trg
    'Ky_MP_NP_Trg': 0.33,  # Line 2656
    'Ky_NP_MP_Trg': 1.0,  # Line 2657

    # From calculate_Mlk_MPuse_g_Trg
    'Kl_MP_NP_Trg': 0.69,  # Line 54, 2596, 2651, 2654

    # From get_nutrient_intakes
    # Line 1005, this is a true digestbility.  There is a neg intercept of -3.43% of DM
    'Fd_dcrOM': 96,
    'fCPAdu': 0.064,
    'KpFor': 4.87,  # %/h
    # From Bayesian fit to Digesta Flow data with Seo Kp as priors, eqn. 26 in Hanigan et al.
    'KpConc': 5.28,
    'IntRUP': -0.086,  # Intercept, kg/d
    'refCPIn': 3.39,  # average CPIn for the DigestaFlow dataset, kg/d.  3/21/18, MDH
    'TT_dcFA_Base': 73,
    'TT_dcFat_Base': 68,
    # For Heifer check in calculate_MP_requiement
    'En_CP': 5.65,

    # From heifer_growth
    'Ka_LateGest_DMIn': 1.47,
    'Kc_LateGest_DMIn': -0.035,

    # For GE calculation
    'En_FA': 9.4,  # Combustion energies for each nutrient, MCal/kg of nutrient
    'En_CP': 5.65,  # excludes NPN
    'En_NFC': 4.2,
    'En_NDF': 4.2,
    'En_NDFnf': 4.14,
    'En_NPNCP': 0.89,  # per kg of CP equivalent based on urea at 2.5 kcal/g
    'En_rOM': 4.0,
    'En_St': 4.23,
    'En_WSC': 3.9,
    'En_Acet': 3.48,
    'En_Prop': 4.96,
    'En_Butr': 5.95,
    'Dt_dcCP_ClfLiq': 0.95,
    'TT_dcFA_ClfDryFd': 81,  # Line 1249, Used for all calf dry feed
    'TT_dcFA_ClfLiqFd': 81,  # Line 1250, Used for missing values in calf liquid feeds
    'UCT': 25,  # Line 230, calf
    'An_GutFill_BWmature': 0.18,  # Line 2400, mature animals
    'LCT': 15,  # calf < 3 wks of age, Line 228, NOTE: LCT is changed to 5 whe An_AgeDay > 21, should it be part of coeff_dict?
    'UCT': 25,  # calf, line 230

    # Doudenal endogenous CP AA profile (g hydrated AA / 100 g CP) corrected for 24 h
    # hydrolysis recovery. Lapierre et al.from Orskov et al. 1986.  Br. J. Nutr. 56:241-248.
    # corrected for 24 h recovery by Lapierre
    'EndArgProf': 4.61,  # Line 1446-1455
    'EndHisProf': 2.90,
    'EndIleProf': 4.09,
    'EndLeuProf': 7.67,
    'EndLysProf': 6.23,
    'EndMetProf': 1.26,
    'EndPheProf': 3.98,
    'EndThrProf': 5.18,
    'EndTrpProf': 1.29,
    'EndValProf': 5.29,

    #AA dehydration factors for mass change during peptide formation (g anhyd AAt / g hydrated AAt)
    'HydrArg': 0.8967,
    'HydrHis': 0.8840,
    'HydrIle': 0.8628,
    'HydrLeu': 0.8628,
    'HydrLys': 0.8769,
    'HydrMet': 0.8794,
    'HydrPhe': 0.8910,
    'HydrThr': 0.8490,
    'HydrTrp': 0.9118,
    'HydrVal': 0.8464,
    'MWArg': 174.2,
    'MWHis': 155.2,
    'MWIle': 131.2,
    'MWLeu': 131.2,
    'MWLys': 146.2,
    'MWMet': 149.2,
    'MWPhe': 165.2,
    'MWThr': 119.1,
    'MWTrp': 204.2,
    'MWVal': 117.2,

    # Milk Protein AA Composition, g/100 g of TP
    'Mlk_Arg_TP': 3.74,
    'Mlk_His_TP': 2.92,
    'Mlk_Ile_TP': 6.18,
    'Mlk_Leu_TP': 10.56,
    'Mlk_Lys_TP': 8.82,
    'Mlk_Met_TP': 3.03,
    'Mlk_Phe_TP': 5.26,
    'Mlk_Thr_TP': 4.62,
    'Mlk_Trp_TP': 1.65,
    'Mlk_Val_TP': 6.90,

    # Body Protein AA Composition, g/100 g of TP
    'Body_Arg_TP': 8.20,
    'Body_His_TP': 3.04,
    'Body_Ile_TP': 3.69,
    'Body_Leu_TP': 8.27,
    'Body_Lys_TP': 7.90,
    'Body_Met_TP': 2.37,
    'Body_Phe_TP': 4.41,
    'Body_Thr_TP': 4.84,
    'Body_Trp_TP': 1.05,
    'Body_Val_TP': 5.15,

    # Endogenous Urinary Protein AA Composition, g/100 g of TP; these are set equal to body protein AA comp
    'Ur_ArgEnd_TP': 8.20,
    'Ur_HisEnd_TP': 3.04,
    'Ur_IleEnd_TP': 3.69,
    'Ur_LeuEnd_TP': 8.27,
    'Ur_LysEnd_TP': 7.90,
    'Ur_MetEnd_TP': 2.37,
    'Ur_PheEnd_TP': 4.41,
    'Ur_ThrEnd_TP': 4.84,
    'Ur_TrpEnd_TP': 1.05,
    'Ur_ValEnd_TP': 5.15,

    # Metabolic Fecal Protein AA Composition, g/100 g of TP
    'Fe_ArgMetab_TP': 5.90,
    'Fe_HisMetab_TP': 3.54,
    'Fe_IleMetab_TP': 5.39,
    'Fe_LeuMetab_TP': 9.19,
    'Fe_LysMetab_TP': 7.61,
    'Fe_MetMetab_TP': 1.73,
    'Fe_PheMetab_TP': 5.28,
    'Fe_ThrMetab_TP': 7.36,
    'Fe_TrpMetab_TP': 1.79,
    'Fe_ValMetab_TP': 7.01,

    #Scurf Protein AA Composition, g/100 g of TP
    'Scrf_Arg_TP': 9.60,
    'Scrf_His_TP': 1.75,
    'Scrf_Ile_TP': 2.96,
    'Scrf_Leu_TP': 6.93,
    'Scrf_Lys_TP': 5.64,
    'Scrf_Met_TP': 1.40,
    'Scrf_Phe_TP': 3.61,
    'Scrf_Thr_TP': 4.01,
    'Scrf_Trp_TP': 0.73,
    'Scrf_Val_TP': 4.66,
    'fN_3MH': (3 * 14) / 169,
    'Fet_Ksyn': 5.16e-2,
    'Fet_KsynDecay': 7.59e-5,
    'Fet_Wt': 0,
    'Fet_BWgain': 0,  # open animal, kg/d
    'AshGain_RsrvGain': 0.02,
    'CH4vol_kg': 1497,  # liters/kg
    'En_CH4': 55.5 / 4.184, # mcal/kg methane; 890 kJ/mol / 16 g/mol = 55.6 MJ/kg from Rossini, 1930
    'An_Fe_m': 0,  # no Fe maintenance requirement
    'fIlEndTP_CP': 0.73, # Fraction of EndCP that is True Protein, from Lapierre, not used in model
    'Kf_ME_RE_ClfLiq': 0.56 # Line 2828
}

# Dictionary to use when infusions are not provided to model
infusion_dict = {
    'Inf_Acet_g': 0,
    'Inf_ADF_g': 0,
    'Inf_Arg_g': 0,
    'Inf_Ash_g': 0,
    'Inf_Butr_g': 0,
    'Inf_CP_g': 0,
    'Inf_CPARum_CP': 0,
    'Inf_CPBRum_CP': 0,
    'Inf_CPCRum_CP': 0,
    'Inf_dcFA': 0,
    'Inf_dcRUP': 0,
    'Inf_DM_g': 0,
    'Inf_EE_g': 0,
    'Inf_FA_g': 0,
    'Inf_Glc_g': 0,
    'Inf_His_g': 0,
    'Inf_Ile_g': 0,
    'Inf_KdCPB': 0,
    'Inf_Leu_g': 0,
    'Inf_Lys_g': 0,
    'Inf_Met_g': 0,
    'Inf_NDF_g': 0,
    'Inf_NPNCP_g': 0,
    'Inf_Phe_g': 0,
    'Inf_Prop_g': 0,
    'Inf_St_g': 0,
    'Inf_Thr_g': 0,
    'Inf_Trp_g': 0,
    'Inf_ttdcSt': 0,
    'Inf_Val_g': 0,
    'Inf_VFA_g': 0,
    'Inf_Location': "Rumen"
}

MP_NP_efficiency_dict = {
    'Trg_AbsHis_NPHis': 0.75,
    'Trg_AbsIle_NPIle': 0.71,
    'Trg_AbsLeu_NPLeu': 0.73,
    'Trg_AbsLys_NPLys': 0.72,
    'Trg_AbsMet_NPMet': 0.73,
    'Trg_AbsPhe_NPPhe': 0.6,
    'Trg_AbsThr_NPThr': 0.64,
    'Trg_AbsTrp_NPTrp': 0.86,
    'Trg_AbsVal_NPVal': 0.74,
    'Trg_MP_NP': 0.69
}

mPrt_coeff_list = [
    {  # NRC derived Coefficients from Dec. 20, 2020 solutions. AIC=10,631, mPrt_eqn == 0
        "mPrt_Int_src": -97.0,
        "mPrt_k_BW_src": -0.4201,
        "mPrt_k_DEInp_src": 10.79,
        "mPrt_k_DigNDF_src": -4.595,
        "mPrt_k_DEIn_StFA_src": 0,
        "mPrt_k_DEIn_NDF_src": 0,
        "mPrt_k_Arg_src": 0,
        "mPrt_k_His_src": 1.675,
        "mPrt_k_Ile_src": 0.885,
        "mPrt_k_Leu_src": 0.466,
        "mPrt_k_Lys_src": 1.153,
        "mPrt_k_Met_src": 1.839,
        "mPrt_k_Phe_src": 0,
        "mPrt_k_Thr_src": 0,
        "mPrt_k_Trp_src": 0.0,
        "mPrt_k_Val_src": 0,
        "mPrt_k_NEAA_src": 0,
        "mPrt_k_OthAA_src": 0.0773,
        "mPrt_k_EAA2_src": -0.00215
    },
    {  # VT1 derived Coefficients from Dec. 20, 2020 solutions. AIC=10,629, mPrt_eqn == 1
        "mPrt_Int_src": -141,
        "mPrt_k_BW_src": -0.4146,
        "mPrt_k_DEInp_src": 10.65,
        "mPrt_k_DigNDF_src": -4.62,
        "mPrt_k_DEIn_StFA_src": 0,
        "mPrt_k_DEIn_NDF_src": 0,
        "mPrt_k_Arg_src": 0.8175,
        "mPrt_k_His_src": 1.641,
        "mPrt_k_Ile_src": 0.837,
        "mPrt_k_Leu_src": 0.623,
        "mPrt_k_Lys_src": 1.235,
        "mPrt_k_Met_src": 1.846,
        "mPrt_k_Phe_src": 0,
        "mPrt_k_Thr_src": 0,
        "mPrt_k_Trp_src": 0,
        "mPrt_k_Val_src": 0,
        "mPrt_k_NEAA_src": 0.0925,
        "mPrt_k_OthAA_src": 0,
        "mPrt_k_EAA2_src": -0.002451
    },
    {  # VT2 derived Coefficients from April, 2022 solutions after further data cleaning, AIC=10,405. In publication. mPrt_eqn == 2
        "mPrt_Int_src": -73.7,
        "mPrt_k_BW_src": -0.3663,
        "mPrt_k_DEInp_src": 0,
        "mPrt_k_DigNDF_src": 0,
        "mPrt_k_DEIn_StFA_src": 10.87,
        "mPrt_k_DEIn_NDF_src": 5.43,
        "mPrt_k_Arg_src": 0,
        "mPrt_k_His_src": 1.19,
        "mPrt_k_Ile_src": 1.08,
        "mPrt_k_Leu_src": 0.238,
        "mPrt_k_Lys_src": 1.08,
        "mPrt_k_Met_src": 1.91,
        "mPrt_k_Phe_src": 0,
        "mPrt_k_Thr_src": 1.36,
        "mPrt_k_Trp_src": 0,
        "mPrt_k_Val_src": 0,
        "mPrt_k_NEAA_src": 0.075,
        "mPrt_k_OthAA_src": 0,
        "mPrt_k_EAA2_src": -0.00175
    }
]

f_Imb = pd.Series([1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0],
                  index=[
                      'Arg', 'His', 'Ile', 'Leu', 'Lys', 'Met', 'Phe', 'Thr',
                      'Trp', 'Val'
                  ])
