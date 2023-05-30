# Above each function is the documentation used in the R code version. This needs to be replaced with documentation for python.
import math
import pandas as pd

#' Calculate ME Requirements
#' 
#' This function calculates ME requirements for 1 cow using 4 functions, which
#' are required to be pre-loaded: [calculate_An_MEmUse], [calculate_An_MEgain],
#' [calculate_Gest_MEuse], [calculate_Trg_Mlk_MEout].
#' 
#' For details on how each value is calculated see the individual functions.
#'
#' @param An_BW Number. Animal Body Weight in kg.
#' @param Dt_DMIn Number. Animal Dry Matter Intake in kg/day.
#' @param Trg_MilkProd Number.Animal Milk Production in kg/day.
#' @param An_BW_mature Number. Animal Mature Liveweight in kg. 
#' @param Trg_FrmGain Number. Target gain in body Frame Weight in kg fresh weight/day.
#' @param An_GestDay Number. Day of Gestation.
#' @param An_GestLength Number. Normal Gestation Length in days.
#' @param An_AgeDay Number. Animal Age in days. 
#' @param Fet_BWbrth Number. Target calf birth weight in kg.
#' @param An_LactDay Number. Day of Lactation.
#' @param An_Parity_rl Number. Animal Parity where 1 = Primiparous and 2 = Multiparous.
#' @param Trg_MilkFatp Percentage. Animal Milk Fat percentage.
#' @param Trg_MilkTPp Percentage. Animal Milk True Protein percentage.
#' @param Trg_MilkLacp Percentage. Animal Milk Lactose percentage.
#' @param Trg_RsrvGain Number. Target gain or loss in body reserves (66% fat, 8% CP) in kg fresh weight/day.  
#'
#' @return Trg_MEuse, A number with the units Mcal/d. Referred to as Trg_MEuse in equation
#'   *insert eq number* on page *insert number*.
#'
#' @export
#'
def calculate_ME_requirement(An_BW, Dt_DMIn, Trg_MilkProd, An_BW_mature,
                             Trg_FrmGain, An_GestDay, An_GestLength,
                             An_AgeDay, Fet_BWbrth, An_LactDay,
                             An_Parity_rl, Trg_MilkFatp,
                             Trg_MilkTPp, Trg_MilkLacp, Trg_RsrvGain):
    An_MEmUse = calculate_An_MEmUse(An_BW, Dt_DMIn)
# An_MEmUse: ME requirement for maintenance, mcal/d
  
    An_MEgain = calculate_An_MEgain(Trg_MilkProd, An_BW, An_BW_mature, Trg_FrmGain, Trg_RsrvGain)
# An_MEgain: ME requirement for frame and reserve gain, mcal/d
  
    Gest_MEuse = calculate_Gest_MEuse(An_GestDay, An_GestLength, An_AgeDay,
                                      Fet_BWbrth, An_LactDay, An_Parity_rl)
# Gest_MEuse: ME requirement for gestation, mcal/d
  
    Trg_Mlk_MEout = calculate_Trg_Mlk_MEout(Trg_MilkProd, Trg_MilkFatp, Trg_MilkTPp,
                                            Trg_MilkLacp)
# Trg_Mlk_MEout: ME requirement for milk production, mcal/d
  
    Trg_MEuse = An_MEmUse + An_MEgain + Gest_MEuse + Trg_Mlk_MEout   # Line 2923  
    return(Trg_MEuse)


