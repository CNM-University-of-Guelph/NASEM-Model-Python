# dev_DMI_equations
# This file contains all the calculations for dry matter intake (DMI)
# Calculations are in the order coresponding to their DMIn_eqn value

from nasem_dairy.ration_balancer.ration_balancer_functions import check_coeffs_in_coeff_dict
import math

# Precalculation for heifer DMI predicitons


def calculate_Kb_LateGest_DMIn(Dt_NDF):
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
def calculate_An_PrePartWklim(An_PrePartWk):
    # Late Gestation eqn. from Hayirli et al., 2003) for dry cows and heifers
    if An_PrePartWk < -3:  # constrain to the interval 0 to -3.
        An_PrePartWklim = -3
    elif An_PrePartWk > 0:
        An_PrePartWklim = 0
    else:
        An_PrePartWklim = An_PrePartWk

    return An_PrePartWklim 


# Need when DMIn_eqn == 2,3,4,5,6,7,10
def calculate_Dt_DMIn_BW_LateGest_i(An_PrePartWklim, Kb_LateGest_DMIn, coeff_dict):
    req_coeffs = ['Ka_LateGest_DMIn', 'Kc_LateGest_DMIn']
    check_coeffs_in_coeff_dict(coeff_dict, req_coeffs)
    # Late gestation individual animal prediction, % of BW.  Use to assess for a specific day for a given animal
    Dt_DMIn_BW_LateGest_i = coeff_dict['Ka_LateGest_DMIn'] + Kb_LateGest_DMIn * \
        An_PrePartWklim + coeff_dict['Kc_LateGest_DMIn'] * An_PrePartWklim**2
    return Dt_DMIn_BW_LateGest_i


# Need when DMIn_eqn == 10,12,13,14,15,16,17
def calculate_Dt_DMIn_BW_LateGest_p(An_PrePartWkDurat, Kb_LateGest_DMIn, coeff_dict):
    req_coeffs = ['Ka_LateGest_DMIn', 'Kc_LateGest_DMIn']
    check_coeffs_in_coeff_dict(coeff_dict, req_coeffs)
    # Late gestation Group/Pen mean DMI/BW for an interval of 0 to PrePart_WkDurat.  Assumes pen steady state and PrePart_wk = pen mean
    Dt_DMIn_BW_LateGest_p = (coeff_dict['Ka_LateGest_DMIn'] * An_PrePartWkDurat + Kb_LateGest_DMIn / 2 *
                             An_PrePartWkDurat**2 + coeff_dict['Kc_LateGest_DMIn'] / 3 * An_PrePartWkDurat**3) / An_PrePartWkDurat
    return Dt_DMIn_BW_LateGest_p


# Need when DMIn_eqn == 2,3,4,5,6,7
def calculate_Dt_DMIn_Heif_LateGestInd(An_BW, Dt_DMIn_BW_LateGest_i):
    # Individual intake for the specified day prepart or the pen mean intake for the interval, 0 to PrePart_WkDurat
    Dt_DMIn_Heif_LateGestInd = 0.88 * An_BW * \
        Dt_DMIn_BW_LateGest_i / 100  # Individual animal
    return Dt_DMIn_Heif_LateGestInd


# Need when DMIn_eqn == 12,13,14,15,16,17
def calculate_Dt_DMIn_Heif_LateGestPen(An_BW, Dt_DMIn_BW_LateGest_p):
    Dt_DMIn_Heif_LateGestPen = 0.88 * An_BW * \
        Dt_DMIn_BW_LateGest_p / 100  # Pen mean
    return Dt_DMIn_Heif_LateGestPen


# Need when DMIn_eqn == 5,7,15,17
def calculate_Dt_NDFdev_DMI(An_BW, Dt_NDF):
    # NRC 2020 Heifer Eqns. from the Transition Ch.
    Dt_NDFdev_DMI = Dt_NDF - \
        (23.11 + 0.07968 * An_BW - 0.00006252 * An_BW**2)      # Line 316
    return Dt_NDFdev_DMI


# DMIn_eqn == 2, 12
def calculate_Dt_DMIn_Heif_NRCa(An_BW, An_BW_mature):
    '''
    Test docs for calcualte_Dt_DMIn_Heif_NRCa
    '''
    #Animal factors only, eqn. 2-3 NRC
    Dt_DMIn_Heif_NRCa = 0.022 * An_BW_mature * (1 - math.exp(-1.54 * An_BW / An_BW_mature))

    return Dt_DMIn_Heif_NRCa


# DMIn_eqn == 3, 13
def calculate_Dt_DMIn_Heif_NRCad(An_BW, An_BW_mature, Dt_NDF):
    # Anim & diet factors, eqn 2-4 NRC
    Dt_DMIn_Heif_NRCad = (0.0226 * An_BW_mature * (1 - math.exp(-1.47 * An_BW / An_BW_mature))) - (
        0.082 * (Dt_NDF - (23.1 + 56 * An_BW / An_BW_mature) - 30.6 * (An_BW / An_BW_mature)**2))
    return Dt_DMIn_Heif_NRCad


# DMIn_eqn == 4, 14
def calculate_Dt_DMIn_Heif_H1(An_BW):
    # Holstein, animal factors only
    Dt_DMIn_Heif_H1 = 15.36 * (1 - math.exp(-0.0022 * An_BW))
    return Dt_DMIn_Heif_H1


