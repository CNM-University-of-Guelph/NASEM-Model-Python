from nasem_dairy.ration_balancer.ration_balancer_functions import check_coeffs_in_coeff_dict

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


def calculate_Mlk_Prod(An_StatePhys, mProd_eqn, Mlk_Prod_comp, Mlk_Prod_NEalow, Mlk_Prod_MPalow, Trg_MilkProd):
# Takes all milk production predictions and determines which to use as the milk production for future calculations 
    if An_StatePhys == "Lactating Cow" and mProd_eqn==1:    #Milk production from component predictions
        Mlk_Prod = Mlk_Prod_comp
    elif An_StatePhys == "Lactating Cow" and mProd_eqn==2:  #use NE Allowable Milk prediction
        Mlk_Prod = Mlk_Prod_NEalow
    elif An_StatePhys == "Lactating Cow" and mProd_eqn==3:  #Use MP Allowable based predictions
        Mlk_Prod = Mlk_Prod_MPalow
    elif An_StatePhys == "Lactating Cow" and mProd_eqn==4:
        Mlk_Prod = min(Mlk_Prod_NEalow,Mlk_Prod_MPalow)
    else:
        Mlk_Prod = Trg_MilkProd     # Use user entered production if no prediction selected or if not a lactating cow
        
    return Mlk_Prod


def calculate_MlkNE_Milk(Mlk_Prod, Mlk_Fat_g, MlkNP_Milk, Trg_MilkLacp):
    if Mlk_Prod == 0:
        MlkNE_Milk = 0
    else:
        Mlk_Fat = Mlk_Fat_g / 1000
        MlkFat_Milk = Mlk_Fat / Mlk_Prod
        MlkNE_Milk = 9.29 * MlkFat_Milk + 5.85 * MlkNP_Milk + 3.95 * Trg_MilkLacp / 100     # Line 2916
    return MlkNE_Milk


def calculate_Mlk_MEout(Mlk_Prod, MlkNE_Milk, coeff_dict):
    req_coeffs = ['Kl_ME_NE']
    check_coeffs_in_coeff_dict(coeff_dict, req_coeffs)

    Mlk_NEout = MlkNE_Milk * Mlk_Prod                                           # Line 2917
    Mlk_MEout = Mlk_NEout / coeff_dict['Kl_ME_NE']                              # Line 2918

    return Mlk_MEout
