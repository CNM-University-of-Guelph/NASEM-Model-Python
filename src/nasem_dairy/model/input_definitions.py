"""Definitions for input schemas and data structures.

This module defines various TypedDict classes and schemas that represent the 
expected structure and types of input data for the NASEM model. These 
definitions are used throughout the model for input validation and type 
checking.

Classes:
    AnimalInput: Defines the schema for animal input data.
    EquationSelection: Defines the schema for equation selection input data.
    InfusionInput: Defines the schema for infusion input data.
    CoeffDict: Defines the schema for coefficient dictionaries.
    MPNPEfficiencyDict: Defines the schema for MP/NP efficiency input data.
    mPrtCoeffDict: Defines the schema for mPrt coefficient input data.

Variables:
    f_Imb: A pandas Series representing imbalance factors for amino acids.
    UserDietSchema: A dictionary defining the expected structure of the user diet.
    FeedLibrarySchema: A dictionary defining the expected structure of the feed library.
"""

from typing import TypedDict, Optional, Literal

import pandas as pd

class AnimalInput(TypedDict):
    An_Parity_rl: float
    Trg_MilkProd: float
    An_BW: float
    An_BCS: float
    An_LactDay: int
    Trg_MilkFatp: float
    Trg_MilkTPp: float
    Trg_MilkLacp: float
    Trg_Dt_DMIn: float
    An_BW_mature: float
    Trg_FrmGain: float
    An_GestDay: int
    An_GestLength: int
    Trg_RsrvGain: float
    Fet_BWbrth: float
    An_AgeDay: float
    An_305RHA_MlkTP: float
    An_StatePhys: Literal["Calf", "Heifer", "Dry Cow", "Lactating Cow", "Other"]
    An_Breed: Literal["Holstein", "Jersey", "Other"]
    An_AgeDryFdStart: int
    Env_TempCurr: float
    Env_DistParlor: float
    Env_TripsParlor: int
    Env_Topo: float
    An_AgeConcept1st: int


class EquationSelection(TypedDict):
    Use_DNDF_IV: Literal[0, 1, 2]
    DMIn_eqn: Literal[
        0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10 , 11, 12, 13, 14, 15, 16, 17, 18
        ]
    mProd_eqn: Literal[0, 1, 2, 3, 4]
    MiN_eqn: Literal[1, 2, 3]
    NonMilkCP_ClfLiq: Literal[0, 1]
    Monensin_eqn: Literal[0, 1]
    mPrt_eqn: Literal[0, 1, 2, 3]
    mFat_eqn: Literal[0, 1]
    RumDevDisc_Clf: Literal[0, 1]


class InfusionInput(TypedDict):
    Inf_Acet_g: float
    Inf_ADF_g: float
    Inf_Arg_g: float
    Inf_Ash_g: float
    Inf_Butr_g: float
    Inf_CP_g: float
    Inf_CPARum_CP: float
    Inf_CPBRum_CP: float
    Inf_CPCRum_CP: float
    Inf_dcFA: float
    Inf_dcRUP: float
    Inf_DM_g: float
    Inf_EE_g: float
    Inf_FA_g: float
    Inf_Glc_g: float
    Inf_His_g: float
    Inf_Ile_g: float
    Inf_KdCPB: float
    Inf_Leu_g: float
    Inf_Lys_g: float
    Inf_Met_g: float
    Inf_NDF_g: float
    Inf_NPNCP_g: float
    Inf_Phe_g: float
    Inf_Prop_g: float
    Inf_St_g: float
    Inf_Thr_g: float
    Inf_Trp_g: float
    Inf_ttdcSt: float
    Inf_Val_g: float
    Inf_VFA_g: float
    Inf_Location: str


UserDietSchema = {
    "Feedstuff": str,
    "kg_user": float,
}


