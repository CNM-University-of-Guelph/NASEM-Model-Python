"""Fecal output calculations for nitrogen and organic matter losses.

This module includes functions to estimate the amount of nitrogen and organic 
matter lost through feces, based on dietary intake and physiological state.
"""

import numpy as np
import pandas as pd


def calculate_Fe_rOMend(Dt_DMIn: float, coeff_dict: dict) -> float:
    """
    Examples
    --------
    ```
    coeff_dict = {"Fe_rOMend_DMI": 3.43}
    
    calculate_Fe_rOMend(
        Dt_DMIn = 30.0, coeff_dict = coeff_dict
    )
    ```
    """
    # Line 1007, From Tebbe et al., 2017. Negative interecept represents endogenous rOM
    Fe_rOMend = coeff_dict['Fe_rOMend_DMI'] / 100 * Dt_DMIn
    return Fe_rOMend


def calculate_Fe_RUP(
    An_RUPIn: float, 
    InfSI_TPIn: float, 
    An_idRUPIn: float
) -> float:
    Fe_RUP = An_RUPIn + InfSI_TPIn - An_idRUPIn  # SI infusions not considered
    return Fe_RUP


def calculate_Fe_RumMiCP(Du_MiCP: float, Du_idMiCP: float) -> float:
    Fe_RumMiCP = Du_MiCP - Du_idMiCP  # Line 1196
    return Fe_RumMiCP


def calculate_K_FeCPend_ClfLiq(NonMilkCP_ClfLiq: int):
    K_FeCPend_ClfLiq = 34.4 if NonMilkCP_ClfLiq > 0 else 11.9
    return K_FeCPend_ClfLiq


def calculate_Fe_CPend_g(
    An_StatePhys: str, 
    An_DMIn: float,
    An_NDF: float, 
    Dt_DMIn: float, 
    Dt_DMIn_ClfLiq: float, 
    K_FeCPend_ClfLiq: float
) -> float:
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
        Fe_CPend_g = (K_FeCPend_ClfLiq * Dt_DMIn_ClfLiq + 
                      20.6 * (An_DMIn - Dt_DMIn_ClfLiq))
    else:
        #g/d, endogen secretions plus urea capture in microbies in rumen and LI
        # Line 1187
        Fe_CPend_g = (12 + 0.12 * An_NDF) * Dt_DMIn
    return Fe_CPend_g


def calculate_Fe_CPend(Fe_CPend_g: float) -> float:
    Fe_CPend = Fe_CPend_g / 1000  # Line 1190
    return Fe_CPend


def calculate_Fe_CP(
    An_StatePhys: str, 
    Dt_CPIn_ClfLiq: float, 
    Dt_dcCP_ClfDry: float, 
    An_CPIn: float,
    Fe_RUP: float, 
    Fe_RumMiCP: float, 
    Fe_CPend: float, 
    InfSI_NPNCPIn: float, 
    coeff_dict: dict
) -> float:
    """
    Examples
    --------
    ```
    coeff_dict = {"dcNPNCP": 100, "Dt_dcCP_ClfLiq": 0.95}
    
    calculate_Fe_CP(
        An_StatePhys = "Adult", Dt_CPIn_ClfLiq = 10.0, Dt_dcCP_ClfDry = 0.75, 
        An_CPIn = 50.0, Fe_RUP = 5.0, Fe_RumMiCP = 3.0, Fe_CPend = 2.0, 
        InfSI_NPNCPIn = 4.0, coeff_dict = coeff_dict
    )
    ```
    """
    # Line 1202, Double counting portion of RumMiCP derived from End CP. Needs to be fixed. MDH
    Fe_CP = (Fe_RUP + Fe_RumMiCP + Fe_CPend + 
             InfSI_NPNCPIn * (1 - coeff_dict['dcNPNCP'] / 100))
    # CP based for calves. Ignores RDP, RUP, Fe_NPend, etc.  Needs refinement.
    if An_StatePhys == "Calf": 
        Fe_CP = ((1 - coeff_dict['Dt_dcCP_ClfLiq']) * Dt_CPIn_ClfLiq 
                 + (1 - Dt_dcCP_ClfDry) * (An_CPIn - Dt_CPIn_ClfLiq) + Fe_CPend)    
    return Fe_CP


def calculate_Fe_NPend(Fe_CPend: float) -> float:
    """
    Fe_NPend: Fecal NP from endogenous secretions and urea captured by microbes, kg
    """
    Fe_NPend = Fe_CPend * 0.73  # 73% TP from Lapierre, kg/d, Line 1191
    return Fe_NPend


def calculate_Fe_NPend_g(Fe_NPend: float) -> float:
    """
    Fe_NPend_g: Fe_NPend in g
    """
    Fe_NPend_g = Fe_NPend * 1000  # Line 1192
    return Fe_NPend_g


