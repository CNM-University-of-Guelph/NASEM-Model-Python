import math
import pandas as pd
from nasem_dairy.ration_balancer.ration_balancer_functions import check_coeffs_in_coeff_dict


def calculate_MP_requirement(An_DEInp, An_DENPNCPIn, An_DigTPaIn, An_GasEOut, Frm_NPgain, Dt_NDFIn, Dt_DMIn, An_BW, An_BW_mature, Trg_FrmGain,
                             Trg_RsrvGain, Trg_MilkProd, Trg_MilkTPp, GrUter_BWgain, An_StatePhys, coeff_dict):
  '''
  Calculate metabolizable protein (MP) requirement.

  This function calculates MP requirements for 1 cow using 4 functions: :py:func:`An_MPm_g_Trg`, :py:func:`Body_MPuse_g_Trg`,
  :py:func:`Gest_MPuse_g_Trg`, and :py:func:`Mlk_MPuse_g_Trg`.

  For details on how each value is calculated, see the individual functions.

  Parameters:
      Dt_NDFIn: Number. NDF Intake in kg.
      Dt_DMIn: Number. Animal Dry Matter Intake in kg/day.
      An_BW: Number. Animal Body Weight in kg.
      An_BW_mature: Number. Animal Mature Liveweight in kg.
      Trg_FrmGain: Number. Target gain in body Frame Weight in kg fresh weight/day.
      Trg_RsrvGain: Number. Target gain or loss in body reserves (66% fat, 8% CP) in kg fresh weight/day.
      Trg_MilkProd: Number. Animal Milk Production in kg/day.
      Trg_MilkTPp: Percentage. Animal Milk True Protein percentage.
      GrUter_BWgain (Number): Average rate of fresh tissue growth for gravid uterus, kg fresh wt/d
      coeff_dict (Dict): Dictionary containing all coefficients for the model
      
  Returns:
      An_MPuse_g_Trg: Metabolizable protein requirement (g/d)
      An_MPm_g_Trg: Metabolizable protein requirement for maintenance (g/d)
      Body_MPuse_g_Trg: Metabolizable protein requirement for reserve and frame gain (g/d)
      Gest_MPuse_g_Trg: Metabolizable protein requirement for gestation (g/d)
      Mlk_MPuse_g_Trg: Metabolizable protein requirement for milk production (g/d)
  '''
  req_coeffs = ['En_CP']
  check_coeffs_in_coeff_dict(coeff_dict, req_coeffs)

  An_MPm_g_Trg = calculate_An_MPm_g_Trg(Dt_NDFIn, Dt_DMIn, An_BW, An_StatePhys, coeff_dict)
  # An_MPm_g_Trg: MP requirement for maintenance, g/d
  
  Body_MPuse_g_Trg, Body_NPgain, Rsrv_NPgain, Body_NPgain_g = calculate_Body_MPuse_g_Trg(An_BW, An_BW_mature, Trg_FrmGain,
                                                Trg_RsrvGain, An_StatePhys, coeff_dict)
  # Body_MPuse_g_Trg: MP requirement for frame and reserve gain, g/d
 
  Gest_MPuse_g_Trg = calculate_Gest_MPuse_g_Trg(GrUter_BWgain, coeff_dict)
  # Gest_MPuse_g_Trg: MP requirement for gestation, g/d
  
  Mlk_MPuse_g_Trg = calculate_Mlk_MPuse_g_Trg(Trg_MilkProd, Trg_MilkTPp, coeff_dict)
  # Mlk_MPuse_g_Trg: MP requirement for milk production, g/d
  
  An_MPuse_g_Trg = An_MPm_g_Trg + Body_MPuse_g_Trg + Gest_MPuse_g_Trg + Mlk_MPuse_g_Trg # Line 2680

  # Recalculate Body_MPuse_g_Trg for Heifers
  An_MEIn_approx = An_DEInp + An_DENPNCPIn + (An_DigTPaIn - Body_NPgain) * 4.0 + Body_NPgain * coeff_dict['En_CP'] - An_GasEOut

  if An_StatePhys == "Heifer" and An_MPuse_g_Trg < ((53 - 25 * An_BW / An_BW_mature) * An_MEIn_approx):
    Min_MPuse_g = ((53 - 25 * An_BW / An_BW_mature) * An_MEIn_approx)
  else:
    Min_MPuse_g = An_MPuse_g_Trg
  
  Diff_MPuse_g = Min_MPuse_g - An_MPuse_g_Trg

  #Adjust MPuse based on Min_MPuse
  if An_StatePhys == "Heifer" and Diff_MPuse_g > 0:
    Frm_MPUse_g_Trg = Frm_MPUse_g_Trg + Diff_MPuse_g
  
    #Recalculate Kg_MP_NP
    Frm_NPgain_g = Frm_NPgain * 1000
    Kg_MP_NP_Trg = Frm_NPgain_g / Frm_MPUse_g_Trg

    #Recalculate Rsrv and Body_MPUse
    Rsrv_NPgain_g = Rsrv_NPgain * 1000
    Rsrv_MPUse_g_Trg = Rsrv_NPgain_g / Kg_MP_NP_Trg
    Body_MPUse_g_Trg = Body_NPgain_g / Kg_MP_NP_Trg

    # Recalculate MP requirement 
    An_MPuse_g_Trg = An_MPm_g_Trg + Frm_MPUse_g_Trg + Rsrv_MPUse_g_Trg + Gest_MPUse_g_Trg + Mlk_MPUse_g_Trg
    print("An_MPuse_g_Trg has been recalculated")
  
  # calculate on a kg basis to allow easier comparison the MP intake
  An_MPuse_kg_Trg = An_MPuse_g_Trg / 1000
  
  return An_MPuse_g_Trg , An_MPm_g_Trg, Body_MPuse_g_Trg, Gest_MPuse_g_Trg, Mlk_MPuse_g_Trg, An_MPuse_kg_Trg


