# Above each function is the documentation from the R version. This needs to be replaced.
import math
import pandas as pd

#' Calculate MP Requirements
#'
#' This function calculates ME requirements for 1 cow using 4 functions, which
#' are required to be pre-loaded: [An_MPm_g_Trg], [Body_MPUse_g_Trg],
#' [Gest_MPUse_g_Trg], [Mlk_MPUse_g_Trg].
#' 
#' For details on how each value is calculated see the individual functions.
#'
#' @param Dt_NDFIn Number. NDF Intake in kg.
#' @param Dt_DMIn Number. Animal Dry Matter Intake in kg/day.
#' @param An_BW Number. Animal Body Weight in kg.
#' @param An_BW_mature Number. Animal Mature Liveweight in kg.
#' @param Trg_FrmGain Number. Target gain in body Frame Weight in kg fresh weight/day.
#' @param Trg_RsrvGain Number. Target gain or loss in body reserves (66% fat, 8% CP) in kg fresh weight/day.
#' @param An_GestDay Number. Day of Gestation.
#' @param An_GestLength Number. Normal Gestation Length in days.
#' @param An_AgeDay Number. Animal Age in days. 
#' @param Fet_BWbrth Number. Target calf birth weight in kg.
#' @param An_LactDay Number. Day of Lactation.
#' @param An_Parity_rl Number. Animal Parity where 1 = Primiparous and 2 = Multiparous.
#' @param Trg_MilkProd Number.Animal Milk Production in kg/day.
#' @param Trg_MilkTPp Percentage. Animal Milk True Protein percentage.
#'
#' @return An_MPuse_g_Trg, A number with the units g/d. Referred to as An_MPuse_g_Trg in equation
#' 
#' @export
#'
def calculate_MP_requirement(Dt_NDFIn, Dt_DMIn, An_BW, An_BW_mature, Trg_FrmGain,
                             Trg_RsrvGain, An_GestDay, An_GestLength, 
                             An_AgeDay, Fet_BWbrth, An_LactDay, An_Parity_rl,
                             Trg_MilkProd, Trg_MilkTPp):
  
  An_MPm_g_Trg = calculate_An_MPm_g_Trg(Dt_NDFIn, Dt_DMIn, An_BW)
  # An_MPm_g_Trg: MP requirement for maintenance, g/d
  
  Body_MPUse_g_Trg = calculate_Body_MPuse_g_Trg(An_BW, An_BW_mature, Trg_FrmGain,
                                                Trg_RsrvGain)
  # Body_MPUse_g_Trg: MP requirement for frame and reserve gain, g/d
  
  Gest_MPUse_g_Trg = calculate_Gest_MPuse_g_Trg(An_GestDay, An_GestLength, An_AgeDay,
                                                Fet_BWbrth, An_LactDay, An_Parity_rl)
  # Gest_MPUse_g_Trg: MP requirement for gestation, g/d
  
  Mlk_MPUse_g_Trg = calculate_Mlk_MPuse_g_Trg(Trg_MilkProd, Trg_MilkTPp)
  # Mlk_MPUse_g_Trg: MP requirement for milk production, g/d
  
  An_MPuse_g_Trg = An_MPm_g_Trg + Body_MPUse_g_Trg + Gest_MPUse_g_Trg + Mlk_MPUse_g_Trg # Line 2680
  return(An_MPuse_g_Trg)


