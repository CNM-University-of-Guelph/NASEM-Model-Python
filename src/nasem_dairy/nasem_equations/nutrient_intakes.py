"""Functions for calcualting nutrient intakes.

This module contains functions to estimate the intake of various nutrients 
by animals, including energy, protein, and minerals, based on dietary composition 
and dry matter intake.
"""
import math

import numpy as np
import pandas as pd


####################
# Functions for Feed Intakes
####################
def calculate_TT_dcFdNDF_Lg(Fd_NDF: pd.Series, Fd_Lg: pd.Series) -> pd.Series:
    Fd_NFD_check = np.where(Fd_NDF == 0, 1e-6, Fd_NDF)
    TT_dcFdNDF_Lg = (0.75 * (Fd_NDF - Fd_Lg) * 
                     (1 - (Fd_Lg / Fd_NFD_check)**0.667) / Fd_NFD_check * 100)  
    # Line 235-236
    return TT_dcFdNDF_Lg


def calculate_Fd_DNDF48(Fd_Conc: pd.Series, Fd_DNDF48_input: pd.Series) -> pd.Series:
    # I can't find Fd_DNDF48 in any of the feed libraries, 
    # including the feed library in the NASEM software,
    # For now all the Fd_DNDF48 values are being calculated
    # I've added a column of 0s as the Fd_DNDF48 column
    condition = (Fd_Conc < 100) & (Fd_DNDF48_input.isin([0, np.nan]))
    condition_conc = (Fd_Conc == 100) & (Fd_DNDF48_input.isin([0, np.nan]))
    # Line 241, mean of Mike Allen database used for DMI equation
    Fd_DNDF48 = np.where(condition, 48.3, Fd_DNDF48_input)
    # Line 242, mean of concentrates in the feed library
    Fd_DNDF48 = np.where(condition_conc, 65, Fd_DNDF48)
    Fd_DNDF48 = pd.Series(Fd_DNDF48, index=Fd_Conc.index)
    return Fd_DNDF48


def calculate_TT_dcFdNDF_48h(Fd_DNDF48: pd.Series) -> pd.Series:
    TT_dcFdNDF_48h = 12 + 0.61 * Fd_DNDF48  # Line 245
    return TT_dcFdNDF_48h


def calculate_TT_dcFdNDF_Base(
    Use_DNDF_IV: int, 
    Fd_Conc: pd.Series, 
    TT_dcFdNDF_Lg: pd.Series,
    TT_dcFdNDF_48h: pd.Series
) -> pd.Series:
    condition1 = (Use_DNDF_IV == 1) & (Fd_Conc < 100) & ~TT_dcFdNDF_48h.isna()  
    # Line 249, Forages only
    condition2 = (Use_DNDF_IV == 2) & ~TT_dcFdNDF_48h.isna()  
    # Line 251, All Ingredients
    TT_dcFdNDF_Base = TT_dcFdNDF_Lg
    TT_dcFdNDF_Base = np.where(condition1, TT_dcFdNDF_48h, TT_dcFdNDF_Base)
    TT_dcFdNDF_Base = np.where(condition2, TT_dcFdNDF_48h, TT_dcFdNDF_Base)
    # Line 248, Prefill with the Lg based predictions as a default
    return TT_dcFdNDF_Base


def calculate_Fd_GE(
    An_StatePhys: str, 
    Fd_Category: pd.Series, 
    Fd_CP: pd.Series, 
    Fd_FA: pd.Series, 
    Fd_Ash: pd.Series, 
    Fd_St: pd.Series,
    Fd_NDF: pd.Series, 
    coeff_dict: dict
) -> pd.Series:
    """
    Examples
    --------
    ```
    coeff_dict = {
        'En_CP': 0.75, 'En_FA': 0.90, 'En_rOM': 0.80, 'En_St': 0.70, 'En_NDF': 0.65
    }
    Fd_Category = pd.Series(['Calf Liquid Feed', 'Adult Dry Feed'])
    Fd_CP = pd.Series([20.0, 15.0])
    Fd_FA = pd.Series([5.0, 6.0])
    Fd_Ash = pd.Series([10.0, 8.0])
    Fd_St = pd.Series([12.0, 14.0])
    Fd_NDF = pd.Series([30.0, 25.0])

    calculate_Fd_GE(
        An_StatePhys = "Calf", 
        Fd_Category = pd.Series(['Calf Liquid Feed', 'Adult Dry Feed']), 
        Fd_CP = pd.Series([20.0, 15.0]), Fd_FA = pd.Series([5.0, 6.0]), 
        Fd_Ash = pd.Series([10.0, 8.0]), Fd_St = pd.Series([12.0, 14.0]), 
        Fd_NDF = pd.Series([30.0, 25.0]), coeff_dict = coeff_dict
    )
    ```
    """
    condition = (An_StatePhys == "Calf") & (Fd_Category == "Calf Liquid Feed")
    Fd_GE = np.where(condition, 
                     (
                      (Fd_CP / 100 * coeff_dict['En_CP'] + 
                       Fd_FA / 100 * coeff_dict['En_FA'] + 
                       (100 - Fd_Ash - Fd_CP - Fd_FA) / 
                       100 * coeff_dict['En_rOM'])
                       ),  # Line 278, liquid feed exception
                     (
                       Fd_CP / 100 * coeff_dict['En_CP'] + 
                       Fd_FA / 100 * coeff_dict['En_FA'] + 
                       Fd_St / 100 * coeff_dict['En_St'] + 
                       Fd_NDF / 100 * coeff_dict['En_NDF'] + 
                       (100 - Fd_CP - Fd_FA - Fd_St - Fd_NDF - Fd_Ash) / 
                       100 * coeff_dict['En_rOM']
                       )) # Line 279, the remainder
    return Fd_GE


def calculate_Fd_DMIn(Dt_DMIn: pd.Series, Fd_DMInp: pd.Series) -> pd.Series:
    Fd_DMIn = Fd_DMInp * Dt_DMIn  # Line 441
    return Fd_DMIn


def calculate_Fd_AFIn(Fd_DM: pd.Series, Fd_DMIn: pd.Series) -> pd.Series:
    Fd_AFIn = np.where(Fd_DM == 0, 0, Fd_DMIn / (Fd_DM / 100))  # Line 442
    return Fd_AFIn


def calculate_Fd_For(Fd_Conc: pd.Series):
    Fd_For = 100 - Fd_Conc  # Line 446
    return Fd_For


def calculate_Fd_ForWet(Fd_DM: pd.Series, Fd_For: pd.Series) -> pd.Series:
    condition = (Fd_For > 50) & (Fd_DM < 71)
    Fd_ForWet = np.where(condition, Fd_For, 0)  # Line 447
    return Fd_ForWet


def calculate_Fd_ForDry(Fd_DM: pd.Series, Fd_For: pd.Series) -> pd.Series:
    condition = (Fd_For > 50) & (Fd_DM >= 71)
    Fd_ForDry = np.where(condition, Fd_For, 0)  # Line 448
    return Fd_ForDry


def calculate_Fd_Past(Fd_Category: pd.Series) -> pd.Series:
    Fd_Past = np.where(Fd_Category == 'Pasture', 100, 0)  # Line 449
    return Fd_Past


def calculate_Fd_LiqClf(Fd_Category: pd.Series) -> pd.Series:
    Fd_LiqClf = np.where(Fd_Category == 'Calf Liquid Feed', 100, 0)  # Line 450
    return Fd_LiqClf


def calculate_Fd_ForNDF(Fd_NDF: pd.Series, Fd_Conc: pd.Series) -> pd.Series:
    Fd_ForNDF = (1 - Fd_Conc / 100) * Fd_NDF  # Line 452
    return Fd_ForNDF


def calculate_Fd_NDFnf(Fd_NDF: pd.Series, Fd_NDFIP: pd.Series) -> pd.Series:
    Fd_NDFnf = Fd_NDF - Fd_NDFIP  # Line 453
    return Fd_NDFnf


def calculate_Fd_NPNCP(Fd_CP: pd.Series, Fd_NPN_CP: pd.Series) -> pd.Series:
    Fd_NPNCP = Fd_CP * Fd_NPN_CP / 100  # Line 455
    return Fd_NPNCP


def calculate_Fd_NPN(Fd_NPNCP: pd.Series) -> pd.Series:
    Fd_NPN = Fd_NPNCP / 6.25  # Line 457
    return Fd_NPN


def calculate_Fd_NPNDM(Fd_NPNCP: pd.Series) -> pd.Series:
    Fd_NPNDM = Fd_NPNCP / 2.81  # Line 458
    return Fd_NPNDM


def calculate_Fd_TP(Fd_CP: pd.Series, Fd_NPNCP: pd.Series) -> pd.Series:
    Fd_TP = Fd_CP - Fd_NPNCP  # Line 459
    return Fd_TP


def calculate_Fd_fHydr_FA(Fd_Category: pd.Series) -> pd.Series:
    Fd_fHydr_FA = np.where(Fd_Category == 'Fatty Acid Supplement', 1, 1 / 1.06)  
    # Line 461
    return Fd_fHydr_FA


def calculate_Fd_FAhydr(Fd_FA: pd.Series, Fd_fHydr_FA: pd.Series) -> pd.Series:
    Fd_FAhydr = Fd_FA * Fd_fHydr_FA  # Line 463
    return Fd_FAhydr


def calculate_Fd_NFC(
    Fd_NDF: pd.Series, 
    Fd_TP: pd.Series, 
    Fd_Ash: pd.Series, 
    Fd_FAhydr: pd.Series, 
    Fd_NPNDM: pd.Series
) -> pd.Series:
    Fd_NFC = 100 - Fd_Ash - Fd_NDF - Fd_TP - Fd_NPNDM - Fd_FAhydr  # Line 465
    # Forces any values below 0 to =0           # Line 466
    Fd_NFC.clip(lower=0)
    return Fd_NFC


def calculate_Fd_rOM(
    Fd_NDF: pd.Series, 
    Fd_St: pd.Series, 
    Fd_TP: pd.Series, 
    Fd_FA: pd.Series, 
    Fd_fHydr_FA: pd.Series, 
    Fd_Ash: pd.Series,
    Fd_NPNDM: pd.Series
) -> pd.Series:
    Fd_rOM = (100 - Fd_Ash - Fd_NDF - Fd_St - 
              (Fd_FA*Fd_fHydr_FA) - Fd_TP - Fd_NPNDM) # Line 468
    return Fd_rOM


def calculate_Fd_GEIn(Fd_GE: pd.Series, Fd_DMIn: pd.Series) -> pd.Series:
    Fd_GEIn = Fd_GE * Fd_DMIn  # Line 544
    return Fd_GEIn


def calculate_Fd_DigNDFIn_Base(
    Fd_NDFIn: pd.Series, 
    TT_dcFdNDF_Base: pd.Series
) -> pd.Series:
    Fd_DigNDFIn_Base = TT_dcFdNDF_Base / 100 * Fd_NDFIn  # Line 481
    return Fd_DigNDFIn_Base


def calculate_Fd_NPNCPIn(Fd_CPIn: pd.Series, Fd_NPN_CP: pd.Series) -> pd.Series:
    Fd_NPNCPIn = Fd_CPIn * Fd_NPN_CP / 100  # Line 491
    return Fd_NPNCPIn


def calculate_Fd_NPNIn(Fd_NPNCPIn: pd.Series) -> pd.Series:
    Fd_NPNIn = Fd_NPNCPIn * 0.16  # Line 492
    return Fd_NPNIn


def calculate_Fd_NPNDMIn(Fd_NPNCPIn: pd.Series) -> pd.Series:
    Fd_NPNDMIn = Fd_NPNCPIn / 2.81  # Line 493
    return Fd_NPNDMIn


def calculate_Fd_CPAIn(Fd_CPIn: pd.Series, Fd_CPARU: pd.Series) -> pd.Series:
    Fd_CPAIn = Fd_CPIn * Fd_CPARU / 100  # Line 494
    return Fd_CPAIn


def calculate_Fd_CPBIn(Fd_CPIn: pd.Series, Fd_CPBRU: pd.Series) -> pd.Series:
    Fd_CPBIn = Fd_CPIn * Fd_CPBRU / 100  # Line 495
    return Fd_CPBIn


def calculate_Fd_CPBIn_For(
    Fd_CPIn: pd.Series, 
    Fd_CPBRU: pd.Series, 
    Fd_For: pd.Series
) -> pd.Series:
    Fd_CPBIn_For = Fd_CPIn * Fd_CPBRU / 100 * Fd_For / 100  # Line 496
    return Fd_CPBIn_For


def calculate_Fd_CPBIn_Conc(
    Fd_CPIn: pd.Series, 
    Fd_CPBRU: pd.Series, 
    Fd_Conc: pd.Series
) -> pd.Series:
    Fd_CPBIn_Conc = Fd_CPIn * Fd_CPBRU / 100 * Fd_Conc / 100  # Line 497
    return Fd_CPBIn_Conc


def calculate_Fd_CPCIn(Fd_CPIn: pd.Series, Fd_CPCRU: pd.Series) -> pd.Series:
    Fd_CPCIn = Fd_CPIn * Fd_CPCRU / 100  # Line 498
    return Fd_CPCIn


def calculate_Fd_CPIn_ClfLiq(
    Fd_Category: pd.Series, 
    Fd_DMIn: pd.Series, 
    Fd_CP: pd.Series
) -> pd.Series:
    Fd_CPIn_ClfLiq = np.where(Fd_Category == "Calf Liquid Feed",
                              Fd_DMIn * Fd_CP / 100, 0)  # Line 499
    return Fd_CPIn_ClfLiq


def calculate_Fd_CPIn_ClfDry(
    Fd_Category: pd.Series, 
    Fd_DMIn: pd.Series, 
    Fd_CP: pd.Series
) -> pd.Series:
    Fd_CPIn_ClfDry = np.where(Fd_Category == "Calf Liquid Feed", 
                              0, Fd_DMIn * Fd_CP / 100)  # Line 500
    return Fd_CPIn_ClfDry


def calculate_Fd_rdcRUPB(
    Fd_For: pd.Series, 
    Fd_Conc: pd.Series, 
    Fd_KdRUP: pd.Series, 
    coeff_dict: dict
) -> pd.Series:
    """
    Examples
    --------
    ```
    coeff_dict = {
        'KpFor': 4.87, 'KpConc': 5.28
    }

    calculate_Fd_rdcRUPB(
        Fd_For = pd.Series([10.0, 15.0]), Fd_Conc = pd.Series([5.0, 7.0]), 
        Fd_KdRUP = pd.Series([0.5, 0.6]), coeff_dict = coeff_dict
    )
    ```
    """
    Fd_rdcRUPB = 100 - (
        Fd_For * coeff_dict['KpFor'] /
        (Fd_KdRUP + coeff_dict['KpFor']) + Fd_Conc * coeff_dict['KpConc'] /
        (Fd_KdRUP + coeff_dict['KpConc']))  # Line 514
    return Fd_rdcRUPB


def calculate_Fd_RUPBIn(
    Fd_For: pd.Series, 
    Fd_Conc: pd.Series, 
    Fd_KdRUP: pd.Series, 
    Fd_CPBIn: pd.Series, 
    coeff_dict: dict
) -> pd.Series:
    """
    Examples
    --------
    ```
    coeff_dict = {
        'KpFor': 4.87, 'KpConc': 5.28
    }

    calculate_Fd_RUPBIn(
        Fd_For = pd.Series([10.0, 15.0]), Fd_Conc = pd.Series([5.0, 7.0]),
        Fd_KdRUP = pd.Series([0.5, 0.6]), Fd_CPBIn = pd.Series([12.0, 18.0]),
        coeff_dict = coeff_dict
    )
    ```
    """
    Fd_RUPBIn = (Fd_CPBIn * Fd_For / 
                 100 * coeff_dict['KpFor'] / 
                 (Fd_KdRUP + coeff_dict['KpFor']) + Fd_CPBIn * Fd_Conc / 
                 100 * coeff_dict['KpConc'] / 
                 (Fd_KdRUP + coeff_dict['KpConc'])) # Line 516
    return Fd_RUPBIn


def calculate_Fd_RUPIn(
    Fd_CPIn: pd.Series, 
    Fd_CPAIn: pd.Series, 
    Fd_CPCIn: pd.Series, 
    Fd_NPNCPIn: pd.Series, 
    Fd_RUPBIn: pd.Series,
    coeff_dict: dict
) -> pd.Series:
    """
    Examples
    --------
    ```
    coeff_dict = {
        'refCPIn': 3.39, 'fCPAdu': 0.064, 'IntRUP': -0.086
    }

    calculate_Fd_RUPIn(
        Fd_CPIn = pd.Series([20.0, 25.0]), Fd_CPAIn = pd.Series([5.0, 6.0]), 
        Fd_CPCIn = pd.Series([1.0, 1.5]), Fd_NPNCPIn = pd.Series([0.5, 0.7]), 
        Fd_RUPBIn = pd.Series([10.0, 12.0]), coeff_dict = coeff_dict
    )
    ```
    """
    Fd_RUPIn = ((Fd_CPAIn - Fd_NPNCPIn) * coeff_dict['fCPAdu'] + 
                Fd_RUPBIn + Fd_CPCIn + coeff_dict['IntRUP'] / 
                coeff_dict['refCPIn'] * Fd_CPIn) # Line 518
    return Fd_RUPIn


def calculate_Fd_RUP_CP(Fd_CPIn: pd.Series, Fd_RUPIn: pd.Series) -> pd.Series:
    Fd_RUP_CP = np.where(Fd_CPIn > 0, Fd_RUPIn / Fd_CPIn * 100, 0)
    return Fd_RUP_CP


def calculate_Fd_RUP(
    Fd_CPIn: pd.Series, 
    Fd_RUPIn: pd.Series, 
    Fd_DMIn: pd.Series
) -> pd.Series:
    Fd_RUP = np.where(Fd_CPIn > 0, Fd_RUPIn / Fd_DMIn * 100, 0)  # Line 522
    return Fd_RUP


def calculate_Fd_RDP(
    Fd_CPIn: pd.Series, 
    Fd_CP: pd.Series, 
    Fd_RUP: pd.Series
) -> pd.Series:
    Fd_RDP = np.where(Fd_CPIn > 0, Fd_CP - Fd_RUP, 0)  # Line 523
    return Fd_RDP


def calculate_Fd_OMIn(Fd_DMIn: pd.Series, Fd_AshIn: pd.Series) -> pd.Series:
    Fd_OMIn = Fd_DMIn - Fd_AshIn  # Line 543
    return Fd_OMIn


def calculate_Fd_DE_base_1(
    Fd_NDF: pd.Series, 
    Fd_Lg: pd.Series, 
    Fd_St: pd.Series, 
    Fd_dcSt: pd.Series, 
    Fd_FA: pd.Series, 
    Fd_dcFA: pd.Series,
    Fd_Ash: pd.Series, 
    Fd_CP: pd.Series, 
    Fd_NPNCP: pd.Series, 
    Fd_RUP: pd.Series, 
    Fd_dcRUP: pd.Series
) -> pd.Series:
    adjusted_NDF = np.where(Fd_NDF == 0, 1e-9, Fd_NDF)
    # if Fd_NDF == 0:
    #     adjusted_NDF = 1e-9
    # else:
    #     adjusted_NDF = Fd_NDF
    # # Standard Equation 1 - IVNDF not used
    # Line 548-552
    Fd_DE_base_1 = (
    0.75 * (Fd_NDF - Fd_Lg) * (1 - ((Fd_Lg / adjusted_NDF) ** 0.667)) * 0.042
    + Fd_St * Fd_dcSt / 100 * 0.0423
    + Fd_FA * Fd_dcFA / 100 * 0.094
    + (100 - (Fd_FA / 1.06) - Fd_Ash - Fd_NDF - Fd_St - 
       (Fd_CP - (Fd_NPNCP - Fd_NPNCP / 2.81)))
    * 0.96 * 0.04
    + ((Fd_CP - Fd_RUP / 100 * Fd_CP)
    + Fd_RUP / 100 * Fd_CP * Fd_dcRUP / 100
    - Fd_NPNCP) * 0.0565
    + Fd_NPNCP * 0.0089
    - (0.137 + 0.093 + 0.088)
    )
    return Fd_DE_base_1


def calculate_Fd_DE_base_2(
    Fd_NDF: pd.Series, 
    Fd_St: pd.Series, 
    Fd_dcSt: pd.Series, 
    Fd_FA: pd.Series, 
    Fd_dcFA: pd.Series, 
    Fd_Ash: pd.Series,
    Fd_CP: pd.Series, 
    Fd_NPNCP: pd.Series, 
    Fd_RUP: pd.Series, 
    Fd_dcRUP: pd.Series, 
    Fd_DNDF48_NDF: pd.Series
) -> pd.Series:
    # Standard equation 2 - based on setting of IVNDF use switch
    Fd_DE_base_2 = (
    (0.12 + 0.0061 * Fd_DNDF48_NDF) * Fd_NDF * 0.042
    + (Fd_St * Fd_dcSt / 100 * 0.0423)
    + (Fd_FA * Fd_dcFA / 100 * 0.094)
    + ((100 - (Fd_FA / 1.06) - (Fd_CP - (Fd_NPNCP - Fd_NPNCP / 2.81))
        - Fd_Ash - Fd_NDF - Fd_St) * 0.96 * 0.04)
    + ((Fd_CP - Fd_RUP / 100 * Fd_CP)
       + Fd_RUP / 100 * Fd_CP * Fd_dcRUP / 100 - Fd_NPNCP) * 0.0565
    + Fd_NPNCP * 0.0089
    - (0.137 + 0.093 + 0.088)
    ) # Line 554-557
    return Fd_DE_base_2


def calculate_Fd_DE_base(
    Use_DNDF_IV: int, 
    Fd_DE_base_1: pd.Series, 
    Fd_DE_base_2: pd.Series, 
    Fd_For: pd.Series, 
    Fd_FA: pd.Series,
    Fd_RDP: pd.Series, 
    Fd_RUP: pd.Series, 
    Fd_dcRUP: pd.Series, 
    Fd_CP: pd.Series, 
    Fd_Ash: pd.Series, 
    Fd_dcFA: pd.Series,
    Fd_NPN: pd.Series, 
    Fd_Category: pd.Series
) -> pd.Series:
    Fd_DE_base = np.where(Use_DNDF_IV == 0, 
                          Fd_DE_base_1, Fd_DE_base_2) # Line 559

    condition = (Use_DNDF_IV == 1) & (Fd_For == 0)
    Fd_DE_base = np.where(condition, Fd_DE_base_1, Fd_DE_base)  # Line 560

    Fd_DE_base = np.where(
        Fd_Category == "Animal Protein",  # Line 561-563
        0.73 * Fd_FA * 0.094 + (Fd_RDP + (Fd_RUP * Fd_dcRUP)) * 0.056 +
        (0.96 * (100 - Fd_FA / 1.06 - Fd_CP - Fd_Ash) * 0.04) - 0.318,
        Fd_DE_base)

    Fd_DE_base = np.where(Fd_Category == "Fat Supplement",  # Line 564-565
                          (Fd_FA * Fd_dcFA/100 * 0.094 + 
                          (100 - Fd_Ash - (Fd_FA/1.06) * 0.96) * 0.043 - 0.318),
                          Fd_DE_base)

    Fd_DE_base = np.where(
        Fd_Category == "Fatty Acid Supplement",  # Line 566
        Fd_FA * Fd_dcFA / 100 * 0.094 - 0.318, Fd_DE_base)

    Fd_DE_base = np.where(Fd_Category == "Calf Liquid Feed",  # Line 567
                          ((0.094 * Fd_FA + 0.057 * Fd_CP + 
                            0.04 * (100 - Fd_Ash - Fd_CP - Fd_FA)) * 0.95),
                          Fd_DE_base)

    Fd_DE_base = np.where(
        Fd_Category == "Sugar/Sugar Alcohol",  # Line 568
        (100 - Fd_Ash) * 0.04 * 0.96 - 0.318, Fd_DE_base)

    Fd_DE_base = np.where(
        Fd_Category == "Vitamin/Mineral", 0, Fd_DE_base) # Line 569

    condition_2 = (Fd_Category == "Vitamin/Mineral") & (Fd_NPN > 0)
    Fd_DE_base = np.where(
        condition_2, (Fd_CP * 0.089) - 0.318, Fd_DE_base) # Line 570
    # According to Weiss, need to set urea, ammonium phoshate and other NPN 
    # sources to: (Fd_CP * 0.089) - 0.318. It appears they are set to 0 in the 
    # software, rather than as Bill specified. MDH
    return Fd_DE_base


def calculate_Fd_DEIn_base(
    Fd_DE_base: pd.Series, 
    Fd_DMIn: pd.Series
) -> pd.Series:
    Fd_DEIn_base = Fd_DE_base * Fd_DMIn  # Line 574
    return Fd_DEIn_base


def calculate_Fd_DEIn_base_ClfLiq(
    Fd_Category: pd.Series, 
    Fd_DEIn_base: pd.Series
) -> pd.Series:
    Fd_DEIn_base_ClfLiq = np.where(Fd_Category == "Calf Liquid Feed", 
                                   Fd_DEIn_base, 0) # Line 575
    return Fd_DEIn_base_ClfLiq


def calculate_Fd_DEIn_base_ClfDry(
    Fd_Category: pd.Series, 
    Fd_DEIn_base: pd.Series
) -> pd.Series:
    Fd_DEIn_base_ClfDry = np.where(Fd_Category == "Calf Liquid Feed", 
                                   0, Fd_DEIn_base) # Line 576
    return Fd_DEIn_base_ClfDry


def calculate_Fd_DMIn_ClfLiq(
    An_StatePhys: str, 
    Fd_DMIn: pd.Series, 
    Fd_Category: pd.Series
) -> pd.Series:
    condition = (An_StatePhys == "Calf") & (Fd_Category == "Calf Liquid Feed")  
    Fd_DMIn_ClfLiq = np.where(condition, Fd_DMIn, 0)  # milk intake, Line 283
    return Fd_DMIn_ClfLiq


def calculate_Fd_DE_ClfLiq(
    An_StatePhys: str, 
    Fd_Category: pd.Series, 
    Fd_GE: pd.Series
) -> pd.Series:
    condition = (An_StatePhys == "Calf") & (Fd_Category == "Calf Liquid Feed")
    # prelim estimate for DMI only, mcal/kg, nutrients are in %, Line 284
    Fd_DE_ClfLiq = np.where(condition, 0.95 * Fd_GE, 0)
    return Fd_DE_ClfLiq


def calculate_Fd_ME_ClfLiq(
    An_StatePhys: str, 
    Fd_Category: pd.Series, 
    Fd_DE_ClfLiq: pd.Series
) -> pd.Series:
    condition = (An_StatePhys == "Calf") & (Fd_Category == "Calf Liquid Feed")
    Fd_ME_ClfLiq = np.where(condition, 
                            Fd_DE_ClfLiq * 0.96,
                            0)  # mcal/kg, nutrients are in %, Line 285
    return Fd_ME_ClfLiq


def calculate_Fd_DMIn_ClfFor(
    Dt_DMIn: float, 
    Fd_Conc: pd.Series, 
    Fd_DMInp: pd.Series
) -> pd.Series:
    Fd_DMIn_ClfFor = (1 - Fd_Conc / 100) * Dt_DMIn * Fd_DMInp  # Line 296
    return Fd_DMIn_ClfFor


def calculate_Fd_PinorgIn(
    Fd_PIn: pd.Series, 
    Fd_Pinorg_P: pd.Series
) -> pd.Series:
    Fd_PinorgIn = Fd_PIn * Fd_Pinorg_P / 100  # Line 731, ??Check Bill's text
    return Fd_PinorgIn


def calculate_Fd_PorgIn(Fd_PIn: pd.Series, Fd_Porg_P: pd.Series) -> pd.Series:
    # Line 732 Fd_PphytIn = Fd_PIn*Fd_Pphyt_P/100, Depracated by Bill. 
    # Reduced to inorganic and organic.
    Fd_PorgIn = Fd_PIn * Fd_Porg_P / 100
    return Fd_PorgIn


def calculate_Fd_MgIn_min(
    Fd_Category: pd.Series, 
    Fd_MgIn: pd.Series
) -> pd.Series:
    Fd_MgIn_min = Fd_MgIn.copy()
    Fd_MgIn_min[Fd_Category != "Vitamin/Mineral"] = 0
    return Fd_MgIn_min


def calculate_Fd_acCa(
    An_StatePhys: str, 
    Fd_acCa_input: pd.Series, 
    Dt_DMIn_ClfLiq: float
) -> np.ndarray:
    condition = (An_StatePhys == "Calf") & (Dt_DMIn_ClfLiq > 0)  # Line 1839
    Fd_acCa = np.where(condition, 1, Fd_acCa_input)
    condition2 = (An_StatePhys == "Calf") & (Dt_DMIn_ClfLiq == 0)  # Line 1840
    Fd_acCa = np.where(condition2, 0.60, Fd_acCa)
    return Fd_acCa


def calculate_Fd_acPtot(
    An_StatePhys: str, 
    Fd_Category: pd.Series, 
    Fd_Pinorg_P: pd.Series, 
    Fd_Porg_P: pd.Series,
    Fd_acPtot_input: pd.Series, 
    Dt_DMIn_ClfLiq: float
) -> np.ndarray:
    Fd_acPtot = np.where(Fd_Category == "Vitamin/Mineral", 
                         Fd_acPtot_input, 
                         Fd_Pinorg_P * 0.0084 + Fd_Porg_P * 0.0068) # Line 1841
    condition = (An_StatePhys == "Calf") & (Dt_DMIn_ClfLiq > 0)  # Line 1842
    Fd_acPtot = np.where(condition, 1, Fd_acPtot)
    condition2 = (An_StatePhys == "Calf") & (Dt_DMIn_ClfLiq == 0)  # Line 1843
    Fd_acPtot = np.where(condition2, 0.75, Fd_acPtot)
    return Fd_acPtot


def calculate_Fd_acMg(
    An_StatePhys: str, 
    Fd_acMg_input: pd.Series, 
    Dt_DMIn_ClfLiq: float
) -> np.ndarray:
    condition = (An_StatePhys == "Calf") & (Dt_DMIn_ClfLiq > 0)  # Line 1844
    Fd_acMg = np.where(condition, 1, Fd_acMg_input)
    condition2 = (An_StatePhys == "Calf") & (Dt_DMIn_ClfLiq == 0)  # line 1845
    Fd_acMg = np.where(condition2, 0.26, Fd_acMg)
    return Fd_acMg


def calculate_Fd_acNa(
    An_StatePhys: str, 
    Fd_acNa_input: pd.Series
) -> np.ndarray:
    Fd_acNa = np.where(An_StatePhys == "Calf", 1.0, Fd_acNa_input) # Line 1846
    return Fd_acNa


def calculate_Fd_acK(An_StatePhys: str, Fd_acK_input: pd.Series) -> np.ndarray:
    Fd_acK = np.where(An_StatePhys == "Calf", 1.0, Fd_acK_input) # Line 1847
    return Fd_acK


def calculate_Fd_acCl(
    An_StatePhys: str, 
    Fd_acCl_input: pd.Series, 
    Dt_DMIn_ClfLiq: float
) -> np.ndarray:
    condition = (An_StatePhys == "Calf") & (Dt_DMIn_ClfLiq > 0)  # Line 1848
    Fd_acCl = np.where(condition, 1, Fd_acCl_input)
    condition2 = (An_StatePhys == "Calf") & (Dt_DMIn_ClfLiq == 0)  # line 1849
    Fd_acCl = np.where(condition2, 0.92, Fd_acCl)
    return Fd_acCl


def calculate_Fd_absCaIn(Fd_CaIn: pd.Series, Fd_acCa: pd.Series) -> pd.Series:
    Fd_absCaIn = Fd_CaIn * Fd_acCa  # line 1851
    return Fd_absCaIn


def calculate_Fd_absPIn(Fd_PIn: pd.Series, Fd_acPtot: pd.Series) -> pd.Series:
    Fd_absPIn = Fd_PIn * Fd_acPtot  # line 1852
    return Fd_absPIn


