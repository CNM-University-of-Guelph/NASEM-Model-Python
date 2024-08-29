"""Microbial protein synthesis and flow calculations.

This module contains functions to estimate the production, flow, and 
digestion of microbial protein within the rumen, based on various dietary inputs.
"""


def calculate_RDPIn_MiNmax(
    Dt_DMIn: float, 
    An_RDP: float, 
    An_RDPIn: float
) -> float:
    if An_RDP <= 12:  # Line 1124
        RDPIn_MiNmax = An_RDPIn
    else:
        RDPIn_MiNmax = Dt_DMIn * 0.12
    return RDPIn_MiNmax


def calculate_MiN_Vm(RDPIn_MiNmax: float, coeff_dict: dict) -> float:
    """
    Examples
    --------
    ```
    coeff_dict = {"VmMiNInt": 100.8, "VmMiNRDPSlp": 81.56}
    
    calculate_MiN_Vm(
        RDPIn_MiNmax = 100.0, coeff_dict = coeff_dict
    )
    ```
    """
    MiN_Vm = coeff_dict['VmMiNInt'] + coeff_dict['VmMiNRDPSlp'] * RDPIn_MiNmax     
    # Line 1125
    return MiN_Vm


def calculate_Du_MiN_NRC2021_g(
    MiN_Vm: float, 
    Rum_DigNDFIn: float, 
    Rum_DigStIn: float, 
    An_RDPIn_g: float,
    coeff_dict: dict
) -> float:
    """
    Examples
    --------
    ```
    coeff_dict = {"KmMiNRDNDF": 0.0939, "KmMiNRDSt": 0.0274}
    
    calculate_Du_MiN_NRC2021_g(
        MiN_Vm = 25.0, Rum_DigNDFIn = 200.0, Rum_DigStIn = 150.0, 
        An_RDPIn_g = 300.0, coeff_dict = coeff_dict
    )
    ```
    """
    Du_MiN_NRC2021_g = (MiN_Vm / (1 + coeff_dict['KmMiNRDNDF'] / Rum_DigNDFIn + 
                                  coeff_dict['KmMiNRDSt'] / Rum_DigStIn)) # Line 1126
    if Du_MiN_NRC2021_g > 1 * An_RDPIn_g / 6.25:  # Line 1130
        Du_MiN_NRC2021_g = 1 * An_RDPIn_g / 6.25
    else:
        Du_MiN_NRC2021_g = Du_MiN_NRC2021_g
    return Du_MiN_NRC2021_g


def calculate_Du_MiN_VTln_g(
    Dt_rOMIn: float, 
    Dt_ForNDFIn: float, 
    An_RDPIn: float, 
    Rum_DigStIn: float,
    Rum_DigNDFIn: float, 
    coeff_dict: dict
) -> float:
    """
    Examples
    --------
    ```
    coeff_dict = {
        "Int_MiN_VT": 18.686, "KrdSt_MiN_VT": 10.214, "KrdNDF_MiN_VT": 28.976, 
        "KRDP_MiN_VT": 43.405, "KrOM_MiN_VT": -11.731, "KForNDF_MiN_VT": 8.895, 
        "KrOM2_MiN_VT": 2.861, "KrdStxrOM_MiN_VT": 5.637, 
        "KrdNDFxForNDF_MiN_VT": -2.22
    }
    
    calculate_Du_MiN_VTln_g(
        Dt_rOMIn = 300.0, Dt_ForNDFIn = 100.0, An_RDPIn = 200.0, 
        Rum_DigStIn = 150.0, Rum_DigNDFIn = 250.0, coeff_dict = coeff_dict
    )
    ```
    """
    # Line 1144-1146
    Du_MiN_VTln_g = (coeff_dict['Int_MiN_VT'] + 
                     coeff_dict['KrdSt_MiN_VT'] * Rum_DigStIn + 
                     coeff_dict['KrdNDF_MiN_VT'] * Rum_DigNDFIn + 
                     coeff_dict['KRDP_MiN_VT'] * An_RDPIn + 
                     coeff_dict['KrOM_MiN_VT'] * Dt_rOMIn + 
                     coeff_dict['KForNDF_MiN_VT'] * Dt_ForNDFIn + 
                     coeff_dict['KrOM2_MiN_VT'] * Dt_rOMIn**2 + 
                     coeff_dict['KrdStxrOM_MiN_VT'] * Rum_DigStIn * Dt_rOMIn + 
                     coeff_dict['KrdNDFxForNDF_MiN_VT'] * Rum_DigNDFIn * 
                     Dt_ForNDFIn)
    return Du_MiN_VTln_g


def calculate_Du_MiN_VTnln_g(
    An_RDPIn: float, 
    Rum_DigNDFIn: float, 
    Rum_DigStIn: float
) -> float:
    Du_MiN_VTnln_g = (7.47 + 0.574 * An_RDPIn * 1000 / 
                      (1 + 3.60 / Rum_DigNDFIn + 12.3 / Rum_DigStIn)) # Line 1147
    return Du_MiN_VTnln_g


def calculate_Du_MiN_g(
    MiN_eqn: int, 
    MiN_Vm: float, 
    Dt_rOMIn: float,
    Dt_ForNDFIn: float,
    An_RDPIn: float,
    Rum_DigNDFIn: float,
    Rum_DigStIn: float,
    An_RDPIn_g: float,
    coeff_dict: dict
) -> float:
    if MiN_eqn == 1:
        Du_MiN_g = calculate_Du_MiN_NRC2021_g(
            MiN_Vm, Rum_DigNDFIn, Rum_DigStIn, An_RDPIn_g, 
            coeff_dict
            )
    elif MiN_eqn == 2:
        Du_MiN_g = calculate_Du_MiN_VTln_g(
            Dt_rOMIn, Dt_ForNDFIn, An_RDPIn, Rum_DigStIn, Rum_DigNDFIn, 
            coeff_dict
            )
    elif MiN_eqn == 3:
        Du_MiN_g = calculate_Du_MiN_VTnln_g(
            An_RDPIn, Rum_DigNDFIn, Rum_DigStIn
            )
    else:
        raise ValueError(
            f"Invalid MiN_eqn: {MiN_eqn} was entered. "
            "Must choose 1, 2 or 3."
            )
    return Du_MiN_g


