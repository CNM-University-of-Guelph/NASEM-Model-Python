"""Functions to calculate nutrients from infusions. 
"""

import numpy as np


def calculate_Inf_TPIn(Inf_CPIn: float, Inf_NPNCPIn: float) -> float:
    Inf_TPIn = Inf_CPIn - Inf_NPNCPIn  # Line 848
    return Inf_TPIn


def calculate_Inf_OMIn(Inf_DMIn: float, Inf_AshIn: float) -> float:
    Inf_OMIn = Inf_DMIn - Inf_AshIn  # Line 853
    return Inf_OMIn


def calculate_Inf_Rum(Inf_Location: str) -> int:
    if Inf_Location == "Rumen": # Line 874
        Inf_Rum = 1
        return Inf_Rum
    Inf_Rum = 0
    return Inf_Rum


def calculate_Inf_SI(Inf_Location: str) -> int:
    if Inf_Location in ["Abomasum", "Duodenum", "Duodenal"]: # Line 875
        Inf_SI = 1
        return Inf_SI
    Inf_SI = 0 
    return Inf_SI


def calculate_Inf_Art(Inf_Location: str) -> int:
    if Inf_Location in ["Jugular", "Arterial", "Iliac Artery", "Blood"]:
        Inf_Art = 1 # Line 876
    else:
        Inf_Art = 0
    return Inf_Art 


def calculate_InfRum_TPIn(InfRum_CPIn: float, InfRum_NPNCPIn: float) -> float:
    InfRum_TPIn = InfRum_CPIn - InfRum_NPNCPIn  # Line 884
    return InfRum_TPIn


def calculate_InfSI_TPIn(InfSI_CPIn: float, InfSI_NPNCPIn: float) -> float:
    InfSI_TPIn = InfSI_CPIn - InfSI_NPNCPIn
    return InfSI_TPIn


def calculate_InfRum_RUPIn(
    InfRum_CPAIn: float, 
    InfRum_CPBIn: float, 
    InfRum_CPCIn: float,
    InfRum_NPNCPIn: float, 
    Inf_KdCPB: float, 
    coeff_dict: dict
) -> float:
    """
    Examples
    --------
    ```
    coeff_dict = {"fCPAdu": 0.064, "KpConc": 5.28}
    
    calculate_InfRum_RUPIn(
        InfRum_CPAIn = 50.0, InfRum_CPBIn = 30.0, InfRum_CPCIn = 20.0, 
        InfRum_NPNCPIn = 10.0, Inf_KdCPB = 0.05, coeff_dict = coeff_dict
    )
    ```
    """
    InfRum_RUPIn = ((InfRum_CPAIn - InfRum_NPNCPIn) * coeff_dict['fCPAdu'] + 
                    InfRum_CPBIn * coeff_dict['KpConc'] / 
                    (Inf_KdCPB + coeff_dict['KpConc']) + InfRum_CPCIn) # Line 1084
    return InfRum_RUPIn


def calculate_InfRum_RUP_CP(InfRum_CPIn: float, InfRum_RUPIn: float) -> float:
    if InfRum_CPIn == 0:
        InfRum_RUP_CP = 0
    else:
        InfRum_RUP_CP = InfRum_RUPIn / InfRum_CPIn * 100  # Line 1088
    return InfRum_RUP_CP


def calculate_InfRum_idRUPIn(InfRum_RUPIn: float, Inf_dcRUP: float) -> float:
    InfRum_idRUPIn = InfRum_RUPIn * Inf_dcRUP / 100  # RUP, Line 1089
    return InfRum_idRUPIn


def calculate_InfSI_idTPIn(InfSI_TPIn: float, Inf_dcRUP: float) -> float:
    InfSI_idTPIn = InfSI_TPIn * Inf_dcRUP / 100 # intestinally infused, Line 1090
    return InfSI_idTPIn


def calculate_InfSI_idCPIn(
    InfSI_idTPIn: float, 
    InfSI_NPNCPIn: float, 
    coeff_dict: dict
) -> float:
    """
    Examples
    --------
    ```
    coeff_dict = {"dcNPNCP": 100}
    
    calculate_InfSI_idCPIn(
        InfSI_idTPIn = 40.0, InfSI_NPNCPIn = 20.0, coeff_dict = coeff_dict
    )
    ```
    """
    # SI infused idTP + urea or ammonia, Line 1092
    InfSI_idCPIn = InfSI_idTPIn + InfSI_NPNCPIn * coeff_dict['dcNPNCP'] / 100
    return InfSI_idCPIn


def calculate_Inf_idCPIn(InfRum_idRUPIn: float, InfSI_idCPIn: float) -> float:
    # RUP + intestinally infused, Line 1093
    Inf_idCPIn = InfRum_idRUPIn + InfSI_idCPIn
    return Inf_idCPIn


def calculate_InfRum_RDPIn(InfRum_CPIn: float, InfRum_RUPIn: float) -> float:
    InfRum_RDPIn = InfRum_CPIn - InfRum_RUPIn  # Line 1105
    return InfRum_RDPIn


def calculate_Inf_DigFAIn(Inf_FAIn: float, coeff_dict: dict) -> float:
    """
    Examples
    --------
    ```
    coeff_dict = {"TT_dcFA_Base": 73}
    
    calculate_Inf_DigFAIn(
        Inf_FAIn = 50.0, coeff_dict = coeff_dict
    )
    ```
    """
    # Line 1306, used dcFA which is similar to oil, but should define for each infusate
    Inf_DigFAIn = Inf_FAIn * coeff_dict['TT_dcFA_Base']
    return Inf_DigFAIn


def calculate_Inf_DEAcetIn(Inf_AcetIn: float, coeff_dict: dict) -> float:
    """
    Examples
    --------
    ```
    coeff_dict = {"En_Acet": 3.48}
    
    calculate_Inf_DEAcetIn(
        Inf_AcetIn = 40.0, coeff_dict = coeff_dict
    )
    ```
    """
    Inf_DEAcetIn = Inf_AcetIn * coeff_dict['En_Acet']
    return Inf_DEAcetIn


def calculate_Inf_DEPropIn(Inf_PropIn: float, coeff_dict: dict) -> float:
    """
    Examples
    --------
    ```
    coeff_dict = {"En_Prop": 4.96}
    
    calculate_Inf_DEPropIn(
        Inf_PropIn = 30.0, coeff_dict = coeff_dict
    )
    ```
    """
    Inf_DEPropIn = Inf_PropIn * coeff_dict['En_Prop']  # Line 1363
    return Inf_DEPropIn