def calculate_An_MPm_g_Trg(Dt_NDFIn, Dt_DMIn, An_BW, An_StatePhys, coeff_dict):
  '''
  Calculate metabolizable protein requirements for maintenance

  Takes the following columns from a dataframe passed by :py:func:`execute_MP_requirement` 
  and gives the result to :py:func:`calculate_MP_requirement`: "Dt_NDFIn", "An_BW", and "Dt_DMIn".

  Parameters:
      Dt_NDFIn: Number. NDF Intake in kg.
      Dt_DMIn: Number. Animal Dry Matter Intake in kg/day.
      An_BW: Number. Animal Body Weight in kg.
      coeff_dict (Dict): Dictionary containing all coefficients for the model

  Returns:
      An_MPm_g_Trg: Metabolizable protein requirement for maintenance (g/d)
  '''
  req_coeffs = ['Km_MP_NP_Trg', 'Body_NP_CP']
  check_coeffs_in_coeff_dict(coeff_dict, req_coeffs)

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
  # Scrf_MPuse_g_Trg: Scurf MP, g
  # Ur_Nend_g: Urinary endogenous N, g
  # Ur_NPend_g: Urinary endogenous NP, g
  # Ur_MPendUse_g: Urinary endogenous MP, g
  
  #Fe_MPendUse_g_Trg
  An_NDF = Dt_NDFIn / Dt_DMIn * 100                                # Lines 942, 944
  Fe_CPend_g = (12 + 0.12*An_NDF) * (Dt_DMIn)                      # Line 1186, Infusions removed
  Fe_CPend = Fe_CPend_g / 1000                                     # Line 1189
  Fe_NPend = Fe_CPend * 0.73	                                     # Line 1191
  Fe_NPend_g = Fe_NPend * 1000                                     # Line 1192