def calculate_Du_MiCP(Du_MiCP_g: float) -> float:
    Du_MiCP = Du_MiCP_g / 1000  # Line 1166
    return Du_MiCP


def calculate_Du_idMiCP_g(Du_MiCP_g: float, coeff_dict: dict) -> float:
    """
    Examples
    --------
    ```
    coeff_dict = {"SI_dcMiCP": 80}
    
    calculate_Du_idMiCP_g(
        Du_MiCP_g = 200.0, coeff_dict = coeff_dict
    )
    ```
    """
    Du_idMiCP_g = coeff_dict['SI_dcMiCP'] / 100 * Du_MiCP_g  # Line 1180
    return Du_idMiCP_g


def calculate_Du_idMiCP(Du_idMiCP_g: float) -> float:
    Du_idMiCP = Du_idMiCP_g / 1000
    return Du_idMiCP


def calculate_Du_idMiTP_g(Du_idMiCP_g: float, coeff_dict: dict) -> float:
    """
    Examples
    --------
    ```
    coeff_dict = {"fMiTP_MiCP": 0.824}
    
    calculate_Du_idMiTP_g(
        Du_idMiCP_g = 160.0, coeff_dict = coeff_dict
    )
    ```
    """
    Du_idMiTP_g = coeff_dict['fMiTP_MiCP'] * Du_idMiCP_g  # Line 1182
    return Du_idMiTP_g


def calculate_Du_idMiTP(Du_idMiTP_g: float) -> float:
    Du_idMiTP = Du_idMiTP_g / 1000
    return Du_idMiTP


def calculate_Du_MiTP(Du_MiTP_g: float) -> float:
    """
    Du_MiTP_g: Duodenal microbial true protein, g/d
    """
    Du_MiTP = Du_MiTP_g / 1000  # Line 1167
    return Du_MiTP


def calculate_Du_EndCP_g(Dt_DMIn: float, InfRum_DMIn: float) -> float:
    """
    Du_EndCP_g: Duodenal endogenous flow of crude protein, g/d
    """
    Du_EndCP_g = 96.1 + 7.54 * (Dt_DMIn + InfRum_DMIn)  # Line 1170
    return Du_EndCP_g


def calculate_Du_EndN_g(Dt_DMIn: float, InfRum_DMIn: float) -> float:
    """
    Du_EndN_g: Duodenal endogenous flow of nitrogen, g/d 
    """
    Du_EndN_g = 15.4 + 1.21 * (Dt_DMIn + InfRum_DMIn)
    # g/d, recalc of the above eqn (calculate_Du_EndCP_g) at 16% N in CP, Line 1171
    return Du_EndN_g


def calculate_Du_EndCP(Du_EndCP_g: float) -> float:
    """
    Du_EndCP: Duodenal endogenous flow of crude protein, kg/d 
    """
    Du_EndCP = Du_EndCP_g / 1000  # Line 1172
    return Du_EndCP


def calculate_Du_EndN(Du_EndN_g: float) -> float:
    """
    Du_EndN: Duodenal endogenous flow of nitrogen, kg/d 
    """
    Du_EndN = Du_EndN_g / 1000  # Line 1173
    return Du_EndN


def calculate_Du_NAN_g(
    Du_MiN_g: float, 
    An_RUPIn: float,
    Du_EndN_g: float
) -> float:
    """
    Du_NAN_g: ??? Not sure what NAN means. Something to do with Nitrogen flow. g/d
    """
    Du_NAN_g = Du_MiN_g + An_RUPIn * 0.16 * 1000 + Du_EndN_g  # Line 1175
    return Du_NAN_g


def calculate_Du_NANMN_g(An_RUPIn: float, Du_EndN_g: float) -> float:
    """
    Du_NANMN_g: ??? Not sure what NANMN means, Also has to do with Nitrogen flow, g/d
    """
    Du_NANMN_g = An_RUPIn * 0.16 * 1000 + Du_EndN_g  # Line 1176
    return Du_NANMN_g


def calculate_Du_MiN_NRC2001_g(Dt_TDNIn: float, An_RDPIn: float) -> float:
    """
    Du_MiN_NRC2001_g: Microbial N flow, NRC 2001 equation (g/d)
    """
    # NRC 2001 eqn. for N flow comparison purposes, Line 1389
    if 0.13 * Dt_TDNIn > 0.85 * An_RDPIn:
        Du_MiN_NRC2001_g = 0.85 * An_RDPIn * 1000 * 0.16
    else:
        Du_MiN_NRC2001_g = 0.13 * Dt_TDNIn * 1000 * 0.16
    return Du_MiN_NRC2001_g


def calculate_Rum_MiCP_DigCHO(
    Du_MiCP: float, 
    Rum_DigNDFIn: float,
    Rum_DigStIn: float
) -> float:
    """
    Rum_MiCP_DigCHO: Microbial CP as a fraction of digestable carbohydrates
    """
    Rum_MiCP_DigCHO = Du_MiCP / (Rum_DigNDFIn + Rum_DigStIn)  # Line 3122
    return Rum_MiCP_DigCHO
