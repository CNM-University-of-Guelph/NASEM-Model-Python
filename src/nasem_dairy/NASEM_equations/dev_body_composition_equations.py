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

