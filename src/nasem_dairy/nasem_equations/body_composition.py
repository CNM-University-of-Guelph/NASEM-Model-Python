"""Functions to calculate values related to the body composition of animals.

This includes fat, protein, and water content. There are also estimates of 
composition change based on the change in body reserves.
"""

import math

import numpy as np


def calculate_Frm_Gain_empty(
    Frm_Gain: float, 
    Dt_DMIn_ClfLiq: float, 
    Dt_DMIn_ClfStrt: float,
    An_GutFill_BW: float
) -> float:
    Frm_Gain_empty = Frm_Gain * (1 - An_GutFill_BW)  
    # Line 2439, Assume the same gut fill for frame gain
    if Dt_DMIn_ClfLiq > 0 and Dt_DMIn_ClfStrt > 0:
        # slightly different for grain & milk fed, Line 2440
        Frm_Gain_empty = Frm_Gain * 0.91
    return Frm_Gain_empty


def calculate_Body_Gain_empty(
    Frm_Gain_empty: float, 
    Rsrv_Gain_empty: float
) -> float:
    Body_Gain_empty = Frm_Gain_empty + Rsrv_Gain_empty  # Line 2442
    return Body_Gain_empty


def calculate_NPGain_RsrvGain(coeff_dict: dict) -> float:
    """
    Examples
    --------
    ```
    coeff_dict = {"CPGain_RsrvGain": 0.068, "Body_NP_CP": 0.86}
    
    calculate_NPGain_RsrvGain(coeff_dict = coeff_dict)
    ```
    """
    NPGain_RsrvGain = coeff_dict['CPGain_RsrvGain'] * coeff_dict['Body_NP_CP']  
    # Line 2467
    return NPGain_RsrvGain


def calculate_Rsrv_NPgain(
    NPGain_RsrvGain: float, 
    Rsrv_Gain_empty: float
) -> float:
    Rsrv_NPgain = NPGain_RsrvGain * Rsrv_Gain_empty  # Line 2468
    return Rsrv_NPgain


def calculate_Body_NPgain(Frm_NPgain: float, Rsrv_NPgain: float) -> float:
    Body_NPgain = Frm_NPgain + Rsrv_NPgain  # Line 2473
    return Body_NPgain


def calculate_Body_CPgain(Body_NPgain: float, coeff_dict: dict) -> float:
    """
    Examples
    --------
    ```
    coeff_dict = {"Body_NP_CP": 0.86}
    
    calculate_Body_CPgain(
        Body_NPgain = 50.0, coeff_dict = coeff_dict
    )
    ```
    """
    Body_CPgain = Body_NPgain / coeff_dict['Body_NP_CP']  # Line 2475
    return Body_CPgain


def calculate_Body_CPgain_g(Body_CPgain: float) -> float:
    Body_CPgain_g = Body_CPgain * 1000  # Line 2477
    return Body_CPgain_g


def calculate_Rsrv_Gain(Trg_RsrvGain: float) -> float:
    """
    Trg_RsrvGain (float): Target gain or loss in body reserves 
                          (66% fat, 8% CP) in kg fresh weight/day
    """
    Rsrv_Gain = Trg_RsrvGain  # Line 2435
    return Rsrv_Gain


def calculate_Rsrv_Gain_empty(Rsrv_Gain: float) -> float:
    """
    Rsrv_Gain_empty: Body reserve gain assuming no gut fill association, kg/d
    """
    Rsrv_Gain_empty = Rsrv_Gain  
    # Assume no gut fill associated with reserves gain, Line 2441
    return Rsrv_Gain_empty


def calculate_Rsrv_Fatgain(Rsrv_Gain_empty: float, coeff_dict: dict) -> float:
    """
    FatGain_RsrvGain: Conversion factor from reserve gain to fat gain
    Rsrv_Fatgain: Body reserve fat gain kg/d
    
    Examples
    --------
    ```
    coeff_dict = {"FatGain_RsrvGain": 0.622}
    
    calculate_Rsrv_Fatgain(
        Rsrv_Gain_empty = 40.0, coeff_dict = coeff_dict
    )
    ```
    """
    Rsrv_Fatgain = coeff_dict['FatGain_RsrvGain'] * Rsrv_Gain_empty  # Line 2453
    return Rsrv_Fatgain


