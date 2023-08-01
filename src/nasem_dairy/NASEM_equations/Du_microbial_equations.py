from nasem_dairy.ration_balancer.ration_balancer_functions import check_coeffs_in_coeff_dict

def calculate_Du_MiN_g(Dt_NDFIn, Dt_DMIn, Dt_StIn, Dt_CPIn, Dt_ADFIn, Dt_ForWet, Dt_RUPIn, Dt_ForNDFIn, Dt_RDPIn, coeff_dict):
    """
    Predicts microbial nitrogen (N) synthesis for use in amino acid supply equations

    This function takes nutrient intakes from the diet and uses them to predict microbial crude protein (CP) synthesis. There are
    three equations for predictiong microbial N synthesis. This function calls :py:func:`calculate_Du_MiN_NRC2021_g` as this is the
    default.
     
    :py:func:`calculate_Du_MiN_VTln_g` and :py:func:`calculate_Du_MiN_VTnln_g` are the other microbial N predictions. They can also be called
    ny this function if users want to comapre these predictions before slecting which to use in future calculations.

    Parameters:
        Dt_NDFIn (Number): Neutral detergent fiber (NDF) intake in kg/d
        Dt_DMIn (Number): Dry matter intake, kg/d
        Dt_StIn (Number): Starch intake in kg/dk
        Dt_CPIn (Number): Crude protein (CP) intake in kg/d
        Dt_ADFIn (Number): Acid detergent fiber (ADF) intake in kg/d
        Dt_ForWet (Number): Wet forage intake in kg/d
        Dt_RUPIn (Number): Rumen undegradable protein (RUP) in kg/d
        Dt_ForNDFIn (Number): Forage NDF intake in kg/d
        Dt_RDPIn (Number): Rumen degradable protein in kg/d
        coeff_dict (Dict): Dictionary containing all coefficients for the model

    Returns:
        Du_MiN_NRC2021_g: Microbial N in g/d
    """

    Dt_ForNDF = Dt_ForNDFIn / Dt_DMIn * 100
    An_RDP = Dt_RDPIn / Dt_DMIn * 100

    # Calculate Rum_DigNDFIn
    Rum_dcNDF = -31.9 + 0.721 * Dt_NDFIn / Dt_DMIn * 100 - \
            0.247 * Dt_StIn / Dt_DMIn * 100 + \
            6.63 * Dt_CPIn / Dt_DMIn * 100 - \
            0.211 * (Dt_CPIn / Dt_DMIn * 100) ** 2 - \
            0.387 * Dt_ADFIn / Dt_DMIn / (Dt_NDFIn / Dt_DMIn) * 100 - \
            0.121 * Dt_ForWet + 1.51 * Dt_DMIn

    if Rum_dcNDF < 0.1 or Rum_dcNDF is None:                                                # Line 984
        Rum_dcNDF = 0.1
        
    Rum_DigNDFIn = Rum_dcNDF / 100 * Dt_NDFIn

    # Calculate An_RDPIn
    An_RDPIn = Dt_CPIn - Dt_RUPIn                                                           # Line 1107, 1102

    # Calculate Rum_DigStIn
    Rum_dcSt = 70.6 - 1.45*(Dt_DMIn) + 0.424*Dt_ForNDF + \
            1.39*(Dt_StIn)/(Dt_DMIn)*100 - \
            0.0219*((Dt_StIn)/(Dt_DMIn)*100)**2 - \
            0.154*Dt_ForWet

    if Rum_dcSt < 0.1:                                                                      # Line 992
        Rum_dcSt = 0.1            

    elif Rum_dcSt > 100:                                                                    # Line 993
        Rum_dcSt = 100 

    Rum_DigStIn = Rum_dcSt / 100 * Dt_StIn                                                   # Line 998


    Du_MiN_NRC2021_g = calculate_Du_MiN_NRC2021_g(An_RDP, An_RDPIn, Dt_DMIn, Rum_DigNDFIn, Rum_DigStIn, coeff_dict)
    
    # The 2 alternative predictions are currently disabled but can easily be implemented in the future
    
    # Du_MiN_VTln_g = calculate_Du_MiN_VTln_g(Dt_DMIn, Dt_AshIn, Dt_NDFIn, Dt_StIn, Dt_FAhydrIn, Dt_TPIn, Dt_NPNDMIn, Rum_DigStIn,
    #                                         Rum_DigNDFIn, An_RDPIn, Dt_ForNDFIn)
    # Du_MiN_VTnln_g = calculate_Du_MiN_VTnln_g(An_RDPIn, Rum_DigNDFIn, Rum_DigStIn)

    # return Du_MiN_NRC2021_g, Du_MiN_VTln_g, Du_MiN_VTnln_g
    return Du_MiN_NRC2021_g