def calculate_Fe_MPendUse_g_Trg(
    An_StatePhys: str, 
    Fe_CPend_g: float,
    Fe_NPend_g: float, 
    Km_MP_NP_Trg: float
) -> float:
    """
    Fe_MPendUse_g_Trg: Fecal MP from endogenous secretions and urea captured by microbes, g
    """
    if An_StatePhys == "Calf" or An_StatePhys == "Heifer":
        Fe_MPendUse_g_Trg = Fe_CPend_g / Km_MP_NP_Trg  # Line 2669
    else:
        Fe_MPendUse_g_Trg = Fe_NPend_g / Km_MP_NP_Trg  # Line 2668
    return Fe_MPendUse_g_Trg


def calculate_Fe_rOM(An_rOMIn: float, An_DigrOMaIn: float) -> float:
    """
    Fe_rOM: Fecal residual organic matter, kg/d
    """
    Fe_rOM = An_rOMIn - An_DigrOMaIn  
    # includes undigested rOM and fecal endogenous rOM, Line 1045
    return Fe_rOM


def calculate_Fe_St(
    Dt_StIn: float, 
    Inf_StIn: float,
    An_DigStIn: float
) -> float:
    """
    Fe_St: Fecal starch, kg/d
    """
    Fe_St = Dt_StIn + Inf_StIn - An_DigStIn  # Line 1052
    return Fe_St


def calculate_Fe_NDF(Dt_NDFIn: float, Dt_DigNDFIn: float) -> float:
    """
    Fe_NDF: Fecal NDF, kg/d
    """
    Fe_NDF = Dt_NDFIn - Dt_DigNDFIn
    return Fe_NDF


def calculate_Fe_NDFnf(Dt_NDFnfIn: float, Dt_DigNDFnfIn: float) -> float:
    """
    Fe_NDFnf: Fecal Nitrogen free NDF, kg/d
    """
    Fe_NDFnf = Dt_NDFnfIn - Dt_DigNDFnfIn
    return Fe_NDFnf


def calculate_Fe_Nend(Fe_CPend: float) -> float:
    """
    Fe_Nend: Endogenous N lost in feces (kg/d)
    """
    Fe_Nend = Fe_CPend * 0.16  # kg/d, Line 1190
    return Fe_Nend


def calculate_Fe_RDPend(
    Fe_CPend: float, 
    An_RDPIn: float,
    An_CPIn: float
) -> float:
    """
    Fe_RDPend: Endogenous RDP lost in feces (kg/d), arbitrary value (see comment)
    """
    Fe_RDPend = Fe_CPend * An_RDPIn / An_CPIn  
    # Arbitrary assignment of Fe_CPend to RDP and RUP based on CPI proportion, Line 1193
    return Fe_RDPend


def calculate_Fe_RUPend(
    Fe_CPend: float, 
    An_RUPIn: float,
    An_CPIn: float
) -> float:
    """
    Fe_RUPend: Endogenous RUP lost in feces (kg/d), arbitrary value (see comment)
    """
    Fe_RUPend = Fe_CPend * An_RUPIn / An_CPIn  
    # Only used for tabular reporting to DE from RDP and RUP.  No other function., Line 1194
    return Fe_RUPend


def calculate_Fe_MiTP(Du_MiTP: float, Du_idMiTP: float) -> float:
    """
    Fe_MiTP: Microbial true protein lost in feces (kg/d)
    """
    Fe_MiTP = Du_MiTP - Du_idMiTP  # Line 1196
    return Fe_MiTP


def calculate_Fe_InfCP(
    InfRum_RUPIn: float, 
    InfSI_CPIn: float,
    InfRum_idRUPIn: float, 
    InfSI_idCPIn: float
) -> float:
    """
    Fe_InfCP: Infused CP lost in feces (kg/d)
    """
    Fe_InfCP = ((InfRum_RUPIn + InfSI_CPIn) - 
                (InfRum_idRUPIn + InfSI_idCPIn)) # Included in An_RUP, Line 1198
    return Fe_InfCP


def calculate_Fe_TP(Fe_RUP: float, Fe_MiTP: float, Fe_NPend: float) -> float:
    """
    Fe_TP: True protein lost in feces (kg/d)
    """
    Fe_TP = Fe_RUP + Fe_MiTP + Fe_NPend  # Doesn't apply for calves, Line 1204
    return Fe_TP


def calculate_Fe_N(Fe_CP: float) -> float:
    """
    Fe_N: N lost in feces (kg/d)
    """
    Fe_N = Fe_CP * 0.16  # Line 1205
    return Fe_N


def calculate_Fe_N_g(Fe_N: float) -> float:
    """
    Fe_N_g: N lost in feces (g/d)
    """
    Fe_N_g = Fe_N * 1000  # Line 1206
    return Fe_N_g


def calculate_Fe_FA(
    Dt_FAIn: float, 
    InfRum_FAIn: float, 
    InfSI_FAIn: float,
    Dt_DigFAIn: float, 
    Inf_DigFAIn: float
) -> float:
    """
    Fe_FA: FA lost in feces (kg/d)
    """
    Fe_FA = Dt_FAIn + InfRum_FAIn + InfSI_FAIn - Dt_DigFAIn - Inf_DigFAIn 
    # Line 1310
    return Fe_FA


