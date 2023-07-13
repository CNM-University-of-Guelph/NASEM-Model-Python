import math
import pandas as pd

def calculate_ME_requirement(An_BW, Dt_DMIn, Trg_MilkProd, An_BW_mature,
                             Trg_FrmGain, An_GestDay, An_GestLength,
                             An_AgeDay, Fet_BWbrth, An_LactDay,
                             An_Parity_rl, Trg_MilkFatp,
                             Trg_MilkTPp, Trg_MilkLacp, Trg_RsrvGain):
    """
    Calculate the metabolizable energy (ME) requirement (Mcal/d).

    This function calculates ME requirement for 1 cow using 4 functions:
    :py:func:`calculate_An_MEmUse`, :py:func:`calculate_An_MEgain`, :py:func:`calculate_Gest_MEuse`,
    and :py:func:`calculate_Trg_Mlk_MEout`.
 
    For details on how each value is calculated see the individual functions.

    Parameters:
        An_BW (Number): Animal Body Weight in kg.
        Dt_DMIn (Number): Animal Dry Matter Intake in kg/day.
        Trg_MilkProd (Number): Animal Milk Production in kg/day.
        An_BW_mature (Number): Animal Mature Liveweight in kg.
        Trg_FrmGain (Number): Target gain in body Frame Weight in kg fresh weight/day.
        An_GestDay (Number): Day of Gestation.
        An_GestLength (Number): Normal Gestation Length in days.
        An_AgeDay (Number): Animal Age in days.
        Fet_BWbrth (Number): Target calf birth weight in kg.
        An_LactDay (Number): Day of Lactation.
        An_Parity_rl (Number): Animal Parity where 1 = Primiparous and 2 = Multiparous.
        Trg_MilkFatp (Percentage): Animal Milk Fat percentage.
        Trg_MilkTPp (Percentage): Animal Milk True Protein percentage.
        Trg_MilkLacp (Percentage): Animal Milk Lactose percentage.
        Trg_RsrvGain (Number): Target gain or loss in body reserves (66% fat, 8% CP) in kg fresh weight/day.

    Returns:
        Trg_MEuse (Number): A number with the units Mcal/d.
    """
    An_MEmUse = calculate_An_MEmUse(An_BW, Dt_DMIn)
# An_MEmUse: ME requirement for maintenance, Mcal/d
  
    An_MEgain = calculate_An_MEgain(Trg_MilkProd, An_BW, An_BW_mature, Trg_FrmGain, Trg_RsrvGain)
# An_MEgain: ME requirement for frame and reserve gain, Mcal/d
  
    Gest_MEuse = calculate_Gest_MEuse(An_GestDay, An_GestLength, An_AgeDay,
                                      Fet_BWbrth, An_LactDay, An_Parity_rl)
# Gest_MEuse: ME requirement for gestation, Mcal/d
  
    Trg_Mlk_MEout = calculate_Trg_Mlk_MEout(Trg_MilkProd, Trg_MilkFatp, Trg_MilkTPp,
                                            Trg_MilkLacp)
# Trg_Mlk_MEout: ME requirement for milk production, Mcal/d
  
    Trg_MEuse = An_MEmUse + An_MEgain + Gest_MEuse + Trg_Mlk_MEout   # Line 2923
      
    return Trg_MEuse, An_MEmUse, An_MEgain, Gest_MEuse, Trg_Mlk_MEout


