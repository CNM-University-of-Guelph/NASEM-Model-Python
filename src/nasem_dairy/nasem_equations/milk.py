"""Milk production and composition calculations.

This module covers calculations related to milk production, including the 
estimation of milk energy content, protein, fat, and lactose yields.
"""
import numpy as np
import pandas as pd


def calculate_Trg_NEmilk_Milk(
    Trg_MilkFatp: float, 
    Trg_MilkTPp: float,
    Trg_MilkLacp: float
) -> float:
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
        Trg_NEmilk_Milk = 0.36 + 9.69 * Trg_MilkFatp / 100  # Line 384/2887
    else:
        Trg_NEmilk_Milk = (9.29 * Trg_MilkFatp / 100 + 
                           5.85 * Trg_MilkTPp / 100 + 
                           3.95 * Trg_MilkLacp / 100)  # Line 386/2888
    return Trg_NEmilk_Milk


def calculate_Mlk_NP_g(
    An_StatePhys: str, 
    mPrt_eqn: int,
    Trg_Mlk_NP_g: float,
    An_BW: float, 
    Abs_AA_g: pd.Series, 
    mPrt_k_AA: pd.Series, 
    Abs_neAA_g: float,
    Abs_OthAA_g: float, 
    Abs_EAA2b_g: float, 
    mPrt_k_EAA2: float, 
    An_DigNDF: float,
    An_DEInp: float, 
    An_DEStIn: float, 
    An_DEFAIn: float, 
    An_DErOMIn: float, 
    An_DENDFIn: float,
    mPrt_coeff: dict
) -> float:
    """
    Examples
    --------
    ```python
    mPrt_coeff = {
        'mPrt_k_NEAA': 0, 'mPrt_k_OthAA': 0.07773, 'mPrt_k_DEInp': 10.79,
        'mPrt_k_DigNDF': -4.595, 'mPrt_k_DEIn_StFA': 0, 'mPrt_k_DEIn_NDF': 0,
        'mPrt_k_BW': -0.4201, 'mPrt_Int': -97.0
    }
    Abs_AA_g = pd.Series({'Arg': 1.0, 'His': 0.5, 'Ile': 1.2, 'Leu': 1.5, 'Lys': 1.1,
                           'Met': 0.8, 'Phe': 1.0, 'Thr': 0.9, 'Trp': 0.7, 'Val': 1.3})
    mPrt_k_AA = pd.Series({'Arg': 0.02, 'His': 0.03, 'Ile': 0.04, 'Leu': 0.05, 'Lys': 0.06,
                           'Met': 0.07, 'Phe': 0.08, 'Thr': 0.09, 'Trp': 0.10, 'Val': 0.11})

    calculate_Mlk_NP_g(
        An_StatePhys = "Lactating Cow", mPrt_eqn = 1, Trg_Mlk_NP_g = 100.0, 
        An_BW = 650, Abs_AA_g = Abs_AA_g, mPrt_k_AA = mPrt_k_AA, Abs_neAA_g = 0.5, 
        Abs_OthAA_g = 0.3, Abs_EAA2b_g = 0.4, mPrt_k_EAA2 = 0.2, An_DigNDF = 25.0, 
        An_DEInp = 30.0, An_DEStIn = 15.0, An_DEFAIn = 10.0, An_DErOMIn = 5.0, 
        An_DENDFIn = 20.0, mPrt_coeff = mPrt_coeff
    )
    ```
    """
    if An_StatePhys != "Lactating Cow":  # Line 2204
        Mlk_NP_g = 0
    elif mPrt_eqn == 0:
        Mlk_NP_g = Trg_Mlk_NP_g
    else:
        Mlk_NP_g = (mPrt_coeff['mPrt_Int'] + 
                    Abs_AA_g['Arg'] * mPrt_k_AA['Arg'] + 
                    Abs_AA_g['His'] * mPrt_k_AA['His'] + 
                    Abs_AA_g['Ile'] * mPrt_k_AA['Ile'] + 
                    Abs_AA_g['Leu'] * mPrt_k_AA['Leu'] + 
                    Abs_AA_g['Lys'] * mPrt_k_AA['Lys'] + 
                    Abs_AA_g['Met'] * mPrt_k_AA['Met'] + 
                    Abs_AA_g['Phe'] * mPrt_k_AA['Phe'] + 
                    Abs_AA_g['Thr'] * mPrt_k_AA['Thr'] + 
                    Abs_AA_g['Trp'] * mPrt_k_AA['Trp'] + 
                    Abs_AA_g['Val'] * mPrt_k_AA['Val'] + 
                    Abs_neAA_g * mPrt_coeff['mPrt_k_NEAA'] + 
                    Abs_OthAA_g * mPrt_coeff['mPrt_k_OthAA'] + 
                    Abs_EAA2b_g * mPrt_k_EAA2 + 
                    An_DEInp * mPrt_coeff['mPrt_k_DEInp'] + 
                    (An_DigNDF - 17.06) * mPrt_coeff['mPrt_k_DigNDF'] + 
                    (An_DEStIn + An_DEFAIn + 
                     An_DErOMIn) * mPrt_coeff['mPrt_k_DEIn_StFA'] + 
                    An_DENDFIn * mPrt_coeff['mPrt_k_DEIn_NDF'] + 
                    (An_BW - 612) * mPrt_coeff['mPrt_k_BW'])
    return Mlk_NP_g


