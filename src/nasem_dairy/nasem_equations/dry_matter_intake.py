"""Functions for calculating for dry matter intake (DMI).

Includes equations for animals of different physiological states. Some equations
will use diet information in the prediction.
"""

import math
from typing import Union

import pandas as pd

import nasem_dairy.nasem_equations.nutrient_intakes as diet


# Precalculation for heifer DMI predicitons
def calculate_Kb_LateGest_DMIn(Dt_NDF: float) -> float:
    """
    Calculate the ______________ for predicting dry matter intake (DMI) in late gestation for heifers.

    Parameters
    ----------
    Dt_NDF : float
        The neutral detergent fiber (NDF) as a percentage.

    Returns
    -------
    float
        The precalculation factor (Kb_LateGest_DMIn) for heifer DMI predictions.

    Notes
    -----
    - This function is used as a _____ for predicting heifer dry matter intake (DMI).
    - The input Dt_NDF is constrained to the range of 30 to 55% of dry matter (DM).
    - Kb_LateGest_DMIn is calculated as -(0.365 - 0.0028 * Dt_NDF_drylim), where Dt_NDF_drylim is the constrained value.

    Examples
    --------
    Calculate the precalculation factor for heifer DMI predictions in late gestation:

    ```{python}
    import nasem_dairy as nd
    nd.calculate_Kb_LateGest_DMIn(Dt_NDF=40)
    ```
    """
    Dt_NDF_drylim = Dt_NDF  # Dt_NDF_drylim only used in this calculation
    if Dt_NDF < 30:  # constrain Dt_NDF to the range of 30 to 55% of DM
        Dt_NDF_drylim = 30
    if Dt_NDF > 55:
        Dt_NDF_drylim = 55

    Kb_LateGest_DMIn = -(0.365 - 0.0028 * Dt_NDF_drylim)
    return Kb_LateGest_DMIn


# Precalculation for heifer DMI predicitons
def calculate_An_PrePartWklim(An_PrePartWk: float) -> Union[int, float]:
    # Late Gestation eqn. from Hayirli et al., 2003) for dry cows and heifers
    if An_PrePartWk < -3:  # constrain to the interval 0 to -3.
        An_PrePartWklim = -3
    elif An_PrePartWk > 0:
        An_PrePartWklim = 0
    else:
        An_PrePartWklim = An_PrePartWk
    return An_PrePartWklim


# Need when DMIn_eqn == 2,3,4,5,6,7,10
def calculate_Dt_DMIn_BW_LateGest_i(
    An_PrePartWklim: Union[int, float], 
    Kb_LateGest_DMIn: float,
    coeff_dict: dict
) -> float:
    """
    Examples
    --------
    ```
    coeff_dict = {"Ka_LateGest_DMIn": 1.47, "Kc_LateGest_DMIn": -0.035}
    
    calculate_Dt_DMIn_BW_LateGest_i(
        An_PrePartWklim = 6.0, Kb_LateGest_DMIn = 0.05, coeff_dict = coeff_dict
    )
    ```
    """
    # Late gestation individual animal prediction, % of BW.  Use to assess for a
    # specific day for a given animal
    Dt_DMIn_BW_LateGest_i = (coeff_dict['Ka_LateGest_DMIn'] + 
                             Kb_LateGest_DMIn * An_PrePartWklim + 
                             coeff_dict['Kc_LateGest_DMIn'] * An_PrePartWklim**2)
    return Dt_DMIn_BW_LateGest_i


