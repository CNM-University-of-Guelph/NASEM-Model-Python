# dev_milk_equations
# All calculations related to milk production, milk components, and milk energy
from nasem_dairy.ration_balancer.ration_balancer_functions import check_coeffs_in_coeff_dict


def calculate_Trg_NEmilk_Milk(Trg_MilkTPp,
                              Trg_MilkFatp,
                              Trg_MilkLacp):
    # If milk protein or milk lactose are missing use Tyrrell and Reid (1965) eqn.
    if Trg_MilkLacp is None or Trg_MilkTPp is None:
        Trg_NEmilk_Milk = 0.36 + 9.69 * Trg_MilkFatp/100    # Line 385/2888
    else:
        Trg_NEmilk_Milk = 9.29*Trg_MilkFatp/100 + 5.85 * \
            Trg_MilkTPp/100 + 3.95*Trg_MilkLacp/100  # Line 383/2887
    return Trg_NEmilk_Milk


def calculate_Mlk_NP_g(An_StatePhys, An_BW, Abs_AA_g, mPrt_k_AA, Abs_neAA_g, Abs_OthAA_g, Abs_EAA2b_g, mPrt_k_EAA2, An_DigNDF, An_DEInp, An_DEStIn, An_DEFAIn, An_DErOMIn, An_DENDFIn, coeff_dict):
    req_coeff = ['mPrt_Int', 'mPrt_k_NEAA', 'mPrt_k_OthAA', 'mPrt_k_DEInp',
                 'mPrt_k_DigNDF', 'mPrt_k_DEIn_StFA', 'mPrt_k_DEIn_NDF', 'mPrt_k_BW']
    check_coeffs_in_coeff_dict(coeff_dict, req_coeff)
    if An_StatePhys != "Lactating Cow":                 # Line 2204
        Mlk_NP_g = 0
    else:
        Mlk_NP_g = coeff_dict['mPrt_Int'] + Abs_AA_g['Arg'] * mPrt_k_AA['Arg'] + Abs_AA_g['His'] * mPrt_k_AA['His'] \
            + Abs_AA_g['Ile'] * mPrt_k_AA['Ile'] + Abs_AA_g['Leu'] * mPrt_k_AA['Leu'] \
            + Abs_AA_g['Lys'] * mPrt_k_AA['Lys'] + Abs_AA_g['Met'] * mPrt_k_AA['Met'] \
            + Abs_AA_g['Phe'] * mPrt_k_AA['Phe'] + Abs_AA_g['Thr'] * mPrt_k_AA['Thr'] \
            + Abs_AA_g['Trp'] * mPrt_k_AA['Trp'] + Abs_AA_g['Val'] * mPrt_k_AA['Val'] \
            + Abs_neAA_g * coeff_dict['mPrt_k_NEAA'] + Abs_OthAA_g * coeff_dict['mPrt_k_OthAA'] + Abs_EAA2b_g * mPrt_k_EAA2 \
            + An_DEInp * coeff_dict['mPrt_k_DEInp'] + (An_DigNDF - 17.06) * coeff_dict['mPrt_k_DigNDF'] + (An_DEStIn + An_DEFAIn + An_DErOMIn) \
            * coeff_dict['mPrt_k_DEIn_StFA'] + An_DENDFIn * coeff_dict['mPrt_k_DEIn_NDF'] + (An_BW - 612) * coeff_dict['mPrt_k_BW']
    return Mlk_NP_g
