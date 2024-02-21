# dev_microbial_protein_equations
from nasem_dairy.ration_balancer.ration_balancer_functions import check_coeffs_in_coeff_dict


def calculate_RDPIn_MiNmax(Dt_DMIn, An_RDP, An_RDPIn):
    if An_RDP <= 12:                                                               # Line 1124
        RDPIn_MiNmax = An_RDPIn
    else:
        RDPIn_MiNmax = Dt_DMIn * 0.12
    return RDPIn_MiNmax


def calculate_MiN_Vm(RDPIn_MiNmax, coeff_dict):
    req_coeffs = ['VmMiNInt', 'VmMiNRDPSlp']
    check_coeffs_in_coeff_dict(coeff_dict, req_coeffs)
    MiN_Vm = coeff_dict['VmMiNInt'] + \
        coeff_dict['VmMiNRDPSlp'] * RDPIn_MiNmax     # Line 1125
    return MiN_Vm


def calculate_Du_MiN_NRC2021_g(MiN_Vm, Rum_DigNDFIn, Rum_DigStIn, An_RDPIn_g, coeff_dict):
    req_coeffs = ['KmMiNRDNDF', 'KmMiNRDSt']
    check_coeffs_in_coeff_dict(coeff_dict, req_coeffs)
    Du_MiN_NRC2021_g = MiN_Vm / \
        (1 + coeff_dict['KmMiNRDNDF'] / Rum_DigNDFIn +
         coeff_dict['KmMiNRDSt'] / Rum_DigStIn)   # Line 1126
    if Du_MiN_NRC2021_g > 1 * An_RDPIn_g/6.25:  # Line 1130
        Du_MiN_NRC2021_g = 1 * An_RDPIn_g/6.25
    else:
        Du_MiN_NRC2021_g = Du_MiN_NRC2021_g
    return Du_MiN_NRC2021_g


def calculate_Du_MiN_VTln_g(Dt_rOMIn, Dt_ForNDFIn, An_RDPIn, Rum_DigStIn, Rum_DigNDFIn, coeff_dict):
    req_coeffs = ['Int_MiN_VT',
                  'KrdSt_MiN_VT',
                  'KrdNDF_MiN_VT',
                  'KRDP_MiN_VT',
                  'KrOM_MiN_VT',
                  'KForNDF_MiN_VT',
                  'KrOM2_MiN_VT',
                  'KrdStxrOM_MiN_VT',
                  'KrdNDFxForNDF_MiN_VT'
                  ]
    check_coeffs_in_coeff_dict(coeff_dict, req_coeffs)
    # Line 1144-1146
    Du_MiN_VTln_g = coeff_dict['Int_MiN_VT'] + coeff_dict['KrdSt_MiN_VT'] * \
        Rum_DigStIn + coeff_dict['KrdNDF_MiN_VT'] * Rum_DigNDFIn
    + coeff_dict['KRDP_MiN_VT'] * An_RDPIn + coeff_dict['KrOM_MiN_VT'] * \
        Dt_rOMIn + coeff_dict['KForNDF_MiN_VT'] * Dt_ForNDFIn
    + coeff_dict['KrOM2_MiN_VT'] * Dt_rOMIn ** 2
    + coeff_dict['KrdStxrOM_MiN_VT'] * Rum_DigStIn * Dt_rOMIn + \
        coeff_dict['KrdNDFxForNDF_MiN_VT'] * Rum_DigNDFIn * Dt_ForNDFIn
    return Du_MiN_VTln_g


def calculate_Du_MiN_VTnln_g(An_RDPIn, Rum_DigNDFIn, Rum_DigStIn):
    Du_MiN_VTnln_g = 7.47 + 0.574 * An_RDPIn * 1000 / \
        (1 + 3.60 / Rum_DigNDFIn + 12.3 / Rum_DigStIn)    # Line 1147
    return Du_MiN_VTnln_g


def calculate_Du_MiCP(Du_MiCP_g):
    Du_MiCP = Du_MiCP_g / 1000                      # Line 1166
    return Du_MiCP


def calculate_Du_idMiCP_g(Du_MiCP_g, coeff_dict):
    req_coeff = ['SI_dcMiCP']
    check_coeffs_in_coeff_dict(coeff_dict, req_coeff)
    Du_idMiCP_g = coeff_dict['SI_dcMiCP'] / 100 * Du_MiCP_g     # Line 1180
    return Du_idMiCP_g


def calculate_Du_idMiCP(Du_idMiCP_g):
    Du_idMiCP = Du_idMiCP_g / 1000
    return Du_idMiCP


def calculate_Du_idMiTP_g(Du_idMiCP_g, coeff_dict):
    req_coeff = ['fMiTP_MiCP']
    check_coeffs_in_coeff_dict(coeff_dict, req_coeff)
    Du_idMiTP_g = coeff_dict['fMiTP_MiCP'] * Du_idMiCP_g  # Line 1182
    return Du_idMiTP_g


def calculate_Du_idMiTP(Du_idMiTP_g):
    Du_idMiTP = Du_idMiTP_g / 1000
    return Du_idMiTP