class CoeffDict(TypedDict):
    An_Fe_m: float
    An_GutFill_BWmature: float
    An_NEmUse_Env: float
    AshGain_RsrvGain: float
    Body_Arg_TP: float
    Body_His_TP: float
    Body_Ile_TP: float
    Body_Leu_TP: float
    Body_Lys_TP: float
    Body_Met_TP: float
    Body_NP_CP: float
    Body_Phe_TP: float
    Body_Thr_TP: float
    Body_Trp_TP: float
    Body_Val_TP: float
    CH4vol_kg: float
    CPGain_RsrvGain: float
    CP_GrUtWt: float
    dcNPNCP: float
    Dt_dcCP_ClfLiq: float
    En_Acet: float
    En_Butr: float
    En_CH4: float
    En_CP: float
    En_FA: float
    En_NDF: float
    En_NDFnf: float
    En_NFC: float
    En_NPNCP: float
    En_Prop: float
    En_St: float
    En_WSC: float
    En_rOM: float
    EndArgProf: float
    EndHisProf: float
    EndIleProf: float
    EndLeuProf: float
    EndLysProf: float
    EndMetProf: float
    EndPheProf: float
    EndThrProf: float
    EndTrpProf: float
    EndValProf: float
    FatGain_RsrvGain: float
    Fe_ArgMetab_TP: float
    Fe_HisMetab_TP: float
    Fe_IleMetab_TP: float
    Fe_LeuMetab_TP: float
    Fe_LysMetab_TP: float
    Fe_MetMetab_TP: float
    Fe_PheMetab_TP: float
    Fe_ThrMetab_TP: float
    Fe_TrpMetab_TP: float
    Fe_ValMetab_TP: float
    Fe_rOMend_DMI: float
    Fet_BWgain: float
    Fet_Ksyn: float
    Fet_KsynDecay: float
    Fet_Wt: float
    Fd_dcrOM: float
    fCPAdu: float
    fMiTP_MiCP: float
    fN_3MH: float
    fIlEndTP_CP: float
    Gest_NPother_g: float
    GrUterWt_FetBWbrth: float
    GrUter_BWgain_coeff: float
    GrUter_Ksyn: float
    GrUter_KsynDecay: float
    HydrArg: float
    HydrHis: float
    HydrIle: float
    HydrLeu: float
    HydrLys: float
    HydrMet: float
    HydrPhe: float
    HydrThr: float
    HydrTrp: float
    HydrVal: float
    IntRUP: float
    Int_MiN_VT: float
    K_305RHA_MlkTP: float
    Ka_LateGest_DMIn: float
    Kc_LateGest_DMIn: float
    Kf_ME_RE_ClfLiq: float
    Kg_MP_NP_Trg_coeff: float
    Kl_ME_NE: float
    Kl_MP_NP_Trg: float
    KmMiNRDNDF: float
    KmMiNRDSt: float
    Km_MP_NP_Trg: float
    KpConc: float
    KpFor: float
    KrdNDF_MiN_VT: float
    KrdNDFxForNDF_MiN_VT: float
    KrdSt_MiN_VT: float
    KrdStxrOM_MiN_VT: float
    KRDP_MiN_VT: float
    KrOM_MiN_VT: float
    KrOM2_MiN_VT: float
    KForNDF_MiN_VT: float
    Kx_MP_NP_Trg: float
    Ky_MP_NP_Trg: float
    Ky_NP_MP_Trg: float
    LCT: float
    MiTPArgProf: float
    MiTPHisProf: float
    MiTPIleProf: float
    MiTPLeuProf: float
    MiTPLysProf: float
    MiTPMetProf: float
    MiTPPheProf: float
    MiTPThrProf: float
    MiTPTrpProf: float
    MiTPValProf: float
    Mlk_Arg_TP: float
    Mlk_His_TP: float
    Mlk_Ile_TP: float
    Mlk_Leu_TP: float
    Mlk_Lys_TP: float
    Mlk_Met_TP: float
    Mlk_Phe_TP: float
    Mlk_Thr_TP: float
    Mlk_Trp_TP: float
    Mlk_Val_TP: float
    MWArg: float
    MWHis: float
    MWIle: float
    MWLeu: float
    MWLys: float
    MWMet: float
    MWPhe: float
    MWThr: float
    MWTrp: float
    MWVal: float
    NE_GrUtWt: float
    RecArg: float
    RecHis: float
    RecIle: float
    RecLeu: float
    RecLys: float
    RecMet: float
    RecPhe: float
    RecThr: float
    RecTrp: float
    RecVal: float
    refCPIn: float
    Scrf_Arg_TP: float
    Scrf_His_TP: float
    Scrf_Ile_TP: float
    Scrf_Leu_TP: float
    Scrf_Lys_TP: float
    Scrf_Met_TP: float
    Scrf_Phe_TP: float
    Scrf_Thr_TP: float
    Scrf_Trp_TP: float
    Scrf_Val_TP: float
    SI_dcMiCP: float
    TT_dcFA_Base: float
    TT_dcFA_ClfDryFd: float
    TT_dcFA_ClfLiqFd: float
    TT_dcFat_Base: float
    UCT: float
    Ur_ArgEnd_TP: float
    Ur_HisEnd_TP: float
    Ur_IleEnd_TP: float
    Ur_LeuEnd_TP: float
    Ur_LysEnd_TP: float
    Ur_MetEnd_TP: float
    Ur_PheEnd_TP: float
    Ur_ThrEnd_TP: float
    Ur_TrpEnd_TP: float
    Ur_ValEnd_TP: float
    UterWt_FetBWbrth: float
    Uter_BWgain_coeff: float
    Uter_Kdeg: float
    Uter_Ksyn: float
    Uter_KsynDecay: float
    Uter_Wt_coeff: float
    VmMiNInt: float
    VmMiNRDPSlp: float


