
from nasem_dairy.ration_balancer.ration_balancer_functions import check_coeffs_in_coeff_dict


def calculate_ME_requirement(An_BW, Dt_DMIn, Trg_MilkProd, An_BW_mature,
                             Trg_FrmGain, Trg_MilkFatp, Trg_MilkTPp, Trg_MilkLacp,
                             Trg_RsrvGain, GrUter_BWgain, coeff_dict):
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
        Trg_MilkFatp (Percentage): Animal Milk Fat percentage.
        Trg_MilkTPp (Percentage): Animal Milk True Protein percentage.
        Trg_MilkLacp (Percentage): Animal Milk Lactose percentage.
        Trg_RsrvGain (Number): Target gain or loss in body reserves (66% fat, 8% CP) in kg fresh weight/day.
        GrUter_BWgain (Number): Average rate of fresh tissue growth for gravid uterus, kg fresh wt/d 
        coeff_dict (Dict): Dictionary containing all coefficients for the model

    Returns:
        Trg_MEuse (Number): A number with the units Mcal/d.
        An_MEmUse (Number): Metabolizable energy requirement for maintenance, Mcal/d
        An_MEgain (Number): Metabolizable energy requirement for frame and reserve gain, Mcal/d
        Gest_MEuse (Number): Metabolizable energy requirement for gestation, Mcal/d
        Trg_Mlk_MEout (Number): A number with the units Mcal/day.
        Trg_NEmilk_Milk (Number): Net energy content of milk, Mcal

    """
    An_MEmUse = calculate_An_MEmUse(An_BW, Dt_DMIn, coeff_dict)
# An_MEmUse: ME requirement for maintenance, Mcal/d
  
    An_MEgain, Frm_NEgain, Rsrv_NEgain = calculate_An_MEgain(Trg_MilkProd, An_BW, An_BW_mature, Trg_FrmGain, coeff_dict, Trg_RsrvGain)
# An_MEgain: ME requirement for frame and reserve gain, Mcal/d
  
    Gest_MEuse = calculate_Gest_MEuse(GrUter_BWgain, coeff_dict)
# Gest_MEuse: ME requirement for gestation, Mcal/d
  
    Trg_Mlk_MEout, Trg_NEmilk_Milk = calculate_Trg_Mlk_MEout(Trg_MilkProd, Trg_MilkFatp, Trg_MilkTPp,
                                            Trg_MilkLacp, coeff_dict)
# Trg_Mlk_MEout: ME requirement for milk production, Mcal/d
  
    Trg_MEuse = An_MEmUse + An_MEgain + Gest_MEuse + Trg_Mlk_MEout   # Line 2923
      
    return Trg_MEuse, An_MEmUse, An_MEgain, Gest_MEuse, Trg_Mlk_MEout, Trg_NEmilk_Milk, Frm_NEgain, Rsrv_NEgain


def calculate_An_MEmUse(An_BW, Dt_DMIn, coeff_dict, Dt_PastIn=0, Dt_PastSupplIn=0, Env_DistParlor=0, Env_TripsParlor=0, Env_Topo=0):
    '''
    Calculate metabolizable energy requirements for maintenance

    # TODO: update docs - execute_ME_requirement no longer used
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
       coeff_dict (Dict): Dictionary containing all coefficients for the model
       Dt_PastIn (Number): Animal Pasture Intake in kg/day.
       Dt_PastSupplIn (Number): Animal Supplement Intake while on pasture, could be concentrate or forage, in kg/day.
       Env_DistParlor (Number): Distance from barn or paddock to the parlor in meters.
       Env_TripsParlor (Number): Number of daily trips to and from parlor, usually two times the number of milkings.
       Env_Topo (Number): Positive elevation change per day in meters

    Returns:
       An_MEmUse (Number): A number with the units Mcal/day.
    '''     
    req_coeffs = ['An_NEmUse_Env', 'Km_ME_NE']
    check_coeffs_in_coeff_dict(coeff_dict, req_coeffs)


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
   #  An_NEmUse_Env = 0                                               # Line 2785
    An_MBW = An_BW ** 0.75                                          # Line 223

    if Dt_PastIn / Dt_DMIn < 0.005:                                 # Line 2793
        An_NEm_Act_Graze = 0
    else:
        An_NEm_Act_Graze = 0.0075 * An_MBW * (600 - 12 * Dt_PastSupplIn) / 600

    An_NEm_Act_Parlor = (0.00035 * Env_DistParlor / 1000) * Env_TripsParlor * An_BW  # Line 2795
    An_NEm_Act_Topo = 0.0067 * Env_Topo / 1000 * An_BW              # Line 2796
    An_NEmUse_Act = An_NEm_Act_Graze + An_NEm_Act_Parlor + An_NEm_Act_Topo  # Line 2797

    An_NEmUse = An_NEmUse_NS + coeff_dict['An_NEmUse_Env'] + An_NEmUse_Act        # Line 2801
   #  Km_ME_NE = 0.66                                                 # Line 2817

    An_MEmUse = An_NEmUse / coeff_dict['Km_ME_NE']                                # Line 2844
    return An_MEmUse


def calculate_An_MEgain(Trg_MilkProd, An_BW, An_BW_mature, Trg_FrmGain, coeff_dict, 
                        Trg_RsrvGain=0):
   '''
   Calculate metabolizable energy requirements for growth.
   
   # TODO: update docs - execute_ME_requirement no longer used
   Takes the following columns from a dataframe passed by :py:func:`execute_ME_requirement` 
   and gives result to :py:func:`calculate_ME_requirement`:
   "Trg_MilkProd", "An_BW", "An_BW_mature", "Trg_FrmGain", and "Trg_RsrvGain"

   Parameters:
      Trg_MilkProd (Number): Animal Milk Production in kg/day.
      An_BW (Number): Animal Body Weight in kg.
      An_BW_mature (Number): Animal Mature Liveweight in kg. 
      Trg_FrmGain (Number): Target gain in body Frame Weight in kg fresh weight/day.
      coeff_dict (Dict): Dictionary containing all coefficients for the model
      Trg_RsrvGain (Number): Target gain or loss in body reserves (66% fat, 8% CP) in kg fresh weight/day. 

   Returns:
      An_MEgain (Number): A number with the units Mcal/d.
   '''
   req_coeffs = ['FatGain_RsrvGain', 'Kr_ME_RE', 'An_GutFill_BW', 'Body_NP_CP', 'Kf_ME_RE']
   check_coeffs_in_coeff_dict(coeff_dict, req_coeffs)

   # FatGain_RsrvGain: Conversion factor from reserve gain to fat gain
   # Rsrv_Gain_empty: Body reserve gain assuming no gut fill association
   # Rsrv_Fatgain: Body reserve fat gain
   # CPGain_FrmGain: CP gain per unit of frame gain
   # Rsrv_CPgain: CP portion of body reserve gain
   # Rsrv_NEgain: NE of body reserve gain, mcal/d
   # Kr_ME_RE: Efficiency of ME to reserve RE for heifers/dry cows (91), lactating 
   # cows gaining reserve (92), and lactating cows losing reserve (92)
   # Rsrv_MEgain: ME of body reserve gain, mcal/d
      
   # FatGain_RsrvGain = 0.622                                       # Line 2451
   Rsrv_Gain_empty = Trg_RsrvGain                                 # Line 2441 and 2435
   Rsrv_Fatgain = coeff_dict['FatGain_RsrvGain']*Rsrv_Gain_empty                # Line 2453
   CPGain_FrmGain = 0.201-0.081*An_BW/An_BW_mature                # Line 2458
   Rsrv_CPgain = CPGain_FrmGain * Rsrv_Gain_empty                 # Line 2470
   Rsrv_NEgain = 9.4*Rsrv_Fatgain + 5.55*Rsrv_CPgain              # Line 2866
   # Kr_ME_RE = 0.60                                                # Line 2834

   Kr_ME_RE = coeff_dict['Kr_ME_RE']
   
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
   # An_GutFill_BW = 0.18                                           # Line 2410, check the heifer value
   Frm_Gain_empty = Frm_Gain*(1- coeff_dict['An_GutFill_BW'])                    # Line 2439
   Frm_Fatgain = FatGain_FrmGain*Frm_Gain_empty                   # Line 2452
   # Body_NP_CP = 0.86                                              # Line 1963
   NPGain_FrmGain = CPGain_FrmGain * coeff_dict['Body_NP_CP']                   # Line 2459
   Frm_NPgain = NPGain_FrmGain * Frm_Gain_empty                   # Line 2460
   Frm_CPgain = Frm_NPgain /  coeff_dict['Body_NP_CP']                         # Line 2463
   Frm_NEgain = 9.4*Frm_Fatgain + 5.55*Frm_CPgain                 # Line 2867
   # Kf_ME_RE = 0.4                                                 # Line 2831
   Frm_MEgain = Frm_NEgain / coeff_dict['Kf_ME_RE']                             # Line 2872
      
   An_MEgain = Rsrv_MEgain + Frm_MEgain                           # Line 2873
   return(An_MEgain, Frm_NEgain, Rsrv_NEgain)


def calculate_Gest_MEuse(GrUter_BWgain, coeff_dict):
  '''
  Calculate metabolizable energy requirements for gestation.

  # TODO: update docs - execute_ME_requirement no longer used
   
  Takes the following columns from a dataframe passed by :py:func:`execute_ME_requirement` 
  and gives result to :py:func:`calculate_ME_requirement`:
  "An_GestDay", "An_GestLength", "An_AgeDay", "Fet_BWbrth", "An_LactDay", and "An_Parity_rl"

  Parameters:
      GrUter_BWgain (Number): Average rate of fresh tissue growth for gravid uterus, kg fresh wt/d
      coeff_dict (Dict): Dictionary containing all coefficients for the model
     
  Returns:
      Gest_MEuse (Number): A number with units Mcal/day.
  '''
  req_coeffs = ['NE_GrUtWt']
  check_coeffs_in_coeff_dict(coeff_dict, req_coeffs)

#   NE_GrUtWt = 0.95                                               # Line 2297
  Gest_REgain = GrUter_BWgain * coeff_dict['NE_GrUtWt']                        # Line 2360
              
  if Gest_REgain >= 0:                                           # Line 2839
     Ky_ME_NE = 0.14
  else: 
     Ky_ME_NE = 0.89
     
  Gest_MEuse = Gest_REgain / Ky_ME_NE                            # Line 2859
  return(Gest_MEuse)


def calculate_Trg_Mlk_MEout(Trg_MilkProd, Trg_MilkFatp, Trg_MilkTPp, Trg_MilkLacp, coeff_dict):
   '''
   Calculate metabolizable energy requirements for milk production.

   # TODO: update docs - execute_ME_requirement no longer used
   
   Takes the following columns from a dataframe passed by :py:func:`execute_ME_requirement` 
   and gives result to :py:func:`calculate_ME_requirement`:
   "Trg_MilkProd", "Trg_MilkFatp", "Trg_MilkTPp", and "Trg_MilkLacp".

   Parameters:
      Trg_MilkProd (Number): Animal Milk Production in kg/day.
      Trg_MilkFatp (Percentage): Animal Milk Fat percentage.
      Trg_MilkTPp (Percentage): Animal Milk True Protein percentage.
      Trg_MilkLacp (Percentage): Animal Milk Lactose percentage.
      coeff_dict (Dict): Dictionary containing all coefficients for the model

   Returns:
      Trg_Mlk_MEout (Number): A number with the units Mcal/day.
      Trg_NEmilk_Milk (Number): Net energy content of milk, Mcal
   '''
   req_coeffs = ['Kl_ME_NE']
   check_coeffs_in_coeff_dict(coeff_dict, req_coeffs)

   # Trg_NEmilk_Milk: Target energy output per kg milk
   # Trg_Mlk_NEout: NE for milk production
   # Kl_ME_NE: Conversion of NE to ME for lactation
   # Trg_Mlk_MEout: ME for milk production
  
   Trg_NEmilk_Milk = 9.29*Trg_MilkFatp/100 + 5.85*Trg_MilkTPp/100 + 3.95*Trg_MilkLacp/100 # Line 2886
   Trg_Mlk_NEout = Trg_MilkProd * Trg_NEmilk_Milk                 # Line 2888
   # Kl_ME_NE = 0.66                                                # Line 2823
   Trg_Mlk_MEout = Trg_Mlk_NEout / coeff_dict['Kl_ME_NE']                       # Line 2889
   return Trg_Mlk_MEout, Trg_NEmilk_Milk