def calculate_Inf_DEButrIn(Inf_ButrIn: float, coeff_dict: dict) -> float:
    """
    Examples
    --------
    ```
    coeff_dict = {"En_Butr": 5.95}
    
    calculate_Inf_DEButrIn(
        Inf_ButrIn = 20.0, coeff_dict = coeff_dict
    )
    ```
    """
    Inf_DEButrIn = Inf_ButrIn * coeff_dict['En_Butr']
    return Inf_DEButrIn


def calculate_Inf_DMIn(Inf_DM_g: float) -> float:
    Inf_DMIn = Inf_DM_g / 1000
    return Inf_DMIn


def calculate_Inf_StIn(Inf_St_g: float) -> float:
    Inf_StIn = Inf_St_g / 1000
    return Inf_StIn


def calculate_Inf_NDFIn(Inf_NDF_g: float) -> float:
    Inf_NDFIn = Inf_NDF_g / 1000
    return Inf_NDFIn


def calculate_Inf_ADFIn(Inf_ADF_g: float) -> float:
    Inf_ADFIn = Inf_ADF_g / 1000
    return Inf_ADFIn


def calculate_Inf_GlcIn(Inf_Glc_g: float) -> float:
    Inf_GlcIn = Inf_Glc_g / 1000
    return Inf_GlcIn


def calculate_Inf_CPIn(Inf_CP_g: float) -> float:
    Inf_CPIn = Inf_CP_g / 1000
    return Inf_CPIn


def calculate_Inf_NPNCPIn(Inf_NPNCP_g: float) -> float:
    Inf_NPNCPIn = Inf_NPNCP_g / 1000
    return Inf_NPNCPIn


def calculate_Inf_FAIn(Inf_FA_g: float) -> float:
    Inf_FAIn = Inf_FA_g / 1000
    return Inf_FAIn


def calculate_Inf_AshIn(Inf_Ash_g: float) -> float:
    Inf_AshIn = Inf_Ash_g / 1000
    return Inf_AshIn


def calculate_Inf_VFAIn(Inf_VFA_g: float) -> float:
    Inf_VFAIn = Inf_VFA_g / 1000
    return Inf_VFAIn


def calculate_Inf_AcetIn(Inf_Acet_g: float) -> float:
    Inf_AcetIn = Inf_Acet_g / 1000
    return Inf_AcetIn


def calculate_Inf_PropIn(Inf_Prop_g: float) -> float:
    Inf_PropIn = Inf_Prop_g / 1000
    return Inf_PropIn


def calculate_Inf_ButrIn(Inf_Butr_g: float) -> float:
    Inf_ButrIn = Inf_Butr_g / 1000
    return Inf_ButrIn


def calculate_Inf_CPAIn(Inf_CP_g: float, Inf_CPARum_CP: float) -> float:
    Inf_CPAIn = (Inf_CP_g / 1000) * (Inf_CPARum_CP / 100)
    return Inf_CPAIn


def calculate_Inf_CPBIn(Inf_CP_g: float, Inf_CPBRum_CP: float) -> float:
    Inf_CPBIn = (Inf_CP_g / 1000) * (Inf_CPBRum_CP / 100)
    return Inf_CPBIn


def calculate_Inf_CPCIn(Inf_CP_g: float, Inf_CPCRum_CP: float) -> float:
    Inf_CPCIn = (Inf_CP_g / 1000) * (Inf_CPCRum_CP / 100)
    return Inf_CPCIn


def calculate_Inf_DM(Dt_DMIn: float, Inf_DMIn: float) -> float:
    Inf_DM = (Inf_DMIn / (Dt_DMIn + Inf_DMIn)) * 100
    return Inf_DM


def calculate_Inf_OM(Dt_DMIn: float, Inf_OMIn: float) -> float:
    Inf_OM = (Inf_OMIn / (Dt_DMIn + Inf_OMIn)) * 100
    return Inf_OM


def calculate_Inf_St(Dt_DMIn: float, Inf_StIn: float) -> float:
    Inf_St = (Inf_StIn / (Dt_DMIn + Inf_StIn)) * 100
    return Inf_St


def calculate_Inf_NDF(Dt_DMIn: float, Inf_NDFIn: float) -> float:
    Inf_NDF = (Inf_NDFIn / (Dt_DMIn + Inf_NDFIn)) * 100
    return Inf_NDF


def calculate_Inf_ADF(Dt_DMIn: float, Inf_ADFIn: float) -> float:
    Inf_ADF = (Inf_ADFIn / (Dt_DMIn + Inf_ADFIn)) * 100
    return Inf_ADF


def calculate_Inf_Glc(Dt_DMIn: float, Inf_GlcIn: float) -> float:
    Inf_Glc = (Inf_GlcIn / (Dt_DMIn + Inf_GlcIn)) * 100
    return Inf_Glc


def calculate_Inf_CP(Dt_DMIn: float, Inf_CPIn: float) -> float:
    Inf_CP = (Inf_CPIn / (Dt_DMIn + Inf_CPIn)) * 100
    return Inf_CP


def calculate_Inf_FA(Dt_DMIn: float, Inf_FAIn: float) -> float:
    Inf_FA = (Inf_FAIn / (Dt_DMIn + Inf_FAIn)) * 100
    return Inf_FA


def calculate_Inf_VFA(Dt_DMIn: float, Inf_VFAIn: float) -> float:
    Inf_VFA = (Inf_VFAIn / (Dt_DMIn + Inf_VFAIn)) * 100
    return Inf_VFA


def calculate_Inf_Acet(Dt_DMIn: float, Inf_AcetIn: float) -> float:
    Inf_Acet = (Inf_AcetIn / (Dt_DMIn + Inf_AcetIn)) * 100
    return Inf_Acet


def calculate_Inf_Prop(Dt_DMIn: float, Inf_PropIn: float) -> float:
    Inf_Prop = (Inf_PropIn / (Dt_DMIn + Inf_PropIn)) * 100
    return Inf_Prop


def calculate_Inf_Butr(Dt_DMIn: float, Inf_ButrIn: float) -> float:
    Inf_Butr = (Inf_ButrIn / (Dt_DMIn + Inf_ButrIn)) * 100
    return Inf_Butr