# Need when DMIn_eqn == 10,12,13,14,15,16,17
def calculate_Dt_DMIn_BW_LateGest_p(
    An_PrePartWkDurat: Union[int, float], 
    Kb_LateGest_DMIn: float,
    coeff_dict: dict
) -> float:
    """
    Examples
    --------
    ```
    coeff_dict = {
        "Ka_LateGest_DMIn": 1.47, "Kc_LateGest_DMIn": -0.035
    }
    
    calculate_Dt_DMIn_BW_LateGest_p(
        An_PrePartWkDurat = 6.0, Kb_LateGest_DMIn = 0.05, 
        coeff_dict = coeff_dict
    )
    ```
    """
    # Late gestation Group/Pen mean DMI/BW for an interval of 0 to 
    # PrePart_WkDurat. Assumes pen steady state and PrePart_wk = pen mean
    Dt_DMIn_BW_LateGest_p = (coeff_dict['Ka_LateGest_DMIn'] * An_PrePartWkDurat
                             + Kb_LateGest_DMIn / 2 * An_PrePartWkDurat**2 +
                             coeff_dict['Kc_LateGest_DMIn'] / 3 *
                             An_PrePartWkDurat**3) / An_PrePartWkDurat
    return Dt_DMIn_BW_LateGest_p


# Need when DMIn_eqn == 2,3,4,5,6,7
def calculate_Dt_DMIn_Heif_LateGestInd(
    An_BW: float, 
    Dt_DMIn_BW_LateGest_i: float
) -> float:
    # Individual intake for the specified day prepart or the pen mean intake 
    # for the interval, 0 to PrePart_WkDurat
    Dt_DMIn_Heif_LateGestInd = 0.88 * An_BW * Dt_DMIn_BW_LateGest_i / 100 
    # Individual animal
    return Dt_DMIn_Heif_LateGestInd


# Need when DMIn_eqn == 12,13,14,15,16,17
def calculate_Dt_DMIn_Heif_LateGestPen(
    An_BW: float, 
    Dt_DMIn_BW_LateGest_p: float
) -> float:
    Dt_DMIn_Heif_LateGestPen = 0.88 * An_BW * Dt_DMIn_BW_LateGest_p / 100  
    # Pen mean
    return Dt_DMIn_Heif_LateGestPen


# Need when DMIn_eqn == 5,7,15,17
def calculate_Dt_NDFdev_DMI(An_BW: float, Dt_NDF: float) -> float:
    # NRC 2020 Heifer Eqns. from the Transition Ch., Line 316
    Dt_NDFdev_DMI = Dt_NDF - (23.11 + 0.07968 * An_BW - 0.00006252 * An_BW**2)
    return Dt_NDFdev_DMI


# DMIn_eqn == 2, 12
def calculate_Dt_DMIn_Heif_NRCa(An_BW: float, An_BW_mature: float) -> float:
    '''
    Test docs for calcualte_Dt_DMIn_Heif_NRCa
    '''
    # Animal factors only, eqn. 2-3 NRC
    Dt_DMIn_Heif_NRCa = (0.022 * An_BW_mature * 
                         (1 - math.exp(-1.54 * An_BW / An_BW_mature)))
    return Dt_DMIn_Heif_NRCa


# DMIn_eqn == 3, 13
def calculate_Dt_DMIn_Heif_NRCad(
    An_BW: float, 
    An_BW_mature: float, 
    Dt_NDF: float
) -> float:
    # Anim & diet factors, eqn 2-4 NRC
    Dt_DMIn_Heif_NRCad = ((0.0226 * An_BW_mature * 
                           (1 - math.exp(-1.47 * An_BW / An_BW_mature))) - 
                           (0.082 * (Dt_NDF - (23.1 + 56 * An_BW / An_BW_mature) 
                                     - 30.6 * (An_BW / An_BW_mature)**2)))
    return Dt_DMIn_Heif_NRCad


# DMIn_eqn == 4, 14
def calculate_Dt_DMIn_Heif_H1(An_BW: float) -> float:
    # Holstein, animal factors only
    Dt_DMIn_Heif_H1 = 15.36 * (1 - math.exp(-0.0022 * An_BW))
    return Dt_DMIn_Heif_H1


# DMIn_eqn == 5, 15
def calculate_Dt_DMIn_Heif_H2(An_BW: float, Dt_NDFdev_DMI: float) -> float:
    # Holstein, animal factors and NDF
    Dt_DMIn_Heif_H2 = (15.79 * (1 - math.exp(-0.0021 * An_BW)) - 
                       (0.082 * Dt_NDFdev_DMI))
    return Dt_DMIn_Heif_H2


