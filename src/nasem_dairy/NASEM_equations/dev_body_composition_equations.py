# Body composition equations
# Calculations for body reseves gain/loss, frame gain, energy reserves
import numpy as np
from nasem_dairy.ration_balancer.ration_balancer_functions import check_coeffs_in_coeff_dict

def calculate_CPGain_FrmGain(An_BW, An_BW_mature):
    CPGain_FrmGain = 0.201 - 0.081 * An_BW / An_BW_mature   # Line 2458
    return CPGain_FrmGain


def calculate_Frm_Gain(Trg_FrmGain):
    Frm_Gain = Trg_FrmGain		#kg/d.  Add any predictions of ADG and select Trg or Pred ADG here
    return Frm_Gain


def calculate_Frm_Gain_empty(Frm_Gain, Dt_DMIn_ClfLiq, Dt_DMIn_ClfStrt, coeff_dict):
    req_coeff = ['An_GutFill_BW']
    check_coeffs_in_coeff_dict(coeff_dict, req_coeff)
    Frm_Gain_empty = Frm_Gain * (1 - coeff_dict['An_GutFill_BW'])   #Line 2439, Assume the same gut fill for frame gain
    condition = (Dt_DMIn_ClfLiq > 0) and (Dt_DMIn_ClfStrt > 0)
    Frm_Gain_empty = np.where(condition, Frm_Gain * 0.91, Frm_Gain_empty)  #Line 2440, slightly different for grain & milk fed
    return Frm_Gain_empty


def calculate_NPGain_FrmGain(CPGain_FrmGain, coeff_dict):
    req_coeff = ['Body_NP_CP']
    check_coeffs_in_coeff_dict(coeff_dict, req_coeff)
    NPGain_FrmGain = CPGain_FrmGain * coeff_dict['Body_NP_CP']  # Line 2460, convert to CP to TP gain / gain
    return NPGain_FrmGain


def calculate_Rsrv_Gain(Trg_RsrvGain):
    Rsrv_Gain = Trg_RsrvGain    # Line 2435
    return Rsrv_Gain


def calculate_Rsrv_Gain_empty(Rsrv_Gain):
    Rsrv_Gain_empty = Rsrv_Gain    # Line 2441, Assume no gut fill associated with reserves gain
    return Rsrv_Gain_empty


def calculate_Body_Gain_empty(Frm_Gain_empty, Rsrv_Gain_empty):
    Body_Gain_empty = Frm_Gain_empty + Rsrv_Gain_empty  # Line 2442
    return Body_Gain_empty


def calculate_Frm_NPgain(An_StatePhys, NPGain_FrmGain, Frm_Gain_empty, Body_Gain_empty, An_REgain_Calf):
    Frm_NPgain = NPGain_FrmGain * Frm_Gain_empty     # Line 2461
    Frm_NPgain = np.where(An_StatePhys == "Calf", (166.22 * Body_Gain_empty + 6.13 * An_REgain_Calf / Body_Gain_empty) / 1000, Frm_NPgain)
    return Frm_NPgain


def calculate_NPGain_RsrvGain(coeff_dict):
    req_coeff = ['CPGain_RsrvGain', 'Body_NP_CP']
    check_coeffs_in_coeff_dict(coeff_dict, req_coeff)
    NPGain_RsrvGain = coeff_dict['CPGain_RsrvGain'] * coeff_dict['Body_NP_CP']                   # Line 2467
    return NPGain_RsrvGain


def calculate_Rsrv_NPgain(NPGain_RsrvGain, Rsrv_Gain_empty):
    Rsrv_NPgain = NPGain_RsrvGain * Rsrv_Gain_empty                    # Line 2468
    return Rsrv_NPgain


def calculate_Body_NPgain(Frm_NPgain, Rsrv_NPgain):
    Body_NPgain = Frm_NPgain + Rsrv_NPgain      # Line 2473
    return Body_NPgain