def calculate_Du_MiN_NRC2021_g(An_RDP, An_RDPIn, Dt_DMIn, Rum_DigNDFIn, Rum_DigStIn, coeff_dict): 
    """
    Default microbial nitrogen (N) prediction

    Parameters:
        An_RDP (Number): An_RDPIn divided by DMI, no units
        Dt_RDPIn (Number): Rumen degradable protein in kg/d
        Dt_DMIn (Number): Dry matter intake, kg/d
        Rum_DigNDFIn (Number): Digestable neutral detergent fiber (NDF) intake, kg/d
        Rum_DigStIn (Number): Digestable starch intake, kg/d
        coeff_dict (Dict): Dictionary containing all coefficients for the model

    Returns:
        Du_MiN_NRC2021_g: Microbial N in g/d
    """

    req_coeffs = ['VmMiNInt', 'VmMiNRDPSlp', 'KmMiNRDNDF', 'KmMiNRDSt']
    check_coeffs_in_coeff_dict(coeff_dict, req_coeffs)
        
    if An_RDP <= 12:                                                                        # Line 1124
        RDPIn_MiNmax = An_RDPIn
    else:
        RDPIn_MiNmax = Dt_DMIn * 0.12
        # RDP intake capped at 12% DM from Firkins paper
    MiN_Vm = coeff_dict['VmMiNInt'] + coeff_dict['VmMiNRDPSlp'] * RDPIn_MiNmax                                          # Line 1125            

    Du_MiN_NRC2021_g = MiN_Vm / (1 + coeff_dict['KmMiNRDNDF'] / Rum_DigNDFIn + coeff_dict['KmMiNRDSt'] / Rum_DigStIn)   # Line 1126

    return Du_MiN_NRC2021_g


def calculate_Du_MiN_VTln_g(Dt_DMIn, Dt_AshIn, Dt_NDFIn, Dt_StIn, Dt_FAhydrIn, Dt_TPIn, Dt_NPNDMIn, Rum_DigStIn,
                            Rum_DigNDFIn, An_RDPIn, Dt_ForNDFIn, coeff_dict):
    # *** NEED TO TEST ***
    """
    Microbial nitrogen (N) prediction from Hanigan, 2021

    Currently unused in the model.

    Parameters:
        Dt_DMIn (Number): Dry matter intake, kg/d
        Dt_AshIn (Number): Ash intake in kg/d
        Dt_NDFIn (Number): Neutral detergent fiber (NDF) intake in kg/d
        Dt_StIn (Number): Starch intake in kg/d
        Dt_FAhydrIn (Number): Hydrated? fatty acid intake, kg/d
        Dt_TPIn (Number): True protein intake in kg/d
        Dt_NPNDMIn (Number): Non-protein nitrogen relative to DMI? Check textbook
        Rum_DigStIn (Number): Rumen degradable starch intake in kg/d
        Rum_DigNDFIn (Number): Rumen degradable NDF intake in kg/d
        An_RDPIn (Number): Rumen degradable protein intake in kg/d
        Dt_ForNDFIn (Number): Forage NDF intake in kg/d
        coeff_dict (Dict): Dictionary containing all coefficients for the model

    Returns: 
        Du_MiN_VTln_g: Microbial N in g/d
    """
    req_coeffs = ['Int_MiN_VT', 'KrdSt_MiN_VT', 'KrdNDF_MiN_VT', 'KRDP_MiN_VT', 'KrOM_MiN_VT', 'KForNDF_MiN_VT', 'KrOM2_MiN_VT', 'KrdStxrOM_MiN_VT', 'KrdNDFxForNDF_MiN_VT']
    check_coeffs_in_coeff_dict(coeff_dict, req_coeffs)

    Dt_rOMIn = Dt_DMIn-Dt_AshIn-Dt_NDFIn-Dt_StIn-Dt_FAhydrIn-Dt_TPIn-Dt_NPNDMIn             # Line 647
    if Dt_rOMIn < 0:                                                                        # Line 648
        Dt_rOMIn = 0                                                                        

    Du_MiN_VTln_g = coeff_dict['Int_MiN_VT'] + coeff_dict['KrdSt_MiN_VT'] * Rum_DigStIn + coeff_dict['KrdNDF_MiN_VT'] * Rum_DigNDFIn        # Line 1144-1146
    + coeff_dict['KRDP_MiN_VT'] * An_RDPIn + coeff_dict['KrOM_MiN_VT'] * Dt_rOMIn + coeff_dict['KForNDF_MiN_VT'] * Dt_ForNDFIn + coeff_dict['KrOM2_MiN_VT'] * Dt_rOMIn ** 2 
    + coeff_dict['KrdStxrOM_MiN_VT'] * Rum_DigStIn * Dt_rOMIn + coeff_dict['KrdNDFxForNDF_MiN_VT'] * Rum_DigNDFIn * Dt_ForNDFIn

    return Du_MiN_VTln_g


def calculate_Du_MiN_VTnln_g(An_RDPIn, Rum_DigNDFIn, Rum_DigStIn):
    # *** NEED TO TEST ***
    """
    Microbial nitrogen (N) prediction from White, 2017  

    Currently unused in the model.

    Parameters:
        An_RDPIn (Number): Rumen degradable protein intake in kg/d
        Rum_DigNDFIn (Number): Rumen degradable NDF intake in kg/d
        Rum_DigStIn (Number): Rumen degradable starch intake in kg/d
    
    Returns:
        Du_MiN_VTnln_g: Microbial N ing g/d
    
    """
    Du_MiN_VTnln_g = 7.47 + 0.574 * An_RDPIn * 1000 / (1 + 3.60 / Rum_DigNDFIn + 12.3 / Rum_DigStIn)    # Line 1147

    return Du_MiN_VTnln_g