# DMIn_eqn == 6, 16
def calculate_Dt_DMIn_Heif_HJ1(An_BW: float) -> float:
    """
    _summary_

    Parameters
    ----------
    An_BW : _type_
        _description_

    Returns
    -------
    _type_
        _description_
    """
    #Holstein x Jersey, animal factors only
    Dt_DMIn_Heif_HJ1 = 12.91 * (1 - math.exp(-0.00295 * An_BW))
    return Dt_DMIn_Heif_HJ1


# DMIn_eqn == 7, 17
def calculate_Dt_DMIn_Heif_HJ2(An_BW:float, Dt_NDFdev_DMI: float) -> float:
    """
    Calculate the predicted dry matter intake (DMI) for Holstein x Jersey crossbred heifers
    considering animal factors and neutral detergent fiber (NDF).

    Parameters
    ----------
    An_BW : float
        The body weight of the heifer in kg.
    Dt_NDFdev_DMI : float
        The neutral detergent fiber (NDF) as a percentage

    Returns
    -------
    float
        The predicted dry matter intake (DMI) in kg

    Notes
    -----
    - See equation number ___ in the Nutrient Requirements of Dairy Cattle book (NASEM, 2021)
    - See line number 317 in the original R code published with the book's software
    - This function is equated when equation_selection for DMIn_eqn is equal to 7 and 17


    Examples
    -------

    ```{python}
    import nasem_dairy as nd
    nd.calculate_Dt_DMIn_Heif_HJ2(
        An_BW = 700,
        Dt_NDFdev_DMI = 14
        )
    ```
   
    """
    #Holstein x Jersey, animal factors and NDF
    Dt_DMIn_Heif_HJ2 = (13.48 * (1 - math.exp(-0.0027 * An_BW)) - 
                        (0.082 * Dt_NDFdev_DMI))
    return Dt_DMIn_Heif_HJ2


# DMIn_eqn == 8
def calculate_Dt_DMIn_Lact1(
    An_BW: float, 
    An_BCS: float, 
    An_LactDay: int,
    An_Parity_rl: int, 
    Trg_NEmilkOut: float
) -> float:
    """
    Calculate the predicted dry matter intake (DMI) for lactating dairy cows using equation 8.

    Parameters
    ----------
    An_BW : float
        The body weight of the lactating cow in kg.
    An_BCS : float
        The body condition score (BCS) of the lactating cow.
    An_LactDay : int
        The lactation day of the cow.
    An_Parity_rl : int
        The parity of the cow (number of times calved).
    Trg_NEmilkOut : float
        Net energy of milk production in Mcal.

    Returns
    -------
    float
        The predicted dry matter intake (DMI) in kg.

    Notes
    -----
    - See equation number 2-1 in the Nutrient Requirements of Dairy Cattle book (NASEM, 2021).
    - See lines 387-92 in the original R code published with the book's software.
    - Trg_NEmilkOut is calculated as Trg_NEmilk_Milk * Trg_MilkProd (see line 386).
    - This function is associated with DMIn_eqn equal to 8.

    Examples
    --------
    Calculate the dry matter intake for a lactating dairy cow:

    ```python
    import nasem_dairy as nd
    nd.calculate_Dt_DMIn_Lact1(
        An_BW=600,
        An_BCS=3.5,
        An_LactDay=120,
        An_Parity_rl=2,
        Trg_NEmilkOut=0.65
    )
    ```

    Returns
    -------
    float
        The predicted dry matter intake (DMI) for the given parameters.
    """
    Dt_DMIn_Lact1 = ((3.7 + 5.7 * (An_Parity_rl - 1) + 0.305 * Trg_NEmilkOut + 
                      0.022 * An_BW + 
                      (-0.689 - 1.87 * (An_Parity_rl - 1)) * An_BCS) * 
                      (1 - (0.212 + 0.136 * (An_Parity_rl - 1)) * 
                       math.exp(-0.053 * An_LactDay))) # Line 390
    return Dt_DMIn_Lact1