def calculate_Mlk_CP_g(Mlk_NP_g: float) -> float:
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


def calculate_Mlk_Fatemp_g(
    An_StatePhys: str, 
    An_LactDay_MlkPred: int,
    Dt_DMIn: float, 
    Dt_FAIn: float, 
    Dt_DigC160In: float,
    Dt_DigC183In: float,
    Abs_AA_g: pd.Series 
) -> float:
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
        Mlk_Fatemp_g = (453 - 1.42 * An_LactDay_MlkPred + 
                        24.52 * (Dt_DMIn - Dt_FAIn) + 
                        0.41 * Dt_DigC160In * 1000 + 
                        1.80 * Dt_DigC183In * 1000 + 
                        1.45 * Abs_AA_g["Ile"] + 
                        1.34 * Abs_AA_g["Met"])
    else:
        Mlk_Fatemp_g = 0  # Line 2261
    return Mlk_Fatemp_g


def calculate_Mlk_Fat_g(
    mFat_eqn: int, 
    Trg_Mlk_Fat_g: float,
    Mlk_Fatemp_g: float
) -> float:
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
    Mlk_NP = Mlk_NP_g / 1000  # Line 2210
    return Mlk_NP


def calculate_Mlk_Prod_comp(
    An_Breed: str, 
    Mlk_NP: float, 
    Mlk_Fat: float,
    An_DEIn: float, 
    An_LactDay_MlkPred: int,
    An_Parity_rl: int
) -> float:
    """
    Mlk_Prod_comp: Component based milk production prediciton, kg/d
    An_DEIn (Number): Digestible energy intake in Mcal/d
        An_LactDay_MlkPred (Number): A variable to max the days in milk at 375 to prevent polynomial from getting out of range
        An_Parity_rl (Number): Animal Parity where 1 = Primiparous and 2 = Multiparous.
    """
    # Component based milk production prediction; derived by regression from predicted milk protein and milk fat
    # Holstein equation, Line 2275
    Mlk_Prod_comp = (4.541 + 11.13 * Mlk_NP + 
                     2.648 * Mlk_Fat + 
                     0.1829 * An_DEIn - 
                     0.06257 * (An_LactDay_MlkPred - 137.1) + 
                     2.766e-4 * (An_LactDay_MlkPred - 137.1)**2 + 
                     1.603e-6 * (An_LactDay_MlkPred - 137.1)**3 - 
                     7.397e-9 * (An_LactDay_MlkPred - 137.1)**4 + 
                     1.567 * (An_Parity_rl - 1))
    if An_Breed == "Jersey":
        Mlk_Prod_comp = Mlk_Prod_comp - 3.400  # Line 2278
    elif (An_Breed != "Jersey") & (An_Breed != "Holstein"):
        Mlk_Prod_comp = Mlk_Prod_comp - 1.526
    return Mlk_Prod_comp