#' Calculate Metabolizable Protein Requirements for Maintenance
#'
#' Takes the following columns from a dataframe passed by [dev_execute_MP_requirement] 
#' and gives result to [calculate_MP_requirement]:
#' "Dt_NDFIn", "An_BW", and "Dt_DMIn"
#'
#' @param Dt_NDFIn Number. NDF Intake in kg.
#' @param Dt_DMIn Number. Animal Dry Matter Intake in kg/day.
#' @param An_BW Number. Animal Body Weight in kg.
#'
#' @return An_MPm_g_Trg, A number with units g/d.
#' 
#' @export
#'
def calculate_An_MPm_g_Trg(Dt_NDFIn, Dt_DMIn, An_BW): 
  # An_NDF: NDF % of diet
  # Fe_CPend_g: Fecal CP from endogenous secretions and urea captured by microbes, g
  # Fe_CPend: Fe_CPend_g in kg
  # Fe_NPend: Fecal NP from endogenous secretions and urea captured by microbes, kg
  # Fe_NPend_g: Fecal NP from endogenous secretions and urea captured by microbes, g
  # Km_MP_NP_Trg: Conversion of NP to MP for maintenance
  # Fe_MPendUse_g_Trg: Fecal MP from endogenous secretions and urea captured by microbes, g
  # Scrf_CP_g: Scurf CP, g
  # Body_NP_CP: Conversion of CP to NP
  # Scrf_NP_g: Scurf NP, g
  # Scrf_MPUse_g_Trg: Scurf MP, g
  # Ur_Nend_g: Urinary endogenous N, g
  # Ur_NPend_g: Urinary endogenous NP, g
  # Ur_MPendUse_g: Urinary endogenous MP, g
  
  #Fe_MPendUse_g_Trg
  An_NDF = Dt_NDFIn / Dt_DMIn * 100                                # Lines 942, 944
  Fe_CPend_g = (12 + 0.12*An_NDF) * (Dt_DMIn)                      # Line 1186, Infusions removed
  Fe_CPend = Fe_CPend_g / 1000                                     # Line 1189
  Fe_NPend = Fe_CPend * 0.73	                                     # Line 1191
  Fe_NPend_g = Fe_NPend * 1000                                     # Line 1192
  Km_MP_NP_Trg = 0.69                                              # Lines 54, 2596, 2651 and 2652
  Fe_MPendUse_g_Trg = Fe_NPend_g / Km_MP_NP_Trg                    # Line 2668
  
  #Scrf_MPUse_g_Trg
  Scrf_CP_g = 0.20 * An_BW**0.60                                   # Line 1964
  Body_NP_CP = 0.86                                                # Line 1963
  Scrf_NP_g = Scrf_CP_g * Body_NP_CP                               # Line 1966
  Scrf_MPUse_g_Trg = Scrf_NP_g / Km_MP_NP_Trg                      # Line 2670
  
  Ur_Nend_g = 0.053 * An_BW                                        # Line 2029
  Ur_NPend_g = Ur_Nend_g * 6.25                                    # Line 2030
  Ur_MPendUse_g = Ur_NPend_g                                       # Line 2672
  
  An_MPm_g_Trg = Fe_MPendUse_g_Trg + Scrf_MPUse_g_Trg + Ur_MPendUse_g # Line 2679
  return(An_MPm_g_Trg)