# DMIn_eqn == 9 
def calculate_Dt_DMIn_Lact2(
    Dt_ForNDF: float, 
    Dt_ADF: float, 
    Dt_NDF: float, 
    Dt_ForDNDF48_ForNDF: float,
    Trg_MilkProd: float
) -> float:
    Dt_DMIn_Lact2 = (12.0 - 0.107 * Dt_ForNDF + 8.17 * Dt_ADF / Dt_NDF + 
                     0.0253 * Dt_ForDNDF48_ForNDF - 
                     0.328 * (Dt_ADF / Dt_NDF - 0.602) * 
                     (Dt_ForDNDF48_ForNDF - 48.3) + 
                     0.225 * Trg_MilkProd + 0.00390 * 
                     (Dt_ForDNDF48_ForNDF - 48.3) * (Trg_MilkProd - 33.1))
    return Dt_DMIn_Lact2

# DMIn_eqn == 10
def calculate_Dt_DMIn_DryCow1_FarOff(
    An_BW: float, 
    Dt_DMIn_BW_LateGest_i: float
) -> float:
    Dt_DMIn_DryCow1_FarOff = An_BW * Dt_DMIn_BW_LateGest_i / 100
    return Dt_DMIn_DryCow1_FarOff


# DMIn_eqn == 10
def calculate_Dt_DMIn_DryCow1_Close(
    An_BW: float, 
    Dt_DMIn_BW_LateGest_p: float
) -> float:
    Dt_DMIn_DryCow1_Close = An_BW * Dt_DMIn_BW_LateGest_p / 100
    return Dt_DMIn_DryCow1_Close


def calculate_Dt_DMIn_DryCow_AdjGest(
    An_GestDay: int,
    An_GestLength: int,
    An_BW: float
) -> float:
    # from Hayirli et al., 2003 JDS
    if (An_GestDay - An_GestLength) < -21:
        Dt_DMIn_DryCow_AdjGest = 0
    else:
        Dt_DMIn_DryCow_AdjGest = (
            An_BW * (-0.756 * math.exp(0.154 * (An_GestDay - An_GestLength))) 
            / 100
            )
    return Dt_DMIn_DryCow_AdjGest


# DMIn_eqn == 11
def calculate_Dt_DMIn_DryCow2(
    An_BW: float, 
    Dt_DMIn_DryCow_AdjGest: float
) -> float:
    Dt_DMIn_DryCow2 = An_BW * 1.979 / 100 + Dt_DMIn_DryCow_AdjGest
    return Dt_DMIn_DryCow2


def calculate_Dt_DMIn_Calf1(
    Dt_DMIn_ClfLiq: float, 
    Dt_DMIn_ClfStrt: float,
    Dt_DMIn_ClfFor: float
) -> float:
    """
    Dt_DMIn_Calf1: Calf DMI with predicted starter intake, kg/d
    Liquid feed + calfd starter + forage intake
    """
    Dt_DMIn_Calf1 = Dt_DMIn_ClfLiq + Dt_DMIn_ClfStrt + Dt_DMIn_ClfFor
    # DMI w/ predicted starter, Line 308
    return Dt_DMIn_Calf1


