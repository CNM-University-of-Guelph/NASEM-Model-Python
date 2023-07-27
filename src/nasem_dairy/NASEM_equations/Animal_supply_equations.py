import math
from nasem_dairy.ration_balancer.ration_balancer_functions import check_coeffs_in_coeff_dict

def calculate_An_NE(Dt_CPIn, Dt_FAIn, Mlk_NP_g, An_DEIn, An_DigNDF, Fe_CP, Fe_CPend_g, Dt_DMIn, An_BW, An_BW_mature, Trg_FrmGain,
                    Trg_RsrvGain, GrUter_BWgain, coeff_dict):
    """
    Calculates net energy intake

    Parameters:
        Dt_CPIn (Number): Crude protein (CP) intake in kg/d
        Dt_FAIn (Number): Fatty acid intake, kg/d
        Mlk_NP_g (Number): Net protein in milk, g/d
        An_DEIn (Number): Digestible energy intake in Mcal/d
        An_DigNDF (Number): Total tract digested neutral detergent fiber
        Fe_CP (Number): Fecal crude protein, kg/d
        Fe_CPend_g (Number): Fecal crude protein coming from endogenous secretions
        Dt_DMIn (Number): Dry matter intake, kg/d
        An_BW (Number): Animal bodyweight in kg
        An_BW_mature (Number): Animal Mature Liveweight in kg.
        Trg_FrmGain (Number): Target gain in body Frame Weight in kg fresh weight/day
        Trg_RsrvGain (Number): Target gain or loss in body reserves (66% fat, 8% CP) in kg fresh weight/day
        GrUter_BWgain (Number): Average rate of fresh tissue growth for gravid uterus, kg fresh wt/d
        coeff_dict (Dict): Dictionary containing all coefficients for the model
    
    Returns:
        An_NE: Net energy, Mcal/kg 
        An_MEIn: Metabolizable energy intake, Mcal/kg
    """

    req_coeffs = ['Body_NP_CP', 'An_GutFill_BW', 'CPGain_RsrvGain', 'GrUter_BWgain', 
                  'CP_GrUtWt', 'Gest_NPother_g']
    check_coeffs_in_coeff_dict(coeff_dict, req_coeffs)


    #######################
    ### An_GasEOut_Lact ###
    #######################
    # An_DigNDF = An_DigNDFIn / Dt_DMIn * 100
    An_GasEOut_Lact = 0.294 * Dt_DMIn - 0.347 * Dt_FAIn / Dt_DMIn * 100 + 0.0409 * An_DigNDF

    ################
    ### Ur_DEout ###
    ################
    Scrf_CP_g = 0.20 * An_BW**0.60                                                                      # Line 1965
    Mlk_CP_g = Mlk_NP_g / 0.95                                          # Line 2213
    CPGain_FrmGain = 0.201 - 0.081 * An_BW / An_BW_mature
    # Body_NP_CP = 0.86                                                      # Line 1964
    Frm_Gain = Trg_FrmGain
    # An_GutFill_BW = 0.18                                                   # Line 2400 and 2411
    Frm_Gain_empty = Frm_Gain * (1 - coeff_dict['An_GutFill_BW'])
    NPGain_FrmGain = CPGain_FrmGain * coeff_dict['Body_NP_CP']                           # Line 2460
    Frm_NPgain = NPGain_FrmGain * Frm_Gain_empty                           # Line 2461
    # CPGain_RsrvGain = 0.068                                           # Line 2466
    NPGain_RsrvGain = coeff_dict['CPGain_RsrvGain'] * coeff_dict['Body_NP_CP']                   # Line 2467
    Rsrv_Gain_empty = Trg_RsrvGain                                    # Line 2435 and 2441
    Rsrv_NPgain = NPGain_RsrvGain * Rsrv_Gain_empty                    # Line 2468
    Body_NPgain = Frm_NPgain + Rsrv_NPgain
    Body_CPgain = Body_NPgain / coeff_dict['Body_NP_CP']                                  # Line 2475
    Body_CPgain_g = Body_CPgain * 1000                                      # Line 2477

    # CP_GrUtWt = 0.123                                               # Line 2298, kg CP/kg fresh Gr Uterus weight
    # Gest_NPother_g = 0                                              # Line 2353, Net protein gain in other maternal tissues during late gestation: mammary, intestine, liver, and blood. This should be replaced with a growth funncton such as Dijkstra's mammary growth equation. MDH.                                                              
    Gest_NCPgain_g = GrUter_BWgain * coeff_dict['CP_GrUtWt'] * 1000
    Gest_NPgain_g = Gest_NCPgain_g * coeff_dict['Body_NP_CP']
    Gest_NPuse_g = Gest_NPgain_g + coeff_dict['Gest_NPother_g']                             # Line 2366
    Gest_CPuse_g = Gest_NPuse_g / coeff_dict['Body_NP_CP']                                  # Line 2367
    Ur_Nout_g = (Dt_CPIn * 1000 - Fe_CP * 1000 - Scrf_CP_g - Fe_CPend_g - Mlk_CP_g - Body_CPgain_g - Gest_CPuse_g) / 6.25     # Line 2742
    Ur_DEout = 0.0143 * Ur_Nout_g                               # Line 2748

    An_MEIn = An_DEIn - An_GasEOut_Lact - Ur_DEout
    An_NE_In = An_MEIn * 0.66                                  # Line 2762
    An_NE = An_NE_In / Dt_DMIn                                 # Line 2763

    return An_NE, An_MEIn


