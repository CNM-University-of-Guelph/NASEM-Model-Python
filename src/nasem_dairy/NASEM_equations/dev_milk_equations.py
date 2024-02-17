# dev_milk_equations
# All calculations related to milk production, milk components, and milk energy
from nasem_dairy.ration_balancer.ration_balancer_functions import check_coeffs_in_coeff_dict


def calculate_Trg_NEmilk_Milk(
        Trg_MilkFatp: float, 
        Trg_MilkTPp: float, 
        Trg_MilkLacp: float) -> float:
    """
    *Calculate Target (Trg) Net Energy of Milk (NEmilk) per Kilogram of Milk*

    Calculate the target energy output in Megacalories (Mcal/kg milk) based on the milk composition: fat, true protein, and lactose percentages. 

    Parameters
    ----------
    Trg_MilkFatp : float
        The target percentage of milk fat.
    Trg_MilkTPp : float
        The target percentage of milk true protein.
    Trg_MilkLacp : float
        The target percentage of milk lactose, typically about 4.85%.

    Returns
    -------
    float
        The target net energy of milk (NEmilk; Mcal/kg of milk)

    Notes
    -----
    - Reference to specific line in the Nutrient Requirements of Dairy Cattle R Code: 
        - If Lactose or TP missing: Line 384 & repeated on line 2887.
        - else: Line Line 386 & repeated on line 2888.
        - It was repeated in R code due to needing values for predicting DMI of lactating cows
    - Equations from the Nutrient Requirements of Dairy Cattle book:
        - If all milk fat, true protein, and lactose are known - Equation 3-14b 
        - If only milk fat known - Equation 3-14c
        - Note that equation using CP instead of TP is not implemented (Equation 3-14a) 
        - Also, see Equation 20-217 and 20-218
    
    - TODO: Currently, model can't catch when Trg_MilkTPp or Trg_MilkLacp is missing. No way to pass 'None' via input.csv. This first if statement is also not tested. 

    Examples
    --------
    ```{python}
    import nasem_dairy as nd

    # Example calculation of target net energy of milk
    nd.calculate_Trg_NEmilk_Milk(
        Trg_MilkFatp=3.5,  # 3.5% milk fat
        Trg_MilkTPp=3.0,   # 3.0% true protein
        Trg_MilkLacp=4.85   # 4.85% lactose
    )
    ```
    """    
    # If milk protein or milk lactose are missing use Tyrrell and Reid (1965) eqn.
    if Trg_MilkLacp is None or Trg_MilkTPp is None:
        Trg_NEmilk_Milk = 0.36 + 9.69 * Trg_MilkFatp/100    # Line 384/2887
    else:
        Trg_NEmilk_Milk = 9.29 * Trg_MilkFatp/100 + 5.85 * Trg_MilkTPp/100 + 3.95 * Trg_MilkLacp/100  # Line 386/2888
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


def calculate_Mlk_CP_g(Mlk_NP_g):
    Mlk_CP_g = Mlk_NP_g / 0.95  # Line 2213
    return Mlk_CP_g


def calculate_An_LactDay_MlkPred(An_LactDay: int) -> int:
    """
    An_LactDay_MlkPred: An_LactDay but capped at day 375
    """
    # Cap DIM at 375 d to prevent the polynomial from getting out of range, Line 2259
    if An_LactDay <= 375:
        An_LactDay_MlkPred = An_LactDay
    elif An_LactDay > 375:
        An_LactDay_MlkPred = 375

    return An_LactDay_MlkPred


def calculate_Trg_Mlk_Fat(Trg_MilkProd: float, Trg_MilkFatp: float) -> float:
    """
    Trg_Mlk_Fat: Target milk fat in kg, based on user input milk production and fat % 
    """
    Trg_Mlk_Fat = Trg_MilkProd * Trg_MilkFatp / 100  # Line 2262
    return Trg_Mlk_Fat


def calculate_Trg_Mlk_Fat_g(Trg_Mlk_Fat: float) -> float:
    """
    Trg_Mlk_Fat_g: Target milk fat g, based on user input milk production and fat % 
    """
    Trg_Mlk_Fat_g = Trg_Mlk_Fat * 1000  # Line 2263
    return Trg_Mlk_Fat_g