def calculate_Dt_DMIn(
    DMIn_eqn: int,
    Trg_Dt_DMIn: float,
    An_StatePhys: str,
    An_BW: float,
    An_BW_mature: float,
    An_BCS: int,
    An_LactDay: int,
    An_Parity_rl: int, 
    Trg_MilkProd: float,
    An_GestDay: int,
    An_GestLength: int,
    An_AgeDryFdStart: int,
    Env_TempCurr: float,
    An_PrePartWk: float,
    Trg_NEmilkOut: float,
    An_PrePartWklim: float,
    An_PrePartWkDurat: float,
    Fd_NDF: pd.Series,
    Fd_DMInp: pd.Series,
    Fd_ADF: pd.Series,
    Fd_ForNDF: pd.Series,
    Fd_Conc: pd.Series,
    Fd_DNDF48_input: pd.Series,
    Trg_Fd_DMIn: pd.Series,
    Fd_Category: pd.Series,
    Fd_CP: pd.Series,
    Fd_FA: pd.Series,
    Fd_Ash: pd.Series,
    Fd_St: pd.Series,
    coeff_dict: dict
) -> float:   
    Dt_NDF = (Fd_NDF * Fd_DMInp).sum()
    Dt_ADF = (Fd_ADF * Fd_DMInp).sum()
    Dt_ForNDF = (Fd_ForNDF * Fd_DMInp).sum()
    Fd_DNDF48 = diet.calculate_Fd_DNDF48(
        Fd_Conc, Fd_DNDF48_input
        )
    Dt_ForDNDF48 = diet.calculate_Dt_ForDNDF48(
        Fd_DMInp, Fd_Conc, Fd_NDF, 
        Fd_DNDF48
        )
    Dt_ForDNDF48_ForNDF = diet.calculate_Dt_ForDNDF48_ForNDF(
        Dt_ForDNDF48, Dt_ForNDF
        )
    Kb_LateGest_DMIn = calculate_Kb_LateGest_DMIn(Dt_NDF)

    if DMIn_eqn == 0:
        Dt_DMIn = Trg_Dt_DMIn

    elif DMIn_eqn == 1:
        Fd_DMIn_ClfLiq = diet.calculate_Fd_DMIn_ClfLiq(
            An_StatePhys, Trg_Fd_DMIn, Fd_Category
        )
        Fd_DMIn_ClfFor = diet.calculate_Fd_DMIn_ClfFor(
            Trg_Dt_DMIn, Fd_Conc, Fd_DMInp
        )
        Fd_GE = diet.calculate_Fd_GE(
            An_StatePhys, Fd_Category, Fd_CP, 
            Fd_FA, Fd_Ash, Fd_St,
            Fd_NDF, coeff_dict
        )
        Fd_DE_ClfLiq = diet.calculate_Fd_DE_ClfLiq(
            An_StatePhys, Fd_Category, Fd_GE
        )
        Fd_ME_ClfLiq = diet.calculate_Fd_ME_ClfLiq(
            An_StatePhys, Fd_Category, Fd_DE_ClfLiq
        )
        Dt_MEIn_ClfLiq = diet.calculate_Dt_MEIn_ClfLiq(
            Fd_ME_ClfLiq, Fd_DMIn_ClfLiq
        )
        Dt_DMIn_ClfLiq = Fd_DMIn_ClfLiq.sum()
        Dt_DMIn_ClfFor = Fd_DMIn_ClfFor.sum()
        Dt_DMIn_ClfStrt = diet.calculate_Dt_DMIn_ClfStrt(
            An_BW, Dt_MEIn_ClfLiq, Dt_DMIn_ClfLiq, Dt_DMIn_ClfFor,
            An_AgeDryFdStart, Env_TempCurr, DMIn_eqn, Trg_Dt_DMIn, coeff_dict
        )
        Dt_DMIn = calculate_Dt_DMIn_Calf1(
            Dt_DMIn_ClfLiq, Dt_DMIn_ClfStrt, Dt_DMIn_ClfFor
            )
    
    # Individual Heifer DMI Predictions
    elif DMIn_eqn in [2, 3, 4, 5, 6, 7]:
        Dt_DMIn_BW_LateGest_i = calculate_Dt_DMIn_BW_LateGest_i(
            An_PrePartWklim, Kb_LateGest_DMIn, coeff_dict
            )
        Dt_DMIn_Heif_LateGestInd = calculate_Dt_DMIn_Heif_LateGestInd(
            An_BW, Dt_DMIn_BW_LateGest_i
            )
        
        if DMIn_eqn == 2:
            if An_PrePartWk > An_PrePartWkDurat:
                Dt_DMIn = min(
                    calculate_Dt_DMIn_Heif_NRCa(An_BW, An_BW_mature),
                    Dt_DMIn_Heif_LateGestInd)
            else:
                Dt_DMIn = calculate_Dt_DMIn_Heif_NRCa(An_BW, An_BW_mature)
        
        if DMIn_eqn == 3:
            if An_PrePartWk > An_PrePartWkDurat:
                Dt_DMIn = min(
                    calculate_Dt_DMIn_Heif_NRCad(An_BW, An_BW_mature, Dt_NDF),
                    Dt_DMIn_Heif_LateGestInd)
            else:
                Dt_DMIn = calculate_Dt_DMIn_Heif_NRCad(
                    An_BW, An_BW_mature, Dt_NDF
                    )

        if DMIn_eqn == 4:
            if An_PrePartWk > An_PrePartWkDurat:
                Dt_DMIn = min(
                    calculate_Dt_DMIn_Heif_H1(An_BW),
                    Dt_DMIn_Heif_LateGestInd)
            else:
                Dt_DMIn = calculate_Dt_DMIn_Heif_H1(An_BW)

        if DMIn_eqn == 5:
            Dt_NDFdev_DMI = calculate_Dt_NDFdev_DMI(An_BW, Dt_NDF)
            if An_PrePartWk > An_PrePartWkDurat:
                Dt_DMIn = min(
                    calculate_Dt_DMIn_Heif_H2(An_BW, Dt_NDFdev_DMI),
                    Dt_DMIn_Heif_LateGestInd)
            else:
                Dt_DMIn = calculate_Dt_DMIn_Heif_H2(An_BW, Dt_NDFdev_DMI)

        if DMIn_eqn == 6:
            if An_PrePartWk > An_PrePartWkDurat:
                Dt_DMIn = min(
                    calculate_Dt_DMIn_Heif_HJ1(An_BW),
                    Dt_DMIn_Heif_LateGestInd)
            else:
                Dt_DMIn = calculate_Dt_DMIn_Heif_HJ1(An_BW)
        
        if DMIn_eqn == 7:
            Dt_NDFdev_DMI = calculate_Dt_NDFdev_DMI(An_BW, Dt_NDF)
            if An_PrePartWk > An_PrePartWkDurat:
                Dt_DMIn = min(
                    calculate_Dt_DMIn_Heif_HJ2(An_BW, Dt_NDFdev_DMI),
                    Dt_DMIn_Heif_LateGestInd)
            else:
                Dt_DMIn = calculate_Dt_DMIn_Heif_HJ2(An_BW, Dt_NDFdev_DMI)

    elif DMIn_eqn == 8:
        Dt_DMIn = calculate_Dt_DMIn_Lact1(
            An_BW, An_BCS, An_LactDay, An_Parity_rl, Trg_NEmilkOut
            )

    elif DMIn_eqn == 9:
        Dt_DMIn = calculate_Dt_DMIn_Lact2(
            Dt_ForNDF, Dt_ADF, Dt_NDF, Dt_ForDNDF48_ForNDF, Trg_MilkProd
        )

    elif DMIn_eqn == 10:
        Dt_DMIn_BW_LateGest_i = calculate_Dt_DMIn_BW_LateGest_i(
            An_PrePartWklim, Kb_LateGest_DMIn, coeff_dict
            )
        Dt_DMIn_BW_LateGest_p = calculate_Dt_DMIn_BW_LateGest_p(
            An_PrePartWkDurat, Kb_LateGest_DMIn, coeff_dict
            )
        if An_PrePartWk > An_PrePartWkDurat:
            Dt_DMIn = min(
                calculate_Dt_DMIn_DryCow1_FarOff(An_BW, Dt_DMIn_BW_LateGest_i),
                calculate_Dt_DMIn_DryCow1_Close(An_BW, Dt_DMIn_BW_LateGest_p))
        else:
            Dt_DMIn = calculate_Dt_DMIn_DryCow1_FarOff(
                An_BW, Dt_DMIn_BW_LateGest_i
                )

    elif DMIn_eqn == 11:
        Dt_DMIn_DryCow_AdjGest = calculate_Dt_DMIn_DryCow_AdjGest(
            An_GestDay, An_GestLength, An_BW
        )
        Dt_DMIn = calculate_Dt_DMIn_DryCow2(
            An_BW, Dt_DMIn_DryCow_AdjGest
            )
    
    elif DMIn_eqn in [12, 13, 14, 15, 16, 17]:
        Dt_DMIn_BW_LateGest_p = calculate_Dt_DMIn_BW_LateGest_p(
            An_PrePartWkDurat, Kb_LateGest_DMIn, coeff_dict
            )
        Dt_DMIn_Heif_LateGestPen = calculate_Dt_DMIn_Heif_LateGestPen(
            An_BW, Dt_DMIn_BW_LateGest_p
            )
        
        if DMIn_eqn == 12:
            if An_PrePartWk > An_PrePartWkDurat:
                Dt_DMIn = min(
                    calculate_Dt_DMIn_Heif_NRCa(An_BW, An_BW_mature),
                    Dt_DMIn_Heif_LateGestPen)
            else:
                Dt_DMIn = calculate_Dt_DMIn_Heif_NRCa(An_BW, An_BW_mature)
        
        if DMIn_eqn == 13:
            if An_PrePartWk > An_PrePartWkDurat:
                Dt_DMIn = min(
                    calculate_Dt_DMIn_Heif_NRCad(An_BW, An_BW_mature, Dt_NDF),
                    Dt_DMIn_Heif_LateGestPen)
            else:
                Dt_DMIn = calculate_Dt_DMIn_Heif_NRCad(
                    An_BW, An_BW_mature, Dt_NDF
                    )
        
        if DMIn_eqn == 14:
            if An_PrePartWk > An_PrePartWkDurat:
                Dt_DMIn = min(
                    calculate_Dt_DMIn_Heif_H1(An_BW),
                    Dt_DMIn_Heif_LateGestPen)
            else:
                Dt_DMIn = calculate_Dt_DMIn_Heif_H1(An_BW)
        
        if DMIn_eqn == 15:
            Dt_NDFdev_DMI = calculate_Dt_NDFdev_DMI(An_BW, Dt_NDF)
            if An_PrePartWk > An_PrePartWkDurat:
                Dt_DMIn = min(
                    calculate_Dt_DMIn_Heif_H2(An_BW, Dt_NDFdev_DMI),
                    Dt_DMIn_Heif_LateGestPen)
            else:
                Dt_DMIn = calculate_Dt_DMIn_Heif_H2(An_BW, Dt_NDFdev_DMI)
    
        if DMIn_eqn == 16:
            if An_PrePartWk > An_PrePartWkDurat:
                Dt_DMIn = min(
                    calculate_Dt_DMIn_Heif_HJ1(An_BW),
                    Dt_DMIn_Heif_LateGestPen)
            else:
                Dt_DMIn = calculate_Dt_DMIn_Heif_HJ1(An_BW)
        
        if DMIn_eqn == 17:
            Dt_NDFdev_DMI = calculate_Dt_NDFdev_DMI(An_BW, Dt_NDF)
            if An_PrePartWk > An_PrePartWkDurat:
                Dt_DMIn = min(
                    calculate_Dt_DMIn_Heif_HJ2(An_BW, Dt_NDFdev_DMI),
                    Dt_DMIn_Heif_LateGestPen)
            else:
                Dt_DMIn = calculate_Dt_DMIn_Heif_HJ2(An_BW, Dt_NDFdev_DMI)
  
    else:
        raise ValueError(
            f"Invalid value for DMIn_eqn: {DMIn_eqn}. Must be between 0 and 17."
            )
    
    return Dt_DMIn
    