#   Km_MP_NP_Trg = 0.69                                              # Lines 54, 2596, 2651 and 2652
  Fe_MPendUse_g_Trg = Fe_NPend_g / coeff_dict['Km_MP_NP_Trg']                    # Line 2668
  
  if An_StatePhys == "Calf" or An_StatePhys == "Heifer":
    Fe_MPendUse_g_Trg = Fe_CPend_g / coeff_dict['Km_MP_NP_Trg']

  #Scrf_MPuse_g_Trg
  Scrf_CP_g = 0.20 * An_BW**0.60                                   # Line 1964
#   Body_NP_CP = 0.86                                                # Line 1963
  Scrf_NP_g = Scrf_CP_g * coeff_dict['Body_NP_CP']                               # Line 1966
  Scrf_MPuse_g_Trg = Scrf_NP_g / coeff_dict['Km_MP_NP_Trg']                       # Line 2670

  if An_StatePhys == "Calf" or An_StatePhys == "Heifer":
    Scrf_MPuse_g_Trg = Scrf_CP_g / coeff_dict['Km_MP_NP_Trg'] 
  
  Ur_Nend_g = 0.053 * An_BW                                        # Line 2029
  Ur_NPend_g = Ur_Nend_g * 6.25                                    # Line 2030
  Ur_MPendUse_g = Ur_NPend_g                                       # Line 2672
  
  An_MPm_g_Trg = Fe_MPendUse_g_Trg + Scrf_MPuse_g_Trg + Ur_MPendUse_g # Line 2679
  return(An_MPm_g_Trg)


def calculate_Body_MPuse_g_Trg(An_BW, An_BW_mature, Trg_FrmGain, Trg_RsrvGain, An_StatePhys, coeff_dict): 
  '''
  Calculate metabolizable protein requirements for growth.

  Takes the following columns from a dataframe passed by :py:func:`execute_MP_requirement` 
  and gives the result to :py:func:`calculate_MP_requirement`: "An_BW", "An_BW_matureand", 
  "Trg_FrmGain", and "Trg_RsrvGain".

  Parameters:
      An_BW: Number. Animal body weight in kg.
      An_BW_mature: Number. Animal mature liveweight in kg.
      Trg_FrmGain: Number. Target gain in body frame weight in kg fresh weight/day.
      Trg_RsrvGain: Number. Target gain or loss in body reserves (66% fat, 8% CP) 
                    in kg fresh weight/day.
      coeff_dict (Dict): Dictionary containing all coefficients for the model

  Returns:
      Body_MPuse_g_Trg: Metabolizable protein requirement for reserve and frame gain (g/d)
  '''
  req_coeffs = ['Body_NP_CP', 'An_GutFill_BW', 'CPGain_RsrvGain', 'Kg_MP_NP_Trg']
  check_coeffs_in_coeff_dict(coeff_dict, req_coeffs)

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
  CPGain_FrmGain = 0.201 - 0.081 * An_BW / An_BW_mature                  # Line 2458
#   Body_NP_CP = 0.86                                                # Line 1963
  NPGain_FrmGain = CPGain_FrmGain * coeff_dict['Body_NP_CP']                     # Line 2459
  Frm_Gain = Trg_FrmGain                                           # Line 2434
#   An_GutFill_BW = 0.18                                             # Line 2400 and 2411
  Frm_Gain_empty = Frm_Gain * (1 - coeff_dict['An_GutFill_BW'])                      # Line 2439
  Frm_NPgain = NPGain_FrmGain * Frm_Gain_empty                     # Line 2460
  
#   CPGain_RsrvGain = 0.068                                          # Line 2466
  NPGain_RsrvGain = coeff_dict['CPGain_RsrvGain'] * coeff_dict['Body_NP_CP']                   # Line 2467
  Rsrv_Gain_empty = Trg_RsrvGain                                   # Line 2435 and 2441
  Rsrv_NPgain = NPGain_RsrvGain * Rsrv_Gain_empty                  # Line 2468
  
  Body_NPgain = Frm_NPgain + Rsrv_NPgain                           # Line 2473
  Body_NPgain_g = Body_NPgain * 1000                               # Line 2475