def calculate_CPGain_FrmGain(An_BW: float, An_BW_mature: float) -> float:
    """
    CPGain_FrmGain: CP gain per unit of frame gain kg/d
    """
    CPGain_FrmGain = 0.201 - 0.081 * An_BW / An_BW_mature  
    # CP gain / gain for heifers, Line 2458
    return CPGain_FrmGain


def calculate_Rsrv_CPgain(
    CPGain_FrmGain: float,
    Rsrv_Gain_empty: float
) -> float:
    """
    Rsrv_CPgain: CP portion of body reserve gain, g/g
    """
    Rsrv_CPgain = CPGain_FrmGain * Rsrv_Gain_empty  # Line 2470
    return Rsrv_CPgain


def calculate_FatGain_FrmGain(
    An_StatePhys: str, 
    An_REgain_Calf: float,
    An_BW: float, 
    An_BW_mature: float
) -> float:
    """
    FatGain_FrmGain: Fat gain per unit frame gain, kg/kg EBW (Empty body weight)
    This is the proportion of the empty body weight that is fat, which increases 
    (and protein decreases) as the animal matures
    This is why it is scaled to a proportion of mature BW (An_BW / An_BW_mature)
    Also in equation 20-253
    """
    if An_StatePhys == "Calf":
        FatGain_FrmGain = 0.0786 + 0.0370 * An_REgain_Calf # Calves,..., g/g EBW
    else:
        FatGain_FrmGain = (0.067 + 0.375 * An_BW / An_BW_mature)
    if math.isnan(FatGain_FrmGain):
        FatGain_FrmGain = 0
    return FatGain_FrmGain


def calculate_Frm_Gain(Trg_FrmGain: float) -> float:
    """
    Frame gain, kg/d
    """
    Frm_Gain = Trg_FrmGain  
    # Add any predictions of ADG and select Trg or Pred ADG here, Line 2434
    return Frm_Gain


def calculate_Frm_Fatgain(
    FatGain_FrmGain: float,
    Frm_Gain_empty: float
) -> float:
    """
    Frm_Fatgain: Frame fat gain kg/?
    FatGain_FrmGain is the kg of fat per kg of empty frame gain, based on the BW of the animal as a % of mature BW. 
    Here, the actual kg/kg * EBG (kg/d) = frame fat gain kg/d
    In the book, the Fat_ADG from equation 3-20a (which is  FatGain_FrmGain here) is corrected for empty body weight (e.g. x 0.85), keeping it in kg/kg units. 
     this is a mix of Equations 11-5a and 11-6a (but 11-6a assumes 0.85, not EBG/ADG)
    """
    Frm_Fatgain = FatGain_FrmGain * Frm_Gain_empty  # Line 2452
    return Frm_Fatgain


def calculate_NPGain_FrmGain(CPGain_FrmGain: float, coeff_dict: dict) -> float:
    """
    NPGain_FrmGain: Net protein gain per unit frame gain
    NOTE for these gain per unit gain values I believe they are unitless/have units g/g, not much said in the R code
    
    Examples
    --------
    ```
    coeff_dict = {"Body_NP_CP": 0.86}
    
    calculate_NPGain_FrmGain(
        CPGain_FrmGain = 60.0, coeff_dict = coeff_dict
    )
    ```
    """
    # Convert to CP to TP gain / gain, Line 2459
    NPGain_FrmGain = CPGain_FrmGain * coeff_dict['Body_NP_CP']
    return NPGain_FrmGain


def calculate_Frm_NPgain(
    An_StatePhys: str, 
    NPGain_FrmGain: float,
    Frm_Gain_empty: float, 
    Body_Gain_empty: float,
    An_REgain_Calf: float
) -> float:
    """
    Frm_NPgain: NP portion of frame gain
    """
    Frm_NPgain = NPGain_FrmGain * Frm_Gain_empty  # TP gain, Line 2460
    if An_StatePhys == "Calf":
        Frm_NPgain = (166.22 * Body_Gain_empty + 6.13 * An_REgain_Calf /
                      Body_Gain_empty) / 1000  # Line 2461
    return Frm_NPgain


def calculate_Frm_CPgain(Frm_NPgain: float, coeff_dict: dict) -> float:
    """
    Frm_CPgain: CP portion of frame gain

    Examples
    --------
    ```
    coeff_dict = {"Body_NP_CP": 0.86}
    
    calculate_Frm_CPgain(
        Frm_NPgain = 50.0, coeff_dict = coeff_dict
    )
    ```
    """
    Frm_CPgain = Frm_NPgain / coeff_dict['Body_NP_CP']  # Line 2463
    return Frm_CPgain