def calculate_Fd_absMgIn_base(
    Fd_MgIn: pd.Series, 
    Fd_acMg: pd.Series
) -> pd.Series:
    Fd_absMgIn_base = Fd_MgIn * Fd_acMg  # line 1853
    return Fd_absMgIn_base


def calculate_Fd_absNaIn(Fd_NaIn: pd.Series, Fd_acNa: pd.Series) -> pd.Series:
    Fd_absNaIn = Fd_NaIn * Fd_acNa  # line 1854
    return Fd_absNaIn


def calculate_Fd_absKIn(Fd_KIn: pd.Series, Fd_acK: pd.Series) -> pd.Series:
    Fd_absKIn = Fd_KIn * Fd_acK  # line 1855
    return Fd_absKIn


def calculate_Fd_absClIn(Fd_ClIn: pd.Series, Fd_acCl: pd.Series) -> pd.Series:
    Fd_absClIn = Fd_ClIn * Fd_acCl  # line 1856
    return Fd_absClIn


def calculate_Fd_acCo(An_StatePhys: str) -> np.ndarray:
    Fd_acCo = np.where(An_StatePhys == "Calf", 0, 1.0) # Line 1860
    return Fd_acCo


def calculate_Fd_acCu(
    An_StatePhys: str, 
    Fd_acCu_input: pd.Series, 
    Dt_DMIn_ClfLiq: float
) -> np.ndarray:
    Fd_acCu = np.where(An_StatePhys == "Calf", 1.0, Fd_acCu_input) # Line 1861
    condition = (An_StatePhys == "Calf") & (Dt_DMIn_ClfLiq == 0)
    Fd_acCu = np.where(condition, 0.10, Fd_acCu) # Line 1862
    return Fd_acCu


def calculate_Fd_acFe(
    An_StatePhys: str, 
    Fd_acFe_input: pd.Series, 
    Dt_DMIn_ClfLiq: float
) -> np.ndarray:
    Fd_acFe = np.where(An_StatePhys == "Calf", 1.0, Fd_acFe_input) # Line 1863
    condition = (An_StatePhys == "Calf") & (Dt_DMIn_ClfLiq == 0)
    Fd_acFe = np.where(condition, 0.10, Fd_acFe) # Line 1864
    return Fd_acFe


def calculate_Fd_acMn(
    An_StatePhys: str, 
    Fd_acMn_input: pd.Series, 
    Dt_DMIn_ClfLiq: float
) -> np.ndarray:
    Fd_acMn = np.where(
        An_StatePhys == "Calf",  # Line 1865
        1.0,
        Fd_acMn_input)
    condition = (An_StatePhys == "Calf") & (Dt_DMIn_ClfLiq == 0)
    Fd_acMn = np.where(
        condition,  # Line 1866
        0.005,
        Fd_acMn)
    return Fd_acMn


def calculate_Fd_acZn(
    An_StatePhys: str, 
    Fd_acZn_input: pd.Series , 
    Dt_DMIn_ClfLiq: float
) -> pd.Series:
    Fd_acZn = Fd_acZn_input.copy()
    if An_StatePhys == "Calf":
        Fd_acZn[:] = 1.0
    if An_StatePhys == "Calf" and Dt_DMIn_ClfLiq == 0.0:
        Fd_acZn[:] = 0.20
    return Fd_acZn


def calculate_Fd_DigSt(Fd_St: pd.Series, Fd_dcSt: pd.Series) -> pd.Series:
    Fd_DigSt = Fd_St * Fd_dcSt / 100  # Line 1014
    return Fd_DigSt


def calculate_Fd_DigStIn_Base(
    Fd_DigSt: pd.Series, 
    Fd_DMIn: pd.Series
) -> pd.Series:
    Fd_DigStIn_Base = Fd_DigSt / 100 * Fd_DMIn  # Line 1015
    return Fd_DigStIn_Base


def calculate_Fd_DigrOMt(Fd_rOM: pd.Series, coeff_dict: dict) -> pd.Series:
    """
    Examples
    --------
    ```
    coeff_dict = {
        'Fd_dcrOM': 96
    }

    calculate_Fd_DigrOMt(
        Fd_rOM = pd.Series([100.0, 150.0]), coeff_dict = coeff_dict
    )
    ```
    """
    # Truly digested rOM in each feed, % of DM
    Fd_DigrOMt = coeff_dict['Fd_dcrOM'] / 100 * Fd_rOM
    return Fd_DigrOMt


def calculate_Fd_DigrOMtIn(
    Fd_DigrOMt: pd.Series, 
    Fd_DMIn: pd.Series
) -> pd.Series:
    Fd_DigrOMtIn = Fd_DigrOMt / 100 * Fd_DMIn  # Line 1010, kg/d
    return Fd_DigrOMtIn


def calculate_Fd_idRUPIn(Fd_dcRUP: pd.Series, Fd_RUPIn: pd.Series) -> pd.Series:
    # Line 1072, dcRUP is the RUP DC by feed read in from the Feed Matrix.
    Fd_idRUPIn = (Fd_dcRUP / 100) * Fd_RUPIn
    return Fd_idRUPIn


def calculate_TT_dcFdFA(
    An_StatePhys: str, 
    Fd_Category: pd.Series, 
    Fd_Type: pd.Series, 
    Fd_dcFA: pd.Series,
    coeff_dict: dict
) -> pd.Series:
    """
    Examples
    --------
    ```
    coeff_dict = {
        'TT_dcFA_Base':73, 'TT_dcFat_Base': 68, 'TT_dcFA_ClfDryFd': 81, 
        'TT_dcFA_ClfLiqFd': 81
    }

    calculate_TT_dcFdFA(
        An_StatePhys = "Calf", Fd_dcFA = pd.Series([None, 0.70, None, None])
        Fd_Category = pd.Series(["Fatty Acid Supplement", "Fat Supplement", "Calf Liquid Feed", "Other"])
        Fd_Type = pd.Series(["Concentrate", "Other", "Concentrate", "Other"])
        coeff_dict = coeff_dict
    )
    ```
    """
    TT_dcFdFA = Fd_dcFA.copy()  # Line 1251

    condition_1 = (
        (TT_dcFdFA.isna()) & 
        (Fd_Category == "Fatty Acid Supplement")
        )
    TT_dcFdFA[condition_1] = coeff_dict['TT_dcFA_Base'] # Line 1252

    condition_2 =(
        (TT_dcFdFA.isna()) & 
        (Fd_Category == "Fat Supplement")
        )
    TT_dcFdFA[condition_2] = coeff_dict['TT_dcFat_Base'] # Line 1253
    # Line 1254, Fill in any remaining missing values with fat dc
    TT_dcFdFA = TT_dcFdFA.fillna(coeff_dict['TT_dcFat_Base'])

    condition_3 = (
        (An_StatePhys == "Calf") & 
        (Fd_Category != "Calf Liquid Feed") & 
        (Fd_Type == "Concentrate")
        )
    # Line 1255, likely an over estimate for forage
    TT_dcFdFA[condition_3] = coeff_dict['TT_dcFA_ClfDryFd']

    condition_4 = (
        (TT_dcFdFA.isna()) & 
        (An_StatePhys == "Calf") & 
        (Fd_Category == "Calf Liquid Feed")
        )
    # Line 1256, Default if dc is not entered.
    TT_dcFdFA[condition_4] = coeff_dict['TT_dcFA_ClfLiqFd']
    TT_dcFdFA = pd.to_numeric(TT_dcFdFA, errors='coerce').fillna(0).astype(float)
    return TT_dcFdFA


def calculate_Fd_DigFAIn(
    TT_dcFdFA: pd.Series, 
    Fd_FA: pd.Series, 
    Fd_DMIn: pd.Series
) -> pd.Series:
    Fd_DigFAIn = TT_dcFdFA / 100 * Fd_FA / 100 * Fd_DMIn
    return Fd_DigFAIn


def calculate_Fd_DigrOMa(Fd_DigrOMt: float, coeff_dict: dict) -> float:
    """
    Fd_DigrOMa: Apparently digested residual organic matter, % DM
    
    Examples
    --------
    ```
    coeff_dict = {'Fe_rOMend_DMI': 3.43}

    calculate_Fd_DigrOMa(
        Fd_DigrOMt = 20.0, coeff_dict = coeff_dict
    )
    ```
    """
    Fd_DigrOMa = Fd_DigrOMt - coeff_dict['Fe_rOMend_DMI']  # Line 1008
    # Apparently digested (% DM). Generates some negative values for minerals and other low rOM feeds.
    return Fd_DigrOMa


def calculate_Fd_DigrOMaIn(Fd_DigrOMa: float, Fd_DMIn: float) -> float:
    """
    Fd_DigrOMaIn: Apparently digested residual organic matter intkae, kg/d
    """
    Fd_DigrOMaIn = Fd_DigrOMa / 100 * Fd_DMIn  # kg/d, Line 1009
    return Fd_DigrOMaIn


def calculate_Fd_DigWSC(Fd_WSC: float) -> float:
    """
    Fd_DigWSC: Digested water soluble carbohydrate, % DM
    """
    Fd_DigWSC = Fd_WSC  # 100% digestible, Line 1011
    return Fd_DigWSC


def calculate_Fd_DigWSCIn(Fd_DigWSC: float, Fd_DMIn: float) -> float:
    """
    Fd_DigWSCIn: Digested water soluble carbohydrate intake , kg/d
    """
    Fd_DigWSCIn = Fd_DigWSC / 100 * Fd_DMIn  # Line 1012
    return Fd_DigWSCIn


def calculate_Fd_idRUP(
    Fd_CPIn: float | pd.Series,
    Fd_idRUPIn: float | pd.Series,
    Fd_DMIn: float | pd.Series
) -> float | pd.Series:
    """
    Fd_idRUP: Intestinally digested RUP, % DM
    """
    Fd_idRUP = np.where(Fd_CPIn > 0, Fd_idRUPIn / Fd_DMIn * 100, 0)  # Line 1073
    return Fd_idRUP


def calculate_Fd_Fe_RUPout(
    Fd_RUPIn: float | pd.Series,
    Fd_dcRUP: float | pd.Series
) -> float | pd.Series:
    """
    Fd_Fe_RUPout: Fecal RUP output, kg/d
    """
    Fd_Fe_RUPout = Fd_RUPIn * (1 - Fd_dcRUP / 100)  # Line 1078
    return Fd_Fe_RUPout


def calculate_Fd_ADFIn(Fd_ADF: pd.Series, Fd_DMIn: pd.Series) -> pd.Series:
    Fd_ADFIn = Fd_ADF / 100 * Fd_DMIn
    return Fd_ADFIn


def calculate_Fd_NDFIn(Fd_NDF: pd.Series, Fd_DMIn: pd.Series) -> pd.Series:
    Fd_NDFIn = Fd_NDF / 100 * Fd_DMIn
    return Fd_NDFIn


def calculate_Fd_StIn(Fd_St: pd.Series, Fd_DMIn: pd.Series) -> pd.Series:
    Fd_StIn = Fd_St / 100 * Fd_DMIn
    return Fd_StIn


def calculate_Fd_NFCIn(Fd_NFC: pd.Series, Fd_DMIn: pd.Series) -> pd.Series:
    Fd_NFCIn = Fd_NFC / 100 * Fd_DMIn
    return Fd_NFCIn


def calculate_Fd_WSCIn(Fd_WSC: pd.Series, Fd_DMIn: pd.Series) -> pd.Series:
    Fd_WSCIn = Fd_WSC / 100 * Fd_DMIn
    return Fd_WSCIn


def calculate_Fd_rOMIn(Fd_rOM: pd.Series, Fd_DMIn: pd.Series) -> pd.Series:
    Fd_rOMIn = Fd_rOM / 100 * Fd_DMIn
    return Fd_rOMIn


def calculate_Fd_LgIn(Fd_Lg: pd.Series, Fd_DMIn: pd.Series) -> pd.Series:
    Fd_LgIn = Fd_Lg / 100 * Fd_DMIn
    return Fd_LgIn


def calculate_Fd_ConcIn(Fd_Conc: pd.Series, Fd_DMIn: pd.Series) -> pd.Series:
    Fd_ConcIn = Fd_Conc / 100 * Fd_DMIn
    return Fd_ConcIn


def calculate_Fd_ForIn(Fd_For: pd.Series, Fd_DMIn: pd.Series) -> pd.Series:
    Fd_ForIn = Fd_For / 100 * Fd_DMIn
    return Fd_ForIn


def calculate_Fd_ForNDFIn(
    Fd_ForNDF: pd.Series, 
    Fd_DMIn: pd.Series
) -> pd.Series:
    Fd_ForNDFIn = Fd_ForNDF / 100 * Fd_DMIn
    return Fd_ForNDFIn


def calculate_Fd_ForWetIn(
    Fd_ForWet: pd.Series, 
    Fd_DMIn: pd.Series
) -> pd.Series:
    Fd_ForWetIn = Fd_ForWet / 100 * Fd_DMIn
    return Fd_ForWetIn


def calculate_Fd_ForDryIn(
    Fd_ForDry: pd.Series, 
    Fd_DMIn: pd.Series
) -> pd.Series:
    Fd_ForDryIn = Fd_ForDry / 100 * Fd_DMIn
    return Fd_ForDryIn


def calculate_Fd_PastIn(Fd_Past: pd.Series, Fd_DMIn: pd.Series) -> pd.Series:
    Fd_PastIn = Fd_Past / 100 * Fd_DMIn
    return Fd_PastIn


def calculate_Fd_CPIn(Fd_CP: pd.Series, Fd_DMIn: pd.Series) -> pd.Series:
    Fd_CPIn = Fd_CP / 100 * Fd_DMIn
    return Fd_CPIn


def calculate_Fd_TPIn(Fd_TP: pd.Series, Fd_DMIn: pd.Series) -> pd.Series:
    Fd_TPIn = Fd_TP / 100 * Fd_DMIn
    return Fd_TPIn


def calculate_Fd_CFatIn(Fd_CFat: pd.Series, Fd_DMIn: pd.Series) -> pd.Series:
    Fd_CFatIn = Fd_CFat / 100 * Fd_DMIn
    return Fd_CFatIn


def calculate_Fd_FAIn(Fd_FA: pd.Series, Fd_DMIn: pd.Series) -> pd.Series:
    Fd_FAIn = Fd_FA / 100 * Fd_DMIn
    return Fd_FAIn


def calculate_Fd_FAhydrIn(
    Fd_FAhydr: pd.Series, 
    Fd_DMIn: pd.Series
) -> pd.Series:
    Fd_FAhydrIn = Fd_FAhydr / 100 * Fd_DMIn
    return Fd_FAhydrIn


def calculate_Fd_AshIn(Fd_Ash: pd.Series, Fd_DMIn: pd.Series) -> pd.Series:
    Fd_AshIn = Fd_Ash / 100 * Fd_DMIn
    return Fd_AshIn


def calculate_Fd_C120In(
    Fd_C120_FA: pd.Series, 
    Fd_FA: pd.Series, 
    Fd_DMIn: pd.Series
) -> pd.Series:
    Fd_C120In = Fd_C120_FA / 100 * Fd_FA / 100 * Fd_DMIn
    return Fd_C120In


def calculate_Fd_C140In(
    Fd_C140_FA: pd.Series, 
    Fd_FA: pd.Series, 
    Fd_DMIn: pd.Series
) -> pd.Series:
    Fd_C140In = Fd_C140_FA / 100 * Fd_FA / 100 * Fd_DMIn
    return Fd_C140In


def calculate_Fd_C160In(
    Fd_C160_FA: pd.Series, 
    Fd_FA: pd.Series, 
    Fd_DMIn: pd.Series
) -> pd.Series:
    Fd_C160In = Fd_C160_FA / 100 * Fd_FA / 100 * Fd_DMIn
    return Fd_C160In


def calculate_Fd_C161In(
    Fd_C161_FA: pd.Series, 
    Fd_FA: pd.Series, 
    Fd_DMIn: pd.Series
) -> pd.Series:
    Fd_C161In = Fd_C161_FA / 100 * Fd_FA / 100 * Fd_DMIn
    return Fd_C161In


def calculate_Fd_C180In(
    Fd_C180_FA: pd.Series, 
    Fd_FA: pd.Series, 
    Fd_DMIn: pd.Series
) -> pd.Series:
    Fd_C180In = Fd_C180_FA / 100 * Fd_FA / 100 * Fd_DMIn
    return Fd_C180In


def calculate_Fd_C181tIn(
    Fd_C181t_FA: pd.Series, 
    Fd_FA: pd.Series, 
    Fd_DMIn: pd.Series
) -> pd.Series:
    Fd_C181tIn = Fd_C181t_FA / 100 * Fd_FA / 100 * Fd_DMIn
    return Fd_C181tIn


def calculate_Fd_C181cIn(
    Fd_C181c_FA: pd.Series, 
    Fd_FA: pd.Series, 
    Fd_DMIn: pd.Series
) -> pd.Series:
    Fd_C181cIn = Fd_C181c_FA / 100 * Fd_FA / 100 * Fd_DMIn
    return Fd_C181cIn


def calculate_Fd_C182In(
    Fd_C182_FA: pd.Series, 
    Fd_FA: pd.Series, 
    Fd_DMIn: pd.Series
) -> pd.Series:
    Fd_C182In = Fd_C182_FA / 100 * Fd_FA / 100 * Fd_DMIn
    return Fd_C182In


def calculate_Fd_C183In(
    Fd_C183_FA: pd.Series, 
    Fd_FA: pd.Series, 
    Fd_DMIn: pd.Series
) -> pd.Series:
    Fd_C183In = Fd_C183_FA / 100 * Fd_FA / 100 * Fd_DMIn
    return Fd_C183In


def calculate_Fd_OtherFAIn(
    Fd_OtherFA_FA: pd.Series, 
    Fd_FA: pd.Series, 
    Fd_DMIn: pd.Series
) -> pd.Series:
    Fd_OtherFAIn = Fd_OtherFA_FA / 100 * Fd_FA / 100 * Fd_DMIn
    return Fd_OtherFAIn


def calculate_Fd_CaIn(Fd_DMIn: pd.Series, Fd_Ca: pd.Series) -> pd.Series:
    Fd_CaIn = Fd_DMIn * Fd_Ca / 100 * 1000
    return Fd_CaIn


def calculate_Fd_PIn(Fd_DMIn: pd.Series, Fd_P: pd.Series) -> pd.Series:
    Fd_PIn = Fd_DMIn * Fd_P / 100 * 1000
    return Fd_PIn


def calculate_Fd_NaIn(Fd_DMIn: pd.Series, Fd_Na: pd.Series) -> pd.Series:
    Fd_NaIn = Fd_DMIn * Fd_Na / 100 * 1000
    return Fd_NaIn


def calculate_Fd_MgIn(Fd_DMIn: pd.Series, Fd_Mg: pd.Series) -> pd.Series:
    Fd_MgIn = Fd_DMIn * Fd_Mg / 100 * 1000
    return Fd_MgIn


def calculate_Fd_KIn(Fd_DMIn: pd.Series, Fd_K: pd.Series) -> pd.Series:
    Fd_KIn = Fd_DMIn * Fd_K / 100 * 1000
    return Fd_KIn


def calculate_Fd_ClIn(Fd_DMIn: pd.Series, Fd_Cl: pd.Series) -> pd.Series:
    Fd_ClIn = Fd_DMIn * Fd_Cl / 100 * 1000
    return Fd_ClIn


def calculate_Fd_SIn(Fd_DMIn: pd.Series, Fd_S: pd.Series) -> pd.Series:
    Fd_SIn = Fd_DMIn * Fd_S / 100 * 1000
    return Fd_SIn


def calculate_Fd_CoIn(Fd_DMIn: pd.Series, Fd_Co: pd.Series) -> pd.Series:
    Fd_CoIn = Fd_DMIn * Fd_Co
    return Fd_CoIn


def calculate_Fd_CrIn(Fd_DMIn: pd.Series, Fd_Cr: pd.Series) -> pd.Series:
    Fd_CrIn = Fd_DMIn * Fd_Cr
    return Fd_CrIn


def calculate_Fd_CuIn(Fd_DMIn: pd.Series, Fd_Cu: pd.Series) -> pd.Series:
    Fd_CuIn = Fd_DMIn * Fd_Cu
    return Fd_CuIn


def calculate_Fd_FeIn(Fd_DMIn: pd.Series, Fd_Fe: pd.Series) -> pd.Series:
    Fd_FeIn = Fd_DMIn * Fd_Fe
    return Fd_FeIn


def calculate_Fd_IIn(Fd_DMIn: pd.Series, Fd_I: pd.Series) -> pd.Series:
    Fd_IIn = Fd_DMIn * Fd_I
    return Fd_IIn


def calculate_Fd_MnIn(Fd_DMIn: pd.Series, Fd_Mn: pd.Series) -> pd.Series:
    Fd_MnIn = Fd_DMIn * Fd_Mn
    return Fd_MnIn


def calculate_Fd_MoIn(Fd_DMIn: pd.Series, Fd_Mo: pd.Series) -> pd.Series:
    Fd_MoIn = Fd_DMIn * Fd_Mo
    return Fd_MoIn


def calculate_Fd_SeIn(Fd_DMIn: pd.Series, Fd_Se: pd.Series) -> pd.Series:
    Fd_SeIn = Fd_DMIn * Fd_Se
    return Fd_SeIn


def calculate_Fd_ZnIn(Fd_DMIn: pd.Series, Fd_Zn: pd.Series) -> pd.Series:
    Fd_ZnIn = Fd_DMIn * Fd_Zn
    return Fd_ZnIn


def calculate_Fd_VitAIn(Fd_DMIn: pd.Series, Fd_VitA: pd.Series) -> pd.Series:
    Fd_VitAIn = Fd_DMIn * Fd_VitA
    return Fd_VitAIn


def calculate_Fd_VitDIn(Fd_DMIn: pd.Series, Fd_VitD: pd.Series) -> pd.Series:
    Fd_VitDIn = Fd_DMIn * Fd_VitD
    return Fd_VitDIn


def calculate_Fd_VitEIn(Fd_DMIn: pd.Series, Fd_VitE: pd.Series) -> pd.Series:
    Fd_VitEIn = Fd_DMIn * Fd_VitE
    return Fd_VitEIn


def calculate_Fd_CholineIn(
    Fd_DMIn: pd.Series, 
    Fd_Choline: pd.Series
) -> pd.Series:
    Fd_CholineIn = Fd_DMIn * Fd_Choline
    return Fd_CholineIn


def calculate_Fd_BiotinIn(
    Fd_DMIn: pd.Series, 
    Fd_Biotin: pd.Series
) -> pd.Series:
    Fd_BiotinIn = Fd_DMIn * Fd_Biotin
    return Fd_BiotinIn


def calculate_Fd_NiacinIn(
    Fd_DMIn: pd.Series, 
    Fd_Niacin: pd.Series
) -> pd.Series:
    Fd_NiacinIn = Fd_DMIn * Fd_Niacin
    return Fd_NiacinIn


def calculate_Fd_B_CaroteneIn(
    Fd_DMIn: pd.Series, 
    Fd_B_Carotene: pd.Series
) -> pd.Series:
    Fd_B_CaroteneIn = Fd_DMIn * Fd_B_Carotene
    return Fd_B_CaroteneIn


def calculate_Fd_absCoIn(Fd_CoIn: pd.Series, Fd_acCo: pd.Series) -> pd.Series:
    Fd_absCoIn = Fd_CoIn * Fd_acCo
    return Fd_absCoIn


def calculate_Fd_absCuIn(Fd_CuIn: pd.Series, Fd_acCu: pd.Series) -> pd.Series:
    Fd_absCuIn = Fd_CuIn * Fd_acCu
    return Fd_absCuIn


def calculate_Fd_absFeIn(Fd_FeIn: pd.Series, Fd_acFe: pd.Series) -> pd.Series:
    Fd_absFeIn = Fd_FeIn * Fd_acFe
    return Fd_absFeIn


def calculate_Fd_absMnIn(Fd_MnIn: pd.Series, Fd_acMn: pd.Series) -> pd.Series:
    Fd_absMnIn = Fd_MnIn * Fd_acMn
    return Fd_absMnIn


def calculate_Fd_absZnIn(Fd_ZnIn: pd.Series, Fd_acZn: pd.Series) -> pd.Series:
    Fd_absZnIn = Fd_ZnIn * Fd_acZn
    return Fd_absZnIn


def calculate_Fd_Argt_CP(Fd_Arg_CP: pd.Series, coeff_dict: dict) -> pd.Series:
    Fd_Argt_CP = Fd_Arg_CP / coeff_dict["RecArg"]
    return Fd_Argt_CP


def calculate_Fd_Hist_CP(Fd_His_CP: pd.Series, coeff_dict: dict) -> pd.Series:
    Fd_Hist_CP = Fd_His_CP / coeff_dict["RecHis"]
    return Fd_Hist_CP


def calculate_Fd_Ilet_CP(Fd_Ile_CP: pd.Series, coeff_dict: dict) -> pd.Series:
    Fd_Ilet_CP = Fd_Ile_CP / coeff_dict["RecIle"]
    return Fd_Ilet_CP


def calculate_Fd_Leut_CP(Fd_Leu_CP: pd.Series, coeff_dict: dict) -> pd.Series:
    Fd_Leut_CP = Fd_Leu_CP / coeff_dict["RecLeu"]
    return Fd_Leut_CP


def calculate_Fd_Lyst_CP(Fd_Lys_CP: pd.Series, coeff_dict: dict) -> pd.Series:
    Fd_Lyst_CP = Fd_Lys_CP / coeff_dict["RecLys"]
    return Fd_Lyst_CP


def calculate_Fd_Mett_CP(Fd_Met_CP: pd.Series, coeff_dict: dict) -> pd.Series:
    Fd_Mett_CP = Fd_Met_CP / coeff_dict["RecMet"]
    return Fd_Mett_CP


def calculate_Fd_Phet_CP(Fd_Phe_CP: pd.Series, coeff_dict: dict) -> pd.Series:
    Fd_Phet_CP = Fd_Phe_CP / coeff_dict["RecPhe"]
    return Fd_Phet_CP


def calculate_Fd_Thrt_CP(Fd_Thr_CP: pd.Series, coeff_dict: dict) -> pd.Series:
    Fd_Thrt_CP = Fd_Thr_CP / coeff_dict["RecThr"]
    return Fd_Thrt_CP


def calculate_Fd_Trpt_CP(Fd_Trp_CP: pd.Series, coeff_dict: dict) -> pd.Series:
    Fd_Trpt_CP = Fd_Trp_CP / coeff_dict["RecTrp"]
    return Fd_Trpt_CP


def calculate_Fd_Valt_CP(Fd_Val_CP: pd.Series, coeff_dict: dict) -> pd.Series:
    Fd_Valt_CP = Fd_Val_CP / coeff_dict["RecVal"]
    return Fd_Valt_CP


def calculate_Fd_ArgRUPIn(
    Fd_Argt_CP: pd.Series, 
    Fd_RUPIn: pd.Series
) -> pd.Series:
    Fd_ArgRUPIn = Fd_Argt_CP / 100 * Fd_RUPIn * 1000
    return Fd_ArgRUPIn


def calculate_Fd_HisRUPIn(
    Fd_Hist_CP: pd.Series, 
    Fd_RUPIn: pd.Series
) -> pd.Series:
    Fd_HisRUPIn = Fd_Hist_CP / 100 * Fd_RUPIn * 1000
    return Fd_HisRUPIn


def calculate_Fd_IleRUPIn(
    Fd_Ilet_CP: pd.Series, 
    Fd_RUPIn: pd.Series
) -> pd.Series:
    Fd_IleRUPIn = Fd_Ilet_CP / 100 * Fd_RUPIn * 1000
    return Fd_IleRUPIn


def calculate_Fd_LeuRUPIn(
    Fd_Leut_CP: pd.Series, 
    Fd_RUPIn: pd.Series
) -> pd.Series:
    Fd_LeuRUPIn = Fd_Leut_CP / 100 * Fd_RUPIn * 1000
    return Fd_LeuRUPIn


def calculate_Fd_LysRUPIn(
    Fd_Lyst_CP: pd.Series, 
    Fd_RUPIn: pd.Series
) -> pd.Series:
    Fd_LysRUPIn = Fd_Lyst_CP / 100 * Fd_RUPIn * 1000
    return Fd_LysRUPIn


def calculate_Fd_MetRUPIn(
    Fd_Mett_CP: pd.Series, 
    Fd_RUPIn: pd.Series
) -> pd.Series:
    Fd_MetRUPIn = Fd_Mett_CP / 100 * Fd_RUPIn * 1000
    return Fd_MetRUPIn


def calculate_Fd_PheRUPIn(
    Fd_Phet_CP: pd.Series, 
    Fd_RUPIn: pd.Series
) -> pd.Series:
    Fd_PheRUPIn = Fd_Phet_CP / 100 * Fd_RUPIn * 1000
    return Fd_PheRUPIn


def calculate_Fd_ThrRUPIn(
    Fd_Thrt_CP: pd.Series, 
    Fd_RUPIn: pd.Series
) -> pd.Series:
    Fd_ThrRUPIn = Fd_Thrt_CP / 100 * Fd_RUPIn * 1000
    return Fd_ThrRUPIn


def calculate_Fd_TrpRUPIn(
    Fd_Trpt_CP: pd.Series, 
    Fd_RUPIn: pd.Series
) -> pd.Series:
    Fd_TrpRUPIn = Fd_Trpt_CP / 100 * Fd_RUPIn * 1000
    return Fd_TrpRUPIn


def calculate_Fd_ValRUPIn(
    Fd_Valt_CP: pd.Series, 
    Fd_RUPIn: pd.Series
) -> pd.Series:
    Fd_ValRUPIn = Fd_Valt_CP / 100 * Fd_RUPIn * 1000
    return Fd_ValRUPIn


def calculate_Fd_IdArgRUPIn(
    Fd_dcRUP: pd.Series, 
    Fd_ArgRUPIn: pd.Series, 
    SIDigArg: float
) -> pd.Series:
    Fd_IdArgRUPIn = Fd_dcRUP / 100 * Fd_ArgRUPIn * SIDigArg
    return Fd_IdArgRUPIn


def calculate_Fd_IdHisRUPIn(
    Fd_dcRUP: pd.Series, 
    Fd_HisRUPIn: pd.Series, 
    SIDigHis: float
) -> pd.Series:
    Fd_IdHisRUPIn = Fd_dcRUP / 100 * Fd_HisRUPIn * SIDigHis
    return Fd_IdHisRUPIn


def calculate_Fd_IdIleRUPIn(
    Fd_dcRUP: pd.Series, 
    Fd_IleRUPIn: pd.Series, 
    SIDigIle: float
) -> pd.Series:
    Fd_IdIleRUPIn = Fd_dcRUP / 100 * Fd_IleRUPIn * SIDigIle
    return Fd_IdIleRUPIn


def calculate_Fd_IdLeuRUPIn(
    Fd_dcRUP: pd.Series, 
    Fd_LeuRUPIn: pd.Series, 
    SIDigLeu: float
) -> pd.Series:
    Fd_IdLeuRUPIn = Fd_dcRUP / 100 * Fd_LeuRUPIn * SIDigLeu
    return Fd_IdLeuRUPIn


def calculate_Fd_IdLysRUPIn(
    Fd_dcRUP: pd.Series, 
    Fd_LysRUPIn: pd.Series, 
    SIDigLys: float
) -> pd.Series:
    Fd_IdLysRUPIn = Fd_dcRUP / 100 * Fd_LysRUPIn * SIDigLys
    return Fd_IdLysRUPIn


def calculate_Fd_IdMetRUPIn(
    Fd_dcRUP: pd.Series, 
    Fd_MetRUPIn: pd.Series, 
    SIDigMet: float
) -> pd.Series:
    Fd_IdMetRUPIn = Fd_dcRUP / 100 * Fd_MetRUPIn * SIDigMet
    return Fd_IdMetRUPIn


def calculate_Fd_IdPheRUPIn(
    Fd_dcRUP: pd.Series, 
    Fd_PheRUPIn: pd.Series, 
    SIDigPhe: float
) -> pd.Series:
    Fd_IdPheRUPIn = Fd_dcRUP / 100 * Fd_PheRUPIn * SIDigPhe
    return Fd_IdPheRUPIn