def calculate_Fe_OM(
    Fe_CP: float, 
    Fe_NDF: float, 
    Fe_St: float, 
    Fe_rOM: float,
    Fe_FA: float
) -> float:
    """
    Fe_OM: Organic matter lost in feces (kg/d)
    """
    Fe_OM = Fe_CP + Fe_NDF + Fe_St + Fe_rOM + Fe_FA  # kg/d, Line 1314
    return Fe_OM


def calculate_Fe_OM_end(Fe_rOMend: float, Fe_CPend: float) -> float:
    """
    Fe_OM_end: Endogenous organic matter lost in feces (kg/d)
    """
    Fe_OM_end = Fe_rOMend + Fe_CPend  # Line 1315
    return Fe_OM_end


def calculate_Fe_DEMiCPend(Fe_RumMiCP: float, coeff_dict: dict) -> float:
    """
    Fe_DEMiCPend: Digestable energy in undigested ruminacl MiCP and RDP (Mcal/d)
    
    Examples
    --------
    ```
    coeff_dict = {"En_CP": 5.65}
    
    calculate_Fe_DEMiCPend(
        Fe_RumMiCP = 20.0, coeff_dict = coeff_dict
    )
    ```
    """
    Fe_DEMiCPend = Fe_RumMiCP * coeff_dict['En_CP']
    # DE in undigested ruminal MiCP and RDP portion of Fe_EndCP, Line 1356
    return Fe_DEMiCPend


def calculate_Fe_DERDPend(Fe_RDPend: float, coeff_dict: dict) -> float:
    """
    Fe_DERDPend: Digestable energy in fecal RDP, arbitrary value (Mcal/d)
    
    Examples
    --------
    ```
    coeff_dict = {"En_CP": 5.65}
    
    calculate_Fe_DERDPend(
        Fe_RDPend = 15.0, coeff_dict = coeff_dict
    )
    ```
    """
    Fe_DERDPend = Fe_RDPend * coeff_dict['En_CP']
    # Arbitrary DE assignment of Fe_CPend DE to RDP and RUP. Reporting use only, Line 1357
    return Fe_DERDPend


def calculate_Fe_DERUPend(Fe_RUPend: float, coeff_dict: dict) -> float:
    """
    Fe_DERUPend: Digestable energy in fecal RUP, arbitrary value (Mcal/d)
    
    Examples
    --------
    ```
    coeff_dict = {"En_CP": 5.65}
    
    calculate_Fe_DERUPend(
        Fe_RUPend = 10.0, coeff_dict = coeff_dict
    )
    ```
    """
    Fe_DERUPend = Fe_RUPend * coeff_dict['En_CP']  # Line 1358
    return Fe_DERUPend


def calculate_Fe_DEout(An_GEIn: float, An_DEIn: float) -> float:
    """
    Fe_DEout: Digestable energy lost in feces (Mcal/d)
    """
    Fe_DEout = An_GEIn - An_DEIn  # Line 1380
    return Fe_DEout


def calculate_Fe_DE_GE(Fe_DEout: float, An_GEIn: float) -> float:
    """
    Fe_DE_GE: Ratio of DE loss to GE
    """
    Fe_DE_GE = Fe_DEout / An_GEIn  # Line 1381
    return Fe_DE_GE


def calculate_Fe_DE(Fe_DEout: float, An_DMIn: float) -> float:
    """
    Fe_DE: Digestable energy lost in feces per kg DMI (Mcal/kg)
    """
    Fe_DE = Fe_DEout / An_DMIn  # Line 1382
    return Fe_DE


def calculate_Fe_AAMetab_TP(aa_list: list, coeff_dict: dict) -> np.ndarray:
    Fe_AAMetab_TP = np.array([coeff_dict[f"Fe_{aa}Metab_TP"] for aa in aa_list])
    return Fe_AAMetab_TP


def calculate_Fe_AAMet_g(
    Fe_NPend_g: float, 
    Fe_AAMetab_TP: np.ndarray
) -> np.ndarray:
    """
    Fe_AAMet_g: Metabolic fecal AA (g/d)
    """
    Fe_AAMet_g = Fe_NPend_g * Fe_AAMetab_TP / 100  # Lines 1994-2003
    return Fe_AAMet_g


def calculate_Fe_AAMet_AbsAA(
    Fe_AAMet_g: np.array,
        Abs_AA_g: pd.Series
) -> np.array:
    """
    Fe_AAMet_AbsAA: Metabolic fecal AA as fraction of absorbed aa 
    """
    Fe_AAMet_AbsAA = Fe_AAMet_g / Abs_AA_g  # Lines 2006-2015
    return Fe_AAMet_AbsAA


def calculate_Fe_MPendUse_g(Fe_NPend_g: float, Km_MP_NP: float) -> float:
    """
    Fe_MPendUse_g: Endogenous MP in feces (g/d)
    """
    Fe_MPendUse_g = Fe_NPend_g / Km_MP_NP  # Line 2726
    return Fe_MPendUse_g