def calculate_Body_NPgain_g(Body_NPgain: float) -> float:
    """
    Body_NPgain_g: Net protein from frame and reserve gain, g
    """
    Body_NPgain_g = Body_NPgain * 1000  # Line 2475
    return Body_NPgain_g


def calculate_An_BWmature_empty(
    An_BW_mature: float, 
    coeff_dict: dict
) -> float:
    """
    An_BWmature_empty: kg bodyweight with no gut fill 

    Examples
    --------
    ```
    coeff_dict = {"An_GutFill_BWmature": 0.18}
    
    calculate_An_BWmature_empty(
        An_BW_mature = 600.0, coeff_dict = coeff_dict
    )
    ```
    """
    An_BWmature_empty = An_BW_mature * (1 - coeff_dict['An_GutFill_BWmature'])
    return An_BWmature_empty


def calculate_Body_Gain(Frm_Gain: float, Rsrv_Gain: float) -> float:
    """
    Body_Gain: Bodyweight gain, kg/d
    """
    Body_Gain = Frm_Gain + Rsrv_Gain  # Line 2436
    return Body_Gain


def calculate_Trg_BWgain(Trg_FrmGain: float, Trg_RsrvGain: float) -> float:
    """
    Trg_BWgain: Target rate of bodyweight gain, kg/d
    """
    Trg_BWgain = Trg_FrmGain + Trg_RsrvGain  
    # This could also be generated by prediction equations, Line 224
    return Trg_BWgain


def calculate_Trg_BWgain_g(Trg_BWgain: float) -> float:
    """
    Trg_BWgain_g: Target rate of bodyweight gain, g/d
    """
    Trg_BWgain_g = Trg_BWgain * 1000  # Line 225
    return Trg_BWgain_g


def calculate_Conc_BWgain(GrUter_BWgain: float, Uter_BWgain: float) -> float:
    """
    Conc_BWgain: ?
    """
    Conc_BWgain = GrUter_BWgain - Uter_BWgain  # Line 2349
    return Conc_BWgain


def calculate_BW_BCS(An_BW: float) -> float:
    """
    BW_BCS: Calculate BCS from BW?
    """
    BW_BCS = 0.094 * An_BW  
    # Each BCS represents 94 g of weight per kg of BW, Line 2395
    return BW_BCS


def calculate_An_BWnp3(An_BWnp: float, An_BCS: float) -> float:
    """
    An_BWnp3: Non-pregnant BW standardized to BCS 3(kg)
    """
    An_BWnp3 = An_BWnp / (
        1 + 0.094 * (An_BCS - 3)
    )  # BWnp standardized to BCS of 3 using 9.4% of BW/unit of BCS, Line 2397
    return An_BWnp3


def calculate_An_GutFill_Wt_Erdman(
    Dt_DMIn: float, 
    InfRum_DMIn: float,
    InfSI_DMIn: float
) -> float:
    """
    An_GutFill_Wt_Erdman: Gut fill from Erdman et al. 2017
    """
    An_GutFill_Wt_Erdman = 5.9 * (Dt_DMIn + InfRum_DMIn + InfSI_DMIn)  
    # cows only, from Erdman et al. 2017; not used, Line 2411
    return An_GutFill_Wt_Erdman


def calculate_An_BWnp_empty(An_BWnp: float, An_GutFill_Wt: float) -> float:
    """
    An_BWnp_empty: Non pregnant empty BW (kg). 
    Comment says 3 Std BCS standardized but this does not use An_BWnp3?
    """
    An_BWnp_empty = An_BWnp - An_GutFill_Wt  # BCS3 Std EBW, Line 2416
    return An_BWnp_empty


def calculate_An_BWnp3_empty(An_BWnp3: float, An_GutFill_Wt: float) -> float:
    """
    An_BWnp3_empty: Non pregnant empty bodyweight standardized 3 Std
    """
    An_BWnp3_empty = An_BWnp3 - An_GutFill_Wt  # BCS3 Std EBWnp, Line 2417
    return An_BWnp3_empty


def calculate_Body_Fat_EBW(An_BW: float, An_BW_mature: float) -> float:
    """
    Body_Fat_EBW: g fat / g empty BW
    """
    Body_Fat_EBW = 0.067 + 0.188 * An_BW / An_BW_mature  # Line 2420
    return Body_Fat_EBW


