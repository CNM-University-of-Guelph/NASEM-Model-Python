import pandas as pd
import math

def mineral_intakes(An_StatePhys, feed_data, diet_info, Dt_DMIn_ClfLiq=0):
    '''
    ADD DOCSTRING
    '''
    # Currently calf calculations have not been incorporated into the model, Calf liquid feed DMI (Dt_DMIn_ClfLiq) is therefore set to 0
    # Once calf calculations are added a real value can be passed here

    # Lists of macro and micro mineral abreviations
    macro_minerals = ['Ca', 'P', 'Pinorg', 'Porg', 'Na', 'Mg', 'K', 'Cl', 'S']
    abs_macro_minerals = ['Ca', 'P', 'Mg', 'Na', 'K', 'Cl']
    micro_minerals = ['Co', 'Cr', 'Cu', 'Fe', 'I', 'Mn', 'Mo', 'Se', 'Zn']
    abs_micro_minerals = ['Co', 'Cu', 'Fe', 'Mn', 'Zn']

    mineral_values = pd.DataFrame(index=[macro_minerals + micro_minerals])

    ####################
    # Get Diet Data
    ####################
    feed_columns = ['Fd_Category', 'Fd_Ca', 'Fd_P', 'Fd_Pinorg_P', 'Fd_Porg_P', 'Fd_Na', 'Fd_Mg', 'Fd_K', 'Fd_Cl', 'Fd_S',
                    'Fd_Co', 'Fd_Cr', 'Fd_Cu', 'Fd_Fe', 'Fd_I', 'Fd_Mn', 'Fd_Mo', 'Fd_Se', 'Fd_Zn', 'Fd_acCa', 'Fd_acPtot',
                    'Fd_acMg', 'Fd_acNa', 'Fd_acK', 'Fd_acCl', 'Fd_acCu', 'Fd_acFe', 'Fd_acMn', 'Fd_acZn']
    df_minerals = pd.DataFrame(feed_data[feed_columns])

    # Get DMI for each feed from diet_info using the index of df_min to match the values
    for feed in df_minerals.index:
        if feed in diet_info['Feedstuff'].values:
            df_minerals.at[feed, 'Fd_DMIn'] = diet_info[diet_info['Feedstuff'] == feed]['kg_user'].values[0]

    # Save DMI as variable
    Dt_DMIn = df_minerals['Fd_DMIn'].sum()  

    # Adjust values based on An_StatePhys and Fd_Category
    df_minerals.loc[df_minerals['Fd_Category'] != 'Vitamin/Mineral', 'Fd_MgIn_min'] = 0
    df_minerals.loc[df_minerals['Fd_Category'] == 'Vitamin/Mineral', 'Fd_MgIn_min'] = df_minerals['Fd_DMIn'] * df_minerals['Fd_Mg'] / 100 * 1000

    # Adjust absorption coefficients for calves
    if An_StatePhys == 'Calf':
        df_minerals['Fd_acNa'] = 1
        df_minerals['Fd_acK'] = 1
        df_minerals['Fd_acCu'] = 1.0    # Line 1861
        df_minerals['Fd_acFe'] = 1.0    # Line 1863
        df_minerals['Fd_acMn'] = 1.0    # Line 1865
        df_minerals['Fd_acZn'] = 1.0    # Line 1867
    
    if An_StatePhys == 'Calf' and Dt_DMIn_ClfLiq > 0:
        df_minerals['Fd_acCa'] = 1  # Line 1839
        df_minerals['Fd_acPtot'] = 1 # Line 1842
        df_minerals['Fd_acMg'] = 1  # Line 1844
        df_minerals['Fd_acCl'] = 1  # Line 1848
    elif An_StatePhys == 'Calf' and Dt_DMIn_ClfLiq == 0:
        df_minerals['Fd_acCa'] = 0.60   # Line 1840
        df_minerals['Fd_acPtot'] = 0.75 # Line 1843
        df_minerals['Fd_acMg'] = 0.26   # Line 1845
        df_minerals['Fd_acCl'] = 0.92   # Line 1849
        df_minerals['Fd_acCu'] = 0.10   # Line 1862
        df_minerals['Fd_acFe'] = 0.10   # Line 1864
        df_minerals['Fd_acMn'] = 0.005  # Line 1866
        df_minerals['Fd_acZn'] = 0.20   # Line 1868
    
    df_minerals.loc[df_minerals['Fd_Category'] != 'Vitamin/Mineral', 'Fd_acPtot'] = df_minerals['Fd_Pinorg_P'] * 0.0084 + df_minerals['Fd_Porg_P'] * 0.0068 # Line 1841
    
    if An_StatePhys == 'Calf':  # Line 1860
        df_minerals['Fd_acCo'] = 0
    else:
        df_minerals['Fd_acCo'] = 1.0


    ####################
    # Macromineral Supply and Absorption
    ####################
    for macro in macro_minerals:
        # Macromineral intakes for each ingredient, g/d
        if 'Fd_{}'.format(macro) in df_minerals.columns:
            df_minerals['Fd_{}In'.format(macro)] = df_minerals['Fd_DMIn'] * df_minerals['Fd_{}'.format(macro)] / 100 * 1000
    # Pinorg and Porg have a different first step, require Fd_PIn from above step
    df_minerals['Fd_PinorgIn'] = df_minerals['Fd_PIn'] * df_minerals['Fd_Pinorg_P'] / 100   #??Check Bill's text
    df_minerals['Fd_PorgIn'] = df_minerals['Fd_PIn'] * df_minerals['Fd_Porg_P'] / 100  #Depracated by Bill.  Reduced to inorganic and organic.     

    for macro in macro_minerals:
        # Total diet macromineral intakes, g/d
        mineral_values.loc[macro, 'Dt_mineralIn'] = df_minerals['Fd_{}In'.format(macro)].sum()  # Lines 762-771
        # Macro minerals, % of DM
        mineral_values.loc[macro, 'Dt_macro'] = mineral_values.loc[macro, 'Dt_mineralIn'] / Dt_DMIn / 1000 * 100  

    for macro in abs_macro_minerals:
        if macro == 'P':
            df_minerals['Fd_absPIn'] = df_minerals['Fd_PIn'] * df_minerals['Fd_acPtot'] # Line 1852
        elif macro == 'Mg':
            df_minerals['Fd_absMgIn_base'] = df_minerals['Fd_MgIn'] * df_minerals['Fd_acMg'] # Line 1853
        else:
            df_minerals['Fd_abs{}In'.format(macro)] = df_minerals['Fd_{}In'.format(macro)] * df_minerals['Fd_ac{}'.format(macro)] # Line 1851, 1854-1856

    for macro in abs_macro_minerals:
        if macro == 'Mg':
            if An_StatePhys == 'Calf':
                Dt_acMg = 1
            else:
                # Awkward to use .iloc[0] after a .loc[] but prevents warning from math.log()
                Dt_acMg = (44.1 - 5.42 * math.log(mineral_values.loc['K', 'Dt_macro'].iloc[0] * 10.0) - 0.08 * df_minerals['Fd_MgIn_min'].sum() / df_minerals['Fd_MgIn'].sum() * 100) / 100
            mineral_values.loc[macro, 'Abs_mineralIn'] = Dt_acMg * df_minerals['Fd_MgIn_min'].sum()
        else:
            mineral_values.loc[macro, 'Abs_mineralIn'] = df_minerals['Fd_abs{}In'.format(macro)].sum()


    ####################
    # Micromineral Supply and Absorption
    ####################
    for micro in micro_minerals:
    #Micro Mineral Intakes from each ingredient, mg/d
        df_minerals['Fd_{}In'.format(micro)] = df_minerals['Fd_DMIn'] * df_minerals['Fd_{}'.format(micro)] # Lines 741-749
    #Total Dietary Micro Mineral Intakes, mg/d
        mineral_values.loc[micro, 'Dt_mineralIn'] = df_minerals['Fd_{}In'.format(micro)].sum()  # Lines 774-782
    #Total Dietary Micro Mineral Intakes, % intake
        mineral_values.loc[micro, 'Dt_micro'] = mineral_values.loc[micro, 'Dt_mineralIn'] / Dt_DMIn     # Lines 807-815

    for micro in abs_micro_minerals:
        df_minerals['Fd_abs{}In'.format(micro)] = df_minerals['Fd_{}In'.format(micro)] * df_minerals['Fd_ac{}'.format(micro)]  # Lines 1870-1874
        mineral_values.loc[micro, 'Abs_mineralIn'] = df_minerals['Fd_abs{}In'.format(micro)].sum()  # Line 1884-1888

    # Drop the columns from feed_data
    df_minerals = df_minerals.drop(columns=feed_columns)

    return df_minerals, mineral_values