#' Calculate Metabolizable Energy Requirements for Maintenance
#'
#' Takes the following columns from a dataframe passed by [dev_execute_ME_requirement] 
#' and gives result to [calculate_ME_requirement]:
#' "An_BW", "Dt_DMIn", "Dt_PastIn", "Dt_PastSupplIn", "Env_DistParlor", "Env_TripsParlor",
#' and "Env_Topo"
#' 
#' By default "Dt_PastIn", "Dt_PastSupplIn", "Env_DistParlor", "Env_TripsParlor",
#' and "Env_Topo" are set to 0. These are the variables needed to calculate 
#' maintenance energy for cows on pasture. If cows are not out on pasture these
#' variables can be ignored when running the model. The default setting assumes 
#' cows do not have access to pasture.
#'
#' @param An_BW Number. Animal Body Weight in kg.
#' @param Dt_DMIn Number. Animal Dry Matter Intake in kg/day.
#' @param Dt_PastIn Number. Animal Pasture Intake in kg/day.
#' @param Dt_PastSupplIn Number. Animal Supplement Intake while on pasture, could be concentrate or forage, in kg/day.
#' @param Env_DistParlor Number. Distance from barn or paddock to the parlor in meters.
#' @param Env_TripsParlor Number. Number of daily trips to and from parlor, usually two times the number of milkings.
#' @param Env_Topo Number. Positive elevation change per day in meters
#'
#' @return An_MEmUse, A number with the units Mcal/day.
#' 
#' @export
#'
def calculate_An_MEmUse(An_BW, Dt_DMIn, Dt_PastIn=0, Dt_PastSupplIn=0, Env_DistParlor=0, Env_TripsParlor=0, Env_Topo=0):
    # An_NEmUse_NS: NE required for maintenance in unstressed cow, mcal/d
    # An_NEmUse_Env: NE cost of environmental stress, the model only considers this for calves
    # An_MBW: Metabolic body weight
    # An_NEm_Act_Graze: NE use for grazing activity
    # An_NEm_Act_Parlor: NE use walking to parlor
    # An_NEm_Act_Topo: NE use due to topography
    # An_NEmUse_Act: Total NE use for activity on pasture
    # An_NEmUse: Total NE use for maintenance
    # Km_ME_NE: Conversion of NE to ME

    An_NEmUse_NS = 0.10 * An_BW ** 0.75                             # Line 2781
    An_NEmUse_Env = 0                                               # Line 2785
    An_MBW = An_BW ** 0.75                                          # Line 223

    if Dt_PastIn / Dt_DMIn < 0.005:                                 # Line 2793
        An_NEm_Act_Graze = 0
    else:
        An_NEm_Act_Graze = 0.0075 * An_MBW * (600 - 12 * Dt_PastSupplIn) / 600

    An_NEm_Act_Parlor = (0.00035 * Env_DistParlor / 1000) * Env_TripsParlor * An_BW  # Line 2795
    An_NEm_Act_Topo = 0.0067 * Env_Topo / 1000 * An_BW              # Line 2796
    An_NEmUse_Act = An_NEm_Act_Graze + An_NEm_Act_Parlor + An_NEm_Act_Topo  # Line 2797

    An_NEmUse = An_NEmUse_NS + An_NEmUse_Env + An_NEmUse_Act        # Line 2801
    Km_ME_NE = 0.66                                                 # Line 2817

    An_MEmUse = An_NEmUse / Km_ME_NE                                # Line 2844
    return An_MEmUse