def calculate_Body_NonFat_EBW(Body_Fat_EBW: float) -> float:
    """
    Body_NonFat_EBW: Non fat empty bodyweight (g/g EBW)
    """
    Body_NonFat_EBW = 1 - Body_Fat_EBW  # Line 2421
    return Body_NonFat_EBW


def calculate_Body_CP_EBW(Body_NonFat_EBW: float) -> float:
    """
    Body_CP_EBW: g CP / g EBW
    """
    Body_CP_EBW = 0.215 * Body_NonFat_EBW  # Line 2422
    return Body_CP_EBW


def calculate_Body_Ash_EBW(Body_NonFat_EBW: float) -> float:
    """
    Body_Ash_EBW: g Ash / g EBW
    """
    Body_Ash_EBW = 0.056 * Body_NonFat_EBW  # Line 2423
    return Body_Ash_EBW


def calculate_Body_Wat_EBW(Body_NonFat_EBW: float) -> float:
    """
    Body_Wat_EBW: g water? / g EBW
    """
    Body_Wat_EBW = 0.729 * Body_NonFat_EBW  # Line 2424
    return Body_Wat_EBW


def calculate_Body_Fat(An_BWnp_empty: float, Body_Fat_EBW: float) -> float:
    """
    Body_Fat: Body fat (g)
    """
    Body_Fat = An_BWnp_empty * Body_Fat_EBW  
    # Using a non-pregnant BW, Line 2426
    return Body_Fat


def calculate_Body_NonFat(
    An_BWnp_empty: float,
    Body_NonFat_EBW: float
) -> float:
    """
    Body_NonFat: Non fat bodyweight (g)
    """
    Body_NonFat = An_BWnp_empty * Body_NonFat_EBW  # Line 2427
    return Body_NonFat


def calculate_Body_CP(An_BWnp_empty: float, Body_NonFat_EBW: float) -> float:
    """
    Body_CP: CP bodyweight (g)
    """
    Body_CP = An_BWnp_empty * Body_NonFat_EBW  # Line 2428
    return Body_CP


def calculate_Body_Ash(An_BWnp_empty: float, Body_Ash_EBW: float) -> float:
    """
    Body_Ash: Ash bodyweight (g)
    """
    Body_Ash = An_BWnp_empty * Body_Ash_EBW  # Line 2429
    return Body_Ash


def calculate_Body_Wat(An_BWnp_empty: float, Body_Wat_EBW: float) -> float:
    """
    Body_Wat: Water bodyweight (g)
    """
    Body_Wat = An_BWnp_empty * Body_Wat_EBW  # Line 2430
    return Body_Wat


def calculate_An_BodConcgain(Body_Gain: float, Conc_BWgain: float) -> float:
    """
    An_BodConcgain: ? (kg/d)
    """
    An_BodConcgain = Body_Gain + Conc_BWgain  # Minus fetal fluid, Line 2437
    return An_BodConcgain


def calculate_NonFatGain_FrmGain(FatGain_FrmGain: float) -> float:
    """
    NonFatGain_FrmGain: Non fat frame gain (g/g)
    """
    NonFatGain_FrmGain = 1 - FatGain_FrmGain  # Line 2450
    return NonFatGain_FrmGain


def calculate_Body_Fatgain(Frm_Fatgain: float, Rsrv_Fatgain: float) -> float:
    """
    Body_Fatgain: Fat gain (g/g)
    """
    Body_Fatgain = Frm_Fatgain + Rsrv_Fatgain  # Line 2454
    return Body_Fatgain


def calculate_Body_NonFatGain(
    Body_Gain_empty: float,
    Body_Fatgain: float
) -> float:
    """
    Body_NonFatGain: Non fat gain (g/g)
    """
    Body_NonFatGain = Body_Gain_empty - Body_Fatgain  # Line 2455
    return Body_NonFatGain


def calculate_Frm_CPgain_g(Frm_CPgain: float) -> float:
    """
    Frm_CPgain_g: Body frame crude protein gain (kg)
    """
    Frm_CPgain_g = Frm_CPgain * 1000  # Line 2464
    return Frm_CPgain_g


def calculate_Rsrv_CPgain_g(Rsrv_CPgain: float) -> float:
    """
    Rsrv_CPgain_g: Body reserve crude protein gain (g/d)
    """
    Rsrv_CPgain_g = Rsrv_CPgain * 1000  # Line 2471
    return Rsrv_CPgain_g