def vitamin_supply(feed_data, diet_info):
    '''
    ADD DOCSTRING
    '''
    vitamins = ['VitA', 'VitD', 'VitE', 'Choline', 'Biotin', 'Niacin', 'B_Carotene']
    vitamin_values = pd.DataFrame(index=vitamins)

    ####################
    # Get Diet Data
    ####################
    feed_columns = ['Fd_VitA', 'Fd_VitD', 'Fd_VitE', 'Fd_Choline', 'Fd_Biotin', 'Fd_Niacin', 'Fd_B_Carotene']
    df_vitamins = pd.DataFrame(feed_data[feed_columns])

    # Get DMI for each feed from diet_info using the index of df_min to match the values
    for feed in df_vitamins.index:
        if feed in diet_info['Feedstuff'].values:
            df_vitamins.at[feed, 'Fd_DMIn'] = diet_info[diet_info['Feedstuff'] == feed]['kg_user'].values[0]

    ####################
    # Vitamin Supply
    ####################
    for vitamin in vitamins:
        df_vitamins['Fd_{}In'.format(vitamin)] = df_vitamins['Fd_DMIn'] * df_vitamins['Fd_{}'.format(vitamin)] # Lines 752-759

        vitamin_values.loc[vitamin, 'Dt_vitaminIn'] = df_vitamins['Fd_{}In'.format(vitamin)].sum()  # Lines 785-791

        vitamin_values.loc[vitamin, 'Dt_{}'.format(vitamin)] = vitamin_values.loc[vitamin, 'Dt_vitaminIn'] / df_vitamins['Fd_DMIn'].sum()   # Lines 818-825

    return df_vitamins