def calculate_An_MPavail_Milk_Trg(
    An_MPIn: float, 
    An_MPuse_g_Trg: float,
    Mlk_MPUse_g_Trg: float
) -> float:
    """
    An_MPavail_Milk_Trg: Metabolizalbe protein available for milk production, kg MP

    An_MPuse_g_Trg (Number): Metabolizable protein requirement, g/d
        Mlk_MPuse_g_Trg (Number): Metabolizable protein requirement for milk, g/d
        An_MPIn (Number): Metabolizlable protein intake, kg/d 
        Trg_MilkTPp (Percentage): Animal Milk True Protein percentage
        coeff_dict (Dict): Dictionary containing all coefficients for the model
    """
    An_MPavail_Milk_Trg = An_MPIn - An_MPuse_g_Trg / 1000 + Mlk_MPUse_g_Trg / 1000  
    # Line 2706
    return An_MPavail_Milk_Trg


def calculate_Mlk_NP_MPalow_Trg_g(
    An_MPavail_Milk_Trg: float,
    coeff_dict: dict
) -> float:
    """
    Mlk_NP_MPalow_Trg_g: net protein available for milk production, g milk NP/d
    
    Examples
    --------
    ```python
    coeff_dict = {"Kx_MP_NP_Trg": 0.69}
    
    calculate_Mlk_NP_MPalow_Trg_g(
        An_MPavail_Milk_Trg = 5.0, coeff_dict = coeff_dict
    )
    ```
    """
    Mlk_NP_MPalow_Trg_g = An_MPavail_Milk_Trg * coeff_dict['Kx_MP_NP_Trg'] * 1000  
    # g milk NP/d, Line 2707
    return Mlk_NP_MPalow_Trg_g


def calculate_Mlk_Prod_MPalow(
    Mlk_NP_MPalow_Trg_g: float,
    Trg_MilkTPp: float
) -> float:
    """
    Mlk_Prod_MPalow: Metabolizable protein allowable milk production, kg/d
    """
    if Trg_MilkTPp != 0:
        Mlk_Prod_MPalow = Mlk_NP_MPalow_Trg_g / (Trg_MilkTPp / 100) / 1000
    else:
        Mlk_Prod_MPalow = None
    # Line 2708, kg milk/d using Trg milk protein % to predict volume
    return Mlk_Prod_MPalow


def calculate_An_MEavail_Milk(
    An_MEIn: float, 
    An_MEgain: float,
    An_MEmUse: float, 
    Gest_MEuse: float
) -> float:
    """
    An_MEavail_Milk: Metabolisable energy available milk production, Mcal/d
    """
    An_MEavail_Milk = An_MEIn - An_MEgain - An_MEmUse - Gest_MEuse  # Line 2897
    return An_MEavail_Milk


def calculate_Mlk_Prod_NEalow(
    An_MEavail_Milk: float, 
    Trg_NEmilk_Milk: float,
    coeff_dict: dict
) -> float:
    """
    Mlk_Prod_NEalow: Net energy allowable milk production, kg/d
    
    Examples
    --------
    ```python
    coeff_dict = {"Kl_ME_NE": 0.66}
    
    calculate_Mlk_Prod_NEalow(
        An_MEavail_Milk = 12.0, Trg_NEmilk_Milk = 1.5, coeff_dict = coeff_dict
    )
    ```
    """
    if Trg_NEmilk_Milk != 0 and not np.isnan(Trg_NEmilk_Milk):
        Mlk_Prod_NEalow = An_MEavail_Milk * coeff_dict['Kl_ME_NE'] / Trg_NEmilk_Milk
    else:
        Mlk_Prod_NEalow = np.nan 
    # Line 2898, Energy allowable Milk Production, kg/d
    return Mlk_Prod_NEalow