def calculate_Body_AshGain(Body_NonFatGain: float) -> float:
    """
    Body_AshGain: Body ash gain (g/g)
    """
    Body_AshGain = 0.056 * Body_NonFatGain  
    # Alternative method of estimation Body and Frm Ash, Line 2484
    return Body_AshGain


def calculate_Frm_AshGain(Body_AshGain: float) -> float:
    """
    Frm_AshGain: Body frame ash gain (g/g)
    """
    Frm_AshGain = Body_AshGain  # Line 2485
    return Frm_AshGain


def calculate_WatGain_RsrvGain(
    NPGain_RsrvGain: float,
    coeff_dict: dict
) -> float:
    """
    WatGain_RsrvGain: Body reserve water gain (g/g)
    
    Examples
    --------
    ```
    coeff_dict = {"FatGain_RsrvGain": 0.622, "AshGain_RsrvGain": 0.02}
    
    calculate_WatGain_RsrvGain(
        NPGain_RsrvGain = 0.20, coeff_dict = coeff_dict
    )
    ```
    """
    WatGain_RsrvGain = (100 - coeff_dict['FatGain_RsrvGain'] - NPGain_RsrvGain - 
                        coeff_dict['AshGain_RsrvGain'])  # Line 2489
    return WatGain_RsrvGain


def calculate_Rsrv_WatGain(
    WatGain_RsrvGain: float,
    Rsrv_Gain_empty: float
) -> float:
    """
    Rsrv_WatGain: Body reserve water gain (g/g)
    """
    Rsrv_WatGain = WatGain_RsrvGain * Rsrv_Gain_empty  # Line 2491
    return Rsrv_WatGain


def calculate_Body_WatGain(Body_NonFatGain: float) -> float:
    """
    Body_WatGain: Bodyweight water gain (g/g)
    """
    Body_WatGain = 0.729 * Body_NonFatGain  
    # Alternative method of estimation, Line 2493
    return Body_WatGain


def calculate_Frm_WatGain(Body_WatGain: float, Rsrv_WatGain: float) -> float:
    """
    Frm_WatGain: Body frame water gain (g/g)
    """
    Frm_WatGain = Body_WatGain - Rsrv_WatGain  # Line 2494
    return Frm_WatGain


def calculate_An_MPavail_Gain_Trg(
    An_MPIn: float, 
    An_MPuse_g_Trg: float,
    Body_MPUse_g_Trg: float
) -> float:
    """
    An_MPavail_Gain_Trg: MP available for target gain? (kg/d)
    """
    An_MPavail_Gain_Trg = (An_MPIn - An_MPuse_g_Trg / 
                           1000 + Body_MPUse_g_Trg / 1000)  # Line 2712
    return An_MPavail_Gain_Trg


def calculate_Body_NPgain_MPalowTrg_g(
    An_MPavail_Gain_Trg: float,
    Kg_MP_NP_Trg: float
) -> float:
    """
    Body_NPgain_MPalowTrg_g: MP allowable NP gain (g/d)
    """
    Body_NPgain_MPalowTrg_g = An_MPavail_Gain_Trg * Kg_MP_NP_Trg * 1000  
    # g NP gain/d, Line 2713
    return Body_NPgain_MPalowTrg_g


def calculate_Body_CPgain_MPalowTrg_g(
    Body_NPgain_MPalowTrg_g: float,
    coeff_dict: dict
) -> float:
    """
    Body_CPgain_MPalowTrg_g: MP allowable CP gain (g/d)
    
    Examples
    --------
    ```
    coeff_dict = {"Body_NP_CP": 0.80}
    
    calculate_Body_CPgain_MPalowTrg_g(
        Body_NPgain_MPalowTrg_g = 40.0, 
        coeff_dict = coeff_dict
    )
    ```
    """
    Body_CPgain_MPalowTrg_g = Body_NPgain_MPalowTrg_g / coeff_dict['Body_NP_CP']  
    # g CP gain/d, Line 2714
    return Body_CPgain_MPalowTrg_g


def calculate_Body_Gain_MPalowTrg_g(
    Body_NPgain_MPalowTrg_g: float,
    NPGain_FrmGain: float
) -> float:
    """
    Body_Gain_MPalowTrg_g: MP allowable body gain (g/d)
    """
    Body_Gain_MPalowTrg_g = Body_NPgain_MPalowTrg_g / NPGain_FrmGain  
    # g/d, Assume all is frame gain, Line 2715
    return Body_Gain_MPalowTrg_g