def calculate_Mlk_Fatemp_g(An_StatePhys: str, An_LactDay_MlkPred: int, Dt_DMIn: float, Dt_FAIn: float, Dt_DigC160In: float, Dt_DigC183In: float, Abs_Ile_g: float, Abs_Met_g: float):
    """
    Mlk_Fatemp_g: Milk fat prediciton, g, from Daley et al. no year given 

        Dt_FAIn (Number): Fatty acid intake, kg/d
        Dt_DigC160In (Number): Digestable C16:0 fatty acid intake, kg/d
        Dt_DigC183In (Number): Digestable C18:3 fatty acid intake, kg/d 
        
        Dt_DMIn (Number): Dry matter intake, kg/d
        
        An_LactDay_MlkPred: An_LactDay but capped at day 375, prevents polynomial from getting out of range

        Abs_Ile_g: Net absorbed hydrated Isoleucine (g/d) from diet, microbes and infusions 
        Abs_Met_g: Net absorbed hydrated Methionine (g/d) from diet, microbes and infusions
    """
    if An_StatePhys == "Lactating Cow":
        # Line 2259, (Equation 20-215, p. 440)
        Mlk_Fatemp_g = 453 - 1.42 * An_LactDay_MlkPred \
            + 24.52 * (Dt_DMIn - Dt_FAIn) \
            + 0.41 * Dt_DigC160In * 1000 \
            + 1.80 * Dt_DigC183In * 1000 \
            + 1.45 * Abs_Ile_g \
            + 1.34 * Abs_Met_g
    else:
        Mlk_Fatemp_g = 0    # Line 2261
    return Mlk_Fatemp_g


def calculate_Mlk_Fat_g(mFat_eqn: int, Trg_Mlk_Fat_g: float, Mlk_Fatemp_g: float) -> float:
    """
    Mlk_Fat_g: Predicted milk fat, g
    """
    if mFat_eqn == 0:
        Mlk_Fat_g = Trg_Mlk_Fat_g
    else:
        Mlk_Fat_g = Mlk_Fatemp_g
    return Mlk_Fat_g


def calculate_Mlk_Fat(Mlk_Fat_g: float) -> float:
    """
    Mlk_Fat: Milk fat, kg
    """
    Mlk_Fat = Mlk_Fat_g / 1000  # Line 2267
    return Mlk_Fat


def calculate_Mlk_NP(Mlk_NP_g: float) -> float:
    """
    Mlk_NP: Net protein in milk, kg NP/d
    """
    Mlk_NP = Mlk_NP_g / 1000    # Line 2210
    return Mlk_NP


def calculate_Mlk_Prod_comp(An_Breed: str, Mlk_NP: float, Mlk_Fat: float, An_DEIn: float, An_LactDay_MlkPred: int, An_Parity_rl: int) -> float:
    """
    Mlk_Prod_comp: Component based milk production prediciton, kg/d
    An_DEIn (Number): Digestible energy intake in Mcal/d
        An_LactDay_MlkPred (Number): A variable to max the days in milk at 375 to prevent polynomial from getting out of range
        An_Parity_rl (Number): Animal Parity where 1 = Primiparous and 2 = Multiparous.
    """
    # Component based milk production prediction; derived by regression from predicted milk protein and milk fat
    # Holstein equation, Line 2275
    Mlk_Prod_comp = 4.541 \
        + 11.13 * Mlk_NP \
        + 2.648 * Mlk_Fat \
        + 0.1829 * An_DEIn \
        - 0.06257 * (An_LactDay_MlkPred - 137.1) \
        + 2.766e-4 * (An_LactDay_MlkPred - 137.1)**2 \
        + 1.603e-6 * (An_LactDay_MlkPred - 137.1)**3 \
        - 7.397e-9 * (An_LactDay_MlkPred - 137.1)**4 \
        + 1.567 * (An_Parity_rl - 1)

    if An_Breed == "Jersey":
        Mlk_Prod_comp = Mlk_Prod_comp - 3.400   # Line 2278
    elif (An_Breed != "Jersey") & (An_Breed != "Holstein"):
        Mlk_Prod_comp = Mlk_Prod_comp - 1.526
    return Mlk_Prod_comp