def calculate_MlkNP_Milk(
    An_StatePhys: str, 
    Mlk_NP_g: float, 
    Mlk_Prod: float
) -> float:
    """
    MlkNP_Milk: Net protein content of milk, g/g
    """
    if An_StatePhys == "Lactating Cow":
        MlkNP_Milk = Mlk_NP_g / 1000 / Mlk_Prod  
        # Milk true protein, g/g, Line 2907-2908
    else:
        MlkNP_Milk = 0
    return MlkNP_Milk


def calculate_Mlk_Prod(
    An_StatePhys: str, 
    mProd_eqn: int, 
    Mlk_Prod_comp: float,
    Mlk_Prod_NEalow: float, 
    Mlk_Prod_MPalow: float,
    Trg_MilkProd: float
) -> float:
    """
    Mlk_Prod: Milk production, kg/d, can be user entered target or a prediction 
    """
    if An_StatePhys == "Lactating Cow" and mProd_eqn == 1:  
        # Milk production from component predictions, Line 2282
        Mlk_Prod = Mlk_Prod_comp
    elif An_StatePhys == "Lactating Cow" and mProd_eqn == 2:  
        # use NE Allowable Milk prediction, Line 2899
        Mlk_Prod = Mlk_Prod_NEalow
    elif An_StatePhys == "Lactating Cow" and mProd_eqn == 3:  
        # Use MP Allowable based predictions, Line 2709
        Mlk_Prod = Mlk_Prod_MPalow
    elif An_StatePhys == "Lactating Cow" and mProd_eqn == 4:  
        # Use min of NE and MP Allowable, Line 2900
        Mlk_Prod = min(Mlk_Prod_NEalow, Mlk_Prod_MPalow)
    else:
        Mlk_Prod = Trg_MilkProd  
        # Use user entered production if no prediction selected or if not a lactating cow
    return Mlk_Prod


def calculate_MlkFat_Milk(
    An_StatePhys: str, 
    Mlk_Fat: float,
    Mlk_Prod: float
) -> float:
    """
    MlkFat_Milk: Milk fat g/g 
    """
    if An_StatePhys == "Lactating Cow":
        MlkFat_Milk = Mlk_Fat / Mlk_Prod  # Milk Fat, g/g, Line 2909
    else:
        MlkFat_Milk = 0
    return MlkFat_Milk


def calculate_MlkNE_Milk(
    MlkFat_Milk: float, 
    MlkNP_Milk: float,
    Trg_MilkLacp: float
) -> float:
    """
    MlkNE_Milk: NE content of milk, NE/kg
    """
    MlkNE_Milk = (9.29 * MlkFat_Milk + 
                  5.85 * MlkNP_Milk + 
                  3.95 * Trg_MilkLacp / 100)  # Line 2916
    return MlkNE_Milk


def calculate_Mlk_NEout(MlkNE_Milk: float, Mlk_Prod: float) -> float:
    """
    Mlk_NEout: Total NE in milk Mcal/d
    """
    Mlk_NEout = MlkNE_Milk * Mlk_Prod  # Line 2918
    return Mlk_NEout


def calculate_Mlk_MEout(Mlk_NEout: float, coeff_dict: dict) -> float:
    """
    Mlk_MEout: Total ME in milk Mcal/d

    Examples
    --------
    ```python
    coeff_dict = {"Kl_ME_NE": 0.66}
    
    calculate_Mlk_MEout(
        Mlk_NEout = 3.0, coeff_dict = coeff_dict
    )
    ```
    """
    Mlk_MEout = Mlk_NEout / coeff_dict['Kl_ME_NE']
    return Mlk_MEout


