# dev_rumen_equations

def calculate_Rum_dcNDF(Dt_DMIn, Dt_NDFIn, Dt_StIn, Dt_CPIn, Dt_ADFIn, Dt_ForWet):
    Rum_dcNDF = -31.9 + 0.721 * Dt_NDFIn / Dt_DMIn * 100 - \
        0.247 * Dt_StIn / Dt_DMIn * 100 + \
        6.63 * Dt_CPIn / Dt_DMIn * 100 - \
        0.211 * (Dt_CPIn / Dt_DMIn * 100) ** 2 - \
        0.387 * Dt_ADFIn / Dt_DMIn / (Dt_NDFIn / Dt_DMIn) * 100 - \
        0.121 * Dt_ForWet + 1.51 * Dt_DMIn

    if Rum_dcNDF < 0.1 or Rum_dcNDF is None:                                                # Line 984
        Rum_dcNDF = 0.1
    return Rum_dcNDF


def calculate_Rum_dcSt(Dt_DMIn, Dt_ForNDF, Dt_StIn, Dt_ForWet):
    Rum_dcSt = 70.6 - 1.45*(Dt_DMIn) + 0.424*Dt_ForNDF + \
        1.39*(Dt_StIn)/(Dt_DMIn)*100 - \
        0.0219*((Dt_StIn)/(Dt_DMIn)*100)**2 - \
        0.154*Dt_ForWet

    if Rum_dcSt < 0.1:                                                                      # Line 992
        Rum_dcSt = 0.1
    elif Rum_dcSt > 100:                                                                    # Line 993
        Rum_dcSt = 100
    return Rum_dcSt


def calculate_Rum_DigNDFIn(Rum_dcNDF, Dt_NDFIn):
    Rum_DigNDFIn = Rum_dcNDF / 100 * Dt_NDFIn
    return Rum_DigNDFIn


def calculate_Rum_DigStIn(Rum_dcSt, Dt_StIn):
    # Line 998
    Rum_DigStIn = Rum_dcSt / 100 * Dt_StIn
    return Rum_DigStIn