def calculate_An_DEIn(Dt_DigNDFIn_Base, Dt_NDFIn, Dt_DigStIn_Base, Dt_StIn, Dt_DigrOMtIn, Dt_CPIn, Dt_RUPIn, Dt_idRUPIn, Dt_NPNCPIn, Dt_DigFAIn, Du_MiCP_g, An_BW, Dt_DMIn, coeff_dict):
    """
    Digestable energy (DE) supply

    Calculates DE for each feed component as well as a total DE intake

    Parameters:
        Dt_DigNDFIn_Base (Number): Digestable neutral detergent fiber (NDF) intake, kg/d
        Dt_NDFIn (Number): Neutral detergent fiber (NDF) intake in kg/d
        Dt_DigStIn_Base (Number): Digestable starch intake, kg/d
        Dt_StIn (Number): Starch intake in kg/d
        Dt_DigrOMtIn (Number): Digestable residual organic matter intake, kg/d
        Dt_CPIn (Number): Crude protein (CP) intake in kg/d
        Dt_RUPIn (Number): Rumen undegradable protein (RUP) in kg/d
        Dt_idRUPIn (Number): Intestinally digested rumen undegradable protein intake, kg/d
        Dt_NPNCPIn (Number): Crude protein from non-protein nitrogen (NPN) intake, kg/d
        Dt_DigFAIn (Number): Digestable fatty acid intake, kg/d
        Du_MiCP_g (Number): Microbial crude proetin, g
        An_BW (Number): Animal bodyweight in kg
        Dt_DMIn (Number): Dry matter intake, kg/d
        coeff_dict (Dict): Dictionary containing all coefficients for the model

    Returns:
        An_DEIn (Number): Digestible energy intake in Mcal/d
        An_DENPNCPIn (Number): Digestible energy crud eprotein synthesized from non protein nitrogen (NPN), Mcal/d
        An_DETPIn (Number): Digestible energy from true protein, Mcal/d
        An_DigNDFIn (Number): Digestable neutral detergent fiber (NDF) intake, Mcal/d
        An_DEStIn (Number): Digestible energy from starch, Mcal/d
        An_DEFAIn (Number): Digestible energy from fatty acids, Mcal/d
        An_DErOMIn (Number): Digestible energy from residual organic matter, Mcal/d
        An_DENDFIn (Number): Digestible energy from neutral detergent fiber (NDF), Mcal
        Fe_CP (Number): Fecal crude protein, kg/d
        Fe_CPend_g (Number): Fecal crude protein coming from endogenous secretions
        Du_idMiCP_g (Number): Intestinally digested microbial crude protein, g/d
    """