def calculate_An_MPavail_Milk_Trg(An_MPIn: float, An_MPuse_g_Trg: float, Mlk_MPUse_g_Trg: float) -> float:
    """
    An_MPavail_Milk_Trg: Metabolizalbe protein available for milk production, kg MP

    An_MPuse_g_Trg (Number): Metabolizable protein requirement, g/d
        Mlk_MPuse_g_Trg (Number): Metabolizable protein requirement for milk, g/d
        An_MPIn (Number): Metabolizlable protein intake, kg/d 
        Trg_MilkTPp (Percentage): Animal Milk True Protein percentage
        coeff_dict (Dict): Dictionary containing all coefficients for the model
    """
    An_MPavail_Milk_Trg = An_MPIn - An_MPuse_g_Trg / 1000 + Mlk_MPUse_g_Trg / 1000    # Line 2706
    return An_MPavail_Milk_Trg


def calculate_Mlk_NP_MPalow_Trg_g(An_MPavail_Milk_Trg: float, coeff_dict: dict) -> float:
    """
    Mlk_NP_MPalow_Trg_g: net protein available for milk production, g milk NP/d
    """
    req_coeff = ['Kx_MP_NP_Trg']
    check_coeffs_in_coeff_dict(coeff_dict, req_coeff)
    Mlk_NP_MPalow_Trg_g = An_MPavail_Milk_Trg * coeff_dict['Kx_MP_NP_Trg'] * 1000   # g milk NP/d, Line 2707
    return Mlk_NP_MPalow_Trg_g


def calculate_Mlk_Prod_MPalow(Mlk_NP_MPalow_Trg_g: float, Trg_MilkTPp: float) -> float:
    """
    Mlk_Prod_MPalow: Metabolizable protein allowable milk production, kg/d
    """
    Mlk_Prod_MPalow = Mlk_NP_MPalow_Trg_g / (Trg_MilkTPp / 100) / 1000  
    # Line 2708, kg milk/d using Trg milk protein % to predict volume
    return Mlk_Prod_MPalow


def calculate_An_MEavail_Milk(An_MEIn: float, An_MEgain: float, An_MEmUse: float, Gest_MEuse: float) -> float:
    """
    An_MEavail_Milk: Metabolisable energy available milk production, Mcal/d
    """
    An_MEavail_Milk = An_MEIn - An_MEgain - An_MEmUse - Gest_MEuse  # Line 2897
    return An_MEavail_Milk


def calculate_Mlk_Prod_NEalow(An_MEavail_Milk: float, Trg_NEmilk_Milk: float, coeff_dict: dict) -> float:
    """
    Mlk_Prod_NEalow: Net energy allowable milk production, kg/d
    """
    req_coeff = ['Kl_ME_NE']
    check_coeffs_in_coeff_dict(coeff_dict, req_coeff)
    # Line 2898, Energy allowable Milk Production, kg/d
    Mlk_Prod_NEalow = An_MEavail_Milk * coeff_dict['Kl_ME_NE'] / Trg_NEmilk_Milk
    return Mlk_Prod_NEalow

def calculate_MlkNP_Milk(An_StatePhys: str, Mlk_NP_g: float, Mlk_Prod: float):
    """
    MlkNP_Milk: Net protein content of milk, g/g
    """
    if An_StatePhys == "Lactating Cow": 
        MlkNP_Milk = Mlk_NP_g / 1000 / Mlk_Prod # Milk true protein, g/g, Line 2907-2908
    else:
        MlkNP_Milk = 0
    return MlkNP_Milk


def calculate_Mlk_Prod(An_StatePhys: str, mProd_eqn: int, Mlk_Prod_comp: float, Mlk_Prod_NEalow: float, Mlk_Prod_MPalow: float, Trg_MilkProd: float) -> float:
    """
    Mlk_Prod: Milk production, kg/d, can be user entered target or a prediction 
    """
    if An_StatePhys == "Lactating Cow" and mProd_eqn==1:    # Milk production from component predictions, Line 2282
        Mlk_Prod = Mlk_Prod_comp
    elif An_StatePhys == "Lactating Cow" and mProd_eqn==2:  # use NE Allowable Milk prediction, Line 2899
        Mlk_Prod = Mlk_Prod_NEalow
    elif An_StatePhys == "Lactating Cow" and mProd_eqn==3:  # Use MP Allowable based predictions, Line 2709
        Mlk_Prod = Mlk_Prod_MPalow
    elif An_StatePhys == "Lactating Cow" and mProd_eqn==4:  # Use min of NE and MP Allowable, Line 2900
        Mlk_Prod = min(Mlk_Prod_NEalow, Mlk_Prod_MPalow)
    else:
        Mlk_Prod = Trg_MilkProd     # Use user entered production if no prediction selected or if not a lactating cow
    return Mlk_Prod