def calculate_Fd_IdThrRUPIn(
    Fd_dcRUP: pd.Series, 
    Fd_ThrRUPIn: pd.Series, 
    SIDigThr: float
) -> pd.Series:
    Fd_IdThrRUPIn = Fd_dcRUP / 100 * Fd_ThrRUPIn * SIDigThr
    return Fd_IdThrRUPIn


def calculate_Fd_IdTrpRUPIn(
    Fd_dcRUP: pd.Series, 
    Fd_TrpRUPIn: pd.Series, 
    SIDigTrp: float
) -> pd.Series:
    Fd_IdTrpRUPIn = Fd_dcRUP / 100 * Fd_TrpRUPIn * SIDigTrp
    return Fd_IdTrpRUPIn


def calculate_Fd_IdValRUPIn(
    Fd_dcRUP: pd.Series, 
    Fd_ValRUPIn: pd.Series, 
    SIDigVal: float
) -> pd.Series:
    Fd_IdValRUPIn = Fd_dcRUP / 100 * Fd_ValRUPIn * SIDigVal
    return Fd_IdValRUPIn


def calculate_Fd_DigC120In(
    TT_dcFdFA: pd.Series, 
    Fd_C120_FA: pd.Series, 
    Fd_FA: pd.Series, 
    Fd_DMIn: pd.Series
) -> pd.Series:
    Fd_DigC120In = TT_dcFdFA / 100 * Fd_C120_FA / 100 * Fd_FA / 100 * Fd_DMIn
    return Fd_DigC120In


def calculate_Fd_DigC140In(
    TT_dcFdFA: pd.Series, 
    Fd_C140_FA: pd.Series, 
    Fd_FA: pd.Series, 
    Fd_DMIn: pd.Series
) -> pd.Series:
    Fd_DigC140In = TT_dcFdFA / 100 * Fd_C140_FA / 100 * Fd_FA / 100 * Fd_DMIn
    return Fd_DigC140In


def calculate_Fd_DigC160In(
    TT_dcFdFA: pd.Series, 
    Fd_C160_FA: pd.Series, 
    Fd_FA: pd.Series, 
    Fd_DMIn: pd.Series
) -> pd.Series:
    Fd_DigC160In = TT_dcFdFA / 100 * Fd_C160_FA / 100 * Fd_FA / 100 * Fd_DMIn
    return Fd_DigC160In


def calculate_Fd_DigC161In(
    TT_dcFdFA: pd.Series, 
    Fd_C161_FA: pd.Series, 
    Fd_FA: pd.Series, 
    Fd_DMIn: pd.Series
) -> pd.Series:
    Fd_DigC161In = TT_dcFdFA / 100 * Fd_C161_FA / 100 * Fd_FA / 100 * Fd_DMIn
    return Fd_DigC161In


def calculate_Fd_DigC180In(
    TT_dcFdFA: pd.Series, 
    Fd_C180_FA: pd.Series, 
    Fd_FA: pd.Series, 
    Fd_DMIn: pd.Series
) -> pd.Series:
    Fd_DigC180In = TT_dcFdFA / 100 * Fd_C180_FA / 100 * Fd_FA / 100 * Fd_DMIn
    return Fd_DigC180In


def calculate_Fd_DigC181tIn(
    TT_dcFdFA: pd.Series, 
    Fd_C181t_FA: pd.Series, 
    Fd_FA: pd.Series, 
    Fd_DMIn: pd.Series
) -> pd.Series:
    Fd_DigC181tIn = TT_dcFdFA / 100 * Fd_C181t_FA / 100 * Fd_FA / 100 * Fd_DMIn
    return Fd_DigC181tIn


def calculate_Fd_DigC181cIn(
    TT_dcFdFA: pd.Series, 
    Fd_C181c_FA: pd.Series, 
    Fd_FA: pd.Series, 
    Fd_DMIn: pd.Series
) -> pd.Series:
    Fd_DigC181cIn = TT_dcFdFA / 100 * Fd_C181c_FA / 100 * Fd_FA / 100 * Fd_DMIn
    return Fd_DigC181cIn


def calculate_Fd_DigC182In(
    TT_dcFdFA: pd.Series, 
    Fd_C182_FA: pd.Series, 
    Fd_FA: pd.Series, 
    Fd_DMIn: pd.Series
) -> pd.Series:
    Fd_DigC182In = TT_dcFdFA / 100 * Fd_C182_FA / 100 * Fd_FA / 100 * Fd_DMIn
    return Fd_DigC182In


def calculate_Fd_DigC183In(
    TT_dcFdFA: pd.Series, 
    Fd_C183_FA: pd.Series, 
    Fd_FA: pd.Series, 
    Fd_DMIn: pd.Series
) -> pd.Series:
    Fd_DigC183In = TT_dcFdFA / 100 * Fd_C183_FA / 100 * Fd_FA / 100 * Fd_DMIn
    return Fd_DigC183In


def calculate_Fd_DigOtherFAIn(
    TT_dcFdFA: pd.Series, 
    Fd_OtherFA_FA: pd.Series, 
    Fd_FA: pd.Series, 
    Fd_DMIn: pd.Series
) -> pd.Series:
    Fd_DigOtherFAIn = TT_dcFdFA / 100 * Fd_OtherFA_FA / 100 * Fd_FA / 100 * Fd_DMIn
    return Fd_DigOtherFAIn


def calculate_Fd_ArgIn(
    Fd_CPIn: pd.Series, 
    Fd_Argt_CP: pd.Series, 
    Fd_CP: pd.Series, 
    Fd_DMIn: pd.Series
) -> pd.Series:
    Fd_ArgIn = np.where(
        Fd_CPIn > 0, 
        (Fd_Argt_CP / 100) * (Fd_CP / 100) * (Fd_DMIn * 1000), 
        0
    )
    return Fd_ArgIn


def calculate_Fd_HisIn(
    Fd_CPIn: pd.Series, 
    Fd_Hist_CP: pd.Series, 
    Fd_CP: pd.Series, 
    Fd_DMIn: pd.Series
) -> pd.Series:
    Fd_HisIn = np.where(
        Fd_CPIn > 0, 
        (Fd_Hist_CP / 100) * (Fd_CP / 100) * (Fd_DMIn * 1000), 
        0
    )
    return Fd_HisIn


def calculate_Fd_IleIn(
    Fd_CPIn: pd.Series, 
    Fd_Ilet_CP: pd.Series, 
    Fd_CP: pd.Series, 
    Fd_DMIn: pd.Series
) -> pd.Series:
    Fd_IleIn = np.where(
        Fd_CPIn > 0, 
        (Fd_Ilet_CP / 100) * (Fd_CP / 100) * (Fd_DMIn * 1000), 
        0
    )
    return Fd_IleIn


def calculate_Fd_LeuIn(
    Fd_CPIn: pd.Series, 
    Fd_Leut_CP: pd.Series, 
    Fd_CP: pd.Series, 
    Fd_DMIn: pd.Series
) -> pd.Series:
    Fd_LeuIn = np.where(
        Fd_CPIn > 0, 
        (Fd_Leut_CP / 100) * (Fd_CP / 100) * (Fd_DMIn * 1000), 
        0
    )
    return Fd_LeuIn


def calculate_Fd_LysIn(
    Fd_CPIn: pd.Series, 
    Fd_Lyst_CP: pd.Series, 
    Fd_CP: pd.Series, 
    Fd_DMIn: pd.Series
) -> pd.Series:
    Fd_LysIn = np.where(
        Fd_CPIn > 0, 
        (Fd_Lyst_CP / 100) * (Fd_CP / 100) * (Fd_DMIn * 1000), 
        0
    )
    return Fd_LysIn


def calculate_Fd_MetIn(
    Fd_CPIn: pd.Series, 
    Fd_Mett_CP: pd.Series, 
    Fd_CP: pd.Series, 
    Fd_DMIn: pd.Series
) -> pd.Series:
    Fd_MetIn = np.where(
        Fd_CPIn > 0, 
        (Fd_Mett_CP / 100) * (Fd_CP / 100) * (Fd_DMIn * 1000), 
        0
    )
    return Fd_MetIn


def calculate_Fd_PheIn(
    Fd_CPIn: pd.Series, 
    Fd_Phet_CP: pd.Series, 
    Fd_CP: pd.Series, 
    Fd_DMIn: pd.Series
) -> pd.Series:
    Fd_PheIn = np.where(
        Fd_CPIn > 0, 
        (Fd_Phet_CP / 100) * (Fd_CP / 100) * (Fd_DMIn * 1000), 
        0
    )
    return Fd_PheIn


def calculate_Fd_ThrIn(
    Fd_CPIn: pd.Series, 
    Fd_Thrt_CP: pd.Series, 
    Fd_CP: pd.Series, 
    Fd_DMIn: pd.Series
) -> pd.Series:
    Fd_ThrIn = np.where(
        Fd_CPIn > 0, 
        (Fd_Thrt_CP / 100) * (Fd_CP / 100) * (Fd_DMIn * 1000), 
        0
    )
    return Fd_ThrIn


def calculate_Fd_TrpIn(
    Fd_CPIn: pd.Series, 
    Fd_Trpt_CP: pd.Series, 
    Fd_CP: pd.Series, 
    Fd_DMIn: pd.Series
) -> pd.Series:
    Fd_TrpIn = np.where(
        Fd_CPIn > 0, 
        (Fd_Trpt_CP / 100) * (Fd_CP / 100) * (Fd_DMIn * 1000), 
        0
    )
    return Fd_TrpIn


def calculate_Fd_ValIn(
    Fd_CPIn: pd.Series, 
    Fd_Valt_CP: pd.Series, 
    Fd_CP: pd.Series, 
    Fd_DMIn: pd.Series
) -> pd.Series:
    Fd_ValIn = np.where(
        Fd_CPIn > 0, 
        (Fd_Valt_CP / 100) * (Fd_CP / 100) * (Fd_DMIn * 1000), 
        0
    )
    return Fd_ValIn


def calculate_Fd_AFInp(Fd_AFIn: pd.Series) -> pd.Series:
    Fd_AFInp = Fd_AFIn / Fd_AFIn.sum()
    return Fd_AFInp


def calculate_Fd_RDPIn(Fd_RDP: pd.Series, Fd_DMIn: pd.Series) -> pd.Series:
    Fd_RDPIn = Fd_RDP / 100 * Fd_DMIn
    return Fd_RDPIn


####################
# Functions for Diet Intakes
####################
def calculate_Dt_ForDNDF48(
    Fd_DMInp: pd.Series, 
    Fd_Conc: pd.Series, 
    Fd_NDF: pd.Series, 
    Fd_DNDF48: pd.Series
) -> float:
    Dt_ForDNDF48 = ((1 - Fd_Conc / 100) * Fd_NDF * Fd_DNDF48 / 100 *
                    Fd_DMInp).sum()  # Line 259
    return Dt_ForDNDF48


def calculate_Dt_ForDNDF48_ForNDF(
    Dt_ForDNDF48: float, 
    Dt_ForNDF: float
) -> float:
    if Dt_ForNDF != 0 and not np.isnan(Dt_ForNDF):
        Dt_ForDNDF48_ForNDF = Dt_ForDNDF48 / Dt_ForNDF * 100 # Line 260
    else:
        Dt_ForDNDF48_ForNDF = None
    return Dt_ForDNDF48_ForNDF


def calculate_Dt_ADF_NDF(Dt_ADF: float, Dt_NDF: float) -> float:
    Dt_ADF_NDF = Dt_ADF / Dt_NDF  # Line 261
    return Dt_ADF_NDF


def calculate_Dt_DE_ClfLiq(
    Dt_DEIn_ClfLiq: float, 
    Dt_DMIn_ClfLiq: float
) -> float:
    # Line 289, DE content of the liquid feed
    Dt_DE_ClfLiq = 0 if Dt_DEIn_ClfLiq == 0 else Dt_DEIn_ClfLiq / Dt_DMIn_ClfLiq
    Dt_DE_ClfLiq = 0 if np.isnan(Dt_DE_ClfLiq) else Dt_DE_ClfLiq # Line 290
    return Dt_DE_ClfLiq


def calculate_Dt_ME_ClfLiq(
    Dt_MEIn_ClfLiq: float, 
    Dt_DMIn_ClfLiq: float
) -> float:
    # Line 291, ME content of the liquid feed
    Dt_ME_ClfLiq = Dt_MEIn_ClfLiq / Dt_DMIn_ClfLiq
    Dt_ME_ClfLiq = 0 if np.isnan(Dt_ME_ClfLiq) else Dt_ME_ClfLiq # Line 292    
    return Dt_ME_ClfLiq


def calculate_Dt_NDFnfIn(Fd_DMIn: pd.Series, Fd_NDFnf: pd.Series) -> float:
    Dt_NDFnfIn = (Fd_NDFnf / 100 * Fd_DMIn).sum()  # Line 588
    return Dt_NDFnfIn


def calculate_Dt_Lg_NDF(Dt_LgIn: float, Dt_NDFIn: float) -> float:
    Dt_Lg_NDF = Dt_LgIn / Dt_NDFIn * 100  # Line 591
    return Dt_Lg_NDF


def calculate_Dt_ForNDFIn(Fd_DMIn: pd.Series, Fd_ForNDF: pd.Series) -> float:
    Dt_ForNDFIn = (Fd_ForNDF / 100 * Fd_DMIn).sum()  # Line 592
    return Dt_ForNDFIn


def calculate_Dt_PastSupplIn(Dt_DMInSum: float, Dt_PastIn: float) -> float:
    # Line 597, Could be supplemental concentrate or forage
    Dt_PastSupplIn = Dt_DMInSum - Dt_PastIn
    return Dt_PastSupplIn


def calculate_Dt_NIn(Dt_CPIn: float) -> float:
    Dt_NIn = Dt_CPIn / 6.25  # Line 614
    return Dt_NIn


def calculate_Dt_RUPIn(Fd_RUPIn: pd.Series) -> float:
    # The feed summation is not as accurate as the equation below
    Dt_RUPIn = Fd_RUPIn.sum()  # Line 616
    Dt_RUPIn = 0 if Dt_RUPIn < 0 else Dt_RUPIn # Line 617

    # The following diet level RUPIn is slightly more accurate than the feed 
    # level summation as the intercept exactly matches the regression equations, 
    # but feed level is very close.
    # if concerned about intercept, switch to using this eqn for RUP
    # this is called Dt_RUPIn.dt in the R code line 618
    # Dt_RUPIn = (Dt_CPAIn - Dt_NPNIn) * coeff_dict['fCPAdu'] + Dt_RUPBIn + 
    # Dt_CPCIn + coeff_dict['IntRUP']   # Line 619
    return Dt_RUPIn


def calculate_Dt_RUP_CP(Dt_CPIn: float, Dt_RUPIn: float) -> float:
    Dt_RUP_CP = Dt_RUPIn / Dt_CPIn * 100  # Line 621
    return Dt_RUP_CP


def calculate_Dt_fCPBdu(Dt_RUPBIn: float, Dt_CPBIn: float) -> float:
    Dt_fCPBdu = Dt_RUPBIn / Dt_CPBIn  # Line 622
    return Dt_fCPBdu


def calculate_Dt_UFAIn(
    Dt_C161In: float, 
    Dt_C181tIn: float, 
    Dt_C181cIn: float, 
    Dt_C182In: float, 
    Dt_C183In: float
) -> float:
    Dt_UFAIn = Dt_C161In + Dt_C181tIn + Dt_C181cIn + Dt_C182In + Dt_C183In
    # Line 639
    return Dt_UFAIn


def calculate_Dt_MUFAIn(
    Dt_C161In: float, 
    Dt_C181tIn: float, 
    Dt_C181cIn: float
) -> float:
    Dt_MUFAIn = Dt_C161In + Dt_C181tIn + Dt_C181cIn  # Line 640
    return Dt_MUFAIn


def calculate_Dt_PUFAIn(
    Dt_UFAIn: float, 
    Dt_C161In: float, 
    Dt_C181tIn: float, 
    Dt_C181cIn: float
) -> float:
    Dt_PUFAIn = Dt_UFAIn - (Dt_C161In + Dt_C181tIn + Dt_C181cIn)  # Line 641
    return Dt_PUFAIn


def calculate_Dt_SatFAIn(Dt_FAIn: float, Dt_UFAIn: float) -> float:
    Dt_SatFAIn = Dt_FAIn - Dt_UFAIn  # Line 642
    return Dt_SatFAIn


def calculate_Dt_OMIn(Dt_DMIn: float, Dt_AshIn: float) -> float:
    Dt_OMIn = Dt_DMIn - Dt_AshIn  # Line 645
    return Dt_OMIn


def calculate_Dt_rOMIn(
    Dt_DMIn: float, 
    Dt_AshIn: float, 
    Dt_NDFIn: float, 
    Dt_StIn: float, 
    Dt_FAhydrIn: float, 
    Dt_TPIn: float,
    Dt_NPNDMIn: float
) -> float:
    Dt_rOMIn = (Dt_DMIn - Dt_AshIn - Dt_NDFIn - Dt_StIn - 
                Dt_FAhydrIn - Dt_TPIn - Dt_NPNDMIn) # Line 646
    # Is negative on some diets. Some Ash and CP in NDF, and water from FAhydr 
    # in TAG contributes. Trap negative Dt values. More likely due to entry 
    # errors or bad analyses of other nutrients
    Dt_rOMIn = 0 if Dt_rOMIn < 0  else Dt_rOMIn # Lines 647
    return Dt_rOMIn


def calculate_Dt_DM(Dt_DMIn: float, Dt_AFIn: float) -> float:
    Dt_DM = Dt_DMIn / Dt_AFIn * 100  # Line 655
    return Dt_DM


def calculate_Dt_NDFIn_BW(An_BW: float, Dt_NDFIn: float) -> float:
    Dt_NDFIn_BW = Dt_NDFIn / An_BW * 100  # Line 658
    return Dt_NDFIn_BW


def calculate_Dt_ForNDF_NDF(Dt_ForNDF: float, Dt_NDF: float) -> float:
    Dt_ForNDF_NDF = Dt_ForNDF / Dt_NDF * 100  # Line 663
    return Dt_ForNDF_NDF


def calculate_Dt_ForNDFIn_BW(An_BW: float, Dt_ForNDFIn: float) -> float:
    Dt_ForNDFIn_BW = Dt_ForNDFIn / An_BW * 100  # Line 664
    return Dt_ForNDFIn_BW


def calculate_Dt_DMInSum(Fd_DMIn: pd.Series) -> float:
    Dt_DMInSum = Fd_DMIn.sum()  # Line 579
    return Dt_DMInSum


def calculate_Dt_DEIn_ClfLiq(
    Fd_DE_ClfLiq: pd.Series, 
    Fd_DMIn_ClfLiq: pd.Series
) -> float:
    Dt_DEIn_ClfLiq = (Fd_DE_ClfLiq * Fd_DMIn_ClfLiq).sum()  # Line 287
    return Dt_DEIn_ClfLiq


def calculate_Dt_MEIn_ClfLiq(
    Fd_ME_ClfLiq: pd.Series, 
    Fd_DMIn_ClfLiq: pd.Series
) -> float:
    Dt_MEIn_ClfLiq = (Fd_ME_ClfLiq * Fd_DMIn_ClfLiq).sum()  # Line 288
    return Dt_MEIn_ClfLiq


def calculate_Dt_CPA_CP(Dt_CPAIn: float, Dt_CPIn: float) -> float:
    Dt_CPA_CP = Dt_CPAIn / Dt_CPIn * 100  # Line 684
    return Dt_CPA_CP


def calculate_Dt_CPB_CP(Dt_CPBIn: float, Dt_CPIn: float) -> float:
    Dt_CPB_CP = Dt_CPBIn / Dt_CPIn * 100  # Line 685
    return Dt_CPB_CP


def calculate_Dt_CPC_CP(Dt_CPCIn: float, Dt_CPIn: float) -> float:
    Dt_CPC_CP = Dt_CPCIn / Dt_CPIn * 100  # Line 686
    return Dt_CPC_CP


def calculate_Dt_RDPIn(Dt_CPIn: float, Dt_RUPIn: float) -> float:
    Dt_RDPIn = Dt_CPIn - Dt_RUPIn  # Line 1101
    return Dt_RDPIn


def calculate_Dt_DigNDFIn(TT_dcNDF: float, Dt_NDFIn: float) -> float:
    Dt_DigNDFIn = TT_dcNDF / 100 * Dt_NDFIn
    return Dt_DigNDFIn


def calculate_Dt_DigStIn(Dt_StIn: float, TT_dcSt: float) -> float:
    Dt_DigStIn = Dt_StIn * TT_dcSt / 100  # Line 1032
    return Dt_DigStIn


def calculate_Dt_DigrOMaIn(Dt_DigrOMtIn: float, Fe_rOMend: float) -> float:
    Dt_DigrOMaIn = Dt_DigrOMtIn - Fe_rOMend
    return Dt_DigrOMaIn


def calculate_Dt_dcCP_ClfDry(An_StatePhys: str, Dt_DMIn_ClfLiq: float) -> float:
    Dt_dcCP_ClfDry = (0.70 
                      if (An_StatePhys == "Calf") and (Dt_DMIn_ClfLiq < 0.01)
                      else 0.75) # Line 1199
    return Dt_dcCP_ClfDry


def calculate_Dt_DENDFIn(Dt_DigNDFIn: float, coeff_dict: dict) -> float:
    """
    Examples
    --------
    ``
    coeff_dict = {'En_NDF': 4.2}

    calculate_Dt_DENDFIn(
        Dt_DigNDFIn = 10.0, coeff_dict = coeff_dict
    )
    ```
    """
    Dt_DENDFIn = Dt_DigNDFIn * coeff_dict['En_NDF']
    return Dt_DENDFIn


def calculate_Dt_DEStIn(Dt_DigStIn: float, coeff_dict: dict) -> float:
    """
    Examples
    --------
    ```
    coeff_dict = {'En_St': 4.23}
    
    calculate_Dt_DEStIn(
        Dt_DigStIn = 12.0, coeff_dict = coeff_dict
    )
    ```
    """
    Dt_DEStIn = Dt_DigStIn * coeff_dict['En_St']
    return Dt_DEStIn


def calculate_Dt_DErOMIn(Dt_DigrOMaIn: float, coeff_dict: dict) -> float:
    """
    Examples
    --------
    ```
    coeff_dict = {'En_rOM': 4.0}
    
    calculate_Dt_DErOMIn(
        Dt_DigrOMaIn = 12.0, coeff_dict = coeff_dict
    )
    ```
    """
    Dt_DErOMIn = Dt_DigrOMaIn * coeff_dict['En_rOM']  # Line 1344
    return Dt_DErOMIn


def calculate_Dt_DENPNCPIn(Dt_NPNCPIn: float, coeff_dict: dict) -> float:
    """
    Examples
    --------
    ```
    coeff_dict = {
        'dcNPNCP': 100, 'En_NPNCP': 0.89
    }
    
    calculate_Dt_DENPNCPIn(
        Dt_NPNCPIn = 15.0, coeff_dict = coeff_dict
    )
    ```
    """
    Dt_DENPNCPIn = (Dt_NPNCPIn * coeff_dict['dcNPNCP'] / 
                    100 * coeff_dict['En_NPNCP'])
    return Dt_DENPNCPIn


def calculate_Dt_DEFAIn(Dt_DigFAIn: float, coeff_dict: dict) -> float:
    """
    Examples
    --------
    ```
    coeff_dict = {'En_FA': 9.4}
    
    calculate_Dt_DEFAIn(
        Dt_DigFAIn = 10.0, coeff_dict = coeff_dict
    )
    ```
    """
    Dt_DEFAIn = Dt_DigFAIn * coeff_dict['En_FA']
    return Dt_DEFAIn


def calculate_Dt_DMIn_ClfStrt(
    An_BW: float, 
    Dt_MEIn_ClfLiq: float, 
    Dt_DMIn_ClfLiq: float,
    Dt_DMIn_ClfFor: float, 
    An_AgeDryFdStart: int, 
    Env_TempCurr: float,
    DMIn_eqn: int, 
    Trg_Dt_DMIn: float, 
    coeff_dict: dict
) -> float:
    """
    Examples
    --------
    ```
    coeff_dict = {'UCT': 25.0}

    calculate_Dt_DMIn_ClfStrt(
        An_BW = 100.0, Dt_MEIn_ClfLiq = 15.0, Dt_DMIn_ClfLiq = 2.0, 
        Dt_DMIn_ClfFor = 3.0, An_AgeDryFdStart = 30, Env_TempCurr = 28.0, 
        DMIn_eqn = 1, Trg_Dt_DMIn = 10.0, coeff_dict = coeff_dict
    )
    ```
    """
    # Predict Calf Starter Intake, kg/d
    # Temperate Environment Predicted Starter Intake, Line 301
    Dt_DMIn_ClfStrt = (-652.5 + 14.734 * An_BW + 
                       18.896 * Dt_MEIn_ClfLiq + 
                       73.3 * An_AgeDryFdStart / 7 + 
                       13.496 * (An_AgeDryFdStart / 7)**2 - 
                       29.614 * An_AgeDryFdStart / 7 * Dt_MEIn_ClfLiq) / 1000
    
    # Tropical Environment Predicted Starter Intake, TempCurr > UCT+10 degrees C
    if Env_TempCurr > coeff_dict['UCT'] + 10: # Line 305
        Dt_DMIn_ClfStrt = ( 
            600.1 * (1 + 14863.7 * np.exp(-1.553 * An_AgeDryFdStart / 7))**-1 + 
            9.951 * An_BW - 
            130.434 * Dt_MEIn_ClfLiq) / 1000
        
    # Adjust Starter Intake based on target intake if DMIeqn=0. Line 311
    clf_dmi_sum = Dt_DMIn_ClfLiq + Dt_DMIn_ClfStrt + Dt_DMIn_ClfFor
    Dt_DMIn_ClfStrt = (Trg_Dt_DMIn - Dt_DMIn_ClfLiq - Dt_DMIn_ClfFor
                       if (DMIn_eqn == 0) and (clf_dmi_sum != Trg_Dt_DMIn)
                       else Dt_DMIn_ClfStrt)
    return Dt_DMIn_ClfStrt


def calculate_Dt_DigCPaIn(Dt_CPIn: float, Fe_CP: float) -> float:
    Dt_DigCPaIn = Dt_CPIn - Fe_CP  # kg CP/d, apparent total tract digested CP
    return Dt_DigCPaIn


def calculate_Dt_DECPIn(Dt_DigCPaIn: float, coeff_dict: dict) -> float:
    """
    Examples
    --------
    ```
    coeff_dict = {'En_CP': 5.65}

    calculate_Dt_DECPIn(
        Dt_DigCPaIn = 10.0, coeff_dict = coeff_dict
    )
    ```
    """
    Dt_DECPIn = Dt_DigCPaIn * coeff_dict['En_CP']
    return Dt_DECPIn


def calculate_Dt_DETPIn(
    Dt_DECPIn: float, 
    Dt_DENPNCPIn: float, 
    coeff_dict: dict
) -> float:
    """
    Examples
    --------
    ```
    coeff_dict = {
        'En_NPNCP': 0.89, 'En_CP': 5.65
    }

    calculate_Dt_DETPIn(
        Dt_DECPIn = 20.0, Dt_DENPNCPIn = 15.0, coeff_dict = coeff_dict
    )
    ```
    """
    # Line 1348, Caution! DigTPaIn not clean so subtracted DE for CP equiv of 
    # NPN to correct. Not a true DE_TP.
    Dt_DETPIn = (Dt_DECPIn - Dt_DENPNCPIn / 
                 coeff_dict['En_NPNCP'] * coeff_dict['En_CP'])
    return Dt_DETPIn


def calculate_Dt_DEIn(
    An_StatePhys: str, 
    Dt_DENDFIn: float, 
    Dt_DEStIn: float, 
    Dt_DErOMIn: float,
    Dt_DETPIn: float, 
    Dt_DENPNCPIn: float, 
    Dt_DEFAIn: float, 
    Dt_DMIn_ClfLiq: float,
    Dt_DEIn_base_ClfLiq: float, 
    Dt_DEIn_base_ClfDry: float, 
    Monensin_eqn: int
) -> float:
    Dt_DEIn = (Dt_DENDFIn + Dt_DEStIn + Dt_DErOMIn + 
               Dt_DETPIn + Dt_DENPNCPIn + Dt_DEFAIn) # Line 1365
    Dt_DEIn = (Dt_DEIn_base_ClfLiq + Dt_DEIn_base_ClfDry
               if (An_StatePhys == "Calf") and (Dt_DMIn_ClfLiq > 0)
               else Dt_DEIn) # Line 1371
    Dt_DEIn = Dt_DEIn * 1.02 if Monensin_eqn == 1 else Dt_DEIn # Line 1374  
    return Dt_DEIn


def calculate_Dt_acMg(
    An_StatePhys: str, 
    Dt_K: float, 
    Dt_MgIn_min: float,
    Dt_MgIn: float
) -> float:
    if An_StatePhys == "Calf": # Line 1880
        Dt_acMg = 1.0
    else:
        Dt_acMg = (44.1 - 5.42 * math.log(Dt_K * 10) - 
                   0.08 * Dt_MgIn_min / Dt_MgIn * 100) / 100
    return Dt_acMg


def calculate_Abs_MgIn(Dt_acMg: float, Dt_MgIn: float) -> float:
    Abs_MgIn = Dt_acMg * Dt_MgIn  # Mg absorption is inhibited by K, Line 1881
    return Abs_MgIn


def calculate_Dt_DigWSCIn(Fd_DigWSCIn: pd.Series) -> float:
    """
    Dt_DigWSCIn: Digestable water soluble carbohydrate intake, kg/d
    """
    Dt_DigWSCIn = Fd_DigWSCIn.sum()  
    # This is not used as it isn't additive with St, MDH. Line 1019
    return Dt_DigWSCIn


def calculate_Dt_DigSt(Dt_DigStIn: float, Dt_DMIn: float) -> float:
    """
    Dt_DigSt: Digestable starch, % DM
    """
    Dt_DigSt = Dt_DigStIn / Dt_DMIn * 100  # Line 1036
    return Dt_DigSt


def calculate_Dt_DigWSC(Dt_DigWSCIn: float, Dt_DMIn: float) -> float:
    """
    Dt_DigWSC: Digestable water soluble carbohydrate, % DM
    """
    Dt_DigWSC = Dt_DigWSCIn / Dt_DMIn * 100  # line 1038
    return Dt_DigWSC


def calculate_Dt_DigrOMa(Dt_DigrOMaIn: float, Dt_DMIn: float) -> float:
    """
    Dt_DigrOMa: Apparently digestable residual organic matter, % DM
    """
    Dt_DigrOMa = Dt_DigrOMaIn / Dt_DMIn * 100  # Line 1040
    return Dt_DigrOMa


def calculate_Dt_DigrOMa_Dt(Dt_rOM: float, coeff_dict: dict) -> float:
    """
    Dt_DigrOMa_Dt: Apparently digestable residual organic matter, % DM???
    
    This variable is not used anywhere, used as crosscheck? (see comment)
    
    Examples
    --------
    ```
    coeff_dict = {'Fe_rOMend_DMI': 3.43}

    calculate_Dt_DigrOMa_Dt(
        Dt_rOM = 25.0, coeff_dict = coeff_dict
    )
    ```
    """
    # In R code variable is Dt_DigrOMa.Dt
    Dt_DigrOMa_Dt = Dt_rOM * 0.96 - coeff_dict['Fe_rOMend_DMI']  
    # Crosscheck the feed level calculation and summation., Line 1041
    return Dt_DigrOMa_Dt


def calculate_Dt_DigrOMt(Dt_DigrOMtIn: float, Dt_DMIn: float) -> float:
    """
    Dt_DigrOMt: Truly digested residual organic matter, % DM
    """
    Dt_DigrOMt = Dt_DigrOMtIn / Dt_DMIn * 100  # Line 1042
    return Dt_DigrOMt


def calculate_Dt_DigNDFnfIn(TT_dcNDF: float, Dt_NDFnfIn: float) -> float:
    """
    Dt_DigNDFnfIn: Nitrogen Free Digestable NDF Intake, kg/d 
    """
    Dt_DigNDFnfIn = TT_dcNDF / 100 * Dt_NDFnfIn  # Line 1064
    return Dt_DigNDFnfIn