# Consider renaiming as this really calculates all of the DE intakes as well as the total

    req_coeffs = ['En_NDF', 'En_St', 'En_rOM', 'Fe_rOMend_DMI', 
                  'SI_dcMiCP', 'En_CP', 'dcNPNCP', 'En_NPNCP', 'En_FA']
    check_coeffs_in_coeff_dict(coeff_dict, req_coeffs)

    # Replaces An_NDF as input
    An_NDF = Dt_NDFIn / Dt_DMIn * 100

    #An_DigNDFIn#
    TT_dcNDF_Base = Dt_DigNDFIn_Base / Dt_NDFIn * 100                     # Line 1056
    if math.isnan(TT_dcNDF_Base) is True:
        TT_dcNDF_Base = 0

    An_DMIn_BW = Dt_DMIn / An_BW
    # En_NDF = 4.2

    if TT_dcNDF_Base == 0:
        TT_dcNDF = 0
    else:
        TT_dcNDF = (TT_dcNDF_Base / 100 - 0.59 * (Dt_StIn / Dt_DMIn - 0.26) - 1.1 * (An_DMIn_BW - 0.035)) * 100       # Line 1060


    Dt_DigNDFIn = TT_dcNDF / 100 * Dt_NDFIn
    
    
    An_DigNDFIn = Dt_DigNDFIn + 0 * TT_dcNDF/100                                    # Line 1063, the 0 is a placeholder for InfRum_NDFIn, ask Dave about this, I think the TT_dcNDF is not needed
    An_DENDFIn = An_DigNDFIn * coeff_dict['En_NDF']                                               # Line 1353
    
    #An_DEStIn#
    # En_St = 4.23                                                                   # Line 271
    TT_dcSt_Base = Dt_DigStIn_Base / Dt_StIn * 100                                 # Line 1030    
    if math.isnan(TT_dcSt_Base) is True:
        TT_dcSt_Base = 0

    if TT_dcSt_Base == 0:
        TT_dcSt = 0
    else:
        TT_dcSt = TT_dcSt_Base - (1.0 * (An_DMIn_BW - 0.035)) * 100                 # Line 1032
    An_DigStIn = Dt_StIn * TT_dcSt / 100                                            # Line 1033
    An_DEStIn = An_DigStIn * coeff_dict['En_St']                                                  # Line 1351

    #An_DErOMIn#
    # En_rOM = 4.0                                                                    # Line 271
    # Fe_rOMend_DMI = 3.43                                                            # Line 1005, 3.43% of DMI
    Fe_rOMend = coeff_dict['Fe_rOMend_DMI'] / 100 * Dt_DMIn                               	    # Line 1007, From Tebbe et al., 2017.  Negative interecept represents endogenous rOM
    An_DigrOMaIn = Dt_DigrOMtIn - Fe_rOMend                                         # Line 1024, 1022
    An_DErOMIn = An_DigrOMaIn * coeff_dict['En_rOM']                                              # Line 1352

    #An_DETPIn#
    # SI_dcMiCP = 80			                                                    	# Line 1123, Digestibility coefficient for Microbial Protein (%) from NRC 2001 
    # En_CP = 5.65                                                                    # Line 266
    # dcNPNCP = 100	                                                                # Line 1092, urea and ammonium salt digestibility
    # En_NPNCP = 0.89                                                                 # Line 270
    An_idRUPIn = Dt_idRUPIn                                       # Line 1099
    Fe_RUP = Dt_RUPIn - An_idRUPIn                                                  # Line 1198   
    Du_MiCP = Du_MiCP_g / 1000                                                      # Line 1166
    Du_idMiCP_g = coeff_dict['SI_dcMiCP'] / 100 * Du_MiCP_g
    Du_idMiCP = Du_idMiCP_g / 1000
    Fe_RumMiCP = Du_MiCP - Du_idMiCP                                                # Line 1196
    Fe_CPend_g = (12 + 0.12 * An_NDF) * Dt_DMIn            # line 1187, g/d, endogen secretions plus urea capture in microbies in rumen and LI
    Fe_CPend = Fe_CPend_g / 1000                                                    # Line 1190
    Fe_CP = Fe_RUP + Fe_RumMiCP + Fe_CPend          # Line 1202, Double counting portion of RumMiCP derived from End CP. Needs to be fixed. MDH
    An_DigCPaIn = Dt_CPIn - Fe_CP		            # Line 1222, apparent total tract
    An_DECPIn = An_DigCPaIn * coeff_dict['En_CP']
    An_DENPNCPIn = Dt_NPNCPIn * coeff_dict['dcNPNCP'] / 100 * coeff_dict['En_NPNCP']                                                          # Line 1355, 1348
    
    # Line 1356, Caution! DigTPaIn not clean so subtracted DE for CP equiv of NPN to correct. Not a true DE_TP.
    An_DETPIn = An_DECPIn - An_DENPNCPIn / coeff_dict['En_NPNCP'] * coeff_dict['En_CP']                      

    #An_DEFAIn#
    # En_FA = 9.4                                                                                         # Line 265
    An_DigFAIn = Dt_DigFAIn                                                                             # Line 1309
    An_DEFAIn = An_DigFAIn * coeff_dict['En_FA']

    An_DEIn = An_DENDFIn + An_DEStIn + An_DErOMIn + An_DETPIn + An_DENPNCPIn + An_DEFAIn  # Line 1367

    return An_DEIn, An_DENPNCPIn, An_DETPIn, An_DigNDFIn, An_DEStIn, An_DEFAIn, An_DErOMIn, An_DENDFIn, Fe_CP, Fe_CPend_g, Du_idMiCP_g
