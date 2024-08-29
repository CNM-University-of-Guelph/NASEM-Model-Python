"""NASEM Nutrient Requirements of Dairy Cattle model implementation.

This module implements the NASEM (National Academies of Sciences, Engineering, 
and Medicine) Nutrient Requirements of Dairy Cattle model. It provides 
a function for calculating various nutritional and physiological requirements 
for dairy cattle based on user-defined inputs such as diet composition, animal 
characteristics, and environmental conditions.

Functions:
    nasem: Runs the NASEM model to compute nutritional and physiological 
           requirements based on input data.

Example:
    user_diet_in, animal_input_in, equation_selection_in, infusion_input = nd.demo("lactating_cow_test")
    
    output = nd.nasem(
        user_diet=user_diet_in, 
        animal_input=animal_input_in, 
        equation_selection=equation_selection_in, 
    )
"""

import importlib.resources
from typing import Dict, List, Any, Optional

import numpy as np
import pandas as pd

import nasem_dairy.nasem_equations.amino_acid as aa
import nasem_dairy.nasem_equations.animal as animal
import nasem_dairy.nasem_equations.body_composition as body_comp
import nasem_dairy.nasem_equations.coefficient_adjustment as coeff_adjust
import nasem_dairy.nasem_equations.dry_matter_intake as dmi
import nasem_dairy.nasem_equations.energy_requirement as energy_req
import nasem_dairy.nasem_equations.fecal as fecal
import nasem_dairy.nasem_equations.gestation as gestation
import nasem_dairy.nasem_equations.infusion as infusion
import nasem_dairy.nasem_equations.manure as manure
import nasem_dairy.nasem_equations.methane as methane
import nasem_dairy.nasem_equations.microbial_protein as micp
import nasem_dairy.nasem_equations.micronutrient_requirement as micro_req
import nasem_dairy.nasem_equations.milk as milk
import nasem_dairy.nasem_equations.nutrient_intakes as diet
import nasem_dairy.nasem_equations.protein as protein
import nasem_dairy.nasem_equations.protein_requirement as protein_req
import nasem_dairy.nasem_equations.rumen as rumen
import nasem_dairy.nasem_equations.report as report
import nasem_dairy.nasem_equations.urine as urine
import nasem_dairy.nasem_equations.water as water
import nasem_dairy.data.constants as constants
import nasem_dairy.model.input_validation as validate
import nasem_dairy.model.utility as utility
from nasem_dairy.model_output.ModelOutput import ModelOutput