def calculate_Dt_DigNDF(Dt_DigNDFIn: float, Dt_DMIn: float) -> float:
    """
    Dt_DigNDF: Digestable NDF, % DM
    """
    Dt_DigNDF = Dt_DigNDFIn / Dt_DMIn * 100  # Line 1065
    return Dt_DigNDF


def calculate_Dt_DigNDFnf(Dt_DigNDFnfIn: float, Dt_DMIn: float) -> float:
    """
    Dt_DigNDFnf: Nitrogen free Digestable NDF, % DM
    """
    Dt_DigNDFnf = Dt_DigNDFnfIn / Dt_DMIn * 100
    return Dt_DigNDFnf


def calculate_Dt_idcRUP(Dt_idRUPIn: float, Dt_RUPIn: float) -> float:
    """
    Dt_idcRUP: Intestinal digestability of RUP, no units
    """
    Dt_idcRUP = Dt_idRUPIn / Dt_RUPIn * 100  
    # Intestinal digestibility of RUP, Line 1075
    return Dt_idcRUP


def calculate_Dt_Fe_RUPout(Fd_Fe_RUPout: float | pd.Series) -> float:
    """
    Dt_Fe_RUPout: Fecal rumed undegradable protein output from diet, kg/d
    """
    Dt_Fe_RUPout = Fd_Fe_RUPout.sum()  # Line 1081
    return Dt_Fe_RUPout


def calculate_Dt_RDTPIn(
    Dt_RDPIn: float, 
    Dt_NPNCPIn: float,
    coeff_dict: dict
) -> float:
    """
    Dt_RDTPIn: Rumed degradable true protein intake, kg/d
    
    Examples
    --------
    ```
    coeff_dict = {'dcNPNCP':100}

    calculate_Dt_RDTPIn(
        Dt_RDPIn = 10.0, Dt_NPNCPIn = 2.0, coeff_dict = coeff_dict
    )
    ```
    """
    Dt_RDTPIn = Dt_RDPIn - (Dt_NPNCPIn * coeff_dict['dcNPNCP'] / 100)  
    # assumes all NPN is soluble. Reflects only urea and ammonium salt
    # NPN sources, Line 1102
    return Dt_RDTPIn


def calculate_Dt_RDP(Dt_RDPIn: float, Dt_DMIn: float) -> float:
    """
    Dt_RDP: Diet rumed degradable protein, % DM
    """
    Dt_RDP = Dt_RDPIn / Dt_DMIn * 100  # Line 1103
    return Dt_RDP


def calculate_Dt_RDP_CP(Dt_RDP: float, Dt_CP: float) -> float:
    """
    Dt_RDP_CP: Diet rumed degradable protein % of crude protein
    """
    Dt_RDP_CP = Dt_RDP / Dt_CP * 100  # Line 1104
    return Dt_RDP_CP


def calculate_Dt_GE(Dt_GEIn: float, Dt_DMIn: float) -> float:
    """
    Dt_GE: Gross energy concentration (Mcal/kg diet)
    """
    Dt_GE = Dt_GEIn / Dt_DMIn  # Line 1340
    return Dt_GE


def calculate_Dt_DE(Dt_DEIn: float, Dt_DMIn: float) -> float:
    """
    Dt_DE: Digestable energy (Mcal/d)
    """
    Dt_DE = Dt_DEIn / Dt_DMIn  # Line 1377
    return Dt_DE


def calculate_Dt_TDN(
    Dt_DigSt: float, 
    Dt_DigNDF: float, 
    Dt_DigrOMa: float,
    Dt_DigCPa: float, 
    Dt_DigFA: float
) -> float:
    """
    Dt_TDN: Dietary total digestable nutrients (kg/d)
    """
    Dt_TDN = Dt_DigSt + Dt_DigNDF + Dt_DigrOMa + Dt_DigCPa + Dt_DigFA * 2.25
    # Line 1387
    return Dt_TDN


def calculate_Dt_TDNIn(Dt_TDN: float, Dt_DMIn: float) -> float:
    """
    Dt_TDNIn: Total digestable nutrients (% DMI)
    """
    Dt_TDNIn = Dt_TDN / 100 * Dt_DMIn  # Line 1388
    return Dt_TDNIn


def calculate_Dt_GasE_IPCC2(Dt_GEIn: float) -> float:
    """
    Dt_GasE_IPCC2: ? (Mcal/d)
    """
    Dt_GasE_IPCC2 = 0.065 * Dt_GEIn # for comparison purposes, Line 1392
    return Dt_GasE_IPCC2


def calculate_Dt_GasEOut_Lact(
    Dt_DMIn: float, 
    Dt_FA: float,
    Dt_DigNDF: float
) -> float:
    """
    Dt_GasEOut_Lact: Gaseous energy loss, lactating cow (Mcal/d)
    """
    Dt_GasEOut_Lact = 0.294 * Dt_DMIn - 0.347 * Dt_FA + 0.0409 * Dt_DigNDF  
    # Lact Cows, Line 1395
    return Dt_GasEOut_Lact


def calculate_Dt_GasEOut_Heif(Dt_GEIn: float, Dt_NDF: float) -> float:
    """
    Dt_GasEOut_Heif: Gaseous energy loss, heifer (Mcal/d)
    """
    Dt_GasEOut_Heif = -0.038 + 0.051 * Dt_GEIn - 0.0091 * Dt_NDF  
    # Heifers/Buls, Line 1396
    return Dt_GasEOut_Heif


def calculate_Dt_GasEOut_Dry(Dt_GEIn: float, Dt_FA: float) -> float:
    """
    Dt_GasEOut_Dry: Gaseous energy loss, dry cow (Mcal/d)
    """
    Dt_GasEOut_Dry = -0.69 + 0.053 * Dt_GEIn - 0.0789 * Dt_FA  
    #Heifers/Bulls, convert from EE to FA assum 57% FA in EE, from BW, Line 1397
    return Dt_GasEOut_Dry


def calculate_Dt_GasEOut(
    An_StatePhys: str, 
    Monensin_eqn: int, 
    Dt_DMIn: float,
    Dt_FA: float, 
    Dt_DigNDF: float, 
    Dt_GEIn: float,
    Dt_NDF: float
) -> float:
    """
    Dt_GasEOut: Gaseous energy loss (Mcal/d)
    """
    if An_StatePhys == "Lactating Cow":  # Line 1400-1404
        Dt_GasEOut = calculate_Dt_GasEOut_Lact(Dt_DMIn, Dt_FA, Dt_DigNDF)
    elif An_StatePhys == "Heifer":
        Dt_GasEOut = calculate_Dt_GasEOut_Heif(Dt_GEIn, Dt_NDF)
    elif An_StatePhys == "Dry Cow":
        Dt_GasEOut = calculate_Dt_GasEOut_Dry(Dt_GEIn, Dt_FA)
    elif An_StatePhys == "Calf":
        Dt_GasEOut = 0.0
    # No observations on calves.
    # Would not be 0 once the calf starts eating dry feed.
    if Monensin_eqn == 1:
        Dt_GasEOut = Dt_GasEOut * 0.95
    return Dt_GasEOut


def calculate_Dt_ADF(Fd_DMInp: pd.Series, Fd_ADF: pd.Series) -> float:
    Dt_ADF = (Fd_DMInp * Fd_ADF).sum()
    return Dt_ADF


def calculate_Dt_NDF(Fd_DMInp: pd.Series, Fd_NDF: pd.Series) -> float:
    Dt_NDF = (Fd_DMInp * Fd_NDF).sum()
    return Dt_NDF


def calculate_Dt_For(Fd_DMInp: pd.Series, Fd_For: pd.Series) -> float:
    Dt_For = (Fd_DMInp * Fd_For).sum()
    return Dt_For


def calculate_Dt_ForNDF(Fd_DMInp: pd.Series, Fd_ForNDF: pd.Series) -> float:
    Dt_ForNDF = (Fd_DMInp * Fd_ForNDF).sum()
    return Dt_ForNDF


def calculate_Dt_DMIn_ClfLiq(Fd_DMIn_ClfLiq: pd.Series) -> float:
    Dt_DMIn_ClfLiq = Fd_DMIn_ClfLiq.sum()
    return Dt_DMIn_ClfLiq


def calculate_Dt_DMIn_ClfFor(Fd_DMIn_ClfFor: pd.Series) -> float:
    Dt_DMIn_ClfFor = Fd_DMIn_ClfFor.sum()
    return Dt_DMIn_ClfFor


def calculate_Dt_AFIn(Fd_AFIn: pd.Series) -> float:
    Dt_AFIn = Fd_AFIn.sum()
    return Dt_AFIn


def calculate_Dt_NDFIn(Fd_NDFIn: pd.Series) -> float:
    Dt_NDFIn = Fd_NDFIn.sum()
    return Dt_NDFIn


def calculate_Dt_ADFIn(Fd_ADFIn: pd.Series) -> float:
    Dt_ADFIn = Fd_ADFIn.sum()
    return Dt_ADFIn


def calculate_Dt_LgIn(Fd_LgIn: pd.Series) -> float:
    Dt_LgIn = Fd_LgIn.sum()
    return Dt_LgIn


def calculate_Dt_DigNDFIn_Base(Fd_DigNDFIn_Base: pd.Series) -> float:
    Dt_DigNDFIn_Base = Fd_DigNDFIn_Base.sum()
    return Dt_DigNDFIn_Base


def calculate_Dt_ForWetIn(Fd_ForWetIn: pd.Series) -> float:
    Dt_ForWetIn = Fd_ForWetIn.sum()
    return Dt_ForWetIn


def calculate_Dt_ForDryIn(Fd_ForDryIn: pd.Series) -> float:
    Dt_ForDryIn = Fd_ForDryIn.sum()
    return Dt_ForDryIn


def calculate_Dt_PastIn(Fd_PastIn: pd.Series) -> float:
    Dt_PastIn = Fd_PastIn.sum()
    return Dt_PastIn


def calculate_Dt_ForIn(Fd_ForIn: pd.Series) -> float:
    Dt_ForIn = Fd_ForIn.sum()
    return Dt_ForIn


def calculate_Dt_ConcIn(Fd_ConcIn: pd.Series) -> float:
    Dt_ConcIn = Fd_ConcIn.sum()
    return Dt_ConcIn


def calculate_Dt_NFCIn(Fd_NFCIn: pd.Series) -> float:
    Dt_NFCIn = Fd_NFCIn.sum()
    return Dt_NFCIn


def calculate_Dt_StIn(Fd_StIn: pd.Series) -> float:
    Dt_StIn = Fd_StIn.sum()
    return Dt_StIn


def calculate_Dt_WSCIn(Fd_WSCIn: pd.Series) -> float:
    Dt_WSCIn = Fd_WSCIn.sum()
    return Dt_WSCIn


def calculate_Dt_CPIn(Fd_CPIn: pd.Series) -> float:
    Dt_CPIn = Fd_CPIn.sum()
    return Dt_CPIn


def calculate_Dt_CPIn_ClfLiq(Fd_CPIn_ClfLiq: pd.Series) -> float:
    Dt_CPIn_ClfLiq = Fd_CPIn_ClfLiq.sum()
    return Dt_CPIn_ClfLiq


def calculate_Dt_TPIn(Fd_TPIn: pd.Series) -> float:
    Dt_TPIn = Fd_TPIn.sum()
    return Dt_TPIn


def calculate_Dt_NPNCPIn(Fd_NPNCPIn: pd.Series) -> float:
    Dt_NPNCPIn = Fd_NPNCPIn.sum()
    return Dt_NPNCPIn


def calculate_Dt_NPNIn(Fd_NPNIn: pd.Series) -> float:
    Dt_NPNIn = Fd_NPNIn.sum()
    return Dt_NPNIn


def calculate_Dt_NPNDMIn(Fd_NPNDMIn: pd.Series) -> float:
    Dt_NPNDMIn = Fd_NPNDMIn.sum()
    return Dt_NPNDMIn


def calculate_Dt_CPAIn(Fd_CPAIn: pd.Series) -> float:
    Dt_CPAIn = Fd_CPAIn.sum()
    return Dt_CPAIn


def calculate_Dt_CPBIn(Fd_CPBIn: pd.Series) -> float:
    Dt_CPBIn = Fd_CPBIn.sum()
    return Dt_CPBIn


def calculate_Dt_CPCIn(Fd_CPCIn: pd.Series) -> float:
    Dt_CPCIn = Fd_CPCIn.sum()
    return Dt_CPCIn


def calculate_Dt_RUPBIn(Fd_RUPBIn: pd.Series) -> float:
    Dt_RUPBIn = Fd_RUPBIn.sum()
    return Dt_RUPBIn


def calculate_Dt_CFatIn(Fd_CFatIn: pd.Series) -> float:
    Dt_CFatIn = Fd_CFatIn.sum()
    return Dt_CFatIn


def calculate_Dt_FAIn(Fd_FAIn: pd.Series) -> float:
    Dt_FAIn = Fd_FAIn.sum()
    return Dt_FAIn


def calculate_Dt_FAhydrIn(Fd_FAhydrIn: pd.Series) -> float:
    Dt_FAhydrIn = Fd_FAhydrIn.sum()
    return Dt_FAhydrIn


def calculate_Dt_C120In(Fd_C120In: pd.Series) -> float:
    Dt_C120In = Fd_C120In.sum()
    return Dt_C120In


def calculate_Dt_C140In(Fd_C140In: pd.Series) -> float:
    Dt_C140In = Fd_C140In.sum()
    return Dt_C140In


def calculate_Dt_C160In(Fd_C160In: pd.Series) -> float:
    Dt_C160In = Fd_C160In.sum()
    return Dt_C160In


def calculate_Dt_C161In(Fd_C161In: pd.Series) -> float:
    Dt_C161In = Fd_C161In.sum()
    return Dt_C161In


def calculate_Dt_C180In(Fd_C180In: pd.Series) -> float:
    Dt_C180In = Fd_C180In.sum()
    return Dt_C180In


def calculate_Dt_C181tIn(Fd_C181tIn: pd.Series) -> float:
    Dt_C181tIn = Fd_C181tIn.sum()
    return Dt_C181tIn


def calculate_Dt_C181cIn(Fd_C181cIn: pd.Series) -> float:
    Dt_C181cIn = Fd_C181cIn.sum()
    return Dt_C181cIn


def calculate_Dt_C182In(Fd_C182In: pd.Series) -> float:
    Dt_C182In = Fd_C182In.sum()
    return Dt_C182In


def calculate_Dt_C183In(Fd_C183In: pd.Series) -> float:
    Dt_C183In = Fd_C183In.sum()
    return Dt_C183In


def calculate_Dt_OtherFAIn(Fd_OtherFAIn: pd.Series) -> float:
    Dt_OtherFAIn = Fd_OtherFAIn.sum()
    return Dt_OtherFAIn


def calculate_Dt_AshIn(Fd_AshIn: pd.Series) -> float:
    Dt_AshIn = Fd_AshIn.sum()
    return Dt_AshIn


def calculate_Dt_GEIn(Fd_GEIn: pd.Series) -> float:
    Dt_GEIn = Fd_GEIn.sum()
    return Dt_GEIn


def calculate_Dt_DEIn_base(Fd_DEIn_base: pd.Series) -> float:
    Dt_DEIn_base = Fd_DEIn_base.sum()
    return Dt_DEIn_base


def calculate_Dt_DEIn_base_ClfLiq(Fd_DEIn_base_ClfLiq: pd.Series) -> float:
    Dt_DEIn_base_ClfLiq = Fd_DEIn_base_ClfLiq.sum()
    return Dt_DEIn_base_ClfLiq


def calculate_Dt_DEIn_base_ClfDry(Fd_DEIn_base_ClfDry: pd.Series) -> float:
    Dt_DEIn_base_ClfDry = Fd_DEIn_base_ClfDry.sum()
    return Dt_DEIn_base_ClfDry


def calculate_Dt_DigStIn_Base(Fd_DigStIn_Base: pd.Series) -> float:
    Dt_DigStIn_Base = Fd_DigStIn_Base.sum()
    return Dt_DigStIn_Base


def calculate_Dt_DigrOMtIn(Fd_DigrOMtIn: pd.Series) -> float:
    Dt_DigrOMtIn = Fd_DigrOMtIn.sum()
    return Dt_DigrOMtIn


def calculate_Dt_idRUPIn(Fd_idRUPIn: pd.Series) -> float:
    Dt_idRUPIn = Fd_idRUPIn.sum()
    return Dt_idRUPIn


def calculate_Dt_DigFAIn(Fd_DigFAIn: pd.Series) -> float:
    Dt_DigFAIn = Fd_DigFAIn.sum()
    return Dt_DigFAIn


def calculate_Dt_ArgIn(Fd_ArgIn: pd.Series) -> float:
    Dt_ArgIn = Fd_ArgIn.sum()
    return Dt_ArgIn


def calculate_Dt_HisIn(Fd_HisIn: pd.Series) -> float:
    Dt_HisIn = Fd_HisIn.sum()
    return Dt_HisIn


def calculate_Dt_IleIn(Fd_IleIn: pd.Series) -> float:
    Dt_IleIn = Fd_IleIn.sum()
    return Dt_IleIn


def calculate_Dt_LeuIn(Fd_LeuIn: pd.Series) -> float:
    Dt_LeuIn = Fd_LeuIn.sum()
    return Dt_LeuIn


def calculate_Dt_LysIn(Fd_LysIn: pd.Series) -> float:
    Dt_LysIn = Fd_LysIn.sum()
    return Dt_LysIn


def calculate_Dt_MetIn(Fd_MetIn: pd.Series) -> float:
    Dt_MetIn = Fd_MetIn.sum()
    return Dt_MetIn


def calculate_Dt_PheIn(Fd_PheIn: pd.Series) -> float:
    Dt_PheIn = Fd_PheIn.sum()
    return Dt_PheIn


def calculate_Dt_ThrIn(Fd_ThrIn: pd.Series) -> float:
    Dt_ThrIn = Fd_ThrIn.sum()
    return Dt_ThrIn


def calculate_Dt_TrpIn(Fd_TrpIn: pd.Series) -> float:
    Dt_TrpIn = Fd_TrpIn.sum()
    return Dt_TrpIn


def calculate_Dt_ValIn(Fd_ValIn: pd.Series) -> float:
    Dt_ValIn = Fd_ValIn.sum()
    return Dt_ValIn


def calculate_Dt_ArgRUPIn(Fd_ArgRUPIn: pd.Series) -> float:
    Dt_ArgRUPIn = Fd_ArgRUPIn.sum()
    return Dt_ArgRUPIn


def calculate_Dt_HisRUPIn(Fd_HisRUPIn: pd.Series) -> float:
    Dt_HisRUPIn = Fd_HisRUPIn.sum()
    return Dt_HisRUPIn


def calculate_Dt_IleRUPIn(Fd_IleRUPIn: pd.Series) -> float:
    Dt_IleRUPIn = Fd_IleRUPIn.sum()
    return Dt_IleRUPIn


def calculate_Dt_LeuRUPIn(Fd_LeuRUPIn: pd.Series) -> float:
    Dt_LeuRUPIn = Fd_LeuRUPIn.sum()
    return Dt_LeuRUPIn


def calculate_Dt_LysRUPIn(Fd_LysRUPIn: pd.Series) -> float:
    Dt_LysRUPIn = Fd_LysRUPIn.sum()
    return Dt_LysRUPIn


def calculate_Dt_MetRUPIn(Fd_MetRUPIn: pd.Series) -> float:
    Dt_MetRUPIn = Fd_MetRUPIn.sum()
    return Dt_MetRUPIn


def calculate_Dt_PheRUPIn(Fd_PheRUPIn: pd.Series) -> float:
    Dt_PheRUPIn = Fd_PheRUPIn.sum()
    return Dt_PheRUPIn


def calculate_Dt_ThrRUPIn(Fd_ThrRUPIn: pd.Series) -> float:
    Dt_ThrRUPIn = Fd_ThrRUPIn.sum()
    return Dt_ThrRUPIn


def calculate_Dt_TrpRUPIn(Fd_TrpRUPIn: pd.Series) -> float:
    Dt_TrpRUPIn = Fd_TrpRUPIn.sum()
    return Dt_TrpRUPIn


def calculate_Dt_ValRUPIn(Fd_ValRUPIn: pd.Series) -> float:
    Dt_ValRUPIn = Fd_ValRUPIn.sum()
    return Dt_ValRUPIn


def calculate_Dt_RUP(Dt_RUPIn: float, Dt_DMIn: float) -> float:
    Dt_RUP = Dt_RUPIn / Dt_DMIn * 100
    return Dt_RUP


def calculate_Dt_OM(Dt_OMIn: float, Dt_DMIn: float) -> float:
    Dt_OM = Dt_OMIn / Dt_DMIn * 100
    return Dt_OM


def calculate_Dt_NDFnf(Dt_NDFnfIn: float, Dt_DMIn: float) -> float:
    Dt_NDFnf = Dt_NDFnfIn / Dt_DMIn * 100
    return Dt_NDFnf


def calculate_Dt_Lg(Dt_LgIn: float, Dt_DMIn: float) -> float:
    Dt_Lg = Dt_LgIn / Dt_DMIn * 100
    return Dt_Lg


def calculate_Dt_NFC(Dt_NFCIn: float, Dt_DMIn: float) -> float:
    Dt_NFC = Dt_NFCIn / Dt_DMIn * 100
    return Dt_NFC


def calculate_Dt_St(Dt_StIn: float, Dt_DMIn: float) -> float:
    Dt_St = Dt_StIn / Dt_DMIn * 100
    return Dt_St


def calculate_Dt_WSC(Dt_WSCIn: float, Dt_DMIn: float) -> float:
    Dt_WSC = Dt_WSCIn / Dt_DMIn * 100
    return Dt_WSC


def calculate_Dt_rOM(Dt_rOMIn: float, Dt_DMIn: float) -> float:
    Dt_rOM = Dt_rOMIn / Dt_DMIn * 100
    return Dt_rOM


def calculate_Dt_CFat(Dt_CFatIn: float, Dt_DMIn: float) -> float:
    Dt_CFat = Dt_CFatIn / Dt_DMIn * 100
    return Dt_CFat


def calculate_Dt_FA(Dt_FAIn: float, Dt_DMIn: float) -> float:
    Dt_FA = Dt_FAIn / Dt_DMIn * 100
    return Dt_FA


def calculate_Dt_FAhydr(Dt_FAhydrIn: float, Dt_DMIn: float) -> float:
    Dt_FAhydr = Dt_FAhydrIn / Dt_DMIn * 100
    return Dt_FAhydr


def calculate_Dt_CP(Dt_CPIn: float, Dt_DMIn: float) -> float:
    Dt_CP = Dt_CPIn / Dt_DMIn * 100
    return Dt_CP


def calculate_Dt_TP(Dt_TPIn: float, Dt_DMIn: float) -> float:
    Dt_TP = Dt_TPIn / Dt_DMIn * 100
    return Dt_TP


def calculate_Dt_NPNCP(Dt_NPNCPIn: float, Dt_DMIn: float) -> float:
    Dt_NPNCP = Dt_NPNCPIn / Dt_DMIn * 100
    return Dt_NPNCP


def calculate_Dt_NPN(Dt_NPNIn: float, Dt_DMIn: float) -> float:
    Dt_NPN = Dt_NPNIn / Dt_DMIn * 100
    return Dt_NPN


def calculate_Dt_NPNDM(Dt_NPNDMIn: float, Dt_DMIn: float) -> float:
    Dt_NPNDM = Dt_NPNDMIn / Dt_DMIn * 100
    return Dt_NPNDM


def calculate_Dt_CPA(Dt_CPAIn: float, Dt_DMIn: float) -> float:
    Dt_CPA = Dt_CPAIn / Dt_DMIn * 100
    return Dt_CPA


def calculate_Dt_CPB(Dt_CPBIn: float, Dt_DMIn: float) -> float:
    Dt_CPB = Dt_CPBIn / Dt_DMIn * 100
    return Dt_CPB


def calculate_Dt_CPC(Dt_CPCIn: float, Dt_DMIn: float) -> float:
    Dt_CPC = Dt_CPCIn / Dt_DMIn * 100
    return Dt_CPC


def calculate_Dt_Ash(Dt_AshIn: float, Dt_DMIn: float) -> float:
    Dt_Ash = Dt_AshIn / Dt_DMIn * 100
    return Dt_Ash


def calculate_Dt_ForWet(Dt_ForWetIn: float, Dt_DMIn: float) -> float:
    Dt_ForWet = Dt_ForWetIn / Dt_DMIn * 100
    return Dt_ForWet


def calculate_Dt_ForDry(Dt_ForDryIn: float, Dt_DMIn: float) -> float:
    Dt_ForDry = Dt_ForDryIn / Dt_DMIn * 100
    return Dt_ForDry


def calculate_Dt_Conc(Dt_ConcIn: float, Dt_DMIn: float) -> float:
    Dt_Conc = Dt_ConcIn / Dt_DMIn * 100
    return Dt_Conc


def calculate_Dt_C120(Dt_C120In: float, Dt_DMIn: float) -> float:
    Dt_C120 = Dt_C120In / Dt_DMIn * 100
    return Dt_C120


def calculate_Dt_C140(Dt_C140In: float, Dt_DMIn: float) -> float:
    Dt_C140 = Dt_C140In / Dt_DMIn * 100
    return Dt_C140


def calculate_Dt_C160(Dt_C160In: float, Dt_DMIn: float) -> float:
    Dt_C160 = Dt_C160In / Dt_DMIn * 100
    return Dt_C160


def calculate_Dt_C161(Dt_C161In: float, Dt_DMIn: float) -> float:
    Dt_C161 = Dt_C161In / Dt_DMIn * 100
    return Dt_C161


def calculate_Dt_C180(Dt_C180In: float, Dt_DMIn: float) -> float:
    Dt_C180 = Dt_C180In / Dt_DMIn * 100
    return Dt_C180


def calculate_Dt_C181t(Dt_C181tIn: float, Dt_DMIn: float) -> float:
    Dt_C181t = Dt_C181tIn / Dt_DMIn * 100
    return Dt_C181t


def calculate_Dt_C181c(Dt_C181cIn: float, Dt_DMIn: float) -> float:
    Dt_C181c = Dt_C181cIn / Dt_DMIn * 100
    return Dt_C181c


def calculate_Dt_C182(Dt_C182In: float, Dt_DMIn: float) -> float:
    Dt_C182 = Dt_C182In / Dt_DMIn * 100
    return Dt_C182


def calculate_Dt_C183(Dt_C183In: float, Dt_DMIn: float) -> float:
    Dt_C183 = Dt_C183In / Dt_DMIn * 100
    return Dt_C183


def calculate_Dt_OtherFA(Dt_OtherFAIn: float, Dt_DMIn: float) -> float:
    Dt_OtherFA = Dt_OtherFAIn / Dt_DMIn * 100
    return Dt_OtherFA


def calculate_Dt_UFA(Dt_UFAIn: float, Dt_DMIn: float) -> float:
    Dt_UFA = Dt_UFAIn / Dt_DMIn * 100
    return Dt_UFA


def calculate_Dt_MUFA(Dt_MUFAIn: float, Dt_DMIn: float) -> float:
    Dt_MUFA = Dt_MUFAIn / Dt_DMIn * 100
    return Dt_MUFA


def calculate_Dt_PUFA(Dt_PUFAIn: float, Dt_DMIn: float) -> float:
    Dt_PUFA = Dt_PUFAIn / Dt_DMIn * 100
    return Dt_PUFA


def calculate_Dt_SatFA(Dt_SatFAIn: float, Dt_DMIn: float) -> float:
    Dt_SatFA = Dt_SatFAIn / Dt_DMIn * 100
    return Dt_SatFA


def calculate_Dt_C120_FA(Dt_C120In: float, Dt_FAIn: float) -> float:
    Dt_C120_FA = Dt_C120In / Dt_FAIn * 100
    return Dt_C120_FA


def calculate_Dt_C140_FA(Dt_C140In: float, Dt_FAIn: float) -> float:
    Dt_C140_FA = Dt_C140In / Dt_FAIn * 100
    return Dt_C140_FA


def calculate_Dt_C160_FA(Dt_C160In: float, Dt_FAIn: float) -> float:
    Dt_C160_FA = Dt_C160In / Dt_FAIn * 100
    return Dt_C160_FA


def calculate_Dt_C161_FA(Dt_C161In: float, Dt_FAIn: float) -> float:
    Dt_C161_FA = Dt_C161In / Dt_FAIn * 100
    return Dt_C161_FA


def calculate_Dt_C180_FA(Dt_C180In: float, Dt_FAIn: float) -> float:
    Dt_C180_FA = Dt_C180In / Dt_FAIn * 100
    return Dt_C180_FA


def calculate_Dt_C181t_FA(Dt_C181tIn: float, Dt_FAIn: float) -> float:
    Dt_C181t_FA = Dt_C181tIn / Dt_FAIn * 100
    return Dt_C181t_FA


def calculate_Dt_C181c_FA(Dt_C181cIn: float, Dt_FAIn: float) -> float:
    Dt_C181c_FA = Dt_C181cIn / Dt_FAIn * 100
    return Dt_C181c_FA


def calculate_Dt_C182_FA(Dt_C182In: float, Dt_FAIn: float) -> float:
    Dt_C182_FA = Dt_C182In / Dt_FAIn * 100
    return Dt_C182_FA


def calculate_Dt_C183_FA(Dt_C183In: float, Dt_FAIn: float) -> float:
    Dt_C183_FA = Dt_C183In / Dt_FAIn * 100
    return Dt_C183_FA


def calculate_Dt_OtherFA_FA(Dt_OtherFAIn: float, Dt_FAIn: float) -> float:
    Dt_OtherFA_FA = Dt_OtherFAIn / Dt_FAIn * 100
    return Dt_OtherFA_FA


def calculate_Dt_UFA_FA(Dt_UFAIn: float, Dt_FAIn: float) -> float:
    Dt_UFA_FA = Dt_UFAIn / Dt_FAIn * 100
    return Dt_UFA_FA


def calculate_Dt_MUFA_FA(Dt_MUFAIn: float, Dt_FAIn: float) -> float:
    Dt_MUFA_FA = Dt_MUFAIn / Dt_FAIn * 100
    return Dt_MUFA_FA


def calculate_Dt_PUFA_FA(Dt_PUFAIn: float, Dt_FAIn: float) -> float:
    Dt_PUFA_FA = Dt_PUFAIn / Dt_FAIn * 100
    return Dt_PUFA_FA


def calculate_Dt_SatFA_FA(Dt_SatFAIn: float, Dt_FAIn: float) -> float:
    Dt_SatFA_FA = Dt_SatFAIn / Dt_FAIn * 100
    return Dt_SatFA_FA


def calculate_Dt_CaIn(Fd_CaIn: pd.Series) -> float:
    Dt_CaIn = Fd_CaIn.sum()
    return Dt_CaIn


def calculate_Dt_PIn(Fd_PIn: pd.Series) -> float:
    Dt_PIn = Fd_PIn.sum()
    return Dt_PIn


def calculate_Dt_PinorgIn(Fd_PinorgIn: pd.Series) -> float:
    Dt_PinorgIn = Fd_PinorgIn.sum()
    return Dt_PinorgIn


def calculate_Dt_PorgIn(Fd_PorgIn: pd.Series) -> float:
    Dt_PorgIn = Fd_PorgIn.sum()
    return Dt_PorgIn


def calculate_Dt_NaIn(Fd_NaIn: pd.Series) -> float:
    Dt_NaIn = Fd_NaIn.sum()
    return Dt_NaIn


def calculate_Dt_MgIn(Fd_MgIn: pd.Series) -> float:
    Dt_MgIn = Fd_MgIn.sum()
    return Dt_MgIn


def calculate_Dt_MgIn_min(Fd_MgIn_min: pd.Series) -> float:
    Dt_MgIn_min = Fd_MgIn_min.sum()
    return Dt_MgIn_min


def calculate_Dt_KIn(Fd_KIn: pd.Series) -> float:
    Dt_KIn = Fd_KIn.sum()
    return Dt_KIn