def calculate_Mlk_NPmx(
    mPrtmx_AA2: pd.Series, 
    An_DEInp: float, 
    An_DigNDF: float,
    An_BW: float, 
    Abs_neAA_g: float, 
    Abs_OthAA_g: float,
    mPrt_coeff: dict
) -> float:
    """
    Mlk_NPmx: Maximal milk protein output at the entered DE, DigNDF, and BW
    """
    # Calculate the maximal milk protein output at the entered DE, DigNDF, and BW
    Mlk_NPmx = (mPrt_coeff['mPrt_Int'] + mPrtmx_AA2['Arg'] + 
                mPrtmx_AA2['His'] + mPrtmx_AA2['Ile'] + 
                mPrtmx_AA2['Leu'] + mPrtmx_AA2['Lys'] + 
                mPrtmx_AA2['Met'] + mPrtmx_AA2['Thr'] + 
                mPrtmx_AA2['Val'] + 
                An_DEInp * mPrt_coeff['mPrt_k_DEInp'] + 
                (An_DigNDF - 17.06) * mPrt_coeff['mPrt_k_DigNDF'] + 
                (An_BW - 612) * mPrt_coeff['mPrt_k_BW'] + 
                Abs_neAA_g * mPrt_coeff['mPrt_k_NEAA'] + 
                Abs_OthAA_g * mPrt_coeff['mPrt_k_OthAA']) # Line 2195-2197
    return Mlk_NPmx


def calculate_MlkNP_MlkNPmx(Mlk_NP_g: float, Mlk_NPmx: float) -> float:
    """
    MlkNP_MlkNPmx: Predicted milk net protein as fraction of maximum milk net protein
    """
    # Calculate predicted Mlk_NP as proportion of max mPrt for reporting 
    # purposes. This value should not exceed ~0.8 for an 18% CP diet with ~60% 
    # MP for peak production. (0.8 needs refinement). If it does, this is an 
    # indication that the genetic potential scalar, f_mPrt_max, is set too low
    MlkNP_MlkNPmx = Mlk_NP_g / Mlk_NPmx  # Line 2202
    return MlkNP_MlkNPmx


def calculate_Mlk_CP(Mlk_CP_g: float) -> float:
    """
    Mlk_CP: Milk crude protein (kg)
    """
    Mlk_CP = Mlk_CP_g / 1000  # Line 2213
    return Mlk_CP


def calculate_Mlk_AA_TP(aa_list: list, coeff_dict: dict) -> np.ndarray:
    Mlk_AA_TP = np.array([coeff_dict[f"Mlk_{aa}_TP"] for aa in aa_list])
    return Mlk_AA_TP


def calculate_Mlk_AA_g(
    Mlk_NP_g: float,
    Mlk_AA_TP: float
) -> pd.Series:
    """
    Mlk_AA_g: aa output in milk protein 
    """
    Mlk_AA_g = Mlk_NP_g * Mlk_AA_TP / 100  # Line 2216-2225
    return Mlk_AA_g


def calculate_Mlk_EAA_g(Mlk_AA_g: pd.Series) -> float:
    """
    Mlk_EAA_g: Total EAA in milk protein 
    """
    Mlk_EAA_g = Mlk_AA_g.sum()  # Line 2226
    return Mlk_EAA_g


def calculate_MlkNP_AnMP(Mlk_NP_g: float, An_MPIn_g: float) -> float:
    """
    MlkNP_AnMP: Milk protein as a fraction of metabolizable protein 
    """
    MlkNP_AnMP = Mlk_NP_g / An_MPIn_g  # Line 2229
    return MlkNP_AnMP


def calculate_MlkAA_AbsAA(
    Mlk_AA_g: pd.Series,
    Abs_AA_g: pd.Series
) -> pd.Series:
    """
    MlkAA_AbsAA: Milk aa efficiency as fraction of absorbed aa
    """
    MlkAA_AbsAA = Mlk_AA_g / Abs_AA_g  # Line 2230-2239
    return MlkAA_AbsAA