def calculate_InfRum_DMIn(Inf_Rum: float, Inf_DMIn: float) -> float:
    InfRum_DMIn = Inf_Rum * Inf_DMIn
    return InfRum_DMIn


def calculate_InfRum_OMIn(Inf_Rum: float, Inf_OMIn: float) -> float:
    InfRum_OMIn = Inf_Rum * Inf_OMIn
    return InfRum_OMIn


def calculate_InfRum_CPIn(Inf_Rum: float, Inf_CPIn: float) -> float:
    InfRum_CPIn = Inf_Rum * Inf_CPIn
    return InfRum_CPIn


def calculate_InfRum_NPNCPIn(Inf_Rum: float, Inf_NPNCPIn: float) -> float:
    InfRum_NPNCPIn = Inf_Rum * Inf_NPNCPIn
    return InfRum_NPNCPIn


def calculate_InfRum_CPAIn(Inf_Rum: float, Inf_CPAIn: float) -> float:
    InfRum_CPAIn = Inf_Rum * Inf_CPAIn
    return InfRum_CPAIn


def calculate_InfRum_CPBIn(Inf_Rum: float, Inf_CPBIn: float) -> float:
    InfRum_CPBIn = Inf_Rum * Inf_CPBIn
    return InfRum_CPBIn


def calculate_InfRum_CPCIn(Inf_Rum: float, Inf_CPCIn: float) -> float:
    InfRum_CPCIn = Inf_Rum * Inf_CPCIn
    return InfRum_CPCIn


def calculate_InfRum_StIn(Inf_Rum: float, Inf_StIn: float) -> float:
    InfRum_StIn = Inf_Rum * Inf_StIn
    return InfRum_StIn


def calculate_InfRum_NDFIn(Inf_Rum: float, Inf_NDFIn: float) -> float:
    InfRum_NDFIn = Inf_Rum * Inf_NDFIn
    return InfRum_NDFIn


def calculate_InfRum_ADFIn(Inf_Rum: float, Inf_ADFIn: float) -> float:
    InfRum_ADFIn = Inf_Rum * Inf_ADFIn
    return InfRum_ADFIn


def calculate_InfRum_FAIn(Inf_Rum: float, Inf_FAIn: float) -> float:
    InfRum_FAIn = Inf_Rum * Inf_FAIn
    return InfRum_FAIn


def calculate_InfRum_GlcIn(Inf_Rum: float, Inf_GlcIn: float) -> float:
    InfRum_GlcIn = Inf_Rum * Inf_GlcIn
    return InfRum_GlcIn


def calculate_InfRum_VFAIn(Inf_Rum: float, Inf_VFAIn: float) -> float:
    InfRum_VFAIn = Inf_Rum * Inf_VFAIn
    return InfRum_VFAIn


def calculate_InfRum_AcetIn(Inf_Rum: float, Inf_AcetIn: float) -> float:
    InfRum_AcetIn = Inf_Rum * Inf_AcetIn
    return InfRum_AcetIn


def calculate_InfRum_PropIn(Inf_Rum: float, Inf_PropIn: float) -> float:
    InfRum_PropIn = Inf_Rum * Inf_PropIn
    return InfRum_PropIn


def calculate_InfRum_ButrIn(Inf_Rum: float, Inf_ButrIn: float) -> float:
    InfRum_ButrIn = Inf_Rum * Inf_ButrIn
    return InfRum_ButrIn


def calculate_InfRum_AshIn(Inf_Rum: float, Inf_AshIn: float) -> float:
    InfRum_AshIn = Inf_Rum * Inf_AshIn
    return InfRum_AshIn


def calculate_InfSI_DMIn(Inf_SI: float, Inf_DMIn: float) -> float:
    InfSI_DMIn = Inf_SI * Inf_DMIn
    return InfSI_DMIn


def calculate_InfSI_OMIn(Inf_SI: float, Inf_OMIn: float) -> float:
    InfSI_OMIn = Inf_SI * Inf_OMIn
    return InfSI_OMIn


def calculate_InfSI_CPIn(Inf_SI: float, Inf_CPIn: float) -> float:
    InfSI_CPIn = Inf_SI * Inf_CPIn
    return InfSI_CPIn


def calculate_InfSI_NPNCPIn(Inf_SI: float, Inf_NPNCPIn: float) -> float:
    InfSI_NPNCPIn = Inf_SI * Inf_NPNCPIn
    return InfSI_NPNCPIn


def calculate_InfSI_StIn(Inf_SI: float, Inf_StIn: float) -> float:
    InfSI_StIn = Inf_SI * Inf_StIn
    return InfSI_StIn


def calculate_InfSI_GlcIn(Inf_SI: float, Inf_GlcIn: float) -> float:
    InfSI_GlcIn = Inf_SI * Inf_GlcIn
    return InfSI_GlcIn


def calculate_InfSI_NDFIn(Inf_SI: float, Inf_NDFIn: float) -> float:
    InfSI_NDFIn = Inf_SI * Inf_NDFIn
    return InfSI_NDFIn


def calculate_InfSI_ADFIn(Inf_SI: float, Inf_ADFIn: float) -> float:
    InfSI_ADFIn = Inf_SI * Inf_ADFIn
    return InfSI_ADFIn


def calculate_InfSI_FAIn(Inf_SI: float, Inf_FAIn: float) -> float:
    InfSI_FAIn = Inf_SI * Inf_FAIn
    return InfSI_FAIn


def calculate_InfSI_VFAIn(Inf_SI: float, Inf_VFAIn: float) -> float:
    InfSI_VFAIn = Inf_SI * Inf_VFAIn
    return InfSI_VFAIn


def calculate_InfSI_AcetIn(Inf_SI: float, Inf_AcetIn: float) -> float:
    InfSI_AcetIn = Inf_SI * Inf_AcetIn
    return InfSI_AcetIn


def calculate_InfSI_PropIn(Inf_SI: float, Inf_PropIn: float) -> float:
    InfSI_PropIn = Inf_SI * Inf_PropIn
    return InfSI_PropIn


def calculate_InfSI_ButrIn(Inf_SI: float, Inf_ButrIn: float) -> float:
    InfSI_ButrIn = Inf_SI * Inf_ButrIn
    return InfSI_ButrIn