def nasem(
    user_diet: pd.DataFrame,
    animal_input: Dict[str, Any],
    equation_selection: Dict[str, Any],
    feed_library: Optional[pd.DataFrame] = None,
    coeff_dict: Optional[Dict[str, float]] = constants.coeff_dict,
    infusion_input: Optional[Dict[str, float]] = constants.infusion_dict,
    MP_NP_efficiency: Optional[Dict[str, float]] = constants.MP_NP_efficiency_dict,
    mPrt_coeff_list: Optional[List[Dict[str, float]]] = constants.mPrt_coeff_list,
    f_Imb: Optional[pd.Series] = constants.f_Imb,
) -> ModelOutput:
    """
    Run the NASEM (National Academies of Sciences, Engineering, and Medicine) Nutrient Requirements of Dairy Cattle model.

    This function runs the NASEM dairy model using various inputs, including the 
    user's diet, animal inputs, selected equations, and optional infusion data. 
    The function returns a ModelOutput object containing the results of the 
    calculations.

    Args:
        user_diet: A pandas DataFrame representing the user's diet input.
        animal_input: A dictionary containing the animal's input data, such as 
                      body weight, milk production, and other physiological parameters.
        equation_selection: A dictionary specifying the equations to be used in 
                            the model.
        feed_library: An optional pandas DataFrame representing the feed library. 
                      If not provided, the standard feed library is used.
        coeff_dict: A dictionary of coefficients used throughout the model. Defaults 
                    to the standard coefficients from the NASEM constants.
        infusion_input: An optional dictionary of nutrient infusion rates and 
                        locations. If not provided, default values are used.
        MP_NP_efficiency_dict: A dictionary containing the MP to NP efficiency 
                               coefficients for various amino acids. Defaults to the 
                               standard dictionary from NASEM constants.
        mPrt_coeff_list: A list of dictionaries containing microbial protein equation 
                         coefficients. Defaults to the standard list from NASEM constants.
        f_Imb: An optional pandas Series representing imbalance factors for amino 
               acids. If not provided, default values are used.

    Returns:
        ModelOutput: An object containing the results of the NASEM dairy model.

    Raises:
        ValueError: If any input validation checks fail or if required data is 
                    missing from the inputs.
        TypeError: If any input is not of the expected type.

    Example:
        user_diet_in, animal_input_in, equation_selection_in, infusion_input = nd.demo("lactating_cow_test")
        
        output = nd.nasem(
            user_diet=user_diet_in, 
            animal_input=animal_input_in, 
            equation_selection=equation_selection_in, 
            coeff_dict=nd.coeff_dict
        )
    """
    ####################
    # Validate Inputs  
    ####################
    if feed_library is None:
        path_to_package_data = importlib.resources.files(
            "nasem_dairy.data.feed_library"
            )
        feed_library = pd.read_csv(
            path_to_package_data.joinpath("NASEM_feed_library.csv")
        )
    user_diet = validate.validate_user_diet(user_diet.copy())
    animal_input = validate.validate_animal_input(animal_input.copy())
    equation_selection = validate.validate_equation_selection(
        equation_selection.copy()
        )
    feed_library = validate.validate_feed_library_df(feed_library.copy(),
                                                        user_diet.copy())
    coeff_dict = validate.validate_coeff_dict(coeff_dict.copy())
    infusion_input = validate.validate_infusion_input(infusion_input.copy())
    MP_NP_efficiency = validate.validate_MP_NP_efficiency_input(
        MP_NP_efficiency.copy()
        )
    mPrt_coeff_list = validate.validate_mPrt_coeff_list(mPrt_coeff_list.copy())
    f_Imb = validate.validate_f_Imb(f_Imb.copy())
    # Adjust value of mPrt_eqn when used to index mPrt_coeff_list as the indexing 
    # in R and Python use different starting values. Use max to prevent negatives
    mPrt_coeff = mPrt_coeff_list[max(0, equation_selection["mPrt_eqn"] - 1)]  
    aa_list = [
        "Arg", "His", "Ile", "Leu", "Lys", "Met", "Phe", "Thr", "Trp", "Val"
    ]
    aa_values = pd.DataFrame(index=aa_list)
    diet_data = {}
    an_data = {}

    feed_data = utility.get_feed_data(
        animal_input["Trg_Dt_DMIn"], user_diet, feed_library
        )
    feed_data["Fd_ForNDF"] = diet.calculate_Fd_ForNDF(
        feed_data["Fd_NDF"], feed_data["Fd_Conc"]
    )

    ####################
    # Dt_DMIn Calculation
    ####################
    An_PrePartDay = animal.calculate_An_PrePartDay(
        animal_input["An_GestDay"], animal_input["An_GestLength"]
        )
    An_PrePartWk = animal.calculate_An_PrePartWk(An_PrePartDay)
    Trg_NEmilk_Milk = milk.calculate_Trg_NEmilk_Milk(
        animal_input["Trg_MilkFatp"], animal_input["Trg_MilkTPp"],
        animal_input["Trg_MilkLacp"]
        )
    Trg_NEmilkOut = energy_req.calculate_Trg_NEmilkOut(
        Trg_NEmilk_Milk, animal_input["Trg_MilkProd"]
        )
    An_PrePartWklim = dmi.calculate_An_PrePartWklim(An_PrePartWk)
    An_PrePartWkDurat = animal.calculate_An_PrePartWkDurat(An_PrePartWklim)
    Dt_DMIn = dmi.calculate_Dt_DMIn(
        equation_selection["DMIn_eqn"], animal_input["Trg_Dt_DMIn"], 
        animal_input["An_StatePhys"], animal_input["An_BW"], 
        animal_input["An_BW_mature"], animal_input["An_BCS"],
        animal_input["An_LactDay"], animal_input["An_Parity_rl"], 
        animal_input["Trg_MilkProd"], animal_input["An_GestDay"], 
        animal_input["An_GestLength"], animal_input["An_AgeDryFdStart"],
        animal_input["Env_TempCurr"], An_PrePartWk, 
        Trg_NEmilkOut, An_PrePartWklim, An_PrePartWkDurat, feed_data["Fd_NDF"],
        feed_data["Fd_DMInp"], feed_data["Fd_ADF"], feed_data["Fd_ForNDF"],
        feed_data["Fd_Conc"], feed_data["Fd_DNDF48_input"],
        feed_data["Trg_Fd_DMIn"], feed_data["Fd_Category"], feed_data["Fd_CP"],
        feed_data["Fd_FA"], feed_data["Fd_Ash"], feed_data["Fd_St"], coeff_dict
        )

    ####################
    # Input Based Calculations  
    ####################
    # NOTE This section has all the calculations that use ONLY user input values
    # This was done to help with reorganizing the function. It may be possible 
    # to move some of these further down in the function to better group them 
    ### ARRAYS ###
    Trg_AbsAA_NPxprtAA = aa.calculate_Trg_AbsAA_NPxprtAA_array(
        MP_NP_efficiency, aa_list
        )
    mPrt_k_AA_array = aa.calculate_mPrt_k_AA_array(mPrt_coeff, aa_list)
    MWAA = aa.calculate_MWAA(aa_list, coeff_dict)
    Body_AA_TP = aa.calculate_Body_AA_TP(aa_list, coeff_dict)
    MiTPAAProf = aa.calculate_MiTPAAProf(aa_list, coeff_dict)
    EndAAProf = aa.calculate_EndAAProf(aa_list, coeff_dict)
    RecAA = aa.calculate_RecAA(aa_list, coeff_dict)
    Mlk_AA_TP = milk.calculate_Mlk_AA_TP(aa_list, coeff_dict)
    Fe_AAMetab_TP = fecal.calculate_Fe_AAMetab_TP(aa_list, coeff_dict)   
    Ur_AAEnd_TP = urine.calculate_Ur_AAEnd_TP(aa_list, coeff_dict)

    ### COEFFS ONLY ###
    NPGain_RsrvGain = body_comp.calculate_NPGain_RsrvGain(coeff_dict)

    ### OTHER ###
    An_DMIn_BW = animal.calculate_An_DMIn_BW(animal_input["An_BW"], Dt_DMIn)
    f_mPrt_max = protein.calculate_f_mPrt_max(
        animal_input["An_305RHA_MlkTP"], coeff_dict
        )
    Scrf_CP_g = protein.calculate_Scrf_CP_g(animal_input["An_StatePhys"],
                                            animal_input["An_BW"]
                                            )
    CPGain_FrmGain = body_comp.calculate_CPGain_FrmGain(
        animal_input["An_BW"], animal_input["An_BW_mature"]
        )
    NPGain_FrmGain = body_comp.calculate_NPGain_FrmGain(
        CPGain_FrmGain, coeff_dict
        )
    Frm_Gain = body_comp.calculate_Frm_Gain(animal_input["Trg_FrmGain"])
    Rsrv_Gain = body_comp.calculate_Rsrv_Gain(animal_input["Trg_RsrvGain"])
    Rsrv_Gain_empty = body_comp.calculate_Rsrv_Gain_empty(Rsrv_Gain)
    Rsrv_NPgain = body_comp.calculate_Rsrv_NPgain(
        NPGain_RsrvGain, Rsrv_Gain_empty
        )
    animal_input["Trg_BWgain"] = body_comp.calculate_Trg_BWgain(
        animal_input["Trg_FrmGain"], animal_input["Trg_RsrvGain"]
        )
    animal_input["Trg_BWgain_g"] = body_comp.calculate_Trg_BWgain_g(
        animal_input["Trg_BWgain"]
        )
    BW_BCS = body_comp.calculate_BW_BCS(animal_input["An_BW"])
    Body_Fat_EBW = body_comp.calculate_Body_Fat_EBW(
        animal_input["An_BW"], animal_input["An_BW_mature"]
        )
    CPGain_FrmGain = body_comp.calculate_CPGain_FrmGain(
        animal_input["An_BW"], animal_input["An_BW_mature"]
        )
    Frm_Gain = body_comp.calculate_Frm_Gain(animal_input["Trg_FrmGain"])
    An_BWmature_empty = body_comp.calculate_An_BWmature_empty(
        animal_input["An_BW_mature"], coeff_dict
        )
    coeff_dict["LCT"] = coeff_adjust.adjust_LCT(animal_input["An_AgeDay"])
    animal_input["An_PostPartDay"] = gestation.calculate_An_PostPartDay(
        animal_input["An_LactDay"]
        )
    Uter_Wtpart = gestation.calculate_Uter_Wtpart(
        animal_input["Fet_BWbrth"], coeff_dict
        )
    GrUter_Wtpart = gestation.calculate_GrUter_Wtpart(
        animal_input["Fet_BWbrth"], coeff_dict
        )
    An_Preg = gestation.calculate_An_Preg(
        animal_input["An_GestDay"], animal_input["An_GestLength"]
        )
    Fet_Wt = gestation.calculate_Fet_Wt(
        animal_input["An_GestDay"], animal_input["An_GestLength"], 
        animal_input["Fet_BWbrth"], coeff_dict
        )
    K_FeCPend_ClfLiq = fecal.calculate_K_FeCPend_ClfLiq(
        equation_selection["NonMilkCP_ClfLiq"]
        )
    Fe_rOMend = fecal.calculate_Fe_rOMend(Dt_DMIn, coeff_dict)
    Km_MP_NP_Trg = protein_req.calculate_Km_MP_NP_Trg(
        animal_input["An_StatePhys"], coeff_dict
        )    
    Trg_Mlk_NP_g = protein_req.calculate_Trg_Mlk_NP_g(
        animal_input["Trg_MilkProd"], animal_input["Trg_MilkTPp"]
        )
    An_NEm_Act_Parlor = energy_req.calculate_An_NEm_Act_Parlor(
        animal_input["An_BW"], animal_input["Env_DistParlor"],
        animal_input["Env_TripsParlor"]
        )
    An_NEm_Act_Topo = energy_req.calculate_An_NEm_Act_Topo(
        animal_input["An_BW"], animal_input["Env_Topo"]
        )
    Kr_ME_RE = energy_req.calculate_Kr_ME_RE(
        animal_input["Trg_MilkProd"], animal_input["Trg_RsrvGain"]
        )
    Ur_Nend_g = urine.calculate_Ur_Nend_g(animal_input["An_BW"])
    Ur_Nend_Urea_g = urine.calculate_Ur_Nend_Urea_g(animal_input["An_BW"])
    Ur_Nend_Creatn_g = urine.calculate_Ur_Nend_Creatn_g(animal_input["An_BW"])
    Ur_Nend_PD_g = urine.calculate_Ur_Nend_PD_g(animal_input["An_BW"])
    Ur_NPend_3MH_g = urine.calculate_Ur_NPend_3MH_g(animal_input["An_BW"])
    Ur_EAAend_g = urine.calculate_Ur_EAAend_g(animal_input["An_BW"])
    An_LactDay_MlkPred = milk.calculate_An_LactDay_MlkPred(
        animal_input["An_LactDay"]
        )
    Trg_Mlk_Fat = milk.calculate_Trg_Mlk_Fat(
        animal_input["Trg_MilkProd"], animal_input["Trg_MilkFatp"]
        )
    Trg_MilkLac = milk.calculate_Trg_MilkLac(
        animal_input["Trg_MilkLacp"], animal_input["Trg_MilkProd"]
        )
    Trg_MilkProd_EPcor = milk.calculate_Trg_MilkProd_EPcor(
        animal_input["Trg_MilkProd"], animal_input["Trg_MilkFatp"],
        animal_input["Trg_MilkTPp"]
        )
    MlkNP_Int = milk.calculate_MlkNP_Int(animal_input["An_BW"], mPrt_coeff)
    Dt_DMIn_BW = report.calculate_Dt_DMIn_BW(Dt_DMIn, animal_input["An_BW"])
    Dt_DMIn_MBW = report.calculate_Dt_DMIn_MBW(Dt_DMIn, animal_input["An_BW"])

    ####################
    # Nutrient Intakes
    ####################
    infusion_data = infusion.calculate_infusion_data(
        infusion_input, Dt_DMIn, coeff_dict
        )   
    feed_data = diet.calculate_feed_data(
        Dt_DMIn, animal_input["An_StatePhys"], 
        equation_selection["Use_DNDF_IV"], feed_data, coeff_dict
        )
    diet_data["Dt_CPIn_ClfLiq"] = diet.calculate_Dt_CPIn_ClfLiq(
        feed_data["Fd_CPIn_ClfLiq"]
        )
    diet_data["Dt_DMIn_ClfLiq"] = diet.calculate_Dt_DMIn_ClfLiq(
        feed_data["Fd_DMIn_ClfLiq"]
        )
    diet_data["Dt_NDFIn"] = diet.calculate_Dt_NDFIn(feed_data["Fd_NDFIn"])
    diet_data["Dt_StIn"] = diet.calculate_Dt_StIn(feed_data["Fd_StIn"])
    diet_data["Dt_CPIn"] = diet.calculate_Dt_CPIn(feed_data["Fd_CPIn"])
    diet_data["Dt_ADFIn"] = diet.calculate_Dt_ADFIn(feed_data["Fd_ADFIn"])
    diet_data["Dt_ForNDF"] = diet.calculate_Dt_ForNDF(
        feed_data["Fd_DMInp"], feed_data["Fd_ForNDF"]
        )
    diet_data["Dt_AshIn"] = diet.calculate_Dt_AshIn(feed_data["Fd_AshIn"])
    diet_data["Dt_FAhydrIn"] = diet.calculate_Dt_FAhydrIn(
        feed_data["Fd_FAhydrIn"]
        )
    diet_data["Dt_TPIn"] = diet.calculate_Dt_TPIn(feed_data["Fd_TPIn"])
    diet_data["Dt_NPNDMIn"] = diet.calculate_Dt_NPNDMIn(
        feed_data["Fd_NPNDMIn"]
        )
    diet_data["Dt_idRUPIn"] = diet.calculate_Dt_idRUPIn(
        feed_data["Fd_idRUPIn"]
        )
    diet_data["Dt_ForWetIn"] = diet.calculate_Dt_ForWetIn(
        feed_data["Fd_ForWetIn"]
        )
    diet_data["Dt_dcCP_ClfDry"] = diet.calculate_Dt_dcCP_ClfDry(
        animal_input["An_StatePhys"], diet_data["Dt_DMIn_ClfLiq"]
        )
    diet_data["Dt_ForNDFIn"] = diet.calculate_Dt_ForNDFIn(
        feed_data["Fd_DMIn"], feed_data["Fd_ForNDF"]
        )
    diet_data["Dt_ForWet"] = diet.calculate_Dt_ForWet(
        diet_data["Dt_ForWetIn"], Dt_DMIn
        )
    diet_data["Dt_rOMIn"] = diet.calculate_Dt_rOMIn(
        Dt_DMIn, diet_data["Dt_AshIn"], diet_data["Dt_NDFIn"], 
        diet_data["Dt_StIn"], diet_data["Dt_FAhydrIn"], diet_data["Dt_TPIn"],
        diet_data["Dt_NPNDMIn"]
        )
    diet_data["Dt_RUPIn"] = diet.calculate_Dt_RUPIn(feed_data["Fd_RUPIn"])
    diet_data["Dt_RDPIn"] = diet.calculate_Dt_RDPIn(
        diet_data["Dt_CPIn"], diet_data["Dt_RUPIn"]
        )
    an_data["An_CPIn"] = animal.calculate_An_CPIn(
        diet_data["Dt_CPIn"], infusion_data["Inf_CPIn"]
        )
    an_data["An_RUPIn"] = animal.calculate_An_RUPIn(
        diet_data["Dt_RUPIn"], infusion_data["InfRum_RUPIn"]
        )
    an_data["An_idRUPIn"] = animal.calculate_An_idRUPIn(
        diet_data["Dt_idRUPIn"], infusion_data["InfRum_idRUPIn"], 
        infusion_data["InfSI_idTPIn"]
        )
    an_data["An_DMIn"] = animal.calculate_An_DMIn(
        Dt_DMIn, infusion_data["Inf_DMIn"]
        )
    an_data["An_NDFIn"] = animal.calculate_An_NDFIn(
        diet_data["Dt_NDFIn"], infusion_data["InfRum_NDFIn"], 
        infusion_data["InfSI_NDFIn"]
    )
    an_data["An_NDF"] = animal.calculate_An_NDF(
        an_data["An_NDFIn"], Dt_DMIn, infusion_data["InfRum_DMIn"], 
        infusion_data["InfSI_DMIn"]
        )  
    an_data["An_RDPIn"] = animal.calculate_An_RDPIn(
        diet_data["Dt_RDPIn"], infusion_data["InfRum_RDPIn"]
        )
    an_data["An_RDP"] = animal.calculate_An_RDP(
        an_data["An_RDPIn"], Dt_DMIn, infusion_data["InfRum_DMIn"]
        )
    an_data["An_RDPIn_g"] = animal.calculate_An_RDPIn_g(an_data["An_RDPIn"])
    Rum_dcNDF = rumen.calculate_Rum_dcNDF(
        Dt_DMIn, diet_data["Dt_NDFIn"], diet_data["Dt_StIn"], 
        diet_data["Dt_CPIn"], diet_data["Dt_ADFIn"], diet_data["Dt_ForWet"]
        ) 
    Rum_dcSt = rumen.calculate_Rum_dcSt(
        Dt_DMIn, diet_data["Dt_ForNDF"], diet_data["Dt_StIn"], 
        diet_data["Dt_ForWet"]
        )
    Rum_DigNDFIn = rumen.calculate_Rum_DigNDFIn(
        Rum_dcNDF, diet_data["Dt_NDFIn"]
        )
    Rum_DigStIn = rumen.calculate_Rum_DigStIn(Rum_dcSt, diet_data["Dt_StIn"])    
    RDPIn_MiNmax = micp.calculate_RDPIn_MiNmax(
        Dt_DMIn, an_data["An_RDP"], an_data["An_RDPIn"]
        )
    MiN_Vm = micp.calculate_MiN_Vm(RDPIn_MiNmax, coeff_dict)
    Du_MiN_g = micp.calculate_Du_MiN_g(
        equation_selection["MiN_eqn"], MiN_Vm, diet_data["Dt_rOMIn"], 
        diet_data["Dt_ForNDFIn"], an_data["An_RDPIn"], Rum_DigNDFIn, 
        Rum_DigStIn, an_data["An_RDPIn_g"], coeff_dict
    )   
    Fe_RUP = fecal.calculate_Fe_RUP(
        an_data["An_RUPIn"], infusion_data["InfSI_TPIn"], an_data["An_idRUPIn"]
        )
    Du_MiCP_g = protein.calculate_Du_MiCP_g(Du_MiN_g)
    Du_MiCP = micp.calculate_Du_MiCP(Du_MiCP_g)
    Du_idMiCP_g = micp.calculate_Du_idMiCP_g(Du_MiCP_g, coeff_dict)
    Du_idMiCP = micp.calculate_Du_idMiCP(Du_idMiCP_g)
    Du_MiTP_g = protein.calculate_Du_MiTP_g(Du_MiCP_g, coeff_dict)
    Du_MiTP = micp.calculate_Du_MiTP(Du_MiTP_g)
    Du_idMiTP_g = micp.calculate_Du_idMiTP_g(Du_idMiCP_g, coeff_dict)
    Du_idMiTP = micp.calculate_Du_idMiTP(Du_idMiTP_g)
    Fe_RumMiCP = fecal.calculate_Fe_RumMiCP(Du_MiCP, Du_idMiCP)
    Fe_CPend_g = fecal.calculate_Fe_CPend_g(
        animal_input["An_StatePhys"], an_data["An_DMIn"], an_data["An_NDF"], 
        Dt_DMIn, diet_data["Dt_DMIn_ClfLiq"], K_FeCPend_ClfLiq
        )
    Fe_CPend = fecal.calculate_Fe_CPend(Fe_CPend_g)
    Fe_NPend = fecal.calculate_Fe_NPend(Fe_CPend)
    Fe_CP = fecal.calculate_Fe_CP(
        animal_input["An_StatePhys"], diet_data["Dt_CPIn_ClfLiq"], 
        diet_data["Dt_dcCP_ClfDry"], an_data["An_CPIn"], Fe_RUP, Fe_RumMiCP, 
        Fe_CPend, infusion_data["InfSI_NPNCPIn"], coeff_dict
        )
    Fe_MiTP = fecal.calculate_Fe_MiTP(Du_MiTP, Du_idMiTP)
    Fe_RDPend = fecal.calculate_Fe_RDPend(
        Fe_CPend, an_data["An_RDPIn"], an_data["An_CPIn"]
        )
    Fe_RUPend = fecal.calculate_Fe_RUPend(
        Fe_CPend, an_data["An_RUPIn"], an_data["An_CPIn"]
        )
    Fe_DEMiCPend = fecal.calculate_Fe_DEMiCPend(Fe_RumMiCP, coeff_dict)
    Fe_DERDPend = fecal.calculate_Fe_DERDPend(Fe_RDPend, coeff_dict)
    Fe_DERUPend = fecal.calculate_Fe_DERUPend(Fe_RUPend, coeff_dict)
    aa_values["Du_AAMic"] = aa.calculate_Du_AAMic(Du_MiTP_g, MiTPAAProf)
    aa_values["Du_IdAAMic"] = aa.calculate_Du_IdAAMic(
        aa_values["Du_AAMic"], coeff_dict
        )
    Uter_Wt = gestation.calculate_Uter_Wt(
        animal_input["An_Parity_rl"], animal_input["An_AgeDay"], 
        animal_input["An_LactDay"], animal_input["An_GestDay"], 
        animal_input["An_GestLength"], Uter_Wtpart, coeff_dict
        )
    GrUter_Wt = gestation.calculate_GrUter_Wt(
        animal_input["An_GestDay"], animal_input["An_GestLength"], Uter_Wt, 
        GrUter_Wtpart, coeff_dict
        )
    ##### DIET_DATA #####
    diet_data = diet.calculate_diet_data(
        feed_data, diet_data, Dt_DMIn, animal_input["An_BW"], 
        animal_input["An_StatePhys"], An_DMIn_BW, 
        animal_input["An_AgeDryFdStart"], animal_input["Env_TempCurr"],
        equation_selection["DMIn_eqn"], equation_selection["Monensin_eqn"],
        Fe_rOMend, Fe_CP, Fe_CPend,  Fe_MiTP,  Fe_NPend, Du_idMiTP, 
        aa_values["Du_IdAAMic"], coeff_dict
        )
    ##### AN_DATA #####
    an_data = animal.calculate_an_data(
        an_data, diet_data, infusion_data, equation_selection["Monensin_eqn"], 
        GrUter_Wt, Dt_DMIn, Fe_CP, animal_input["An_StatePhys"], 
        animal_input["An_BW"], animal_input["An_BW_mature"], 
        animal_input["An_Parity_rl"], Fe_MiTP, Fe_NPend, Fe_DEMiCPend, 
        Fe_DERDPend, Fe_DERUPend, Du_idMiCP, coeff_dict
        )    
    diet_data["TT_dcAnSt"] = diet.calculate_TT_dcAnSt(
        an_data["An_DigStIn"], diet_data["Dt_StIn"], infusion_data["Inf_StIn"]
        )
    diet_data["TT_dcrOMa"] = diet.calculate_TT_dcrOMa(
        an_data["An_DigrOMaIn"], diet_data["Dt_rOMIn"],
        infusion_data["InfRum_GlcIn"], infusion_data["InfRum_AcetIn"],
        infusion_data["InfRum_PropIn"], infusion_data["InfRum_ButrIn"],
        infusion_data["InfSI_GlcIn"], infusion_data["InfSI_AcetIn"],
        infusion_data["InfSI_PropIn"], infusion_data["InfSI_ButrIn"]
        )
    diet_data["TT_dcrOMt"] = diet.calculate_TT_dcrOMt(
        an_data["An_DigrOMtIn"], diet_data["Dt_rOMIn"],
        infusion_data["InfRum_GlcIn"], infusion_data["InfRum_AcetIn"],
        infusion_data["InfRum_PropIn"], infusion_data["InfRum_ButrIn"],
        infusion_data["InfSI_GlcIn"], infusion_data["InfSI_AcetIn"],
        infusion_data["InfSI_PropIn"], infusion_data["InfSI_ButrIn"]
        )  

    ####################
    # Gestation Energy and Net Protein
    ####################
    Uter_BWgain = gestation.calculate_Uter_BWgain(
        animal_input["An_LactDay"], animal_input["An_GestDay"], 
        animal_input["An_GestLength"], Uter_Wt, coeff_dict
        )
    GrUter_BWgain = gestation.calculate_GrUter_BWgain(
        animal_input["An_LactDay"], animal_input["An_GestDay"], 
        animal_input["An_GestLength"], GrUter_Wt, Uter_BWgain, coeff_dict
        )
    Fet_BWgain = gestation.calculate_Fet_BWgain(
        animal_input["An_GestDay"], animal_input["An_GestLength"], 
        Fet_Wt, coeff_dict
        )
    Conc_BWgain = body_comp.calculate_Conc_BWgain(GrUter_BWgain, Uter_BWgain)
    Gest_NCPgain_g = gestation.calculate_Gest_NCPgain_g(
        GrUter_BWgain, coeff_dict
        )
    Gest_NPgain_g = gestation.calculate_Gest_NPgain_g(
        Gest_NCPgain_g, coeff_dict
        )
    Gest_NPuse_g = gestation.calculate_Gest_NPuse_g(Gest_NPgain_g, coeff_dict)
    Gest_CPuse_g = gestation.calculate_Gest_CPuse_g(Gest_NPuse_g, coeff_dict)
    aa_values["Gest_AA_g"] = gestation.calculate_Gest_AA_g(
        Gest_NPuse_g, Body_AA_TP
        )
    Gest_EAA_g = gestation.calculate_Gest_EAA_g(aa_values["Gest_AA_g"])

    ####################
    # Digestable Nutrients
    ####################
    Rum_DigNDFnfIn = rumen.calculate_Rum_DigNDFnfIn(
        Rum_dcNDF, diet_data["Dt_NDFnfIn"]
        )
    Du_StPas = rumen.calculate_Du_StPas(
        diet_data["Dt_StIn"], infusion_data["InfRum_StIn"], Rum_DigStIn
        )
    Du_NDFPas = rumen.calculate_Du_NDFPas(
        diet_data["Dt_NDFIn"], infusion_data["Inf_NDFIn"], Rum_DigNDFIn
        )
    Rum_MiCP_DigCHO = micp.calculate_Rum_MiCP_DigCHO(
        Du_MiCP, Rum_DigNDFIn, Rum_DigStIn
        )
    Du_IdEAAMic = aa.calculate_Du_IdEAAMic(aa_values["Du_IdAAMic"])
    Dt_IdAARUPIn = diet.calculate_Dt_IdAARUPIn_array(diet_data, aa_list)
    Dt_IdEAARUPIn = aa.calculate_Dt_IdEAARUPIn(Dt_IdAARUPIn)

    ####################
    # Ruminal N Flow and Microbial Crude Protein
    ####################
    Du_EndCP_g = micp.calculate_Du_EndCP_g(
        Dt_DMIn, infusion_data["InfRum_DMIn"]
        )
    Du_EndN_g = micp.calculate_Du_EndN_g(Dt_DMIn, infusion_data["InfRum_DMIn"])
    Du_EndCP = micp.calculate_Du_EndCP(Du_EndCP_g)
    Du_EndN = micp.calculate_Du_EndN(Du_EndN_g)
    Du_NAN_g = micp.calculate_Du_NAN_g(Du_MiN_g, an_data["An_RUPIn"], Du_EndN_g)
    Du_NANMN_g = micp.calculate_Du_NANMN_g(an_data["An_RUPIn"], Du_EndN_g)
    An_RDPbal_g = animal.calculate_An_RDPbal_g(an_data["An_RDPIn_g"], Du_MiCP_g)
    Du_MiN_NRC2001_g = micp.calculate_Du_MiN_NRC2001_g(
        diet_data["Dt_TDNIn"], an_data["An_RDPIn"]
        )
    An_MPIn = animal.calculate_An_MPIn(
        animal_input["An_StatePhys"], an_data["An_DigCPtIn"], 
        diet_data["Dt_idRUPIn"], Du_idMiTP, infusion_data["InfArt_TPIn"]
        )
    An_MPIn_g = animal.calculate_An_MPIn_g(An_MPIn)
    An_MP = animal.calculate_An_MP(
        An_MPIn, Dt_DMIn, infusion_data["InfRum_DMIn"], 
        infusion_data["InfSI_DMIn"]
        )
    An_MP_CP = animal.calculate_An_MP_CP(An_MPIn, an_data["An_CPIn"])

    ####################
    # Amino Acids
    ####################
    An_IdAAIn = aa.calculate_An_IdAAIn_array(an_data, aa_list)
    An_IdEAAIn = aa.calculate_An_IdEAAIn(An_IdAAIn)
    Inf_AA_g = aa.calculate_Inf_AA_g(infusion_data, aa_list)
    Dt_AARUPIn = aa.calculate_Dt_AARUPIn(aa_list, diet_data)
    Inf_AARUPIn = aa.calculate_Inf_AARUPIn(aa_list, infusion_data)
    Dt_AAIn = aa.calculate_Dt_AAIn(aa_list, diet_data)
    aa_values["Du_AAEndP"] = aa.calculate_Du_AAEndP(Du_EndCP_g, EndAAProf)
    aa_values["Du_AA"] = aa.calculate_Du_AA(
        Dt_AARUPIn, Inf_AARUPIn, aa_values["Du_AAMic"], aa_values["Du_AAEndP"]
        )
    Du_EAA_g = aa.calculate_Du_EAA_g(aa_values["Du_AA"])
    aa_values["DuAA_DtAA"] = aa.calculate_DuAA_AArg(aa_values["Du_AA"], Dt_AAIn)
    aa_values["Du_AA24h"] = aa.calculate_Du_AA24h(aa_values["Du_AA"], RecAA)
    aa_values["Abs_AA_g"] = aa.calculate_Abs_AA_g(
        An_IdAAIn, Inf_AA_g, infusion_data["Inf_Art"]
        )
    aa_values["mPrtmx_AA"] = aa.calculate_mPrtmx_AA(mPrt_k_AA_array, mPrt_coeff)
    aa_values["mPrtmx_AA2"] = aa.calculate_mPrtmx_AA2(
        aa_values["mPrtmx_AA"], f_mPrt_max
        )
    aa_values["AA_mPrtmx"] = aa.calculate_AA_mPrtmx(mPrt_k_AA_array, mPrt_coeff)
    aa_values["mPrt_AA_01"] = aa.calculate_mPrt_AA_01(
        aa_values["AA_mPrtmx"], mPrt_k_AA_array, mPrt_coeff
        )
    aa_values["mPrt_k_AA"] = aa.calculate_mPrt_k_AA(
        aa_values["mPrtmx_AA2"], aa_values["mPrt_AA_01"], aa_values["AA_mPrtmx"]
        )
    aa_values["IdAA_DtAA"] = aa.calculate_IdAA_DtAA(Dt_AAIn, An_IdAAIn)
    Abs_EAA_g = aa.calculate_Abs_EAA_g(aa_values["Abs_AA_g"])
    Abs_neAA_g = aa.calculate_Abs_neAA_g(An_MPIn_g, Abs_EAA_g)
    Abs_OthAA_g = aa.calculate_Abs_OthAA_g(Abs_neAA_g, aa_values["Abs_AA_g"])
    Abs_EAA2b_g = aa.calculate_Abs_EAA2b_g(
        equation_selection["mPrt_eqn"], aa_values["Abs_AA_g"]
        )
    mPrt_k_EAA2 = aa.calculate_mPrt_k_EAA2(
        aa_values["mPrtmx_AA2"], aa_values["mPrt_AA_01"], aa_values["AA_mPrtmx"]
        )
    Abs_EAA2_g = aa.calculate_Abs_EAA2_g(aa_values["Abs_AA_g"])
    aa_values["Abs_AA_MPp"] = aa.calculate_Abs_AA_MPp(
        aa_values["Abs_AA_g"], An_MPIn_g
        )
    aa_values["Abs_AA_p"] = aa.calculate_Abs_AA_p(
        aa_values["Abs_AA_g"], Abs_EAA_g
        )
    aa_values["Abs_AA_DEI"] = aa.calculate_Abs_AA_DEI(
        aa_values["Abs_AA_g"], an_data["An_DEIn"]
        )
    aa_values["Abs_AA_mol"] = aa.calculate_Abs_AA_mol(
        aa_values["Abs_AA_g"], MWAA
        )
    aa_values["GestAA_AbsAA"] = gestation.calculate_GestAA_AbsAA(
        aa_values["Gest_AA_g"], aa_values["Abs_AA_g"]
        )

    ####################
    # Fecal Loss
    ####################
    Fe_Nend = fecal.calculate_Fe_Nend(Fe_CPend)
    Fe_NPend_g = fecal.calculate_Fe_NPend_g(Fe_NPend)
    Fe_MPendUse_g_Trg = fecal.calculate_Fe_MPendUse_g_Trg(
        animal_input["An_StatePhys"], Fe_CPend_g, Fe_NPend_g, Km_MP_NP_Trg
        )
    Fe_InfCP = fecal.calculate_Fe_InfCP(
        infusion_data["InfRum_RUPIn"], infusion_data["InfSI_CPIn"], 
        infusion_data["InfRum_idRUPIn"], infusion_data["InfSI_idCPIn"]
        )
    Fe_TP = fecal.calculate_Fe_TP(Fe_RUP, Fe_MiTP, Fe_NPend)
    Fe_N = fecal.calculate_Fe_N(Fe_CP)
    Fe_N_g = fecal.calculate_Fe_N_g(Fe_N)
    Fe_FA = fecal.calculate_Fe_FA(
        diet_data["Dt_FAIn"], infusion_data["InfRum_FAIn"], 
        infusion_data["InfSI_FAIn"], diet_data["Dt_DigFAIn"], 
        infusion_data["Inf_DigFAIn"]
        )
    Fe_OM_end = fecal.calculate_Fe_OM_end(Fe_rOMend, Fe_CPend)
    Fe_rOM = fecal.calculate_Fe_rOM(
        an_data["An_rOMIn"], an_data["An_DigrOMaIn"]
        )
    Fe_St = fecal.calculate_Fe_St(
        diet_data["Dt_StIn"], infusion_data["Inf_StIn"], an_data["An_DigStIn"]
        )
    Fe_NDF = fecal.calculate_Fe_NDF(
        diet_data["Dt_NDFIn"], diet_data["Dt_DigNDFIn"]
        )
    Fe_NDFnf = fecal.calculate_Fe_NDFnf(
        diet_data["Dt_NDFnfIn"], diet_data["Dt_DigNDFnfIn"]
        )
    Fe_OM = fecal.calculate_Fe_OM(Fe_CP, Fe_NDF, Fe_St, Fe_rOM, Fe_FA)
    Fe_DEout = fecal.calculate_Fe_DEout(an_data["An_GEIn"], an_data["An_DEIn"])
    Fe_DE_GE = fecal.calculate_Fe_DE_GE(Fe_DEout, an_data["An_GEIn"])
    Fe_DE = fecal.calculate_Fe_DE(Fe_DEout, an_data["An_DMIn"])
    Fe_AAMet_g = fecal.calculate_Fe_AAMet_g(Fe_NPend_g, Fe_AAMetab_TP)
    Fe_AAMet_AbsAA = fecal.calculate_Fe_AAMet_AbsAA(
        Fe_AAMet_g, aa_values["Abs_AA_g"]
        )
    
    ####################
    # Milk Protein
    ####################
    Trg_Mlk_NP = milk.calculate_Trg_Mlk_NP(Trg_Mlk_NP_g)
    Mlk_NPmx = milk.calculate_Mlk_NPmx(
        aa_values["mPrtmx_AA2"], an_data["An_DEInp"], an_data["An_DigNDF"], 
        animal_input["An_BW"], Abs_neAA_g, Abs_OthAA_g, mPrt_coeff
        )
    Mlk_NP_g = milk.calculate_Mlk_NP_g(
        animal_input["An_StatePhys"], equation_selection["mPrt_eqn"],
        Trg_Mlk_NP_g, animal_input["An_BW"], aa_values["Abs_AA_g"], 
        aa_values["mPrt_k_AA"], Abs_neAA_g, Abs_OthAA_g, Abs_EAA2b_g, 
        mPrt_k_EAA2, an_data["An_DigNDF"], an_data["An_DEInp"],
        an_data["An_DEStIn"], an_data["An_DEFAIn"], an_data["An_DErOMIn"],
        an_data["An_DENDFIn"], mPrt_coeff
        )
    aa_values["Mlk_AA_g"] = milk.calculate_Mlk_AA_g(Mlk_NP_g, Mlk_AA_TP)
    aa_values["MlkAA_AbsAA"] = milk.calculate_MlkAA_AbsAA(
        aa_values["Mlk_AA_g"], aa_values["Abs_AA_g"]
        )
    aa_values["MlkAA_DtAA"] = milk.calculate_MlkAA_DtAA(
        aa_values["Mlk_AA_g"], Dt_AAIn
        )
    aa_values["Trg_Mlk_AA_g"] = aa.calculate_Trg_Mlk_AA_g(
        Trg_Mlk_NP_g, Mlk_AA_TP
        )
    Trg_Mlk_EAA_g = aa.calculate_Trg_Mlk_EAA_g(aa_values["Trg_Mlk_AA_g"])
    
    
    MlkNP_MlkNPmx = milk.calculate_MlkNP_MlkNPmx(Mlk_NP_g, Mlk_NPmx)
    Mlk_CP_g = milk.calculate_Mlk_CP_g(Mlk_NP_g)
    Mlk_CP = milk.calculate_Mlk_CP(Mlk_CP_g)
    Mlk_EAA_g = milk.calculate_Mlk_EAA_g(aa_values["Mlk_AA_g"])
    MlkNP_AnMP = milk.calculate_MlkNP_AnMP(Mlk_NP_g, An_MPIn_g)
    MlkEAA_AbsEAA = milk.calculate_MlkEAA_AbsEAA(Mlk_EAA_g, Abs_EAA_g)
    MlkNP_AnCP = milk.calculate_MlkNP_AnCP(Mlk_NP_g, an_data["An_CPIn"])
    Mlk_NP = milk.calculate_Mlk_NP(Mlk_NP_g)
    
    ####################
    # Body Composition, Frame, and Reserve Gain
    ####################
    Frm_Gain_empty = body_comp.calculate_Frm_Gain_empty(
        Frm_Gain, diet_data["Dt_DMIn_ClfLiq"], diet_data["Dt_DMIn_ClfStrt"], 
        an_data["An_GutFill_BW"]
        )
    Body_Gain_empty = body_comp.calculate_Body_Gain_empty(
        Frm_Gain_empty, Rsrv_Gain_empty
        )
    An_REgain_Calf = animal.calculate_An_REgain_Calf(
        Body_Gain_empty, an_data["An_BW_empty"]
        )
    Frm_NPgain = body_comp.calculate_Frm_NPgain(
        animal_input["An_StatePhys"], NPGain_FrmGain, Frm_Gain_empty, 
        Body_Gain_empty, An_REgain_Calf
        )
    Body_NPgain = body_comp.calculate_Body_NPgain(Frm_NPgain, Rsrv_NPgain)
    Body_CPgain = body_comp.calculate_Body_CPgain(Body_NPgain, coeff_dict)
    Body_CPgain_g = body_comp.calculate_Body_CPgain_g(Body_CPgain)
    Body_Gain = body_comp.calculate_Body_Gain(Frm_Gain, Rsrv_Gain)
    FatGain_FrmGain = body_comp.calculate_FatGain_FrmGain(
        animal_input["An_StatePhys"], An_REgain_Calf, animal_input["An_BW"], 
        animal_input["An_BW_mature"]
        )
    an_data["An_BWnp3"] = body_comp.calculate_An_BWnp3(
        an_data["An_BWnp"], animal_input["An_BCS"]
        )
    an_data["An_GutFill_Wt_Erdman"] = body_comp.calculate_An_GutFill_Wt_Erdman(
        Dt_DMIn, infusion_data["InfRum_DMIn"], infusion_data["InfSI_DMIn"]
        )
    an_data["An_BWnp_empty"] = body_comp.calculate_An_BWnp_empty(
        an_data["An_BWnp"], an_data["An_GutFill_Wt"]
        )
    an_data["An_BWnp3_empty"] = body_comp.calculate_An_BWnp3_empty(
        an_data["An_BWnp3"], an_data["An_GutFill_Wt"]
        )
    Body_NonFat_EBW = body_comp.calculate_Body_NonFat_EBW(Body_Fat_EBW)
    Body_CP_EBW = body_comp.calculate_Body_CP_EBW(Body_NonFat_EBW)
    Body_Ash_EBW = body_comp.calculate_Body_Ash_EBW(Body_NonFat_EBW)
    Body_Wat_EBW = body_comp.calculate_Body_Wat_EBW(Body_NonFat_EBW)
    Body_Fat = body_comp.calculate_Body_Fat(
        an_data["An_BWnp_empty"], Body_Fat_EBW
        )
    Body_NonFat = body_comp.calculate_Body_NonFat(
        an_data["An_BWnp_empty"], Body_NonFat_EBW
        )
    Body_CP = body_comp.calculate_Body_CP(
        an_data["An_BWnp_empty"], Body_NonFat_EBW
        )
    Body_Ash = body_comp.calculate_Body_Ash(
        an_data["An_BWnp_empty"], Body_Ash_EBW
        )
    Body_Wat = body_comp.calculate_Body_Wat(
        an_data["An_BWnp_empty"], Body_Wat_EBW
        )
    An_BodConcgain = body_comp.calculate_An_BodConcgain(Body_Gain, Conc_BWgain)
    NonFatGain_FrmGain = body_comp.calculate_NonFatGain_FrmGain(FatGain_FrmGain)
    Rsrv_AshGain = body_comp.calculate_Rsrv_AshGain(
        Rsrv_Gain_empty, coeff_dict
        )
    Rsrv_Fatgain = body_comp.calculate_Rsrv_Fatgain(Rsrv_Gain_empty, coeff_dict)
    Rsrv_CPgain = body_comp.calculate_Rsrv_CPgain(
        CPGain_FrmGain, Rsrv_Gain_empty
        )
    Frm_Fatgain = body_comp.calculate_Frm_Fatgain(
        FatGain_FrmGain, Frm_Gain_empty
        )
    NPGain_FrmGain = body_comp.calculate_NPGain_FrmGain(
        CPGain_FrmGain, coeff_dict
        )
    Frm_NPgain = body_comp.calculate_Frm_NPgain(
        animal_input["An_StatePhys"], NPGain_FrmGain, Frm_Gain_empty, 
        Body_Gain_empty, An_REgain_Calf
        )
    Frm_CPgain = body_comp.calculate_Frm_CPgain(Frm_NPgain, coeff_dict)
    Body_Fatgain = body_comp.calculate_Body_Fatgain(Frm_Fatgain, Rsrv_Fatgain)
    Body_NonFatGain = body_comp.calculate_Body_NonFatGain(
        Body_Gain_empty, Body_Fatgain
        )
    Frm_CPgain_g = body_comp.calculate_Frm_CPgain_g(Frm_CPgain)
    Rsrv_CPgain_g = body_comp.calculate_Rsrv_CPgain_g(Rsrv_CPgain)
    Body_AshGain = body_comp.calculate_Body_AshGain(Body_NonFatGain)
    Frm_AshGain = body_comp.calculate_Frm_AshGain(Body_AshGain)
    WatGain_RsrvGain = body_comp.calculate_WatGain_RsrvGain(
        NPGain_RsrvGain, coeff_dict
        )
    Rsrv_WatGain = body_comp.calculate_Rsrv_WatGain(
        WatGain_RsrvGain, Rsrv_Gain_empty
        )
    Body_WatGain = body_comp.calculate_Body_WatGain(Body_NonFatGain)
    Frm_WatGain = body_comp.calculate_Frm_WatGain(Body_WatGain, Rsrv_WatGain)

    ####################
    # Urine Loss
    ####################
    Ur_Nout_g = urine.calculate_Ur_Nout_g(
        diet_data["Dt_CPIn"], Fe_CP, Scrf_CP_g, Fe_CPend_g, Mlk_CP_g, 
        Body_CPgain_g, Gest_CPuse_g
        )
    Ur_DEout = urine.calculate_Ur_DEout(Ur_Nout_g)
    Ur_NPend_g = urine.calculate_Ur_NPend_g(
        animal_input["An_StatePhys"], animal_input["An_BW"], Ur_Nend_g
        )
    Ur_MPendUse_g = urine.calculate_Ur_MPendUse_g(Ur_NPend_g)
    Ur_Nend_Creat_g = urine.calculate_Ur_Nend_Creat_g(Ur_Nend_Creatn_g)
    Ur_Nend_3MH_g = urine.calculate_Ur_Nend_3MH_g(Ur_NPend_3MH_g, coeff_dict)
    Ur_Nend_sum_g = urine.calculate_Ur_Nend_sum_g(
        Ur_Nend_Urea_g, Ur_Nend_Creatn_g, Ur_Nend_Creat_g, Ur_Nend_PD_g, 
        Ur_Nend_3MH_g
        )
    Ur_Nend_Hipp_g = urine.calculate_Ur_Nend_Hipp_g(Ur_Nend_sum_g)
    Ur_NPend = urine.calculate_Ur_NPend(Ur_NPend_g)
    Ur_MPend = urine.calculate_Ur_MPend(Ur_NPend)
    Ur_AAEnd_g = urine.calculate_Ur_AAEnd_g(
        Ur_EAAend_g, Ur_NPend_3MH_g, Ur_AAEnd_TP
        )
    Ur_AAEnd_AbsAA = urine.calculate_Ur_AAEnd_AbsAA(
        Ur_AAEnd_g, aa_values["Abs_AA_g"]
        )
    Ur_EAAEnd_g = urine.calculate_Ur_EAAEnd_g(Ur_AAEnd_g)
    Ur_Nout_DigNIn = urine.calculate_Ur_Nout_DigNIn(
        Ur_Nout_g, an_data["An_DigCPtIn"]
        )
    Ur_Nout_CPcatab = urine.calculate_Ur_Nout_CPcatab(Ur_Nout_g, Ur_Nend_g)
    UrDE_DMIn = urine.calculate_UrDE_DMIn(Ur_DEout, an_data["An_DMIn"])
    UrDE_GEIn = urine.calculate_UrDE_GEIn(Ur_DEout, an_data["An_GEIn"])
    UrDE_DEIn = urine.calculate_UrDE_DEIn(Ur_DEout, an_data["An_DEIn"])

    ####################
    # Energy Intake
    ####################
    An_MEIn = animal.calculate_An_MEIn(
        animal_input["An_StatePhys"], animal_input["An_BW"], an_data["An_DEIn"],
        an_data["An_GasEOut"], Ur_DEout, diet_data["Dt_DMIn_ClfLiq"],
        diet_data["Dt_DEIn_base_ClfLiq"], diet_data["Dt_DEIn_base_ClfDry"],
        equation_selection["RumDevDisc_Clf"]
        )
    An_NEIn = animal.calculate_An_NEIn(An_MEIn)
    An_NE = animal.calculate_An_NE(An_NEIn, an_data["An_DMIn"])
    if animal_input["An_StatePhys"] == "Calf":
        an_data["An_MEIn_ClfDry"] = animal.calculate_An_MEIn_ClfDry(
            An_MEIn, diet_data["Dt_MEIn_ClfLiq"]
            )
        an_data["An_ME_ClfDry"] = animal.calculate_An_ME_ClfDry(
            an_data["An_MEIn_ClfDry"], an_data["An_DMIn"], 
            diet_data["Dt_DMIn_ClfLiq"]
            )
        an_data["An_NE_ClfDry"] = animal.calculate_An_NE_ClfDry(
            an_data["An_ME_ClfDry"]
            )
    An_NEmUse_NS = energy_req.calculate_An_NEmUse_NS(
        animal_input["An_StatePhys"], animal_input["An_BW"], 
        an_data["An_BW_empty"], animal_input["An_Parity_rl"], 
        diet_data["Dt_DMIn_ClfLiq"]
        )
    An_NEm_Act_Graze = energy_req.calculate_An_NEm_Act_Graze(
        diet_data["Dt_PastIn"], Dt_DMIn, 
        diet_data["Dt_PastSupplIn"], an_data["An_MBW"]
        )
    An_NEmUse_Act = energy_req.calculate_An_NEmUse_Act(
        An_NEm_Act_Graze, An_NEm_Act_Parlor, An_NEm_Act_Topo
        )
    An_NEmUse = energy_req.calculate_An_NEmUse(
        An_NEmUse_NS, An_NEmUse_Act, coeff_dict
        )
    if animal_input["An_StatePhys"] == "Calf":
        Km_ME_NE = energy_req.calculate_Km_ME_NE_Clf(
            an_data["An_ME_ClfDry"], an_data["An_NE_ClfDry"], 
            diet_data["Dt_DMIn_ClfLiq"], diet_data["Dt_DMIn_ClfStrt"]
            )
    else:
        Km_ME_NE = energy_req.calculate_Km_ME_NE(animal_input["An_StatePhys"])
    An_MEmUse = energy_req.calculate_An_MEmUse(An_NEmUse, Km_ME_NE)
    Rsrv_NEgain = energy_req.calculate_Rsrv_NEgain(Rsrv_Fatgain, Rsrv_CPgain)
    Rsrv_MEgain = energy_req.calculate_Rsrv_MEgain(Rsrv_NEgain, Kr_ME_RE)
    Frm_NEgain = energy_req.calculate_Frm_NEgain(Frm_Fatgain, Frm_CPgain)
    Kf_ME_RE_ClfDry = energy_req.calculate_Kf_ME_RE_ClfDry(an_data["An_DE"])
    Kf_ME_RE = energy_req.calculate_Kf_ME_RE(
        animal_input["An_StatePhys"], Kf_ME_RE_ClfDry, 
        diet_data["Dt_DMIn_ClfLiq"], Dt_DMIn, coeff_dict
        )
    Frm_MEgain = energy_req.calculate_Frm_MEgain(Frm_NEgain, Kf_ME_RE)
    An_MEgain = energy_req.calculate_An_MEgain(Rsrv_MEgain, Frm_MEgain)
    Gest_REgain = energy_req.calculate_Gest_REgain(GrUter_BWgain, coeff_dict)
    Ky_ME_NE = energy_req.calculate_Ky_ME_NE(Gest_REgain)
    Gest_MEuse = energy_req.calculate_Gest_MEuse(Gest_REgain, Ky_ME_NE)
    Trg_Mlk_NEout = energy_req.calculate_Trg_Mlk_NEout(
        animal_input["Trg_MilkProd"], Trg_NEmilk_Milk
        )
    Trg_Mlk_MEout = energy_req.calculate_Trg_Mlk_MEout(
        Trg_Mlk_NEout, coeff_dict
        )
    Trg_MEuse = energy_req.calculate_Trg_MEuse(
        An_MEmUse, An_MEgain, Gest_MEuse, Trg_Mlk_MEout
        )
    ### Estimated ME and NE Intakes ###
    An_ME = animal.calculate_An_ME(An_MEIn, an_data["An_DMIn"])
    An_ME_GE = animal.calculate_An_ME_GE(An_MEIn, an_data["An_GEIn"])
    An_ME_DE = animal.calculate_An_ME_DE(An_MEIn, an_data["An_DEIn"])
    An_NE_GE = animal.calculate_An_NE_GE(An_NEIn, an_data["An_GEIn"])
    An_NE_DE = animal.calculate_An_NE_DE(An_NEIn, an_data["An_DEIn"])
    An_NE_ME = animal.calculate_An_NE_ME(An_NEIn, An_MEIn)
    An_MPIn_MEIn = animal.calculate_An_MPIn_MEIn(An_MPIn_g, An_MEIn)
    ### ME and NE Use ###
    An_MEmUse_NS = energy_req.calculate_An_MEmUse_NS(An_NEmUse_NS, Km_ME_NE)
    An_MEmUse_Act = energy_req.calculate_An_MEmUse_Act(An_NEmUse_Act, Km_ME_NE)
    An_MEmUse_Env = energy_req.calculate_An_MEmUse_Env(Km_ME_NE, coeff_dict)
    An_NEm_ME = energy_req.calculate_An_NEm_ME(An_NEmUse, An_MEIn)
    An_NEm_DE = energy_req.calculate_An_NEm_DE(An_NEmUse, an_data["An_DEIn"])
    An_NEmNS_DE = energy_req.calculate_An_NEmNS_DE(
        An_NEmUse_NS, an_data["An_DEIn"]
        )
    An_NEmAct_DE = energy_req.calculate_An_NEmAct_DE(
        An_NEmUse_Act, an_data["An_DEIn"]
        )
    An_NEmEnv_DE = energy_req.calculate_An_NEmEnv_DE(
        an_data["An_DEIn"], coeff_dict
        )
    An_NEprod_Avail = energy_req.calculate_An_NEprod_Avail(An_NEIn, An_NEmUse)
    An_MEprod_Avail = energy_req.calculate_An_MEprod_Avail(An_MEIn, An_MEmUse)
    Gest_NELuse = energy_req.calculate_Gest_NELuse(Gest_MEuse, coeff_dict)
    Gest_NE_ME = energy_req.calculate_Gest_NE_ME(Gest_MEuse, An_MEIn)
    Gest_NE_DE = energy_req.calculate_Gest_NE_DE(
        Gest_REgain, an_data["An_DEIn"]
        )
    An_REgain = energy_req.calculate_An_REgain(Body_Fatgain, Body_CPgain)
    Rsrv_NE_DE = energy_req.calculate_Rsrv_NE_DE(
        Rsrv_NEgain, an_data["An_DEIn"]
        )
    Frm_NE_DE = energy_req.calculate_Frm_NE_DE(Frm_NEgain, an_data["An_DEIn"])
    Body_NEgain_BWgain = energy_req.calculate_Body_NEgain_BWgain(
        An_REgain, Body_Gain
        )
    An_ME_NEg = energy_req.calculate_An_ME_NEg(An_REgain, An_MEgain)
    Rsrv_NELgain = energy_req.calculate_Rsrv_NELgain(Rsrv_MEgain, coeff_dict)
    Frm_NELgain = energy_req.calculate_Frm_NELgain(Frm_MEgain, coeff_dict)
    An_NELgain = energy_req.calculate_An_NELgain(An_MEgain, coeff_dict)
    An_NEgain_DE = energy_req.calculate_An_NEgain_DE(
        An_REgain, an_data["An_DEIn"]
        )
    An_NEgain_ME = energy_req.calculate_An_NEgain_ME(An_REgain, An_MEIn)
    En_OM = animal.calculate_En_OM(an_data["An_DEIn"], an_data["An_DigOMtIn"])

    ####################
    # Protein Requirement
    ####################
    Scrf_NP_g = protein.calculate_Scrf_NP_g(Scrf_CP_g, coeff_dict)
    Scrf_MPUse_g_Trg = protein.calculate_Scrf_MPUse_g_Trg(
        animal_input["An_StatePhys"], Scrf_CP_g, Scrf_NP_g, Km_MP_NP_Trg
        )
    Scrf_NP = protein.calculate_Scrf_NP(Scrf_NP_g)
    Scrf_N_g = protein.calculate_Scrf_N_g(Scrf_CP_g)
    Scrf_AA_TP = protein.calculate_Scrf_AA_TP(aa_list, coeff_dict)
    Scrf_AA_g = protein.calculate_Scrf_AA_g(Scrf_NP_g, Scrf_AA_TP)
    ScrfAA_AbsAA = protein.calculate_ScrfAA_AbsAA(
        Scrf_AA_g, aa_values["Abs_AA_g"]
        )
    An_MPm_g_Trg = protein_req.calculate_An_MPm_g_Trg(
        Fe_MPendUse_g_Trg, Scrf_MPUse_g_Trg, Ur_MPendUse_g
        )
    Body_NPgain_g = body_comp.calculate_Body_NPgain_g(Body_NPgain)
    Kg_MP_NP_Trg_initial = protein_req.calculate_Kg_MP_NP_Trg_initial(
        animal_input["An_StatePhys"], animal_input["An_Parity_rl"],
        animal_input["An_BW"], an_data["An_BW_empty"],
        animal_input["An_BW_mature"], An_BWmature_empty, MP_NP_efficiency, 
        coeff_dict
        )
    Body_MPUse_g_Trg_initial = protein_req.calculate_Body_MPUse_g_Trg_initial(
        Body_NPgain_g, Kg_MP_NP_Trg_initial
        )
    Gest_MPUse_g_Trg = protein_req.calculate_Gest_MPUse_g_Trg(
        Gest_NPuse_g, coeff_dict
        )
    Mlk_MPUse_g_Trg = protein_req.calculate_Mlk_MPUse_g_Trg(
        Trg_Mlk_NP_g, coeff_dict
        )
    # NOTE This initial protein requirement is the final value in most cases. 
    # There is an adjustment made when An_StatePhys == "Heifer" and 
    # Diff_MPuse_g > 0. Some of the values used to make this adjustment are used
    #  elsewhere so it can"t just be put behind an if statement
    An_MPuse_g_Trg_initial = protein_req.calculate_An_MPuse_g_Trg_initial(
        An_MPm_g_Trg, Body_MPUse_g_Trg_initial, Gest_MPUse_g_Trg, 
        Mlk_MPUse_g_Trg
        )
    An_MEIn_approx = animal.calculate_An_MEIn_approx(
        an_data["An_DEInp"], an_data["An_DENPNCPIn"], an_data["An_DigTPaIn"], 
        Body_NPgain, an_data["An_GasEOut"], coeff_dict
        )
    Min_MPuse_g = protein_req.calculate_Min_MPuse_g(
        animal_input["An_StatePhys"], An_MPuse_g_Trg_initial, 
        animal_input["An_BW"], animal_input["An_BW_mature"], An_MEIn_approx
        )
    Diff_MPuse_g = protein_req.calculate_Diff_MPuse_g(
        Min_MPuse_g, An_MPuse_g_Trg_initial
        )
    Frm_NPgain_g = protein_req.calculate_Frm_NPgain_g(Frm_NPgain)
    Frm_MPUse_g_Trg = protein_req.calculate_Frm_MPUse_g_Trg(
        animal_input["An_StatePhys"], Frm_NPgain_g, Kg_MP_NP_Trg_initial, 
        Diff_MPuse_g
        )
    Kg_MP_NP_Trg = protein_req.calculate_Kg_MP_NP_Trg_heifer_adjustment(
            animal_input["An_StatePhys"], Diff_MPuse_g, Frm_NPgain_g, 
            Frm_MPUse_g_Trg, Kg_MP_NP_Trg_initial
            )
    Rsrv_NPgain_g = protein_req.calculate_Rsrv_NPgain_g(Rsrv_NPgain)
    Rsrv_MPUse_g_Trg = protein_req.calculate_Rsrv_MPUse_g_Trg(
        animal_input["An_StatePhys"], Diff_MPuse_g, Rsrv_NPgain_g, Kg_MP_NP_Trg
        )
    # Recalculate, NOTE can the recalculation be avoided
    Body_MPUse_g_Trg = protein_req.calculate_Body_MPUse_g_Trg(
        animal_input["An_StatePhys"], Diff_MPuse_g, Body_NPgain_g, 
        Body_MPUse_g_Trg_initial, Kg_MP_NP_Trg
        )
    # Recalculate
    An_MPuse_g_Trg = protein_req.calculate_An_MPuse_g_Trg(
        An_MPm_g_Trg, Frm_MPUse_g_Trg, Rsrv_MPUse_g_Trg, Gest_MPUse_g_Trg, 
        Mlk_MPUse_g_Trg
        )
    
    ####################
    # Protein Balance
    ####################
    An_MPBal_g_Trg = protein.calculate_An_MPBal_g_Trg(An_MPIn_g, An_MPuse_g_Trg)
    Xprt_NP_MP_Trg = protein.calculate_Xprt_NP_MP_Trg(
        Scrf_NP_g, Fe_NPend_g, Trg_Mlk_NP_g, Body_NPgain_g, An_MPIn_g, 
        Ur_NPend_g, Gest_MPUse_g_Trg
        )
    Trg_MPIn_req = protein_req.calculate_Trg_MPIn_req(
        Fe_MPendUse_g_Trg, Scrf_MPUse_g_Trg, Ur_MPendUse_g, Body_MPUse_g_Trg, 
        Gest_MPUse_g_Trg, Trg_Mlk_NP_g, coeff_dict
        )
    An_MPavail_Gain_Trg = body_comp.calculate_An_MPavail_Gain_Trg(
        An_MPIn, An_MPuse_g_Trg, Body_MPUse_g_Trg
        )
    Body_NPgain_MPalowTrg_g = body_comp.calculate_Body_NPgain_MPalowTrg_g(
        An_MPavail_Gain_Trg, Kg_MP_NP_Trg)
    Body_CPgain_MPalowTrg_g = body_comp.calculate_Body_CPgain_MPalowTrg_g(
        Body_NPgain_MPalowTrg_g, coeff_dict
        )
    Body_Gain_MPalowTrg_g = body_comp.calculate_Body_Gain_MPalowTrg_g(
        Body_NPgain_MPalowTrg_g, NPGain_FrmGain
        )
    Body_Gain_MPalowTrg = body_comp.calculate_Body_Gain_MPalowTrg(
        Body_Gain_MPalowTrg_g
        )
    Xprt_NP_MP = protein.calculate_Xprt_NP_MP(
        Scrf_NP_g, Fe_NPend_g, Mlk_NP_g, Body_NPgain_g, An_MPIn_g, Ur_NPend_g, 
        Gest_MPUse_g_Trg
        )
    Km_MP_NP = protein.calculate_Km_MP_NP(
        animal_input["An_StatePhys"], Xprt_NP_MP
        )
    Kl_MP_NP = protein.calculate_Kl_MP_NP(Xprt_NP_MP)
    Fe_MPendUse_g = fecal.calculate_Fe_MPendUse_g(Fe_NPend_g, Km_MP_NP)
    Scrf_MPUse_g = protein.calculate_Scrf_MPUse_g(Scrf_NP_g, Km_MP_NP)
    Mlk_MPUse_g = milk.calculate_Mlk_MPUse_g(Mlk_NP_g, Kl_MP_NP)
    An_MPuse_g = protein.calculate_An_MPuse_g(
        Fe_MPendUse_g, Scrf_MPUse_g, Ur_MPendUse_g, Body_MPUse_g_Trg, 
        Gest_MPUse_g_Trg, Mlk_MPUse_g
        )
    An_MPuse = protein.calculate_An_MPuse(An_MPuse_g)
    An_MPBal_g = protein.calculate_An_MPBal_g(An_MPIn_g, An_MPuse_g)
    An_NPuse_g = protein.calculate_An_NPuse_g(
        Scrf_NP_g, Fe_NPend_g, Ur_NPend_g, Mlk_NP_g, Body_NPgain_g, 
        Gest_NPgain_g
        )
    An_MP_NP = protein.calculate_An_MP_NP(An_NPuse_g, An_MPuse_g)
    An_NPxprt_MP = protein.calculate_An_NPxprt_MP(
        An_NPuse_g, Ur_NPend_g, Gest_NPuse_g, An_MPIn_g, Gest_MPUse_g_Trg
        )
    An_CP_NP = protein.calculate_An_CP_NP(An_NPuse_g, an_data["An_CPIn"])
    An_NPBal_g = protein.calculate_An_NPBal_g(An_MPIn_g, An_MP_NP, An_NPuse_g)
    An_NPBal = protein.calculate_An_NPBal(An_NPBal_g)

    ####################
    # Milk Fat
    ####################
    Trg_Mlk_Fat_g = milk.calculate_Trg_Mlk_Fat_g(Trg_Mlk_Fat)
    Mlk_Fatemp_g = milk.calculate_Mlk_Fatemp_g(
        animal_input["An_StatePhys"], An_LactDay_MlkPred, Dt_DMIn,
        diet_data["Dt_FAIn"], diet_data["Dt_DigC160In"],
        diet_data["Dt_DigC183In"], aa_values["Abs_AA_g"]
        )
    Mlk_Fat_g = milk.calculate_Mlk_Fat_g(
        equation_selection["mFat_eqn"], Trg_Mlk_Fat_g, Mlk_Fatemp_g
        )
    Mlk_Fat = milk.calculate_Mlk_Fat(Mlk_Fat_g)

    ####################
    # Milk Production and Milk Energy
    ####################
    Mlk_Prod_comp = milk.calculate_Mlk_Prod_comp(
        animal_input["An_Breed"], Mlk_NP, Mlk_Fat, an_data["An_DEIn"], 
        An_LactDay_MlkPred, animal_input["An_Parity_rl"]
        )
    An_MPavail_Milk_Trg = milk.calculate_An_MPavail_Milk_Trg(
        An_MPIn, An_MPuse_g_Trg, Mlk_MPUse_g_Trg
        )
    Mlk_NP_MPalow_Trg_g = milk.calculate_Mlk_NP_MPalow_Trg_g(
        An_MPavail_Milk_Trg, coeff_dict
        )
    Mlk_Prod_MPalow = milk.calculate_Mlk_Prod_MPalow(
        Mlk_NP_MPalow_Trg_g, animal_input["Trg_MilkTPp"]
        )
    An_MEavail_Milk = milk.calculate_An_MEavail_Milk(
        An_MEIn, An_MEgain, An_MEmUse, Gest_MEuse
        )
    Mlk_Prod_NEalow = milk.calculate_Mlk_Prod_NEalow(
        An_MEavail_Milk, Trg_NEmilk_Milk, coeff_dict
        )
    Mlk_Prod = milk.calculate_Mlk_Prod(
        animal_input["An_StatePhys"], equation_selection["mProd_eqn"], 
        Mlk_Prod_comp, Mlk_Prod_NEalow, Mlk_Prod_MPalow, 
        animal_input["Trg_MilkProd"]
        )
    MlkNP_Milk = milk.calculate_MlkNP_Milk(
        animal_input["An_StatePhys"], Mlk_NP_g, Mlk_Prod
        )
    MlkFat_Milk = milk.calculate_MlkFat_Milk(
        animal_input["An_StatePhys"], Mlk_Fat, Mlk_Prod
        )
    MlkNE_Milk = milk.calculate_MlkNE_Milk(
        MlkFat_Milk, MlkNP_Milk, animal_input["Trg_MilkLacp"]
        )
    Mlk_NEout = milk.calculate_Mlk_NEout(MlkNE_Milk, Mlk_Prod)
    Mlk_MEout = milk.calculate_Mlk_MEout(Mlk_NEout, coeff_dict)
    Trg_NEmilk_DEIn = milk.calculate_Trg_NEmilk_DEIn(
        Trg_Mlk_NEout, an_data["An_DEIn"]
        )
    Mlk_Prod_NEalow_EPcor = milk.calculate_Mlk_Prod_NEalow_EPcor(
        Mlk_Prod_NEalow, animal_input["Trg_MilkFatp"],
        animal_input["Trg_MilkTPp"]
        )
    Mlk_EPcorNEalow_DMIn = milk.calculate_Mlk_EPcorNEalow_DMIn(
        Mlk_Prod_NEalow_EPcor, an_data["An_DMIn"]
        )
    MlkNP_Milk_p = milk.calculate_MlkNP_Milk_p(MlkNP_Milk)
    MlkFat_Milk_p = milk.calculate_MlkFat_Milk_p(MlkFat_Milk)
    Mlk_NE_DE = milk.calculate_Mlk_NE_DE(Mlk_NEout, an_data["An_DEIn"])
    
    ####################
    # Energy Balance
    ####################
    An_MEuse = energy_req.calculate_An_MEuse(
        An_MEmUse, An_MEgain, Gest_MEuse, Mlk_MEout
        )
    An_NEuse = energy_req.calculate_An_NEuse(
        An_NEmUse, An_REgain, Gest_REgain, Mlk_NEout
        )
    Trg_NEuse = energy_req.calculate_Trg_NEuse(
        An_NEmUse, An_REgain, Gest_REgain, Trg_Mlk_NEout
        )
    An_NELuse = energy_req.calculate_An_NELuse(An_MEuse, coeff_dict)
    Trg_NELuse = energy_req.calculate_Trg_NELuse(Trg_MEuse, coeff_dict)
    An_NEprod_GE = energy_req.calculate_An_NEprod_GE(
        An_NEuse, An_NEmUse, an_data["An_GEIn"]
        )
    Trg_NEprod_GE = energy_req.calculate_Trg_NEprod_GE(
        Trg_NEuse, An_NEmUse, an_data["An_GEIn"]
        )
    An_NEmlk_GE = energy_req.calculate_An_NEmlk_GE(
        Mlk_NEout, an_data["An_GEIn"]
        )
    Trg_NEmlk_GE = energy_req.calculate_Trg_NEmlk_GE(
        Trg_Mlk_NEout, an_data["An_GEIn"]
        )
    An_MEbal = energy_req.calculate_An_MEbal(An_MEIn, An_MEuse)
    An_NELbal = energy_req.calculate_An_NELbal(An_MEbal, coeff_dict)
    An_NEbal = energy_req.calculate_An_NEbal(An_NEIn, An_NEuse)
    Trg_MEbal = energy_req.calculate_Trg_MEbal(An_MEIn, Trg_MEuse)
    Trg_NELbal = energy_req.calculate_Trg_NELbal(Trg_MEbal, coeff_dict)
    Trg_NEbal = energy_req.calculate_Trg_NEbal(An_NEIn, Trg_NEuse)
    An_MPuse_MEuse = energy_req.calculate_An_MPuse_MEuse(An_MPuse_g, An_MEuse)
    Trg_MPuse_MEuse = energy_req.calculate_Trg_MPuse_MEuse(
        An_MPuse_g_Trg, An_MEuse
        )
    An_MEavail_Grw = body_comp.calculate_An_MEavail_Grw(
        An_MEIn, An_MEmUse, Gest_MEuse, Mlk_MEout
        )
    Kg_ME_NE = body_comp.calculate_Kg_ME_NE(
        Frm_NEgain, Rsrv_NEgain, Kr_ME_RE, Kf_ME_RE
        )
    Body_Gain_NEalow = body_comp.calculate_Body_Gain_NEalow(
        An_MEavail_Grw, Kg_ME_NE, Body_NEgain_BWgain
        )
    An_BodConcgain_NEalow = body_comp.calculate_An_BodConcgain_NEalow(
        Body_Gain_NEalow, Conc_BWgain
        )
    Body_Fatgain_NEalow = body_comp.calculate_Body_Fatgain_NEalow(
        Body_Gain_NEalow
        )
    Body_NPgain_NEalow = body_comp.calculate_Body_NPgain_NEalow(
        Body_Fatgain_NEalow
        )
    An_Days_BCSdelta1 = body_comp.calculate_An_Days_BCSdelta1(
        BW_BCS, Body_Gain_NEalow
        )

    ####################
    # Nitrogen, Protein and Amino Acid Use
    ####################
    An_NPm_Use = animal.calculate_An_NPm_Use(Scrf_NP_g, Fe_NPend_g, Ur_NPend_g)
    An_CPm_Use = animal.calculate_An_CPm_Use(Scrf_CP_g, Fe_CPend_g, Ur_NPend_g)
    aa_values["Body_AAGain_g"] = aa.calculate_Body_AAGain_g(
        Body_NPgain_g, Body_AA_TP
        )
    Body_EAAGain_g = aa.calculate_Body_EAAGain_g(aa_values["Body_AAGain_g"])
    aa_values["BodyAA_AbsAA"] = aa.calculate_BodyAA_AbsAA(
        aa_values["Body_AAGain_g"], aa_values["Abs_AA_g"]
        )
    An_CPxprt_g = protein.calculate_An_CPxprt_g(
        Scrf_CP_g, Fe_CPend_g, Mlk_CP_g, Body_CPgain_g
        )
    An_NPxprt_g = protein.calculate_An_NPxprt_g(
        Scrf_NP_g, Fe_NPend_g, Mlk_NP_g, Body_NPgain_g
        )
    Trg_NPxprt_g = protein.calculate_Trg_NPxprt_g(
        Scrf_NP_g, Fe_NPend_g, Trg_Mlk_NP_g, Body_NPgain_g
        )
    An_CPprod_g = protein.calculate_An_CPprod_g(
        Mlk_CP_g, Gest_NCPgain_g, Body_CPgain_g
        )
    An_NPprod_g = protein.calculate_An_NPprod_g(
        Mlk_NP_g, Gest_NPgain_g, Body_NPgain_g
        )
    Trg_NPprod_g = protein.calculate_Trg_NPprod_g(
        Trg_Mlk_NP_g, Gest_NPgain_g, Body_NPgain_g
        )
    An_NPprod_MPIn = protein.calculate_An_NPprod_MPIn(An_NPprod_g, An_MPIn_g)
    Trg_NPuse_g = protein.calculate_Trg_NPuse_g(
        Scrf_NP_g, Fe_NPend_g, Ur_NPend_g, Trg_Mlk_NP_g, Body_NPgain_g, 
        Gest_NPgain_g
        )
    An_NCPuse_g = protein.calculate_An_NCPuse_g(
        Scrf_CP_g, Fe_CPend_g, Ur_NPend_g, Mlk_CP_g, Body_CPgain_g, 
        Gest_NCPgain_g
        )
    An_Nprod_g = protein.calculate_An_Nprod_g(
        Gest_NCPgain_g, Body_CPgain_g, Mlk_CP_g
        )
    An_Nprod_NIn = protein.calculate_An_Nprod_NIn(
        An_Nprod_g, an_data["An_NIn_g"]
        )
    An_Nprod_DigNIn = protein.calculate_An_Nprod_DigNIn(
        An_Nprod_g, an_data["An_DigNtIn_g"]
        )
    aa_values["An_AAUse_g"] = aa.calculate_An_AAUse_g(
        aa_values["Gest_AA_g"], aa_values["Mlk_AA_g"], 
        aa_values["Body_AAGain_g"], Scrf_AA_g, Fe_AAMet_g, Ur_AAEnd_g
        )
    An_EAAUse_g = aa.calculate_An_EAAUse_g(aa_values["An_AAUse_g"])
    aa_values["AnAAUse_AbsAA"] = aa.calculate_AnAAUse_AbsAA(
        aa_values["An_AAUse_g"], aa_values["Abs_AA_g"]
        )
    AnEAAUse_AbsEAA = aa.calculate_AnEAAUse_AbsEAA(An_EAAUse_g, Abs_EAA_g)
    aa_values["An_AABal_g"] = aa.calculate_An_AABal_g(
        aa_values["Abs_AA_g"], aa_values["An_AAUse_g"]
        )
    An_EAABal_g = aa.calculate_An_EAABal_g(Abs_EAA_g, An_EAAUse_g)
    Trg_AbsEAA_NPxprtEAA = aa.calculate_Trg_AbsEAA_NPxprtEAA(Trg_AbsAA_NPxprtAA)
    Trg_AbsArg_NPxprtArg = aa.calculate_Trg_AbsArg_NPxprtArg(
        Trg_AbsEAA_NPxprtEAA
        )
    # Add Arg efficiency to the array
    Trg_AbsAA_NPxprtAA = np.insert(Trg_AbsAA_NPxprtAA, 0, Trg_AbsArg_NPxprtArg)
    Trg_AAEff_EAAEff = aa.calculate_Trg_AAEff_EAAEff(
        Trg_AbsAA_NPxprtAA, Trg_AbsEAA_NPxprtEAA
        )
    aa_values["An_AAEff_EAAEff"] = aa.calculate_An_AAEff_EAAEff(
        aa_values["AnAAUse_AbsAA"], AnEAAUse_AbsEAA
        )
    aa_values["Imb_AA"] = aa.calculate_Imb_AA(
        aa_values["An_AAEff_EAAEff"], Trg_AAEff_EAAEff, f_Imb
     )
    Imb_EAA = aa.calculate_Imb_EAA(aa_values["Imb_AA"])
    aa_values["Trg_AAUse_g"] = aa.calculate_Trg_AAUse_g(
        aa_values["Trg_Mlk_AA_g"], Scrf_AA_g, Fe_AAMet_g, Ur_AAEnd_g, 
        aa_values["Gest_AA_g"], aa_values["Body_AAGain_g"]
        )
    Trg_EAAUse_g = aa.calculate_Trg_EAAUse_g(aa_values["Trg_AAUse_g"])
    aa_values["Trg_AbsAA_g"] = aa.calculate_Trg_AbsAA_g(
        aa_values["Trg_Mlk_AA_g"], Scrf_AA_g, Fe_AAMet_g, Trg_AbsAA_NPxprtAA,
        Ur_AAEnd_g, aa_values["Gest_AA_g"], aa_values["Body_AAGain_g"],
        Kg_MP_NP_Trg, coeff_dict
        )
    Trg_AbsEAA_g = aa.calculate_Trg_AbsEAA_g(aa_values["Trg_AbsAA_g"])
    Trg_MlkEAA_AbsEAA = aa.calculate_Trg_MlkEAA_AbsEAA(
        Mlk_EAA_g, aa_values["Mlk_AA_g"], Trg_AbsEAA_g
        )
    MlkNP_DEInp = milk.calculate_MlkNP_DEInp(an_data["An_DEInp"], mPrt_coeff)
    MlkNP_NDF = milk.calculate_MlkNP_NDF(an_data["An_DigNDF"], mPrt_coeff)
    aa_values["MlkNP_AbsAA"] = milk.calculate_MlkNP_AbsAA(
        aa_values["Abs_AA_g"], aa_values["mPrt_k_AA"]
        )
    MlkNP_AbsEAA = milk.calculate_MlkNP_AbsEAA(Abs_EAA2b_g, mPrt_k_EAA2)
    MlkNP_AbsNEAA = milk.calculate_MlkNP_AbsNEAA(Abs_neAA_g, mPrt_coeff)
    MlkNP_AbsOthAA = milk.calculate_MlkNP_AbsOthAA(Abs_OthAA_g, mPrt_coeff)
    aa_values["AnNPxAA_AbsAA"] = aa.calculate_AnNPxAA_AbsAA(
        aa_values["An_AAUse_g"], aa_values["Gest_AA_g"], Ur_AAEnd_g,
        aa_values["Abs_AA_g"], coeff_dict
        )
    AnNPxEAA_AbsEAA = aa.calculate_AnNPxEAA_AbsEAA(
        An_EAAUse_g, Gest_EAA_g, Ur_EAAEnd_g, Abs_EAA_g, coeff_dict
        )
    aa_values["AnNPxAAUser_AbsAA"] = aa.calculate_AnNPxAAUser_AbsAA(
        aa_values["Trg_AAUse_g"], aa_values["Gest_AA_g"], Ur_AAEnd_g,
        aa_values["Abs_AA_g"], coeff_dict
        )
    AnNPxEAAUser_AbsEAA = aa.calculate_AnNPxEAAUser_AbsEAA(
        Trg_EAAUse_g, Gest_EAA_g, Ur_EAAEnd_g, Abs_EAA_g, coeff_dict
        )
    
    ####################
    # Mineral Requirements
    ####################
    ### Calcium ###
    Ca_Mlk = micro_req.calculate_Ca_Mlk(animal_input["An_Breed"])
    Fe_Ca_m = micro_req.calculate_Fe_Ca_m(an_data["An_DMIn"])
    An_Ca_g = micro_req.calculate_An_Ca_g(
        animal_input["An_BW_mature"], animal_input["An_BW"], Body_Gain
        )
    An_Ca_y = micro_req.calculate_An_Ca_y(
        animal_input["An_GestDay"], animal_input["An_BW"]
        )
    An_Ca_l = micro_req.calculate_An_Ca_l(
        Mlk_NP_g, Ca_Mlk, animal_input["Trg_MilkProd"], 
        animal_input["Trg_MilkTPp"]
        )
    An_Ca_Clf = micro_req.calculate_An_Ca_Clf(
        an_data["An_BW_empty"], Body_Gain_empty
        )
    An_Ca_req = micro_req.calculate_An_Ca_req(
        animal_input["An_StatePhys"], diet_data["Dt_DMIn_ClfLiq"], An_Ca_Clf, 
        Fe_Ca_m, An_Ca_g, An_Ca_y, An_Ca_l
        )
    An_Ca_bal = micro_req.calculate_An_Ca_bal(diet_data["Abs_CaIn"], An_Ca_req)
    An_Ca_prod = micro_req.calculate_An_Ca_prod(An_Ca_y, An_Ca_l, An_Ca_g)

    ### Phosphorus ###
    Ur_P_m = micro_req.calculate_Ur_P_m(animal_input["An_BW"])
    Fe_P_m = micro_req.calculate_Fe_P_m(
        animal_input["An_Parity_rl"], an_data["An_DMIn"]
        )
    An_P_m = micro_req.calculate_An_P_m(Ur_P_m, Fe_P_m)
    An_P_g = micro_req.calculate_An_P_g(
        animal_input["An_BW_mature"], animal_input["An_BW"], Body_Gain
        )
    An_P_y = micro_req.calculate_An_P_y(
        animal_input["An_GestDay"], animal_input["An_BW"]
        )
    An_P_l = micro_req.calculate_An_P_l(
        animal_input["Trg_MilkProd"], MlkNP_Milk
        )
    An_P_Clf = micro_req.calculate_An_P_Clf(
        an_data["An_BW_empty"], Body_Gain_empty
        )
    An_P_req = micro_req.calculate_An_P_req(
        animal_input["An_StatePhys"], diet_data["Dt_DMIn_ClfLiq"], An_P_Clf, 
        An_P_m, An_P_g, An_P_y, An_P_l
        )
    An_P_bal = micro_req.calculate_An_P_bal(diet_data["Abs_PIn"], An_P_req)
    Fe_P_g = micro_req.calculate_Fe_P_g(
        diet_data["Dt_PIn"], An_P_l, An_P_y, An_P_g, Ur_P_m
        )
    An_P_prod = micro_req.calculate_An_P_prod(An_P_y, An_P_l, An_P_g)

    ### Magnesium ###
    An_Mg_Clf = micro_req.calculate_An_Mg_Clf(
        an_data["An_BW_empty"], Body_Gain_empty
        )
    Ur_Mg_m = micro_req.calculate_Ur_Mg_m(animal_input["An_BW"])
    Fe_Mg_m = micro_req.calculate_Fe_Mg_m(an_data["An_DMIn"])
    An_Mg_m = micro_req.calculate_An_Mg_m(Ur_Mg_m, Fe_Mg_m)
    An_Mg_g = micro_req.calculate_An_Mg_g(Body_Gain)
    An_Mg_y = micro_req.calculate_An_Mg_y(
        animal_input["An_GestDay"], animal_input["An_BW"]
        )
    An_Mg_l = micro_req.calculate_An_Mg_l(animal_input["Trg_MilkProd"])
    An_Mg_req = micro_req.calculate_An_Mg_req(
        animal_input["An_StatePhys"], diet_data["Dt_DMIn_ClfLiq"], An_Mg_Clf, 
        An_Mg_m, An_Mg_g, An_Mg_y, An_Mg_l
        )
    An_Mg_bal = micro_req.calculate_An_Mg_bal(diet_data["Abs_MgIn"], An_Mg_req)
    An_Mg_prod = micro_req.calculate_An_Mg_prod(An_Mg_y, An_Mg_l, An_Mg_g)

    ### Sodium ###
    An_Na_Clf = micro_req.calculate_An_Na_Clf(
        an_data["An_BW_empty"], Body_Gain_empty
        )
    Fe_Na_m = micro_req.calculate_Fe_Na_m(an_data["An_DMIn"])
    An_Na_g = micro_req.calculate_An_Na_g(Body_Gain)
    An_Na_y = micro_req.calculate_An_Na_y(
        animal_input["An_GestDay"], animal_input["An_BW"]
        )
    An_Na_l = micro_req.calculate_An_Na_l(animal_input["Trg_MilkProd"])
    An_Na_req = micro_req.calculate_An_Na_req(
        animal_input["An_StatePhys"], diet_data["Dt_DMIn_ClfLiq"], An_Na_Clf, 
        Fe_Na_m, An_Na_g, An_Na_y, An_Na_l
        )
    An_Na_bal = micro_req.calculate_An_Na_bal(diet_data["Abs_NaIn"], An_Na_req)
    An_Na_prod = micro_req.calculate_An_Na_prod(An_Na_y, An_Na_l, An_Na_g)

    ### Chlorine ###
    An_Cl_Clf = micro_req.calculate_An_Cl_Clf(
        an_data["An_BW_empty"], Body_Gain_empty
        )
    Fe_Cl_m = micro_req.calculate_Fe_Cl_m(an_data["An_DMIn"])
    An_Cl_g = micro_req.calculate_An_Cl_g(Body_Gain)
    An_Cl_y = micro_req.calculate_An_Cl_y(
        animal_input["An_GestDay"], animal_input["An_BW"]
        )
    An_Cl_l = micro_req.calculate_An_Cl_l(animal_input["Trg_MilkProd"])
    An_Cl_req = micro_req.calculate_An_Cl_req(
        animal_input["An_StatePhys"], diet_data["Dt_DMIn_ClfLiq"], An_Cl_Clf, 
        Fe_Cl_m, An_Cl_g, An_Cl_y, An_Cl_l
        )
    An_Cl_bal = micro_req.calculate_An_Cl_bal(diet_data["Abs_ClIn"], An_Cl_req)
    An_Cl_prod = micro_req.calculate_An_Cl_prod(An_Cl_y, An_Cl_l, An_Cl_g)

    ### Potassium ###
    An_K_Clf = micro_req.calculate_An_K_Clf(
        an_data["An_BW_empty"], Body_Gain_empty
        )
    Ur_K_m = micro_req.calculate_Ur_K_m(
        animal_input["Trg_MilkProd"], animal_input["An_BW"]
        )
    Fe_K_m = micro_req.calculate_Fe_K_m(an_data["An_DMIn"])
    An_K_m = micro_req.calculate_An_K_m(Ur_K_m, Fe_K_m)
    An_K_g = micro_req.calculate_An_K_g(Body_Gain)
    An_K_y = micro_req.calculate_An_K_y(
        animal_input["An_GestDay"], animal_input["An_BW"]
        )
    An_K_l = micro_req.calculate_An_K_l(animal_input["Trg_MilkProd"])
    An_K_req = micro_req.calculate_An_K_req(
        animal_input["An_StatePhys"], diet_data["Dt_DMIn_ClfLiq"], An_K_Clf, 
        An_K_m, An_K_g, An_K_y, An_K_l
        )
    An_K_bal = micro_req.calculate_An_K_bal(diet_data["Abs_KIn"], An_K_req)
    An_K_prod = micro_req.calculate_An_K_prod(An_K_y, An_K_l, An_K_g)

    ### Sulphur ###
    An_S_req = micro_req.calculate_An_S_req(an_data["An_DMIn"])
    An_S_bal = micro_req.calculate_An_S_bal(diet_data["Dt_SIn"], An_S_req)

    ### Cobalt ###
    An_Co_req = micro_req.calculate_An_Co_req(an_data["An_DMIn"])
    An_Co_bal = micro_req.calculate_An_Co_bal(diet_data["Abs_CoIn"], An_Co_req)

    ### Copper ###
    An_Cu_Clf = micro_req.calculate_An_Cu_Clf(
        animal_input["An_BW"], Body_Gain_empty
        )
    An_Cu_m = micro_req.calculate_An_Cu_m(animal_input["An_BW"])
    An_Cu_g = micro_req.calculate_An_Cu_g(Body_Gain)
    An_Cu_y = micro_req.calculate_An_Cu_y(
        animal_input["An_GestDay"], animal_input["An_BW"]
        )
    An_Cu_l = micro_req.calculate_An_Cu_l(animal_input["Trg_MilkProd"])
    An_Cu_req = micro_req.calculate_An_Cu_req(
        animal_input["An_StatePhys"], diet_data["Dt_DMIn_ClfLiq"], An_Cu_Clf, 
        An_Cu_m, An_Cu_g, An_Cu_y, An_Cu_l
        )
    An_Cu_bal = micro_req.calculate_An_Cu_bal(diet_data["Abs_CuIn"], An_Cu_req)
    An_Cu_prod = micro_req.calculate_An_Cu_prod(An_Cu_y, An_Cu_l, An_Cu_g)

    ### Iodine ###
    An_I_req = micro_req.calculate_An_I_req(
        animal_input["An_StatePhys"], an_data["An_DMIn"], animal_input["An_BW"],
        animal_input["Trg_MilkProd"]
        )
    An_I_bal = micro_req.calculate_An_I_bal(diet_data["Dt_IIn"], An_I_req)

    ### Iron ###
    An_Fe_Clf = micro_req.calculate_An_Fe_Clf(Body_Gain)
    An_Fe_g = micro_req.calculate_An_Fe_g(Body_Gain)
    An_Fe_y = micro_req.calculate_An_Fe_y(
        animal_input["An_GestDay"], animal_input["An_BW"]
        )
    An_Fe_l = micro_req.calculate_An_Fe_l(animal_input["Trg_MilkProd"])
    An_Fe_req = micro_req.calculate_An_Fe_req(
        animal_input["An_StatePhys"], diet_data["Dt_DMIn_ClfLiq"], An_Fe_Clf, 
        An_Fe_g, An_Fe_y, An_Fe_l
        )
    An_Fe_bal = micro_req.calculate_An_Fe_bal(diet_data["Abs_FeIn"], An_Fe_req)
    An_Fe_prod = micro_req.calculate_An_Fe_prod(An_Fe_y, An_Fe_l, An_Fe_g)

    ### Maganese ###
    An_Mn_Clf = micro_req.calculate_An_Mn_Clf(animal_input["An_BW"], Body_Gain)
    An_Mn_m = micro_req.calculate_An_Mn_m(animal_input["An_BW"])
    An_Mn_g = micro_req.calculate_An_Mn_g(Body_Gain)
    An_Mn_y = micro_req.calculate_An_Mn_y(
        animal_input["An_GestDay"], animal_input["An_BW"]
        )
    An_Mn_l = micro_req.calculate_An_Mn_l(animal_input["Trg_MilkProd"])
    An_Mn_req = micro_req.calculate_An_Mn_req(
        animal_input["An_StatePhys"], diet_data["Dt_DMIn_ClfLiq"], An_Mn_Clf, 
        An_Mn_m, An_Mn_g, An_Mn_y, An_Mn_l
        )
    An_Mn_bal = micro_req.calculate_An_Mn_bal(diet_data["Abs_MnIn"], An_Mn_req)
    An_Mn_prod = micro_req.calculate_An_Mn_prod(An_Mn_y, An_Mn_l, An_Mn_g)

    ### Selenium ###
    An_Se_req = micro_req.calculate_An_Se_req(an_data["An_DMIn"])
    An_Se_bal = micro_req.calculate_An_Se_bal(diet_data["Dt_SeIn"], An_Se_req)

    ### Zinc ###
    An_Zn_Clf = micro_req.calculate_An_Zn_Clf(an_data["An_DMIn"], Body_Gain)
    An_Zn_m = micro_req.calculate_An_Zn_m(an_data["An_DMIn"])
    An_Zn_g = micro_req.calculate_An_Zn_g(Body_Gain)
    An_Zn_y = micro_req.calculate_An_Zn_y(
        animal_input["An_GestDay"], animal_input["An_BW"]
        )
    An_Zn_l = micro_req.calculate_An_Zn_l(animal_input["Trg_MilkProd"])
    An_Zn_req = micro_req.calculate_An_Zn_req(
        animal_input["An_StatePhys"], diet_data["Dt_DMIn_ClfLiq"], An_Zn_Clf, 
        An_Zn_m, An_Zn_g, An_Zn_y, An_Zn_l
        )
    An_Zn_bal = micro_req.calculate_An_Zn_bal(diet_data["Abs_ZnIn"], An_Zn_req)
    An_Zn_prod = micro_req.calculate_An_Zn_prod(An_Zn_y, An_Zn_l, An_Zn_g)

    ### DCAD ###
    An_DCADmeq = micro_req.calculate_An_DCADmeq(
        diet_data["Dt_K"], diet_data["Dt_Na"], diet_data["Dt_Cl"], 
        diet_data["Dt_S"]
        )
    
    ####################
    # Mineral Use Efficiency
    ####################
    Dt_acCa = micro_req.calculate_Dt_acCa(
        diet_data["Abs_CaIn"], diet_data["Dt_CaIn"]
        )
    Dt_acP = micro_req.calculate_Dt_acP(
        diet_data["Abs_PIn"], diet_data["Dt_PIn"]
        )
    Dt_acNa = micro_req.calculate_Dt_acNa(
        diet_data["Abs_NaIn"], diet_data["Dt_NaIn"]
        )
    Dt_acMg = micro_req.calculate_Dt_acMg_final(
        diet_data["Abs_MgIn"], diet_data["Dt_MgIn"]
        )
    Dt_acK = micro_req.calculate_Dt_acK(
        diet_data["Abs_KIn"], diet_data["Dt_KIn"]
        )
    Dt_acCl = micro_req.calculate_Dt_acCl(
        diet_data["Abs_ClIn"], diet_data["Dt_ClIn"]
        )
    Dt_acCo = micro_req.calculate_Dt_acCo(
        diet_data["Abs_CoIn"], diet_data["Dt_CoIn"]
        )
    Dt_acCu = micro_req.calculate_Dt_acCu(
        diet_data["Abs_CuIn"], diet_data["Dt_CuIn"]
        )
    Dt_acFe = micro_req.calculate_Dt_acFe(
        diet_data["Abs_FeIn"], diet_data["Dt_FeIn"]
        )
    Dt_acMn = micro_req.calculate_Dt_acMn(
        diet_data["Abs_MnIn"], diet_data["Dt_MnIn"]
        )
    Dt_acZn = micro_req.calculate_Dt_acZn(
        diet_data["Abs_ZnIn"], diet_data["Dt_ZnIn"]
        )
    CaProd_CaIn = micro_req.calculate_CaProd_CaIn(
        An_Ca_prod, diet_data["Dt_CaIn"]
        )
    PProd_PIn = micro_req.calculate_PProd_PIn(
        An_P_prod, diet_data["Dt_PIn"]
        )
    MgProd_MgIn = micro_req.calculate_MgProd_MgIn(
        An_Mg_prod, diet_data["Dt_MgIn"]
        )
    KProd_KIn = micro_req.calculate_KProd_KIn(
        An_K_prod, diet_data["Dt_KIn"]
        )
    NaProd_NaIn = micro_req.calculate_NaProd_NaIn(
        An_Na_prod, diet_data["Dt_NaIn"]
        )
    ClProd_ClIn = micro_req.calculate_ClProd_ClIn(
        An_Cl_prod, diet_data["Dt_ClIn"]
        )
    CuProd_CuIn = micro_req.calculate_CuProd_CuIn(
        An_Cu_prod, diet_data["Dt_CuIn"]
        )
    FeProd_FeIn = micro_req.calculate_FeProd_FeIn(
        An_Fe_prod, diet_data["Dt_FeIn"]
        )
    MnProd_MnIn = micro_req.calculate_MnProd_MnIn(
        An_Mn_prod, diet_data["Dt_MnIn"]
        )
    ZnProd_ZnIn = micro_req.calculate_ZnProd_ZnIn(
        An_Zn_prod, diet_data["Dt_ZnIn"]
        )
    CaProd_CaAbs = micro_req.calculate_CaProd_CaAbs(
        An_Ca_prod, diet_data["Abs_CaIn"]
        )
    PProd_PAbs = micro_req.calculate_PProd_PAbs(An_P_prod, diet_data["Abs_PIn"])
    MgProd_MgAbs = micro_req.calculate_MgProd_MgAbs(
        An_Mg_prod, diet_data["Abs_MgIn"]
        )
    KProd_KAbs = micro_req.calculate_KProd_KAbs(An_K_prod, diet_data["Abs_KIn"])
    NaProd_NaAbs = micro_req.calculate_NaProd_NaAbs(
        An_Na_prod, diet_data["Abs_NaIn"]
        )
    ClProd_ClAbs = micro_req.calculate_ClProd_ClAbs(
        An_Cl_prod, diet_data["Abs_ClIn"]
        )
    CuProd_CuAbs = micro_req.calculate_CuProd_CuAbs(
        An_Cu_prod, diet_data["Abs_CuIn"]
        )
    FeProd_FeAbs = micro_req.calculate_FeProd_FeAbs(
        An_Fe_prod, diet_data["Abs_FeIn"]
        )
    MnProd_MnAbs = micro_req.calculate_MnProd_MnAbs(
        An_Mn_prod, diet_data["Abs_MnIn"]
        )
    ZnProd_ZnAbs = micro_req.calculate_ZnProd_ZnAbs(
        An_Zn_prod, diet_data["Abs_ZnIn"]
        )
    
    ####################
    # Vitamin Requirements
    ####################
    An_VitA_req = micro_req.calculate_An_VitA_req(
        animal_input["Trg_MilkProd"], animal_input["An_BW"]
        )
    An_VitA_bal = micro_req.calculate_An_VitA_bal(
        diet_data["Dt_VitAIn"], An_VitA_req
        )
    An_VitD_req = micro_req.calculate_An_VitD_req(
        animal_input["Trg_MilkProd"], animal_input["An_BW"]
        )
    An_VitD_bal = micro_req.calculate_An_VitD_bal(
        diet_data["Dt_VitDIn"], An_VitD_req
        )
    An_VitE_req = micro_req.calculate_An_VitE_req(
        animal_input["Trg_MilkProd"], animal_input["An_Parity_rl"], 
        animal_input["An_StatePhys"], animal_input["An_BW"], 
        animal_input["An_GestDay"], An_Preg, diet_data["Dt_PastIn"]
        )
    An_VitE_bal = micro_req.calculate_An_VitE_bal(
        diet_data["Dt_VitEIn"], An_VitE_req
        )

    ####################
    # Required Mineral Density
    ####################
    Dt_CaReq_DMI = micro_req.calculate_Dt_CaReq_DMI(
        An_Ca_req, Dt_acCa, an_data['An_DMIn']
        )
    Dt_PReq_DMI = micro_req.calculate_Dt_PReq_DMI(
        An_P_req, Dt_acP, an_data['An_DMIn']
        )
    Dt_MgReq_DMI = micro_req.calculate_Dt_MgReq_DMI(
        An_Mg_req, Dt_acMg, an_data['An_DMIn']
        )
    Dt_KReq_DMI = micro_req.calculate_Dt_KReq_DMI(
        An_K_req, Dt_acK, an_data['An_DMIn']
        )
    Dt_NaReq_DMI = micro_req.calculate_Dt_NaReq_DMI(
        An_Na_req, Dt_acNa, an_data['An_DMIn']
        )
    Dt_ClReq_DMI = micro_req.calculate_Dt_ClReq_DMI(
        An_Cl_req, Dt_acCl, an_data['An_DMIn']
        )
    Dt_SReq_DMI = micro_req.calculate_Dt_SReq_DMI(
        An_S_req, an_data["An_DMIn"]
        )
    Dt_CoReq_DMI = micro_req.calculate_Dt_CoReq_DMI(
        An_Co_req, an_data['An_DMIn']
        )
    Dt_CuReq_DMI = micro_req.calculate_Dt_CuReq_DMI(
        An_Cu_req, Dt_acCu, an_data['An_DMIn']
        )
    Dt_FeReq_DMI = micro_req.calculate_Dt_FeReq_DMI(
        An_Fe_req, Dt_acFe, an_data['An_DMIn']
        )
    Dt_IReq_DMI = micro_req.calculate_Dt_IReq_DMI(An_I_req, an_data['An_DMIn'])
    Dt_MnReq_DMI = micro_req.calculate_Dt_MnReq_DMI(
        An_Mn_req, Dt_acMn, an_data['An_DMIn']
        )
    Dt_SeReq_DMI = micro_req.calculate_Dt_SeReq_DMI(
        An_Se_req, an_data['An_DMIn']
        )
    Dt_ZnReq_DMI = micro_req.calculate_Dt_ZnReq_DMI(
        An_Zn_req, Dt_acZn, an_data['An_DMIn']
        )
    Dt_VitAReq_DMI = micro_req.calculate_Dt_VitAReq_DMI(
        An_VitA_req, an_data["An_DMIn"]
        )
    Dt_VitDReq_DMI = micro_req.calculate_Dt_VitDReq_DMI(
        An_VitD_req, an_data['An_DMIn']
        )
    Dt_VitEReq_DMI = micro_req.calculate_Dt_VitEReq_DMI(
        An_VitE_req, an_data['An_DMIn']
        )

    ####################
    # Water Intake
    ####################
    An_WaIn = water.calculate_An_WaIn(
        animal_input["An_StatePhys"], Dt_DMIn, diet_data["Dt_DM"], 
        diet_data["Dt_Na"], diet_data["Dt_K"], diet_data["Dt_CP"], 
        animal_input["Env_TempCurr"]
        )

    ####################
    # Methane Production
    ####################
    CH4out_g = methane.calculate_CH4out_g(an_data["An_GasEOut"], coeff_dict)
    CH4out_L = methane.calculate_CH4out_L(CH4out_g, coeff_dict)
    if animal_input["An_StatePhys"] == "Lactating Cow":
        CH4g_Milk = methane.calculate_CH4g_Milk(CH4out_g, Mlk_Prod)
        CH4L_Milk = methane.calculate_CH4L_Milk(CH4out_L, Mlk_Prod)
    else:
        CH4g_Milk = 0
        CH4L_Milk = 0

    ####################
    # Manure Loss
    ####################
    Man_out = manure.calculate_Man_out(
        animal_input["An_StatePhys"], an_data["An_DMIn"], diet_data["Dt_K"]
        )
    if animal_input["An_StatePhys"] == "Lactating Cow":
        Man_Milk = manure.calculate_Man_Milk(Man_out, Mlk_Prod)
    else:
        Man_Milk = 0
    Man_VolSld = manure.calculate_Man_VolSld(
        Dt_DMIn, infusion_data["InfRum_DMIn"], 
        infusion_data["InfSI_DMIn"], an_data["An_NDF"], an_data["An_CP"]
        )
    Man_VolSld2 = manure.calculate_Man_VolSld2(
        Fe_OM, diet_data["Dt_LgIn"], Ur_Nout_g
        )
    if animal_input["An_StatePhys"] == "Lactating Cow":
        VolSlds_Milk = manure.calculate_VolSlds_Milk(Man_VolSld, Mlk_Prod)
        VolSlds_Milk2 = manure.calculate_VolSlds_Milk2(Man_VolSld2, Mlk_Prod)
    else:
        VolSlds_Milk = 0
        VolSlds_Milk2 = 0
    VolSlds2_Milk = manure.calculate_VolSlds2_Milk(Man_VolSld2, Mlk_Prod)
    Man_Nout_g = manure.calculate_Man_Nout_g(Ur_Nout_g, Fe_N_g, Scrf_N_g)
    Man_Nout2_g = manure.calculate_Man_Nout2_g(an_data["An_NIn_g"], An_Nprod_g)
    ManN_Milk = manure.calculate_ManN_Milk(Man_Nout_g, Mlk_Prod)
    Man_Ca_out = manure.calculate_Man_Ca_out(diet_data["Dt_CaIn"], An_Ca_prod)
    Man_P_out = manure.calculate_Man_P_out(diet_data["Dt_PIn"], An_P_prod)
    Man_Mg_out = manure.calculate_Man_Mg_out(diet_data["Dt_MgIn"], An_Mg_prod)
    Man_K_out = manure.calculate_Man_K_out(diet_data["Dt_KIn"], An_K_prod)
    Man_Na_out = manure.calculate_Man_Na_out(diet_data["Dt_NaIn"], An_Na_prod)
    Man_Cl_out = manure.calculate_Man_Cl_out(diet_data["Dt_ClIn"], An_Cl_prod)
    Man_MacMin_out = manure.calculate_Man_MacMin_out(
        Man_Ca_out, Man_P_out, Man_Mg_out, Man_K_out, Man_Na_out, Man_Cl_out
        )
    Man_Cu_out = manure.calculate_Man_Cu_out(diet_data["Dt_CuIn"], An_Cu_prod)
    Man_Fe_out = manure.calculate_Man_Fe_out(diet_data["Dt_FeIn"], An_Fe_prod)
    Man_Mn_out = manure.calculate_Man_Mn_out(diet_data["Dt_MnIn"], An_Mn_prod)
    Man_Zn_out = manure.calculate_Man_Zn_out(diet_data["Dt_ZnIn"], An_Zn_prod)
    Man_MicMin_out = manure.calculate_Man_MicMin_out(
        Man_Cu_out, Man_Fe_out, Man_Mn_out, Man_Zn_out
        )
    Man_Min_out_g = manure.calculate_Man_Min_out_g(
        Man_MacMin_out, Man_MicMin_out
        )
    Man_Wa_out = manure.calculate_Man_Wa_out(
        animal_input['An_StatePhys'], Man_out, Fe_OM, Ur_Nout_g, Man_Min_out_g
        )
    if animal_input['An_StatePhys'] != "Calf":
        An_Wa_Insens = water.calculate_An_Wa_Insens(
            An_WaIn, Mlk_Prod, Man_Wa_out
            )
    else:
        An_Wa_Insens = 0
        
    if animal_input['An_StatePhys'] == "Lactating Cow":
        WaIn_Milk = water.calculate_WaIn_Milk(An_WaIn, Mlk_Prod)
        ManWa_Milk = manure.calculate_ManWa_Milk(Man_Wa_out, Mlk_Prod)
    else:
        WaIn_Milk = 0
        ManWa_Milk = 0

    #####################
    # Values for Reports
    #####################
    percent_first_parity = report.calculate_percent_first_parity(
        animal_input["An_Parity_rl"]
        )
    if animal_input["An_StatePhys"] == "Heifer":
        age_first_calving = report.calculate_age_first_calving(
            animal_input["An_AgeConcept1st"]
            )
    milk_lactose_percent = report.calculate_milk_lactose_percent(
        animal_input["Trg_MilkProd"], animal_input["Trg_MilkLacp"]
        )
    dmi_percent_bodyweight = report.calculate_dmi_percent_bodyweight(An_DMIn_BW)
    adf_per_ndf = report.calculate_adf_per_ndf(
        an_data["An_ADF"], an_data["An_NDF"]
        )
    digestable_rup = report.calculate_digestable_rup(an_data["An_idRUP"])
    Fd_AFIn_sum = report.calculate_Fd_AFIn_sum(feed_data["Fd_AFInp"])
    Fd_DMIn_sum = report.calculate_Fd_DMIn_sum(feed_data["Fd_DMInp"])
    Fe_DE_GE_percent = report.calculate_Fe_DE_GE_percent(Fe_DE_GE)
    An_DE_GE_percent = report.calculate_An_DE_GE_percent(an_data["An_DE_GE"])
    UrDE_GEIn_percent = report.calculate_UrDE_GEIn_percent(UrDE_GEIn)
    GasE_GEIn_percent = report.calculate_GasE_GEIn_percent(an_data["GasE_GEIn"])
    An_ME_GE_percent = report.calculate_An_ME_GE_percent(An_ME_GE)
    An_NE_GE_percent = report.calculate_An_NE_GE_percent(An_NE_GE)
    UrDE_DEIn_percent = report.calculate_UrDE_DEIn_percent(UrDE_DEIn)
    GasE_DEIn_percent = report.calculate_GasE_DEIn_percent(an_data["GasE_DEIn"])
    An_ME_DE_percent = report.calculate_An_ME_DE_percent(An_ME_DE)
    An_NE_DE_percent = report.calculate_An_NE_DE_percent(An_NE_DE)
    An_NE_ME_percent = report.calculate_An_NE_ME_percent(An_NE_ME)
    An_DEIn_percent = report.calculate_An_DEIn_percent(an_data["An_DEIn"])
    An_MEIn_percent = report.calculate_An_MEIn_percent(An_MEIn)
    Dt_C120In_g = report.calculate_Dt_C120In_g(diet_data["Dt_C120In"])
    Dt_C140In_g = report.calculate_Dt_C140In_g(diet_data["Dt_C140In"])
    Dt_C160In_g = report.calculate_Dt_C160In_g(diet_data["Dt_C160In"])
    Dt_C161In_g = report.calculate_Dt_C161In_g(diet_data["Dt_C161In"])
    Dt_C180In_g = report.calculate_Dt_C180In_g(diet_data["Dt_C180In"])
    Dt_C181tIn_g = report.calculate_Dt_C181tIn_g(diet_data["Dt_C181tIn"])
    Dt_C181cIn_g = report.calculate_Dt_C181cIn_g(diet_data["Dt_C181cIn"])
    Dt_C182In_g = report.calculate_Dt_C182In_g(diet_data["Dt_C182In"])
    Dt_C183In_g = report.calculate_Dt_C183In_g(diet_data["Dt_C183In"])
    Dt_OtherFAIn_g = report.calculate_Dt_OtherFAIn_g(diet_data["Dt_OtherFAIn"])
    Dt_FAIn_g = report.calculate_Dt_FAIn_g(diet_data["Dt_FAIn"])
    Dt_SatFAIn_g = report.calculate_Dt_SatFAIn_g(diet_data["Dt_SatFAIn"])
    Dt_UFAIn_g = report.calculate_Dt_UFAIn_g(diet_data["Dt_UFAIn"])
    Dt_MUFAIn_g = report.calculate_Dt_MUFAIn_g(diet_data["Dt_MUFAIn"])
    Dt_PUFAIn_g = report.calculate_Dt_PUFAIn_g(diet_data["Dt_PUFAIn"])
    Dt_DigFAIn_g = report.calculate_Dt_DigFAIn_g(diet_data["Dt_DigFAIn"])
    An_RDPbal_kg = report.calculate_An_RDPbal_kg(An_RDPbal_g)
    MP_from_body = report.calculate_MP_from_body(Body_MPUse_g_Trg)
    An_BW_centered = report.calculate_An_BW_centered(animal_input["An_BW"])
    An_DigNDF_centered = report.calculate_An_DigNDF_centered(
        an_data["An_DigNDF"]
        )
    An_BW_protein = report.calculate_An_BW_protein(
        animal_input["An_BW"], mPrt_coeff
        )
    Dt_acCa_per_100g = report.calculate_Dt_acCa_per_100g(Dt_acCa)
    Dt_acP_per_100g = report.calculate_Dt_acP_per_100g(Dt_acP)
    Dt_acMg_per_100g = report.calculate_Dt_acMg_per_100g(Dt_acMg)
    Dt_acCl_per_100g = report.calculate_Dt_acCl_per_100g(Dt_acCl)
    Dt_acK_per_100g = report.calculate_Dt_acK_per_100g(Dt_acK)
    Dt_acNa_per_100g = report.calculate_Dt_acNa_per_100g(Dt_acNa)
    Dt_acCo_per_100g = report.calculate_Dt_acCo_per_100g(Dt_acCo)
    Dt_acCu_per_100g = report.calculate_Dt_acCu_per_100g(Dt_acCu)
    Dt_acFe_per_100g = report.calculate_Dt_acFe_per_100g(Dt_acFe)
    Dt_acMn_per_100g = report.calculate_Dt_acMn_per_100g(Dt_acMn)
    Dt_acZn_per_100g = report.calculate_Dt_acZn_per_100g(Dt_acZn)
    An_MPuse_kg_Trg = report.calculate_An_MPuse_kg_Trg(An_MPuse_g_Trg)
    Dt_ForNDFIn_percNDF = report.calculate_Dt_ForNDFIn_percNDF(
        diet_data["Dt_ForNDFIn"], diet_data["Dt_NDFIn"]
        )
    Kb_LateGest_DMIn = dmi.calculate_Kb_LateGest_DMIn(diet_data["Dt_NDF"])

    ####################
    # Capture Outputs
    ####################
    locals_dict = locals()
    model_output = ModelOutput(locals_input=locals_dict)
    return model_output