class InfusionDict(TypedDict):
    Inf_Acet_g: float
    Inf_ADF_g: float
    Inf_Arg_g: float
    Inf_Ash_g: float
    Inf_Butr_g: float
    Inf_CP_g: float
    Inf_CPARum_CP: float
    Inf_CPBRum_CP: float
    Inf_CPCRum_CP: float
    Inf_dcFA: float
    Inf_dcRUP: float
    Inf_DM_g: float
    Inf_EE_g: float
    Inf_FA_g: float
    Inf_Glc_g: float
    Inf_His_g: float
    Inf_Ile_g: float
    Inf_KdCPB: float
    Inf_Leu_g: float
    Inf_Lys_g: float
    Inf_Met_g: float
    Inf_NDF_g: float
    Inf_NPNCP_g: float
    Inf_Phe_g: float
    Inf_Prop_g: float
    Inf_St_g: float
    Inf_Thr_g: float
    Inf_Trp_g: float
    Inf_ttdcSt: float
    Inf_Val_g: float
    Inf_VFA_g: float
    Inf_Location: Literal["Rumen", "Abomasum", "Duodenum", "Jugular", 
                          "Arterial", "Iliac Artery" , "Blood"]


class MPNPEfficiencyDict(TypedDict):
    Trg_AbsHis_NPHis: float
    Trg_AbsIle_NPIle: float
    Trg_AbsLeu_NPLeu: float
    Trg_AbsLys_NPLys: float
    Trg_AbsMet_NPMet: float
    Trg_AbsPhe_NPPhe: float
    Trg_AbsThr_NPThr: float
    Trg_AbsTrp_NPTrp: float
    Trg_AbsVal_NPVal: float
    Trg_MP_NP: float