#' Calculate Metabolizable Energy Requirements for Growth
#' 
#' Takes the following columns from a dataframe passed by [dev_execute_ME_requirement] 
#' and gives result to [calculate_ME_requirement]:
#' "Trg_MilkProd", "An_BW", "An_BW_mature", "Trg_FrmGain", and "Trg_RsrvGain"
#'
#' @param Trg_MilkProd Number.Animal Milk Production in kg/day.
#' @param An_BW Number. Animal Body Weight in kg.
#' @param An_BW_mature Number. Animal Mature Liveweight in kg. 
#' @param Trg_FrmGain Number. Target gain in body Frame Weight in kg fresh weight/day.
#' @param Trg_RsrvGain Number. Target gain or loss in body reserves (66% fat, 8% CP) in kg fresh weight/day. 
#'
#' @return An_MEgain, A number with the units Mcal/d. 
#' 
#' @export
#'
def calculate_An_MEgain(Trg_MilkProd, An_BW, An_BW_mature, Trg_FrmGain,
                        Trg_RsrvGain=0):
  # FatGain_RsrvGain: Conversion factor from reserve gain to fat gain
  # Rsrv_Gain_empty: Body reserve gain assuming no gut fill association
  # Rsrv_Fatgain: Body reserve fat gain
  # CPGain_FrmGain: CP gain per unit of frame gain
  # Rsrv_CPgain: CP portion of body reserve gain
  # Rsrv_NEgain: NE of body reserve gain, mcal/d
  # Kr_ME_RE: Efficiency of ME to reserve RE for heifers/dry cows (91), lactating 
  # cows gaining reserve (92), and lactating cows losing reserve (92)
  # Rsrv_MEgain: ME of body reserve gain, mcal/d
  
  FatGain_RsrvGain = 0.622                                       # Line 2451
  Rsrv_Gain_empty = Trg_RsrvGain                                 # Line 2441 and 2435
  Rsrv_Fatgain = FatGain_RsrvGain*Rsrv_Gain_empty                # Line 2453
  CPGain_FrmGain = 0.201-0.081*An_BW/An_BW_mature                # Line 2458
  Rsrv_CPgain = CPGain_FrmGain * Rsrv_Gain_empty                 # Line 2470
  Rsrv_NEgain = 9.4*Rsrv_Fatgain + 5.55*Rsrv_CPgain              # Line 2866
  Kr_ME_RE = 0.60                                                # Line 2834

  if Trg_MilkProd > 0 and Trg_RsrvGain > 0:                      # Line 2835
     Kr_ME_RE = 0.75          

  if Trg_RsrvGain <= 0:                                          # Line 2836
     Kr_ME_RE = 0.89            

  Rsrv_MEgain = Rsrv_NEgain / Kr_ME_RE                           # Line 2871

  # FatGain_FrmGain: Fat gain per unit frame gain, g/g EBW (Empty body weight)
  # Frm_Gain: Frame gain, kg/d
  # An_GutFill_BW: Proportion of animal BW that is gut fill
  # Frm_Gain_empty: Frame gain assuming the dame gut fill for frame gain
  # Frm_Fatgain: Frame fat gain
  # Body_NP_CP: Conversion of CP to NP
  # NPGain_FrmGain: NP gain per unit frame gain
  # CPGain_FrmGain: CP gain per unit frame gain
  # Frm_NPgain: NP portion of frame gain
  # Frm_CPgain: CP portion of frame gain
  # Frm_NEgain: NE of frame gain
  # Kf_ME_RE: Conversion of NE to ME for frame gain
  # Frm_MEgain: ME of frame gain
  
  FatGain_FrmGain = 0.067+0.375*An_BW/An_BW_mature               # Line 2448
  Frm_Gain = Trg_FrmGain                                         # Line 2434
  An_GutFill_BW = 0.18                                           # Line 2410, check the heifer value
  Frm_Gain_empty = Frm_Gain*(1-An_GutFill_BW)                    # Line 2439
  Frm_Fatgain = FatGain_FrmGain*Frm_Gain_empty                   # Line 2452
  Body_NP_CP = 0.86                                              # Line 1963
  NPGain_FrmGain = CPGain_FrmGain * Body_NP_CP                   # Line 2459
  Frm_NPgain = NPGain_FrmGain * Frm_Gain_empty                   # Line 2460
  Frm_CPgain = Frm_NPgain /  Body_NP_CP                          # Line 2463
  Frm_NEgain = 9.4*Frm_Fatgain + 5.55*Frm_CPgain                 # Line 2867
  Kf_ME_RE = 0.4                                                 # Line 2831
  Frm_MEgain = Frm_NEgain / Kf_ME_RE                             # Line 2872
  
  An_MEgain = Rsrv_MEgain + Frm_MEgain                           # Line 2873
  return(An_MEgain)


#' Calculate Metabolizable Energy Requirements for Gestation
#'
#' Takes the following columns from a dataframe passed by [dev_execute_ME_requirement] 
#' and gives result to [calculate_ME_requirement]:
#' "An_GestDay", "An_GestLength", "An_AgeDay", "Fet_BWbrth", "An_LactDay", and "An_Parity_rl"
#'
#' @param An_GestDay Number. Day of Gestation.
#' @param An_GestLength Number. Normal Gestation Length in days.
#' @param An_AgeDay Number. Animal Age in days.
#' @param Fet_BWbrth Number. Target calf birth weight in kg.
#' @param An_LactDay Number. Day of Lactation.
#' @param An_Parity_rl Number. Animal Parity where 1 = Primiparous and 2 = Multiparous.
#'
#' @return Gest_MEuse, A number with units Mcal/day
#' 
#' @export
#'
def calculate_Gest_MEuse(An_GestDay, An_GestLength, An_AgeDay,
                         Fet_BWbrth, An_LactDay, An_Parity_rl):  
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
  
  Uter_Wt = 0.204                                               # Line 2312-2318

# For the series of if statements I'm not sure if 'elif' can be used. It looks like it changes the value of Uter_Wt
# but then changes it back to the default of 0.204 if the resulting values do not make sense

#   Uter_Wt = ifelse(An_AgeDay < 240, 0, Uter_Wt)
  if An_GestDay < 240:
     Uter_Wt = 0 

#   Uter_Wt = ifelse(An_GestDay > 0 & An_GestDay <= An_GestLength, 
                    # Uter_Wtpart * exp(-(Uter_Ksyn-Uter_KsynDecay*An_GestDay)*(An_GestLength-An_GestDay)), Uter_Wt)
  if An_GestDay > 0 and An_GestDay <= An_GestLength:
    Uter_Wt = Uter_Wtpart * math.exp(-(Uter_Ksyn - Uter_KsynDecay * An_GestDay) * (An_GestLength - An_GestDay))  