def calculate_Body_CPgain(Body_NPgain, coeff_dict):
    req_coeff = ['Body_NP_CP']
    check_coeffs_in_coeff_dict(coeff_dict, req_coeff)
    Body_CPgain = Body_NPgain / coeff_dict['Body_NP_CP']     # Line 2475
    return Body_CPgain


def calculate_Body_CPgain_g(Body_CPgain):
    Body_CPgain_g = Body_CPgain * 1000     # Line 2477
    return Body_CPgain_g


def calculate_Rsrv_Gain(Trg_RsrvGain: float) -> float:
    """
    Trg_RsrvGain (float): Target gain or loss in body reserves (66% fat, 8% CP) in kg fresh weight/day
    """
    Rsrv_Gain = Trg_RsrvGain    # Line 2435
    return Rsrv_Gain


def calculate_Rsrv_Gain_empty(Rsrv_Gain: float) -> float:
    """
    Rsrv_Gain_empty: Body reserve gain assuming no gut fill association, kg/d
    """
    Rsrv_Gain_empty = Rsrv_Gain  # Assume no gut fill associated with reserves gain, Line 2441
    return Rsrv_Gain_empty


def calculate_Rsrv_Fatgain(Rsrv_Gain_empty: float, coeff_dict: dict) -> float:
    """
    FatGain_RsrvGain: Conversion factor from reserve gain to fat gain
    Rsrv_Fatgain: Body reserve fat gain kg/d
    """
    req_coeff = ['FatGain_RsrvGain']
    check_coeffs_in_coeff_dict(coeff_dict, req_coeff)
    Rsrv_Fatgain = coeff_dict['FatGain_RsrvGain'] * Rsrv_Gain_empty   # Line 2453
    return Rsrv_Fatgain


def calculate_CPGain_FrmGain(An_BW: float, An_BW_mature: float) -> float:
    """
    CPGain_FrmGain: CP gain per unit of frame gain kg/d
    """
    CPGain_FrmGain = 0.201 - 0.081 * An_BW / An_BW_mature     # CP gain / gain for heifers, Line 2458
    return CPGain_FrmGain


def calculate_Rsrv_CPgain(CPGain_FrmGain: float, Rsrv_Gain_empty: float) -> float:
    """
    Rsrv_CPgain: CP portion of body reserve gain, g/g
    """
    Rsrv_CPgain = CPGain_FrmGain * Rsrv_Gain_empty      # Line 2470
    return Rsrv_CPgain


def calculate_FatGain_FrmGain(An_StatePhys: str, An_REgain_Calf: float, An_BW: float, An_BW_mature: float) -> float:
    """
    FatGain_FrmGain: Fat gain per unit frame gain, kg/kg EBW (Empty body weight)
    This is the proportion of the empty body weight that is fat, which increases (and protein decreases) as the animal matures
    This is why it is scaled to a proportion of mature BW (An_BW / An_BW_mature)
    Also in equation 20-253
    """
    FatGain_FrmGain = np.where(An_StatePhys == "Calf",  # Line 2446
                               0.0786 + 0.0370 * An_REgain_Calf,   # Calves, ..., g/g EBW
                               (0.067 + 0.375 * An_BW / An_BW_mature))  # Heifers and cows, g/g EBW p. 258 Equation 11-5a
    if np.isnan(FatGain_FrmGain):   # trap NA when no Body_Gain, Line 2449
        FatGain_FrmGain = 0
    return FatGain_FrmGain


def calculate_Frm_Gain(Trg_FrmGain: float) -> float:
    """
    Frame gain, kg/d
    """
    Frm_Gain = Trg_FrmGain  # Add any predictions of ADG and select Trg or Pred ADG here, Line 2434
    return Frm_Gain