def calculate_An_MEmUse(An_BW, Dt_DMIn, Dt_PastIn=0, Dt_PastSupplIn=0, Env_DistParlor=0, Env_TripsParlor=0, Env_Topo=0):
    '''
    Calculate metabolizable energy requirements for maintenance

    Takes the following columns from a dataframe passed by :py:func:`execute_ME_requirement`
    and gives result to :py:func:`calculate_ME_requirement`:
    "An_BW", "Dt_DMIn", "Dt_PastIn", "Dt_PastSupplIn", "Env_DistParlor", "Env_TripsParlor",
    and "Env_Topo"

    By default "Dt_PastIn", "Dt_PastSupplIn", "Env_DistParlor", "Env_TripsParlor",
    and "Env_Topo" are set to 0. These are the variables needed to calculate 
    maintenance energy for cows on pasture. If cows are not out on pasture, these
    variables can be ignored when running the model. The default setting assumes 
    cows do not have access to pasture.

    Parameters:
       An_BW (Number): Animal Body Weight in kg.
       Dt_DMIn (Number): Animal Dry Matter Intake in kg/day.
       Dt_PastIn (Number): Animal Pasture Intake in kg/day.
       Dt_PastSupplIn (Number): Animal Supplement Intake while on pasture, could be concentrate or forage, in kg/day.
       Env_DistParlor (Number): Distance from barn or paddock to the parlor in meters.
       Env_TripsParlor (Number): Number of daily trips to and from parlor, usually two times the number of milkings.
       Env_Topo (Number): Positive elevation change per day in meters

    Returns:
       An_MEmUse (Number): A number with the units Mcal/day.
    '''       
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


def calculate_An_MEgain(Trg_MilkProd, An_BW, An_BW_mature, Trg_FrmGain,
                        Trg_RsrvGain=0):
   '''
   Calculate metabolizable energy requirements for growth.

   Takes the following columns from a dataframe passed by :py:func:`execute_ME_requirement` 
   and gives result to :py:func:`calculate_ME_requirement`:
   "Trg_MilkProd", "An_BW", "An_BW_mature", "Trg_FrmGain", and "Trg_RsrvGain"

   Parameters:
      Trg_MilkProd (Number): Animal Milk Production in kg/day.
      An_BW (Number): Animal Body Weight in kg.
      An_BW_mature (Number): Animal Mature Liveweight in kg. 
      Trg_FrmGain (Number): Target gain in body Frame Weight in kg fresh weight/day.
      Trg_RsrvGain (Number): Target gain or loss in body reserves (66% fat, 8% CP) in kg fresh weight/day. 

   Returns:
      An_MEgain (Number): A number with the units Mcal/d.
   '''
   
  
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


def calculate_Gest_MEuse(An_GestDay, An_GestLength, An_AgeDay,
                         Fet_BWbrth, An_LactDay, An_Parity_rl):
  '''
  Calculate metabolizable energy requirements for gestation.

  Takes the following columns from a dataframe passed by :py:func:`execute_ME_requirement` 
  and gives result to :py:func:`calculate_ME_requirement`:
  "An_GestDay", "An_GestLength", "An_AgeDay", "Fet_BWbrth", "An_LactDay", and "An_Parity_rl"

  Parameters:
      An_GestDay (Number): Day of Gestation.
      An_GestLength (Number): Normal Gestation Length in days.
      An_AgeDay (Number): Animal Age in days.
      Fet_BWbrth (Number): Target calf birth weight in kg.
      An_LactDay (Number): Day of Lactation.
      An_Parity_rl (Number): Animal Parity where 1 = Primiparous and 2 = Multiparous.

  Returns:
      Gest_MEuse (Number): A number with units Mcal/day.
  '''
  
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

  if An_AgeDay < 240:
     Uter_Wt = 0 

  if An_GestDay > 0 and An_GestDay <= An_GestLength:
    Uter_Wt = Uter_Wtpart * math.exp(-(Uter_Ksyn - Uter_KsynDecay * An_GestDay) * (An_GestLength - An_GestDay))  

  if An_GestDay <= 0 and An_LactDay > 0 and An_LactDay < 100:
     Uter_Wt = (Uter_Wtpart-0.204) * math.exp(-Uter_Kdeg*An_LactDay)+0.204

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
   
  #########################
  # ME Gestation Calculation
  #########################
  # Uter_BWgain: Rate of fresh tissue growth for maternal reproductive tissue
  # GrUter_BWgain: Rate of fresh tissue growth for gravid uterus
  # NE_GrUtWt: mcal NE/kg of fresh gravid uterus weight at birth
  # Gest_REgain: NE for gestation
  # Ky_ME_NE: Conversion of NE to ME for gestation
  
  Uter_BWgain = 0  #Open and nonregressing animal

  if An_GestDay > 0 and An_GestDay <= An_GestLength:
     Uter_BWgain = (Uter_Ksyn - Uter_KsynDecay * An_GestDay) * Uter_Wt

  if An_GestDay <= 0 and An_LactDay > 0 and An_LactDay < 100:                 #uterine involution after calving
     Uter_BWgain = -Uter_Kdeg*Uter_Wt
  GrUter_BWgain = 0                                              # Line 2341-2345

  if An_GestDay > 0 and An_GestDay <= An_GestLength:
     GrUter_BWgain = (GrUter_Ksyn-GrUter_KsynDecay*An_GestDay)*GrUter_Wt

  if An_GestDay <= 0 and An_LactDay > 0 and An_LactDay < 100:
     GrUter_BWgain = Uter_BWgain
  NE_GrUtWt = 0.95                                               # Line 2297
  Gest_REgain = GrUter_BWgain * NE_GrUtWt                        # Line 2360
              
  if Gest_REgain >= 0:                                           # Line 2839
     Ky_ME_NE = 0.14
  else: 
     Ky_ME_NE = 0.89
     
  Gest_MEuse = Gest_REgain / Ky_ME_NE                            # Line 2859
  return(Gest_MEuse)


