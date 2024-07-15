import numpy as np
import pandas as pd

import nasem_dairy.NASEM_equations.amino_acid_equations as AA
import nasem_dairy.NASEM_equations.animal_equations as animal
import nasem_dairy.NASEM_equations.body_composition_equations as body_comp
import nasem_dairy.NASEM_equations.coefficient_adjustment as coeff_adjust
import nasem_dairy.NASEM_equations.DMI_equations as DMI
import nasem_dairy.NASEM_equations.energy_requirement_equations as energy
import nasem_dairy.NASEM_equations.fecal_equations as fecal
import nasem_dairy.NASEM_equations.gestation_equations as gestation
import nasem_dairy.NASEM_equations.infusion_equations as infusion
import nasem_dairy.NASEM_equations.manure_equations as manure
import nasem_dairy.NASEM_equations.methane_equations as methane
import nasem_dairy.NASEM_equations.microbial_protein_equations as micp
import nasem_dairy.NASEM_equations.micronutrient_requirement_equations as micro
import nasem_dairy.NASEM_equations.milk_equations as milk
import nasem_dairy.NASEM_equations.nutrient_intakes as diet
import nasem_dairy.NASEM_equations.protein_equations as protein
import nasem_dairy.NASEM_equations.protein_requirement_equations as protein_req
import nasem_dairy.NASEM_equations.rumen_equations as rumen
import nasem_dairy.NASEM_equations.unused_equations as unused
import nasem_dairy.NASEM_equations.urine_equations as urine
import nasem_dairy.NASEM_equations.water_equations as water

import nasem_dairy.ration_balancer.constants as constants
import nasem_dairy.ration_balancer.input_validation as validate
import nasem_dairy.ration_balancer.ModelOutput as output
import nasem_dairy.ration_balancer.ration_balancer_functions as ration_funcs