#' Calculate Metabolizable Protein Requirements for Growth
#'
#' Takes the following columns from a dataframe passed by [dev_execute_MP_requirement] 
#' and gives result to [calculate_MP_requirement]:
#' "An_BW", "An_BW_matureand", "Trg_FrmGain", and "Trg_RsrvGain"
#'
#' @param An_BW Number. Animal Body Weight in kg.
#' @param An_BW_mature Number. Animal Mature Liveweight in kg. 
#' @param Trg_FrmGain Number. Target gain in body Frame Weight in kg fresh weight/day.
#' @param Trg_RsrvGain Number. Target gain or loss in body reserves (66% fat, 8% CP) in kg fresh weight/day. 
#'
#' @return Body_MPuse_g_Trg, A number with units g/d.
#' 
#' @export
#'
def calculate_Body_MPuse_g_Trg(An_BW, An_BW_mature, Trg_FrmGain, Trg_RsrvGain): 
  # CPGain_FrmGain: CP gain per unit of frame gain
  # Body_NP_CP: Conversion of CP to NP
  # NPGain_FrmGain: NP gain per unit frame gain
  # Frm_Gain: Frame gain, kg/d
  # An_GutFill_BW: Proportion of animal BW that is gut fill
  # Frm_Gain_empty: Frame gain assuming the dame gut fill for frame gain
  # Frm_NPgain: NP portion of frame gain
  # CPGain_RsrvGain: CP per unit reserve gain
  # NPGain_RsrvGain: NP per unit reserve gain
  # Rsrv_Gain_empty: Body reserve gain assuming no gut fill association
  # Rsrv_NPgain: NP content of reserve gain
  # Body_NPgain: NP from frame and reserve gain, kg
  # Body_NPgain_g: Body_NPgain in g
  # Kg_MP_NP_Trg: Conversion of NP to MP for growth
  
  CPGain_FrmGain = 0.201-0.081*An_BW/An_BW_mature                  # Line 2458
  Body_NP_CP = 0.86                                                # Line 1963
  NPGain_FrmGain = CPGain_FrmGain * Body_NP_CP                     # Line 2459
  Frm_Gain = Trg_FrmGain                                           # Line 2434
  An_GutFill_BW = 0.18                                             # Line 2400 and 2411
  Frm_Gain_empty = Frm_Gain*(1-An_GutFill_BW)                      # Line 2439
  Frm_NPgain = NPGain_FrmGain * Frm_Gain_empty                     # Line 2460
  
  CPGain_RsrvGain = 0.068                                          # Line 2466
  NPGain_RsrvGain = CPGain_RsrvGain * Body_NP_CP                   # Line 2467
  Rsrv_Gain_empty = Trg_RsrvGain                                   # Line 2435 and 2441
  Rsrv_NPgain = NPGain_RsrvGain * Rsrv_Gain_empty                  # Line 2468
  
  Body_NPgain = Frm_NPgain + Rsrv_NPgain                           # Line 2473
  Body_NPgain_g = Body_NPgain * 1000                               # Line 2475
  Kg_MP_NP_Trg = 0.69                                              # Line 54, 2665
  Body_MPuse_g_Trg = Body_NPgain_g / Kg_MP_NP_Trg                  # Line 2675
  return(Body_MPuse_g_Trg)


#' Calculate Metabolizable Protein Requirements for Pregnancy
#'
#' Takes the following columns from a dataframe passed by [dev_execute_MP_requirement] 
#' and gives result to [calculate_MP_requirement]:
#' "An_GestDay", "An_GestLength", "An_AgeDay", "Fet_BWbrth", "An_LactDay", and "An_Parity_rl"
#'
#' @param An_GestDay Number. Day of Gestation.
#' @param An_GestLength Number. Normal Gestation Length in days.
#' @param An_AgeDay Number. Animal Age in days. 
#' @param Fet_BWbrth Number. Target calf birth weight in kg.
#' @param An_LactDay Number. Day of Lactation.
#' @param An_Parity_rl Number. Animal Parity where 1 = Primiparous and 2 = Multiparous.
#'
#' @return Gest_MPuse_g_Trg, A number with units g/d.
#' 
#' @export
#'
def calculate_Gest_MPuse_g_Trg(An_GestDay, An_GestLength, An_AgeDay, Fet_BWbrth, An_LactDay, An_Parity_rl):
  # Ksyn: Constant for synthesis
  # GrUter_Ksyn: Gravid uterus synthesis rate constant
  # GrUter_KsynDecay: Rate of decay of gravid uterus synthesis approaching parturition
  
  GrUter_Ksyn = 2.43e-2                                         # Line 2302
  GrUter_KsynDecay = 2.45e-5                                    # Line 2303
  
  #########################
  # Uter_Wt Calculation
  #########################
  # UterWt_FetBWbrth: kg maternal tissue/kg calf weight at parturition
  # Uter_Wtpart: Maternal tissue weight (uterus plus caruncles) at parturition
  # Uter_Ksyn: Uterus synthesis rate
  # Uter_KsynDecay: Rate of decay of uterus synthesis approaching parturition
  # Uter_Kdeg: Rate of uterine degradation
  # Uter_Wt: Weight of maternal tissue
  
  UterWt_FetBWbrth = 0.2311                                     # Line 2296
  Uter_Wtpart = Fet_BWbrth * UterWt_FetBWbrth                   # Line 2311
  Uter_Ksyn = 2.42e-2                                           # Line 2306
  Uter_KsynDecay = 3.53e-5                                      # Line 2307
  Uter_Kdeg = 0.20                                              # Line 2308
  
