import numpy as np
from nasem_dairy.ration_balancer.ration_balancer_functions import check_coeffs_in_coeff_dict

def calculate_An_NEmUse_NS(An_StatePhys: str, An_BW: float, An_BW_empty: float, An_parity_rl: int, Dt_DMIn_ClfLiq: float) -> float:
    """
    An_NEmUse_NS: NE required for maintenance in unstressed cow, mcal/d
    Unstressed (NS)
    Net energy (NE) maintenance (NEm) mcal/d    
    """
    An_NEmUse_NS = 0.10 * An_BW ** 0.75  # Heifers, Line 2781
    An_NEmUse_NS = np.where(An_StatePhys == "Calf",     # milk or mixed diet, Line 2779
                            0.0769 * An_BW_empty**0.75,
                            An_NEmUse_NS)
    condition = (An_StatePhys == "Calf") and (Dt_DMIn_ClfLiq == 0)
    An_NEmUse_NS = np.where(condition,                  # weaned calf, Line 2780
                            0.097 * An_BW_empty**0.75,
                            An_NEmUse_NS)
    An_NEmUse_NS = np.where(An_parity_rl > 0,   # Cows, Line 2782
                            0.10 * An_BW**0.75,
                            An_NEmUse_NS)
    return An_NEmUse_NS


def calculate_An_NEm_Act_Graze(Dt_PastIn: float, Dt_DMIn: float, Dt_PastSupplIn: float, An_MBW: float) -> float:
    """
    Net energy (NE) maintenance (NEm) mcal/d    
    An_NEm_Act_Graze: NE use for grazing activity mcal/d
    """
    if Dt_PastIn / Dt_DMIn < 0.005:     # Line 2793
        An_NEm_Act_Graze = 0
    else:
        An_NEm_Act_Graze = 0.0075 * An_MBW * (600 - 12 * Dt_PastSupplIn) / 600
    return An_NEm_Act_Graze


def calculate_An_NEm_Act_Parlor(An_BW: float, Env_DistParlor: float, Env_TripsParlor: float) -> float:
    """
    Env_DistParlor (float): Distance from barn or paddock to the parlor in meters.
    Env_TripsParlor (int): Number of daily trips to and from parlor, usually two times the number of milkings.
    An_NEm_Act_Parlor: NE use walking to parlor mcal/d
    """
    An_NEm_Act_Parlor = (0.00035 * Env_DistParlor / 1000) * Env_TripsParlor * An_BW  # Line 2795
    return An_NEm_Act_Parlor


def calculate_An_NEm_Act_Topo(An_BW: float, Env_Topo: float) -> float:
    """
    Env_Topo (float): Positive elevation change per day in meters
    An_NEm_Act_Topo: NE use due to topography mcal/d
    """
    An_NEm_Act_Topo = 0.0067 * Env_Topo / 1000 * An_BW      # Line 2796
    return An_NEm_Act_Topo


def calculate_An_NEmUse_Act(An_NEm_Act_Graze: float, An_NEm_Act_Parlor: float, An_NEm_Act_Topo: float) -> float:
    """
    An_NEmUse_Act: Total NE use for activity on pasture, mcal/d
    """
    An_NEmUse_Act = An_NEm_Act_Graze + An_NEm_Act_Parlor + An_NEm_Act_Topo  # Line 2797
    return An_NEmUse_Act


def calculate_An_NEmUse(An_NEmUse_NS: float, An_NEmUse_Act: float, coeff_dict: dict) -> float:
    """
    An_NEmUse: Total NE use for maintenance, mcal/d
    """
    req_coeff = ['An_NEmUse_Env']
    check_coeffs_in_coeff_dict(coeff_dict, req_coeff)
    An_NEmUse = An_NEmUse_NS + coeff_dict['An_NEmUse_Env'] + An_NEmUse_Act  # Line 2801
    return An_NEmUse


def calculate_An_MEmUse(An_NEmUse: float, coeff_dict: dict) -> float:
    """
    An_MEmUse: Total Metabolizable Energy use for maintenance, mcal/d
    """
    req_coeff = ['Km_ME_NE']
    check_coeffs_in_coeff_dict(coeff_dict, req_coeff)
    An_MEmUse = An_NEmUse / coeff_dict['Km_ME_NE']      # Line 2844
    return An_MEmUse


def calculate_Rsrv_NEgain(Rsrv_Fatgain: float, Rsrv_CPgain: float) -> float:
    """
    Rsrv_NEgain: NE of body reserve gain, mcal/d
    """
    Rsrv_NEgain = 9.4 * Rsrv_Fatgain + 5.55 * Rsrv_CPgain              # Line 2866
    return Rsrv_NEgain


