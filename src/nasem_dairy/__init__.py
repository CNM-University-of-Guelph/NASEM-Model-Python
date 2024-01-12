# read version from installed package
from importlib.metadata import version
__version__ = version("nasem_dairy")


from nasem_dairy.ration_balancer.ration_balancer_functions import fl_get_rows, get_nutrient_intakes, fl_get_feed_rows, read_input, check_coeffs_in_coeff_dict, read_csv_input, read_infusion_input
from nasem_dairy.ration_balancer.execute_model import NASEM_model
from nasem_dairy.NASEM_equations.misc_equations import calculate_GrUter_BWgain
from nasem_dairy.NASEM_equations.Animal_supply_equations import calculate_An_DEIn, calculate_An_NE
from nasem_dairy.NASEM_equations.Milk_equations import calculate_Mlk_Fat_g, calculate_Mlk_NP_g, calculate_Mlk_Prod_comp, calculate_Mlk_Prod_MPalow, calculate_Mlk_Prod_NEalow, check_animal_lactation_day, calculate_An_MPIn_g
from nasem_dairy.NASEM_equations.ME_equations import calculate_ME_requirement, calculate_An_MEgain, calculate_An_MEmUse, calculate_Gest_MEuse, calculate_Trg_Mlk_MEout
from nasem_dairy.NASEM_equations.MP_equations import calculate_MP_requirement, calculate_An_MPm_g_Trg, calculate_Body_MPuse_g_Trg, calculate_Gest_MPuse_g_Trg, calculate_Mlk_MPuse_g_Trg
from nasem_dairy.ration_balancer.coeff_dict import coeff_dict
from nasem_dairy.NASEM_equations.micronutrient_equations import mineral_requirements
from nasem_dairy.NASEM_equations.temporary_functions import temp_MlkNP_Milk, temp_calc_An_DigTPaIn, temp_calc_An_GasEOut, calculate_Mlk_Prod, calculate_MlkNE_Milk, calculate_Mlk_MEout

from nasem_dairy.NASEM_equations.dev_DMI_equations import (
    calculate_Kb_LateGest_DMIn,
    calculate_An_PrePartWklim,
    calculate_Dt_DMIn_Heif_LateGestInd,
    calculate_Dt_DMIn_Heif_LateGestPen,
    calculate_Dt_NDFdev_DMI,
    calculate_Dt_DMIn_Heif_NRCa,
    calculate_Dt_DMIn_Heif_NRCad,
    calculate_Dt_DMIn_Heif_H1,
    calculate_Dt_DMIn_Heif_H2,
    calculate_Dt_DMIn_Heif_HJ1,
    calculate_Dt_DMIn_Heif_HJ2,
    calculate_Dt_DMIn_Lact1,
    calculate_Dt_DMIn_BW_LateGest_i,
    calculate_Dt_DMIn_BW_LateGest_p,
    calculate_Dt_DMIn_DryCow1_FarOff,
    calculate_Dt_DMIn_DryCow1_Close,
    calculate_Dt_DMIn_DryCow2
)
from nasem_dairy.NASEM_equations.dev_milk_equations import calculate_Trg_NEmilk_Milk
from nasem_dairy.NASEM_equations.dev_nutrient_intakes import (
    calculate_TT_dcFdNDF_Lg,
    calculate_Fd_DNDF48,
    calculate_TT_dcFdNDF_48h,
    calculate_TT_dcFdNDF_Base,
    calculate_Fd_GE,
    calculate_Fd_DMIn,
    calculate_Fd_AFIn,
    calculate_Fd_For,
    calculate_Fd_ForWet,
    calculate_Fd_ForDry,
    calculate_Fd_Past,
    calculate_Fd_LiqClf,
    calculate_Fd_ForNDF,
    calculate_Fd_NDFnf,
    calculate_Fd_NPNCP,
    calculate_Fd_NPN,
    calculate_Fd_NPNDM,
    calculate_Fd_TP,
    calculate_Fd_fHydr_FA,
    calculate_Fd_FAhydr,
    calculate_Fd_NFC,
    calculate_Fd_rOM,
    calculate_Fd_DigNDFIn_Base,
    calculate_Fd_NPNCPIn,
    calculate_Fd_NPNIn,
    calculate_Fd_NPNDMIn,
    calculate_Fd_CPAIn,
    calculate_Fd_CPBIn,
    calculate_Fd_CPBIn_For,
    calculate_Fd_CPBIn_Conc,
    calculate_Fd_CPCIn,
    calculate_Fd_CPIn_ClfLiq,
    calculate_Fd_CPIn_ClfDry,
    calculate_Fd_rdcRUPB,
    calculate_Fd_RUPBIn,
    calculate_Fd_RUPIn,
    calculate_Fd_RUP_CP,
    calculate_Fd_RUP,
    calculate_Fd_RDP,
    calculate_Fd_OMIn,
    calculate_Fd_DE_base_1,
    calculate_Fd_DE_base_2,
    calculate_Fd_DE_base,
    calculate_Fd_DEIn_base,
    calculate_Fd_DEIn_base_ClfLiq,
    calculate_Fd_DEIn_base_ClfDry,
    calculate_Fd_DMIn_ClfLiq,
    calculate_Fd_DE_ClfLiq,
    calculate_Fd_ME_ClfLiq,
    calculate_Fd_DMIn_ClfFor,
    calculate_Fd_PinorgIn,
    calculate_Fd_PorgIn,
    calculate_Fd_MgIn_min,
    calculate_Fd_acCa,
    calculate_Fd_acPtot,
    calculate_Fd_acMg,
    calculate_Fd_acNa,
    calculate_Fd_acK,
    calculate_Fd_acCl,
    calculate_Fd_absCaIn,
    calculate_Fd_absPIn,
    calculate_Fd_absMgIn_base,
    calculate_Fd_absNaIn,
    calculate_Fd_absKIn,
    calculate_Fd_absClIn,
    calculate_Fd_acCo,
    calculate_Fd_acCu,
    calculate_Fd_acFe,
    calculate_Fd_acMn,
    calculate_Fd_acZn,
    calculate_Dt_ForDNDF48,
    calculate_Dt_ForDNDF48_ForNDF,
    calculate_Dt_ADF_NDF,
    calculate_Dt_DE_ClfLiq,
    calculate_Dt_ME_ClfLiq,
    calculate_Dt_NDFnfIn,
    calculate_Dt_Lg_NDF,
    calculate_Dt_ForNDFIn,
    calculate_Dt_PastSupplIn,
    calculate_Dt_NIn,
    calculate_Dt_RUPIn,
    calculate_Dt_RUP_CP,
    calculate_Dt_fCPBdu,
    calculate_Dt_UFAIn,
    calculate_Dt_MUFAIn,
    calculate_Dt_PUFAIn,
    calculate_Dt_SatFAIn,
    calculate_Dt_OMIn,
    calculate_Dt_rOMIn,
    calculate_Dt_DM,
    calculate_Dt_NDFIn_BW,
    calculate_Dt_ForNDF_NDF,
    calculate_Dt_ForNDFIn_BW,
    calculate_Dt_DMInSum,
    calculate_Dt_DEIn_ClfLiq,
    calculate_Dt_MEIn_ClfLiq,
    calculate_Dt_CPA_CP,
    calculate_Dt_CPB_CP,
    calculate_Dt_CPC_CP,
    calculate_diet_data,
    calculate_diet_info
)