def calculate_MlkEAA_AbsEAA(Mlk_EAA_g: float, Abs_EAA_g: float) -> float:
    """
    MlkEAA_AbsEAA: Milk EAA as a fraction of absorbed EAA
    """
    MlkEAA_AbsEAA = Mlk_EAA_g / Abs_EAA_g  # Line 2240
    return MlkEAA_AbsEAA


def calculate_MlkNP_AnCP(Mlk_NP_g: float, An_CPIn: float) -> float:
    """
    MlkNP_AnCP: Milk net protein as fraction of crude protein intake (g/g)
    """
    MlkNP_AnCP = Mlk_NP_g / (An_CPIn * 1000)  # Line 2242
    return MlkNP_AnCP


def calculate_MlkAA_DtAA(
    Mlk_AA_g: pd.Series,
    Dt_AAIn: np.ndarray
) -> float:
    """
    MlkAA_DtAA: Milk aa as a fraction of diet aa intake (g/g)
    """
    MlkAA_DtAA = Mlk_AA_g / Dt_AAIn  # Line 2243-2252
    return MlkAA_DtAA


def calculate_Mlk_MPUse_g(Mlk_NP_g: float, Kl_MP_NP: float) -> float:
    """
    Mlk_MPUse_g: MP used for milk produciton (kg MP/d)
    """
    Mlk_MPUse_g = Mlk_NP_g / Kl_MP_NP  # kg MP/d for lactation, Line 2728
    return Mlk_MPUse_g


def calculate_Trg_MilkLac(Trg_MilkLacp: float, Trg_MilkProd: float) -> float:
    """
    Trg_MilkLac: Target milk lactose (kg/d)
    """
    Trg_MilkLac = Trg_MilkLacp / 100 * Trg_MilkProd  # Line 2886
    return Trg_MilkLac


def calculate_Trg_NEmilk_DEIn(Trg_Mlk_NEout: float, An_DEIn: float) -> float:
    """
    Trg_NEmilk_DEIn: Target milk energy as a proportion of DE intake (Mcal/Mcal)
    """
    Trg_NEmilk_DEIn = Trg_Mlk_NEout / An_DEIn  # Line 2891
    return Trg_NEmilk_DEIn


def calculate_Trg_MilkProd_EPcor(
    Trg_MilkProd: float, 
    Trg_MilkFatp: float,
    Trg_MilkTPp: float
) -> float:
    """
    Trg_MilkProd_EPcor: Energy and protein corrected milk (kg/d)
    """
    Trg_MilkProd_EPcor = (0.327 * Trg_MilkProd + 
                          (12.97 * Trg_MilkFatp / 100 * Trg_MilkProd) + 
                          (7.65 * Trg_MilkTPp / 100 * Trg_MilkProd))
    # energy and protein corrected milk, Line 2892-2893
    return Trg_MilkProd_EPcor


def calculate_Mlk_Prod_NEalow_EPcor(
    Mlk_Prod_NEalow: float, 
    Trg_MilkFatp: float,
    Trg_MilkTPp: float
) -> float:
    """
    Mlk_Prod_NEalow_EPcor: NE allowable energy and protein corrected milk production (kg/d)
    """
    if (np.isnan(Mlk_Prod_NEalow) or np.isnan(Trg_MilkFatp) or 
        np.isnan(Trg_MilkTPp) or Mlk_Prod_NEalow <= 0 or 
        Trg_MilkFatp <= 0 or Trg_MilkTPp <= 0
        ):
        Mlk_Prod_NEalow_EPcor = np.nan
    else:
        Mlk_Prod_NEalow_EPcor = 0.327 * Mlk_Prod_NEalow + (
            12.97 * Trg_MilkFatp / 100 * Mlk_Prod_NEalow) + (
                7.65 * Trg_MilkTPp / 100 * Mlk_Prod_NEalow
            )  # energy and protein corrected milk, Line 2901-2902
    return Mlk_Prod_NEalow_EPcor