def calculate_InfSI_AshIn(Inf_SI: float, Inf_AshIn: float) -> float:
    InfSI_AshIn = Inf_SI * Inf_AshIn
    return InfSI_AshIn


def calculate_InfArt_DMIn(Inf_Art: float, Inf_DMIn: float) -> float:
    InfArt_DMIn = Inf_Art * Inf_DMIn
    return InfArt_DMIn


def calculate_InfArt_OMIn(Inf_Art: float, Inf_OMIn: float) -> float:
    InfArt_OMIn = Inf_Art * Inf_OMIn
    return InfArt_OMIn


def calculate_InfArt_CPIn(Inf_Art: float, Inf_CPIn: float) -> float:
    InfArt_CPIn = Inf_Art * Inf_CPIn
    return InfArt_CPIn


def calculate_InfArt_NPNCPIn(Inf_Art: float, Inf_NPNCPIn: float) -> float:
    InfArt_NPNCPIn = Inf_Art * Inf_NPNCPIn
    return InfArt_NPNCPIn


def calculate_InfArt_TPIn(Inf_Art: float, Inf_TPIn: float) -> float:
    InfArt_TPIn = Inf_Art * Inf_TPIn
    return InfArt_TPIn


def calculate_InfArt_StIn(Inf_Art: float, Inf_StIn: float) -> float:
    InfArt_StIn = Inf_Art * Inf_StIn
    return InfArt_StIn


def calculate_InfArt_GlcIn(Inf_Art: float, Inf_GlcIn: float) -> float:
    InfArt_GlcIn = Inf_Art * Inf_GlcIn
    return InfArt_GlcIn


def calculate_InfArt_NDFIn(Inf_Art: float, Inf_NDFIn: float) -> float:
    InfArt_NDFIn = Inf_Art * Inf_NDFIn
    return InfArt_NDFIn


def calculate_InfArt_ADFIn(Inf_Art: float, Inf_ADFIn: float) -> float:
    InfArt_ADFIn = Inf_Art * Inf_ADFIn
    return InfArt_ADFIn


def calculate_InfArt_FAIn(Inf_Art: float, Inf_FAIn: float) -> float:
    InfArt_FAIn = Inf_Art * Inf_FAIn
    return InfArt_FAIn


def calculate_InfArt_VFAIn(Inf_Art: float, Inf_VFAIn: float) -> float:
    InfArt_VFAIn = Inf_Art * Inf_VFAIn
    return InfArt_VFAIn


def calculate_InfArt_AcetIn(Inf_Art: float, Inf_AcetIn: float) -> float:
    InfArt_AcetIn = Inf_Art * Inf_AcetIn
    return InfArt_AcetIn


def calculate_InfArt_PropIn(Inf_Art: float, Inf_PropIn: float) -> float:
    InfArt_PropIn = Inf_Art * Inf_PropIn
    return InfArt_PropIn


def calculate_InfArt_ButrIn(Inf_Art: float, Inf_ButrIn: float) -> float:
    InfArt_ButrIn = Inf_Art * Inf_ButrIn
    return InfArt_ButrIn


def calculate_InfArt_AshIn(Inf_Art: float, Inf_AshIn: float) -> float:
    InfArt_AshIn = Inf_Art * Inf_AshIn
    return InfArt_AshIn


def calculate_Inf_ArgRUPIn(
    Inf_Rum: float, 
    Inf_Arg_g: float, 
    InfRum_RUP_CP: float
) -> float:
    Inf_ArgRUPIn = Inf_Rum * Inf_Arg_g * (InfRum_RUP_CP / 100)
    return Inf_ArgRUPIn


def calculate_Inf_HisRUPIn(
    Inf_Rum: float, 
    Inf_His_g: float, 
    InfRum_RUP_CP: float
) -> float:
    Inf_HisRUPIn = Inf_Rum * Inf_His_g * (InfRum_RUP_CP / 100)
    return Inf_HisRUPIn


def calculate_Inf_IleRUPIn(
    Inf_Rum: float, 
    Inf_Ile_g: float, 
    InfRum_RUP_CP: float
) -> float:
    Inf_IleRUPIn = Inf_Rum * Inf_Ile_g * (InfRum_RUP_CP / 100)
    return Inf_IleRUPIn


def calculate_Inf_LeuRUPIn(
    Inf_Rum: float, 
    Inf_Leu_g: float, 
    InfRum_RUP_CP: float
) -> float:
    Inf_LeuRUPIn = Inf_Rum * Inf_Leu_g * (InfRum_RUP_CP / 100)
    return Inf_LeuRUPIn


def calculate_Inf_LysRUPIn(
    Inf_Rum: float, 
    Inf_Lys_g: float, 
    InfRum_RUP_CP: float
) -> float:
    Inf_LysRUPIn = Inf_Rum * Inf_Lys_g * (InfRum_RUP_CP / 100)
    return Inf_LysRUPIn


def calculate_Inf_MetRUPIn(
    Inf_Rum: float, 
    Inf_Met_g: float, 
    InfRum_RUP_CP: float
) -> float:
    Inf_MetRUPIn = Inf_Rum * Inf_Met_g * (InfRum_RUP_CP / 100)
    return Inf_MetRUPIn


def calculate_Inf_PheRUPIn(
    Inf_Rum: float, 
    Inf_Phe_g: float, 
    InfRum_RUP_CP: float
) -> float:
    Inf_PheRUPIn = Inf_Rum * Inf_Phe_g * (InfRum_RUP_CP / 100)
    return Inf_PheRUPIn


def calculate_Inf_ThrRUPIn(
    Inf_Rum: float, 
    Inf_Thr_g: float, 
    InfRum_RUP_CP: float
) -> float:
    Inf_ThrRUPIn = Inf_Rum * Inf_Thr_g * (InfRum_RUP_CP / 100)
    return Inf_ThrRUPIn


def calculate_Inf_TrpRUPIn(
    Inf_Rum: float, 
    Inf_Trp_g: float, 
    InfRum_RUP_CP: float
) -> float:
    Inf_TrpRUPIn = Inf_Rum * Inf_Trp_g * (InfRum_RUP_CP / 100)
    return Inf_TrpRUPIn