def calculate_Dt_ClIn(Fd_ClIn: pd.Series) -> float:
    Dt_ClIn = Fd_ClIn.sum()
    return Dt_ClIn


def calculate_Dt_SIn(Fd_SIn: pd.Series) -> float:
    Dt_SIn = Fd_SIn.sum()
    return Dt_SIn


def calculate_Dt_CoIn(Fd_CoIn: pd.Series) -> float:
    Dt_CoIn = Fd_CoIn.sum()
    return Dt_CoIn


def calculate_Dt_CrIn(Fd_CrIn: pd.Series) -> float:
    Dt_CrIn = Fd_CrIn.sum()
    return Dt_CrIn


def calculate_Dt_CuIn(Fd_CuIn: pd.Series) -> float:
    Dt_CuIn = Fd_CuIn.sum()
    return Dt_CuIn


def calculate_Dt_FeIn(Fd_FeIn: pd.Series) -> float:
    Dt_FeIn = Fd_FeIn.sum()
    return Dt_FeIn


def calculate_Dt_IIn(Fd_IIn: pd.Series) -> float:
    Dt_IIn = Fd_IIn.sum()
    return Dt_IIn


def calculate_Dt_MnIn(Fd_MnIn: pd.Series) -> float:
    Dt_MnIn = Fd_MnIn.sum()
    return Dt_MnIn


def calculate_Dt_MoIn(Fd_MoIn: pd.Series) -> float:
    Dt_MoIn = Fd_MoIn.sum()
    return Dt_MoIn


def calculate_Dt_SeIn(Fd_SeIn: pd.Series) -> float:
    Dt_SeIn = Fd_SeIn.sum()
    return Dt_SeIn


def calculate_Dt_ZnIn(Fd_ZnIn: pd.Series) -> float:
    Dt_ZnIn = Fd_ZnIn.sum()
    return Dt_ZnIn


def calculate_Dt_VitAIn(Fd_VitAIn: pd.Series) -> float:
    Dt_VitAIn = Fd_VitAIn.sum()
    return Dt_VitAIn


def calculate_Dt_VitDIn(Fd_VitDIn: pd.Series) -> float:
    Dt_VitDIn = Fd_VitDIn.sum()
    return Dt_VitDIn


def calculate_Dt_VitEIn(Fd_VitEIn: pd.Series) -> float:
    Dt_VitEIn = Fd_VitEIn.sum()
    return Dt_VitEIn


def calculate_Dt_CholineIn(Fd_CholineIn: pd.Series) -> float:
    Dt_CholineIn = Fd_CholineIn.sum()
    return Dt_CholineIn


def calculate_Dt_BiotinIn(Fd_BiotinIn: pd.Series) -> float:
    Dt_BiotinIn = Fd_BiotinIn.sum()
    return Dt_BiotinIn


def calculate_Dt_NiacinIn(Fd_NiacinIn: pd.Series) -> float:
    Dt_NiacinIn = Fd_NiacinIn.sum()
    return Dt_NiacinIn


def calculate_Dt_B_CaroteneIn(Fd_B_CaroteneIn: pd.Series) -> float:
    Dt_B_CaroteneIn = Fd_B_CaroteneIn.sum()
    return Dt_B_CaroteneIn


def calculate_Dt_Ca(Dt_CaIn: float, Dt_DMIn: float) -> float:
    Dt_Ca = Dt_CaIn / Dt_DMIn / 1000 * 100
    return Dt_Ca


def calculate_Dt_P(Dt_PIn: float, Dt_DMIn: float) -> float:
    Dt_P = Dt_PIn / Dt_DMIn / 1000 * 100
    return Dt_P


def calculate_Dt_Pinorg(Dt_PinorgIn: float, Dt_DMIn: float) -> float:
    Dt_Pinorg = Dt_PinorgIn / Dt_DMIn / 1000 * 100
    return Dt_Pinorg


def calculate_Dt_Porg(Dt_PorgIn: float, Dt_DMIn: float) -> float:
    Dt_Porg = Dt_PorgIn / Dt_DMIn / 1000 * 100
    return Dt_Porg


def calculate_Dt_Na(Dt_NaIn: float, Dt_DMIn: float) -> float:
    Dt_Na = Dt_NaIn / Dt_DMIn / 1000 * 100
    return Dt_Na


def calculate_Dt_Mg(Dt_MgIn: float, Dt_DMIn: float) -> float:
    Dt_Mg = Dt_MgIn / Dt_DMIn / 1000 * 100
    return Dt_Mg


def calculate_Dt_K(Dt_KIn: float, Dt_DMIn: float) -> float:
    Dt_K = Dt_KIn / Dt_DMIn / 1000 * 100
    return Dt_K


def calculate_Dt_Cl(Dt_ClIn: float, Dt_DMIn: float) -> float:
    Dt_Cl = Dt_ClIn / Dt_DMIn / 1000 * 100
    return Dt_Cl


def calculate_Dt_S(Dt_SIn: float, Dt_DMIn: float) -> float:
    Dt_S = Dt_SIn / Dt_DMIn / 1000 * 100
    return Dt_S


def calculate_Dt_Co(Dt_CoIn: float, Dt_DMIn: float) -> float:
    Dt_Co = Dt_CoIn / Dt_DMIn
    return Dt_Co


def calculate_Dt_Cr(Dt_CrIn: float, Dt_DMIn: float) -> float:
    Dt_Cr = Dt_CrIn / Dt_DMIn
    return Dt_Cr


def calculate_Dt_Cu(Dt_CuIn: float, Dt_DMIn: float) -> float:
    Dt_Cu = Dt_CuIn / Dt_DMIn
    return Dt_Cu


def calculate_Dt_Fe(Dt_FeIn: float, Dt_DMIn: float) -> float:
    Dt_Fe = Dt_FeIn / Dt_DMIn
    return Dt_Fe


def calculate_Dt_I(Dt_IIn: float, Dt_DMIn: float) -> float:
    Dt_I = Dt_IIn / Dt_DMIn
    return Dt_I


def calculate_Dt_Mn(Dt_MnIn: float, Dt_DMIn: float) -> float:
    Dt_Mn = Dt_MnIn / Dt_DMIn
    return Dt_Mn


def calculate_Dt_Mo(Dt_MoIn: float, Dt_DMIn: float) -> float:
    Dt_Mo = Dt_MoIn / Dt_DMIn
    return Dt_Mo


def calculate_Dt_Se(Dt_SeIn: float, Dt_DMIn: float) -> float:
    Dt_Se = Dt_SeIn / Dt_DMIn
    return Dt_Se


def calculate_Dt_Zn(Dt_ZnIn: float, Dt_DMIn: float) -> float:
    Dt_Zn = Dt_ZnIn / Dt_DMIn
    return Dt_Zn


def calculate_Dt_VitA(Dt_VitAIn: float, Dt_DMIn: float) -> float:
    Dt_VitA = Dt_VitAIn / Dt_DMIn
    return Dt_VitA


def calculate_Dt_VitD(Dt_VitDIn: float, Dt_DMIn: float) -> float:
    Dt_VitD = Dt_VitDIn / Dt_DMIn
    return Dt_VitD


def calculate_Dt_VitE(Dt_VitEIn: float, Dt_DMIn: float) -> float:
    Dt_VitE = Dt_VitEIn / Dt_DMIn
    return Dt_VitE


def calculate_Dt_Choline(Dt_CholineIn: float, Dt_DMIn: float) -> float:
    Dt_Choline = Dt_CholineIn / Dt_DMIn
    return Dt_Choline


def calculate_Dt_Biotin(Dt_BiotinIn: float, Dt_DMIn: float) -> float:
    Dt_Biotin = Dt_BiotinIn / Dt_DMIn
    return Dt_Biotin


def calculate_Dt_Niacin(Dt_NiacinIn: float, Dt_DMIn: float) -> float:
    Dt_Niacin = Dt_NiacinIn / Dt_DMIn
    return Dt_Niacin


def calculate_Dt_B_Carotene(Dt_B_CaroteneIn: float, Dt_DMIn: float) -> float:
    Dt_B_Carotene = Dt_B_CaroteneIn / Dt_DMIn
    return Dt_B_Carotene


def calculate_Dt_IdArgRUPIn(Fd_IdArgRUPIn: pd.Series) -> float:
    Dt_IdArgRUPIn = Fd_IdArgRUPIn.sum()
    return Dt_IdArgRUPIn


def calculate_Dt_IdHisRUPIn(Fd_IdHisRUPIn: pd.Series) -> float:
    Dt_IdHisRUPIn = Fd_IdHisRUPIn.sum()
    return Dt_IdHisRUPIn


def calculate_Dt_IdIleRUPIn(Fd_IdIleRUPIn: pd.Series) -> float:
    Dt_IdIleRUPIn = Fd_IdIleRUPIn.sum()
    return Dt_IdIleRUPIn


def calculate_Dt_IdLeuRUPIn(Fd_IdLeuRUPIn: pd.Series) -> float:
    Dt_IdLeuRUPIn = Fd_IdLeuRUPIn.sum()
    return Dt_IdLeuRUPIn


def calculate_Dt_IdLysRUPIn(Fd_IdLysRUPIn: pd.Series) -> float:
    Dt_IdLysRUPIn = Fd_IdLysRUPIn.sum()
    return Dt_IdLysRUPIn


def calculate_Dt_IdMetRUPIn(Fd_IdMetRUPIn: pd.Series) -> float:
    Dt_IdMetRUPIn = Fd_IdMetRUPIn.sum()
    return Dt_IdMetRUPIn


def calculate_Dt_IdPheRUPIn(Fd_IdPheRUPIn: pd.Series) -> float:
    Dt_IdPheRUPIn = Fd_IdPheRUPIn.sum()
    return Dt_IdPheRUPIn


def calculate_Dt_IdThrRUPIn(Fd_IdThrRUPIn: pd.Series) -> float:
    Dt_IdThrRUPIn = Fd_IdThrRUPIn.sum()
    return Dt_IdThrRUPIn


def calculate_Dt_IdTrpRUPIn(Fd_IdTrpRUPIn: pd.Series) -> float:
    Dt_IdTrpRUPIn = Fd_IdTrpRUPIn.sum()
    return Dt_IdTrpRUPIn


def calculate_Dt_IdValRUPIn(Fd_IdValRUPIn: pd.Series) -> float:
    Dt_IdValRUPIn = Fd_IdValRUPIn.sum()
    return Dt_IdValRUPIn


def calculate_Dt_DigC120In(Fd_DigC120In: pd.Series) -> float:
    Dt_DigC120In = Fd_DigC120In.sum()
    return Dt_DigC120In


def calculate_Dt_DigC140In(Fd_DigC140In: pd.Series) -> float:
    Dt_DigC140In = Fd_DigC140In.sum()
    return Dt_DigC140In


def calculate_Dt_DigC160In(Fd_DigC160In: pd.Series) -> float:
    Dt_DigC160In = Fd_DigC160In.sum()
    return Dt_DigC160In


def calculate_Dt_DigC161In(Fd_DigC161In: pd.Series) -> float:
    Dt_DigC161In = Fd_DigC161In.sum()
    return Dt_DigC161In


def calculate_Dt_DigC180In(Fd_DigC180In: pd.Series) -> float:
    Dt_DigC180In = Fd_DigC180In.sum()
    return Dt_DigC180In


def calculate_Dt_DigC181tIn(Fd_DigC181tIn: pd.Series) -> float:
    Dt_DigC181tIn = Fd_DigC181tIn.sum()
    return Dt_DigC181tIn


def calculate_Dt_DigC181cIn(Fd_DigC181cIn: pd.Series) -> float:
    Dt_DigC181cIn = Fd_DigC181cIn.sum()
    return Dt_DigC181cIn


def calculate_Dt_DigC182In(Fd_DigC182In: pd.Series) -> float:
    Dt_DigC182In = Fd_DigC182In.sum()
    return Dt_DigC182In


def calculate_Dt_DigC183In(Fd_DigC183In: pd.Series) -> float:
    Dt_DigC183In = Fd_DigC183In.sum()
    return Dt_DigC183In


def calculate_Dt_DigOtherFAIn(Fd_DigOtherFAIn: pd.Series) -> float:
    Dt_DigOtherFAIn = Fd_DigOtherFAIn.sum()
    return Dt_DigOtherFAIn


def calculate_Abs_CaIn(Fd_absCaIn: pd.Series) -> float:
    Abs_CaIn = Fd_absCaIn.sum()
    return Abs_CaIn


def calculate_Abs_PIn(Fd_absPIn: pd.Series) -> float:
    Abs_PIn = Fd_absPIn.sum()
    return Abs_PIn


def calculate_Abs_NaIn(Fd_absNaIn: pd.Series) -> float:
    Abs_NaIn = Fd_absNaIn.sum()
    return Abs_NaIn


def calculate_Abs_KIn(Fd_absKIn: pd.Series) -> float:
    Abs_KIn = Fd_absKIn.sum()
    return Abs_KIn


def calculate_Abs_ClIn(Fd_absClIn: pd.Series) -> float:
    Abs_ClIn = Fd_absClIn.sum()
    return Abs_ClIn


def calculate_Abs_CoIn(Fd_absCoIn: pd.Series) -> float:
    Abs_CoIn = Fd_absCoIn.sum()
    return Abs_CoIn


def calculate_Abs_CuIn(Fd_absCuIn: pd.Series) -> float:
    Abs_CuIn = Fd_absCuIn.sum()
    return Abs_CuIn


def calculate_Abs_FeIn(Fd_absFeIn: pd.Series) -> float:
    Abs_FeIn = Fd_absFeIn.sum()
    return Abs_FeIn


def calculate_Abs_MnIn(Fd_absMnIn: pd.Series) -> float:
    Abs_MnIn = Fd_absMnIn.sum()
    return Abs_MnIn


def calculate_Abs_ZnIn(Fd_absZnIn: pd.Series) -> float:
    Abs_ZnIn = Fd_absZnIn.sum()
    return Abs_ZnIn


def calculate_Dt_DigFA_FA(Dt_DigFAIn: float, Dt_FAIn: float) -> float:
    Dt_DigFA_FA = Dt_DigFAIn / Dt_FAIn * 100
    return Dt_DigFA_FA


def calculate_Dt_DigC120_FA(Dt_DigC120In: float, Dt_FAIn: float) -> float:
    Dt_DigC120_FA = Dt_DigC120In / Dt_FAIn * 100
    return Dt_DigC120_FA


def calculate_Dt_DigC140_FA(Dt_DigC140In: float, Dt_FAIn: float) -> float:
    Dt_DigC140_FA = Dt_DigC140In / Dt_FAIn * 100
    return Dt_DigC140_FA


def calculate_Dt_DigC160_FA(Dt_DigC160In: float, Dt_FAIn: float) -> float:
    Dt_DigC160_FA = Dt_DigC160In / Dt_FAIn * 100
    return Dt_DigC160_FA


def calculate_Dt_DigC161_FA(Dt_DigC161In: float, Dt_FAIn: float) -> float:
    Dt_DigC161_FA = Dt_DigC161In / Dt_FAIn * 100
    return Dt_DigC161_FA


def calculate_Dt_DigC180_FA(Dt_DigC180In: float, Dt_FAIn: float) -> float:
    Dt_DigC180_FA = Dt_DigC180In / Dt_FAIn * 100
    return Dt_DigC180_FA


def calculate_Dt_DigC181t_FA(Dt_DigC181tIn: float, Dt_FAIn: float) -> float:
    Dt_DigC181t_FA = Dt_DigC181tIn / Dt_FAIn * 100
    return Dt_DigC181t_FA


def calculate_Dt_DigC181c_FA(Dt_DigC181cIn: float, Dt_FAIn: float) -> float:
    Dt_DigC181c_FA = Dt_DigC181cIn / Dt_FAIn * 100
    return Dt_DigC181c_FA


def calculate_Dt_DigC182_FA(Dt_DigC182In: float, Dt_FAIn: float) -> float:
    Dt_DigC182_FA = Dt_DigC182In / Dt_FAIn * 100
    return Dt_DigC182_FA


def calculate_Dt_DigC183_FA(Dt_DigC183In: float, Dt_FAIn: float) -> float:
    Dt_DigC183_FA = Dt_DigC183In / Dt_FAIn * 100
    return Dt_DigC183_FA


def calculate_Dt_DigUFA_FA(Dt_DigUFAIn: float, Dt_FAIn: float) -> float:
    Dt_DigUFA_FA = Dt_DigUFAIn / Dt_FAIn * 100
    return Dt_DigUFA_FA


def calculate_Dt_DigMUFA_FA(Dt_DigMUFAIn: float, Dt_FAIn: float) -> float:
    Dt_DigMUFA_FA = Dt_DigMUFAIn / Dt_FAIn * 100
    return Dt_DigMUFA_FA


def calculate_Dt_DigPUFA_FA(Dt_DigPUFAIn: float, Dt_FAIn: float) -> float:
    Dt_DigPUFA_FA = Dt_DigPUFAIn / Dt_FAIn * 100
    return Dt_DigPUFA_FA


def calculate_Dt_DigSatFA_FA(Dt_DigSatFAIn: float, Dt_FAIn: float) -> float:
    Dt_DigSatFA_FA = Dt_DigSatFAIn / Dt_FAIn * 100
    return Dt_DigSatFA_FA


def calculate_Dt_DigOtherFA_FA(Dt_DigOtherFAIn: float, Dt_FAIn: float) -> float:
    Dt_DigOtherFA_FA = Dt_DigOtherFAIn / Dt_FAIn * 100
    return Dt_DigOtherFA_FA


def calculate_DtArgRUP_DtArg(Dt_ArgRUPIn: float, Dt_ArgIn: float) -> float:
    Dt_ArgRUP_DtArg = Dt_ArgRUPIn / Dt_ArgIn
    return Dt_ArgRUP_DtArg


def calculate_DtHisRUP_DtHis(Dt_HisRUPIn: float, Dt_HisIn: float) -> float:
    Dt_HisRUP_DtHis = Dt_HisRUPIn / Dt_HisIn
    return Dt_HisRUP_DtHis


def calculate_DtIleRUP_DtIle(Dt_IleRUPIn: float, Dt_IleIn: float) -> float:
    Dt_IleRUP_DtIle = Dt_IleRUPIn / Dt_IleIn
    return Dt_IleRUP_DtIle


def calculate_DtLeuRUP_DtLeu(Dt_LeuRUPIn: float, Dt_LeuIn: float) -> float:
    Dt_LeuRUP_DtLeu = Dt_LeuRUPIn / Dt_LeuIn
    return Dt_LeuRUP_DtLeu


def calculate_DtLysRUP_DtLys(Dt_LysRUPIn: float, Dt_LysIn: float) -> float:
    Dt_LysRUP_DtLys = Dt_LysRUPIn / Dt_LysIn
    return Dt_LysRUP_DtLys


def calculate_DtMetRUP_DtMet(Dt_MetRUPIn: float, Dt_MetIn: float) -> float:
    Dt_MetRUP_DtMet = Dt_MetRUPIn / Dt_MetIn
    return Dt_MetRUP_DtMet


def calculate_DtPheRUP_DtPhe(Dt_PheRUPIn: float, Dt_PheIn: float) -> float:
    Dt_PheRUP_DtPhe = Dt_PheRUPIn / Dt_PheIn
    return Dt_PheRUP_DtPhe


def calculate_DtThrRUP_DtThr(Dt_ThrRUPIn: float, Dt_ThrIn: float) -> float:
    Dt_ThrRUP_DtThr = Dt_ThrRUPIn / Dt_ThrIn
    return Dt_ThrRUP_DtThr


def calculate_DtTrpRUP_DtTrp(Dt_TrpRUPIn: float, Dt_TrpIn: float) -> float:
    Dt_TrpRUP_DtTrp = Dt_TrpRUPIn / Dt_TrpIn
    return Dt_TrpRUP_DtTrp


def calculate_DtValRUP_DtVal(Dt_ValRUPIn: float, Dt_ValIn: float) -> float:
    Dt_ValRUP_DtVal = Dt_ValRUPIn / Dt_ValIn
    return Dt_ValRUP_DtVal


def calculate_Dt_IdArgIn(Du_IdAAMic_Arg: float, Dt_IdArgRUPIn: float) -> float:
    Dt_IdArgIn = Du_IdAAMic_Arg + Dt_IdArgRUPIn
    return Dt_IdArgIn


def calculate_Dt_IdHisIn(Du_IdAAMic_His: float, Dt_IdHisRUPIn: float) -> float:
    Dt_IdHisIn = Du_IdAAMic_His + Dt_IdHisRUPIn
    return Dt_IdHisIn


def calculate_Dt_IdIleIn(Du_IdAAMic_Ile: float, Dt_IdIleRUPIn: float) -> float:
    Dt_IdIleIn = Du_IdAAMic_Ile + Dt_IdIleRUPIn
    return Dt_IdIleIn


def calculate_Dt_IdLeuIn(Du_IdAAMic_Leu: float, Dt_IdLeuRUPIn: float) -> float:
    Dt_IdLeuIn = Du_IdAAMic_Leu + Dt_IdLeuRUPIn
    return Dt_IdLeuIn


def calculate_Dt_IdLysIn(Du_IdAAMic_Lys: float, Dt_IdLysRUPIn: float) -> float:
    Dt_IdLysIn = Du_IdAAMic_Lys + Dt_IdLysRUPIn
    return Dt_IdLysIn


def calculate_Dt_IdMetIn(Du_IdAAMic_Met: float, Dt_IdMetRUPIn: float) -> float:
    Dt_IdMetIn = Du_IdAAMic_Met + Dt_IdMetRUPIn
    return Dt_IdMetIn


def calculate_Dt_IdPheIn(Du_IdAAMic_Phe: float, Dt_IdPheRUPIn: float) -> float:
    Dt_IdPheIn = Du_IdAAMic_Phe + Dt_IdPheRUPIn
    return Dt_IdPheIn


def calculate_Dt_IdThrIn(Du_IdAAMic_Thr: float, Dt_IdThrRUPIn: float) -> float:
    Dt_IdThrIn = Du_IdAAMic_Thr + Dt_IdThrRUPIn
    return Dt_IdThrIn


def calculate_Dt_IdTrpIn(Du_IdAAMic_Trp: float, Dt_IdTrpRUPIn: float) -> float:
    Dt_IdTrpIn = Du_IdAAMic_Trp + Dt_IdTrpRUPIn
    return Dt_IdTrpIn


def calculate_Dt_IdValIn(Du_IdAAMic_Val: float, Dt_IdValRUPIn: float) -> float:
    Dt_IdValIn = Du_IdAAMic_Val + Dt_IdValRUPIn
    return Dt_IdValIn


####################
# Functions for Digestability Coefficients
####################
def calculate_TT_dcNDF_Base(Dt_DigNDFIn_Base: float, Dt_NDFIn: float) -> float:
    TT_dcNDF_Base = Dt_DigNDFIn_Base / Dt_NDFIn * 100  # Line 1056
    if math.isnan(TT_dcNDF_Base):
        TT_dcNDF_Base = 0.0
    return TT_dcNDF_Base


def calculate_TT_dcNDF(
    TT_dcNDF_Base: float, 
    Dt_StIn: float, 
    Dt_DMIn: float, 
    An_DMIn_BW: float
) -> float:
    if TT_dcNDF_Base == 0: 
        TT_dcNDF = 0.0
    else:
        TT_dcNDF = (TT_dcNDF_Base / 100 - 
                    0.59 * (Dt_StIn / Dt_DMIn - 0.26) - 
                    1.1 * (An_DMIn_BW - 0.035)) * 100
    return TT_dcNDF


def calculate_TT_dcSt_Base(Dt_DigStIn_Base: float, Dt_StIn: float) -> float:
    TT_dcSt_Base = Dt_DigStIn_Base / Dt_StIn * 100  # Line 1030
    if math.isnan(TT_dcSt_Base):
        TT_dcSt_Base = 0.0
    return TT_dcSt_Base


def calculate_TT_dcSt(TT_dcSt_Base: float, An_DMIn_BW: float) -> float:
    TT_dcSt = (0.0
               if TT_dcSt_Base == 0 
               else TT_dcSt_Base - (1.0 * (An_DMIn_BW - 0.035)) * 100)
    return TT_dcSt


def calculate_TT_dcAnSt(
    An_DigStIn: float, 
    Dt_StIn: float,
    Inf_StIn: float
) -> float:
    """
    TT_dcAnSt: Starch total tract digestability coefficient
    """
    TT_dcAnSt = An_DigStIn / (Dt_StIn + Inf_StIn) * 100  # Line 1034
    if np.isnan(TT_dcAnSt):  # Line 1035
        TT_dcAnSt = 0.0
    return TT_dcAnSt


def calculate_TT_dcrOMa(
    An_DigrOMaIn: float, 
    Dt_rOMIn: float,
    InfRum_GlcIn: float, 
    InfRum_AcetIn: float,
    InfRum_PropIn: float, 
    InfRum_ButrIn: float,
    InfSI_GlcIn: float, 
    InfSI_AcetIn: float,
    InfSI_PropIn: float, 
    InfSI_ButrIn: float
) -> float:
    """
    TT_dcrOMa: Apparent digested residual organic matter total tract digestability coefficient
    """
    TT_dcrOMa = An_DigrOMaIn / (Dt_rOMIn + InfRum_GlcIn + InfRum_AcetIn +
                                InfRum_PropIn + InfRum_ButrIn + InfSI_GlcIn +
                                InfSI_AcetIn + InfSI_PropIn +
                                InfSI_ButrIn) * 100  # Line 1047-1048
    return TT_dcrOMa


def calculate_TT_dcrOMt(
    An_DigrOMtIn: float, 
    Dt_rOMIn: float,
    InfRum_GlcIn: float, 
    InfRum_AcetIn: float,
    InfRum_PropIn: float, 
    InfRum_ButrIn: float,
    InfSI_GlcIn: float, 
    InfSI_AcetIn: float,
    InfSI_PropIn: float, 
    InfSI_ButrIn: float
) -> float:
    """
    TT_dcrOMt: Truly digested residual organic matter total tract digestability coefficient
    """
    TT_dcrOMt = An_DigrOMtIn / (Dt_rOMIn + InfRum_GlcIn + InfRum_AcetIn +
                                InfRum_PropIn + InfRum_ButrIn + InfSI_GlcIn +
                                InfSI_AcetIn + InfSI_PropIn +
                                InfSI_ButrIn) * 100  # Line 1049-1050
    return TT_dcrOMt


def calculate_Dt_DigCPtIn(
    An_StatePhys: str, 
    Dt_DigCPaIn: float,
    Fe_CPend: float, 
    Dt_RDPIn: float,
    Dt_idRUPIn: float
) -> float:
    """
    Dt_DigCPtIn: True total tract digested CP, kg/d
    """
    if An_StatePhys == "Calf":
        Dt_DigCPtIn = Dt_DigCPaIn + Fe_CPend  # Line 1210
    else:
        Dt_DigCPtIn = Dt_RDPIn + Dt_idRUPIn
        # kg CP/d, true total tract digested CP, Line 1209
    return Dt_DigCPtIn


def calculate_Dt_DigTPaIn(
    Dt_RDTPIn: float, 
    Fe_MiTP: float, 
    Dt_idRUPIn: float,
    Fe_NPend: float
) -> float:
    """
    Dt_DigTPaIn: Apparent total tract digested true protein, kg/d 
    """
    Dt_DigTPaIn = Dt_RDTPIn - Fe_MiTP + Dt_idRUPIn - Fe_NPend  
    # Doesn't apply to calves, Line 1211
    return Dt_DigTPaIn


def calculate_Dt_DigTPtIn(Dt_RDTPIn: float, Dt_idRUPIn: float) -> float:
    """
    Dt_DigTPtIn: True total tract digested true protein, kg/d
    """
    Dt_DigTPtIn = Dt_RDTPIn + Dt_idRUPIn  # Line 1212
    return Dt_DigTPtIn


def calculate_Dt_DigCPa(Dt_DigCPaIn: float, Dt_DMIn: float) -> float:
    """
    Dt_DigCPa: Dietary apparent total tract CP as % of DM
    """
    Dt_DigCPa = Dt_DigCPaIn / Dt_DMIn * 100  
    # Dietary Apparrent total tract % of DM, Line 1213
    return Dt_DigCPa


def calculate_TT_dcDtCPa(Dt_DigCPaIn: float, Dt_CPIn: float) -> float:
    """
    TT_dcDtCPa: Digestability coefficient apparent total tract CP, % CP
    """
    TT_dcDtCPa = Dt_DigCPaIn / Dt_CPIn * 100  # % of CP, Line 1214
    return TT_dcDtCPa


def calculate_Dt_DigCPt(Dt_DigCPtIn: float, Dt_DMIn: float) -> float:
    """
    Dt_DigCPt: Dietary true total tract digested CP, % DM    
    """
    Dt_DigCPt = Dt_DigCPtIn / Dt_DMIn * 100  
    # Dietary True total tract % of DM, Line 1215
    return Dt_DigCPt


def calculate_Dt_DigTPt(Dt_DigTPtIn: float, Dt_DMIn: float) -> float:
    """
    Dt_DigTPt: Dietary true total tract digested true protein, % DM
    """
    Dt_DigTPt = Dt_DigTPtIn / Dt_DMIn * 100  
    # True total tract % of DM, Line 1216
    return Dt_DigTPt


def calculate_TT_dcDtCPt(Dt_DigCPtIn: float, Dt_CPIn: float) -> float:
    """
    TT_dcDtCPt: Digestability coefficient true total tract CP, % CP
    """
    TT_dcDtCPt = Dt_DigCPtIn / Dt_CPIn * 100  # % of CP, Line 1217
    return TT_dcDtCPt


def calculate_Dt_MPIn(
    An_StatePhys: str, 
    Dt_CPIn: float, 
    Fe_CP: float,
    Fe_CPend: float, 
    Dt_idRUPIn: float,
    Du_idMiTP: float
) -> float:
    """
    Dt_MPIn: Dietary metabolizable protein intake, kg/d
    """
    if An_StatePhys == "Calf":
        Dt_MPIn = Dt_CPIn - Fe_CP + Fe_CPend  
        # ignores all ruminal activity, Line 1219
    else:
        Dt_MPIn = Dt_idRUPIn + Du_idMiTP  # Line 1218
    return Dt_MPIn


def calculate_Dt_MP(Dt_MPIn: float, Dt_DMIn: float) -> float:
    """
    Dt_MP: Dietary metabolizable protein, % DM 
    """
    Dt_MP = Dt_MPIn / Dt_DMIn * 100  # % of DM, Line 1220
    return Dt_MP


def calculate_Dt_DigUFAIn(
    Dt_DigC161In: float, 
    Dt_DigC181tIn: float,
    Dt_DigC181cIn: float, 
    Dt_DigC182In: float,
    Dt_DigC183In: float
) -> float:
    """
    Dt_DigUFAIn: Dietary digestable unsaturated FA intake, kg/d 
    """
    Dt_DigUFAIn = (Dt_DigC161In + Dt_DigC181tIn + Dt_DigC181cIn + 
                   Dt_DigC182In + Dt_DigC183In)  # Line 1282
    return Dt_DigUFAIn


def calculate_Dt_DigMUFAIn(
    Dt_DigC161In: float, 
    Dt_DigC181tIn: float,
    Dt_DigC181cIn: float
) -> float:
    """
    Dt_DigMUFAIn: Dietary digestable monounsaturated fatty acid intake, kg/d
    """
    Dt_DigMUFAIn = Dt_DigC161In + Dt_DigC181tIn + Dt_DigC181cIn  # Line 1283
    return Dt_DigMUFAIn


def calculate_Dt_DigPUFAIn(Dt_DigC182In: float, Dt_DigC183In: float) -> float:
    """
    Dt_DigPUFAIn: Dietary digestable polyunsaturated fatty acid intake, kg/d 
    """
    Dt_DigPUFAIn = Dt_DigC182In + Dt_DigC183In  # Line 1284
    return Dt_DigPUFAIn


def calculate_Dt_DigSatFAIn(Dt_DigFAIn: float, Dt_DigUFAIn: float) -> float:
    """
    Dt_DigSatFAIn: Dietary digestable saturated fatty acid intake, kg/d
    """
    Dt_DigSatFAIn = Dt_DigFAIn - Dt_DigUFAIn  # Line 1285
    return Dt_DigSatFAIn