def calculate_Mlk_EPcorNEalow_DMIn(
    Mlk_Prod_NEalow_EPcor: float,
    An_DMIn: float
) -> float:
    """
    Mlk_EPcorNEalow_DMIn: NE allowable energy and protein corrected milk production as a proportion of DMI (kg/kg)
    """
    Mlk_EPcorNEalow_DMIn = Mlk_Prod_NEalow_EPcor / An_DMIn  # Line 2903
    return Mlk_EPcorNEalow_DMIn


def calculate_MlkNP_Milk_p(MlkNP_Milk: float) -> float:
    """
    MlkNP_Milk_p: Milk NP % of milk production
    """
    MlkNP_Milk_p = MlkNP_Milk * 100  # Line 2913
    return MlkNP_Milk_p


def calculate_MlkFat_Milk_p(MlkFat_Milk: float) -> float:
    """
    MlkFat_Milk_p: Milk fat % of milk production
    """
    MlkFat_Milk_p = MlkFat_Milk * 100  # Line 2914
    return MlkFat_Milk_p


def calculate_Mlk_NE_DE(Mlk_NEout: float, An_DEIn: float) -> float:
    """
    Mlk_NE_DE: Milk NE as a proportion of DE intake
    """
    Mlk_NE_DE = Mlk_NEout / An_DEIn  # proportion of DEIn used for milk, Line 2920
    return Mlk_NE_DE


def calculate_MlkNP_Int(An_BW: float, mPrt_coeff: dict) -> float:
    """
    MlkNP_Int: ?
    """
    MlkNP_Int = mPrt_coeff['mPrt_Int'] + (An_BW - 612) * mPrt_coeff['mPrt_k_BW']
    # Line 3179
    return MlkNP_Int


def calculate_MlkNP_DEInp(An_DEInp: float, mPrt_coeff: dict) -> float:
    """
    MlkNP_DEInp: ?
    """
    MlkNP_DEInp = An_DEInp * mPrt_coeff['mPrt_k_DEInp']  # Line 3180
    return MlkNP_DEInp


def calculate_MlkNP_NDF(An_DigNDF: float, mPrt_coeff: dict) -> float:
    """
    MlkNP_NDF: ?
    """
    MlkNP_NDF = (An_DigNDF - 17.06) * mPrt_coeff['mPrt_k_DigNDF']
    return MlkNP_NDF


def calculate_MlkNP_AbsAA(
    Abs_AA_g: pd.Series,
    mPrt_k_AA: pd.Series
) -> pd.Series:
    """
    MlkNP_AbsAA: ?
    """
    MlkNP_AbsAA = Abs_AA_g * mPrt_k_AA  # Line 3182-3191
    return MlkNP_AbsAA


def calculate_MlkNP_AbsEAA(Abs_EAA2b_g: float, mPrt_k_EAA2: float) -> float:
    """
    MlkNP_AbsEAA: ?
    """
    MlkNP_AbsEAA = Abs_EAA2b_g * mPrt_k_EAA2  # Line 3192
    return MlkNP_AbsEAA


def calculate_MlkNP_AbsNEAA(Abs_neAA_g: float, mPrt_coeff: dict) -> float:
    """
    MlkNP_AbsNEAA: ? 
    """
    MlkNP_AbsNEAA = Abs_neAA_g * mPrt_coeff['mPrt_k_NEAA']  # Line 3193
    return MlkNP_AbsNEAA


def calculate_MlkNP_AbsOthAA(Abs_OthAA_g: float, mPrt_coeff: dict) -> float:
    """
    MlkNP_AbsOthAA: ?
    """
    MlkNP_AbsOthAA = Abs_OthAA_g * mPrt_coeff['mPrt_k_OthAA']
    return MlkNP_AbsOthAA


def calculate_Trg_Mlk_NP(Trg_Mlk_NP_g: float) -> float:
    Trg_Mlk_NP = Trg_Mlk_NP_g / 1000    # Line 2205
    return Trg_Mlk_NP