# For the series of 'if' statements I'm not sure if 'elif' can be used. It looks like it changes the value of Uter_Wt
# but then changes it back to the default of 0.204 if the resulting values do not make sense

  Uter_Wt = 0.204                                               # Line 2312-2318
  
  if An_AgeDay < 240:
    Uter_Wt = 0
  
  if An_GestDay > 0 and An_GestDay <= An_GestLength:
    Uter_Wt = Uter_Wtpart * math.exp(-(Uter_Ksyn-Uter_KsynDecay*An_GestDay)*(An_GestLength-An_GestDay))

  if An_GestDay <= 0 and An_LactDay > 0 and An_LactDay < 100:
    Uter_Wt = ((Uter_Wtpart-0.204)* math.exp(-Uter_Kdeg*An_LactDay))+0.204

  if An_Parity_rl > 0 and Uter_Wt < 0.204:
    Uter_Wt = 0.204

  #########################
  # GrUter_Wt Calculation
  ######################### 
  # GrUterWt_FetBWbrth: kg of gravid uterus/ kg of calf birth weight
  # GrUter_Wtpart: Gravid uterus weight at parturition
  # GrUter_Wt: Gravid uterine weight
  
  GrUterWt_FetBWbrth = 1.816                                    # Line 2295
  GrUter_Wtpart = Fet_BWbrth * GrUterWt_FetBWbrth               # Line 2322
  GrUter_Wt = Uter_Wt                                           # Line 2323-2327   

  if An_GestDay > 0 and An_GestDay <= An_GestLength:
    GrUter_Wt = GrUter_Wtpart * math.exp(-(GrUter_Ksyn-GrUter_KsynDecay*An_GestDay)*(An_GestLength-An_GestDay))

  if GrUter_Wt < Uter_Wt:
    GrUter_Wt = Uter_Wt

  ########################
  # MP Gestation Calculation
  #########################
  # Uter_BWgain: Rate of fresh tissue growth for maternal reproductive tissue
  # GrUter_BWgain: Rate of fresh tissue growth for gravid uterus
  # CP_GrUtWt: kg CP/ kg fresh gravid uterus weight
  # Gest_NCPgain_g: Rate of CP deposition in gravid uterus
  # Body_NP_CP: Conversion of CP to NP
  # Gest_NPgain_g: Rate of NP deposition in gravid uterus
  # Gest_NPother_g: NP gain in other maternal tissues during late gestation
  # Gest_NPuse_g: Total NP use for gestation, g
  # Ky_MP_NP_Trg: Conversion of MP to NP for gestation
  # Ky_NP_MP_Trg: Conversion of NP to MP for gestation

  
  
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
  
  CP_GrUtWt = 0.123                                                # Line 2298                                     
  Gest_NCPgain_g = GrUter_BWgain * CP_GrUtWt * 1000                # Line 2363
  Body_NP_CP = 0.86                                                # Line 1963
  Gest_NPgain_g = Gest_NCPgain_g * Body_NP_CP                      # Line 2364
  Gest_NPother_g = 0                                               # Line 2353
  Gest_NPuse_g = Gest_NPgain_g + Gest_NPother_g                    # Line 2365
  Ky_MP_NP_Trg = 0.33                                              # Line 2656
  Ky_NP_MP_Trg = 1.0                                               # Line 2657
  
  if Gest_NPuse_g >= 0:                                            # Line 2676
    Gest_MPuse_g_Trg = Gest_NPuse_g/Ky_MP_NP_Trg
  else:
    Gest_MPuse_g_Trg = Gest_NPuse_g*Ky_NP_MP_Trg

  return(Gest_MPuse_g_Trg)