def calculate_Inf_ValRUPIn(
    Inf_Rum: float, 
    Inf_Val_g: float, 
    InfRum_RUP_CP: float
) -> float:
    Inf_ValRUPIn = Inf_Rum * Inf_Val_g * (InfRum_RUP_CP / 100)
    return Inf_ValRUPIn


def calculate_Inf_IdArgIn(
    Inf_Arg_g: float, 
    Inf_SI: float, 
    Inf_ArgRUPIn: float, 
    Inf_dcRUP: float
) -> float:
    Inf_IdArgIn = ((Inf_Arg_g * Inf_SI) + Inf_ArgRUPIn) * (Inf_dcRUP / 100)
    return Inf_IdArgIn


def calculate_Inf_IdHisIn(
    Inf_His_g: float, 
    Inf_SI: float, 
    Inf_HisRUPIn: float, 
    Inf_dcRUP: float
) -> float:
    Inf_IdHisIn = ((Inf_His_g * Inf_SI) + Inf_HisRUPIn) * (Inf_dcRUP / 100)
    return Inf_IdHisIn


def calculate_Inf_IdIleIn(
    Inf_Ile_g: float, 
    Inf_SI: float, 
    Inf_IleRUPIn: float, 
    Inf_dcRUP: float
) -> float:
    Inf_IdIleIn = ((Inf_Ile_g * Inf_SI) + Inf_IleRUPIn) * (Inf_dcRUP / 100)
    return Inf_IdIleIn


def calculate_Inf_IdLeuIn(
    Inf_Leu_g: float, 
    Inf_SI: float, 
    Inf_LeuRUPIn: float, 
    Inf_dcRUP: float
) -> float:
    Inf_IdLeuIn = ((Inf_Leu_g * Inf_SI) + Inf_LeuRUPIn) * (Inf_dcRUP / 100)
    return Inf_IdLeuIn


def calculate_Inf_IdLysIn(
    Inf_Lys_g: float, 
    Inf_SI: float, 
    Inf_LysRUPIn: float, 
    Inf_dcRUP: float
) -> float:
    Inf_IdLysIn = ((Inf_Lys_g * Inf_SI) + Inf_LysRUPIn) * (Inf_dcRUP / 100)
    return Inf_IdLysIn


def calculate_Inf_IdMetIn(
    Inf_Met_g: float, 
    Inf_SI: float, 
    Inf_MetRUPIn: float, 
    Inf_dcRUP: float
) -> float:
    Inf_IdMetIn = ((Inf_Met_g * Inf_SI) + Inf_MetRUPIn) * (Inf_dcRUP / 100)
    return Inf_IdMetIn


def calculate_Inf_IdPheIn(
    Inf_Phe_g: float, 
    Inf_SI: float, 
    Inf_PheRUPIn: float, 
    Inf_dcRUP: float
) -> float:
    Inf_IdPheIn = ((Inf_Phe_g * Inf_SI) + Inf_PheRUPIn) * (Inf_dcRUP / 100)
    return Inf_IdPheIn


def calculate_Inf_IdThrIn(
    Inf_Thr_g: float, 
    Inf_SI: float, 
    Inf_ThrRUPIn: float, 
    Inf_dcRUP: float
) -> float:
    Inf_IdThrIn = ((Inf_Thr_g * Inf_SI) + Inf_ThrRUPIn) * (Inf_dcRUP / 100)
    return Inf_IdThrIn


def calculate_Inf_IdTrpIn(
    Inf_Trp_g: float, 
    Inf_SI: float, 
    Inf_TrpRUPIn: float, 
    Inf_dcRUP: float
) -> float:
    Inf_IdTrpIn = ((Inf_Trp_g * Inf_SI) + Inf_TrpRUPIn) * (Inf_dcRUP / 100)
    return Inf_IdTrpIn


def calculate_Inf_IdValIn(
    Inf_Val_g: float, 
    Inf_SI: float, 
    Inf_ValRUPIn: float, 
    Inf_dcRUP: float
) -> float:
    Inf_IdValIn = ((Inf_Val_g * Inf_SI) + Inf_ValRUPIn) * (Inf_dcRUP / 100)
    return Inf_IdValIn


