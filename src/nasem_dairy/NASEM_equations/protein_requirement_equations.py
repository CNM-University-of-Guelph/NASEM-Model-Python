# Protein Requirement Equations
# import nasem_dairy.NASEM_equations.protein_requirement_equations as protein_req

import numpy as np

import nasem_dairy.ration_balancer.ration_balancer_functions as ration_funcs


def calculate_An_MPm_g_Trg(Fe_MPendUse_g_Trg: float, 
                           Scrf_MPuse_g_Trg: float,
                           Ur_MPendUse_g: float
) -> float:
    """
    An_MPm_g_Trg: Metabolizable protein requirement for maintenance (g/d)
    """
    An_MPm_g_Trg = Fe_MPendUse_g_Trg + Scrf_MPuse_g_Trg + Ur_MPendUse_g  
    # Line 2679
    return An_MPm_g_Trg


def calculate_Body_MPUse_g_Trg_initial(Body_NPgain_g: float,
                                       coeff_dict: dict
) -> float:
    """
    Body_MPUse_g_Trg: Metabolizable protein requirement for reserve and frame gain (g/d)
    """
    req_coeff = ['Kg_MP_NP_Trg']
    ration_funcs.check_coeffs_in_coeff_dict(coeff_dict, req_coeff)
    Body_MPUse_g_Trg = Body_NPgain_g / coeff_dict['Kg_MP_NP_Trg']  
    # Line 2675, kg MP/d for NP gain
    return Body_MPUse_g_Trg


def calculate_Gest_MPUse_g_Trg(Gest_NPuse_g: float, coeff_dict: dict) -> float:
    """
    Gest_MPUse_g_Trg: Metabolizable protein requirement for gestation (g/d)
    """
    req_coeff = ['Ky_MP_NP_Trg', 'Ky_NP_MP_Trg']
    ration_funcs.check_coeffs_in_coeff_dict(coeff_dict, req_coeff)
    if Gest_NPuse_g >= 0:  # Line 2676
        Gest_MPUse_g_Trg = Gest_NPuse_g / coeff_dict['Ky_MP_NP_Trg']
    else:
        Gest_MPUse_g_Trg = Gest_NPuse_g * coeff_dict['Ky_NP_MP_Trg']
    return Gest_MPUse_g_Trg


def calculate_Trg_Mlk_NP_g(Trg_MilkProd: float, Trg_MilkTPp: float) -> float:
    """
    Trg_Mlk_NP_g: Net protein required for milk production
    """
    Trg_Mlk_NP_g = Trg_MilkProd * 1000 * Trg_MilkTPp / 100  # Line 2205
    return Trg_Mlk_NP_g


def calculate_Mlk_MPUse_g_Trg(Trg_Mlk_NP_g: float, coeff_dict: dict) -> float:
    """
    Mlk_MPUse_g_Trg: Metabolizable protein requirement for milk production (g/d)
    """
    req_coeff = ['Kl_MP_NP_Trg']
    ration_funcs.check_coeffs_in_coeff_dict(coeff_dict, req_coeff)
    Mlk_MPUse_g_Trg = Trg_Mlk_NP_g / coeff_dict['Kl_MP_NP_Trg']  
    # kg MP/d for target milk protein lactation, Line 2677
    return Mlk_MPUse_g_Trg


def calculate_An_MPuse_g_Trg_initial(An_MPm_g_Trg: float,
                                     Body_MPUse_g_Trg: float,
                                     Gest_MPUse_g_Trg: float,
                                     Mlk_MPUse_g_Trg: float
) -> float:
    """
    An_MPuse_g_Trg: Metabolizable protein requirement (g/d)
    NOTE: In R An_MPuse_g_Trg is calculated, used in some calculations then recalculated
            If An_StatePhys == "Heifer" & Diff_MPuse_g > 0 then the value of An_MPuse_g_Trg will change
            To do this in package will need to calculate an inital value (this function) then calcualte the value again
    """
    An_MPuse_g_Trg = (An_MPm_g_Trg + Body_MPUse_g_Trg + 
                      Gest_MPUse_g_Trg + Mlk_MPUse_g_Trg)  # Line 2680
    return An_MPuse_g_Trg