def calculate_Dt_DigFA(Dt_DigFAIn: float, Dt_DMIn: float) -> float:
    """
    Dt_DigFA: Dietary digested FA, % of DMI
    """
    Dt_DigFA = Dt_DigFAIn / Dt_DMIn * 100  # Line 1313
    return Dt_DigFA


def calculate_Dt_DigOMaIn(
    Dt_DigNDFIn: float, 
    Dt_DigStIn: float,
    Dt_DigFAIn: float, 
    Dt_DigrOMaIn: float,
    Dt_DigCPaIn: float
) -> float:
    """
    Dt_DigOMaIn: Apparent digested organic matter intake (kg/d)
    """
    Dt_DigOMaIn = (Dt_DigNDFIn + Dt_DigStIn + Dt_DigFAIn + 
                   Dt_DigrOMaIn + Dt_DigCPaIn)  # Line 1320
    return Dt_DigOMaIn


def calculate_Dt_DigOMtIn(
    Dt_DigNDFIn: float, 
    Dt_DigStIn: float,
    Dt_DigFAIn: float, 
    Dt_DigrOMtIn: float,
    Dt_DigCPtIn: float
) -> float:
    """
    Dt_DigOMtIn: True digested organic matter intake (kg/d)
    """
    Dt_DigOMtIn = (Dt_DigNDFIn + Dt_DigStIn + Dt_DigFAIn + 
                   Dt_DigrOMtIn + Dt_DigCPtIn)  # Line 1321
    return Dt_DigOMtIn


def calculate_Dt_DigOMa(Dt_DigOMaIn: float, Dt_DMIn: float) -> float:
    """
    Dt_DigOMa: Apparent digested dietary organic matter, % DMI
    """
    Dt_DigOMa = Dt_DigOMaIn / Dt_DMIn * 100  # Line 1327
    return Dt_DigOMa


def calculate_Dt_DigOMt(Dt_DigOMtIn: float, Dt_DMIn: float) -> float:
    """
    Dt_DigOMt: True digested dietary organic matter, % DMI
    """
    Dt_DigOMt = Dt_DigOMtIn / Dt_DMIn * 100  # Line 1328
    return Dt_DigOMt


def calculate_TT_dcDtFA(Dt_DigFAIn: float, Dt_FAIn: float) -> float:
    """
    TT_dcDtFA: Digestability coefficient for total tract dietary FA 
    """
    TT_dcDtFA = Dt_DigFAIn / Dt_FAIn * 100  # Line 1311
    return TT_dcDtFA


def calculate_Dt_IdAARUPIn_array(diet_data: dict, aa_list: list) -> pd.Series:
    Dt_IdAARUPIn = pd.Series([diet_data[f"Dt_Id{aa}RUPIn"] for aa in aa_list],
                             index=aa_list)
    return Dt_IdAARUPIn


def calculate_Fd_DMInp(kg_user: pd.Series) -> pd.Series:
    Fd_DMInp = kg_user / kg_user.sum()
    return Fd_DMInp


def calculate_Trg_Fd_DMIn(Fd_DMInp: pd.Series, Trg_Dt_DMIn: float) -> pd.Series:
    Trg_Fd_DMIn = Fd_DMInp * Trg_Dt_DMIn
    return Trg_Fd_DMIn


####################
# Wrapper functions for feed and diet intakes
####################
def calculate_feed_data(
    Dt_DMIn: float, 
    An_StatePhys: str, 
    Use_DNDF_IV: int, 
    feed_data: pd.DataFrame, 
    coeff_dict: dict
) -> pd.DataFrame:
    # Start with copy of feed_data
    complete_feed_data = feed_data.copy()
    new_columns = {}

    # Calculate all aditional feed data columns
    complete_feed_data['Fd_DMIn'] = calculate_Fd_DMIn(
        Dt_DMIn, complete_feed_data['Fd_DMInp']
        )
    new_columns['Fd_GE'] = calculate_Fd_GE(
        An_StatePhys, complete_feed_data['Fd_Category'], 
        complete_feed_data['Fd_CP'], complete_feed_data['Fd_FA'], 
        complete_feed_data['Fd_Ash'], complete_feed_data['Fd_St'],
        complete_feed_data['Fd_NDF'], coeff_dict
        )
    new_columns['Fd_AFIn'] = calculate_Fd_AFIn(
        complete_feed_data['Fd_DM'], complete_feed_data['Fd_DMIn']
        )
    new_columns['Fd_For'] = calculate_Fd_For(complete_feed_data['Fd_Conc'])
    new_columns['Fd_ForWet'] = calculate_Fd_ForWet(
        complete_feed_data['Fd_DM'], new_columns['Fd_For']
        )
    new_columns['Fd_ForDry'] = calculate_Fd_ForDry(
        complete_feed_data['Fd_DM'], new_columns['Fd_For']
        )
    new_columns['Fd_Past'] = calculate_Fd_Past(
        complete_feed_data['Fd_Category']
        )
    new_columns['Fd_LiqClf'] = calculate_Fd_LiqClf(
        complete_feed_data['Fd_Category']
        )
    new_columns['Fd_NDFnf'] = calculate_Fd_NDFnf(
        complete_feed_data['Fd_NDF'], complete_feed_data['Fd_NDFIP']
        )
    new_columns['Fd_NPNCP'] = calculate_Fd_NPNCP(
        complete_feed_data['Fd_CP'], complete_feed_data['Fd_NPN_CP']
        )
    new_columns['Fd_NPN'] = calculate_Fd_NPN(
        new_columns['Fd_NPNCP']
        )
    new_columns['Fd_NPNDM'] = calculate_Fd_NPNDM(
        new_columns['Fd_NPNCP']
        )
    new_columns['Fd_TP'] = calculate_Fd_TP(
        complete_feed_data['Fd_CP'], new_columns['Fd_NPNCP']
        )
    new_columns['Fd_fHydr_FA'] = calculate_Fd_fHydr_FA(
        complete_feed_data['Fd_Category']
        )
    new_columns['Fd_FAhydr'] = calculate_Fd_FAhydr(
        complete_feed_data['Fd_FA'], new_columns['Fd_fHydr_FA']
        )
    new_columns['Fd_NFC'] = calculate_Fd_NFC(
        complete_feed_data['Fd_NDF'], new_columns['Fd_TP'], 
        complete_feed_data['Fd_Ash'], new_columns['Fd_FAhydr'], 
        new_columns['Fd_NPNDM']
        )
    new_columns['Fd_rOM'] = calculate_Fd_rOM(
        complete_feed_data['Fd_NDF'], complete_feed_data['Fd_St'], 
        new_columns['Fd_TP'], complete_feed_data['Fd_FA'], 
        new_columns['Fd_fHydr_FA'], complete_feed_data['Fd_Ash'], 
        new_columns['Fd_NPNDM']
        )
    new_columns['Fd_GEIn'] = calculate_Fd_GEIn(
        new_columns['Fd_GE'], complete_feed_data['Fd_DMIn']
        )
    new_columns["Fd_ADFIn"] = calculate_Fd_ADFIn(
        complete_feed_data["Fd_ADF"], complete_feed_data['Fd_DMIn']
        )
    new_columns["Fd_NDFIn"] = calculate_Fd_NDFIn(
        complete_feed_data["Fd_NDF"], complete_feed_data['Fd_DMIn']
        )
    new_columns["Fd_StIn"] = calculate_Fd_StIn(
        complete_feed_data["Fd_St"], complete_feed_data['Fd_DMIn']
        )
    new_columns["Fd_NFCIn"] = calculate_Fd_NFCIn(
        new_columns["Fd_NFC"], complete_feed_data['Fd_DMIn']
        )
    new_columns["Fd_WSCIn"] = calculate_Fd_WSCIn(
        complete_feed_data["Fd_WSC"], complete_feed_data['Fd_DMIn']
        )
    new_columns["Fd_rOMIn"] = calculate_Fd_rOMIn(
        new_columns["Fd_rOM"], complete_feed_data['Fd_DMIn']
        )
    new_columns["Fd_LgIn"] = calculate_Fd_LgIn(
        complete_feed_data["Fd_Lg"], complete_feed_data['Fd_DMIn']
        )
    new_columns["Fd_ConcIn"] = calculate_Fd_ConcIn(
        complete_feed_data["Fd_Conc"], complete_feed_data['Fd_DMIn']
        )
    new_columns["Fd_ForIn"] = calculate_Fd_ForIn(
        new_columns["Fd_For"], complete_feed_data['Fd_DMIn']
        )
    new_columns["Fd_ForNDFIn"] = calculate_Fd_ForNDFIn(
        complete_feed_data["Fd_ForNDF"], complete_feed_data['Fd_DMIn']
        )
    new_columns["Fd_ForWetIn"] = calculate_Fd_ForWetIn(
        new_columns["Fd_ForWet"], complete_feed_data['Fd_DMIn']
        )
    new_columns["Fd_ForDryIn"] = calculate_Fd_ForDryIn(
        new_columns["Fd_ForDry"], complete_feed_data['Fd_DMIn']
        )
    new_columns["Fd_PastIn"] = calculate_Fd_PastIn(
        new_columns["Fd_Past"], complete_feed_data['Fd_DMIn']
        )
    new_columns["Fd_CPIn"] = calculate_Fd_CPIn(
        complete_feed_data["Fd_CP"], complete_feed_data['Fd_DMIn']
        )
    new_columns["Fd_TPIn"] = calculate_Fd_TPIn(
        new_columns["Fd_TP"], complete_feed_data['Fd_DMIn']
        )
    new_columns["Fd_CFatIn"] = calculate_Fd_CFatIn(
        complete_feed_data["Fd_CFat"], complete_feed_data['Fd_DMIn']
        )
    new_columns["Fd_FAIn"] = calculate_Fd_FAIn(
        complete_feed_data["Fd_FA"], complete_feed_data['Fd_DMIn']
        )
    new_columns["Fd_FAhydrIn"] = calculate_Fd_FAhydrIn(
        new_columns["Fd_FAhydr"], complete_feed_data['Fd_DMIn']
        )
    new_columns["Fd_AshIn"] = calculate_Fd_AshIn(
        complete_feed_data["Fd_Ash"], complete_feed_data['Fd_DMIn']
        )
    # Calculate nutrient intakes for each feed
    new_columns['TT_dcFdNDF_Lg'] = calculate_TT_dcFdNDF_Lg(
        complete_feed_data['Fd_NDF'], complete_feed_data['Fd_Lg']
        )
    new_columns['Fd_DNDF48'] = calculate_Fd_DNDF48(
        complete_feed_data['Fd_Conc'], complete_feed_data['Fd_DNDF48_input']
        )
    new_columns['TT_dcFdNDF_48h'] = calculate_TT_dcFdNDF_48h(
        new_columns['Fd_DNDF48']
        )
    new_columns['TT_dcFdNDF_Base'] = calculate_TT_dcFdNDF_Base(
        Use_DNDF_IV, complete_feed_data['Fd_Conc'], 
        new_columns['TT_dcFdNDF_Lg'], new_columns['TT_dcFdNDF_48h']
        )
    new_columns['Fd_DigNDFIn_Base'] = calculate_Fd_DigNDFIn_Base(
        new_columns['Fd_NDFIn'], new_columns['TT_dcFdNDF_Base']
        )
    new_columns['Fd_NPNCPIn'] = calculate_Fd_NPNCPIn(
        new_columns['Fd_CPIn'], complete_feed_data['Fd_NPN_CP']
        )
    new_columns['Fd_NPNIn'] = calculate_Fd_NPNIn(
        new_columns['Fd_NPNCPIn']
        )
    new_columns['Fd_NPNDMIn'] = calculate_Fd_NPNDMIn(
        new_columns['Fd_NPNCPIn']
        )
    new_columns['Fd_CPAIn'] = calculate_Fd_CPAIn(
        new_columns['Fd_CPIn'], complete_feed_data['Fd_CPARU']
        )
    new_columns['Fd_CPBIn'] = calculate_Fd_CPBIn(
        new_columns['Fd_CPIn'], complete_feed_data['Fd_CPBRU']
        )
    new_columns['Fd_CPBIn_For'] = calculate_Fd_CPBIn_For(
        new_columns['Fd_CPIn'], complete_feed_data['Fd_CPBRU'],
        new_columns['Fd_For']
        )
    new_columns['Fd_CPBIn_Conc'] = calculate_Fd_CPBIn_Conc(
        new_columns['Fd_CPIn'], complete_feed_data['Fd_CPBRU'],
        complete_feed_data['Fd_Conc']
        )
    new_columns['Fd_CPCIn'] = calculate_Fd_CPCIn(
        new_columns['Fd_CPIn'], complete_feed_data['Fd_CPCRU']
        )
    new_columns['Fd_CPIn_ClfLiq'] = calculate_Fd_CPIn_ClfLiq(
        complete_feed_data['Fd_Category'], complete_feed_data['Fd_DMIn'],
        complete_feed_data['Fd_CP']
        )
    new_columns['Fd_CPIn_ClfDry'] = calculate_Fd_CPIn_ClfDry(
        complete_feed_data['Fd_Category'], complete_feed_data['Fd_DMIn'],
        complete_feed_data['Fd_CP']
        )
    new_columns['Fd_OMIn'] = calculate_Fd_OMIn(
        complete_feed_data['Fd_DMIn'], new_columns['Fd_AshIn']
        )
    # Rumen Degraded and Undegraded Protein
    new_columns['Fd_rdcRUPB'] = calculate_Fd_rdcRUPB(
        new_columns['Fd_For'], complete_feed_data['Fd_Conc'],
        complete_feed_data['Fd_KdRUP'], coeff_dict
        )
    new_columns['Fd_RUPBIn'] = calculate_Fd_RUPBIn(
        new_columns['Fd_For'], complete_feed_data['Fd_Conc'],
        complete_feed_data['Fd_KdRUP'], new_columns['Fd_CPBIn'],
        coeff_dict
        )
    new_columns['Fd_RUPIn'] = calculate_Fd_RUPIn(
        new_columns['Fd_CPIn'], new_columns['Fd_CPAIn'],
        new_columns['Fd_CPCIn'], new_columns['Fd_NPNCPIn'],
        new_columns['Fd_RUPBIn'], coeff_dict
        )
    new_columns['Fd_RUP_CP'] = calculate_Fd_RUP_CP(
        new_columns['Fd_CPIn'], new_columns['Fd_RUPIn']
        )
    new_columns['Fd_RUP'] = calculate_Fd_RUP(
        new_columns['Fd_CPIn'], new_columns['Fd_RUPIn'],
        complete_feed_data['Fd_DMIn']
        )
    new_columns['Fd_RDP'] = calculate_Fd_RDP(
        new_columns['Fd_CPIn'], complete_feed_data['Fd_CP'],
        new_columns['Fd_RUP']
        )
    # FA Intakes
    new_columns["Fd_C120In"] = calculate_Fd_C120In(
        complete_feed_data["Fd_C120_FA"], complete_feed_data["Fd_FA"], 
        complete_feed_data['Fd_DMIn']
        )
    new_columns["Fd_C140In"] = calculate_Fd_C140In(
        complete_feed_data["Fd_C140_FA"], complete_feed_data["Fd_FA"], 
        complete_feed_data['Fd_DMIn']
        )
    new_columns["Fd_C160In"] = calculate_Fd_C160In(
        complete_feed_data["Fd_C160_FA"], complete_feed_data["Fd_FA"], 
        complete_feed_data['Fd_DMIn']
        )
    new_columns["Fd_C161In"] = calculate_Fd_C161In(
        complete_feed_data["Fd_C161_FA"], complete_feed_data["Fd_FA"], 
        complete_feed_data['Fd_DMIn']
        )
    new_columns["Fd_C180In"] = calculate_Fd_C180In(
        complete_feed_data["Fd_C180_FA"], complete_feed_data["Fd_FA"], 
        complete_feed_data['Fd_DMIn']
        )
    new_columns["Fd_C181tIn"] = calculate_Fd_C181tIn(
        complete_feed_data["Fd_C181t_FA"], complete_feed_data["Fd_FA"], 
        complete_feed_data['Fd_DMIn']
        )
    new_columns["Fd_C181cIn"] = calculate_Fd_C181cIn(
        complete_feed_data["Fd_C181c_FA"], complete_feed_data["Fd_FA"], 
        complete_feed_data['Fd_DMIn']
        )
    new_columns["Fd_C182In"] = calculate_Fd_C182In(
        complete_feed_data["Fd_C182_FA"], complete_feed_data["Fd_FA"], 
        complete_feed_data['Fd_DMIn']
        )
    new_columns["Fd_C183In"] = calculate_Fd_C183In(
        complete_feed_data["Fd_C183_FA"], complete_feed_data["Fd_FA"], 
        complete_feed_data['Fd_DMIn']
        )
    new_columns["Fd_OtherFAIn"] = calculate_Fd_OtherFAIn(
        complete_feed_data["Fd_OtherFA_FA"], complete_feed_data["Fd_FA"], 
        complete_feed_data['Fd_DMIn']
        )
    new_columns['Fd_DE_base_1'] = calculate_Fd_DE_base_1(
        complete_feed_data['Fd_NDF'], complete_feed_data['Fd_Lg'], 
        complete_feed_data['Fd_St'], complete_feed_data['Fd_dcSt'], 
        complete_feed_data['Fd_FA'], complete_feed_data['Fd_dcFA'],
        complete_feed_data['Fd_Ash'], complete_feed_data['Fd_CP'], 
        new_columns['Fd_NPNCP'], new_columns['Fd_RUP'], 
        complete_feed_data['Fd_dcRUP']
        )
    new_columns['Fd_DE_base_2'] = calculate_Fd_DE_base_2(
        complete_feed_data['Fd_NDF'], complete_feed_data['Fd_St'], 
        complete_feed_data['Fd_dcSt'], complete_feed_data['Fd_FA'], 
        complete_feed_data['Fd_dcFA'], complete_feed_data['Fd_Ash'],
        complete_feed_data['Fd_CP'], new_columns['Fd_NPNCP'],
        new_columns['Fd_RUP'], complete_feed_data['Fd_dcRUP'],
        complete_feed_data['Fd_DNDF48_NDF']
        )
    new_columns['Fd_DE_base'] = calculate_Fd_DE_base(
        Use_DNDF_IV, new_columns['Fd_DE_base_1'],
        new_columns['Fd_DE_base_2'], new_columns['Fd_For'],
        complete_feed_data['Fd_FA'], new_columns['Fd_RDP'],
        new_columns['Fd_RUP'], complete_feed_data['Fd_dcRUP'], 
        complete_feed_data['Fd_CP'], complete_feed_data['Fd_Ash'], 
        complete_feed_data['Fd_dcFA'], new_columns['Fd_NPN'],
        complete_feed_data['Fd_Category']
        )
    new_columns['Fd_DEIn_base'] = calculate_Fd_DEIn_base(
        new_columns['Fd_DE_base'], complete_feed_data['Fd_DMIn']
        )
    new_columns['Fd_DEIn_base_ClfLiq'] = calculate_Fd_DEIn_base_ClfLiq(
        complete_feed_data['Fd_Category'], new_columns['Fd_DEIn_base']
        )
    new_columns['Fd_DEIn_base_ClfDry'] = calculate_Fd_DEIn_base_ClfDry(
        complete_feed_data['Fd_Category'], new_columns['Fd_DEIn_base']
        )
    new_columns['Fd_DMIn_ClfLiq'] = calculate_Fd_DMIn_ClfLiq(
        An_StatePhys, complete_feed_data['Fd_DMIn'], 
        complete_feed_data['Fd_Category']
        )
    new_columns['Fd_DE_ClfLiq'] = calculate_Fd_DE_ClfLiq(
        An_StatePhys, complete_feed_data['Fd_Category'], new_columns['Fd_GE']
        )
    new_columns['Fd_ME_ClfLiq'] = calculate_Fd_ME_ClfLiq(
        An_StatePhys, complete_feed_data['Fd_Category'],
        new_columns['Fd_DE_ClfLiq']
        )
    new_columns['Fd_DMIn_ClfFor'] = calculate_Fd_DMIn_ClfFor(
        Dt_DMIn, complete_feed_data['Fd_Conc'], complete_feed_data['Fd_DMInp']
        )
    new_columns["Fd_CaIn"] = calculate_Fd_CaIn(
        complete_feed_data['Fd_DMIn'], complete_feed_data["Fd_Ca"]
        )
    new_columns["Fd_PIn"] = calculate_Fd_PIn(
        complete_feed_data['Fd_DMIn'], complete_feed_data["Fd_P"]
        )
    new_columns["Fd_NaIn"] = calculate_Fd_NaIn(
        complete_feed_data['Fd_DMIn'], complete_feed_data["Fd_Na"]
        )
    new_columns["Fd_MgIn"] = calculate_Fd_MgIn(
        complete_feed_data['Fd_DMIn'], complete_feed_data["Fd_Mg"]
        )
    new_columns["Fd_KIn"] = calculate_Fd_KIn(
        complete_feed_data['Fd_DMIn'], complete_feed_data["Fd_K"]
        )
    new_columns["Fd_ClIn"] = calculate_Fd_ClIn(
        complete_feed_data['Fd_DMIn'], complete_feed_data["Fd_Cl"]
        )
    new_columns["Fd_SIn"] = calculate_Fd_SIn(
        complete_feed_data['Fd_DMIn'], complete_feed_data["Fd_S"]
        )
    new_columns['Fd_PinorgIn'] = calculate_Fd_PinorgIn(
        new_columns['Fd_PIn'], complete_feed_data['Fd_Pinorg_P']
        )
    new_columns['Fd_PorgIn'] = calculate_Fd_PorgIn(
        new_columns['Fd_PIn'], complete_feed_data['Fd_Porg_P']
        )
    new_columns['Fd_MgIn_min'] = calculate_Fd_MgIn_min(
        complete_feed_data['Fd_Category'], new_columns['Fd_MgIn']
        )
    new_columns["Fd_CoIn"] = calculate_Fd_CoIn(
        complete_feed_data['Fd_DMIn'], complete_feed_data["Fd_Co"]
        )
    new_columns["Fd_CrIn"] = calculate_Fd_CrIn(
        complete_feed_data['Fd_DMIn'], complete_feed_data["Fd_Cr"]
        )
    new_columns["Fd_CuIn"] = calculate_Fd_CuIn(
        complete_feed_data['Fd_DMIn'], complete_feed_data["Fd_Cu"]
        )
    new_columns["Fd_FeIn"] = calculate_Fd_FeIn(
        complete_feed_data['Fd_DMIn'], complete_feed_data["Fd_Fe"]
        )
    new_columns["Fd_IIn"] = calculate_Fd_IIn(
        complete_feed_data['Fd_DMIn'], complete_feed_data["Fd_I"]
        )
    new_columns["Fd_MnIn"] = calculate_Fd_MnIn(
        complete_feed_data['Fd_DMIn'], complete_feed_data["Fd_Mn"]
        )
    new_columns["Fd_MoIn"] = calculate_Fd_MoIn(
        complete_feed_data['Fd_DMIn'], complete_feed_data["Fd_Mo"]
        )
    new_columns["Fd_SeIn"] = calculate_Fd_SeIn(
        complete_feed_data['Fd_DMIn'], complete_feed_data["Fd_Se"]
        )
    new_columns["Fd_ZnIn"] = calculate_Fd_ZnIn(
        complete_feed_data['Fd_DMIn'], complete_feed_data["Fd_Zn"]
        )
    new_columns["Fd_VitAIn"] = calculate_Fd_VitAIn(
        complete_feed_data['Fd_DMIn'], complete_feed_data["Fd_VitA"]
        )
    new_columns["Fd_VitDIn"] = calculate_Fd_VitDIn(
        complete_feed_data['Fd_DMIn'], complete_feed_data["Fd_VitD"]
        )
    new_columns["Fd_VitEIn"] = calculate_Fd_VitEIn(
        complete_feed_data['Fd_DMIn'], complete_feed_data["Fd_VitE"]
        )
    new_columns["Fd_CholineIn"] = calculate_Fd_CholineIn(
        complete_feed_data['Fd_DMIn'], complete_feed_data["Fd_Choline"]
        )
    new_columns["Fd_BiotinIn"] = calculate_Fd_BiotinIn(
        complete_feed_data['Fd_DMIn'], complete_feed_data["Fd_Biotin"]
        )
    new_columns["Fd_NiacinIn"] = calculate_Fd_NiacinIn(
        complete_feed_data['Fd_DMIn'], complete_feed_data["Fd_Niacin"]
        )
    new_columns["Fd_B_CaroteneIn"] = calculate_Fd_B_CaroteneIn(
        complete_feed_data['Fd_DMIn'], complete_feed_data["Fd_B_Carotene"]
        )
    # Dt_DMIn_ClfLiq is needed for the calf mineral absorption calculations
    Dt_DMIn_ClfLiq = new_columns['Fd_DMIn_ClfLiq'].sum()

    new_columns['Fd_acCa'] = calculate_Fd_acCa(
        An_StatePhys, complete_feed_data['Fd_acCa_input'], Dt_DMIn_ClfLiq
        )
    new_columns['Fd_acPtot'] = calculate_Fd_acPtot(
        An_StatePhys, complete_feed_data['Fd_Category'],
        complete_feed_data['Fd_Pinorg_P'], complete_feed_data['Fd_Porg_P'],
        complete_feed_data['Fd_acPtot_input'], Dt_DMIn_ClfLiq
        )
    new_columns['Fd_acMg'] = calculate_Fd_acMg(
        An_StatePhys, complete_feed_data['Fd_acMg_input'], Dt_DMIn_ClfLiq
        )
    new_columns['Fd_acNa'] = calculate_Fd_acNa(
        An_StatePhys, complete_feed_data['Fd_acNa_input']
        )
    new_columns['Fd_acK'] = calculate_Fd_acK(
        An_StatePhys, complete_feed_data['Fd_acK_input']
        )
    new_columns['Fd_acCl'] = calculate_Fd_acCl(
        An_StatePhys, complete_feed_data['Fd_acCl_input'], Dt_DMIn_ClfLiq
        )
    new_columns['Fd_absCaIn'] = calculate_Fd_absCaIn(
        new_columns['Fd_CaIn'], new_columns['Fd_acCa']
        )
    new_columns['Fd_absPIn'] = calculate_Fd_absPIn(
        new_columns['Fd_PIn'], new_columns['Fd_acPtot']
        )
    new_columns['Fd_absMgIn_base'] = calculate_Fd_absMgIn_base(
        new_columns['Fd_MgIn'], new_columns['Fd_acMg']
        )
    new_columns['Fd_absNaIn'] = calculate_Fd_absNaIn(
        new_columns['Fd_NaIn'], new_columns['Fd_acNa']
        )
    new_columns['Fd_absKIn'] = calculate_Fd_absKIn(
        new_columns['Fd_KIn'], new_columns['Fd_acK']
        )
    new_columns['Fd_absClIn'] = calculate_Fd_absClIn(
        new_columns['Fd_ClIn'], new_columns['Fd_acCl']
        )
    new_columns['Fd_acCo'] = calculate_Fd_acCo(An_StatePhys)
    new_columns['Fd_acCu'] = calculate_Fd_acCu(
        An_StatePhys, complete_feed_data['Fd_acCu_input'], Dt_DMIn_ClfLiq
        )
    new_columns['Fd_acFe'] = calculate_Fd_acFe(
        An_StatePhys, complete_feed_data['Fd_acFe_input'], Dt_DMIn_ClfLiq
        )
    new_columns['Fd_acMn'] = calculate_Fd_acMn(
        An_StatePhys, complete_feed_data['Fd_acMn_input'], Dt_DMIn_ClfLiq
        )
    new_columns['Fd_acZn'] = calculate_Fd_acZn(
        An_StatePhys, complete_feed_data['Fd_acZn_input'], Dt_DMIn_ClfLiq
        )
    new_columns["Fd_absCoIn"] = calculate_Fd_absCoIn(
        new_columns["Fd_CoIn"], new_columns["Fd_acCo"]
        )
    new_columns["Fd_absCuIn"] = calculate_Fd_absCuIn(
        new_columns["Fd_CuIn"], new_columns["Fd_acCu"]
        )
    new_columns["Fd_absFeIn"] = calculate_Fd_absFeIn(
        new_columns["Fd_FeIn"], new_columns["Fd_acFe"]
        )
    new_columns["Fd_absMnIn"] = calculate_Fd_absMnIn(
        new_columns["Fd_MnIn"], new_columns["Fd_acMn"]
        )
    new_columns["Fd_absZnIn"] = calculate_Fd_absZnIn(
        new_columns["Fd_ZnIn"], new_columns["Fd_acZn"]
        )
    # Digested endogenous protein is ignored as it is a recycle of previously absorbed aa.
    # SI Digestibility of aa relative to RUP digestibility ([g dAA / g aa] / [g dRUP / g RUP])
    # All set to 1 due to lack of clear evidence for deviations.

    # TODO refactor this to use coeff_dict
    SIDigArgRUPf = 1
    SIDigHisRUPf = 1
    SIDigIleRUPf = 1
    SIDigLeuRUPf = 1
    SIDigLysRUPf = 1
    SIDigMetRUPf = 1
    SIDigPheRUPf = 1
    SIDigThrRUPf = 1
    SIDigTrpRUPf = 1
    SIDigValRUPf = 1
    # Store SIDig values in a dictionary
    SIDig_values = {
        'Arg': SIDigArgRUPf,
        'His': SIDigHisRUPf,
        'Ile': SIDigIleRUPf,
        'Leu': SIDigLeuRUPf,
        'Lys': SIDigLysRUPf,
        'Met': SIDigMetRUPf,
        'Phe': SIDigPheRUPf,
        'Thr': SIDigThrRUPf,
        'Trp': SIDigTrpRUPf,
        'Val': SIDigValRUPf
    }

    new_columns["Fd_Argt_CP"] = calculate_Fd_Argt_CP(
        complete_feed_data["Fd_Arg_CP"], coeff_dict
        )
    new_columns["Fd_Hist_CP"] = calculate_Fd_Hist_CP(
        complete_feed_data["Fd_His_CP"], coeff_dict
        )
    new_columns["Fd_Ilet_CP"] = calculate_Fd_Ilet_CP(
        complete_feed_data["Fd_Ile_CP"], coeff_dict
        )
    new_columns["Fd_Leut_CP"] = calculate_Fd_Leut_CP(
        complete_feed_data["Fd_Leu_CP"], coeff_dict
        )
    new_columns["Fd_Lyst_CP"] = calculate_Fd_Lyst_CP(
        complete_feed_data["Fd_Lys_CP"], coeff_dict
        )
    new_columns["Fd_Mett_CP"] = calculate_Fd_Mett_CP(
        complete_feed_data["Fd_Met_CP"], coeff_dict
        )
    new_columns["Fd_Phet_CP"] = calculate_Fd_Phet_CP(
        complete_feed_data["Fd_Phe_CP"], coeff_dict
        )
    new_columns["Fd_Thrt_CP"] = calculate_Fd_Thrt_CP(
        complete_feed_data["Fd_Thr_CP"], coeff_dict
        )
    new_columns["Fd_Trpt_CP"] = calculate_Fd_Trpt_CP(
        complete_feed_data["Fd_Trp_CP"], coeff_dict
        )
    new_columns["Fd_Valt_CP"] = calculate_Fd_Valt_CP(
        complete_feed_data["Fd_Val_CP"], coeff_dict
        )
    new_columns["Fd_ArgRUPIn"] = calculate_Fd_ArgRUPIn(
        new_columns['Fd_Argt_CP'], new_columns['Fd_RUPIn']
        )
    new_columns["Fd_HisRUPIn"] = calculate_Fd_HisRUPIn(
        new_columns['Fd_Hist_CP'], new_columns['Fd_RUPIn']
        )
    new_columns["Fd_IleRUPIn"] = calculate_Fd_IleRUPIn(
        new_columns['Fd_Ilet_CP'], new_columns['Fd_RUPIn']
        )
    new_columns["Fd_LeuRUPIn"] = calculate_Fd_LeuRUPIn(
        new_columns['Fd_Leut_CP'], new_columns['Fd_RUPIn']
        )
    new_columns["Fd_LysRUPIn"] = calculate_Fd_LysRUPIn(
        new_columns['Fd_Lyst_CP'], new_columns['Fd_RUPIn']
        )
    new_columns["Fd_MetRUPIn"] = calculate_Fd_MetRUPIn(
        new_columns['Fd_Mett_CP'], new_columns['Fd_RUPIn']
        )
    new_columns["Fd_PheRUPIn"] = calculate_Fd_PheRUPIn(
        new_columns['Fd_Phet_CP'], new_columns['Fd_RUPIn']
        )
    new_columns["Fd_ThrRUPIn"] = calculate_Fd_ThrRUPIn(
        new_columns['Fd_Thrt_CP'], new_columns['Fd_RUPIn']
        )
    new_columns["Fd_TrpRUPIn"] = calculate_Fd_TrpRUPIn(
        new_columns['Fd_Trpt_CP'], new_columns['Fd_RUPIn']
        )
    new_columns["Fd_ValRUPIn"] = calculate_Fd_ValRUPIn(
        new_columns['Fd_Valt_CP'], new_columns['Fd_RUPIn']
        )
    new_columns["Fd_IdArgRUPIn"] = calculate_Fd_IdArgRUPIn(
        complete_feed_data["Fd_dcRUP"], new_columns['Fd_ArgRUPIn'], 
        SIDig_values["Arg"]
        )
    new_columns["Fd_IdHisRUPIn"] = calculate_Fd_IdHisRUPIn(
        complete_feed_data["Fd_dcRUP"], new_columns['Fd_HisRUPIn'], 
        SIDig_values["His"]
        )
    new_columns["Fd_IdIleRUPIn"] = calculate_Fd_IdIleRUPIn(
        complete_feed_data["Fd_dcRUP"], new_columns['Fd_IleRUPIn'], 
        SIDig_values["Ile"]
        )
    new_columns["Fd_IdLeuRUPIn"] = calculate_Fd_IdLeuRUPIn(
        complete_feed_data["Fd_dcRUP"], new_columns['Fd_LeuRUPIn'], 
        SIDig_values["Leu"]
        )
    new_columns["Fd_IdLysRUPIn"] = calculate_Fd_IdLysRUPIn(
        complete_feed_data["Fd_dcRUP"], new_columns['Fd_LysRUPIn'], 
        SIDig_values["Lys"]
        )
    new_columns["Fd_IdMetRUPIn"] = calculate_Fd_IdMetRUPIn(
        complete_feed_data["Fd_dcRUP"], new_columns['Fd_MetRUPIn'], 
        SIDig_values["Met"]
        )
    new_columns["Fd_IdPheRUPIn"] = calculate_Fd_IdPheRUPIn(
        complete_feed_data["Fd_dcRUP"], new_columns['Fd_PheRUPIn'], 
        SIDig_values["Phe"]
        )
    new_columns["Fd_IdThrRUPIn"] = calculate_Fd_IdThrRUPIn(
        complete_feed_data["Fd_dcRUP"], new_columns['Fd_ThrRUPIn'], 
        SIDig_values["Thr"]
        )
    new_columns["Fd_IdTrpRUPIn"] = calculate_Fd_IdTrpRUPIn(
        complete_feed_data["Fd_dcRUP"], new_columns['Fd_TrpRUPIn'], 
        SIDig_values["Trp"]
        )
    new_columns["Fd_IdValRUPIn"] = calculate_Fd_IdValRUPIn(
        complete_feed_data["Fd_dcRUP"], new_columns['Fd_ValRUPIn'], 
        SIDig_values["Val"]
        )
    new_columns['Fd_DigSt'] = calculate_Fd_DigSt(
        complete_feed_data['Fd_St'], complete_feed_data['Fd_dcSt']
        )
    new_columns['Fd_DigStIn_Base'] = calculate_Fd_DigStIn_Base(
        new_columns['Fd_DigSt'], complete_feed_data['Fd_DMIn']
        )
    new_columns['Fd_DigrOMt'] = calculate_Fd_DigrOMt(
        new_columns['Fd_rOM'], coeff_dict
        )
    new_columns['Fd_DigrOMtIn'] = calculate_Fd_DigrOMtIn(
        new_columns['Fd_DigrOMt'], complete_feed_data['Fd_DMIn']
        )
    new_columns['Fd_idRUPIn'] = calculate_Fd_idRUPIn(
        complete_feed_data['Fd_dcRUP'], new_columns['Fd_RUPIn']
        )
    new_columns['TT_dcFdFA'] = calculate_TT_dcFdFA(
        An_StatePhys, complete_feed_data['Fd_Category'], 
        complete_feed_data['Fd_Type'], complete_feed_data['Fd_dcFA'], coeff_dict
        )
    new_columns['Fd_DigFAIn'] = calculate_Fd_DigFAIn(
        new_columns['TT_dcFdFA'], complete_feed_data['Fd_FA'],
        complete_feed_data['Fd_DMIn']
        )
    new_columns["Fd_DigC120In"] = calculate_Fd_DigC120In(
        new_columns['TT_dcFdFA'], complete_feed_data["Fd_C120_FA"], 
        complete_feed_data["Fd_FA"], complete_feed_data['Fd_DMIn']
        )
    new_columns["Fd_DigC140In"] = calculate_Fd_DigC140In(
        new_columns['TT_dcFdFA'], complete_feed_data["Fd_C140_FA"], 
        complete_feed_data["Fd_FA"], complete_feed_data['Fd_DMIn']
        )
    new_columns["Fd_DigC160In"] = calculate_Fd_DigC160In(
        new_columns['TT_dcFdFA'], complete_feed_data["Fd_C160_FA"], 
        complete_feed_data["Fd_FA"], complete_feed_data['Fd_DMIn']
        )
    new_columns["Fd_DigC161In"] = calculate_Fd_DigC161In(
        new_columns['TT_dcFdFA'], complete_feed_data["Fd_C161_FA"], 
        complete_feed_data["Fd_FA"], complete_feed_data['Fd_DMIn']
        )
    new_columns["Fd_DigC180In"] = calculate_Fd_DigC180In(
        new_columns['TT_dcFdFA'], complete_feed_data["Fd_C180_FA"], 
        complete_feed_data["Fd_FA"], complete_feed_data['Fd_DMIn']
        )
    new_columns["Fd_DigC181tIn"] = calculate_Fd_DigC181tIn(
        new_columns['TT_dcFdFA'], complete_feed_data["Fd_C181t_FA"], 
        complete_feed_data["Fd_FA"], complete_feed_data['Fd_DMIn']
        )
    new_columns["Fd_DigC181cIn"] = calculate_Fd_DigC181cIn(
        new_columns['TT_dcFdFA'], complete_feed_data["Fd_C181c_FA"], 
        complete_feed_data["Fd_FA"], complete_feed_data['Fd_DMIn']
        )
    new_columns["Fd_DigC182In"] = calculate_Fd_DigC182In(
        new_columns['TT_dcFdFA'], complete_feed_data["Fd_C182_FA"], 
        complete_feed_data["Fd_FA"], complete_feed_data['Fd_DMIn']
        )
    new_columns["Fd_DigC183In"] = calculate_Fd_DigC183In(
        new_columns['TT_dcFdFA'], complete_feed_data["Fd_C183_FA"], 
        complete_feed_data["Fd_FA"], complete_feed_data['Fd_DMIn']
        )
    new_columns["Fd_DigOtherFAIn"] = calculate_Fd_DigOtherFAIn(
        new_columns['TT_dcFdFA'], complete_feed_data["Fd_OtherFA_FA"], 
        complete_feed_data["Fd_FA"], complete_feed_data['Fd_DMIn']
        )
    new_columns['Fd_DigrOMa'] = calculate_Fd_DigrOMa(
        new_columns['Fd_DigrOMt'], coeff_dict
        )
    new_columns['Fd_DigrOMaIn'] = calculate_Fd_DigrOMaIn(
        new_columns['Fd_DigrOMa'], complete_feed_data['Fd_DMIn']
        )
    new_columns['Fd_DigWSC'] = calculate_Fd_DigWSC(
        complete_feed_data['Fd_WSC']
        )
    new_columns['Fd_DigWSCIn'] = calculate_Fd_DigWSCIn(
        new_columns['Fd_DigWSC'], complete_feed_data['Fd_DMIn']
        )
    new_columns['Fd_idRUP'] = calculate_Fd_idRUP(
        new_columns['Fd_CPIn'], new_columns['Fd_idRUPIn'],
        complete_feed_data['Fd_DMIn']
        )
    new_columns['Fd_Fe_RUPout'] = calculate_Fd_Fe_RUPout(
        new_columns['Fd_RUPIn'], complete_feed_data['Fd_dcRUP']
        )
    new_columns["Fd_ArgIn"] = calculate_Fd_ArgIn(
        new_columns["Fd_CPIn"], new_columns['Fd_Argt_CP'], 
        complete_feed_data["Fd_CP"], complete_feed_data['Fd_DMIn']
        )
    new_columns["Fd_HisIn"] = calculate_Fd_HisIn(
        new_columns["Fd_CPIn"], new_columns['Fd_Hist_CP'], 
        complete_feed_data["Fd_CP"], complete_feed_data['Fd_DMIn']
        )
    new_columns["Fd_IleIn"] = calculate_Fd_IleIn(
        new_columns["Fd_CPIn"], new_columns['Fd_Ilet_CP'], 
        complete_feed_data["Fd_CP"], complete_feed_data['Fd_DMIn']
        )
    new_columns["Fd_LeuIn"] = calculate_Fd_LeuIn(
        new_columns["Fd_CPIn"], new_columns['Fd_Leut_CP'], 
        complete_feed_data["Fd_CP"], complete_feed_data['Fd_DMIn']
        )
    new_columns["Fd_LysIn"] = calculate_Fd_LysIn(
        new_columns["Fd_CPIn"], new_columns['Fd_Lyst_CP'], 
        complete_feed_data["Fd_CP"], complete_feed_data['Fd_DMIn']
        )
    new_columns["Fd_MetIn"] = calculate_Fd_MetIn(
        new_columns['Fd_CPIn'], new_columns['Fd_Mett_CP'], 
        complete_feed_data["Fd_CP"], complete_feed_data['Fd_DMIn']
        )
    new_columns["Fd_PheIn"] = calculate_Fd_PheIn(
        new_columns['Fd_CPIn'], new_columns['Fd_Phet_CP'], 
        complete_feed_data["Fd_CP"], complete_feed_data['Fd_DMIn']
        )
    new_columns["Fd_ThrIn"] = calculate_Fd_ThrIn(
        new_columns['Fd_CPIn'], new_columns['Fd_Thrt_CP'], 
        complete_feed_data["Fd_CP"], complete_feed_data['Fd_DMIn']
        )
    new_columns["Fd_TrpIn"] = calculate_Fd_TrpIn(
        new_columns['Fd_CPIn'], new_columns['Fd_Trpt_CP'], 
        complete_feed_data["Fd_CP"], complete_feed_data['Fd_DMIn']
        )
    new_columns["Fd_ValIn"] = calculate_Fd_ValIn(
        new_columns['Fd_CPIn'], new_columns['Fd_Valt_CP'], 
        complete_feed_data["Fd_CP"], complete_feed_data['Fd_DMIn']
        )
    new_columns["Fd_AFInp"] = calculate_Fd_AFInp(
        new_columns["Fd_AFIn"]
        )
    new_columns["Fd_RDPIn"] = calculate_Fd_RDPIn(
        new_columns["Fd_RDP"], complete_feed_data['Fd_DMIn']
    )
    complete_feed_data = pd.concat(
        [complete_feed_data, pd.DataFrame(new_columns)], axis=1
        )
    return complete_feed_data