#   Uter_Wt = ifelse(An_GestDay <= 0 & An_LactDay > 0 & An_LactDay < 100, 
#                     ((Uter_Wtpart-0.204)*exp(-Uter_Kdeg*An_LactDay))+0.204, Uter_Wt)	
  if An_GestDay <= 0 and An_LactDay > 0 and An_LactDay < 100:
     Uter_Wt = (Uter_Wtpart-0.204) * math.exp(-Uter_Kdeg*An_LactDay)+0.204

#   Uter_Wt = ifelse(An_Parity_rl > 0 & Uter_Wt < 0.204, 0.204, Uter_Wt)
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
 
  # GrUter_Wt = ifelse(An_GestDay > 0 & An_GestDay <= An_GestLength,  
  #                     GrUter_Wtpart * exp(-(GrUter_Ksyn-GrUter_KsynDecay*An_GestDay)*(An_GestLength-An_GestDay)), GrUter_Wt)
  if An_GestDay > 0 and An_GestDay <= An_GestLength:
     GrUter_Wt = GrUter_Wtpart * math.exp(-(GrUter_Ksyn-GrUter_KsynDecay*An_GestDay)*(An_GestLength-An_GestDay))
  
  # GrUter_Wt = ifelse(GrUter_Wt < Uter_Wt, Uter_Wt, GrUter_Wt)
  if GrUter_Wt < Uter_Wt:
     GrUter_Wt = Uter_Wt
   
  #########################
  # ME Gestation Calculation
  #########################
  # Uter_BWgain: Rate of fresh tissue growth for maternal reproductive tissue
  # GrUter_BWgain: Rate of fresh tissue growth for gravid uterus
  # NE_GrUtWt: mcal NE/kg of fresh gravid uterus weight at birth
  # Gest_REgain: NE for gestation
  # Ky_ME_NE: Conversion of NE to ME for gestation
  
  Uter_BWgain = 0  #Open and nonregressing animal
  # Uter_BWgain = ifelse(An_GestDay > 0 & An_GestDay <= An_GestLength,  #gestating animal
  #                       (Uter_Ksyn - Uter_KsynDecay * An_GestDay) * Uter_Wt, Uter_BWgain)
  if An_GestDay > 0 and An_GestDay <= An_GestLength:
     Uter_BWgain = (Uter_Ksyn - Uter_KsynDecay * An_GestDay) * Uter_Wt
  # Uter_BWgain = ifelse(An_GestDay <= 0 & An_LactDay > 0 & An_LactDay < 100, #uterine involution after calving
  #                       -Uter_Kdeg*Uter_Wt, Uter_BWgain)
  if An_GestDay <= 0 and An_LactDay > 0 and An_LactDay < 100:                 #uterine involution after calving
     Uter_BWgain = -Uter_Kdeg*Uter_Wt
  GrUter_BWgain = 0                                              # Line 2341-2345
  # GrUter_BWgain = ifelse(An_GestDay > 0 & An_GestDay <= An_GestLength,  
  #                         (GrUter_Ksyn-GrUter_KsynDecay*An_GestDay)*GrUter_Wt, GrUter_BWgain)
  if An_GestDay > 0 and An_GestDay <= An_GestLength:
     GrUter_BWgain = (GrUter_Ksyn-GrUter_KsynDecay*An_GestDay)*GrUter_Wt
  # GrUter_BWgain = ifelse(An_GestDay <= 0 & An_LactDay > 0 & An_LactDay < 100, 
  #                         Uter_BWgain, GrUter_BWgain)
  if An_GestDay <= 0 and An_LactDay > 0 and An_LactDay < 100:
     GrUter_BWgain = Uter_BWgain
  NE_GrUtWt = 0.95                                               # Line 2297
  Gest_REgain = GrUter_BWgain * NE_GrUtWt                        # Line 2360
  # Ky_ME_NE = ifelse(Gest_REgain >= 0, 0.14, 0.89)                # Line 2839
  if Gest_REgain >= 0:
     Ky_ME_NE = 0.14
  else: 
     Ky_ME_NE = 0.89
  Gest_MEuse = Gest_REgain / Ky_ME_NE                             # Line 2859
  return(Gest_MEuse)