# DMIn_eqn == 5, 15
def calculate_Dt_DMIn_Heif_H2(An_BW, Dt_NDFdev_DMI):
    # Holstein, animal factors and NDF
    Dt_DMIn_Heif_H2 = 15.79 * \
        (1 - math.exp(-0.0021 * An_BW)) - (0.082 * Dt_NDFdev_DMI)
    return Dt_DMIn_Heif_H2


# DMIn_eqn == 6, 16
def calculate_Dt_DMIn_Heif_HJ1(An_BW):
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
def calculate_Dt_DMIn_Heif_HJ2(An_BW, Dt_NDFdev_DMI):
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
    Dt_DMIn_Heif_HJ2 = 13.48 * (1 - math.exp(-0.0027 * An_BW)) - (0.082 * Dt_NDFdev_DMI)
    return Dt_DMIn_Heif_HJ2


# DMIn_eqn == 8
def calculate_Dt_DMIn_Lact1(Trg_MilkProd,
                            An_BW,
                            An_BCS,
                            An_LactDay,
                            An_Parity_rl,
                            Trg_NEmilk_Milk):
    """
    Animal based dry matter intake (DMI) prediction for lactating cows 

    This function predicts the DMI using animal factors only. This is equation 2-1 in the NASEM 8 textbook. In the model
    this prediction can be can be selected by setting DMI_pred to 0 in the 'input.txt'. In :py:func:`NASEM_model` Dt_DMIn_Lact1
    will be returned to the animal_input dictionary with the key 'DMI'.

    Parameters:
        An_Parity_rl (Number): Animal Parity where 1 = Primiparous and 2 = Multiparous.
        Trg_MilkProd (Number): Animal Milk Production in kg/day.
        An_BW (Number): Animal Body Weight in kg.
        An_BCS (Number): Body condition score, from 1-5
        An_LactDay (Number): Day of Lactation.

    Returns:
        Dt_DMIn_Lact1 (Number): Dry matter intake, kg/d
    """
    Trg_NEmilkOut = Trg_NEmilk_Milk * Trg_MilkProd  # Line 386
    # Trg_NEmilkOut is only used for this DMI calculation
    Dt_DMIn_Lact1 = (
        3.7 +
        5.7 * (An_Parity_rl - 1) +
        0.305 * Trg_NEmilkOut +
        0.022 * An_BW +
        (-0.689 - 1.87 * (An_Parity_rl - 1)) * An_BCS
    ) * (
        1 - (0.212 + 0.136 * (An_Parity_rl - 1)) *
        math.exp(-0.053 * An_LactDay)
    )  # Line 389
    return Dt_DMIn_Lact1
    
# DMIn_eqn == 8
def calculate_Dt_DMIn_Lact1(Trg_MilkProd, 
                            An_BW, 
                            An_BCS, 
                            An_LactDay, 
                            An_Parity_rl, 
                            Trg_NEmilk_Milk):
    """
    Calculate the predicted dry matter intake (DMI) for lactating dairy cows using equation 8.

    Parameters
    ----------
    Trg_MilkProd : float
        Target milk production in kg per day.
    An_BW : float
        The body weight of the lactating cow in kg.
    An_BCS : float
        The body condition score (BCS) of the lactating cow.
    An_LactDay : int
        The lactation day of the cow.
    An_Parity_rl : int
        The parity of the cow (number of times calved).
    Trg_NEmilk_Milk : float
        Net energy of milk production in Mcal per kg of milk.

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
        Trg_MilkProd=30,
        An_BW=600,
        An_BCS=3.5,
        An_LactDay=120,
        An_Parity_rl=2,
        Trg_NEmilk_Milk=0.65
    )
    ```

    Returns
    -------
    float
        The predicted dry matter intake (DMI) for the given parameters.
    """
    Trg_NEmilkOut = Trg_NEmilk_Milk * Trg_MilkProd  # Line 387
    # Trg_NEmilkOut is only used for this DMI calculation
    Dt_DMIn_Lact1 = (
    3.7 +
    5.7 * (An_Parity_rl - 1) +
    0.305 * Trg_NEmilkOut +
    0.022 * An_BW +
    (-0.689 - 1.87 * (An_Parity_rl - 1)) * An_BCS
    ) * (
    1 - (0.212 + 0.136 * (An_Parity_rl - 1)) * math.exp(-0.053 * An_LactDay)
    )  # Line 390    

    return Dt_DMIn_Lact1



# DMIn_eqn == 10
def calculate_Dt_DMIn_DryCow1_FarOff(An_BW, Dt_DMIn_BW_LateGest_i):
    Dt_DMIn_DryCow1_FarOff = An_BW * Dt_DMIn_BW_LateGest_i / 100
    return Dt_DMIn_DryCow1_FarOff


# DMIn_eqn == 10
def calculate_Dt_DMIn_DryCow1_Close(An_BW, Dt_DMIn_BW_LateGest_p):
    Dt_DMIn_DryCow1_Close = An_BW * Dt_DMIn_BW_LateGest_p / 100
    return Dt_DMIn_DryCow1_Close


# DMIn_eqn == 11
def calculate_Dt_DMIn_DryCow2(An_BW, An_GestDay, An_GestLength):
    # from Hayirli et al., 2003 JDS
    if (An_GestDay - An_GestLength) < -21:
        Dt_DMIn_DryCow_AdjGest = 0
    else:
        Dt_DMIn_DryCow_AdjGest = An_BW * \
            (-0.756 * math.exp(0.154 * (An_GestDay - An_GestLength))) / 100

    Dt_DMIn_DryCow2 = An_BW * 1.979 / 100 + Dt_DMIn_DryCow_AdjGest
    return Dt_DMIn_DryCow2