def calculate_Min_MPuse_g(An_StatePhys: str, 
                          An_MPuse_g_Trg: float,
                          An_BW: float, 
                          An_BW_mature: float,
                          An_MEIn_approx: float
) -> float:
    """
    Min_MPuse_g: I think minimum MP use, g/d, but not 100% sure
    """
    if (An_StatePhys == "Heifer" and 
        An_MPuse_g_Trg < ((53 - 25 * An_BW / An_BW_mature) * An_MEIn_approx)
        ): # Line 2686-2687
        Min_MPuse_g = ((53 - 25 * An_BW / An_BW_mature) * An_MEIn_approx)
    else:
        Min_MPuse_g = An_MPuse_g_Trg
    return Min_MPuse_g


def calculate_Diff_MPuse_g(Min_MPuse_g: float, An_MPuse_g_Trg: float) -> float:
    """
    Diff_MPuse_g: g/d, I believe this is the difference betweem minimum MP use and MP requirement 
    """
    Diff_MPuse_g = Min_MPuse_g - An_MPuse_g_Trg  # Line 2688
    return Diff_MPuse_g


def calculate_Frm_MPUse_g_Trg(An_StatePhys: str, 
                              Frm_NPgain_g: float,
                              Kg_MP_NP_Trg: float,
                              Diff_MPuse_g: float
) -> float:
    """
    Frm_MPUse_g_Trg: kg MP/d for Frame NP gain
    """
    # kg MP/d for Frame NP gain, Line 2674
    Frm_MPUse_g_Trg = Frm_NPgain_g / Kg_MP_NP_Trg  
    if An_StatePhys == "Heifer" and Diff_MPuse_g > 0:
        Frm_MPUse_g_Trg = Frm_MPUse_g_Trg + Diff_MPuse_g  # Line 2691
    return Frm_MPUse_g_Trg


def calculate_Frm_NPgain_g(Frm_NPgain: float) -> float:
    """
    Frm_NPgain_g: Net protein for frame gain, g/d
    """
    Frm_NPgain_g = Frm_NPgain * 1000  # Line 2462
    return Frm_NPgain_g


def calculate_Kg_MP_NP_Trg(An_StatePhys: str, 
                           An_Parity_rl: int, 
                           An_BW: float,
                           An_BW_empty: float, 
                           An_BW_mature: float,
                           An_BWmature_empty: float,
                           MP_NP_efficiency_dict: dict,
                           coeff_dict: dict
) -> float:
    """
    Kg_MP_NP_Trg: Conversion of NP to MP for growth
    """
    req_coeff = ['Body_NP_CP']
    ration_funcs.check_coeffs_in_coeff_dict(coeff_dict, req_coeff)
    Kg_MP_NP_Trg = 0.60 * coeff_dict['Body_NP_CP']  
    # Default value for Growth MP to TP.  Shouldn't be used for any., Line 2659
    condition = (An_Parity_rl == 0) and (An_BW_empty / An_BWmature_empty > 0.12)
    Kg_MP_NP_Trg = np.where(
        condition,  # Line 2660-2662
        (0.64 - 0.3 * An_BW_empty / An_BWmature_empty) *
        coeff_dict['Body_NP_CP'],  # for heifers from 12% until 83% of BW_mature
        Kg_MP_NP_Trg)
    
    Kg_MP_NP_Trg = np.where(
        Kg_MP_NP_Trg < 0.394 * coeff_dict['Body_NP_CP'],
        0.394 * coeff_dict['Body_NP_CP'] * coeff_dict['Body_NP_CP'],  
        # Trap heifer values less than 0.39 MP to CP, Line 2663
        Kg_MP_NP_Trg)
    
    Kg_MP_NP_Trg = np.where(
        An_StatePhys == "Calf",
        (0.70 - 0.532 * (An_BW / An_BW_mature)) * coeff_dict['Body_NP_CP'],  
        # calves, Line 2664
        Kg_MP_NP_Trg)
    
    Kg_MP_NP_Trg = np.where(
        An_Parity_rl > 0,
        MP_NP_efficiency_dict['Trg_MP_NP'],  # Cows, Line 2665
        Kg_MP_NP_Trg)
    return Kg_MP_NP_Trg