def calculate_diet_data(
    complete_feed_data: pd.DataFrame,
    diet_data: dict,
    Dt_DMIn: float, 
    An_BW: float, 
    An_StatePhys: str, 
    An_DMIn_BW: float,
    An_AgeDryFdStart: int, 
    Env_TempCurr: float, 
    DMIn_eqn: int,
    Monensin_eqn: int, 
    Fe_rOMend: float, 
    Fe_CP: float,
    Fe_CPend: float,
    Fe_MiTP: float,
    Fe_NPend: float,
    Du_idMiTP: float,
    Du_IdAAMic: pd.Series,
    coeff_dict: dict
) -> dict:
    # Diet Intakes
    diet_data["Dt_ADF"] = calculate_Dt_ADF(
        complete_feed_data["Fd_DMInp"], complete_feed_data["Fd_ADF"]
        )
    diet_data["Dt_NDF"] = calculate_Dt_NDF(
        complete_feed_data["Fd_DMInp"], complete_feed_data["Fd_NDF"]
        )
    diet_data["Dt_For"] = calculate_Dt_For(
        complete_feed_data["Fd_DMInp"], complete_feed_data["Fd_For"]
        )
    diet_data["Dt_ForNDF"] = calculate_Dt_ForNDF(
        complete_feed_data["Fd_DMInp"], complete_feed_data["Fd_ForNDF"]
        )
    diet_data["Dt_DMIn_ClfLiq"] = calculate_Dt_DMIn_ClfLiq(
        complete_feed_data["Fd_DMIn_ClfLiq"]
        )
    diet_data["Dt_DMIn_ClfFor"] = calculate_Dt_DMIn_ClfFor(
        complete_feed_data["Fd_DMIn_ClfFor"]
        )
    diet_data["Dt_AFIn"] = calculate_Dt_AFIn(
        complete_feed_data["Fd_AFIn"]
        )
    diet_data["Dt_NDFIn"] = calculate_Dt_NDFIn(
        complete_feed_data["Fd_NDFIn"]
        )
    diet_data["Dt_ADFIn"] = calculate_Dt_ADFIn(
        complete_feed_data["Fd_ADFIn"]
        )
    diet_data["Dt_LgIn"] = calculate_Dt_LgIn(
        complete_feed_data["Fd_LgIn"]
        )
    diet_data["Dt_DigNDFIn_Base"] = calculate_Dt_DigNDFIn_Base(
        complete_feed_data["Fd_DigNDFIn_Base"]
        )
    diet_data["Dt_ForWetIn"] = calculate_Dt_ForWetIn(
        complete_feed_data["Fd_ForWetIn"]
        )
    diet_data["Dt_ForDryIn"] = calculate_Dt_ForDryIn(
        complete_feed_data["Fd_ForDryIn"]
        )
    diet_data["Dt_PastIn"] = calculate_Dt_PastIn(
        complete_feed_data["Fd_PastIn"]
        )
    diet_data["Dt_ForIn"] = calculate_Dt_ForIn(
        complete_feed_data["Fd_ForIn"]
        )
    diet_data["Dt_ConcIn"] = calculate_Dt_ConcIn(
        complete_feed_data["Fd_ConcIn"]
        )
    diet_data["Dt_NFCIn"] = calculate_Dt_NFCIn(
        complete_feed_data["Fd_NFCIn"]
        )
    diet_data["Dt_StIn"] = calculate_Dt_StIn(
        complete_feed_data["Fd_StIn"]
        )
    diet_data["Dt_WSCIn"] = calculate_Dt_WSCIn(
        complete_feed_data["Fd_WSCIn"]
        )
    diet_data["Dt_CPIn"] = calculate_Dt_CPIn(
        complete_feed_data["Fd_CPIn"]
        )
    diet_data["Dt_CPIn_ClfLiq"] = calculate_Dt_CPIn_ClfLiq(
        complete_feed_data["Fd_CPIn_ClfLiq"]
        )
    diet_data["Dt_TPIn"] = calculate_Dt_TPIn(
        complete_feed_data["Fd_TPIn"]
        )
    diet_data["Dt_NPNCPIn"] = calculate_Dt_NPNCPIn(
        complete_feed_data["Fd_NPNCPIn"]
        )
    diet_data["Dt_NPNIn"] = calculate_Dt_NPNIn(
        complete_feed_data["Fd_NPNIn"]
        )
    diet_data["Dt_NPNDMIn"] = calculate_Dt_NPNDMIn(
        complete_feed_data["Fd_NPNDMIn"]
        )
    diet_data["Dt_CPAIn"] = calculate_Dt_CPAIn(
        complete_feed_data["Fd_CPAIn"]
        )
    diet_data["Dt_CPBIn"] = calculate_Dt_CPBIn(
        complete_feed_data["Fd_CPBIn"]
        )
    diet_data["Dt_CPCIn"] = calculate_Dt_CPCIn(
        complete_feed_data["Fd_CPCIn"]
        )
    diet_data["Dt_RUPBIn"] = calculate_Dt_RUPBIn(
        complete_feed_data["Fd_RUPBIn"]
        )
    diet_data["Dt_CFatIn"] = calculate_Dt_CFatIn(
        complete_feed_data["Fd_CFatIn"]
        )
    diet_data["Dt_FAIn"] = calculate_Dt_FAIn(
        complete_feed_data["Fd_FAIn"]
        )
    diet_data["Dt_FAhydrIn"] = calculate_Dt_FAhydrIn(
        complete_feed_data["Fd_FAhydrIn"]
        )
    diet_data["Dt_C120In"] = calculate_Dt_C120In(
        complete_feed_data["Fd_C120In"]
        )
    diet_data["Dt_C140In"] = calculate_Dt_C140In(
        complete_feed_data["Fd_C140In"]
        )
    diet_data["Dt_C160In"] = calculate_Dt_C160In(
        complete_feed_data["Fd_C160In"]
        )
    diet_data["Dt_C161In"] = calculate_Dt_C161In(
        complete_feed_data["Fd_C161In"]
        )
    diet_data["Dt_C180In"] = calculate_Dt_C180In(
        complete_feed_data["Fd_C180In"]
        )
    diet_data["Dt_C181tIn"] = calculate_Dt_C181tIn(
        complete_feed_data["Fd_C181tIn"]
        )
    diet_data["Dt_C181cIn"] = calculate_Dt_C181cIn(
        complete_feed_data["Fd_C181cIn"]
        )
    diet_data["Dt_C182In"] = calculate_Dt_C182In(
        complete_feed_data["Fd_C182In"]
        )
    diet_data["Dt_C183In"] = calculate_Dt_C183In(
        complete_feed_data["Fd_C183In"]
        )
    diet_data["Dt_OtherFAIn"] = calculate_Dt_OtherFAIn(
        complete_feed_data["Fd_OtherFAIn"]
        )
    diet_data["Dt_AshIn"] = calculate_Dt_AshIn(
        complete_feed_data["Fd_AshIn"]
        )
    diet_data["Dt_GEIn"] = calculate_Dt_GEIn(
        complete_feed_data["Fd_GEIn"]
        )
    diet_data["Dt_DEIn_base"] = calculate_Dt_DEIn_base(
        complete_feed_data["Fd_DEIn_base"]
        )
    diet_data["Dt_DEIn_base_ClfLiq"] = calculate_Dt_DEIn_base_ClfLiq(
        complete_feed_data["Fd_DEIn_base_ClfLiq"]
        )
    diet_data["Dt_DEIn_base_ClfDry"] = calculate_Dt_DEIn_base_ClfDry(
        complete_feed_data["Fd_DEIn_base_ClfDry"]
        )
    diet_data["Dt_DigStIn_Base"] = calculate_Dt_DigStIn_Base(
        complete_feed_data["Fd_DigStIn_Base"]
        )
    diet_data["Dt_DigrOMtIn"] = calculate_Dt_DigrOMtIn(
        complete_feed_data["Fd_DigrOMtIn"]
        )
    diet_data["Dt_idRUPIn"] = calculate_Dt_idRUPIn(
        complete_feed_data["Fd_idRUPIn"]
        )
    diet_data["Dt_DigFAIn"] = calculate_Dt_DigFAIn(
        complete_feed_data["Fd_DigFAIn"]
        )
    diet_data["Dt_ArgIn"] = calculate_Dt_ArgIn(
        complete_feed_data["Fd_ArgIn"]
        )
    diet_data["Dt_HisIn"] = calculate_Dt_HisIn(
        complete_feed_data["Fd_HisIn"]
        )
    diet_data["Dt_IleIn"] = calculate_Dt_IleIn(
        complete_feed_data["Fd_IleIn"]
        )
    diet_data["Dt_LeuIn"] = calculate_Dt_LeuIn(
        complete_feed_data["Fd_LeuIn"]
        )
    diet_data["Dt_LysIn"] = calculate_Dt_LysIn(
        complete_feed_data["Fd_LysIn"]
        )
    diet_data["Dt_MetIn"] = calculate_Dt_MetIn(
        complete_feed_data["Fd_MetIn"]
        )
    diet_data["Dt_PheIn"] = calculate_Dt_PheIn(
        complete_feed_data["Fd_PheIn"]
        )
    diet_data["Dt_ThrIn"] = calculate_Dt_ThrIn(
        complete_feed_data["Fd_ThrIn"]
        )
    diet_data["Dt_TrpIn"] = calculate_Dt_TrpIn(
        complete_feed_data["Fd_TrpIn"]
        )
    diet_data["Dt_ValIn"] = calculate_Dt_ValIn(
        complete_feed_data["Fd_ValIn"]
        )
    diet_data["Dt_ArgRUPIn"] = calculate_Dt_ArgRUPIn(
        complete_feed_data["Fd_ArgRUPIn"]
        )
    diet_data["Dt_HisRUPIn"] = calculate_Dt_HisRUPIn(
        complete_feed_data["Fd_HisRUPIn"]
        )
    diet_data["Dt_IleRUPIn"] = calculate_Dt_IleRUPIn(
        complete_feed_data["Fd_IleRUPIn"]
        )
    diet_data["Dt_LeuRUPIn"] = calculate_Dt_LeuRUPIn(
        complete_feed_data["Fd_LeuRUPIn"]
        )
    diet_data["Dt_LysRUPIn"] = calculate_Dt_LysRUPIn(
        complete_feed_data["Fd_LysRUPIn"]
        )
    diet_data["Dt_MetRUPIn"] = calculate_Dt_MetRUPIn(
        complete_feed_data["Fd_MetRUPIn"]
        )
    diet_data["Dt_PheRUPIn"] = calculate_Dt_PheRUPIn(
        complete_feed_data["Fd_PheRUPIn"]
        )
    diet_data["Dt_ThrRUPIn"] = calculate_Dt_ThrRUPIn(
        complete_feed_data["Fd_ThrRUPIn"]
        )
    diet_data["Dt_TrpRUPIn"] = calculate_Dt_TrpRUPIn(
        complete_feed_data["Fd_TrpRUPIn"]
        )
    diet_data["Dt_ValRUPIn"] = calculate_Dt_ValRUPIn(
        complete_feed_data["Fd_ValRUPIn"]
        )
    diet_data['Dt_DMInSum'] = calculate_Dt_DMInSum(
        complete_feed_data['Fd_DMIn']
        )
    diet_data['Dt_DEIn_ClfLiq'] = calculate_Dt_DEIn_ClfLiq(
        complete_feed_data['Fd_DE_ClfLiq'], complete_feed_data['Fd_DMIn_ClfLiq']
        )
    diet_data['Dt_MEIn_ClfLiq'] = calculate_Dt_MEIn_ClfLiq(
        complete_feed_data['Fd_ME_ClfLiq'], complete_feed_data['Fd_DMIn_ClfLiq']
        )
    diet_data['Dt_ForDNDF48'] = calculate_Dt_ForDNDF48(
        complete_feed_data['Fd_DMInp'], complete_feed_data['Fd_Conc'], 
        complete_feed_data['Fd_NDF'], complete_feed_data['Fd_DNDF48']
        )
    diet_data['Dt_ForDNDF48_ForNDF'] = calculate_Dt_ForDNDF48_ForNDF(
        diet_data['Dt_ForDNDF48'], diet_data['Dt_ForNDF']
        )
    diet_data['Dt_ADF_NDF'] = calculate_Dt_ADF_NDF(
        diet_data['Dt_ADF'], diet_data['Dt_NDF']
        )
    diet_data['Dt_NDFnfIn'] = calculate_Dt_NDFnfIn(
        complete_feed_data['Fd_DMIn'], complete_feed_data['Fd_NDFnf']
        )
    diet_data['Dt_Lg_NDF'] = calculate_Dt_Lg_NDF(
        diet_data['Dt_LgIn'], diet_data['Dt_NDFIn']
        )
    diet_data['Dt_ForNDFIn'] = calculate_Dt_ForNDFIn(
        complete_feed_data['Fd_DMIn'], complete_feed_data['Fd_ForNDF']
        )
    diet_data['Dt_PastSupplIn'] = calculate_Dt_PastSupplIn(
        diet_data['Dt_DMInSum'], diet_data['Dt_PastIn']
        )
    diet_data['Dt_NIn'] = calculate_Dt_NIn(diet_data['Dt_CPIn'])
    diet_data['Dt_RUPIn'] = calculate_Dt_RUPIn(complete_feed_data['Fd_RUPIn'])
    diet_data['Dt_RUP_CP'] = calculate_Dt_RUP_CP(
        diet_data['Dt_CPIn'], diet_data['Dt_RUPIn']
        )
    diet_data['Dt_fCPBdu'] = calculate_Dt_fCPBdu(
        diet_data['Dt_RUPBIn'], diet_data['Dt_CPBIn']
        )
    diet_data['Dt_UFAIn'] = calculate_Dt_UFAIn(
        diet_data['Dt_C161In'], diet_data['Dt_C181tIn'], 
        diet_data['Dt_C181cIn'], diet_data['Dt_C182In'], 
        diet_data['Dt_C183In']
        )
    diet_data['Dt_MUFAIn'] = calculate_Dt_MUFAIn(
        diet_data['Dt_C161In'], diet_data['Dt_C181tIn'], diet_data['Dt_C181cIn']
        )
    diet_data['Dt_PUFAIn'] = calculate_Dt_PUFAIn(
        diet_data['Dt_UFAIn'], diet_data['Dt_C161In'], diet_data['Dt_C181tIn'], 
        diet_data['Dt_C181cIn']
        )
    diet_data['Dt_SatFAIn'] = calculate_Dt_SatFAIn(
        diet_data['Dt_FAIn'], diet_data['Dt_UFAIn']
        )
    diet_data['Dt_OMIn'] = calculate_Dt_OMIn(Dt_DMIn, diet_data['Dt_AshIn'])
    diet_data['Dt_rOMIn'] = calculate_Dt_rOMIn(
        Dt_DMIn, diet_data['Dt_AshIn'], diet_data['Dt_NDFIn'], 
        diet_data['Dt_StIn'], diet_data['Dt_FAhydrIn'], diet_data['Dt_TPIn'], 
        diet_data['Dt_NPNDMIn']
        )
    diet_data['Dt_DM'] = calculate_Dt_DM(Dt_DMIn, diet_data['Dt_AFIn'])
    diet_data['Dt_NDFIn_BW'] = calculate_Dt_NDFIn_BW(
        An_BW, diet_data['Dt_NDFIn']
        )
    diet_data["Dt_RUP"] = calculate_Dt_RUP(diet_data["Dt_RUPIn"], Dt_DMIn)
    diet_data["Dt_OM"] = calculate_Dt_OM(diet_data["Dt_OMIn"], Dt_DMIn)
    diet_data["Dt_NDFnf"] = calculate_Dt_NDFnf(diet_data["Dt_NDFnfIn"], Dt_DMIn)
    diet_data["Dt_Lg"] = calculate_Dt_Lg(diet_data["Dt_LgIn"], Dt_DMIn)
    diet_data["Dt_NFC"] = calculate_Dt_NFC(diet_data["Dt_NFCIn"], Dt_DMIn)
    diet_data["Dt_St"] = calculate_Dt_St(diet_data["Dt_StIn"], Dt_DMIn)
    diet_data["Dt_WSC"] = calculate_Dt_WSC(diet_data["Dt_WSCIn"], Dt_DMIn)
    diet_data["Dt_rOM"] = calculate_Dt_rOM(diet_data["Dt_rOMIn"], Dt_DMIn)
    diet_data["Dt_CFat"] = calculate_Dt_CFat(diet_data["Dt_CFatIn"], Dt_DMIn)
    diet_data["Dt_FA"] = calculate_Dt_FA(diet_data["Dt_FAIn"], Dt_DMIn)
    diet_data["Dt_FAhydr"] = calculate_Dt_FAhydr(
        diet_data["Dt_FAhydrIn"], Dt_DMIn
        )
    diet_data["Dt_CP"] = calculate_Dt_CP(diet_data["Dt_CPIn"], Dt_DMIn)
    diet_data["Dt_TP"] = calculate_Dt_TP(diet_data["Dt_TPIn"], Dt_DMIn)
    diet_data["Dt_NPNCP"] = calculate_Dt_NPNCP(diet_data["Dt_NPNCPIn"], Dt_DMIn)
    diet_data["Dt_NPN"] = calculate_Dt_NPN(diet_data["Dt_NPNIn"], Dt_DMIn)
    diet_data["Dt_NPNDM"] = calculate_Dt_NPNDM(diet_data["Dt_NPNDMIn"], Dt_DMIn)
    diet_data["Dt_CPA"] = calculate_Dt_CPA(diet_data["Dt_CPAIn"], Dt_DMIn)
    diet_data["Dt_CPB"] = calculate_Dt_CPB(diet_data["Dt_CPBIn"], Dt_DMIn)
    diet_data["Dt_CPC"] = calculate_Dt_CPC(diet_data["Dt_CPCIn"], Dt_DMIn)
    diet_data["Dt_Ash"] = calculate_Dt_Ash(diet_data["Dt_AshIn"], Dt_DMIn)
    diet_data["Dt_ForWet"] = calculate_Dt_ForWet(
        diet_data["Dt_ForWetIn"], Dt_DMIn
        )
    diet_data["Dt_ForDry"] = calculate_Dt_ForDry(
        diet_data["Dt_ForDryIn"], Dt_DMIn
        )
    diet_data["Dt_Conc"] = calculate_Dt_Conc(diet_data["Dt_ConcIn"], Dt_DMIn)
    diet_data["Dt_C120"] = calculate_Dt_C120(diet_data["Dt_C120In"], Dt_DMIn)
    diet_data["Dt_C140"] = calculate_Dt_C140(diet_data["Dt_C140In"], Dt_DMIn)
    diet_data["Dt_C160"] = calculate_Dt_C160(diet_data["Dt_C160In"], Dt_DMIn)
    diet_data["Dt_C161"] = calculate_Dt_C161(diet_data["Dt_C161In"], Dt_DMIn)
    diet_data["Dt_C180"] = calculate_Dt_C180(diet_data["Dt_C180In"], Dt_DMIn)
    diet_data["Dt_C181t"] = calculate_Dt_C181t(diet_data["Dt_C181tIn"], Dt_DMIn)
    diet_data["Dt_C181c"] = calculate_Dt_C181c(diet_data["Dt_C181cIn"], Dt_DMIn)
    diet_data["Dt_C182"] = calculate_Dt_C182(diet_data["Dt_C182In"], Dt_DMIn)
    diet_data["Dt_C183"] = calculate_Dt_C183(diet_data["Dt_C183In"], Dt_DMIn)
    diet_data["Dt_OtherFA"] = calculate_Dt_OtherFA(
        diet_data["Dt_OtherFAIn"], Dt_DMIn
        )
    diet_data["Dt_UFA"] = calculate_Dt_UFA(diet_data["Dt_UFAIn"], Dt_DMIn)
    diet_data["Dt_MUFA"] = calculate_Dt_MUFA(diet_data["Dt_MUFAIn"], Dt_DMIn)
    diet_data["Dt_PUFA"] = calculate_Dt_PUFA(diet_data["Dt_PUFAIn"], Dt_DMIn)
    diet_data["Dt_SatFA"] = calculate_Dt_SatFA(diet_data["Dt_SatFAIn"], Dt_DMIn)
    diet_data["Dt_C120_FA"] = calculate_Dt_C120_FA(
        diet_data["Dt_C120In"], diet_data["Dt_FAIn"]
        )
    diet_data["Dt_C140_FA"] = calculate_Dt_C140_FA(
        diet_data["Dt_C140In"], diet_data["Dt_FAIn"]
        )
    diet_data["Dt_C160_FA"] = calculate_Dt_C160_FA(
        diet_data["Dt_C160In"], diet_data["Dt_FAIn"]
        )
    diet_data["Dt_C161_FA"] = calculate_Dt_C161_FA(
        diet_data["Dt_C161In"], diet_data["Dt_FAIn"]
        )
    diet_data["Dt_C180_FA"] = calculate_Dt_C180_FA(
        diet_data["Dt_C180In"], diet_data["Dt_FAIn"]
        )
    diet_data["Dt_C181t_FA"] = calculate_Dt_C181t_FA(
        diet_data["Dt_C181tIn"], diet_data["Dt_FAIn"]
        )
    diet_data["Dt_C181c_FA"] = calculate_Dt_C181c_FA(
        diet_data["Dt_C181cIn"], diet_data["Dt_FAIn"]
        )
    diet_data["Dt_C182_FA"] = calculate_Dt_C182_FA(
        diet_data["Dt_C182In"], diet_data["Dt_FAIn"]
        )
    diet_data["Dt_C183_FA"] = calculate_Dt_C183_FA(
        diet_data["Dt_C183In"], diet_data["Dt_FAIn"]
        )
    diet_data["Dt_OtherFA_FA"] = calculate_Dt_OtherFA_FA(
        diet_data["Dt_OtherFAIn"], diet_data["Dt_FAIn"]
        )
    diet_data["Dt_UFA_FA"] = calculate_Dt_UFA_FA(
        diet_data["Dt_UFAIn"], diet_data["Dt_FAIn"]
        )
    diet_data["Dt_MUFA_FA"] = calculate_Dt_MUFA_FA(
        diet_data["Dt_MUFAIn"], diet_data["Dt_FAIn"]
        )
    diet_data["Dt_PUFA_FA"] = calculate_Dt_PUFA_FA(
        diet_data["Dt_PUFAIn"], diet_data["Dt_FAIn"]
        )
    diet_data["Dt_SatFA_FA"] = calculate_Dt_SatFA_FA(
        diet_data["Dt_SatFAIn"], diet_data["Dt_FAIn"]
        )
    diet_data['Dt_ForNDF_NDF'] = calculate_Dt_ForNDF_NDF(
        diet_data['Dt_ForNDF'], diet_data['Dt_NDF']
        )
    diet_data['Dt_ForNDFIn_BW'] = calculate_Dt_ForNDFIn_BW(
        An_BW, diet_data['Dt_ForNDFIn']
        )
    diet_data['Dt_CPA_CP'] = calculate_Dt_CPA_CP(
        diet_data['Dt_CPAIn'], diet_data['Dt_CPIn']
        )
    diet_data['Dt_CPB_CP'] = calculate_Dt_CPB_CP(
        diet_data['Dt_CPBIn'], diet_data['Dt_CPIn']
        )
    diet_data['Dt_CPC_CP'] = calculate_Dt_CPC_CP(
        diet_data['Dt_CPCIn'], diet_data['Dt_CPIn']
        )
    diet_data["Dt_CaIn"] = calculate_Dt_CaIn(complete_feed_data["Fd_CaIn"])
    diet_data["Dt_PIn"] = calculate_Dt_PIn(complete_feed_data["Fd_PIn"])
    diet_data["Dt_PinorgIn"] = calculate_Dt_PinorgIn(
        complete_feed_data["Fd_PinorgIn"]
        )
    diet_data["Dt_PorgIn"] = calculate_Dt_PorgIn(
        complete_feed_data["Fd_PorgIn"]
        )
    diet_data["Dt_NaIn"] = calculate_Dt_NaIn(complete_feed_data["Fd_NaIn"])
    diet_data["Dt_MgIn"] = calculate_Dt_MgIn(complete_feed_data["Fd_MgIn"])
    diet_data["Dt_MgIn_min"] = calculate_Dt_MgIn_min(
        complete_feed_data["Fd_MgIn_min"]
        )
    diet_data["Dt_KIn"] = calculate_Dt_KIn(complete_feed_data["Fd_KIn"])
    diet_data["Dt_ClIn"] = calculate_Dt_ClIn(complete_feed_data["Fd_ClIn"])
    diet_data["Dt_SIn"] = calculate_Dt_SIn(complete_feed_data["Fd_SIn"])
    diet_data["Dt_CoIn"] = calculate_Dt_CoIn(complete_feed_data["Fd_CoIn"])
    diet_data["Dt_CrIn"] = calculate_Dt_CrIn(complete_feed_data["Fd_CrIn"])
    diet_data["Dt_CuIn"] = calculate_Dt_CuIn(complete_feed_data["Fd_CuIn"])
    diet_data["Dt_FeIn"] = calculate_Dt_FeIn(complete_feed_data["Fd_FeIn"])
    diet_data["Dt_IIn"] = calculate_Dt_IIn(complete_feed_data["Fd_IIn"])
    diet_data["Dt_MnIn"] = calculate_Dt_MnIn(complete_feed_data["Fd_MnIn"])
    diet_data["Dt_MoIn"] = calculate_Dt_MoIn(complete_feed_data["Fd_MoIn"])
    diet_data["Dt_SeIn"] = calculate_Dt_SeIn(complete_feed_data["Fd_SeIn"])
    diet_data["Dt_ZnIn"] = calculate_Dt_ZnIn(complete_feed_data["Fd_ZnIn"])
    diet_data["Dt_VitAIn"] = calculate_Dt_VitAIn(
        complete_feed_data["Fd_VitAIn"]
        )
    diet_data["Dt_VitDIn"] = calculate_Dt_VitDIn(
        complete_feed_data["Fd_VitDIn"]
        )
    diet_data["Dt_VitEIn"] = calculate_Dt_VitEIn(
        complete_feed_data["Fd_VitEIn"]
        )
    diet_data["Dt_CholineIn"] = calculate_Dt_CholineIn(
        complete_feed_data["Fd_CholineIn"]
        )
    diet_data["Dt_BiotinIn"] = calculate_Dt_BiotinIn(
        complete_feed_data["Fd_BiotinIn"]
        )
    diet_data["Dt_NiacinIn"] = calculate_Dt_NiacinIn(
        complete_feed_data["Fd_NiacinIn"]
        )
    diet_data["Dt_B_CaroteneIn"] = calculate_Dt_B_CaroteneIn(
        complete_feed_data["Fd_B_CaroteneIn"]
        )
    diet_data["Dt_Ca"] = calculate_Dt_Ca(diet_data["Dt_CaIn"], Dt_DMIn)
    diet_data["Dt_P"] = calculate_Dt_P(diet_data["Dt_PIn"], Dt_DMIn)
    diet_data["Dt_Pinorg"] = calculate_Dt_Pinorg(
        diet_data["Dt_PinorgIn"], Dt_DMIn
        )
    diet_data["Dt_Porg"] = calculate_Dt_Porg(diet_data["Dt_PorgIn"], Dt_DMIn)
    diet_data["Dt_Na"] = calculate_Dt_Na(diet_data["Dt_NaIn"], Dt_DMIn)
    diet_data["Dt_Mg"] = calculate_Dt_Mg(diet_data["Dt_MgIn"], Dt_DMIn)
    diet_data["Dt_K"] = calculate_Dt_K(diet_data["Dt_KIn"], Dt_DMIn)
    diet_data["Dt_Cl"] = calculate_Dt_Cl(diet_data["Dt_ClIn"], Dt_DMIn)
    diet_data["Dt_S"] = calculate_Dt_S(diet_data["Dt_SIn"], Dt_DMIn)
    diet_data["Dt_Co"] = calculate_Dt_Co(diet_data["Dt_CoIn"], Dt_DMIn)
    diet_data["Dt_Cr"] = calculate_Dt_Cr(diet_data["Dt_CrIn"], Dt_DMIn)
    diet_data["Dt_Cu"] = calculate_Dt_Cu(diet_data["Dt_CuIn"], Dt_DMIn)
    diet_data["Dt_Fe"] = calculate_Dt_Fe(diet_data["Dt_FeIn"], Dt_DMIn)
    diet_data["Dt_I"] = calculate_Dt_I(diet_data["Dt_IIn"], Dt_DMIn)
    diet_data["Dt_Mn"] = calculate_Dt_Mn(diet_data["Dt_MnIn"], Dt_DMIn)
    diet_data["Dt_Mo"] = calculate_Dt_Mo(diet_data["Dt_MoIn"], Dt_DMIn)
    diet_data["Dt_Se"] = calculate_Dt_Se(diet_data["Dt_SeIn"], Dt_DMIn)
    diet_data["Dt_Zn"] = calculate_Dt_Zn(diet_data["Dt_ZnIn"], Dt_DMIn)
    diet_data["Dt_VitA"] = calculate_Dt_VitA(diet_data["Dt_VitAIn"], Dt_DMIn)
    diet_data["Dt_VitD"] = calculate_Dt_VitD(diet_data["Dt_VitDIn"], Dt_DMIn)
    diet_data["Dt_VitE"] = calculate_Dt_VitE(diet_data["Dt_VitEIn"], Dt_DMIn)
    diet_data["Dt_Choline"] = calculate_Dt_Choline(
        diet_data["Dt_CholineIn"], Dt_DMIn
        )
    diet_data["Dt_Biotin"] = calculate_Dt_Biotin(
        diet_data["Dt_BiotinIn"], Dt_DMIn
        )
    diet_data["Dt_Niacin"] = calculate_Dt_Niacin(
        diet_data["Dt_NiacinIn"], Dt_DMIn
        )
    diet_data["Dt_B_Carotene"] = calculate_Dt_B_Carotene(
        diet_data["Dt_B_CaroteneIn"], Dt_DMIn
        )
    diet_data["Dt_IdArgRUPIn"] = calculate_Dt_IdArgRUPIn(
        complete_feed_data["Fd_IdArgRUPIn"]
        )
    diet_data["Dt_IdHisRUPIn"] = calculate_Dt_IdHisRUPIn(
        complete_feed_data["Fd_IdHisRUPIn"]
        )
    diet_data["Dt_IdIleRUPIn"] = calculate_Dt_IdIleRUPIn(
        complete_feed_data["Fd_IdIleRUPIn"]
        )
    diet_data["Dt_IdLeuRUPIn"] = calculate_Dt_IdLeuRUPIn(
        complete_feed_data["Fd_IdLeuRUPIn"]
        )
    diet_data["Dt_IdLysRUPIn"] = calculate_Dt_IdLysRUPIn(
        complete_feed_data["Fd_IdLysRUPIn"]
        )
    diet_data["Dt_IdMetRUPIn"] = calculate_Dt_IdMetRUPIn(
        complete_feed_data["Fd_IdMetRUPIn"]
        )
    diet_data["Dt_IdPheRUPIn"] = calculate_Dt_IdPheRUPIn(
        complete_feed_data["Fd_IdPheRUPIn"]
        )
    diet_data["Dt_IdThrRUPIn"] = calculate_Dt_IdThrRUPIn(
        complete_feed_data["Fd_IdThrRUPIn"]
        )
    diet_data["Dt_IdTrpRUPIn"] = calculate_Dt_IdTrpRUPIn(
        complete_feed_data["Fd_IdTrpRUPIn"]
        )
    diet_data["Dt_IdValRUPIn"] = calculate_Dt_IdValRUPIn(
        complete_feed_data["Fd_IdValRUPIn"]
        )
    diet_data['Dt_RDPIn'] = calculate_Dt_RDPIn(
        diet_data['Dt_CPIn'], diet_data['Dt_RUPIn']
        )
    # NOTE TT_dc values are calculated here as they are required for calculating 
    # Dt_ values. The could be calculated outside of this function but then 
    # diet_data would need to be calculated in 2 steps
    diet_data['TT_dcNDF_Base'] = calculate_TT_dcNDF_Base(
        diet_data['Dt_DigNDFIn_Base'], diet_data['Dt_NDFIn']
        )
    diet_data['TT_dcNDF'] = calculate_TT_dcNDF(
        diet_data['TT_dcNDF_Base'], diet_data['Dt_StIn'], Dt_DMIn, An_DMIn_BW
        )
    diet_data['TT_dcSt_Base'] = calculate_TT_dcSt_Base(
        diet_data['Dt_DigStIn_Base'], diet_data['Dt_StIn']
        )
    diet_data['TT_dcSt'] = calculate_TT_dcSt(
        diet_data['TT_dcSt_Base'], An_DMIn_BW
        )
    diet_data['Dt_DigNDFIn'] = calculate_Dt_DigNDFIn(
        diet_data['TT_dcNDF'], diet_data['Dt_NDFIn']
        )
    diet_data['Dt_DigStIn'] = calculate_Dt_DigStIn(
        diet_data['Dt_StIn'], diet_data['TT_dcSt']
        )

    diet_data['Dt_DigrOMaIn'] = calculate_Dt_DigrOMaIn(
        diet_data['Dt_DigrOMtIn'], Fe_rOMend
        )
    diet_data['Dt_dcCP_ClfDry'] = calculate_Dt_dcCP_ClfDry(
        An_StatePhys, diet_data['Dt_DMIn_ClfLiq']
        )
    diet_data['Dt_DENDFIn'] = calculate_Dt_DENDFIn(
        diet_data['Dt_DigNDFIn'], coeff_dict
        )
    diet_data['Dt_DEStIn'] = calculate_Dt_DEStIn(
        diet_data['Dt_DigStIn'], coeff_dict
        )
    diet_data['Dt_DErOMIn'] = calculate_Dt_DErOMIn(
        diet_data['Dt_DigrOMaIn'], coeff_dict
        )
    diet_data['Dt_DENPNCPIn'] = calculate_Dt_DENPNCPIn(
        diet_data['Dt_NPNCPIn'], coeff_dict
        )
    diet_data['Dt_DEFAIn'] = calculate_Dt_DEFAIn(
        diet_data['Dt_DigFAIn'], coeff_dict
        )
    diet_data['Dt_DMIn_ClfStrt'] = calculate_Dt_DMIn_ClfStrt(
        An_BW, diet_data['Dt_MEIn_ClfLiq'], diet_data['Dt_DMIn_ClfLiq'],
        diet_data['Dt_DMIn_ClfFor'], An_AgeDryFdStart, Env_TempCurr, DMIn_eqn,
        Dt_DMIn, coeff_dict
        )
    diet_data["Dt_DigC120In"] = calculate_Dt_DigC120In(
        complete_feed_data["Fd_DigC120In"]
        )
    diet_data["Dt_DigC140In"] = calculate_Dt_DigC140In(
        complete_feed_data["Fd_DigC140In"]
        )
    diet_data["Dt_DigC160In"] = calculate_Dt_DigC160In(
        complete_feed_data["Fd_DigC160In"]
        )
    diet_data["Dt_DigC161In"] = calculate_Dt_DigC161In(
        complete_feed_data["Fd_DigC161In"]
        )
    diet_data["Dt_DigC180In"] = calculate_Dt_DigC180In(
        complete_feed_data["Fd_DigC180In"]
        )
    diet_data["Dt_DigC181tIn"] = calculate_Dt_DigC181tIn(
        complete_feed_data["Fd_DigC181tIn"]
        )
    diet_data["Dt_DigC181cIn"] = calculate_Dt_DigC181cIn(
        complete_feed_data["Fd_DigC181cIn"]
        )
    diet_data["Dt_DigC182In"] = calculate_Dt_DigC182In(
        complete_feed_data["Fd_DigC182In"]
        )
    diet_data["Dt_DigC183In"] = calculate_Dt_DigC183In(
        complete_feed_data["Fd_DigC183In"]
        )
    diet_data["Dt_DigOtherFAIn"] = calculate_Dt_DigOtherFAIn(
        complete_feed_data["Fd_DigOtherFAIn"]
        )
    diet_data["Abs_CaIn"] = calculate_Abs_CaIn(complete_feed_data["Fd_absCaIn"])
    diet_data["Abs_PIn"] = calculate_Abs_PIn(complete_feed_data["Fd_absPIn"])
    diet_data["Abs_NaIn"] = calculate_Abs_NaIn(complete_feed_data["Fd_absNaIn"])
    diet_data["Abs_KIn"] = calculate_Abs_KIn(complete_feed_data["Fd_absKIn"])
    diet_data["Abs_ClIn"] = calculate_Abs_ClIn(complete_feed_data["Fd_absClIn"])
    diet_data["Abs_CoIn"] = calculate_Abs_CoIn(complete_feed_data["Fd_absCoIn"])
    diet_data["Abs_CuIn"] = calculate_Abs_CuIn(complete_feed_data["Fd_absCuIn"])
    diet_data["Abs_FeIn"] = calculate_Abs_FeIn(complete_feed_data["Fd_absFeIn"])
    diet_data["Abs_MnIn"] = calculate_Abs_MnIn(complete_feed_data["Fd_absMnIn"])
    diet_data["Abs_ZnIn"] = calculate_Abs_ZnIn(complete_feed_data["Fd_absZnIn"])
    diet_data['Dt_acMg'] = calculate_Dt_acMg(
        An_StatePhys, diet_data['Dt_K'], diet_data['Dt_MgIn_min'], 
        diet_data['Dt_MgIn']
        )
    diet_data['Abs_MgIn'] = calculate_Abs_MgIn(
        diet_data['Dt_acMg'], diet_data['Dt_MgIn']
        )
    diet_data['Dt_DigWSCIn'] = calculate_Dt_DigWSCIn(
        complete_feed_data['Fd_DigWSCIn']
        )
    diet_data['Dt_DigSt'] = calculate_Dt_DigSt(diet_data['Dt_DigStIn'], Dt_DMIn)
    diet_data['Dt_DigWSC'] = calculate_Dt_DigWSC(
        diet_data['Dt_DigWSCIn'], Dt_DMIn
        )
    diet_data['Dt_DigrOMa'] = calculate_Dt_DigrOMa(
        diet_data['Dt_DigrOMaIn'], Dt_DMIn
        )
    diet_data['Dt_DigrOMa_Dt'] = calculate_Dt_DigrOMa_Dt(
        diet_data['Dt_rOM'], coeff_dict
        )
    diet_data['Dt_DigrOMt'] = calculate_Dt_DigrOMt(
        diet_data['Dt_DigrOMtIn'], Dt_DMIn
        )
    diet_data['Dt_DigNDFnfIn'] = calculate_Dt_DigNDFnfIn(
        diet_data['TT_dcNDF'], diet_data['Dt_NDFnfIn']
        )
    diet_data['Dt_DigNDF'] = calculate_Dt_DigNDF(
        diet_data['Dt_DigNDFIn'], Dt_DMIn
        )
    diet_data['Dt_DigNDFnf'] = calculate_Dt_DigNDFnf(
        diet_data['Dt_DigNDFnfIn'], Dt_DMIn
        )
    diet_data['Dt_idcRUP'] = calculate_Dt_idcRUP(
        diet_data['Dt_idRUPIn'], diet_data['Dt_RUPIn']
        )
    diet_data['Dt_Fe_RUPout'] = calculate_Dt_Fe_RUPout(
        complete_feed_data['Fd_Fe_RUPout']
        )
    diet_data['Dt_RDTPIn'] = calculate_Dt_RDTPIn(
        diet_data['Dt_RDPIn'], diet_data['Dt_NPNCPIn'], coeff_dict
        )
    diet_data['Dt_RDP'] = calculate_Dt_RDP(diet_data['Dt_RDPIn'], Dt_DMIn)
    diet_data['Dt_RDP_CP'] = calculate_Dt_RDP_CP(
        diet_data['Dt_RDP'], diet_data['Dt_CP']
        )
    diet_data['Dt_DigUFAIn'] = calculate_Dt_DigUFAIn(
        diet_data['Dt_DigC161In'], diet_data['Dt_DigC181tIn'], 
        diet_data['Dt_DigC181cIn'], diet_data['Dt_DigC182In'], 
        diet_data['Dt_DigC183In']
        )
    diet_data['Dt_DigMUFAIn'] = calculate_Dt_DigMUFAIn(
        diet_data['Dt_DigC161In'], diet_data['Dt_DigC181tIn'],
        diet_data['Dt_DigC181cIn']
        )
    diet_data['Dt_DigPUFAIn'] = calculate_Dt_DigPUFAIn(
        diet_data['Dt_DigC182In'], diet_data['Dt_DigC183In']
        )
    diet_data['Dt_DigSatFAIn'] = calculate_Dt_DigSatFAIn(
        diet_data['Dt_DigFAIn'], diet_data['Dt_DigUFAIn']
        )
    diet_data['Dt_DigFA'] = calculate_Dt_DigFA(diet_data['Dt_DigFAIn'], Dt_DMIn)
    diet_data["Dt_DigFA_FA"] = calculate_Dt_DigFA_FA(
        diet_data["Dt_DigFAIn"], diet_data["Dt_FAIn"]
        )
    diet_data["Dt_DigC120_FA"] = calculate_Dt_DigC120_FA(
        diet_data["Dt_DigC120In"], diet_data["Dt_FAIn"]
        )
    diet_data["Dt_DigC140_FA"] = calculate_Dt_DigC140_FA(
        diet_data["Dt_DigC140In"], diet_data["Dt_FAIn"]
        )
    diet_data["Dt_DigC160_FA"] = calculate_Dt_DigC160_FA(
        diet_data["Dt_DigC160In"], diet_data["Dt_FAIn"]
        )
    diet_data["Dt_DigC161_FA"] = calculate_Dt_DigC161_FA(
        diet_data["Dt_DigC161In"], diet_data["Dt_FAIn"]
        )
    diet_data["Dt_DigC180_FA"] = calculate_Dt_DigC180_FA(
        diet_data["Dt_DigC180In"], diet_data["Dt_FAIn"]
        )
    diet_data["Dt_DigC181t_FA"] = calculate_Dt_DigC181t_FA(
        diet_data["Dt_DigC181tIn"], diet_data["Dt_FAIn"]
        )
    diet_data["Dt_DigC181c_FA"] = calculate_Dt_DigC181c_FA(
        diet_data["Dt_DigC181cIn"], diet_data["Dt_FAIn"]
        )
    diet_data["Dt_DigC182_FA"] = calculate_Dt_DigC182_FA(
        diet_data["Dt_DigC182In"], diet_data["Dt_FAIn"]
        )
    diet_data["Dt_DigC183_FA"] = calculate_Dt_DigC183_FA(
        diet_data["Dt_DigC183In"], diet_data["Dt_FAIn"]
        )
    diet_data["Dt_DigUFA_FA"] = calculate_Dt_DigUFA_FA(
        diet_data["Dt_DigUFAIn"], diet_data["Dt_FAIn"]
        )
    diet_data["Dt_DigMUFA_FA"] = calculate_Dt_DigMUFA_FA(
        diet_data["Dt_DigMUFAIn"], diet_data["Dt_FAIn"]
        )
    diet_data["Dt_DigPUFA_FA"] = calculate_Dt_DigPUFA_FA(
        diet_data["Dt_DigPUFAIn"], diet_data["Dt_FAIn"]
        )
    diet_data["Dt_DigSatFA_FA"] = calculate_Dt_DigSatFA_FA(
        diet_data["Dt_DigSatFAIn"], diet_data["Dt_FAIn"]
        )
    diet_data["Dt_DigOtherFA_FA"] = calculate_Dt_DigOtherFA_FA(
        diet_data["Dt_DigOtherFAIn"], diet_data["Dt_FAIn"]
        )
    diet_data['TT_dcDtFA'] = calculate_TT_dcDtFA(
        diet_data['Dt_DigFAIn'], diet_data['Dt_FAIn']
        )
    diet_data['Dt_GE'] = calculate_Dt_GE(diet_data['Dt_GEIn'], Dt_DMIn)
    diet_data['Dt_GasE_IPCC2'] = calculate_Dt_GasE_IPCC2(diet_data['Dt_GEIn'])
    diet_data['Dt_GasEOut'] = calculate_Dt_GasEOut(
        An_StatePhys, Monensin_eqn, Dt_DMIn, diet_data['Dt_FA'], 
        diet_data['Dt_DigNDF'], diet_data['Dt_GEIn'], diet_data['Dt_NDF']
        )
    diet_data["DtArgRUP_DtArg"] = calculate_DtArgRUP_DtArg(
        diet_data["Dt_ArgRUPIn"], diet_data["Dt_ArgIn"]
        )
    diet_data["DtHisRUP_DtHis"] = calculate_DtHisRUP_DtHis(
        diet_data["Dt_HisRUPIn"], diet_data["Dt_HisIn"]
        )
    diet_data["DtIleRUP_DtIle"] = calculate_DtIleRUP_DtIle(
        diet_data["Dt_IleRUPIn"], diet_data["Dt_IleIn"]
        )
    diet_data["DtLeuRUP_DtLeu"] = calculate_DtLeuRUP_DtLeu(
        diet_data["Dt_LeuRUPIn"], diet_data["Dt_LeuIn"]
        )
    diet_data["DtLysRUP_DtLys"] = calculate_DtLysRUP_DtLys(
        diet_data["Dt_LysRUPIn"], diet_data["Dt_LysIn"]
        )
    diet_data["DtMetRUP_DtMet"] = calculate_DtMetRUP_DtMet(
        diet_data["Dt_MetRUPIn"], diet_data["Dt_MetIn"]
        )
    diet_data["DtPheRUP_DtPhe"] = calculate_DtPheRUP_DtPhe(
        diet_data["Dt_PheRUPIn"], diet_data["Dt_PheIn"]
        )
    diet_data["DtThrRUP_DtThr"] = calculate_DtThrRUP_DtThr(
        diet_data["Dt_ThrRUPIn"], diet_data["Dt_ThrIn"]
        )
    diet_data["DtTrpRUP_DtTrp"] = calculate_DtTrpRUP_DtTrp(
        diet_data["Dt_TrpRUPIn"], diet_data["Dt_TrpIn"]
        )
    diet_data["DtValRUP_DtVal"] = calculate_DtValRUP_DtVal(
        diet_data["Dt_ValRUPIn"], diet_data["Dt_ValIn"]
        )
    diet_data["Dt_DE_ClfLiq"] = calculate_Dt_DE_ClfLiq(
        diet_data["Dt_DEIn_ClfLiq"], diet_data["Dt_DMIn_ClfLiq"]
        )
    diet_data['Dt_DigCPaIn'] = calculate_Dt_DigCPaIn(
        diet_data['Dt_CPIn'], Fe_CP
        )
    diet_data['Dt_DigCPtIn'] = calculate_Dt_DigCPtIn(
        An_StatePhys, diet_data['Dt_DigCPaIn'], Fe_CPend,
        diet_data['Dt_RDPIn'], diet_data['Dt_idRUPIn']
        )
    diet_data['Dt_DigTPaIn'] = calculate_Dt_DigTPaIn(
        diet_data['Dt_RDTPIn'], Fe_MiTP,
        diet_data['Dt_idRUPIn'], Fe_NPend
        )
    diet_data['Dt_DigTPtIn'] = calculate_Dt_DigTPtIn(
        diet_data['Dt_RDTPIn'], diet_data['Dt_idRUPIn']
        )
    diet_data['Dt_DigCPa'] = calculate_Dt_DigCPa(
        diet_data['Dt_DigCPaIn'], Dt_DMIn
        )
    diet_data['TT_dcDtCPa'] = calculate_TT_dcDtCPa(
        diet_data['Dt_DigCPaIn'], diet_data['Dt_CPIn']
        )
    diet_data['Dt_DigCPt'] = calculate_Dt_DigCPt(
        diet_data['Dt_DigCPtIn'], Dt_DMIn
        )
    diet_data['Dt_DigTPt'] = calculate_Dt_DigTPt(
        diet_data['Dt_DigTPtIn'], Dt_DMIn
        )
    diet_data['TT_dcDtCPt'] = calculate_TT_dcDtCPt(
        diet_data['Dt_DigCPtIn'], diet_data['Dt_CPIn']
        )
    diet_data['Dt_MPIn'] = calculate_Dt_MPIn(
        An_StatePhys, diet_data['Dt_CPIn'], Fe_CP, Fe_CPend,
        diet_data['Dt_idRUPIn'], Du_idMiTP
        )
    diet_data['Dt_MP'] = calculate_Dt_MP(
        diet_data['Dt_MPIn'], Dt_DMIn
        )
    diet_data['Dt_DECPIn'] = calculate_Dt_DECPIn(
        diet_data['Dt_DigCPaIn'], coeff_dict
        )
    diet_data['Dt_DETPIn'] = calculate_Dt_DETPIn(
        diet_data['Dt_DECPIn'], diet_data['Dt_DENPNCPIn'],
        coeff_dict
        )
    diet_data['Dt_DEIn'] = calculate_Dt_DEIn(
        An_StatePhys, diet_data['Dt_DENDFIn'],
        diet_data['Dt_DEStIn'], diet_data['Dt_DErOMIn'],
        diet_data['Dt_DETPIn'], diet_data['Dt_DENPNCPIn'],
        diet_data['Dt_DEFAIn'], diet_data['Dt_DMIn_ClfLiq'],
        diet_data['Dt_DEIn_base_ClfLiq'],
        diet_data['Dt_DEIn_base_ClfDry'], Monensin_eqn
        )
    diet_data["Dt_IdArgIn"] = calculate_Dt_IdArgIn(
        Du_IdAAMic["Arg"], diet_data["Dt_IdArgRUPIn"]
        )
    diet_data["Dt_IdHisIn"] = calculate_Dt_IdHisIn(
        Du_IdAAMic["His"], diet_data["Dt_IdHisRUPIn"]
        )
    diet_data["Dt_IdIleIn"] = calculate_Dt_IdIleIn(
        Du_IdAAMic["Ile"], diet_data["Dt_IdIleRUPIn"]
        )
    diet_data["Dt_IdLeuIn"] = calculate_Dt_IdLeuIn(
        Du_IdAAMic["Leu"], diet_data["Dt_IdLeuRUPIn"]
        )
    diet_data["Dt_IdLysIn"] = calculate_Dt_IdLysIn(
        Du_IdAAMic["Lys"], diet_data["Dt_IdLysRUPIn"]
        )
    diet_data["Dt_IdMetIn"] = calculate_Dt_IdMetIn(
        Du_IdAAMic["Met"], diet_data["Dt_IdMetRUPIn"]
        )
    diet_data["Dt_IdPheIn"] = calculate_Dt_IdPheIn(
        Du_IdAAMic["Phe"], diet_data["Dt_IdPheRUPIn"]
        )
    diet_data["Dt_IdThrIn"] = calculate_Dt_IdThrIn(
        Du_IdAAMic["Thr"], diet_data["Dt_IdThrRUPIn"]
        )
    diet_data["Dt_IdTrpIn"] = calculate_Dt_IdTrpIn(
        Du_IdAAMic["Trp"], diet_data["Dt_IdTrpRUPIn"]
        )
    diet_data["Dt_IdValIn"] = calculate_Dt_IdValIn(
        Du_IdAAMic["Val"], diet_data["Dt_IdValRUPIn"]
        )
    diet_data['Dt_DigOMaIn'] = calculate_Dt_DigOMaIn(
        diet_data['Dt_DigNDFIn'], diet_data['Dt_DigStIn'],
        diet_data['Dt_DigFAIn'], diet_data['Dt_DigrOMaIn'],
        diet_data['Dt_DigCPaIn']
        )
    diet_data['Dt_DigOMtIn'] = calculate_Dt_DigOMtIn(
        diet_data['Dt_DigNDFIn'], diet_data['Dt_DigStIn'],
        diet_data['Dt_DigFAIn'], diet_data['Dt_DigrOMtIn'],
        diet_data['Dt_DigCPtIn']
        )
    diet_data['Dt_DigOMa'] = calculate_Dt_DigOMa(
        diet_data['Dt_DigOMaIn'], Dt_DMIn
        )
    diet_data['Dt_DigOMt'] = calculate_Dt_DigOMt(
        diet_data['Dt_DigOMtIn'], Dt_DMIn
        )
    diet_data['Dt_DE'] = calculate_Dt_DE(
        diet_data['Dt_DEIn'], Dt_DMIn
        )
    diet_data['Dt_TDN'] = calculate_Dt_TDN(
        diet_data['Dt_DigSt'], diet_data['Dt_DigNDF'],
        diet_data['Dt_DigrOMa'], diet_data['Dt_DigCPa'],
        diet_data['Dt_DigFA']
        )
    diet_data['Dt_TDNIn'] = calculate_Dt_TDNIn(
        diet_data['Dt_TDN'], Dt_DMIn
        )
    return diet_data
