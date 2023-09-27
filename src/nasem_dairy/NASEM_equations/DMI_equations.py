def dry_cow_equations(DMIn_eqn, An_BW, An_PrePartWk, An_GestDay, An_GestLength, Dt_NDF, coeff_dict):
    req_coeffs = ['Ka_LateGest_DMIn', 'Kc_LateGest_DMIn']
    nd.check_coeffs_in_coeff_dict(coeff_dict, req_coeffs)

    Dt_NDF_drylim = Dt_NDF
    #constrain Dt_NDF to the range of 30 to 55% of DM
    if Dt_NDF < 30:
        Dt_NDF_drylim = 30
    elif Dt_NDF > 55:
        Dt_NDF_drylim = 55

    #Late Gestation eqn. from Hayirli et al., 2003) for dry cows and heifers
    if An_PrePartWk < -3:
        An_PrePartWklim = -3
    elif An_PrePartWk > 0:
        An_PrePartWklim = 0
    else:
        An_PrePartWklim = An_PrePartWk
    An_PrePartWkDurat = An_PrePartWklim * 2

    Kb_LateGest_DMIn = -(0.365 - 0.0028 * Dt_NDF_drylim)
    Dt_DMIn_BW_LateGest_i = coeff_dict['Ka_LateGest_DMIn'] + Kb_LateGest_DMIn * An_PrePartWklim + coeff_dict['Kc_LateGest_DMIn'] * An_PrePartWklim**2
    Dt_DMIn_BW_LateGest_p = (coeff_dict['Ka_LateGest_DMIn'] * An_PrePartWkDurat + Kb_LateGest_DMIn / 2 * An_PrePartWkDurat**2 + coeff_dict['Kc_LateGest_DMIn'] / 3 * An_PrePartWkDurat**3) / An_PrePartWkDurat
    
    Dt_DMIn_DryCow1_FarOff = An_BW * Dt_DMIn_BW_LateGest_i / 100
    Dt_DMIn_DryCow1_Close = An_BW * Dt_DMIn_BW_LateGest_p / 100

    if An_PrePartWk > An_PrePartWkDurat:
        Dt_DMIn_DryCow1 = min(Dt_DMIn_DryCow1_FarOff, Dt_DMIn_DryCow1_Close)
    else:
        Dt_DMIn_DryCow1 = Dt_DMIn_DryCow1_FarOff

    ## from Hayirli et al., 2003 JDS
    if (An_GestDay - An_GestLength) < -21:
        Dt_DMIn_DryCow_AdjGest = 0
    else:
        Dt_DMIn_DryCow_AdjGest = An_BW * (-0.756 * math.exp(0.154 * (An_GestDay - An_GestLength))) / 100
    
    Dt_DMIn_DryCow2 = An_BW * 1.979 / 100 + Dt_DMIn_DryCow_AdjGest

    if DMIn_eqn == 10:
        return_DMI = Dt_DMIn_DryCow1
    elif DMIn_eqn == 11:
        return_DMI = Dt_DMIn_DryCow2

    return return_DMI


def heifer_growth(DMIn_eqn, Dt_NDF, An_BW, An_BW_mature, An_PrePartWk, coeff_dict):
# Lines 317-379
    req_coeffs = ['Ka_LateGest_DMIn', 'Kc_LateGest_DMIn']     
    nd.check_coeffs_in_coeff_dict(coeff_dict, req_coeffs)

#NRC 2020 Heifer Eqns. from the Transition Ch.
    Dt_NDFdev_DMI = Dt_NDF - (23.11 + 0.07968 * An_BW - 0.00006252 * An_BW**2)      # Line 316
#Animal factors only, eqn. 2-3 NRC
    Dt_DMIn_Heif_NRCa = 0.022 * An_BW_mature * (1 - math.exp(-1.54 * An_BW / An_BW_mature))
#Holstein, animal factors only
    Dt_DMIn_Heif_H1 = 15.36 * (1 - math.exp(-0.0022 * An_BW))