#' Calculate Metabolizable Energy Requirements for Milk Production
#'
#' Takes the following columns from a dataframe passed by [dev_execute_ME_requirement] 
#' and gives result to [calculate_ME_requirement]:
#' "Trg_MilkProd", "Trg_MilkFatp", "Trg_MilkTPp", and "Trg_MilkLacp".
#'
#' @param Trg_MilkProd Number.Animal Milk Production in kg/day.
#' @param Trg_MilkFatp Percentage. Animal Milk Fat percentage.
#' @param Trg_MilkTPp Percentage. Animal Milk True Protein percentage.
#' @param Trg_MilkLacp Percentage. Animal Milk Lactose percentage.
#'
#' @return Trg_Mlk_MEout, A number with the units Mcal/day.
#' 
#' @export
#'
def calculate_Trg_Mlk_MEout(Trg_MilkProd, Trg_MilkFatp, Trg_MilkTPp, Trg_MilkLacp):
  # Trg_NEmilk_Milk: Target energy output per kg milk
  # Trg_Mlk_NEout: NE for milk production
  # Kl_ME_NE: Conversion of NE to ME for lactation
  # Trg_Mlk_MEout: ME for milk production
  
  Trg_NEmilk_Milk = 9.29*Trg_MilkFatp/100 + 5.85*Trg_MilkTPp/100 + 3.95*Trg_MilkLacp/100 # Line 2886
  Trg_Mlk_NEout = Trg_MilkProd * Trg_NEmilk_Milk                 # Line 2888
  Kl_ME_NE = 0.66                                                # Line 2823
  Trg_Mlk_MEout = Trg_Mlk_NEout / Kl_ME_NE                       # Line 2889
  return(Trg_Mlk_MEout)


#' Execute ME function with a dataframe
#' 
#' This is a helper function takes a data frame as input with 1 row of data and the following
#' columns and is given to [calculate_ME_requirement]: 
#' "An_BW", "Dt_DMIn", "Trg_MilkProd", "An_BW_mature", "Trg_FrmGain", 
#' "An_GestDay", "An_GestLength", "An_AgeDay", "Fet_BWbrth", "An_LactDay", 
#' "An_Parity_rl", "Trg_MilkFatp", "Trg_MilkTPp", "Trg_MilkLacp" and "Trg_RsrvGain"
#'
#' The columns required in the data frame are described in the [calculate_ME_requirement] function.
#'
#' @param df_in A data frame with 1 row of data and the required columns
#'
#' @return Trg_MEuse, A single number representing the Metabolizable Energy requirements (Mcal/d)
#' @export
#'
def execute_ME_requirement(row):
    # Check if series contains all the required column names
    required_columns = ["An_BW", "Dt_DMIn", "Trg_MilkProd", "An_BW_mature", "Trg_FrmGain",
                        "An_GestDay", "An_GestLength", "An_AgeDay", "Fet_BWbrth", "An_LactDay",
                        "An_Parity_rl", "Trg_MilkFatp", "Trg_MilkTPp", "Trg_MilkLacp", "Trg_RsrvGain"]

    if not set(required_columns).issubset(row.index):
        missing_columns = list(set(required_columns) - set(row.index))
        raise ValueError(f"Required columns are missing: {missing_columns}")

    ##########################################################################
    # Calculate Metabolizable Energy
    ##########################################################################
    An_BW = row['An_BW']
    Dt_DMIn = row['Dt_DMIn']
    Trg_MilkProd = row['Trg_MilkProd']
    An_BW_mature = row['An_BW_mature']
    Trg_FrmGain = row['Trg_FrmGain']
    An_GestDay = row['An_GestDay']
    An_GestLength = row['An_GestLength']
    An_AgeDay = row['An_AgeDay']
    Fet_BWbrth = row['Fet_BWbrth']
    An_LactDay = row['An_LactDay']
    An_Parity_rl = row['An_Parity_rl']
    Trg_MilkFatp = row['Trg_MilkFatp']
    Trg_MilkTPp = row['Trg_MilkTPp']
    Trg_MilkLacp = row['Trg_MilkLacp']
    Trg_RsrvGain = row['Trg_RsrvGain']

    # Call the function with the extracted values
    Trg_MEuse = calculate_ME_requirement(An_BW, Dt_DMIn, Trg_MilkProd, An_BW_mature,
                                         Trg_FrmGain, An_GestDay, An_GestLength,
                                         An_AgeDay, Fet_BWbrth, An_LactDay,
                                         An_Parity_rl, Trg_MilkFatp, Trg_MilkTPp,
                                         Trg_MilkLacp, Trg_RsrvGain)

    return(Trg_MEuse)