def mineral_requirements(An_StatePhys, An_Parity_rl, An_Breed, An_DMIn, An_BW_mature, An_BW, Trg_FrmGain, Trg_RsrvGain, An_GestDay, GrUter_Wt, Mlk_NP_g, Trg_MilkProd, Trg_MilkTPp, Abs_CaIn, MlkNP_Milk, Abs_PIn, Dt_PIn, Abs_MgIn, Abs_NaIn,
                         Abs_ClIn, Abs_KIn, Dt_SIn, Abs_CoIn, Abs_CuIn, Dt_IIn, Abs_FeIn, Abs_MnIn, Dt_SeIn, Abs_ZnIn, Dt_K, Dt_Na, Dt_Cl, Dt_S, Dt_DMIn_ClfLiq = 0):
    '''
    ADD DOCSTRING
    '''

    # Calculations that should be moved in the future
    Frm_Gain = Trg_FrmGain
    Rsrv_Gain = Trg_RsrvGain
    Rsrv_Gain_empty = Rsrv_Gain 
    Body_Gain = Frm_Gain + Rsrv_Gain    # Line 2436

    if An_StatePhys in ["Dry Cow", "Lactating Cow"] and An_Parity_rl > 0:
        An_GutFill_BW = 0.18
    else:
        An_GutFill_BW = 0.06

    Frm_Gain_empty = Frm_Gain * (1 - An_GutFill_BW)	    #Assume the same gut fill for frame gain
    Body_Gain_empty = Frm_Gain_empty + Rsrv_Gain_empty


    An_BWnp = An_BW - GrUter_Wt  #Non-pregnant BW
    An_GutFill_Wt = An_GutFill_BW * An_BWnp
    An_BW_empty = An_BW - An_GutFill_Wt 	

    ############
    # Calcium g/d, Lines 2962-2973
    ############
    if An_Breed == 'Jersey':    
        Ca_Mlk = 1.17
    else:
        Ca_Mlk = 1.03   
    
    Fe_Ca_m = 0.9 * An_DMIn     #Maintenance
    An_Ca_g = (9.83 * An_BW_mature**0.22 * An_BW**-.22) * Body_Gain     #Growth
    An_Ca_y = (0.0245 * math.exp((0.05581 - 0.00007 * An_GestDay) * An_GestDay)- 0.0245 * math.exp((0.05581 - 0.00007 * (An_GestDay - 1)) * (An_GestDay - 1))) * An_BW / 715    #Gestation 
    
    if Mlk_NP_g is None or math.isnan(Mlk_NP_g):    #Lactation
        An_Ca_l = Ca_Mlk * Trg_MilkProd
    else: 
        An_Ca_l = (0.295 + 0.239 * Trg_MilkTPp) * Trg_MilkProd
    
    # this doesn't do anything - An_Ca_l can't ever be nan? :
    # if math.isnan(An_Ca_l):
    #     An_Ca_l = 0

    An_Ca_Clf = (0.0127 * An_BW_empty + (14.4 * (An_BW_empty**-0.139) * Body_Gain_empty)) / 0.73
    if An_StatePhys == 'Calf' and Dt_DMIn_ClfLiq > 0:
        An_Ca_req = An_Ca_Clf
    else:
        An_Ca_req = Fe_Ca_m + An_Ca_g + An_Ca_y + An_Ca_l
    
    An_Ca_bal = Abs_CaIn - An_Ca_req
    An_Ca_prod = An_Ca_y + An_Ca_l + An_Ca_g

    ############
    # Phosphorus g/d, Lines 2976-2991
    ############
    Ur_P_m = 0.0006 * An_BW
    if An_Parity_rl == 0:
        Fe_P_m = 0.8 * An_DMIn
    else:
        Fe_P_m = 1.0 * An_DMIn
    An_P_m = Ur_P_m + Fe_P_m
    An_P_g = (1.2 + (4.635 * An_BW_mature**.22 * An_BW**-0.22)) * Body_Gain
    An_P_y = (0.02743 * math.exp((0.05527 - 0.000075 * An_GestDay) * An_GestDay) - 0.02743 * math.exp((0.05527 - 0.000075 * (An_GestDay - 1)) * (An_GestDay - 1))) * An_BW / 715
    
    if Trg_MilkProd is None or math.isnan(Trg_MilkProd):
        An_P_l = 0      #If MTP not known then 0.9*Milk
    else:
        An_P_l = (0.48 + 0.13 * MlkNP_Milk * 100) * Trg_MilkProd


    An_P_Clf = (0.0118 * An_BW_empty + (5.85 * (An_BW_empty**-0.027) * Body_Gain_empty)) / 0.65
   
    if An_StatePhys == 'Calf' and Dt_DMIn_ClfLiq > 0:
        An_P_req = An_P_Clf
    else:
        An_P_req = An_P_m + An_P_g + An_P_y + An_P_l
    An_P_bal = Abs_PIn - An_P_req   #Infused P not currently considered as an input, but should be
    Fe_P_g = Dt_PIn - An_P_l - An_P_y - An_P_g - Ur_P_m
      #urinary losses will be underestimated at very high dietary P. Ordinarily 99% by feces.
    An_P_prod = An_P_y + An_P_l + An_P_g

    ############
    # Magnesium g/d, Lines 2994-3004
    ############
    An_Mg_Clf = (0.0035 * An_BW_empty + (0.60 * (An_BW_empty**-0.036) * Body_Gain_empty)) / 0.30
    Ur_Mg_m = 0.0007 * An_BW
    Fe_Mg_m = 0.3 * An_DMIn
    An_Mg_m = Ur_Mg_m + Fe_Mg_m
    An_Mg_g = 0.45 * Body_Gain
    if An_GestDay > 190:
        An_Mg_y = 0.3 * (An_BW / 715)
    else:
        An_Mg_y = 0

    if Trg_MilkProd is None or math.isnan(Trg_MilkProd):
        An_Mg_l = 0
    else:
        An_Mg_l = 0.11 * Trg_MilkProd

    if An_StatePhys == 'Calf' and Dt_DMIn_ClfLiq > 0:
        An_Mg_req = An_Mg_Clf
    else:
        An_Mg_req = An_Mg_m + An_Mg_g + An_Mg_y + An_Mg_l

    An_Mg_bal = Abs_MgIn - An_Mg_req
    An_Mg_prod = An_Mg_y + An_Mg_l + An_Mg_g

    ############
    # Sodium g/d, Lines 3007-3015
    ############
    An_Na_Clf = (0.00637 * An_BW_empty + (1.508 * (An_BW_empty**-0.045) * Body_Gain_empty)) / 0.24
    Fe_Na_m = 1.45 * An_DMIn
    An_Na_g = 1.4 * Body_Gain
    if An_GestDay > 190:
        An_Na_y = 1.4 * An_BW / 715
    else:
        An_Na_y = 0

    if Trg_MilkProd is None or math.isnan(Trg_MilkProd):
        An_Na_l = 0
    else:
        An_Na_l = 0.4 * Trg_MilkProd

    if An_StatePhys == 'Calf' and Dt_DMIn_ClfLiq > 0:
        An_Na_req = An_Na_Clf
    else:
        An_Na_req = Fe_Na_m + An_Na_g + An_Na_y + An_Na_l

    An_Na_bal = Abs_NaIn - An_Na_req
    An_Na_prod = An_Na_y + An_Na_l + An_Na_g

    ############
    # Chlorine g/d, Lines 3017-3025
    ############
    An_Cl_Clf = 0.8 * (0.00637 * An_BW_empty + (1.508 * (An_BW_empty**-0.045) * Body_Gain_empty)) / 0.24
    Fe_Cl_m = 1.11 * An_DMIn
    An_Cl_g = 1.0 * Body_Gain
    if An_GestDay > 190:
        An_Cl_y = 1.0 * An_BW / 715       
    else:
       An_Cl_y = 0

    if Trg_MilkProd is None or math.isnan(Trg_MilkProd):
        An_Cl_l = 0
    else:
        An_Cl_l = 1.0 * Trg_MilkProd

    if An_StatePhys == 'Calf' and Dt_DMIn_ClfLiq > 0:
        An_Cl_req = An_Cl_Clf
    else:
        An_Cl_req = Fe_Cl_m + An_Cl_g + An_Cl_y + An_Cl_l

    An_Cl_bal = Abs_ClIn - An_Cl_req
    An_Cl_prod = An_Cl_y + An_Cl_l + An_Cl_g

    ############
    # Potassium g/d, Lines 3027-3037
    ############
    An_K_Clf = (0.0203 * An_BW_empty + (1.14 * (An_BW_empty**-0.048) * Body_Gain_empty)) / 0.13
    if Trg_MilkProd > 0:
        Ur_K_m = 0.2 * An_BW
    else:
        Ur_K_m = 0.07 * An_BW

    Fe_K_m = 2.5 * An_DMIn
    An_K_m = Ur_K_m + Fe_K_m
    An_K_g = 2.5 * Body_Gain

    if An_GestDay > 190:
        An_K_y = 1.03 * An_BW / 715
    else:
        An_K_y = 0

    if Trg_MilkProd is None or math.isnan(Trg_MilkProd):
        An_K_l = 0
    else:
        An_K_l = 1.5 * Trg_MilkProd

    if An_StatePhys == 'Calf' and Dt_DMIn_ClfLiq > 0:
        An_K_req = An_K_Clf
    else: 
        An_K_req = An_K_m + An_K_g + An_K_y + An_K_l

    An_K_bal = Abs_KIn - An_K_req
    An_K_prod = An_K_y + An_K_l + An_K_g

    ############
    # Sulphur g/d, Lines 3039-3040
    ############
    An_S_req = 2 * An_DMIn
    An_S_bal = Dt_SIn - An_S_req

    ############
    # Cobalt mg/d, Lines 3045-3046
    ############
    An_Co_req = 0.2 * An_DMIn  #Based on dietary intake assuming no absorption for a calf
    An_Co_bal = Abs_CoIn - An_Co_req #calf absorption set to 0 and other StatePhys to 1 above

    ############
    # Copper mg/d, Lines 3049-3057
    ############
    An_Cu_Clf = (0.0145 * An_BW + 2.5 * Body_Gain_empty) / 0.5
    An_Cu_m = 0.0145 * An_BW
    An_Cu_g = 2.0 * Body_Gain
    if An_GestDay < 90:
        An_Cu_y = 0
    elif An_GestDay > 190:
        An_Cu_y = 0.0023 * An_BW
    else:
        An_Cu_y = 0.0003 * An_BW

    if Trg_MilkProd is None or math.isnan(Trg_MilkProd):
        An_Cu_l = 0
    else:
        An_Cu_l = 0.04 * Trg_MilkProd

    if An_StatePhys == 'Calf' and Dt_DMIn_ClfLiq > 0:
        An_Cu_req = An_Cu_Clf
    else:
        An_Cu_req = An_Cu_m + An_Cu_g + An_Cu_y + An_Cu_l

    An_Cu_bal = Abs_CuIn - An_Cu_req
    An_Cu_prod = An_Cu_y + An_Cu_l + An_Cu_g

    ############
    # Iodine mg/d, Lines 3059-3060
    ############
    if An_StatePhys == 'Calf':
        An_I_req = 0.8 * An_DMIn
    else:
        An_I_req = 0.216 * An_BW**0.528 + 0.1 * Trg_MilkProd
    An_I_bal = Dt_IIn - An_I_req

    ############
    # Iron mg/d, Lines 3063-3070
    ############
    An_Fe_Clf = 34 * Body_Gain / 0.25
    An_Fe_g = 34 * Body_Gain

    if An_GestDay > 190:
        An_Fe_y = 0.025 * An_BW
    else:
        An_Fe_y = 0

    if Trg_MilkProd is None or math.isnan(Trg_MilkProd):
       An_Fe_l = 0
    else:
        An_Fe_l = 1.0 * Trg_MilkProd

    if An_StatePhys == 'Calf' and Dt_DMIn_ClfLiq > 0:
        An_Fe_req = An_Fe_Clf
    else: 
        An_Fe_req = An_Fe_g + An_Fe_y + An_Fe_l

    An_Fe_bal = Abs_FeIn - An_Fe_req
    An_Fe_prod = An_Fe_y + An_Fe_l + An_Fe_g

    ############
    # Manganese mg/d, Lines 3072-3080
    ############
    An_Mn_Clf = (0.0026 * An_BW + 0.7 * Body_Gain) / 0.01
    An_Mn_m = 0.0026 * An_BW
    An_Mn_g = 0.7 * Body_Gain

    if An_GestDay > 190:
        An_Mn_y = 0.00042 * An_BW
    else:
        An_Mn_y = 0

    if Trg_MilkProd is None or math.isnan(Trg_MilkProd):
       An_Mn_l = 0
    else:
        An_Mn_l = 0.03 * Trg_MilkProd

    if An_StatePhys == 'Calf' and Dt_DMIn_ClfLiq > 0:
        An_Mn_req = An_Mn_Clf
    else: 
        An_Mn_req = An_Mn_m + An_Mn_g + An_Mn_y + An_Mn_l

    An_Mn_bal = Abs_MnIn - An_Mn_req
    An_Mn_prod = An_Mn_y + An_Mn_l + An_Mn_g

    ############
    # Selenium mg/d, Lines 3082-3083
    ############
    An_Se_req = 0.3 * An_DMIn
    An_Se_bal = Dt_SeIn - An_Se_req

    ############
    # Zinc mg/d, Lines 3086-3094
    ############
    An_Zn_Clf = (2.0 * An_DMIn + 24 * Body_Gain) / 0.25
    An_Zn_m = 5.0 * An_DMIn
    An_Zn_g = 24 * Body_Gain

    if An_GestDay > 190:
        An_Zn_y = 0.017 * An_BW
    else:
        An_Zn_y = 0

    if Trg_MilkProd is None or math.isnan(Trg_MilkProd):
       An_Zn_l = 0
    else:
        An_Zn_l = 4.0 * Trg_MilkProd

    if An_StatePhys == 'Calf' and Dt_DMIn_ClfLiq > 0:
        An_Zn_req = An_Zn_Clf
    else: 
        An_Zn_req = An_Zn_m + An_Zn_g + An_Zn_y + An_Zn_l

    An_Zn_bal = Abs_ZnIn - An_Zn_req
    An_Zn_prod = An_Zn_y + An_Zn_l + An_Zn_g
    
    ############
    # DCAD meg/kg, Line 3095
    ############
    An_DCADmeq = (Dt_K.values[0] / 0.039 + Dt_Na.values[0] / 0.023 - Dt_Cl.values[0] / 0.0355 - Dt_S.values[0] / 0.016) * 10

    requirement_names = ['An_Ca_req', 'An_P_req', 'An_Mg_req', 'An_Na_req', 'An_Cl_req', 'An_K_req', 'An_S_req', 'An_Co_req', 'An_Cu_req', 'An_I_req', 'An_Fe_req', 'An_Mn_req', 'An_Se_req', 'An_Zn_req']
    requirement_values = [An_Ca_req, An_P_req, An_Mg_req, An_Na_req, An_Cl_req, An_K_req, An_S_req, An_Co_req, An_Cu_req, An_I_req, An_Fe_req, An_Mn_req, An_Se_req, An_Zn_req]
    mineral_requirements = {variable: number for variable, number in zip(requirement_names, requirement_values)}

    balance_names = ['An_Ca_bal', 'An_P_bal', 'An_Mg_bal', 'An_Na_bal', 'An_Cl_bal', 'An_K_bal', 'An_S_bal', 'An_Co_bal', 'An_Cu_bal', 'An_Fe_bal', 'An_Mn_bal', 'An_Se_bal', 'An_Zn_bal']
    balance_values = [An_Ca_bal, An_P_bal, An_Mg_bal, An_Na_bal, An_Cl_bal, An_K_bal, An_S_bal, An_Co_bal, An_Cu_bal, An_Fe_bal, An_Mn_bal, An_Se_bal, An_Zn_bal]
    mineral_balance = {variable: number.values[0] for variable, number in zip(balance_names, balance_values)}
    # .values[0] is used here to extract just the number without the labels that are inherited from the Series inputs

    return mineral_requirements, mineral_balance, An_DCADmeq