#   Kg_MP_NP_Trg = 0.69                                              # Line 54, 2665
  Body_MPuse_g_Trg = Body_NPgain_g / coeff_dict['Kg_MP_NP_Trg']                  # Line 2675   
  
  return Body_MPuse_g_Trg, Body_NPgain, Rsrv_NPgain, Body_NPgain_g


def calculate_Gest_MPuse_g_Trg(GrUter_BWgain, coeff_dict):
  '''
  Calculate metabolizable protein requirements for pregnancy.

  Takes the following columns from a dataframe passed by :py:func:`execute_MP_requirement` 
  and gives the result to :py:func:`calculate_MP_requirement`: "An_GestDay", "An_GestLength", 
  "An_AgeDay", "Fet_BWbrth", "An_LactDay", and "An_Parity_rl".

  Parameters:
      GrUter_BWgain (Number): Average rate of fresh tissue growth for gravid uterus, kg fresh wt/d
      coeff_dict (Dict): Dictionary containing all coefficients for the model

  Returns:
      Gest_MPuse_g_Trg: Metabolizable protein requirement for gestation (g/d)
  '''  
  req_coeffs = ['CP_GrUtWt', 'Body_NP_CP', 'Gest_NPother_g', 'Ky_MP_NP_Trg', 'Ky_NP_MP_Trg']
  check_coeffs_in_coeff_dict(coeff_dict, req_coeffs)

#   CP_GrUtWt = 0.123                                                # Line 2298                                     
  Gest_NCPgain_g = GrUter_BWgain * coeff_dict['CP_GrUtWt'] * 1000                # Line 2363
#   Body_NP_CP = 0.86                                                # Line 1963
  Gest_NPgain_g = Gest_NCPgain_g * coeff_dict['Body_NP_CP']                      # Line 2364
#   Gest_NPother_g = 0                                               # Line 2353
  Gest_NPuse_g = Gest_NPgain_g + coeff_dict['Gest_NPother_g']                    # Line 2365
#   Ky_MP_NP_Trg = 0.33                                              # Line 2656
#   Ky_NP_MP_Trg = 1.0                                               # Line 2657
  
  if Gest_NPuse_g >= 0:                                            # Line 2676
    Gest_MPuse_g_Trg = Gest_NPuse_g / coeff_dict['Ky_MP_NP_Trg']
  else:
    Gest_MPuse_g_Trg = Gest_NPuse_g * coeff_dict['Ky_NP_MP_Trg']

  return Gest_MPuse_g_Trg


def calculate_Mlk_MPuse_g_Trg(Trg_MilkProd, Trg_MilkTPp, coeff_dict): 
  '''
  Calculate metabolizable protein requirements for production.

  Takes the following columns from a dataframe passed by :py:func:`execute_MP_requirement` 
  and gives the result to :py:func:`calculate_MP_requirement`: "Trg_MilkProd" and "Trg_MilkTPp".

  Parameters:
      Trg_MilkProd: Number. Animal milk production in kg/day.
      Trg_MilkTPp: Percentage. Animal milk true protein percentage.
      coeff_dict (Dict): Dictionary containing all coefficients for the model

  Returns:
      Mlk_MPuse_g_Trg: Metabolizable protein requirement for milk production (g/d)
  '''
  req_coeffs = ['Kl_MP_NP_Trg']
  check_coeffs_in_coeff_dict(coeff_dict, req_coeffs)
  # Trg_Mlk_NP_g: NP required for milk production
  # Kl_MP_NP_Trg: Conversion of NP to MP for milk production
  
  Trg_Mlk_NP_g = Trg_MilkProd*1000 * Trg_MilkTPp/100               # Line 2205
#   Kl_MP_NP_Trg = 0.69                                              # Line 54, 2596, 2651, 2654
  
  Mlk_MPuse_g_Trg = Trg_Mlk_NP_g/ coeff_dict['Kl_MP_NP_Trg']                     # Line 2677
  return Mlk_MPuse_g_Trg