from nasem_dairy.NASEM_equations.dev_rumen_equations import (
    calculate_Rum_dcNDF,
    calculate_Rum_dcSt,
    calculate_Rum_DigNDFIn,
    calculate_Rum_DigStIn
)

from nasem_dairy.NASEM_equations.dev_microbial_protein_equations import (
    calculate_RDPIn_MiNmax,
    calculate_MiN_Vm,
    calculate_Du_MiN_NRC2021_g,
    calculate_Du_MiN_VTln_g,
    calculate_Du_MiN_VTnln_g
)

from nasem_dairy.NASEM_equations.dev_protein_equations import calculate_f_mPrt_max, calculate_Du_MiCP_g, calculate_Du_MiTP_g
from nasem_dairy.NASEM_equations.dev_amino_acid_equations import (
    calculate_Du_AAMic,
    calculate_Du_IdAAMic,
    calculate_Abs_AA_g,
    calculate_mPrtmx_AA,
    calculate_mPrtmx_AA2,
    calculate_AA_mPrtmx,
    calculate_mPrt_AA_01,
    calculate_mPrt_k_AA)

from nasem_dairy.NASEM_equations.dev_infusion_equations import (
    calculate_Inf_TPIn,
    calculate_Inf_OMIn,
    calculate_Inf_Rum,
    calculate_Inf_SI,
    calculate_Inf_Art,
    calculate_InfRum_TPIn,
    calculate_InfSI_TPIn,
    calculate_InfRum_RUPIn,
    calculate_InfRum_RUP_CP,
    calculate_InfRum_idRUPIn,
    calculate_InfSI_idTPIn,
    calculate_InfSI_idCPIn,
    calculate_Inf_idCPIn,
    calculate_InfRum_RDPIn,
    calculate_Inf_DigFAIn,
    calculate_Inf_DEAcetIn,
    calculate_Inf_DEPropIn,
    calculate_Inf_DEButrIn,
    calculate_infusion_data
)

from nasem_dairy.NASEM_equations.dev_animal_equations import (
    calculate_An_RDPIn,
    calculate_An_RDP,
    calculate_An_RDPIn_g,
    calculate_An_data
)