def calculate_Trg_Mlk_MEout(Trg_MilkProd, Trg_MilkFatp, Trg_MilkTPp, Trg_MilkLacp):
   '''
   Calculate metabolizable energy requirements for milk production.

   Takes the following columns from a dataframe passed by :py:func:`execute_ME_requirement` 
   and gives result to :py:func:`calculate_ME_requirement`:
   "Trg_MilkProd", "Trg_MilkFatp", "Trg_MilkTPp", and "Trg_MilkLacp".

   Parameters:
      Trg_MilkProd (Number): Animal Milk Production in kg/day.
      Trg_MilkFatp (Percentage): Animal Milk Fat percentage.
      Trg_MilkTPp (Percentage): Animal Milk True Protein percentage.
      Trg_MilkLacp (Percentage): Animal Milk Lactose percentage.

   Returns:
      Trg_Mlk_MEout (Number): A number with the units Mcal/day.
   '''
   # Trg_NEmilk_Milk: Target energy output per kg milk
   # Trg_Mlk_NEout: NE for milk production
   # Kl_ME_NE: Conversion of NE to ME for lactation
   # Trg_Mlk_MEout: ME for milk production
  
   Trg_NEmilk_Milk = 9.29*Trg_MilkFatp/100 + 5.85*Trg_MilkTPp/100 + 3.95*Trg_MilkLacp/100 # Line 2886
   Trg_Mlk_NEout = Trg_MilkProd * Trg_NEmilk_Milk                 # Line 2888
   Kl_ME_NE = 0.66                                                # Line 2823
   Trg_Mlk_MEout = Trg_Mlk_NEout / Kl_ME_NE                       # Line 2889
   return(Trg_Mlk_MEout)


def execute_ME_requirement(row):
    '''
    Execute :py:func:`calculate_ME_requirement` on a dataframe. 

    This is a helper function that takes a series as the input. The series represents 1 row of data from a dataframe with the following
    values and is given to :py:func:`calculate_ME_requirement`: 
    "An_BW", "Dt_DMIn", "Trg_MilkProd", "An_BW_mature", "Trg_FrmGain", 
    "An_GestDay", "An_GestLength", "An_AgeDay", "Fet_BWbrth", "An_LactDay", 
    "An_Parity_rl", "Trg_MilkFatp", "Trg_MilkTPp", "Trg_MilkLacp", and "Trg_RsrvGain".

    The values required in the series are described in :py:func:`calculate_ME_requirement`.

    Parameters:
       row (Series): A series that contains all the required values.

    Returns:
       Trg_MEuse (Number): The metabolizable energy requirement (Mcal/d).
    '''
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