#Holstein x Jersey, animal factors only
    Dt_DMIn_Heif_HJ1 = 12.91 * (1 - math.exp(-0.00295 * An_BW))
#Anim & diet factors, eqn 2-4 NRC
    Dt_DMIn_Heif_NRCad = (0.0226 * An_BW_mature * (1 - math.exp(-1.47 * An_BW / An_BW_mature))) - (0.082 * (Dt_NDF - (23.1 + 56 * An_BW / An_BW_mature) - 30.6 *(An_BW / An_BW_mature)**2))
#Holstein, animal factors and NDF
    Dt_DMIn_Heif_H2 = 15.79 * (1 - math.exp(-0.0021 * An_BW)) - (0.082 * Dt_NDFdev_DMI)
#Holstein x Jersey, animal factors and NDF
    Dt_DMIn_Heif_HJ2 = 13.48 * (1 - math.exp(-0.0027 * An_BW)) - (0.082 * Dt_NDFdev_DMI)

#Late Gestation eqn. from Hayirli et al., 2003) for dry cows and heifers
    if An_PrePartWk < -3:       #constrain to the interval 0 to -3.
        An_PrePartWklim = -3
    else:
        An_PrePartWklim = An_PrePartWk

    if An_PrePartWk > 0:
        An_PrePartWklim = 0

#the estimated length of time in the close-up pen
    An_PrePartWkDurat = An_PrePartWklim * 2  

    Dt_NDF_drylim = Dt_NDF

    if Dt_NDF < 30:    #constrain Dt_NDF to the range of 30 to 55% of DM
        Dt_NDF_drylim = 30
    if Dt_NDF > 55:
        Dt_NDF_drylim = 55

    Kb_LateGest_DMIn = -(0.365 - 0.0028 * Dt_NDF_drylim)

#These 2 values are called by other functions, must be calculated everytime
#Late gestation individual animal prediction, % of BW.  Use to assess for a specific day for a given animal
    Dt_DMIn_BW_LateGest_i = coeff_dict['Ka_LateGest_DMIn'] + Kb_LateGest_DMIn * An_PrePartWklim + coeff_dict['Kc_LateGest_DMIn'] * An_PrePartWklim**2
#Late gestation Group/Pen mean DMI/BW for an interval of 0 to PrePart_WkDurat.  Assumes pen steady state and PrePart_wk = pen mean
    Dt_DMIn_BW_LateGest_p = (coeff_dict['Ka_LateGest_DMIn'] * An_PrePartWkDurat + Kb_LateGest_DMIn / 2 * An_PrePartWkDurat**2 + coeff_dict['Kc_LateGest_DMIn'] / 3 * An_PrePartWkDurat**3) / An_PrePartWkDurat

#Individual intake for the specified day prepart or the pen mean intake for the interval, 0 to PrePart_WkDurat
    Dt_DMIn_Heif_LateGestInd = 0.88 * An_BW * Dt_DMIn_BW_LateGest_i / 100 #Individual animal
    Dt_DMIn_Heif_LateGestPen = 0.88 * An_BW * Dt_DMIn_BW_LateGest_p / 100 #Pen mean

#Switch to the group transition eqn. when less than An_PrePartWkDurat and predicted transition DMI is less than far off DMI
#These equations generally are discontinuous at -3 weeks, as Dt_DMIn_xxx is greater than Dt_DMIn_xxx_LateGest at -3.  
#Should calculate the decline using the far off DMIn as a reference point, or calculate the discontinuity at the
#point of transition and adjust the close-up DMIn by addition of the gap.