#' Calculate Metabolizable Protein Requirements for Production
#'
#' Takes the following columns from a dataframe passed by [dev_execute_MP_requirement] 
#' and gives result to [calculate_MP_requirement]:
#' "Trg_MilkProd", and "Trg_MilkTPp"
#'
#' @param Trg_MilkProd Number.Animal Milk Production in kg/day.
#' @param Trg_MilkTPp Percentage. Animal Milk True Protein percentage.
#'
#' @return Mlk_MPUse_g_Trg, A number with units g/d.
#' 
#' @export
#'
def calculate_Mlk_MPuse_g_Trg(Trg_MilkProd, Trg_MilkTPp): 
  # Trg_Mlk_NP_g: NP required for milk production
  # Kl_MP_NP_Trg: Conversion of NP to MP for milk production
  
  Trg_Mlk_NP_g = Trg_MilkProd*1000 * Trg_MilkTPp/100               # Line 2205
  Kl_MP_NP_Trg = 0.69                                              # Line 54, 2596, 2651, 2654
  
  Mlk_MPUse_g_Trg = Trg_Mlk_NP_g/ Kl_MP_NP_Trg                     # Line 2677
  return(Mlk_MPUse_g_Trg)


#' Execute MP function with a dataframe 
#'
#' This is a helper function takes a data frame as input with 1 row of data and the following
#' columns and is given to [calculate_MP_requirement]: 
#' "Dt_NDFIn", "An_BW", "Dt_DMIn", "Trg_MilkProd", "An_BW_mature", "Trg_FrmGain", 
#' "An_GestDay", "An_GestLength", "An_AgeDay", "Fet_BWbrth", "An_LactDay", 
#' "An_Parity_rl", "Trg_MilkTPp", and "Trg_RsrvGain"
#'
#' The columns required in the data frame are described in the [calculate_MP_requirement] function.
#'
#' @param df_in A data frame with 1 row of data and the required columns
#'
#' @return An_MPuse_g_Trg, A single number representing the metabolizable Protein requirements (g/d)
#' 
#' @export
#'
def execute_MP_requirement(row):
    # Check if the series contains the required column names
    required_columns = {"An_BW", "Dt_DMIn", "Trg_MilkProd", "An_BW_mature", "Trg_FrmGain",
                        "An_GestDay", "An_GestLength", "An_AgeDay", "Fet_BWbrth", "An_LactDay",
                        "An_Parity_rl", "Trg_MilkTPp", "Trg_RsrvGain", "Dt_NDFIn"}

    if not required_columns.issubset(row.index):
        missing_columns = list(required_columns - set(row.index))
        raise ValueError(f"Required columns are missing: {missing_columns}")

    ##########################################################################
    # Calculate Metabolizable Protein
    ##########################################################################
    Dt_NDFIn = row['Dt_NDFIn']
    Dt_DMIn = row['Dt_DMIn']
    An_BW = row['An_BW']
    An_BW_mature = row['An_BW_mature']
    Trg_FrmGain = row['Trg_FrmGain']
    Trg_RsrvGain = row['Trg_RsrvGain']
    An_GestDay = row['An_GestDay']
    An_GestLength = row['An_GestLength']
    An_AgeDay = row['An_AgeDay']
    Fet_BWbrth = row['Fet_BWbrth']
    An_LactDay = row['An_LactDay']
    An_Parity_rl = row['An_Parity_rl']
    Trg_MilkProd = row['Trg_MilkProd']
    Trg_MilkTPp = row['Trg_MilkTPp']

    # Call the function with the extracted values
    An_MPuse_g_Trg = calculate_MP_requirement(Dt_NDFIn, Dt_DMIn, An_BW, An_BW_mature,
                                              Trg_FrmGain, Trg_RsrvGain, An_GestDay,
                                              An_GestLength, An_AgeDay, Fet_BWbrth,
                                              An_LactDay, An_Parity_rl, Trg_MilkProd,
                                              Trg_MilkTPp)

    return An_MPuse_g_Trg