def calculate_Kr_ME_RE(Trg_MilkProd: float, Trg_RsrvGain: float) -> float:
    """
    Kr_ME_RE: Efficiency of ME to reserve RE for heifers/dry cows (91), lactating 
    """
    if Trg_MilkProd > 0 and Trg_RsrvGain > 0:   # Efficiency of ME to Rsrv RE for lactating cows gaining Rsrv, Line 2835
        Kr_ME_RE = 0.75
    elif Trg_RsrvGain <= 0:     # Line 2836,Efficiency of ME generated for cows losing Rsrv
        Kr_ME_RE = 0.89
    else:
        # Efficiency of ME to RE for reserves gain, Heifers and dry cows, Line 2835
        Kr_ME_RE = 0.60
    return Kr_ME_RE


def calculate_Rsrv_MEgain(Rsrv_NEgain: float, Kr_ME_RE: float) -> float:
    """
    Rsrv_MEgain: ME of body reserve gain, mcal/d
    """
    Rsrv_MEgain = Rsrv_NEgain / Kr_ME_RE    # Line 2871
    return Rsrv_MEgain


def calculate_Frm_NEgain(Frm_Fatgain: float, Frm_CPgain: float) -> float:
    """
    Frm_NEgain: NE of frame gain mcal/d
    """
    Frm_NEgain = 9.4 * Frm_Fatgain + 5.55 * Frm_CPgain      # Line 2867
    return Frm_NEgain


def calculate_Frm_MEgain(Frm_NEgain: float, coeff_dict: dict) -> float:
    """
    Frm_MEgain: ME of frame gain mcal/d
    """
    req_coeff = ['Kf_ME_RE']
    check_coeffs_in_coeff_dict(coeff_dict, req_coeff)
    # Line 2872
    Frm_MEgain = Frm_NEgain / coeff_dict['Kf_ME_RE']
    return Frm_MEgain


def calculate_An_MEgain(Rsrv_MEgain: float, Frm_MEgain: float) -> float:
    """
    An_MEgain: total ME required for frame + reserve gain, mcal/d
    """
    An_MEgain = Rsrv_MEgain + Frm_MEgain    # Line 2873
    return An_MEgain


def calculate_Gest_REgain(GrUter_BWgain: float, coeff_dict: dict) -> float:
    """
    Gest_REgain: reserve energy for gesation gain (uterine growth / regression)
    """
    Gest_REgain = GrUter_BWgain * coeff_dict['NE_GrUtWt']   # This will slightly underestimate release of NE from the regressing uterus, Line 2360
    return Gest_REgain


def calculate_Gest_MEuse(Gest_REgain: float) -> float:
    """
    Gest_MEuse: ME requirement for gestation, mcal/d
    Ky_ME_NE: efficiencies of Energy Use , Mcal NE/Mcal ME
    """
    Ky_ME_NE = np.where(Gest_REgain >= 0, 0.14, 0.89)
    # Gain from Ferrell et al, 1976, and loss assumed = Rsrv loss, Line 2859
    Gest_MEuse = Gest_REgain / Ky_ME_NE
    return Gest_MEuse


def calculate_Trg_NEmilk_Milk(Trg_MilkFatp: float, Trg_MilkTPp: float, Trg_MilkLacp: float) -> float:
    """
    Trg_NEmilk_Milk: Target energy output (mcal) per kg milk
    Trg = target
    p = percent
    """
    Trg_NEmilk_Milk = 9.29 * Trg_MilkFatp / 100 + 5.85 * Trg_MilkTPp / 100 + 3.95 * Trg_MilkLacp / 100  # Line 2887
    if np.isnan(Trg_NEmilk_Milk):
        # If milk protein and lactose are not provided, use the Tyrrell and Reid (1965) eqn., Line 2888
        Trg_NEmilk_Milk = 0.36 + 9.69 * Trg_MilkFatp / 100
    return Trg_NEmilk_Milk


def calculate_Trg_Mlk_NEout(Trg_MilkProd: float, Trg_NEmilk_Milk: float) -> float:
    """
    Trg_Mlk_NEout: NE requirement for milk production, mcal/d
    """
    Trg_Mlk_NEout = Trg_MilkProd * Trg_NEmilk_Milk  # Line 2889
    return Trg_Mlk_NEout


def calculate_Trg_Mlk_MEout(Trg_Mlk_NEout: float, coeff_dict: dict) -> float:
    """
    Kl_ME_NE: Conversion of NE to ME for lactation
    Trg_Mlk_MEout: ME requirement for milk production, mcal/d
    """
    req_coeff = ['Kl_ME_NE']
    check_coeffs_in_coeff_dict(coeff_dict, req_coeff)
    Trg_Mlk_MEout = Trg_Mlk_NEout / coeff_dict['Kl_ME_NE']  # Line 2890
    return Trg_Mlk_MEout


def calculate_Trg_MEuse(An_MEmUse: float, An_MEgain: float, Gest_MEuse: float, Trg_Mlk_MEout: float) -> float:
    """
    Trg_MEuse: Total metabolizable energy requirement mcal/d 
    """
    Trg_MEuse = An_MEmUse + An_MEgain + Gest_MEuse + Trg_Mlk_MEout   # Line 2923
    return Trg_MEuse
