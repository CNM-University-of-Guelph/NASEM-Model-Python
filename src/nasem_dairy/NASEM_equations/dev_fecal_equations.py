# dev_fecal_equations
import numpy as np
from nasem_dairy.ration_balancer.ration_balancer_functions import check_coeffs_in_coeff_dict


def calculate_Fe_rOMend(Dt_DMIn, coeff_dict):
    req_coeff = ['Fe_rOMend_DMI']
    check_coeffs_in_coeff_dict(coeff_dict, req_coeff)
    # Line 1007, From Tebbe et al., 2017.  Negative interecept represents endogenous rOM
    Fe_rOMend = coeff_dict['Fe_rOMend_DMI'] / 100 * Dt_DMIn
    return Fe_rOMend


def calculate_Fe_RUP(An_RUPIn, InfSI_TPIn, An_idRUPIn):
    Fe_RUP = An_RUPIn + InfSI_TPIn - An_idRUPIn  # SI infusions not considered
    return Fe_RUP


def calculate_Fe_RumMiCP(Du_MiCP, Du_idMiCP):
    Fe_RumMiCP = Du_MiCP - Du_idMiCP          # Line 1196
    return Fe_RumMiCP


def calculate_Fe_CPend_g(
        An_StatePhys: str, 
        An_DMIn: float, 
        An_NDF: float, 
        Dt_DMIn: float, 
        Dt_DMIn_ClfLiq: float, 
        NonMilkCP_ClfLiq: int #0 or 1
        ):
    '''
    An_DMIn = DMI + Infusion from calculate_An_DMIn()
    Fe_CPend_g = Metabolic Fecal crude Protein (MFP) in g/d
    Dt_DMIn_ClfLiq = liquid feed dry matter intake in kg/d
    NonMilkCP_ClfLiq = or Milk_Replacer_eqn. equation_selection where 0=no non-milk protein sources in calf liquid feeds, 1=non-milk CP sources used. See lin 1188 R code
    '''
    if An_StatePhys == "Calf":
        # equation 10-12; p. 210;
        # Originally K_FeCPend_ClfLiq is set to 11.9 in book; but can be either 11.9 or 34.4 
        # (An_DMIn - Dt_DMIn_ClfLiq) represents solid feed DM intake
        # should only be called if calf:
        K_FeCPend_ClfLiq = np.where(NonMilkCP_ClfLiq > 0, 34.4, 11.9)

        Fe_CPend_g = K_FeCPend_ClfLiq * Dt_DMIn_ClfLiq + 20.6 * (An_DMIn - Dt_DMIn_ClfLiq)
    else:
        #g/d, endogen secretions plus urea capture in microbies in rumen and LI
        # Line 1187 R Code
        Fe_CPend_g = (12 + 0.12 * An_NDF) * Dt_DMIn
    
    # Fe_CPend_g = (12 + 0.12 * An_NDF) * Dt_DMIn
    # Fe_CPend_g = np.where(An_StatePhys == "Calf", K_FeCPend_ClfLiq * Dt_DMIn_ClfLiq + 20.6 * (An_DMIn - Dt_DMIn_ClfLiq), Fe_CPend_g)
    return Fe_CPend_g


def calculate_Fe_CPend(Fe_CPend_g):
    Fe_CPend = Fe_CPend_g / 1000                   # Line 1190
    return Fe_CPend


def calculate_Fe_CP(An_StatePhys, Dt_CPIn_ClfLiq, Dt_dcCP_ClfDry, An_CPIn, Fe_RUP, Fe_RumMiCP, Fe_CPend, InfSI_NPNCPIn, coeff_dict):
    req_coeff = ['dcNPNCP', 'Dt_dcCP_ClfLiq']
    check_coeffs_in_coeff_dict(coeff_dict, req_coeff)
    # Line 1202, Double counting portion of RumMiCP derived from End CP. Needs to be fixed. MDH
    Fe_CP = Fe_RUP + Fe_RumMiCP + Fe_CPend + \
        InfSI_NPNCPIn * (1 - coeff_dict['dcNPNCP'] / 100)
    Fe_CP = np.where(An_StatePhys == "Calf",
                     (1 - coeff_dict['Dt_dcCP_ClfLiq']) * Dt_CPIn_ClfLiq +
                     (1 - Dt_dcCP_ClfDry) * (An_CPIn - Dt_CPIn_ClfLiq) + Fe_CPend,
                     Fe_CP)  # CP based for calves. Ignores RDP, RUP, Fe_NPend, etc.  Needs refinement.
    return Fe_CP