class mPrtCoeffDict(TypedDict):
    mPrt_Int: float
    mPrt_k_BW: float
    mPrt_k_DEInp: float
    mPrt_k_DigNDF: float
    mPrt_k_DEIn_StFA: float
    mPrt_k_DEIn_NDF: float
    mPrt_k_Arg: float
    mPrt_k_His: float
    mPrt_k_Ile: float
    mPrt_k_Leu: float
    mPrt_k_Lys: float
    mPrt_k_Met: float
    mPrt_k_Phe: float
    mPrt_k_Thr: float
    mPrt_k_Trp: float
    mPrt_k_Val: float
    mPrt_k_NEAA: float
    mPrt_k_OthAA: float
    mPrt_k_EAA2_coeff: float


f_Imb = pd.Series(
    [1.0] * 10, 
    index=["Arg", "His", "Ile", "Leu", "Lys", "Met", "Phe", "Thr", "Trp", "Val"]
)


FeedLibrarySchema = {
    "Fd_Libr": str,
    "UID": str,
    "Fd_Index": int,
    "Fd_Name": str,
    "Fd_Category": str,
    "Fd_Type": str,
    "Fd_DM": float,
    "Fd_Conc": float,
    "Fd_Locked": int,
    "Fd_DE_Base": float,
    "Fd_ADF": float,
    "Fd_NDF": float,
    "Fd_DNDF48_input": float,
    "Fd_DNDF48_NDF": float,
    "Fd_Lg": float,
    "Fd_CP": float,
    "Fd_St": float,
    "Fd_dcSt": float,
    "Fd_WSC": float,
    "Fd_CPARU": float,
    "Fd_CPBRU": float,
    "Fd_CPCRU": float,
    "Fd_dcRUP": float,
    "Fd_CPs_CP": float,
    "Fd_KdRUP": float,
    "Fd_RUP_base": float,
    "Fd_NPN_CP": float,
    "Fd_NDFIP": float,
    "Fd_ADFIP": float,
    "Fd_Arg_CP": float,
    "Fd_His_CP": float,
    "Fd_Ile_CP": float,
    "Fd_Leu_CP": float,
    "Fd_Lys_CP": float,
    "Fd_Met_CP": float,
    "Fd_Phe_CP": float,
    "Fd_Thr_CP": float,
    "Fd_Trp_CP": float,
    "Fd_Val_CP": float,
    "Fd_CFat": float,
    "Fd_FA": float,
    "Fd_dcFA": float,
    "Fd_Ash": float,
    "Fd_C120_FA": float,
    "Fd_C140_FA": float,
    "Fd_C160_FA": float,
    "Fd_C161_FA": float,
    "Fd_C180_FA": float,
    "Fd_C181t_FA": float,
    "Fd_C181c_FA": float,
    "Fd_C182_FA": float,
    "Fd_C183_FA": float,
    "Fd_OtherFA_FA": float,
    "Fd_Ca": float,
    "Fd_P": float,
    "Fd_Pinorg_P": float,
    "Fd_Porg_P": float,
    "Fd_Na": float,
    "Fd_Cl": float,
    "Fd_K": float,
    "Fd_Mg": float,
    "Fd_S": float,
    "Fd_Cr": float,
    "Fd_Co": float,
    "Fd_Cu": float,
    "Fd_Fe": float,
    "Fd_I": float,
    "Fd_Mn": float,
    "Fd_Mo": float,
    "Fd_Se": float,
    "Fd_Zn": float,
    "Fd_B_Carotene": float,
    "Fd_Biotin": float,
    "Fd_Choline": float,
    "Fd_Niacin": float,
    "Fd_VitA": float,
    "Fd_VitD": float,
    "Fd_VitE": float,
    "Fd_acCa_input": float,
    "Fd_acPtot_input": float,
    "Fd_acNa_input": float,
    "Fd_acCl_input": float,
    "Fd_acK_input": float,
    "Fd_acCu_input": float,
    "Fd_acFe_input": float,
    "Fd_acMg_input": float,
    "Fd_acMn_input": float,
    "Fd_acZn_input": float,
}