#NRC 2020 pen intakes
    if An_PrePartWk > An_PrePartWkDurat:
        Dt_DMIn_Heif_NRCap = min(Dt_DMIn_Heif_NRCa, Dt_DMIn_Heif_LateGestPen)
        Dt_DMIn_Heif_NRCadp = min(Dt_DMIn_Heif_NRCad, Dt_DMIn_Heif_LateGestPen)
        Dt_DMIn_Heif_H1p =  min(Dt_DMIn_Heif_H1, Dt_DMIn_Heif_LateGestPen)
        Dt_DMIn_Heif_HJ1p = min(Dt_DMIn_Heif_HJ1, Dt_DMIn_Heif_LateGestPen)
        Dt_DMIn_Heif_H2p = min(Dt_DMIn_Heif_H2, Dt_DMIn_Heif_LateGestPen)
        Dt_DMIn_Heif_HJ2p = min(Dt_DMIn_Heif_HJ2, Dt_DMIn_Heif_LateGestPen)
    else:
        Dt_DMIn_Heif_NRCap = Dt_DMIn_Heif_NRCa
        Dt_DMIn_Heif_NRCadp = Dt_DMIn_Heif_NRCad
        Dt_DMIn_Heif_H1p = Dt_DMIn_Heif_H1
        Dt_DMIn_Heif_HJ1p = Dt_DMIn_Heif_HJ1
        Dt_DMIn_Heif_H2p = Dt_DMIn_Heif_H2
        Dt_DMIn_Heif_HJ2p = Dt_DMIn_Heif_HJ2

#NRC 2020 individual animal intakes
    if An_PrePartWk > An_PrePartWkDurat:
        Dt_DMIn_Heif_NRCai = min(Dt_DMIn_Heif_NRCa, Dt_DMIn_Heif_LateGestInd)
        Dt_DMIn_Heif_NRCadi =  min(Dt_DMIn_Heif_NRCad, Dt_DMIn_Heif_LateGestInd)
        Dt_DMIn_Heif_H1i = min(Dt_DMIn_Heif_H1, Dt_DMIn_Heif_LateGestInd)
        Dt_DMIn_Heif_HJ1i = min(Dt_DMIn_Heif_HJ1, Dt_DMIn_Heif_LateGestInd)
        Dt_DMIn_Heif_H2i = min(Dt_DMIn_Heif_H2, Dt_DMIn_Heif_LateGestInd)
        Dt_DMIn_Heif_HJ2i = min(Dt_DMIn_Heif_HJ2,Dt_DMIn_Heif_LateGestInd)
    else:
        Dt_DMIn_Heif_NRCai = Dt_DMIn_Heif_NRCa
        Dt_DMIn_Heif_NRCadi = Dt_DMIn_Heif_NRCad
        Dt_DMIn_Heif_H1i = Dt_DMIn_Heif_H1
        Dt_DMIn_Heif_HJ1i = Dt_DMIn_Heif_HJ1
        Dt_DMIn_Heif_H2i = Dt_DMIn_Heif_H2
        Dt_DMIn_Heif_HJ2i = Dt_DMIn_Heif_HJ2
    
    # Select the user specified DMI to return
    # This selection could be moved higher up in the function
    if DMIn_eqn == 2:
        return_DMI = Dt_DMIn_Heif_NRCai
    elif DMIn_eqn == 3:
        return_DMI = Dt_DMIn_Heif_NRCadi
    elif DMIn_eqn == 4:
        return_DMI = Dt_DMIn_Heif_H1i
    elif DMIn_eqn == 5:
        return_DMI = Dt_DMIn_Heif_H2i
    elif DMIn_eqn == 6:
        return_DMI = Dt_DMIn_Heif_HJ1i
    elif DMIn_eqn == 7:
        return_DMI = Dt_DMIn_Heif_HJ2i
    elif DMIn_eqn == 12:
        return_DMI = Dt_DMIn_Heif_NRCap
    elif DMIn_eqn == 13:
        return_DMI = Dt_DMIn_Heif_NRCadp
    elif DMIn_eqn == 14:
        return_DMI = Dt_DMIn_Heif_H1p
    elif DMIn_eqn == 15:
        return_DMI = Dt_DMIn_Heif_H2p
    elif DMIn_eqn == 16:
        return_DMI = Dt_DMIn_Heif_HJ1p
    elif DMIn_eqn == 17:
        return_DMI = Dt_DMIn_Heif_HJ2p

    return return_DMI