def calculate_Frm_Gain_empty(Frm_Gain: float, Dt_DMIn_ClfLiq: float, Dt_DMIn_ClfStrt: float, coeff_dict: dict) -> float:
    """
    Frm_Gain_empty: Frame gain assuming the dame gut fill for frame gain, kg/d
    Equation 11-6b : 0.85 * gain (kg/d) - assumes the 15% of live = empty
    Also in Equation 20-250 
    """
    Frm_Gain_empty = Frm_Gain * (1 - coeff_dict['An_GutFill_BW'])   # Assume the same gut fill for frame gain, Line 2439 
    if Dt_DMIn_ClfLiq > 0 and Dt_DMIn_ClfStrt > 0:
        # slightly different for grain & milk fed, Line 2440
        Frm_Gain_empty = Frm_Gain * 0.91
    return Frm_Gain_empty


def calculate_Frm_Fatgain(FatGain_FrmGain: float, Frm_Gain_empty: float) -> float:
    """
    Frm_Fatgain: Frame fat gain kg/?
    FatGain_FrmGain is the kg of fat per kg of empty frame gain, based on the BW of the animal as a % of mature BW. 
    Here, the actual kg/kg * EBG (kg/d) = frame fat gain kg/d
    In the book, the Fat_ADG from equation 3-20a (which is  FatGain_FrmGain here) is corrected for empty body weight (e.g. x 0.85), keeping it in kg/kg units. 
     this is a mix of Equations 11-5a and 11-6a (but 11-6a assumes 0.85, not EBG/ADG)
    """
    Frm_Fatgain = FatGain_FrmGain * Frm_Gain_empty      # Line 2452
    return Frm_Fatgain


def calculate_NPGain_FrmGain(CPGain_FrmGain: float, coeff_dict: dict) -> float:
    """
    NPGain_FrmGain: Net protein gain per unit frame gain
    NOTE for these gain per unit gain values I believe they are unitless/have units g/g, not much said in the R code
    """
    req_coeff = ['Body_NP_CP']
    check_coeffs_in_coeff_dict(coeff_dict, req_coeff)
    # Convert to CP to TP gain / gain, Line 2459
    NPGain_FrmGain = CPGain_FrmGain * coeff_dict['Body_NP_CP']
    return NPGain_FrmGain


def calculate_Frm_NPgain(An_StatePhys: str, NPGain_FrmGain: float, Frm_Gain_empty: float, Body_Gain_empty: float, An_REgain_Calf: float) -> float:
    """
    Frm_NPgain: NP portion of frame gain
    """
    Frm_NPgain = NPGain_FrmGain * Frm_Gain_empty    # TP gain, Line 2460
    if An_StatePhys == "Calf":
        Frm_NPgain = (166.22 * Body_Gain_empty + 6.13 * An_REgain_Calf / Body_Gain_empty) / 1000    # Line 2461
    return Frm_NPgain


def calculate_Frm_CPgain(Frm_NPgain: float, coeff_dict: dict) -> float:
    """
    Frm_CPgain: CP portion of frame gain
    """
    req_coeff = ['Body_NP_CP']
    check_coeffs_in_coeff_dict(coeff_dict, req_coeff)
    Frm_CPgain = Frm_NPgain / coeff_dict['Body_NP_CP']     # Line 2463
    return Frm_CPgain


def calculate_Body_NPgain_g(Body_NPgain: float) -> float:
    """
    Body_NPgain_g: Net protein from frame and reserve gain, g
    """
    Body_NPgain_g = Body_NPgain * 1000  # Line 2475
    return Body_NPgain_g


def calculate_An_BWmature_empty(An_BW_mature, coeff_dict):
    """
    An_BWmature_empty: kg bodyweight with no gut fill 
    """
    req_coeff = ['An_GutFill_BWmature']
    check_coeffs_in_coeff_dict(coeff_dict, req_coeff)
    An_BWmature_empty = An_BW_mature * (1 - coeff_dict['An_GutFill_BWmature'])
    return An_BWmature_empty