def calculate_Rsrv_NPgain_g(Rsrv_NPgain: float) -> float:
    """
    Rsrv_MPUse_g_Trg: MP requirement for body reserves
    """
    Rsrv_NPgain_g = Rsrv_NPgain * 1000
    return Rsrv_NPgain_g


def calculate_Rsrv_MPUse_g_Trg(An_StatePhys: str, 
                               Diff_MPuse_g: float,
                               Rsrv_NPgain_g: float,
                               Kg_MP_NP_Trg: float
) -> float:
    """

    NOTE: Dave please check this one in the R code. I swear they use the exact same calculation inside the ifelse statement but I might be
          missing something. If this is correct I don't think there is any point in having the if statement.
    """
    if An_StatePhys == "Heifer" and Diff_MPuse_g > 0:
        Rsrv_MPUse_g_Trg = Rsrv_NPgain_g / Kg_MP_NP_Trg  # Line 2695
    else:
        Rsrv_MPUse_g_Trg = Rsrv_NPgain_g / Kg_MP_NP_Trg  
        # kg MP/d for Reserves NP gain, Line 2673
    return Rsrv_MPUse_g_Trg


def calculate_Body_MPUse_g_Trg(An_StatePhys: str, 
                               Diff_MPuse_g: float,
                               Body_NPgain_g: float, 
                               Body_MPUse_g_Trg: float,
                               Kg_MP_NP_Trg: float
) -> float:
    """
    Body_MPUse_g_Trg: MP requirement for frame and reserve gain, g/d
    """
    if An_StatePhys == "Heifer" and Diff_MPuse_g > 0:
        Body_MPUse_g_Trg = Body_NPgain_g / Kg_MP_NP_Trg  # Line 2696
    else:
        Body_MPUse_g_Trg = Body_MPUse_g_Trg
    return Body_MPUse_g_Trg


def calculate_An_MPuse_g_Trg(An_MPm_g_Trg: float, 
                             Frm_MPUse_g_Trg: float,
                             Rsrv_MPUse_g_Trg: float, 
                             Gest_MPUse_g_Trg: float,
                             Mlk_MPUse_g_Trg: float
) -> float:
    """
    An_MPuse_g_Trg: Metabolizable protein requirement (g/d)
    """
    An_MPuse_g_Trg = (An_MPm_g_Trg + Frm_MPUse_g_Trg + Rsrv_MPUse_g_Trg + 
                      Gest_MPUse_g_Trg + Mlk_MPUse_g_Trg)  # Line 2697
    return An_MPuse_g_Trg


def calculate_Trg_MPIn_req(Fe_MPendUse_g_Trg: float, 
                           Scrf_MPUse_g_Trg: float,
                           Ur_MPendUse_g: float, 
                           Body_MPUse_g_Trg: float,
                           Gest_MPUse_g_Trg: float, 
                           Trg_Mlk_NP_g: float,
                           coeff_dict: dict
) -> float:
    """
    Trg_MPIn_req: Target MP requirement (g/d)
    """
    req_coeff = ['Kl_MP_NP_Trg']
    ration_funcs.check_coeffs_in_coeff_dict(coeff_dict, req_coeff)
    Trg_MPIn_req = (Fe_MPendUse_g_Trg + Scrf_MPUse_g_Trg + Ur_MPendUse_g + 
                    Body_MPUse_g_Trg + Gest_MPUse_g_Trg + Trg_Mlk_NP_g / 
                    coeff_dict['Kl_MP_NP_Trg'])  # Line 2710
    return Trg_MPIn_req