def execute_model(user_diet: pd.DataFrame,
                  animal_input: dict,
                  equation_selection: dict,
                  feed_library_df: pd.DataFrame,
                  coeff_dict: dict = constants.coeff_dict,
                  infusion_input: dict = constants.infusion_dict,
                  MP_NP_efficiency_input: dict = constants.MP_NP_efficiency_dict,
                  mPrt_coeff_list: list = constants.mPrt_coeff_list,
                  f_Imb: np.array = constants.f_Imb
) -> output.ModelOutput:
    """
    Run the NASEM (National Academies of Sciences, Engineering, and Medicine) Nutrient Requirements of Dairy Cattle model.

    Parameters
    ----------
    user_diet : pd.DataFrame
        DataFrame containing user-defined diet composition in kg of feed ingredient. Expects two columns, 'Feedstuff' as a string with the name from the feed library and 'kg_user' as a float with the kg of the ingredient to feed.
    animal_input : dict
        Dictionary containing animal-specific input values.
    equation_selection : dict
        Dictionary containing equation selection criteria.
    feed_library_df : pd.DataFrame
        DataFrame containing the feed library data.
    coeff_dict : dict, optional
        Dictionary containing coefficients for the model, by default `nd.coeff_dict`.
    infusion_input : dict, optional
        Dictionary containing infusion input data, by default `nd.infusion_dict`.
    MP_NP_efficiency_input : dict, optional
        Dictionary containing amino acid conversion efficiencies, by default `nd.MP_NP_efficiency_dict`.

    Returns
    -------
    Multiple
        Currently returns animal_input, diet_info, equation_selection, diet_data, AA_values, infusion_data, An_data, model_out_dict
        To be updated

    Notes
    -----
    - user_diet, animal_input an equation_selection can be generated from a CSV file using nd.read_csv_input
    - The default feed_library_df can be read from NASEM_feed_library.csv
    
    Examples
    --------
    Run the NASEM dairy model with user-defined inputs:

    ```python
    import nasem_dairy as nd
    nd.dev_run_NASEM_model(
        user_diet=user_diet_df,
        animal_input=animal_input_dict,
        equation_selection=equation_selection_dict,
        feed_library_df=feed_library_df
    )
    ```
    """
    ########################################
    # Step 1: Read User Input
    ########################################
    # prevent mutable changes outside of expected scope (especially for Shiny):
    user_diet = validate.validate_user_diet(user_diet.copy())
    animal_input = validate.validate_animal_input(animal_input.copy())
    equation_selection = validate.validate_equation_selection(
        equation_selection.copy()
        )
    feed_library_df = validate.validate_feed_library_df(feed_library_df.copy(),
                                                        user_diet.copy())
    coeff_dict = validate.validate_coeff_dict(coeff_dict.copy())
    infusion_input = validate.validate_infusion_input(infusion_input.copy())
    MP_NP_efficiency_input = validate.validate_MP_NP_efficiency_input(
        MP_NP_efficiency_input.copy()
        )
    mPrt_coeff_list = validate.validate_mPrt_coeff_list(mPrt_coeff_list.copy())
    f_Imb = validate.validate_f_Imb(f_Imb.copy())
    # Adjust value of mPrt_eqn when used to index mPrt_coeff_list as the indexing 
    # in R and Python use different starting values. Use max to prevent negatives
    mPrt_coeff = mPrt_coeff_list[max(0, equation_selection["mPrt_eqn"] - 1)]  
    AA_list = [
        'Arg', 'His', 'Ile', 'Leu', 'Lys', 'Met', 'Phe', 'Thr', 'Trp', 'Val'
    ]
    Trg_AbsAA_NPxprtAA = np.array([
        MP_NP_efficiency_input[f"Trg_Abs{AA}_NP{AA}"]
        for AA in AA_list
        if AA != "Arg"
    ])

    # Calculate additional physiology values
    animal_input['An_PrePartDay'] = (animal_input['An_GestDay'] - 
                                     animal_input['An_GestLength'])
    animal_input['An_PrePartWk'] = animal_input['An_PrePartDay'] / 7

    animal_input['An_PostPartDay'] = gestation.calculate_An_PostPartDay(
        animal_input['An_LactDay']
        )
    # Check equation_selection to make sure they are integers.
    # This is especially important for Shiny, which may return strings
    # It's important they are correct for if statements below.
    equation_selection_in = equation_selection.copy()
    equation_selection = {}

    for key, value in equation_selection_in.items():
        try:
            num_value = int(value)
            equation_selection[key] = num_value
        except ValueError:
            print(f"Unable to convert '{value}' to an integer for key '{key}'")
    del (equation_selection_in)

    Scrf_CP_g = protein.calculate_Scrf_CP_g(animal_input['An_StatePhys'],
                                            animal_input['An_BW']
                                            )
    CPGain_FrmGain = body_comp.calculate_CPGain_FrmGain(
        animal_input['An_BW'], animal_input['An_BW_mature']
        )
    NPGain_FrmGain = body_comp.calculate_NPGain_FrmGain(
        CPGain_FrmGain, coeff_dict
        )
    Frm_Gain = body_comp.calculate_Frm_Gain(animal_input['Trg_FrmGain'])
    Rsrv_Gain = body_comp.calculate_Rsrv_Gain(animal_input['Trg_RsrvGain'])
    Rsrv_Gain_empty = body_comp.calculate_Rsrv_Gain_empty(Rsrv_Gain)
    NPGain_RsrvGain = body_comp.calculate_NPGain_RsrvGain(coeff_dict)
    Rsrv_NPgain = body_comp.calculate_Rsrv_NPgain(
        NPGain_RsrvGain, Rsrv_Gain_empty
        )
    coeff_dict['LCT'] = coeff_adjust.adjust_LCT(animal_input['An_AgeDay'])
    animal_input['Trg_BWgain'] = body_comp.calculate_Trg_BWgain(
        animal_input['Trg_FrmGain'], animal_input['Trg_RsrvGain']
        )
    animal_input['Trg_BWgain_g'] = body_comp.calculate_Trg_BWgain_g(
        animal_input['Trg_BWgain']
        )

    # if animal_input['An_StatePhys'] != 'Lactating Cow':
    #     animal_input['Trg_MilkProd'] = None

    ########################################
    # Step 2: DMI Equations
    ########################################
    # Prepare diet information
    ########
    # retrieve user's feeds from feed library
    feed_data = ration_funcs.get_feed_rows_feedlibrary(
        feeds_to_get=user_diet['Feedstuff'].tolist(),
        feed_lib_df=feed_library_df)

    # Calculate Fd_DMInp (percentage inclusion as sum of kg_user column)
    # Then, use the percentages to calculate the DMIn for each ingredient, and 
    # merge feed data on
    diet_info_initial = (user_diet.assign(
        Fd_DMInp=lambda df: df['kg_user'] / df['kg_user'].sum(),
        Fd_DMIn=lambda df: df['Fd_DMInp'] * animal_input['DMI'],
        )
        .merge(feed_data, how='left', on='Feedstuff')
       )


    # Add Fd_DNDF48 column, need to add to the database
    # diet_info_initial['Fd_DNDF48'] = 0
    
    
    ########
    # pre calculations for DMI:
    ########
    diet_info_for_DMI = (diet_info_initial.assign(
            Fd_For=lambda df: diet.calculate_Fd_For(df['Fd_Conc']),
            Fd_ForNDF=lambda df: diet.calculate_Fd_ForNDF(
                df['Fd_NDF'], df['Fd_Conc'])
        )
    )
    # # Need to precalculate Dt_NDF for DMI predicitons, this will be based on 
    # the user entered DMI (animal_input['DMI])
    Dt_ADF = (diet_info_for_DMI['Fd_ADF'] * diet_info_for_DMI['Fd_DMInp']).sum()
    Dt_NDF = (diet_info_for_DMI['Fd_NDF'] * diet_info_for_DMI['Fd_DMInp']).sum()
    #Dt_For = (diet_info_initial['Fd_For'] * diet_info_initial['Fd_DMInp']).sum()

    # for eqn 9:
    Dt_ForNDF = (diet_info_for_DMI['Fd_ForNDF'] * diet_info_for_DMI['Fd_DMInp']).sum()
    Fd_DNDF48 = diet.calculate_Fd_DNDF48(
        diet_info_for_DMI['Fd_Conc'],
        diet_info_for_DMI['Fd_DNDF48'])
    Dt_ForDNDF48 = diet.calculate_Dt_ForDNDF48(
        diet_info_for_DMI['Fd_DMInp'], 
        diet_info_for_DMI['Fd_Conc'], 
        diet_info_for_DMI['Fd_NDF'], 
        Fd_DNDF48)
    Dt_ForDNDF48_ForNDF = diet.calculate_Dt_ForDNDF48_ForNDF(Dt_ForDNDF48, Dt_ForNDF)

    # Calculate Target milk net energy
    Trg_NEmilk_Milk = milk.calculate_Trg_NEmilk_Milk(
        animal_input['Trg_MilkTPp'], animal_input['Trg_MilkFatp'], 
        animal_input['Trg_MilkLacp']
        )

    # Predict DMI for heifers
    Kb_LateGest_DMIn = DMI.calculate_Kb_LateGest_DMIn(Dt_NDF)
    An_PrePartWklim = DMI.calculate_An_PrePartWklim(
        animal_input['An_PrePartWk']
        )
    An_PrePartWkDurat = An_PrePartWklim * 2
    Trg_NEmilkOut = energy.calculate_Trg_NEmilkOut(
        Trg_NEmilk_Milk, animal_input['Trg_MilkProd']
        )

    ####################
    # Equation selection
    ####################

    if equation_selection['DMIn_eqn'] == 0:
        # print('Using user input DMI')
        pass

    # Predict DMI for lactating cow
    elif equation_selection['DMIn_eqn'] == 8:
        # print("using DMIn_eqn: 8")
        animal_input['DMI'] = DMI.calculate_Dt_DMIn_Lact1(
            animal_input['An_BW'], animal_input['An_BCS'], 
            animal_input['An_LactDay'], animal_input['An_Parity_rl'], 
            Trg_NEmilkOut
            )
    elif equation_selection['DMIn_eqn'] == 9:
        animal_input['DMI'] = DMI.calculate_Dt_DMIn_Lact2(
            Dt_ForNDF, Dt_ADF, Dt_NDF, Dt_ForDNDF48_ForNDF,
            animal_input['Trg_MilkProd']
        )

    # elif equation_selection['DMIn_eqn'] == 1:


    # Individual Heifer DMI Predictions
    elif equation_selection['DMIn_eqn'] in [2, 3, 4, 5, 6, 7]:
        Dt_DMIn_BW_LateGest_i = DMI.calculate_Dt_DMIn_BW_LateGest_i(
            An_PrePartWklim, Kb_LateGest_DMIn, coeff_dict
            )
        # All the individual DMI predictions require this value
        Dt_DMIn_Heif_LateGestInd = DMI.calculate_Dt_DMIn_Heif_LateGestInd(
            animal_input['An_BW'], Dt_DMIn_BW_LateGest_i
            )
        if equation_selection['DMIn_eqn'] == 2:
            if animal_input['An_PrePartWk'] > An_PrePartWkDurat:
                animal_input['DMI'] = min(
                    DMI.calculate_Dt_DMIn_Heif_NRCa(
                        animal_input['An_BW'],animal_input['An_BW_mature']
                        ),
                    Dt_DMIn_Heif_LateGestInd)
            else:
                animal_input['DMI'] = DMI.calculate_Dt_DMIn_Heif_NRCa(
                    animal_input['An_BW'], animal_input['An_BW_mature']
                    )
        if equation_selection['DMIn_eqn'] == 3:
            if animal_input['An_PrePartWk'] > An_PrePartWkDurat:
                animal_input['DMI'] = min(
                    DMI.calculate_Dt_DMIn_Heif_NRCad(
                        animal_input['An_BW'], animal_input['An_BW_mature'], 
                        Dt_NDF
                        ),
                    Dt_DMIn_Heif_LateGestInd)
            else:
                animal_input['DMI'] = DMI.calculate_Dt_DMIn_Heif_NRCad(
                    animal_input['An_BW'], animal_input['An_BW_mature'], Dt_NDF
                    )
        if equation_selection['DMIn_eqn'] == 4:
            if animal_input['An_PrePartWk'] > An_PrePartWkDurat:
                animal_input['DMI'] = min(
                    DMI.calculate_Dt_DMIn_Heif_H1(animal_input['An_BW']),
                    Dt_DMIn_Heif_LateGestInd)
            else:
                animal_input['DMI'] = DMI.calculate_Dt_DMIn_Heif_H1(
                    animal_input['An_BW']
                    )
        if equation_selection['DMIn_eqn'] == 5:
            Dt_NDFdev_DMI = DMI.calculate_Dt_NDFdev_DMI(
                animal_input['An_BW'], Dt_NDF
                )
            if animal_input['An_PrePartWk'] > An_PrePartWkDurat:
                animal_input['DMI'] = min(
                    DMI.calculate_Dt_DMIn_Heif_H2(
                        animal_input['An_BW'], Dt_NDFdev_DMI),
                    Dt_DMIn_Heif_LateGestInd)
            else:
                animal_input['DMI'] = DMI.calculate_Dt_DMIn_Heif_H2(
                    animal_input['An_BW'], Dt_NDFdev_DMI
                    )
        if equation_selection['DMIn_eqn'] == 6:
            if animal_input['An_PrePartWk'] > An_PrePartWkDurat:
                animal_input['DMI'] = min(
                    DMI.calculate_Dt_DMIn_Heif_HJ1(animal_input['An_BW']),
                    Dt_DMIn_Heif_LateGestInd)
            else:
                animal_input['DMI'] = DMI.calculate_Dt_DMIn_Heif_HJ1(
                    animal_input['An_BW']
                    )
        if equation_selection['DMIn_eqn'] == 7:
            Dt_NDFdev_DMI = DMI.calculate_Dt_NDFdev_DMI(
                animal_input['An_BW'], Dt_NDF
                )
            if animal_input['An_PrePartWk'] > An_PrePartWkDurat:
                animal_input['DMI'] = min(
                    DMI.calculate_Dt_DMIn_Heif_HJ2(
                        animal_input['An_BW'], Dt_NDFdev_DMI),
                    Dt_DMIn_Heif_LateGestInd)
            else:
                animal_input['DMI'] = DMI.calculate_Dt_DMIn_Heif_HJ2(
                    animal_input['An_BW'], Dt_NDFdev_DMI
                    )
    # Group Heifer DMI Predictions
    elif equation_selection['DMIn_eqn'] in [12, 13, 14, 15, 16, 17]:
        Dt_DMIn_BW_LateGest_p = DMI.calculate_Dt_DMIn_BW_LateGest_p(
            An_PrePartWkDurat, Kb_LateGest_DMIn, coeff_dict
            )
        # All group DMI predicitons require this value
        Dt_DMIn_Heif_LateGestPen = DMI.calculate_Dt_DMIn_Heif_LateGestPen(
            animal_input['An_BW'], Dt_DMIn_BW_LateGest_p
            )
        if equation_selection['DMIn_eqn'] == 12:
            if animal_input['An_PrePartWk'] > An_PrePartWkDurat:
                animal_input['DMI'] = min(
                    DMI.calculate_Dt_DMIn_Heif_NRCa(
                        animal_input['An_BW'], animal_input['An_BW_mature']),
                    Dt_DMIn_Heif_LateGestPen)
            else:
                animal_input['DMI'] = DMI.calculate_Dt_DMIn_Heif_NRCa(
                    animal_input['An_BW'], animal_input['An_BW_mature']
                    )
        if equation_selection['DMIn_eqn'] == 13:
            if animal_input['An_PrePartWk'] > An_PrePartWkDurat:
                animal_input['DMI'] = min(
                    DMI.calculate_Dt_DMIn_Heif_NRCad(
                        animal_input['An_BW'], animal_input['An_BW_mature'], 
                        Dt_NDF),
                    Dt_DMIn_Heif_LateGestPen)
            else:
                animal_input['DMI'] = DMI.calculate_Dt_DMIn_Heif_NRCad(
                    animal_input['An_BW'], animal_input['An_BW_mature'], Dt_NDF
                    )
        if equation_selection['DMIn_eqn'] == 14:
            if animal_input['An_PrePartWk'] > An_PrePartWkDurat:
                animal_input['DMI'] = min(
                    DMI.calculate_Dt_DMIn_Heif_H1(animal_input['An_BW']),
                    Dt_DMIn_Heif_LateGestPen)
            else:
                animal_input['DMI'] = DMI.calculate_Dt_DMIn_Heif_H1(
                    animal_input['An_BW']
                    )
        if equation_selection['DMIn_eqn'] == 15:
            Dt_NDFdev_DMI = DMI.calculate_Dt_NDFdev_DMI(
                animal_input['An_BW'], Dt_NDF
                )
            if animal_input['An_PrePartWk'] > An_PrePartWkDurat:
                animal_input['DMI'] = min(
                    DMI.calculate_Dt_DMIn_Heif_H2(
                        animal_input['An_BW'], Dt_NDFdev_DMI),
                    Dt_DMIn_Heif_LateGestPen)
            else:
                animal_input['DMI'] = DMI.calculate_Dt_DMIn_Heif_H2(
                    animal_input['An_BW'], Dt_NDFdev_DMI
                    )
        if equation_selection['DMIn_eqn'] == 16:
            if animal_input['An_PrePartWk'] > An_PrePartWkDurat:
                animal_input['DMI'] = min(
                    DMI.calculate_Dt_DMIn_Heif_HJ1(animal_input['An_BW']),
                    Dt_DMIn_Heif_LateGestPen)
            else:
                animal_input['DMI'] = DMI.calculate_Dt_DMIn_Heif_HJ1(
                    animal_input['An_BW']
                    )
        if equation_selection['DMIn_eqn'] == 17:
            Dt_NDFdev_DMI = DMI.calculate_Dt_NDFdev_DMI(
                animal_input['An_BW'], Dt_NDF
                )
            if animal_input['An_PrePartWk'] > An_PrePartWkDurat:
                animal_input['DMI'] = min(
                    DMI.calculate_Dt_DMIn_Heif_HJ2(
                        animal_input['An_BW'], Dt_NDFdev_DMI),
                    Dt_DMIn_Heif_LateGestPen)
            else:
                animal_input['DMI'] = DMI.calculate_Dt_DMIn_Heif_HJ2(
                    animal_input['An_BW'], Dt_NDFdev_DMI
                    )
    elif equation_selection['DMIn_eqn'] == 10:
        Dt_DMIn_BW_LateGest_i = DMI.calculate_Dt_DMIn_BW_LateGest_i(
            An_PrePartWklim, Kb_LateGest_DMIn, coeff_dict
            )
        Dt_DMIn_BW_LateGest_p = DMI.calculate_Dt_DMIn_BW_LateGest_p(
            An_PrePartWkDurat, Kb_LateGest_DMIn, coeff_dict
            )
        if animal_input['An_PrePartWk'] > An_PrePartWkDurat:
            animal_input['DMI'] = min(
                DMI.calculate_Dt_DMIn_DryCow1_FarOff(
                    animal_input['An_BW'], Dt_DMIn_BW_LateGest_i),
                DMI.calculate_Dt_DMIn_DryCow1_Close(
                    animal_input['An_BW'], Dt_DMIn_BW_LateGest_p))
        else:
            animal_input['DMI'] = DMI.calculate_Dt_DMIn_DryCow1_FarOff(
                animal_input['An_BW'], Dt_DMIn_BW_LateGest_i
                )
    elif equation_selection['DMIn_eqn'] == 11:
        Dt_DMIn_DryCow_AdjGest = DMI.calculate_Dt_DMIn_DryCow_AdjGest(
            animal_input["An_GestDay"], animal_input["An_GestLength"],
            animal_input["An_BW"]
        )
        animal_input['DMI'] = DMI.calculate_Dt_DMIn_DryCow2(
            animal_input['An_BW'], Dt_DMIn_DryCow_AdjGest
            )
    else:
        # It needs to catch all possible solutions, otherwise it's possible that
        # it stays unchanged without warning
        print(
            "DMIn_eqn uncaught - DMI not changed. equation_selection[DMIn_eqn]: "
            + str(equation_selection['DMIn_eqn']))

    # Calculated again as part of diet_data, value may change depending on 
    # DMIn_eqn selections
    del(Dt_NDF, Dt_ADF, Dt_ForNDF, Fd_DNDF48, Dt_ForDNDF48, Dt_ForDNDF48_ForNDF)

    ########################################
    # Step 3: Feed Based Calculations
    ########################################
    # Calculate An_DMIn_BW with the final DMI value; required for calculating diet_data_initial
    Dt_DMIn_BW = unused.calculate_Dt_DMIn_BW(
        animal_input["DMI"], animal_input['An_BW']
        )
    Dt_DMIn_MBW = unused.calculate_Dt_DMIn_MBW(
        animal_input['DMI'], animal_input['An_BW']
        )
    An_DMIn_BW = animal.calculate_An_DMIn_BW(
        animal_input['An_BW'], animal_input['DMI']
        )
    Fe_rOMend = fecal.calculate_Fe_rOMend(animal_input['DMI'], coeff_dict)
    diet_info = diet.calculate_diet_info(
        animal_input['DMI'], animal_input['An_StatePhys'], 
        equation_selection['Use_DNDF_IV'], diet_info=diet_info_initial, 
        coeff_dict=coeff_dict
        )
    # All equations in the f dataframe go into calculate_diet_info()
    # This includes micronutrient calculations which are no longer handled by 
    # seperate functions

    diet_data_initial = diet.calculate_diet_data_initial(
        diet_info, animal_input['DMI'], animal_input['An_BW'],
        animal_input['An_StatePhys'], An_DMIn_BW,
        animal_input['An_AgeDryFdStart'], animal_input['Env_TempCurr'],
        equation_selection['DMIn_eqn'], equation_selection['Monensin_eqn'],
        Fe_rOMend, coeff_dict
        )
    # diet_data contains everything starting with "Dt_"

    ########################################
    # Step 4: Infusion Calculations
    ########################################
    infusion_data = infusion.calculate_infusion_data(
        infusion_input, animal_input['DMI'], coeff_dict
        )

    ########################################
    # Step 4.1: Uterine Bodyweight Calculations
    #########################################
    Uter_Wtpart = gestation.calculate_Uter_Wtpart(
        animal_input['Fet_BWbrth'], coeff_dict
        )
    Uter_Wt = gestation.calculate_Uter_Wt(
        animal_input['An_Parity_rl'], animal_input['An_AgeDay'], 
        animal_input['An_LactDay'], animal_input['An_GestDay'], 
        animal_input['An_GestLength'], Uter_Wtpart, coeff_dict
        )
    GrUter_Wtpart = gestation.calculate_GrUter_Wtpart(
        animal_input['Fet_BWbrth'], coeff_dict
        )
    GrUter_Wt = gestation.calculate_GrUter_Wt(
        animal_input['An_GestDay'], animal_input['An_GestLength'], Uter_Wt, 
        GrUter_Wtpart, coeff_dict
        )
    Uter_BWgain = gestation.calculate_Uter_BWgain(
        animal_input['An_LactDay'], animal_input['An_GestDay'], 
        animal_input['An_GestLength'], Uter_Wt, coeff_dict
        )
    GrUter_BWgain = gestation.calculate_GrUter_BWgain(
        animal_input['An_LactDay'], animal_input['An_GestDay'], 
        animal_input['An_GestLength'], GrUter_Wt, Uter_BWgain, coeff_dict
        )
    An_Preg = gestation.calculate_An_Preg(
        animal_input['An_GestDay'], animal_input['An_GestLength']
        )
    Fet_Wt = gestation.calculate_Fet_Wt(
        animal_input['An_GestDay'], animal_input['An_GestLength'], 
        animal_input['Fet_BWbrth'], coeff_dict
        )
    Fet_BWgain = gestation.calculate_Fet_BWgain(
        animal_input['An_GestDay'], animal_input['An_GestLength'], 
        Fet_Wt, coeff_dict
        )
    Conc_BWgain = body_comp.calculate_Conc_BWgain(GrUter_BWgain, Uter_BWgain)

    ########################################
    # Step 5: Animal Level Calculations
    ########################################
    # Combine Diet and Infusion nutrient supplies
    An_data_initial = animal.calculate_An_data_initial(
        animal_input, diet_data_initial, infusion_data,
        equation_selection['Monensin_eqn'], GrUter_Wt, coeff_dict
        )

    ########################################
    # Step 6: Rumen Digestion Calculations
    ########################################
    # Rumen Digestability Coefficients
    Rum_dcNDF = rumen.calculate_Rum_dcNDF(
        animal_input['DMI'], diet_data_initial['Dt_NDFIn'], 
        diet_data_initial['Dt_StIn'], diet_data_initial['Dt_CPIn'], 
        diet_data_initial['Dt_ADFIn'], diet_data_initial['Dt_ForWet']
        )
    Rum_dcSt = rumen.calculate_Rum_dcSt(
        animal_input['DMI'], diet_data_initial['Dt_ForNDF'], 
        diet_data_initial['Dt_StIn'], diet_data_initial['Dt_ForWet']
        )
    # Rumen Digestable Intakes
    Rum_DigNDFIn = rumen.calculate_Rum_DigNDFIn(
        Rum_dcNDF, diet_data_initial['Dt_NDFIn']
        )
    Rum_DigStIn = rumen.calculate_Rum_DigStIn(
        Rum_dcSt, diet_data_initial['Dt_StIn']
        )
    Rum_DigNDFnfIn = rumen.calculate_Rum_DigNDFnfIn(
        Rum_dcNDF, diet_data_initial['Dt_NDFnfIn']
        )
    # Duodenal Passage?
    Du_StPas = rumen.calculate_Du_StPas(
        diet_data_initial['Dt_StIn'], infusion_data['InfRum_StIn'], Rum_DigStIn
        )
    Du_NDFPas = rumen.calculate_Du_NDFPas(
        diet_data_initial['Dt_NDFIn'], infusion_data['Inf_NDFIn'], Rum_DigNDFIn
        )
    
    ########################################
    # Step 7: Microbial Protein Calculations
    ########################################
    if equation_selection['MiN_eqn'] == 1:
        RDPIn_MiNmax = micp.calculate_RDPIn_MiNmax(
            animal_input['DMI'], An_data_initial['An_RDP'], 
            An_data_initial['An_RDPIn']
            )
        MiN_Vm = micp.calculate_MiN_Vm(RDPIn_MiNmax, coeff_dict)
        Du_MiN_g = micp.calculate_Du_MiN_NRC2021_g(
            MiN_Vm, Rum_DigNDFIn, Rum_DigStIn, An_data_initial['An_RDPIn_g'], 
            coeff_dict
            )
    elif equation_selection['MiN_eqn'] == 2:
        Du_MiN_g = micp.calculate_Du_MiN_VTln_g(
            diet_data_initial['Dt_rOMIn'], diet_data_initial['Dt_ForNDFIn'],
            An_data_initial['An_RDPIn'], Rum_DigStIn, Rum_DigNDFIn, coeff_dict
            )
    elif equation_selection['MiN_eqn'] == 3:
        Du_MiN_g = micp.calculate_Du_MiN_VTnln_g(
            An_data_initial['An_RDPIn'], Rum_DigNDFIn, Rum_DigStIn
            )
    else:
        raise ValueError(
            f"Invalid MiN_eqn: {equation_selection['MiN_eqn']} was entered. "
            "Must choose 1, 2 or 3."
            )

    Du_MiCP_g = protein.calculate_Du_MiCP_g(Du_MiN_g)
    Du_MiTP_g = protein.calculate_Du_MiTP_g(Du_MiCP_g, coeff_dict)
    Du_MiCP = micp.calculate_Du_MiCP(Du_MiCP_g)
    Du_idMiCP_g = micp.calculate_Du_idMiCP_g(Du_MiCP_g, coeff_dict)
    Du_idMiCP = micp.calculate_Du_idMiCP(Du_idMiCP_g)
    Du_MiTP = micp.calculate_Du_MiTP(Du_MiTP_g)
    Du_EndCP_g = micp.calculate_Du_EndCP_g(
        animal_input['DMI'], infusion_data['InfRum_DMIn']
        )
    Du_EndN_g = micp.calculate_Du_EndN_g(
        animal_input['DMI'], infusion_data['InfRum_DMIn']
        )
    Du_EndCP = micp.calculate_Du_EndCP(Du_EndCP_g)
    Du_EndN = micp.calculate_Du_EndN(Du_EndN_g)
    Du_NAN_g = micp.calculate_Du_NAN_g(
        Du_MiN_g, An_data_initial['An_RUPIn'], Du_EndN_g
        )
    Du_NANMN_g = micp.calculate_Du_NANMN_g(
        An_data_initial['An_RUPIn'], Du_EndN_g
        )
    An_RDPbal_g = animal.calculate_An_RDPbal_g(
        An_data_initial['An_RDPIn_g'], Du_MiCP_g
        )
    Du_idMiTP_g = micp.calculate_Du_idMiTP_g(Du_idMiCP_g, coeff_dict)
    Du_idMiTP = micp.calculate_Du_idMiTP(Du_idMiTP_g)

    ########################################
    # Step 7.1: Fe_CP Calculation /  Finish Dt_ and An_ calculations
    ########################################
    # Required to finish Dt_ and An_ calculations
    Fe_RUP = fecal.calculate_Fe_RUP(
        An_data_initial['An_RUPIn'], infusion_data['InfSI_TPIn'], 
        An_data_initial['An_idRUPIn']
        )
    Fe_RumMiCP = fecal.calculate_Fe_RumMiCP(Du_MiCP, Du_idMiCP)
    Fe_CPend_g = fecal.calculate_Fe_CPend_g(
        animal_input['An_StatePhys'], An_data_initial['An_DMIn'], 
        An_data_initial['An_NDF'], animal_input['DMI'], 
        diet_data_initial['Dt_DMIn_ClfLiq'], 
        equation_selection["NonMilkCP_ClfLiq"]
        )
    Fe_CPend = fecal.calculate_Fe_CPend(Fe_CPend_g)
    Fe_CP = fecal.calculate_Fe_CP(
        animal_input['An_StatePhys'], diet_data_initial['Dt_CPIn_ClfLiq'], 
        diet_data_initial['Dt_dcCP_ClfDry'], An_data_initial['An_CPIn'], Fe_RUP, 
        Fe_RumMiCP, Fe_CPend, infusion_data['InfSI_NPNCPIn'], coeff_dict
        )
    Fe_Nend = fecal.calculate_Fe_Nend(Fe_CPend)
    Fe_NPend = fecal.calculate_Fe_NPend(Fe_CPend)
    Fe_NPend_g = fecal.calculate_Fe_NPend_g(Fe_NPend)
    Km_MP_NP_Trg = protein_req.calculate_Km_MP_NP_Trg(
        animal_input['An_StatePhys'], coeff_dict
        )
    Fe_MPendUse_g_Trg = fecal.calculate_Fe_MPendUse_g_Trg(
        animal_input['An_StatePhys'], Fe_CPend_g, Fe_NPend_g, Km_MP_NP_Trg
        )
    Fe_RDPend = fecal.calculate_Fe_RDPend(
        Fe_CPend, An_data_initial['An_RDPIn'], An_data_initial['An_CPIn']
        )
    Fe_RUPend = fecal.calculate_Fe_RUPend(
        Fe_CPend, An_data_initial['An_RUPIn'], An_data_initial['An_CPIn']
        )
    Fe_MiTP = fecal.calculate_Fe_MiTP(Du_MiTP, Du_idMiTP)
    Fe_InfCP = fecal.calculate_Fe_InfCP(
        infusion_data['InfRum_RUPIn'], infusion_data['InfSI_CPIn'], 
        infusion_data['InfRum_idRUPIn'], infusion_data['InfSI_idCPIn']
        )
    Fe_TP = fecal.calculate_Fe_TP(Fe_RUP, Fe_MiTP, Fe_NPend)
    Fe_N = fecal.calculate_Fe_N(Fe_CP)
    Fe_N_g = fecal.calculate_Fe_N_g(Fe_N)
    Fe_FA = fecal.calculate_Fe_FA(
        diet_data_initial['Dt_FAIn'], infusion_data['InfRum_FAIn'], 
        infusion_data['InfSI_FAIn'], diet_data_initial['Dt_DigFAIn'], 
        infusion_data['Inf_DigFAIn']
        )
    Fe_OM_end = fecal.calculate_Fe_OM_end(Fe_rOMend, Fe_CPend)
    Fe_DEMiCPend = fecal.calculate_Fe_DEMiCPend(Fe_RumMiCP, coeff_dict)
    Fe_DERDPend = fecal.calculate_Fe_DERDPend(Fe_RDPend, coeff_dict)
    Fe_DERUPend = fecal.calculate_Fe_DERUPend(Fe_RUPend, coeff_dict)

    ########################################
    # Step 7.2: Microbial Amino Acid Calculations
    ########################################
    MiTPAAProf = AA.calculate_MiTPAAProf(AA_list, coeff_dict)
    EndAAProf = AA.calculate_EndAAProf(AA_list, coeff_dict)
    Dt_AARUPIn = AA.calculate_Dt_AARUPIn(AA_list, diet_data_initial)
    Inf_AARUPIn = AA.calculate_Inf_AARUPIn(AA_list, infusion_data)
    Dt_AAIn = AA.calculate_Dt_AAIn(AA_list, diet_data_initial)
    RecAA = AA.calculate_RecAA(AA_list, coeff_dict)
    # Dataframe for storing all individual amino acid values
    AA_values = pd.DataFrame(index=AA_list)
    AA_values["Du_AAMic"] = AA.calculate_Du_AAMic(Du_MiTP_g, MiTPAAProf)
    AA_values['Du_IdAAMic'] = AA.calculate_Du_IdAAMic(
        AA_values['Du_AAMic'], coeff_dict
        )
    AA_values['Du_AAEndP'] = AA.calculate_Du_AAEndP(
        Du_EndCP_g, EndAAProf
        )
    AA_values['Du_AA'] = AA.calculate_Du_AA(
        Dt_AARUPIn, Inf_AARUPIn, AA_values['Du_AAMic'], AA_values['Du_AAEndP']
        )
    Du_EAA_g = AA_values['Du_AA'].sum()
    AA_values['DuAA_DtAA'] = AA.calculate_DuAA_AArg(
        AA_values['Du_AA'], Dt_AAIn
        )
    AA_values['Du_AA24h'] = AA.calculate_Du_AA24h(
        AA_values['Du_AA'], RecAA
        )
    
    ########################################
    # Step 7.3: Complete diet_data and An_data
    ########################################
    diet_data = diet.calculate_diet_data_complete(
        diet_data_initial, animal_input['An_StatePhys'], animal_input['DMI'],
        Fe_CP, Fe_CPend, Fe_MiTP, Fe_NPend, equation_selection['Monensin_eqn'],
        AA_values['Du_IdAAMic'], Du_idMiTP, coeff_dict
        )
    An_data = animal.calculate_An_data_complete(
        An_data_initial, diet_data, animal_input['An_StatePhys'],
        animal_input['An_BW'], animal_input['DMI'], Fe_CP, Fe_MiTP, Fe_NPend,
        Fe_DEMiCPend, Fe_DERDPend, Fe_DERUPend, Du_idMiCP, infusion_data,
        equation_selection['Monensin_eqn'], coeff_dict
        )
    # Calculate remaining digestability coefficients
    diet_data['TT_dcAnSt'] = diet.calculate_TT_dcAnSt(
        An_data['An_DigStIn'], diet_data['Dt_StIn'], infusion_data['Inf_StIn']
        )
    diet_data['TT_dcrOMa'] = diet.calculate_TT_dcrOMa(
        An_data['An_DigrOMaIn'], diet_data['Dt_rOMIn'],
        infusion_data['InfRum_GlcIn'], infusion_data['InfRum_AcetIn'],
        infusion_data['InfRum_PropIn'], infusion_data['InfRum_ButrIn'],
        infusion_data['InfSI_GlcIn'], infusion_data['InfSI_AcetIn'],
        infusion_data['InfSI_PropIn'], infusion_data['InfSI_ButrIn']
        )
    diet_data['TT_dcrOMt'] = diet.calculate_TT_dcrOMt(
        An_data['An_DigrOMtIn'], diet_data['Dt_rOMIn'],
        infusion_data['InfRum_GlcIn'], infusion_data['InfRum_AcetIn'],
        infusion_data['InfRum_PropIn'], infusion_data['InfRum_ButrIn'],
        infusion_data['InfSI_GlcIn'], infusion_data['InfSI_AcetIn'],
        infusion_data['InfSI_PropIn'], infusion_data['InfSI_ButrIn']
        )
    # NRC 2001 Microbial N flow
    Du_MiN_NRC2001_g = micp.calculate_Du_MiN_NRC2001_g(
        diet_data['Dt_TDNIn'], An_data['An_RDPIn']
        )
    # Fecal loss
    Fe_rOM = fecal.calculate_Fe_rOM(
        An_data['An_rOMIn'], An_data['An_DigrOMaIn']
        )
    Fe_St = fecal.calculate_Fe_St(
        diet_data['Dt_StIn'], infusion_data['Inf_StIn'], An_data['An_DigStIn']
        )
    Fe_NDF = fecal.calculate_Fe_NDF(
        diet_data['Dt_NDFIn'], diet_data['Dt_DigNDFIn']
        )
    Fe_NDFnf = fecal.calculate_Fe_NDFnf(
        diet_data['Dt_NDFnfIn'], diet_data['Dt_DigNDFnfIn']
        )
    Fe_OM = fecal.calculate_Fe_OM(Fe_CP, Fe_NDF, Fe_St, Fe_rOM, Fe_FA)
    Fe_DEout = fecal.calculate_Fe_DEout(An_data['An_GEIn'], An_data['An_DEIn'])
    Fe_DE_GE = fecal.calculate_Fe_DE_GE(Fe_DEout, An_data['An_GEIn'])
    Fe_DE = fecal.calculate_Fe_DE(Fe_DEout, An_data['An_DMIn'])

    ########################################
    # Step 10: Metabolizable Protein Intake
    ########################################
    An_MPIn = animal.calculate_An_MPIn(
        animal_input['An_StatePhys'], An_data['An_DigCPtIn'], 
        diet_data['Dt_idRUPIn'], Du_idMiTP, infusion_data['InfArt_TPIn']
        )
    An_MPIn_g = animal.calculate_An_MPIn_g(An_MPIn)
    An_MP = animal.calculate_An_MP(
        An_MPIn, animal_input['DMI'], infusion_data['InfRum_DMIn'], 
        infusion_data['InfSI_DMIn']
        )
    An_MP_CP = animal.calculate_An_MP_CP(An_MPIn, An_data['An_CPIn'])

    ########################################
    # Step 8: Amino Acid Calculations
    ########################################
    # Create array from of coefficients for the AA calculations
    mPrt_k_AA = AA.calculate_mPrt_k_AA_array(mPrt_coeff, AA_list)
    An_IdAAIn = AA.calculate_An_IdAAIn(An_data, AA_list)
    Inf_AA_g = AA.calculate_Inf_AA_g(infusion_data, AA_list)
    MWAA = AA.calculate_MWAA(AA_list, coeff_dict)
    Body_AA_TP = AA.calculate_Body_AA_TP(AA_list, coeff_dict)
    AA_values['Abs_AA_g'] = AA.calculate_Abs_AA_g(
        An_IdAAIn, Inf_AA_g, infusion_data['Inf_Art']
        )
    AA_values['mPrtmx_AA'] = AA.calculate_mPrtmx_AA(mPrt_k_AA, mPrt_coeff)
    f_mPrt_max = protein.calculate_f_mPrt_max(
        animal_input['An_305RHA_MlkTP'], coeff_dict
        )
    AA_values['mPrtmx_AA2'] = AA.calculate_mPrtmx_AA2(
        AA_values['mPrtmx_AA'], f_mPrt_max
        )
    AA_values['AA_mPrtmx'] = AA.calculate_AA_mPrtmx(mPrt_k_AA, mPrt_coeff)
    AA_values['mPrt_AA_01'] = AA.calculate_mPrt_AA_01(
        AA_values['AA_mPrtmx'], mPrt_k_AA, mPrt_coeff
        )
    AA_values['mPrt_k_AA'] = AA.calculate_mPrt_k_AA(
        AA_values['mPrtmx_AA2'], AA_values['mPrt_AA_01'], AA_values['AA_mPrtmx']
        )
    AA_values['IdAA_DtAA'] = AA.calculate_IdAA_DtAA(Dt_AAIn, An_IdAAIn)

    Abs_EAA_g = AA.calculate_Abs_EAA_g(AA_values['Abs_AA_g'])
    Abs_neAA_g = AA.calculate_Abs_neAA_g(An_MPIn_g, Abs_EAA_g)
    Abs_OthAA_g = AA.calculate_Abs_OthAA_g(Abs_neAA_g, AA_values['Abs_AA_g'])
    Abs_EAA2b_g = AA.calculate_Abs_EAA2b_g(
        equation_selection['mPrt_eqn'], AA_values['Abs_AA_g']
        )
    mPrt_k_EAA2 = AA.calculate_mPrt_k_EAA2(
        AA_values.loc['Met', 'mPrtmx_AA2'], AA_values.loc['Met', 'mPrt_AA_01'], 
        AA_values.loc['Met', 'AA_mPrtmx']
        )
    Abs_EAA2_g = AA.calculate_Abs_EAA2_g(AA_values['Abs_AA_g'])
    AA_values['Abs_AA_MPp'] = AA.calculate_Abs_AA_MPp(
        AA_values['Abs_AA_g'], An_MPIn_g
        )
    AA_values['Abs_AA_p'] = AA.calculate_Abs_AA_p(
        AA_values['Abs_AA_g'], Abs_EAA_g
        )
    AA_values['Abs_AA_DEI'] = AA.calculate_Abs_AA_DEI(
        AA_values['Abs_AA_g'], An_data['An_DEIn']
        )
    AA_values['Abs_AA_mol'] = AA.calculate_Abs_AA_mol(
        AA_values['Abs_AA_g'], MWAA
        )
    ########################################
    # Step 11: Milk Production Prediciton
    ########################################
    # Milk Requirement
    Trg_Mlk_NP_g = protein_req.calculate_Trg_Mlk_NP_g(
        animal_input['Trg_MilkProd'], animal_input['Trg_MilkTPp']
        )
    Mlk_NPmx = milk.calculate_Mlk_NPmx(
        AA_values['mPrtmx_AA2'], An_data['An_DEInp'], An_data['An_DigNDF'], 
        animal_input['An_BW'], Abs_neAA_g, Abs_OthAA_g, mPrt_coeff
        )
    Mlk_NP_g = milk.calculate_Mlk_NP_g(
        animal_input['An_StatePhys'], equation_selection["mPrt_eqn"],
        Trg_Mlk_NP_g, animal_input['An_BW'],
        AA_values['Abs_AA_g'], AA_values['mPrt_k_AA'], Abs_neAA_g, Abs_OthAA_g,
        Abs_EAA2b_g, mPrt_k_EAA2, An_data['An_DigNDF'], An_data['An_DEInp'],
        An_data['An_DEStIn'], An_data['An_DEFAIn'], An_data['An_DErOMIn'],
        An_data['An_DENDFIn'], mPrt_coeff
        )
    MlkNP_MlkNPmx = milk.calculate_MlkNP_MlkNPmx(Mlk_NP_g, Mlk_NPmx)
    Mlk_CP_g = milk.calculate_Mlk_CP_g(Mlk_NP_g)
    Mlk_CP = milk.calculate_Mlk_CP(Mlk_CP_g)
    AA_values['Mlk_AA_g'] = milk.calculate_Mlk_AA_g(
        Mlk_NP_g, coeff_dict, AA_list
        )
    Mlk_EAA_g = milk.calculate_Mlk_EAA_g(AA_values['Mlk_AA_g'])
    MlkNP_AnMP = milk.calculate_MlkNP_AnMP(Mlk_NP_g, An_MPIn_g)
    AA_values['MlkAA_AbsAA'] = milk.calculate_MlkAA_AbsAA(
        AA_values['Mlk_AA_g'], AA_values['Abs_AA_g']
        )
    MlkEAA_AbsEAA = milk.calculate_MlkEAA_AbsEAA(Mlk_EAA_g, Abs_EAA_g)
    MlkNP_AnCP = milk.calculate_MlkNP_AnCP(Mlk_NP_g, An_data['An_CPIn'])
    AA_values['MlkAA_DtAA'] = milk.calculate_MlkAA_DtAA(
        AA_values['Mlk_AA_g'], diet_data, AA_list
        )
    # Fecal AA loss
    Fe_AAMet_g = fecal.calculate_Fe_AAMet_g(Fe_NPend_g, coeff_dict, AA_list)
    Fe_AAMet_AbsAA = fecal.calculate_Fe_AAMet_AbsAA(
        Fe_AAMet_g, AA_values['Abs_AA_g']
        )

    ########################################
    # Step 12: Body Frame and Reserve Gain
    ########################################
    Frm_Gain_empty = body_comp.calculate_Frm_Gain_empty(
        Frm_Gain, diet_data['Dt_DMIn_ClfLiq'], diet_data['Dt_DMIn_ClfStrt'], 
        An_data['An_GutFill_BW']
        )
    Body_Gain_empty = body_comp.calculate_Body_Gain_empty(
        Frm_Gain_empty, Rsrv_Gain_empty
        )
    An_REgain_Calf = animal.calculate_An_REgain_Calf(
        Body_Gain_empty, An_data['An_BW_empty']
        )
    Frm_NPgain = body_comp.calculate_Frm_NPgain(
        animal_input['An_StatePhys'], NPGain_FrmGain, Frm_Gain_empty, 
        Body_Gain_empty, An_REgain_Calf
        )
    Body_NPgain = body_comp.calculate_Body_NPgain(Frm_NPgain, Rsrv_NPgain)
    Body_CPgain = body_comp.calculate_Body_CPgain(Body_NPgain, coeff_dict)
    Body_CPgain_g = body_comp.calculate_Body_CPgain_g(Body_CPgain)
    Rsrv_Gain = body_comp.calculate_Rsrv_Gain(animal_input['Trg_RsrvGain'])
    Body_Gain = body_comp.calculate_Body_Gain(Frm_Gain, Rsrv_Gain)
    FatGain_FrmGain = body_comp.calculate_FatGain_FrmGain(
        animal_input['An_StatePhys'], An_REgain_Calf, animal_input['An_BW'], 
        animal_input['An_BW_mature']
        )
    BW_BCS = body_comp.calculate_BW_BCS(animal_input['An_BW'])
    An_data['An_BWnp3'] = body_comp.calculate_An_BWnp3(
        An_data['An_BWnp'], animal_input['An_BCS']
        )
    An_data['An_GutFill_Wt_Erdman'] = body_comp.calculate_An_GutFill_Wt_Erdman(
        animal_input['DMI'], infusion_data['InfRum_DMIn'],
        infusion_data['InfSI_DMIn']
        )
    An_data['An_GutFill_Wt'] = body_comp.calculate_An_GutFill_Wt(
        An_data['An_GutFill_BW'], An_data['An_BWnp']
        )
    An_data['An_BWnp_empty'] = body_comp.calculate_An_BWnp_empty(
        An_data['An_BWnp'], An_data['An_GutFill_Wt']
        )
    An_data['An_BWnp3_empty'] = body_comp.calculate_An_BWnp3_empty(
        An_data['An_BWnp3'], An_data['An_GutFill_Wt']
        )
    Body_Fat_EBW = body_comp.calculate_Body_Fat_EBW(
        animal_input['An_BW'], animal_input['An_BW_mature']
        )
    Body_NonFat_EBW = body_comp.calculate_Body_NonFat_EBW(Body_Fat_EBW)
    Body_CP_EBW = body_comp.calculate_Body_CP_EBW(Body_NonFat_EBW)
    Body_Ash_EBW = body_comp.calculate_Body_Ash_EBW(Body_NonFat_EBW)
    Body_Wat_EBW = body_comp.calculate_Body_Wat_EBW(Body_NonFat_EBW)
    Body_Fat = body_comp.calculate_Body_Fat(
        An_data['An_BWnp_empty'], Body_Fat_EBW
        )
    Body_NonFat = body_comp.calculate_Body_NonFat(
        An_data['An_BWnp_empty'], Body_NonFat_EBW
        )
    Body_CP = body_comp.calculate_Body_CP(
        An_data['An_BWnp_empty'], Body_NonFat_EBW
        )
    Body_Ash = body_comp.calculate_Body_Ash(
        An_data['An_BWnp_empty'], Body_Ash_EBW
        )
    Body_Wat = body_comp.calculate_Body_Wat(
        An_data['An_BWnp_empty'], Body_Wat_EBW
        )
    An_BodConcgain = body_comp.calculate_An_BodConcgain(Body_Gain, Conc_BWgain)
    NonFatGain_FrmGain = body_comp.calculate_NonFatGain_FrmGain(FatGain_FrmGain)

    ########################################
    # Step 13: Gestation Protein Use
    ########################################
    Gest_NCPgain_g = gestation.calculate_Gest_NCPgain_g(
        GrUter_BWgain, coeff_dict
        )
    Gest_NPgain_g = gestation.calculate_Gest_NPgain_g(
        Gest_NCPgain_g, coeff_dict
        )
    Gest_NPuse_g = gestation.calculate_Gest_NPuse_g(
        Gest_NPgain_g, coeff_dict
        )
    Gest_CPuse_g = gestation.calculate_Gest_CPuse_g(Gest_NPuse_g, coeff_dict)
    AA_values['Gest_AA_g'] = gestation.calculate_Gest_AA_g(
        Gest_NPuse_g, coeff_dict, AA_list
        )
    Gest_EAA_g = gestation.calculate_Gest_EAA_g(AA_values['Gest_AA_g'])
    AA_values['GestAA_AbsAA'] = gestation.calculate_GestAA_AbsAA(
        AA_values['Gest_AA_g'], AA_values['Abs_AA_g']
        )

    ########################################
    # Step 14: Urinary Loss
    ########################################
    Ur_Nout_g = urine.calculate_Ur_Nout_g(
        diet_data['Dt_CPIn'], Fe_CP, Scrf_CP_g, Fe_CPend_g, Mlk_CP_g, 
        Body_CPgain_g, Gest_CPuse_g
        )
    Ur_DEout = urine.calculate_Ur_DEout(Ur_Nout_g)

    ########################################
    # Step 15: Energy Intake
    ########################################
    An_MEIn = animal.calculate_An_MEIn(
        animal_input['An_StatePhys'], animal_input['An_BW'], An_data['An_DEIn'],
        An_data['An_GasEOut'], Ur_DEout, diet_data['Dt_DMIn_ClfLiq'],
        diet_data['Dt_DEIn_base_ClfLiq'], diet_data['Dt_DEIn_base_ClfDry'],
        equation_selection['RumDevDisc_Clf']
        )
    An_NEIn = animal.calculate_An_NEIn(An_MEIn)
    An_NE = animal.calculate_An_NE(An_NEIn, An_data['An_DMIn'])
    if animal_input['An_StatePhys'] == "Calf":
        An_data['An_MEIn_ClfDry'] = animal.calculate_An_MEIn_ClfDry(
            An_MEIn, diet_data['Dt_MEIn_ClfLiq']
            )
        An_data['An_ME_ClfDry'] = animal.calculate_An_ME_ClfDry(
            An_data['An_MEIn_ClfDry'], An_data['An_DMIn'], 
            diet_data['Dt_DMIn_ClfLiq']
            )
        An_data['An_NE_ClfDry'] = animal.calculate_An_NE_ClfDry(
            An_data['An_ME_ClfDry']
            )

    ########################################
    # Step 16: Energy Requirement
    ########################################
    # Maintenance Requirements
    An_NEmUse_NS = energy.calculate_An_NEmUse_NS(
        animal_input['An_StatePhys'], animal_input['An_BW'], 
        An_data['An_BW_empty'], animal_input['An_Parity_rl'], 
        diet_data['Dt_DMIn_ClfLiq']
        )
    An_NEm_Act_Graze = energy.calculate_An_NEm_Act_Graze(
        diet_data['Dt_PastIn'], animal_input['DMI'], 
        diet_data['Dt_PastSupplIn'], An_data['An_MBW']
        )
    An_NEm_Act_Parlor = energy.calculate_An_NEm_Act_Parlor(
        animal_input['An_BW'], animal_input['Env_DistParlor'],
        animal_input['Env_TripsParlor']
        )
    An_NEm_Act_Topo = energy.calculate_An_NEm_Act_Topo(
        animal_input['An_BW'], animal_input['Env_Topo']
        )
    An_NEmUse_Act = energy.calculate_An_NEmUse_Act(
        An_NEm_Act_Graze, An_NEm_Act_Parlor, An_NEm_Act_Topo
        )
    An_NEmUse = energy.calculate_An_NEmUse(
        An_NEmUse_NS, An_NEmUse_Act, coeff_dict
        )
    if animal_input["An_StatePhys"] == "Calf":
        Km_ME_NE = energy.calculate_Km_ME_NE_Clf(
            An_data["An_ME_ClfDry"], An_data["An_NE_ClfDry"], 
            diet_data["Dt_DMIn_ClfLiq"], diet_data["Dt_DMIn_ClfStrt"]
            )
    else:
        Km_ME_NE = energy.calculate_Km_ME_NE(animal_input["An_StatePhys"])
    An_MEmUse = energy.calculate_An_MEmUse(An_NEmUse, Km_ME_NE)

    # Gain Requirements
    Rsrv_Gain_empty = body_comp.calculate_Rsrv_Gain_empty(Rsrv_Gain)
    Rsrv_Fatgain = body_comp.calculate_Rsrv_Fatgain(Rsrv_Gain_empty, coeff_dict)
    CPGain_FrmGain = body_comp.calculate_CPGain_FrmGain(
        animal_input['An_BW'], animal_input['An_BW_mature']
        )
    Rsrv_CPgain = body_comp.calculate_Rsrv_CPgain(
        CPGain_FrmGain, Rsrv_Gain_empty
        )
    Rsrv_NEgain = energy.calculate_Rsrv_NEgain(Rsrv_Fatgain, Rsrv_CPgain)
    Kr_ME_RE = energy.calculate_Kr_ME_RE(
        animal_input['Trg_MilkProd'], animal_input['Trg_RsrvGain']
        )
    Rsrv_MEgain = energy.calculate_Rsrv_MEgain(Rsrv_NEgain, Kr_ME_RE)
    Frm_Gain = body_comp.calculate_Frm_Gain(animal_input['Trg_FrmGain'])
    Frm_Fatgain = body_comp.calculate_Frm_Fatgain(
        FatGain_FrmGain, Frm_Gain_empty
        )
    NPGain_FrmGain = body_comp.calculate_NPGain_FrmGain(
        CPGain_FrmGain, coeff_dict
        )
    Frm_NPgain = body_comp.calculate_Frm_NPgain(
        animal_input['An_StatePhys'], NPGain_FrmGain, Frm_Gain_empty, 
        Body_Gain_empty, An_REgain_Calf
        )
    Frm_CPgain = body_comp.calculate_Frm_CPgain(Frm_NPgain, coeff_dict)
    Frm_NEgain = energy.calculate_Frm_NEgain(Frm_Fatgain, Frm_CPgain)
    Kf_ME_RE_ClfDry = energy.calculate_Kf_ME_RE_ClfDry(An_data['An_DE'])
    Kf_ME_RE = energy.calculate_Kf_ME_RE(
        animal_input['An_StatePhys'], Kf_ME_RE_ClfDry, 
        diet_data['Dt_DMIn_ClfLiq'], animal_input['DMI'], coeff_dict
        )
    Frm_MEgain = energy.calculate_Frm_MEgain(Frm_NEgain, Kf_ME_RE)
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
    An_MEgain = energy.calculate_An_MEgain(Rsrv_MEgain, Frm_MEgain)
    
    # Gestation Requirement
    Gest_REgain = energy.calculate_Gest_REgain(GrUter_BWgain, coeff_dict)
    Gest_MEuse = energy.calculate_Gest_MEuse(Gest_REgain)

    # Milk Production Requirement
    Trg_NEmilk_Milk = milk.calculate_Trg_NEmilk_Milk(
        animal_input['Trg_MilkFatp'], animal_input['Trg_MilkTPp'],
        animal_input['Trg_MilkLacp']
        )
    Trg_Mlk_NEout = energy.calculate_Trg_Mlk_NEout(
        animal_input['Trg_MilkProd'], Trg_NEmilk_Milk
        )
    Trg_Mlk_MEout = energy.calculate_Trg_Mlk_MEout(Trg_Mlk_NEout, coeff_dict)

    # Total Metabolizalbe Energy Requirement
    Trg_MEuse = energy.calculate_Trg_MEuse(
        An_MEmUse, An_MEgain, Gest_MEuse, Trg_Mlk_MEout
        )

    ########################################
    # Step 17: Protein Requirement
    ########################################
    # Maintenance Requirement
    Scrf_NP_g = protein.calculate_Scrf_NP_g(Scrf_CP_g, coeff_dict)
    Scrf_MPUse_g_Trg = protein.calculate_Scrf_MPUse_g_Trg(
        animal_input['An_StatePhys'], Scrf_CP_g, Scrf_NP_g, Km_MP_NP_Trg
        )
    Scrf_NP = protein.calculate_Scrf_NP(Scrf_NP_g)
    Scrf_N_g = protein.calculate_Scrf_N_g(Scrf_CP_g)
    Scrf_AA_g = protein.calculate_Scrf_AA_g(Scrf_NP_g, coeff_dict, AA_list)
    ScrfAA_AbsAA = protein.calculate_ScrfAA_AbsAA(
        Scrf_AA_g, AA_values['Abs_AA_g']
        )
    Ur_Nend_g = urine.calculate_Ur_Nend_g(animal_input['An_BW'])
    Ur_NPend_g = urine.calculate_Ur_NPend_g(
        animal_input['An_StatePhys'], animal_input['An_BW'], Ur_Nend_g
        )
    Ur_MPendUse_g = urine.calculate_Ur_MPendUse_g(Ur_NPend_g)
    Ur_Nend_Urea_g = urine.calculate_Ur_Nend_Urea_g(animal_input['An_BW'])
    Ur_Nend_Creatn_g = urine.calculate_Ur_Nend_Creatn_g(animal_input['An_BW'])
    Ur_Nend_Creat_g = urine.calculate_Ur_Nend_Creat_g(Ur_Nend_Creatn_g)
    Ur_Nend_PD_g = urine.calculate_Ur_Nend_PD_g(animal_input['An_BW'])
    Ur_NPend_3MH_g = urine.calculate_Ur_NPend_3MH_g(animal_input['An_BW'])
    Ur_Nend_3MH_g = urine.calculate_Ur_Nend_3MH_g(Ur_NPend_3MH_g, coeff_dict)
    Ur_Nend_sum_g = urine.calculate_Ur_Nend_sum_g(
        Ur_Nend_Urea_g, Ur_Nend_Creatn_g, Ur_Nend_Creat_g, Ur_Nend_PD_g, 
        Ur_Nend_3MH_g
        )
    Ur_Nend_Hipp_g = urine.calculate_Ur_Nend_Hipp_g(Ur_Nend_sum_g)
    Ur_NPend = urine.calculate_Ur_NPend(Ur_NPend_g)
    Ur_MPend = urine.calculate_Ur_MPend(Ur_NPend)
    Ur_EAAend_g = urine.calculate_Ur_EAAend_g(animal_input['An_BW'])
    Ur_AAEnd_g = urine.calculate_Ur_AAEnd_g(
        Ur_EAAend_g, Ur_NPend_3MH_g, coeff_dict, AA_list
        )
    Ur_AAEnd_AbsAA = urine.calculate_Ur_AAEnd_AbsAA(
        Ur_AAEnd_g, AA_values['Abs_AA_g']
        )
    Ur_EAAEnd_g = urine.calculate_Ur_EAAEnd_g(Ur_AAEnd_g)
    An_MPm_g_Trg = protein_req.calculate_An_MPm_g_Trg(
        Fe_MPendUse_g_Trg, Scrf_MPUse_g_Trg, Ur_MPendUse_g
        )
    # Gain Requirement
    Body_NPgain_g = body_comp.calculate_Body_NPgain_g(Body_NPgain)
    An_BWmature_empty = body_comp.calculate_An_BWmature_empty(
        animal_input['An_BW_mature'], coeff_dict
        )
    Kg_MP_NP_Trg = protein_req.calculate_Kg_MP_NP_Trg(
        animal_input['An_StatePhys'], animal_input['An_Parity_rl'],
        animal_input['An_BW'], An_data['An_BW_empty'],
        animal_input['An_BW_mature'], An_BWmature_empty, MP_NP_efficiency_input, 
        coeff_dict
        )
    Body_MPUse_g_Trg = protein_req.calculate_Body_MPUse_g_Trg_initial(
        Body_NPgain_g, Kg_MP_NP_Trg
        )
    # Gestation Requirement
    Gest_MPUse_g_Trg = protein_req.calculate_Gest_MPUse_g_Trg(
        Gest_NPuse_g, coeff_dict
        )
    Mlk_MPUse_g_Trg = protein_req.calculate_Mlk_MPUse_g_Trg(Trg_Mlk_NP_g, coeff_dict)
    # Total Protein Requirement
    # NOTE This initial protein requirement is the final value in most cases. 
    # There is an adjustment made when An_StatePhys == "Heifer" and 
    # Diff_MPuse_g > 0. Some of the values used to make this adjustment are used
    #  elsewhere so it can't just be put behind an if statement
    An_MPuse_g_Trg = protein_req.calculate_An_MPuse_g_Trg_initial(
        An_MPm_g_Trg, Body_MPUse_g_Trg, Gest_MPUse_g_Trg, Mlk_MPUse_g_Trg
        )
    An_MEIn_approx = animal.calculate_An_MEIn_approx(
        An_data['An_DEInp'], An_data['An_DENPNCPIn'], An_data['An_DigTPaIn'], 
        Body_NPgain, An_data['An_GasEOut'], coeff_dict
        )
    Min_MPuse_g = protein_req.calculate_Min_MPuse_g(
        animal_input['An_StatePhys'], An_MPuse_g_Trg, animal_input['An_BW'], 
        animal_input['An_BW_mature'], An_MEIn_approx
        )
    Diff_MPuse_g = protein_req.calculate_Diff_MPuse_g(
        Min_MPuse_g, An_MPuse_g_Trg
        )
    Frm_NPgain_g = protein_req.calculate_Frm_NPgain_g(Frm_NPgain)
    Frm_MPUse_g_Trg = protein_req.calculate_Frm_MPUse_g_Trg(
        animal_input['An_StatePhys'], Frm_NPgain_g, Kg_MP_NP_Trg, Diff_MPuse_g
        )
    Kg_MP_NP_Trg = protein_req.calculate_Kg_MP_NP_Trg_heifer_adjustment(
        animal_input['An_StatePhys'], Diff_MPuse_g, Frm_NPgain_g, 
        Frm_MPUse_g_Trg, Kg_MP_NP_Trg
        )
    Rsrv_NPgain_g = protein_req.calculate_Rsrv_NPgain_g(Rsrv_NPgain)
    Rsrv_MPUse_g_Trg = protein_req.calculate_Rsrv_MPUse_g_Trg(
        animal_input['An_StatePhys'], Diff_MPuse_g, Rsrv_NPgain_g, Kg_MP_NP_Trg
        )
    # Recalculate
    Body_MPUse_g_Trg = protein_req.calculate_Body_MPUse_g_Trg(
        animal_input['An_StatePhys'], Diff_MPuse_g, Body_NPgain_g, 
        Body_MPUse_g_Trg, Kg_MP_NP_Trg
        )
    # Recalculate
    An_MPuse_g_Trg = protein_req.calculate_An_MPuse_g_Trg(
        An_MPm_g_Trg, Frm_MPUse_g_Trg, Rsrv_MPUse_g_Trg, Gest_MPUse_g_Trg, 
        Mlk_MPUse_g_Trg
        )
    An_NPm_Use = animal.calculate_An_NPm_Use(Scrf_NP_g, Fe_NPend_g, Ur_NPend_g)
    An_CPm_Use = animal.calculate_An_CPm_Use(Scrf_CP_g, Fe_CPend_g, Ur_NPend_g)
    # AA for Body Gain
    AA_values['Body_AAGain_g'] = AA.calculate_Body_AAGain_g(
        Body_NPgain_g, Body_AA_TP
        )
    Body_EAAGain_g = AA.calculate_Body_EAAGain_g(AA_values['Body_AAGain_g'])
    AA_values['BodyAA_AbsAA'] = AA.calculate_BodyAA_AbsAA(
        AA_values['Body_AAGain_g'], AA_values['Abs_AA_g']
        )

    ### Total NP, N and AA Use and Postabsorptive Efficiency ###
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
    An_NPuse_g = protein.calculate_An_NPuse_g(
        Scrf_NP_g, Fe_NPend_g, Ur_NPend_g, Mlk_NP_g, Body_NPgain_g, 
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
        An_Nprod_g, An_data['An_NIn_g']
        )
    An_Nprod_DigNIn = protein.calculate_An_Nprod_DigNIn(
        An_Nprod_g, An_data['An_DigNtIn_g']
        )
    AA_values['An_AAUse_g'] = AA.calculate_An_AAUse_g(
        AA_values['Gest_AA_g'], AA_values['Mlk_AA_g'], 
        AA_values['Body_AAGain_g'], Scrf_AA_g, Fe_AAMet_g, Ur_AAEnd_g
        )
    An_EAAUse_g = AA.calculate_An_EAAUse_g(AA_values['An_AAUse_g'])
    AA_values['AnAAUse_AbsAA'] = AA.calculate_AnAAUse_AbsAA(
        AA_values['An_AAUse_g'], AA_values['Abs_AA_g']
        )
    AnEAAUse_AbsEAA = AA.calculate_AnEAAUse_AbsEAA(An_EAAUse_g, Abs_EAA_g)
    AA_values['An_AABal_g'] = AA.calculate_An_AABal_g(
        AA_values['Abs_AA_g'], AA_values['An_AAUse_g']
        )
    An_EAABal_g = AA.calculate_An_EAABal_g(Abs_EAA_g, An_EAAUse_g)
    Trg_AbsEAA_NPxprtEAA = AA.calculate_Trg_AbsEAA_NPxprtEAA(Trg_AbsAA_NPxprtAA)
    Trg_AbsArg_NPxprtArg = AA.calculate_Trg_AbsArg_NPxprtArg(
        Trg_AbsEAA_NPxprtEAA
        )
    # Add Arg efficiency to the array
    Trg_AbsAA_NPxprtAA = np.insert(Trg_AbsAA_NPxprtAA, 0, Trg_AbsArg_NPxprtArg)
    Trg_AAEff_EAAEff = AA.calculate_Trg_AAEff_EAAEff(
        Trg_AbsAA_NPxprtAA, Trg_AbsEAA_NPxprtEAA
        )
    AA_values['An_AAEff_EAAEff'] = AA.calculate_An_AAEff_EAAEff(
        AA_values['AnAAUse_AbsAA'], AnEAAUse_AbsEAA
        )
    AA_values['Imb_AA'] = AA.calculate_Imb_AA(
        AA_values['An_AAEff_EAAEff'], Trg_AAEff_EAAEff, f_Imb
     )
    Imb_EAA = AA.calculate_Imb_EAA(AA_values['Imb_AA'])

    ########################################
    # Milk Production Calculations
    ########################################
    An_LactDay_MlkPred = milk.calculate_An_LactDay_MlkPred(
        animal_input['An_LactDay']
        )
    Trg_Mlk_Fat = milk.calculate_Trg_Mlk_Fat(
        animal_input['Trg_MilkProd'], animal_input['Trg_MilkFatp']
        )
    Trg_Mlk_Fat_g = milk.calculate_Trg_Mlk_Fat_g(Trg_Mlk_Fat)
    Mlk_Fatemp_g = milk.calculate_Mlk_Fatemp_g(
        animal_input['An_StatePhys'], An_LactDay_MlkPred, animal_input['DMI'],
        diet_data['Dt_FAIn'], diet_data['Dt_DigC160In'],
        diet_data['Dt_DigC183In'], AA_values.loc['Ile', 'Abs_AA_g'],
        AA_values.loc['Met', 'Abs_AA_g']
        )
    Mlk_Fat_g = milk.calculate_Mlk_Fat_g(
        equation_selection['mFat_eqn'], Trg_Mlk_Fat_g, Mlk_Fatemp_g
        )
    Mlk_Fat = milk.calculate_Mlk_Fat(Mlk_Fat_g)
    Mlk_NP = milk.calculate_Mlk_NP(Mlk_NP_g)
    Mlk_Prod_comp = milk.calculate_Mlk_Prod_comp(
        animal_input['An_Breed'], Mlk_NP, Mlk_Fat, An_data['An_DEIn'], 
        An_LactDay_MlkPred, animal_input['An_Parity_rl']
        )
    An_MPavail_Milk_Trg = milk.calculate_An_MPavail_Milk_Trg(
        An_MPIn, An_MPuse_g_Trg, Mlk_MPUse_g_Trg
        )
    Mlk_NP_MPalow_Trg_g = milk.calculate_Mlk_NP_MPalow_Trg_g(
        An_MPavail_Milk_Trg, coeff_dict
        )
    Mlk_Prod_MPalow = milk.calculate_Mlk_Prod_MPalow(
        Mlk_NP_MPalow_Trg_g, animal_input['Trg_MilkTPp']
        )
    An_MEavail_Milk = milk.calculate_An_MEavail_Milk(
        An_MEIn, An_MEgain, An_MEmUse, Gest_MEuse
        )
    Mlk_Prod_NEalow = milk.calculate_Mlk_Prod_NEalow(
        An_MEavail_Milk, Trg_NEmilk_Milk, coeff_dict
        )
    Mlk_Prod = milk.calculate_Mlk_Prod(
        animal_input['An_StatePhys'], equation_selection['mProd_eqn'], 
        Mlk_Prod_comp, Mlk_Prod_NEalow, Mlk_Prod_MPalow, 
        animal_input['Trg_MilkProd']
        )
    MlkNP_Milk = milk.calculate_MlkNP_Milk(
        animal_input['An_StatePhys'], Mlk_NP_g, Mlk_Prod
        )
    MlkFat_Milk = milk.calculate_MlkFat_Milk(
        animal_input['An_StatePhys'], Mlk_Fat, Mlk_Prod
        )
    MlkNE_Milk = milk.calculate_MlkNE_Milk(
        MlkFat_Milk, MlkNP_Milk, animal_input['Trg_MilkLacp']
        )
    Mlk_NEout = milk.calculate_Mlk_NEout(MlkNE_Milk, Mlk_Prod)
    Mlk_MEout = milk.calculate_Mlk_MEout(Mlk_NEout, coeff_dict)
    
    ### MP Use and MP Allowable Production ###
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
        animal_input['An_StatePhys'], Xprt_NP_MP
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
    An_MP_NP = protein.calculate_An_MP_NP(An_NPuse_g, An_MPuse_g)
    An_NPxprt_MP = protein.calculate_An_NPxprt_MP(
        An_NPuse_g, Ur_NPend_g, Gest_NPuse_g, An_MPIn_g, Gest_MPUse_g_Trg
        )
    An_CP_NP = protein.calculate_An_CP_NP(An_NPuse_g, An_data['An_CPIn'])
    An_NPBal_g = protein.calculate_An_NPBal_g(An_MPIn_g, An_MP_NP, An_NPuse_g)
    An_NPBal = protein.calculate_An_NPBal(An_NPBal_g)

    ### Urine N and Energy Loss ###
    Ur_Nout_DigNIn = urine.calculate_Ur_Nout_DigNIn(
        Ur_Nout_g, An_data['An_DigCPtIn']
        )
    Ur_Nout_CPcatab = urine.calculate_Ur_Nout_CPcatab(Ur_Nout_g, Ur_Nend_g)
    UrDE_DMIn = urine.calculate_UrDE_DMIn(Ur_DEout, An_data['An_DMIn'])
    UrDE_GEIn = urine.calculate_UrDE_GEIn(Ur_DEout, An_data['An_GEIn'])
    UrDE_DEIn = urine.calculate_UrDE_DEIn(Ur_DEout, An_data['An_DEIn'])

    ### Estimated ME and NE Intakes ###
    An_ME = animal.calculate_An_ME(An_MEIn, An_data['An_DMIn'])
    An_ME_GE = animal.calculate_An_ME_GE(An_MEIn, An_data['An_GEIn'])
    An_ME_DE = animal.calculate_An_ME_DE(An_MEIn, An_data['An_DEIn'])
    An_NE_GE = animal.calculate_An_NE_GE(An_NEIn, An_data['An_GEIn'])
    An_NE_DE = animal.calculate_An_NE_DE(An_NEIn, An_data['An_DEIn'])
    An_NE_ME = animal.calculate_An_NE_ME(An_NEIn, An_MEIn)
    An_MPIn_MEIn = animal.calculate_An_MPIn_MEIn(An_MPIn_g, An_MEIn)

    ### ME and NE Use ###
    An_MEmUse_NS = energy.calculate_An_MEmUse_NS(An_NEmUse_NS, Km_ME_NE)
    An_MEmUse_Act = energy.calculate_An_MEmUse_Act(An_NEmUse_Act, Km_ME_NE)
    An_MEmUse_Env = energy.calculate_An_MEmUse_Env(Km_ME_NE, coeff_dict)
    An_NEm_ME = energy.calculate_An_NEm_ME(An_NEmUse, An_MEIn)
    An_NEm_DE = energy.calculate_An_NEm_DE(An_NEmUse, An_data['An_DEIn'])
    An_NEmNS_DE = energy.calculate_An_NEmNS_DE(An_NEmUse_NS, An_data['An_DEIn'])
    An_NEmAct_DE = energy.calculate_An_NEmAct_DE(
        An_NEmUse_Act, An_data['An_DEIn']
        )
    An_NEmEnv_DE = energy.calculate_An_NEmEnv_DE(An_data['An_DEIn'], coeff_dict)
    An_NEprod_Avail = energy.calculate_An_NEprod_Avail(An_NEIn, An_NEmUse)
    An_MEprod_Avail = energy.calculate_An_MEprod_Avail(An_MEIn, An_MEmUse)
    Gest_NELuse = energy.calculate_Gest_NELuse(Gest_MEuse, coeff_dict)
    Gest_NE_ME = energy.calculate_Gest_NE_ME(Gest_MEuse, An_MEIn)
    Gest_NE_DE = energy.calculate_Gest_NE_DE(Gest_REgain, An_data['An_DEIn'])
    An_REgain = energy.calculate_An_REgain(Body_Fatgain, Body_CPgain)
    Rsrv_NE_DE = energy.calculate_Rsrv_NE_DE(Rsrv_NEgain, An_data['An_DEIn'])
    Frm_NE_DE = energy.calculate_Frm_NE_DE(Frm_NEgain, An_data['An_DEIn'])
    Body_NEgain_BWgain = energy.calculate_Body_NEgain_BWgain(
        An_REgain, Body_Gain
        )
    An_ME_NEg = energy.calculate_An_ME_NEg(An_REgain, An_MEgain)
    Rsrv_NELgain = energy.calculate_Rsrv_NELgain(Rsrv_MEgain, coeff_dict)
    Frm_NELgain = energy.calculate_Frm_NELgain(Frm_MEgain, coeff_dict)
    An_NELgain = energy.calculate_An_NELgain(An_MEgain, coeff_dict)
    An_NEgain_DE = energy.calculate_An_NEgain_DE(An_REgain, An_data['An_DEIn'])
    An_NEgain_ME = energy.calculate_An_NEgain_ME(An_REgain, An_MEIn)
    Trg_MilkLac = milk.calculate_Trg_MilkLac(
        animal_input['Trg_MilkLacp'], animal_input['Trg_MilkProd']
        )
    Trg_NEmilk_DEIn = milk.calculate_Trg_NEmilk_DEIn(
        Trg_Mlk_NEout, An_data['An_DEIn']
        )
    Trg_MilkProd_EPcor = milk.calculate_Trg_MilkProd_EPcor(
        animal_input['Trg_MilkProd'], animal_input['Trg_MilkFatp'],
        animal_input['Trg_MilkTPp']
        )
    Mlk_Prod_NEalow_EPcor = milk.calculate_Mlk_Prod_NEalow_EPcor(
        Mlk_Prod_NEalow, animal_input['Trg_MilkFatp'],
        animal_input['Trg_MilkTPp']
        )
    Mlk_EPcorNEalow_DMIn = milk.calculate_Mlk_EPcorNEalow_DMIn(
        Mlk_Prod_NEalow_EPcor, An_data['An_DMIn']
        )
    MlkNP_Milk_p = milk.calculate_MlkNP_Milk_p(MlkNP_Milk)
    MlkFat_Milk_p = milk.calculate_MlkFat_Milk_p(MlkFat_Milk)
    Mlk_NE_DE = milk.calculate_Mlk_NE_DE(Mlk_NEout, An_data['An_DEIn'])
    An_MEuse = energy.calculate_An_MEuse(
        An_MEmUse, An_MEgain, Gest_MEuse, Mlk_MEout
        )
    An_NEuse = energy.calculate_An_NEuse(
        An_NEmUse, An_REgain, Gest_REgain, Mlk_NEout
        )
    Trg_NEuse = energy.calculate_Trg_NEuse(
        An_NEmUse, An_REgain, Gest_REgain, Trg_Mlk_NEout
        )
    An_NELuse = energy.calculate_An_NELuse(An_MEuse, coeff_dict)
    Trg_NELuse = energy.calculate_Trg_NELuse(Trg_MEuse, coeff_dict)
    An_NEprod_GE = energy.calculate_An_NEprod_GE(
        An_NEuse, An_NEmUse, An_data['An_GEIn']
        )
    Trg_NEprod_GE = energy.calculate_Trg_NEprod_GE(
        Trg_NEuse, An_NEmUse, An_data['An_GEIn']
        )
    An_NEmlk_GE = energy.calculate_An_NEmlk_GE(Mlk_NEout, An_data['An_GEIn'])
    Trg_NEmlk_GE = energy.calculate_Trg_NEmlk_GE(
        Trg_Mlk_NEout, An_data['An_GEIn']
        )
    An_MEbal = energy.calculate_An_MEbal(An_MEIn, An_MEuse)
    An_NELbal = energy.calculate_An_NELbal(An_MEbal, coeff_dict)
    An_NEbal = energy.calculate_An_NEbal(An_NEIn, An_NEuse)
    Trg_MEbal = energy.calculate_Trg_MEbal(An_MEIn, Trg_MEuse)
    Trg_NELbal = energy.calculate_Trg_NELbal(Trg_MEbal, coeff_dict)
    Trg_NEbal = energy.calculate_Trg_NEbal(An_NEIn, Trg_NEuse)
    An_MPuse_MEuse = energy.calculate_An_MPuse_MEuse(An_MPuse_g, An_MEuse)
    Trg_MPuse_MEuse = energy.calculate_Trg_MPuse_MEuse(An_MPuse_g_Trg, An_MEuse)
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
    Body_Fatgain_NEalow = body_comp.calculate_Body_Fatgain_NEalow(Body_Gain_NEalow)
    Body_NPgain_NEalow = body_comp.calculate_Body_NPgain_NEalow(
        Body_Fatgain_NEalow
        )
    An_Days_BCSdelta1 = body_comp.calculate_An_Days_BCSdelta1(
        BW_BCS, Body_Gain_NEalow
        )

    ########################################
    # Mineral Requirement Calculations
    ########################################
    ### Calcium ###
    Ca_Mlk = micro.calculate_Ca_Mlk(animal_input['An_Breed'])
    Fe_Ca_m = micro.calculate_Fe_Ca_m(An_data['An_DMIn'])
    An_Ca_g = micro.calculate_An_Ca_g(
        animal_input['An_BW_mature'], animal_input['An_BW'], Body_Gain
        )
    An_Ca_y = micro.calculate_An_Ca_y(
        animal_input['An_GestDay'], animal_input['An_BW']
        )
    An_Ca_l = micro.calculate_An_Ca_l(
        Mlk_NP_g, Ca_Mlk, animal_input['Trg_MilkProd'], 
        animal_input['Trg_MilkTPp']
        )
    An_Ca_Clf = micro.calculate_An_Ca_Clf(
        An_data['An_BW_empty'], Body_Gain_empty
        )
    An_Ca_req = micro.calculate_An_Ca_req(
        animal_input['An_StatePhys'], diet_data['Dt_DMIn_ClfLiq'], An_Ca_Clf, 
        Fe_Ca_m, An_Ca_g, An_Ca_y, An_Ca_l
        )
    An_Ca_bal = micro.calculate_An_Ca_bal(diet_data['Abs_CaIn'], An_Ca_req)
    An_Ca_prod = micro.calculate_An_Ca_prod(An_Ca_y, An_Ca_l, An_Ca_g)

    ### Phosphorus ###
    Ur_P_m = micro.calculate_Ur_P_m(animal_input['An_BW'])
    Fe_P_m = micro.calculate_Fe_P_m(
        animal_input['An_Parity_rl'], An_data['An_DMIn']
        )
    An_P_m = micro.calculate_An_P_m(Ur_P_m, Fe_P_m)
    An_P_g = micro.calculate_An_P_g(
        animal_input['An_BW_mature'], animal_input['An_BW'], Body_Gain
        )
    An_P_y = micro.calculate_An_P_y(
        animal_input['An_GestDay'], animal_input['An_BW']
        )
    An_P_l = micro.calculate_An_P_l(animal_input['Trg_MilkProd'], MlkNP_Milk)
    An_P_Clf = micro.calculate_An_P_Clf(An_data['An_BW_empty'], Body_Gain_empty)
    An_P_req = micro.calculate_An_P_req(
        animal_input['An_StatePhys'], diet_data['Dt_DMIn_ClfLiq'], An_P_Clf, 
        An_P_m, An_P_g, An_P_y, An_P_l
        )
    An_P_bal = micro.calculate_An_P_bal(diet_data['Abs_PIn'], An_P_req)
    Fe_P_g = micro.calculate_Fe_P_g(
        diet_data['Dt_PIn'], An_P_l, An_P_y, An_P_g, Ur_P_m
        )
    An_P_prod = micro.calculate_An_P_prod(An_P_y, An_P_l, An_P_g)

    ### Magnesium ###
    An_Mg_Clf = micro.calculate_An_Mg_Clf(An_data['An_BW_empty'], Body_Gain_empty)
    Ur_Mg_m = micro.calculate_Ur_Mg_m(animal_input['An_BW'])
    Fe_Mg_m = micro.calculate_Fe_Mg_m(An_data['An_DMIn'])
    An_Mg_m = micro.calculate_An_Mg_m(Ur_Mg_m, Fe_Mg_m)
    An_Mg_g = micro.calculate_An_Mg_g(Body_Gain)
    An_Mg_y = micro.calculate_An_Mg_y(
        animal_input['An_GestDay'], animal_input['An_BW']
        )
    An_Mg_l = micro.calculate_An_Mg_l(animal_input['Trg_MilkProd'])
    An_Mg_req = micro.calculate_An_Mg_req(
        animal_input['An_StatePhys'], diet_data['Dt_DMIn_ClfLiq'], An_Mg_Clf, 
        An_Mg_m, An_Mg_g, An_Mg_y, An_Mg_l
        )
    An_Mg_bal = micro.calculate_An_Mg_bal(diet_data['Abs_MgIn'], An_Mg_req)
    An_Mg_prod = micro.calculate_An_Mg_prod(An_Mg_y, An_Mg_l, An_Mg_g)

    ### Sodium ###
    An_Na_Clf = micro.calculate_An_Na_Clf(
        An_data['An_BW_empty'], Body_Gain_empty
        )
    Fe_Na_m = micro.calculate_Fe_Na_m(An_data['An_DMIn'])
    An_Na_g = micro.calculate_An_Na_g(Body_Gain)
    An_Na_y = micro.calculate_An_Na_y(
        animal_input['An_GestDay'], animal_input['An_BW']
        )
    An_Na_l = micro.calculate_An_Na_l(animal_input['Trg_MilkProd'])
    An_Na_req = micro.calculate_An_Na_req(
        animal_input['An_StatePhys'], diet_data['Dt_DMIn_ClfLiq'], An_Na_Clf, 
        Fe_Na_m, An_Na_g, An_Na_y, An_Na_l
        )
    An_Na_bal = micro.calculate_An_Na_bal(diet_data['Abs_NaIn'], An_Na_req)
    An_Na_prod = micro.calculate_An_Na_prod(An_Na_y, An_Na_l, An_Na_g)

    ### Chlorine ###
    An_Cl_Clf = micro.calculate_An_Cl_Clf(An_data['An_BW_empty'], Body_Gain_empty)
    Fe_Cl_m = micro.calculate_Fe_Cl_m(An_data['An_DMIn'])
    An_Cl_g = micro.calculate_An_Cl_g(Body_Gain)
    An_Cl_y = micro.calculate_An_Cl_y(
        animal_input['An_GestDay'], animal_input['An_BW']
        )
    An_Cl_l = micro.calculate_An_Cl_l(animal_input['Trg_MilkProd'])
    An_Cl_req = micro.calculate_An_Cl_req(
        animal_input['An_StatePhys'], diet_data['Dt_DMIn_ClfLiq'], An_Cl_Clf, 
        Fe_Cl_m, An_Cl_g, An_Cl_y, An_Cl_l
        )
    An_Cl_bal = micro.calculate_An_Cl_bal(diet_data['Abs_ClIn'], An_Cl_req)
    An_Cl_prod = micro.calculate_An_Cl_prod(An_Cl_y, An_Cl_l, An_Cl_g)

    ### Potassium ###
    An_K_Clf = micro.calculate_An_K_Clf(An_data['An_BW_empty'], Body_Gain_empty)
    Ur_K_m = micro.calculate_Ur_K_m(
        animal_input['Trg_MilkProd'], animal_input['An_BW']
        )
    Fe_K_m = micro.calculate_Fe_K_m(An_data['An_DMIn'])
    An_K_m = micro.calculate_An_K_m(Ur_K_m, Fe_K_m)
    An_K_g = micro.calculate_An_K_g(Body_Gain)
    An_K_y = micro.calculate_An_K_y(
        animal_input['An_GestDay'], animal_input['An_BW']
        )
    An_K_l = micro.calculate_An_K_l(animal_input['Trg_MilkProd'])
    An_K_req = micro.calculate_An_K_req(
        animal_input['An_StatePhys'], diet_data['Dt_DMIn_ClfLiq'], An_K_Clf, 
        An_K_m, An_K_g, An_K_y, An_K_l
        )
    An_K_bal = micro.calculate_An_K_bal(diet_data['Abs_KIn'], An_K_req)
    An_K_prod = micro.calculate_An_K_prod(An_K_y, An_K_l, An_K_g)

    ### Sulphur ###
    An_S_req = micro.calculate_An_S_req(An_data['An_DMIn'])
    An_S_bal = micro.calculate_An_S_bal(diet_data['Dt_SIn'], An_S_req)

    ### Cobalt ###
    An_Co_req = micro.calculate_An_Co_req(An_data['An_DMIn'])
    An_Co_bal = micro.calculate_An_Co_bal(diet_data['Abs_CoIn'], An_Co_req)

    ### Copper ###
    An_Cu_Clf = micro.calculate_An_Cu_Clf(
        animal_input['An_BW'], Body_Gain_empty
        )
    An_Cu_m = micro.calculate_An_Cu_m(animal_input['An_BW'])
    An_Cu_g = micro.calculate_An_Cu_g(Body_Gain)
    An_Cu_y = micro.calculate_An_Cu_y(
        animal_input['An_GestDay'], animal_input['An_BW']
        )
    An_Cu_l = micro.calculate_An_Cu_l(animal_input['Trg_MilkProd'])
    An_Cu_req = micro.calculate_An_Cu_req(
        animal_input['An_StatePhys'], diet_data['Dt_DMIn_ClfLiq'], An_Cu_Clf, 
        An_Cu_m, An_Cu_g, An_Cu_y, An_Cu_l
        )
    An_Cu_bal = micro.calculate_An_Cu_bal(diet_data['Abs_CuIn'], An_Cu_req)
    An_Cu_prod = micro.calculate_An_Cu_prod(An_Cu_y, An_Cu_l, An_Cu_g)

    ### Iodine ###
    An_I_req = micro.calculate_An_I_req(
        animal_input['An_StatePhys'], An_data['An_DMIn'], animal_input['An_BW'],
        animal_input['Trg_MilkProd']
        )
    An_I_bal = micro.calculate_An_I_bal(diet_data['Dt_IIn'], An_I_req)

    ### Iron ###
    An_Fe_Clf = micro.calculate_An_Fe_Clf(Body_Gain)
    An_Fe_g = micro.calculate_An_Fe_g(Body_Gain)
    An_Fe_y = micro.calculate_An_Fe_y(
        animal_input['An_GestDay'], animal_input['An_BW']
        )
    An_Fe_l = micro.calculate_An_Fe_l(animal_input['Trg_MilkProd'])
    An_Fe_req = micro.calculate_An_Fe_req(
        animal_input['An_StatePhys'], diet_data['Dt_DMIn_ClfLiq'], An_Fe_Clf, 
        An_Fe_g, An_Fe_y, An_Fe_l
        )
    An_Fe_bal = micro.calculate_An_Fe_bal(diet_data['Abs_FeIn'], An_Fe_req)
    An_Fe_prod = micro.calculate_An_Fe_prod(An_Fe_y, An_Fe_l, An_Fe_g)

    ### Maganese ###
    An_Mn_Clf = micro.calculate_An_Mn_Clf(animal_input['An_BW'], Body_Gain)
    An_Mn_m = micro.calculate_An_Mn_m(animal_input['An_BW'])
    An_Mn_g = micro.calculate_An_Mn_g(Body_Gain)
    An_Mn_y = micro.calculate_An_Mn_y(
        animal_input['An_GestDay'], animal_input['An_BW']
        )
    An_Mn_l = micro.calculate_An_Mn_l(animal_input['Trg_MilkProd'])
    An_Mn_req = micro.calculate_An_Mn_req(
        animal_input['An_StatePhys'], diet_data['Dt_DMIn_ClfLiq'], An_Mn_Clf, 
        An_Mn_m, An_Mn_g, An_Mn_y, An_Mn_l
        )
    An_Mn_bal = micro.calculate_An_Mn_bal(diet_data['Abs_MnIn'], An_Mn_req)
    An_Mn_prod = micro.calculate_An_Mn_prod(An_Mn_y, An_Mn_l, An_Mn_g)

    ### Selenium ###
    An_Se_req = micro.calculate_An_Se_req(An_data['An_DMIn'])
    An_Se_bal = micro.calculate_An_Se_bal(diet_data['Dt_SeIn'], An_Se_req)

    ### Zinc ###
    An_Zn_Clf = micro.calculate_An_Zn_Clf(An_data['An_DMIn'], Body_Gain)
    An_Zn_m = micro.calculate_An_Zn_m(An_data['An_DMIn'])
    An_Zn_g = micro.calculate_An_Zn_g(Body_Gain)
    An_Zn_y = micro.calculate_An_Zn_y(
        animal_input['An_GestDay'], animal_input['An_BW']
        )
    An_Zn_l = micro.calculate_An_Zn_l(animal_input['Trg_MilkProd'])
    An_Zn_req = micro.calculate_An_Zn_req(
        animal_input['An_StatePhys'], diet_data['Dt_DMIn_ClfLiq'], An_Zn_Clf, 
        An_Zn_m, An_Zn_g, An_Zn_y, An_Zn_l
        )
    An_Zn_bal = micro.calculate_An_Zn_bal(diet_data['Abs_ZnIn'], An_Zn_req)
    An_Zn_prod = micro.calculate_An_Zn_prod(An_Zn_y, An_Zn_l, An_Zn_g)

    ### DCAD ###
    An_DCADmeq = micro.calculate_An_DCADmeq(
        diet_data['Dt_K'], diet_data['Dt_Na'], diet_data['Dt_Cl'], 
        diet_data['Dt_S']
        )

    ### Vitamin Requirements ###
    An_VitA_req = micro.calculate_An_VitA_req(animal_input['Trg_MilkProd'],
                                        animal_input['An_BW'])
    An_VitA_bal = micro.calculate_An_VitA_bal(diet_data['Dt_VitAIn'], An_VitA_req)
    An_VitD_req = micro.calculate_An_VitD_req(animal_input['Trg_MilkProd'],
                                        animal_input['An_BW'])
    An_VitD_bal = micro.calculate_An_VitD_bal(diet_data['Dt_VitDIn'], An_VitD_req)
    An_VitE_req = micro.calculate_An_VitE_req(animal_input['Trg_MilkProd'],
                                        animal_input['An_Parity_rl'],
                                        animal_input['An_StatePhys'],
                                        animal_input['An_BW'],
                                        animal_input['An_GestDay'], An_Preg,
                                        diet_data['Dt_PastIn'])
    An_VitE_bal = micro.calculate_An_VitE_bal(diet_data['Dt_VitEIn'], An_VitE_req)

    ########################################
    # Water Calculations
    ########################################
    An_WaIn = water.calculate_An_WaIn(
        animal_input['An_StatePhys'], animal_input['DMI'], diet_data['Dt_DM'], 
        diet_data['Dt_Na'], diet_data['Dt_K'], diet_data['Dt_CP'], 
        animal_input['Env_TempCurr']
        )

    ### End of Model Calculations ###
    Rum_MiCP_DigCHO = micp.calculate_Rum_MiCP_DigCHO(
        Du_MiCP, Rum_DigNDFIn, Rum_DigStIn
        )
    Dt_IdAARUPIn = pd.Series([diet_data[f'Dt_Id{AA}RUPIn'] for AA in AA_list],
                             index=AA_list)
    Mlk_AA_TP = pd.Series([coeff_dict[f"Mlk_{AA}_TP"] for AA in AA_list],
                          index=AA_list)
    An_IdEAAIn = AA.calculate_An_IdEAAIn(An_IdAAIn)
    Du_IdEAAMic = AA.calculate_Du_IdEAAMic(AA_values['Du_IdAAMic'])
    Dt_IdEAARUPIn = AA.calculate_Dt_IdEAARUPIn(Dt_IdAARUPIn)
    An_RUPIn_g = animal.calculate_An_RUPIn_g(An_data['An_RUPIn'])
    AA_values['Trg_Mlk_AA_g'] = AA.calculate_Trg_Mlk_AA_g(
        Trg_Mlk_NP_g, Mlk_AA_TP
        )
    Trg_Mlk_EAA_g = AA.calculate_Trg_Mlk_EAA_g(AA_values['Trg_Mlk_AA_g'])
    AA_values['Trg_AAUse_g'] = AA.calculate_Trg_AAUse_g(
        AA_values['Trg_Mlk_AA_g'], Scrf_AA_g, Fe_AAMet_g, Ur_AAEnd_g, 
        AA_values['Gest_AA_g'], AA_values['Body_AAGain_g']
        )
    Trg_EAAUse_g = AA.calculate_Trg_EAAUse_g(AA_values['Trg_AAUse_g'])
    AA_values['Trg_AbsAA_g'] = AA.calculate_Trg_AbsAA_g(
        AA_values['Trg_Mlk_AA_g'], Scrf_AA_g, Fe_AAMet_g, Trg_AbsAA_NPxprtAA,
        Ur_AAEnd_g, AA_values['Gest_AA_g'], AA_values['Body_AAGain_g'],
        Kg_MP_NP_Trg, coeff_dict
        )
    Trg_AbsEAA_g = AA.calculate_Trg_AbsEAA_g(AA_values['Trg_AbsAA_g'])
    Trg_MlkEAA_AbsEAA = AA.calculate_Trg_MlkEAA_AbsEAA(
        Mlk_EAA_g, AA_values.loc["Arg", "Mlk_AA_g"], Trg_AbsEAA_g
        )
    MlkNP_Int = milk.calculate_MlkNP_Int(animal_input['An_BW'], mPrt_coeff)
    MlkNP_DEInp = milk.calculate_MlkNP_DEInp(An_data['An_DEInp'], mPrt_coeff)
    MlkNP_NDF = milk.calculate_MlkNP_NDF(An_data['An_DigNDF'], mPrt_coeff)
    AA_values['MlkNP_AbsAA'] = milk.calculate_MlkNP_AbsAA(
        AA_values['Abs_AA_g'], AA_values["mPrt_k_AA"]
        )
    MlkNP_AbsEAA = milk.calculate_MlkNP_AbsEAA(Abs_EAA2b_g, mPrt_k_EAA2)
    MlkNP_AbsNEAA = milk.calculate_MlkNP_AbsNEAA(Abs_neAA_g, mPrt_coeff)
    MlkNP_AbsOthAA = milk.calculate_MlkNP_AbsOthAA(Abs_OthAA_g, mPrt_coeff)
    AA_values['AnNPxAA_AbsAA'] = AA.calculate_AnNPxAA_AbsAA(
        AA_values['An_AAUse_g'], AA_values['Gest_AA_g'], Ur_AAEnd_g,
        AA_values['Abs_AA_g'], coeff_dict
        )
    AnNPxEAA_AbsEAA = AA.calculate_AnNPxEAA_AbsEAA(
        An_EAAUse_g, Gest_EAA_g, Ur_EAAEnd_g, Abs_EAA_g, coeff_dict
        )
    AA_values['AnNPxAAUser_AbsAA'] = AA.calculate_AnNPxAAUser_AbsAA(
        AA_values['Trg_AAUse_g'], AA_values['Gest_AA_g'], Ur_AAEnd_g,
        AA_values["Abs_AA_g"], coeff_dict
        )
    AnNPxEAAUser_AbsEAA = AA.calculate_AnNPxEAAUser_AbsEAA(
        Trg_EAAUse_g, Gest_EAA_g, Ur_EAAEnd_g, Abs_EAA_g, coeff_dict
        )

    Dt_acCa = micro.calculate_Dt_acCa(
        diet_data['Abs_CaIn'], diet_data['Dt_CaIn']
        )
    Dt_acP = micro.calculate_Dt_acP(diet_data['Abs_PIn'], diet_data['Dt_PIn'])
    Dt_acNa = micro.calculate_Dt_acNa(
        diet_data['Abs_NaIn'], diet_data['Dt_NaIn']
        )
    Dt_acMg = micro.recalculate_Dt_acMg(
        diet_data['Abs_MgIn'], diet_data['Dt_MgIn']
        )
    Dt_acK = micro.calculate_Dt_acK(diet_data['Abs_KIn'], diet_data['Dt_KIn'])
    Dt_acCl = micro.calculate_Dt_acCl(
        diet_data['Abs_ClIn'], diet_data['Dt_ClIn']
        )
    Dt_acCo = micro.calculate_Dt_acCo(
        diet_data['Abs_CoIn'], diet_data['Dt_CoIn']
        )
    Dt_acCu = micro.calculate_Dt_acCu(
        diet_data['Abs_CuIn'], diet_data['Dt_CuIn']
        )
    Dt_acFe = micro.calculate_Dt_acFe(
        diet_data['Abs_FeIn'], diet_data['Dt_FeIn']
        )
    Dt_acMn = micro.calculate_Dt_acMn(
        diet_data['Abs_MnIn'], diet_data['Dt_MnIn']
        )
    Dt_acZn = micro.calculate_Dt_acZn(
        diet_data['Abs_ZnIn'], diet_data['Dt_ZnIn']
        )

    CH4out_g = methane.calculate_CH4out_g(An_data['An_GasEOut'], coeff_dict)
    CH4out_L = methane.calculate_CH4out_L(CH4out_g, coeff_dict)
    if animal_input['An_StatePhys'] == "Lactating Cow":
        CH4g_Milk = methane.calculate_CH4g_Milk(CH4out_g, Mlk_Prod)
        CH4L_Milk = methane.calculate_CH4L_Milk(CH4out_L, Mlk_Prod)
    else:
        CH4g_Milk = 0
        CH4L_Milk = 0
    Man_out = manure.calculate_Man_out(
        animal_input['An_StatePhys'], An_data['An_DMIn'], diet_data['Dt_K']
        )
    if animal_input['An_StatePhys'] == "Lactating Cow":
        Man_Milk = manure.calculate_Man_Milk(Man_out, Mlk_Prod)
    else:
        Man_Milk = 0
    Man_VolSld = manure.calculate_Man_VolSld(
        animal_input['DMI'], infusion_data['InfRum_DMIn'], 
        infusion_data['InfSI_DMIn'], An_data['An_NDF'], An_data["An_CP"]
        )
    Man_VolSld2 = manure.calculate_Man_VolSld2(
        Fe_OM, diet_data['Dt_LgIn'], Ur_Nout_g
        )
    if animal_input['An_StatePhys'] == "Lactating Cow":
        VolSlds_Milk = manure.calculate_VolSlds_Milk(Man_VolSld, Mlk_Prod)
        VolSlds_Milk2 = manure.calculate_VolSlds_Milk2(Man_VolSld2, Mlk_Prod)
    else:
        VolSlds_Milk = 0
        VolSlds_Milk2 = 0
    Man_Nout_g = manure.calculate_Man_Nout_g(Ur_Nout_g, Fe_N_g, Scrf_N_g)
    Man_Nout2_g = manure.calculate_Man_Nout2_g(An_data['An_NIn_g'], An_Nprod_g)
    ManN_Milk = manure.calculate_ManN_Milk(Man_Nout_g, Mlk_Prod)
    Man_Ca_out = manure.calculate_Man_Ca_out(diet_data['Dt_CaIn'], An_Ca_prod)
    Man_P_out = manure.calculate_Man_P_out(diet_data['Dt_PIn'], An_P_prod)
    Man_Mg_out = manure.calculate_Man_Mg_out(diet_data['Dt_MgIn'], An_Mg_prod)
    Man_K_out = manure.calculate_Man_K_out(diet_data['Dt_KIn'], An_K_prod)
    Man_Na_out = manure.calculate_Man_Na_out(diet_data['Dt_NaIn'], An_Na_prod)
    Man_Cl_out = manure.calculate_Man_Cl_out(diet_data['Dt_ClIn'], An_Cl_prod)
    Man_MacMin_out = manure.calculate_Man_MacMin_out(
        Man_Ca_out, Man_P_out, Man_Mg_out, Man_K_out, Man_Na_out, Man_Cl_out
        )
    Man_Cu_out = manure.calculate_Man_Cu_out(diet_data['Dt_CuIn'], An_Cu_prod)
    Man_Fe_out = manure.calculate_Man_Fe_out(diet_data['Dt_FeIn'], An_Fe_prod)
    Man_Mn_out = manure.calculate_Man_Mn_out(diet_data['Dt_MnIn'], An_Mn_prod)
    Man_Zn_out = manure.calculate_Man_Zn_out(diet_data['Dt_ZnIn'], An_Zn_prod)
    Man_MicMin_out = manure.calculate_Man_MicMin_out(
        Man_Cu_out, Man_Fe_out, Man_Mn_out, Man_Zn_out
        )
    Man_Min_out_g = manure.calculate_Man_Min_out_g(
        Man_MacMin_out, Man_MicMin_out
        )
    CaProd_CaIn = micro.calculate_CaProd_CaIn(An_Ca_prod, diet_data['Dt_CaIn'])
    PProd_PIn = micro.calculate_PProd_PIn(An_P_prod, diet_data['Dt_PIn'])
    MgProd_MgIn = micro.calculate_MgProd_MgIn(An_Mg_prod, diet_data['Dt_MgIn'])
    KProd_KIn = micro.calculate_KProd_KIn(An_K_prod, diet_data['Dt_KIn'])
    NaProd_NaIn = micro.calculate_NaProd_NaIn(An_Na_prod, diet_data['Dt_NaIn'])
    ClProd_ClIn = micro.calculate_ClProd_ClIn(An_Cl_prod, diet_data['Dt_ClIn'])
    CuProd_CuIn = micro.calculate_CuProd_CuIn(An_Cu_prod, diet_data['Dt_CuIn'])
    FeProd_FeIn = micro.calculate_FeProd_FeIn(An_Fe_prod, diet_data['Dt_FeIn'])
    MnProd_MnIn = micro.calculate_MnProd_MnIn(An_Mn_prod, diet_data['Dt_MnIn'])
    ZnProd_ZnIn = micro.calculate_ZnProd_ZnIn(An_Zn_prod, diet_data['Dt_ZnIn'])
    CaProd_CaAbs = micro.calculate_CaProd_CaAbs(
        An_Ca_prod, diet_data['Abs_CaIn']
        )
    PProd_PAbs = micro.calculate_PProd_PAbs(An_P_prod, diet_data['Abs_PIn'])
    MgProd_MgAbs = micro.calculate_MgProd_MgAbs(
        An_Mg_prod, diet_data['Abs_MgIn']
        )
    KProd_KAbs = micro.calculate_KProd_KAbs(An_K_prod, diet_data['Abs_KIn'])
    NaProd_NaAbs = micro.calculate_NaProd_NaAbs(
        An_Na_prod, diet_data['Abs_NaIn']
        )
    ClProd_ClAbs = micro.calculate_ClProd_ClAbs(
        An_Cl_prod, diet_data['Abs_ClIn']
        )
    CuProd_CuAbs = micro.calculate_CuProd_CuAbs(
        An_Cu_prod, diet_data['Abs_CuIn']
        )
    FeProd_FeAbs = micro.calculate_FeProd_FeAbs(
        An_Fe_prod, diet_data['Abs_FeIn']
        )
    MnProd_MnAbs = micro.calculate_MnProd_MnAbs(
        An_Mn_prod, diet_data['Abs_MnIn']
        )
    ZnProd_ZnAbs = micro.calculate_ZnProd_ZnAbs(
        An_Zn_prod, diet_data['Abs_ZnIn']
        )
    Dt_CaReq_DMI = micro.calculate_Dt_CaReq_DMI(
        An_Ca_req, Dt_acCa, An_data['An_DMIn']
        )
    Dt_PReq_DMI = micro.calculate_Dt_PReq_DMI(
        An_P_req, Dt_acP, An_data['An_DMIn']
        )
    Dt_MgReq_DMI = micro.calculate_Dt_MgReq_DMI(
        An_Mg_req, Dt_acMg, An_data['An_DMIn']
        )
    Dt_KReq_DMI = micro.calculate_Dt_KReq_DMI(
        An_K_req, Dt_acK, An_data['An_DMIn']
        )
    Dt_NaReq_DMI = micro.calculate_Dt_NaReq_DMI(
        An_Na_req, Dt_acNa, An_data['An_DMIn']
        )
    Dt_ClReq_DMI = micro.calculate_Dt_ClReq_DMI(
        An_Cl_req, Dt_acCl, An_data['An_DMIn']
        )
    Dt_SReq_DMI = micro.calculate_Dt_SReq_DMI(An_S_req, An_data["An_DMIn"])
    Dt_CoReq_DMI = micro.calculate_Dt_CoReq_DMI(An_Co_req, An_data['An_DMIn'])
    Dt_CuReq_DMI = micro.calculate_Dt_CuReq_DMI(
        An_Cu_req, Dt_acCu, An_data['An_DMIn']
        )
    Dt_FeReq_DMI = micro.calculate_Dt_FeReq_DMI(
        An_Fe_req, Dt_acFe, An_data['An_DMIn']
        )
    Dt_IReq_DMI = micro.calculate_Dt_IReq_DMI(An_I_req, An_data['An_DMIn'])
    Dt_MnReq_DMI = micro.calculate_Dt_MnReq_DMI(
        An_Mn_req, Dt_acMn, An_data['An_DMIn']
        )
    Dt_SeReq_DMI = micro.calculate_Dt_SeReq_DMI(An_Se_req, An_data['An_DMIn'])
    Dt_ZnReq_DMI = micro.calculate_Dt_ZnReq_DMI(
        An_Zn_req, Dt_acZn, An_data['An_DMIn']
        )
    Dt_VitAReq_DMI = micro.calculate_Dt_VitAReq_DMI(
        An_VitA_req, An_data["An_DMIn"]
        )
    Dt_VitDReq_DMI = micro.calculate_Dt_VitDReq_DMI(
        An_VitD_req, An_data['An_DMIn']
        )
    Dt_VitEReq_DMI = micro.calculate_Dt_VitEReq_DMI(
        An_VitE_req, An_data['An_DMIn']
        )
    Man_Wa_out = manure.calculate_Man_Wa_out(
        animal_input['An_StatePhys'], Man_out, Fe_OM, Ur_Nout_g, Man_Min_out_g
        )
    if animal_input['An_StatePhys'] != "Calf":
        An_Wa_Insens = water.calculate_An_Wa_Insens(An_WaIn, Mlk_Prod, Man_Wa_out)
    else:
        An_Wa_Insens = 0
        
    if animal_input['An_StatePhys'] == "Lactating Cow":
        WaIn_Milk = water.calculate_WaIn_Milk(An_WaIn, Mlk_Prod)
        ManWa_Milk = manure.calculate_ManWa_Milk(Man_Wa_out, Mlk_Prod)
    else:
        WaIn_Milk = 0
        ManWa_Milk = 0
    del (An_IdAAIn)
    del (Dt_IdAARUPIn)
    del (Mlk_AA_TP)

    # Add missing values
    An_Grazing = animal.calculate_An_Grazing(
        diet_data["Dt_PastIn"], animal_input["DMI"]
        )
    En_OM = animal.calculate_En_OM(An_data["An_DEIn"], An_data["An_DigOMtIn"])
    Rsrv_AshGain = body_comp.calculate_Rsrv_AshGain(
        Rsrv_Gain_empty, coeff_dict
        )
    Trg_Mlk_NP = milk.calculate_Trg_Mlk_NP(Trg_Mlk_NP_g)
    VolSlds2_Milk = manure.calculate_VolSlds2_Milk(Man_VolSld2, Mlk_Prod)

    ########################################
    # Capture Outputs
    ########################################
    locals_dict = locals()
    model_output = output.ModelOutput(locals_input=locals_dict)
    return model_output
    