def calculate_Body_Gain_MPalowTrg(Body_Gain_MPalowTrg_g: float) -> float:
    """
    Body_Gain_MPalowTrg: MP allowable body gain (kg/d)
    """
    Body_Gain_MPalowTrg = Body_Gain_MPalowTrg_g / 1000  # Line 2716
    return Body_Gain_MPalowTrg


def calculate_An_MEavail_Grw(
    An_MEIn: float, 
    An_MEmUse: float,
    Gest_MEuse: float, 
    Mlk_MEout: float
) -> float:
    """
    An_MEavail_Grw: ME available for growth (Mcal/d)
    """
    An_MEavail_Grw = An_MEIn - An_MEmUse - Gest_MEuse - Mlk_MEout  # Line 2947
    return An_MEavail_Grw


def calculate_Kg_ME_NE(
    Frm_NEgain: float, 
    Rsrv_NEgain: float, 
    Kr_ME_RE: float,
    Kf_ME_RE: float
) -> float:
    """
    Kg_ME_NE: ME to NE for NE allowable gain?
    """
    if Frm_NEgain + Rsrv_NEgain == 0:
        Kg_ME_NE = 0
    else:
    #Use a weighted average of Kf and Kr to predict allowable gain at that mix of Frm and Rsrv gain.
        Kg_ME_NE = (Kf_ME_RE * Frm_NEgain / 
                    (Frm_NEgain + Rsrv_NEgain) + Kr_ME_RE * Rsrv_NEgain / 
                    (Frm_NEgain + Rsrv_NEgain))
    return Kg_ME_NE


def calculate_Body_Gain_NEalow(
    An_MEavail_Grw: float, 
    Kg_ME_NE: float,
    Body_NEgain_BWgain: float
) -> float:
    """
    Body_Gain_NEalow: NE allowable body gain
    """
    if (Body_NEgain_BWgain != 0 # Line 2950
        and not np.isnan(An_MEavail_Grw) 
        and not np.isnan(Kg_ME_NE) 
        and not np.isnan(Body_NEgain_BWgain)
        ):
        Body_Gain_NEalow = An_MEavail_Grw * Kg_ME_NE / Body_NEgain_BWgain 
    else:
        Body_Gain_NEalow = np.nan
    return Body_Gain_NEalow


def calculate_An_BodConcgain_NEalow(
    Body_Gain_NEalow: float,
    Conc_BWgain: float
) -> float:
    """
    An_BodConcgain_NEalow: ?
    """
    An_BodConcgain_NEalow = Body_Gain_NEalow + Conc_BWgain  # Line 2954
    return An_BodConcgain_NEalow


def calculate_Body_Fatgain_NEalow(Body_Gain_NEalow: float) -> float:
    """
    Body_Fatgain_NEalow: NE allowable body fat gain (kg/d?)
    """
    Body_Fatgain_NEalow = 0.85 * (Body_Gain_NEalow / 0.85 -1.19) / 8.21  
    # Line 2955
    return Body_Fatgain_NEalow


def calculate_Body_NPgain_NEalow(Body_Fatgain_NEalow: float) -> float:
    """
    Body_NPgain_NEalow: NE allowable body NP gain (kg/d?)
    """
    Body_NPgain_NEalow = 0.85 * (1 - Body_Fatgain_NEalow / 0.85) * 0.215
    return Body_NPgain_NEalow


def calculate_An_Days_BCSdelta1(
    BW_BCS: float,
    Body_Gain_NEalow: float
) -> float:
    """
    An_Days_BCSdelta1: Days to gain/lose 1 BCS 
    """
    An_Days_BCSdelta1 = BW_BCS / Body_Gain_NEalow  
    # days to gain or lose 1 BCS (9.4% of BW), 5 pt scale., Line 2958
    return An_Days_BCSdelta1


def calculate_Rsrv_AshGain(
    Rsrv_Gain_empty: float,
    coeff_dict: dict
) -> float:
    """
    Examples
    --------
    ```
    coeff_dict = {"AshGain_RsrvGain": 0.02}
    
    calculate_Rsrv_AshGain(
        Rsrv_Gain_empty = 40.0, coeff_dict = coeff_dict
    )
    ```
    """
    Rsrv_AshGain = coeff_dict["AshGain_RsrvGain"] * Rsrv_Gain_empty   # Line 2481
    return Rsrv_AshGain
