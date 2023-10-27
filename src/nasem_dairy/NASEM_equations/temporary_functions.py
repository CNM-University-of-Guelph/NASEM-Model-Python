def temp_MlkNP_Milk(An_StatePhys, Mlk_NP_g, Mlk_Prod_comp, Trg_MilkProd):

    if An_StatePhys == "Lactating Cow":
        Mlk_Prod = Mlk_Prod_comp
    else:
        Mlk_Prod = Trg_MilkProd #This means that for a dry cow it uses the Target Milk Production, but it can't be 0 because it throws error
        # therefore it seems that they needed the extra flag below to force to 0 ?

    
    if An_StatePhys != "Lactating Cow":
        MlkNP_Milk = 0
    else:
        MlkNP_Milk = (Mlk_NP_g / 1000) / Mlk_Prod	#Milk true protein, g/g

    return MlkNP_Milk

def temp_calc_An_DigTPaIn(Fe_CP, diet_info):
    # Dt_TPIn = sum(Fd_TPIn)
    An_TPIn = diet_info.loc['Diet', 'Fd_TPIn']

    An_DigTPaIn = An_TPIn  - Fe_CP #- InfArt_CPIn, no infusions in the model at this point

    return An_DigTPaIn


def temp_calc_An_GasEOut(An_DigNDF, An_StatePhys, diet_info, Dt_DMIn):
    An_GasEOut_Dry = 0.69 + 0.053 * diet_info.loc['Diet', 'Fd_GEIn'] - 0.07 * diet_info.loc['Diet', 'Fd_FAIn'] / Dt_DMIn * 100 

    An_GasEOut_Lact = 0.294 * Dt_DMIn - 0.347 * diet_info.loc['Diet', 'Fd_FAIn'] / Dt_DMIn * 100 + 0.0409 * An_DigNDF

    An_GasEOut_Heif = -0.038 + 0.051 * diet_info.loc['Diet', 'Fd_GEIn'] + 0.0091 * diet_info.loc['Diet', 'Fd_NDF_%_diet'] * 100

    if An_StatePhys == 'Dry Cow':
        An_GasEOut = An_GasEOut_Dry
    # elif An_StatePhys == 'Calf':
    #     An_GasEOut = An_GasEOut_Clf
    elif An_StatePhys == 'Lactating Cow':
        An_GasEOut = An_GasEOut_Lact
    elif An_StatePhys == 'Heifer':
        An_GasEOut = An_GasEOut_Heif

    return An_GasEOut