def calculate_infusion_data(
    infusion_input: dict, 
    Dt_DMIn: float, 
    coeff_dict: dict
) -> dict:
    '''
    Infusion input is a dictionary
    '''
    # Calculate all infusion values "Inf_" and store in a dictionary
    infusion_data = infusion_input.copy()
    infusion_data["Inf_DMIn"] = calculate_Inf_DMIn(infusion_data["Inf_DM_g"])
    infusion_data["Inf_StIn"] = calculate_Inf_StIn(infusion_data["Inf_St_g"])
    infusion_data["Inf_NDFIn"] = calculate_Inf_NDFIn(infusion_data["Inf_NDF_g"])
    infusion_data["Inf_ADFIn"] = calculate_Inf_ADFIn(infusion_data["Inf_ADF_g"])
    infusion_data["Inf_GlcIn"] = calculate_Inf_GlcIn(infusion_data["Inf_Glc_g"])
    infusion_data["Inf_CPIn"] = calculate_Inf_CPIn(infusion_data["Inf_CP_g"])
    infusion_data["Inf_NPNCPIn"] = calculate_Inf_NPNCPIn(
        infusion_data["Inf_NPNCP_g"]
        )
    infusion_data["Inf_FAIn"] = calculate_Inf_FAIn(infusion_data["Inf_FA_g"])
    infusion_data["Inf_AshIn"] = calculate_Inf_AshIn(infusion_data["Inf_Ash_g"])
    infusion_data["Inf_VFAIn"] = calculate_Inf_VFAIn(infusion_data["Inf_VFA_g"])
    infusion_data["Inf_AcetIn"] = calculate_Inf_AcetIn(
        infusion_data["Inf_Acet_g"]
        )
    infusion_data["Inf_PropIn"] = calculate_Inf_PropIn(
        infusion_data["Inf_Prop_g"]
        )
    infusion_data["Inf_ButrIn"] = calculate_Inf_ButrIn(
        infusion_data["Inf_Butr_g"]
        )
    infusion_data["Inf_CPAIn"] = calculate_Inf_CPAIn(
        infusion_data["Inf_CP_g"], infusion_data["Inf_CPARum_CP"]
        )
    infusion_data["Inf_CPBIn"] = calculate_Inf_CPBIn(
        infusion_data["Inf_CP_g"], infusion_data["Inf_CPBRum_CP"]
        )
    infusion_data["Inf_CPCIn"] = calculate_Inf_CPCIn(
        infusion_data["Inf_CP_g"], infusion_data["Inf_CPCRum_CP"]
        )
    infusion_data['Inf_TPIn'] = calculate_Inf_TPIn(
        infusion_data['Inf_CPIn'], infusion_data['Inf_NPNCPIn']
        )
    infusion_data['Inf_OMIn'] = calculate_Inf_OMIn(
        infusion_data['Inf_DMIn'], infusion_data['Inf_AshIn']
        )
    infusion_data["Inf_DM"] = calculate_Inf_DM(
        Dt_DMIn, infusion_data["Inf_DMIn"]
        )
    infusion_data["Inf_OM"] = calculate_Inf_OM(
        Dt_DMIn, infusion_data["Inf_OMIn"]
        )
    infusion_data["Inf_St"] = calculate_Inf_St(
        Dt_DMIn, infusion_data["Inf_StIn"]
        )
    infusion_data["Inf_NDF"] = calculate_Inf_NDF(
        Dt_DMIn, infusion_data["Inf_NDFIn"]
        )
    infusion_data["Inf_ADF"] = calculate_Inf_ADF(
        Dt_DMIn, infusion_data["Inf_ADFIn"]
        )
    infusion_data["Inf_Glc"] = calculate_Inf_Glc(
        Dt_DMIn, infusion_data["Inf_GlcIn"]
        )
    infusion_data["Inf_CP"] = calculate_Inf_CP(
        Dt_DMIn, infusion_data["Inf_CPIn"]
        )
    infusion_data["Inf_FA"] = calculate_Inf_FA(
        Dt_DMIn, infusion_data["Inf_FAIn"]
        )
    infusion_data["Inf_VFA"] = calculate_Inf_VFA(
        Dt_DMIn, infusion_data["Inf_VFAIn"]
        )
    infusion_data["Inf_Acet"] = calculate_Inf_Acet(
        Dt_DMIn, infusion_data["Inf_AcetIn"]
        )
    infusion_data["Inf_Prop"] = calculate_Inf_Prop(
        Dt_DMIn, infusion_data["Inf_PropIn"]
        )
    infusion_data["Inf_Butr"] = calculate_Inf_Butr(
        Dt_DMIn, infusion_data["Inf_ButrIn"]
        )
    infusion_data['Inf_Rum'] = calculate_Inf_Rum(infusion_input['Inf_Location'])
    infusion_data['Inf_SI'] = calculate_Inf_SI(infusion_input['Inf_Location'])
    infusion_data['Inf_Art'] = calculate_Inf_Art(infusion_input['Inf_Location'])
    infusion_data["InfRum_DMIn"] = calculate_InfRum_DMIn(
        infusion_data["Inf_Rum"], infusion_data["Inf_DMIn"]
        )
    infusion_data["InfRum_OMIn"] = calculate_InfRum_OMIn(
        infusion_data["Inf_Rum"], infusion_data["Inf_OMIn"]
        )
    infusion_data["InfRum_CPIn"] = calculate_InfRum_CPIn(
        infusion_data["Inf_Rum"], infusion_data["Inf_CPIn"]
        )
    infusion_data["InfRum_NPNCPIn"] = calculate_InfRum_NPNCPIn(
        infusion_data["Inf_Rum"], infusion_data["Inf_NPNCPIn"]
        )
    infusion_data["InfRum_CPAIn"] = calculate_InfRum_CPAIn(
        infusion_data["Inf_Rum"], infusion_data["Inf_CPAIn"]
        )
    infusion_data["InfRum_CPBIn"] = calculate_InfRum_CPBIn(
        infusion_data["Inf_Rum"], infusion_data["Inf_CPBIn"]
        )
    infusion_data["InfRum_CPCIn"] = calculate_InfRum_CPCIn(
        infusion_data["Inf_Rum"], infusion_data["Inf_CPCIn"]
        )
    infusion_data["InfRum_StIn"] = calculate_InfRum_StIn(
        infusion_data["Inf_Rum"], infusion_data["Inf_StIn"]
        )
    infusion_data["InfRum_NDFIn"] = calculate_InfRum_NDFIn(
        infusion_data["Inf_Rum"], infusion_data["Inf_NDFIn"]
        )
    infusion_data["InfRum_ADFIn"] = calculate_InfRum_ADFIn(
        infusion_data["Inf_Rum"], infusion_data["Inf_ADFIn"]
        )
    infusion_data["InfRum_FAIn"] = calculate_InfRum_FAIn(
        infusion_data["Inf_Rum"], infusion_data["Inf_FAIn"]
        )
    infusion_data["InfRum_GlcIn"] = calculate_InfRum_GlcIn(
        infusion_data["Inf_Rum"], infusion_data["Inf_GlcIn"]
        )
    infusion_data["InfRum_VFAIn"] = calculate_InfRum_VFAIn(
        infusion_data["Inf_Rum"], infusion_data["Inf_VFAIn"]
        )
    infusion_data["InfRum_AcetIn"] = calculate_InfRum_AcetIn(
        infusion_data["Inf_Rum"], infusion_data["Inf_AcetIn"]
        )
    infusion_data["InfRum_PropIn"] = calculate_InfRum_PropIn(
        infusion_data["Inf_Rum"], infusion_data["Inf_PropIn"]
        )
    infusion_data["InfRum_ButrIn"] = calculate_InfRum_ButrIn(
        infusion_data["Inf_Rum"], infusion_data["Inf_ButrIn"]
        )
    infusion_data["InfRum_AshIn"] = calculate_InfRum_AshIn(
        infusion_data["Inf_Rum"], infusion_data["Inf_AshIn"]
        )
    infusion_data['InfRum_TPIn'] = calculate_InfRum_TPIn(
        infusion_data['InfRum_CPIn'], infusion_data['InfRum_NPNCPIn']
        )
    infusion_data["InfSI_DMIn"] = calculate_InfSI_DMIn(
        infusion_data["Inf_SI"], infusion_data["Inf_DMIn"]
        )
    infusion_data["InfSI_OMIn"] = calculate_InfSI_OMIn(
        infusion_data["Inf_SI"], infusion_data["Inf_OMIn"]
        )
    infusion_data["InfSI_CPIn"] = calculate_InfSI_CPIn(
        infusion_data["Inf_SI"], infusion_data["Inf_CPIn"]
        )
    infusion_data["InfSI_NPNCPIn"] = calculate_InfSI_NPNCPIn(
        infusion_data["Inf_SI"], infusion_data["Inf_NPNCPIn"]
        )
    infusion_data["InfSI_StIn"] = calculate_InfSI_StIn(
        infusion_data["Inf_SI"], infusion_data["Inf_StIn"]
        )
    infusion_data["InfSI_GlcIn"] = calculate_InfSI_GlcIn(
        infusion_data["Inf_SI"], infusion_data["Inf_GlcIn"]
        )
    infusion_data["InfSI_NDFIn"] = calculate_InfSI_NDFIn(
        infusion_data["Inf_SI"], infusion_data["Inf_NDFIn"]
        )
    infusion_data["InfSI_ADFIn"] = calculate_InfSI_ADFIn(
        infusion_data["Inf_SI"], infusion_data["Inf_ADFIn"]
        )
    infusion_data["InfSI_FAIn"] = calculate_InfSI_FAIn(
        infusion_data["Inf_SI"], infusion_data["Inf_FAIn"]
        )
    infusion_data["InfSI_VFAIn"] = calculate_InfSI_VFAIn(
        infusion_data["Inf_SI"], infusion_data["Inf_VFAIn"]
        )
    infusion_data["InfSI_AcetIn"] = calculate_InfSI_AcetIn(
        infusion_data["Inf_SI"], infusion_data["Inf_AcetIn"]
        )
    infusion_data["InfSI_PropIn"] = calculate_InfSI_PropIn(
        infusion_data["Inf_SI"], infusion_data["Inf_PropIn"]
        )
    infusion_data["InfSI_ButrIn"] = calculate_InfSI_ButrIn(
        infusion_data["Inf_SI"], infusion_data["Inf_ButrIn"]
        )
    infusion_data["InfSI_AshIn"] = calculate_InfSI_AshIn(
        infusion_data["Inf_SI"], infusion_data["Inf_AshIn"]
        )
    infusion_data['InfSI_TPIn'] = calculate_InfSI_TPIn(
        infusion_data['InfSI_CPIn'], infusion_data['InfSI_NPNCPIn']
        )
    infusion_data["InfArt_DMIn"] = calculate_InfArt_DMIn(
        infusion_data["Inf_Art"], infusion_data["Inf_DMIn"]
        )
    infusion_data["InfArt_OMIn"] = calculate_InfArt_OMIn(
        infusion_data["Inf_Art"], infusion_data["Inf_OMIn"]
        )
    infusion_data["InfArt_CPIn"] = calculate_InfArt_CPIn(
        infusion_data["Inf_Art"], infusion_data["Inf_CPIn"]
        )
    infusion_data["InfArt_NPNCPIn"] = calculate_InfArt_NPNCPIn(
        infusion_data["Inf_Art"], infusion_data["Inf_NPNCPIn"]
        )
    infusion_data["InfArt_TPIn"] = calculate_InfArt_TPIn(
        infusion_data["Inf_Art"], infusion_data["Inf_TPIn"]
        )
    infusion_data["InfArt_StIn"] = calculate_InfArt_StIn(
        infusion_data["Inf_Art"], infusion_data["Inf_StIn"]
        )
    infusion_data["InfArt_GlcIn"] = calculate_InfArt_GlcIn(
        infusion_data["Inf_Art"], infusion_data["Inf_GlcIn"]
        )
    infusion_data["InfArt_NDFIn"] = calculate_InfArt_NDFIn(
        infusion_data["Inf_Art"], infusion_data["Inf_NDFIn"]
        )
    infusion_data["InfArt_ADFIn"] = calculate_InfArt_ADFIn(
        infusion_data["Inf_Art"], infusion_data["Inf_ADFIn"]
        )
    infusion_data["InfArt_FAIn"] = calculate_InfArt_FAIn(
        infusion_data["Inf_Art"], infusion_data["Inf_FAIn"]
        )
    infusion_data["InfArt_VFAIn"] = calculate_InfArt_VFAIn(
        infusion_data["Inf_Art"], infusion_data["Inf_VFAIn"]
        )
    infusion_data["InfArt_AcetIn"] = calculate_InfArt_AcetIn(
        infusion_data["Inf_Art"], infusion_data["Inf_AcetIn"]
        )
    infusion_data["InfArt_PropIn"] = calculate_InfArt_PropIn(
        infusion_data["Inf_Art"], infusion_data["Inf_PropIn"]
        )
    infusion_data["InfArt_ButrIn"] = calculate_InfArt_ButrIn(
        infusion_data["Inf_Art"], infusion_data["Inf_ButrIn"]
        )
    infusion_data["InfArt_AshIn"] = calculate_InfArt_AshIn(
        infusion_data["Inf_Art"], infusion_data["Inf_AshIn"]
        )

    # RUP does not include CP infused into the SI
    # In general, CPB for infused proteins, which are generally soluble, has 
    # been set to 0. Abo/Duod infusions only considered at absorption.
    infusion_data['InfRum_RUPIn'] = calculate_InfRum_RUPIn(
        infusion_data['InfRum_CPAIn'], infusion_data['InfRum_CPBIn'],
        infusion_data['InfRum_CPCIn'], infusion_data['InfRum_NPNCPIn'],
        infusion_input['Inf_KdCPB'], coeff_dict)
    infusion_data['InfRum_RUP_CP'] = calculate_InfRum_RUP_CP(
        infusion_data['InfRum_CPIn'], infusion_data['InfRum_RUPIn']
        )
    infusion_data['InfRum_idRUPIn'] = calculate_InfRum_idRUPIn(
        infusion_data['InfRum_RUPIn'], infusion_input['Inf_dcRUP']
        )
    infusion_data['InfSI_idTPIn'] = calculate_InfSI_idTPIn(
        infusion_data['InfSI_TPIn'], infusion_input['Inf_dcRUP']
        )
    infusion_data['InfSI_idCPIn'] = calculate_InfSI_idCPIn(
        infusion_data['InfSI_idTPIn'], infusion_data['InfSI_NPNCPIn'],
        coeff_dict)
    infusion_data['Inf_idCPIn'] = calculate_Inf_idCPIn(
        infusion_data['InfRum_idRUPIn'], infusion_data['InfSI_idCPIn']
        )
    infusion_data['InfRum_RDPIn'] = calculate_InfRum_RDPIn(
        infusion_data['InfRum_CPIn'], infusion_data['InfRum_RUPIn']
        )
    # Infused individual FA should be calculated here if they are to be 
    # considered. Requires a change to the infusion table. MDH
    infusion_data['Inf_DigFAIn'] = calculate_Inf_DigFAIn(
        infusion_data['Inf_FAIn'], coeff_dict)
    infusion_data['Inf_DEAcetIn'] = calculate_Inf_DEAcetIn(
        infusion_data['Inf_AcetIn'], coeff_dict)
    infusion_data['Inf_DEPropIn'] = calculate_Inf_DEPropIn(
        infusion_data['Inf_PropIn'], coeff_dict)
    infusion_data['Inf_DEButrIn'] = calculate_Inf_DEButrIn(
        infusion_data['Inf_ButrIn'], coeff_dict)
    infusion_data["Inf_ArgRUPIn"] = calculate_Inf_ArgRUPIn(
        infusion_data["Inf_Rum"], infusion_data["Inf_Arg_g"], 
        infusion_data["InfRum_RUP_CP"]
        )
    infusion_data["Inf_HisRUPIn"] = calculate_Inf_HisRUPIn(
        infusion_data["Inf_Rum"], infusion_data["Inf_His_g"], 
        infusion_data["InfRum_RUP_CP"]
        )
    infusion_data["Inf_IleRUPIn"] = calculate_Inf_IleRUPIn(
        infusion_data["Inf_Rum"], infusion_data["Inf_Ile_g"], 
        infusion_data["InfRum_RUP_CP"]
        )
    infusion_data["Inf_LeuRUPIn"] = calculate_Inf_LeuRUPIn(
        infusion_data["Inf_Rum"], infusion_data["Inf_Leu_g"], 
        infusion_data["InfRum_RUP_CP"]
        )
    infusion_data["Inf_LysRUPIn"] = calculate_Inf_LysRUPIn(
        infusion_data["Inf_Rum"], infusion_data["Inf_Lys_g"], 
        infusion_data["InfRum_RUP_CP"]
        )
    infusion_data["Inf_MetRUPIn"] = calculate_Inf_MetRUPIn(
        infusion_data["Inf_Rum"], infusion_data["Inf_Met_g"], 
        infusion_data["InfRum_RUP_CP"]
        )
    infusion_data["Inf_PheRUPIn"] = calculate_Inf_PheRUPIn(
        infusion_data["Inf_Rum"], infusion_data["Inf_Phe_g"], 
        infusion_data["InfRum_RUP_CP"]
        )
    infusion_data["Inf_ThrRUPIn"] = calculate_Inf_ThrRUPIn(
        infusion_data["Inf_Rum"], infusion_data["Inf_Thr_g"], 
        infusion_data["InfRum_RUP_CP"]
        )
    infusion_data["Inf_TrpRUPIn"] = calculate_Inf_TrpRUPIn(
        infusion_data["Inf_Rum"], infusion_data["Inf_Trp_g"], 
        infusion_data["InfRum_RUP_CP"]
        )
    infusion_data["Inf_ValRUPIn"] = calculate_Inf_ValRUPIn(
        infusion_data["Inf_Rum"], infusion_data["Inf_Val_g"], 
        infusion_data["InfRum_RUP_CP"]
        )
    infusion_data["Inf_IdArgIn"] = calculate_Inf_IdArgIn(
        infusion_data["Inf_Arg_g"], infusion_data["Inf_SI"], 
        infusion_data["Inf_ArgRUPIn"], infusion_data["Inf_dcRUP"]
        )
    infusion_data["Inf_IdHisIn"] = calculate_Inf_IdHisIn(
        infusion_data["Inf_His_g"], infusion_data["Inf_SI"], 
        infusion_data["Inf_HisRUPIn"], infusion_data["Inf_dcRUP"]
        )
    infusion_data["Inf_IdIleIn"] = calculate_Inf_IdIleIn(
        infusion_data["Inf_Ile_g"], infusion_data["Inf_SI"], 
        infusion_data["Inf_IleRUPIn"], infusion_data["Inf_dcRUP"]
        )
    infusion_data["Inf_IdLeuIn"] = calculate_Inf_IdLeuIn(
        infusion_data["Inf_Leu_g"], infusion_data["Inf_SI"], 
        infusion_data["Inf_LeuRUPIn"], infusion_data["Inf_dcRUP"]
        )
    infusion_data["Inf_IdLysIn"] = calculate_Inf_IdLysIn(
        infusion_data["Inf_Lys_g"], infusion_data["Inf_SI"], 
        infusion_data["Inf_LysRUPIn"], infusion_data["Inf_dcRUP"]
        )
    infusion_data["Inf_IdMetIn"] = calculate_Inf_IdMetIn(
        infusion_data["Inf_Met_g"], infusion_data["Inf_SI"], 
        infusion_data["Inf_MetRUPIn"], infusion_data["Inf_dcRUP"]
        )
    infusion_data["Inf_IdPheIn"] = calculate_Inf_IdPheIn(
        infusion_data["Inf_Phe_g"], infusion_data["Inf_SI"], 
        infusion_data["Inf_PheRUPIn"], infusion_data["Inf_dcRUP"]
        )
    infusion_data["Inf_IdThrIn"] = calculate_Inf_IdThrIn(
        infusion_data["Inf_Thr_g"], infusion_data["Inf_SI"], 
        infusion_data["Inf_ThrRUPIn"], infusion_data["Inf_dcRUP"]
        )
    infusion_data["Inf_IdTrpIn"] = calculate_Inf_IdTrpIn(
        infusion_data["Inf_Trp_g"], infusion_data["Inf_SI"], 
        infusion_data["Inf_TrpRUPIn"], infusion_data["Inf_dcRUP"]
        )
    infusion_data["Inf_IdValIn"] = calculate_Inf_IdValIn(
        infusion_data["Inf_Val_g"], infusion_data["Inf_SI"], 
        infusion_data["Inf_ValRUPIn"], infusion_data["Inf_dcRUP"]
        )
    infusion_data['Inf_ttdcSt'] = infusion_input['Inf_ttdcSt']
    return infusion_data
