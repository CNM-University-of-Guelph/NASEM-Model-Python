# dev_nutrient_intakes
# All functions for calculating nutrient intakes based on ration formulation
# NOTE Any new functions need to be added to the appropriate wrapper
import math
import numpy as np
import pandas as pd
from nasem_dairy.ration_balancer.ration_balancer_functions import check_coeffs_in_coeff_dict

####################
# Functions for Feed Intakes
####################


def calculate_TT_dcFdNDF_Lg(Fd_NDF, Fd_Lg):
    Fd_NFD_check = np.where(Fd_NDF == 0, 1e-6, Fd_NDF)
    TT_dcFdNDF_Lg = 0.75 * (Fd_NDF - Fd_Lg) * (1 - (Fd_Lg / Fd_NFD_check)
                                               ** 0.667) / Fd_NFD_check * 100  # Line 235-236
    return TT_dcFdNDF_Lg


def calculate_Fd_DNDF48(Fd_Conc, Fd_DNDF48):
    # I can't find Fd_DNDF48 in any of the feed libraries, including the feed library in the NASEM software,
    # For now all the Fd_DNDF48 values are being calculated
    # I've added a column of 0s as the Fd_DNDF48 column
    condition = (Fd_Conc < 100) & (Fd_DNDF48.isin([0, np.nan]))
    condition_conc = (Fd_Conc == 100) & (Fd_DNDF48.isin([0, np.nan]))
    # Line 241, mean of Mike Allen database used for DMI equation
    Fd_DNDF48 = np.where(condition, 48.3, Fd_DNDF48)
    # Line 242, mean of concentrates in the feed library
    Fd_DNDF48 = np.where(condition_conc, 65, Fd_DNDF48)
    return Fd_DNDF48


def calculate_TT_dcFdNDF_48h(Fd_DNDF48):
    TT_dcFdNDF_48h = 12 + 0.61 * Fd_DNDF48  # Line 245
    return TT_dcFdNDF_48h


def calculate_TT_dcFdNDF_Base(Use_DNDF_IV, Fd_Conc, TT_dcFdNDF_Lg, TT_dcFdNDF_48h):
    condition1 = (Use_DNDF_IV == 1) & (Fd_Conc < 100) & ~TT_dcFdNDF_48h.isna()  # Line 249, Forages only
    condition2 = (Use_DNDF_IV == 2) & ~TT_dcFdNDF_48h.isna()                    # Line 251, All Ingredients
    # Line 248, Prefill with the Lg based predictions as a default
    TT_dcFdNDF_Base = TT_dcFdNDF_Lg
    TT_dcFdNDF_Base = np.where(condition1, TT_dcFdNDF_48h, TT_dcFdNDF_Base)
    TT_dcFdNDF_Base = np.where(condition2, TT_dcFdNDF_48h, TT_dcFdNDF_Base)
    return TT_dcFdNDF_Base


def calculate_Fd_GE(An_StatePhys, Fd_Category, Fd_CP, Fd_FA, Fd_Ash, Fd_St, Fd_NDF, coeff_dict):
    req_coeffs = ['En_CP', 'En_FA', 'En_rOM', 'En_St', 'En_NDF']
    check_coeffs_in_coeff_dict(coeff_dict, req_coeffs)

    condition = (An_StatePhys == "Calf") & (Fd_Category == "Calf Liquid Feed")
    Fd_GE = np.where(condition,
                     (Fd_CP/100 * coeff_dict['En_CP'] + Fd_FA/100 * coeff_dict['En_FA'] + (
                         100 - Fd_Ash - Fd_CP - Fd_FA) / 100 * coeff_dict['En_rOM']),  # Line 278, liquid feed exception
                     (Fd_CP/100 * coeff_dict['En_CP'] + Fd_FA/100 * coeff_dict['En_FA'] + Fd_St/100 * coeff_dict['En_St'] + Fd_NDF/100 * \
                      coeff_dict['En_NDF'] + (100 - Fd_CP - Fd_FA - Fd_St - Fd_NDF - Fd_Ash)/100 * coeff_dict['En_rOM'])  # Line 279, the remainder
                     )
    return Fd_GE


def calculate_Fd_DMIn(DMI, Fd_DMInp):
    Fd_DMIn = Fd_DMInp * DMI  # Line 441
    return Fd_DMIn


def calculate_Fd_AFIn(Fd_DM, Fd_DMIn):
    Fd_AFIn = np.where(Fd_DM == 0, 0, Fd_DMIn / (Fd_DM / 100))  # Line 442
    return Fd_AFIn


def calculate_Fd_For(Fd_Conc):
    Fd_For = 100 - Fd_Conc    # Line 446
    return Fd_For


def calculate_Fd_ForWet(Fd_DM, Fd_For):
    condition = (Fd_For > 50) & (Fd_DM < 71)
    Fd_ForWet = np.where(condition, Fd_For, 0)  # Line 447
    return Fd_ForWet


def calculate_Fd_ForDry(Fd_DM, Fd_For):
    condition = (Fd_For > 50) & (Fd_DM >= 71)
    Fd_ForDry = np.where(condition, Fd_For, 0)  # Line 448
    return Fd_ForDry


def calculate_Fd_Past(Fd_Category):
    Fd_Past = np.where(Fd_Category == 'Pasture', 100, 0)  # Line 449
    return Fd_Past


def calculate_Fd_LiqClf(Fd_Category):
    Fd_LiqClf = np.where(Fd_Category == 'Calf Liquid Feed', 100, 0)  # Line 450
    return Fd_LiqClf


def calculate_Fd_ForNDF(Fd_NDF, Fd_Conc):
    Fd_ForNDF = (1-Fd_Conc/100) * Fd_NDF    # Line 452
    return Fd_ForNDF


def calculate_Fd_NDFnf(Fd_NDF, Fd_NDFIP):
    Fd_NDFnf = Fd_NDF - Fd_NDFIP    # Line 453
    return Fd_NDFnf


def calculate_Fd_NPNCP(Fd_CP, Fd_NPN_CP):
    Fd_NPNCP = Fd_CP * Fd_NPN_CP * 100  # Line 455
    return Fd_NPNCP


def calculate_Fd_NPN(Fd_NPNCP):
    Fd_NPN = Fd_NPNCP / 6.25  # Line 457
    return Fd_NPN


def calculate_Fd_NPNDM(Fd_NPNCP):
    Fd_NPNDM = Fd_NPNCP / 2.81  # Line 458
    return Fd_NPNDM


def calculate_Fd_TP(Fd_CP, Fd_NPNCP):
    Fd_TP = Fd_CP - Fd_NPNCP  # Line 459
    return Fd_TP


def calculate_Fd_fHydr_FA(Fd_Category):
    Fd_fHydr_FA = np.where(
        Fd_Category == 'Fatty Acid Supplement', 1, 1/1.06)  # Line 461
    return Fd_fHydr_FA


def calculate_Fd_FAhydr(Fd_FA, Fd_fHydr_FA):
    Fd_FAhydr = Fd_FA * Fd_fHydr_FA  # Line 463
    return Fd_FAhydr


def calculate_Fd_NFC(Fd_NDF, Fd_TP, Fd_Ash, Fd_FAhydr, Fd_NPNDM):
    Fd_NFC = 100 - Fd_Ash - Fd_NDF - Fd_TP - Fd_NPNDM - Fd_FAhydr   # Line 465
    # Forces any values below 0 to =0           # Line 466
    Fd_NFC.clip(lower=0)
    return Fd_NFC


def calculate_Fd_rOM(Fd_NDF, Fd_St, Fd_TP, Fd_FA, Fd_fHydr_FA, Fd_Ash, Fd_NPNDM):
    Fd_rOM = 100 - Fd_Ash - Fd_NDF - Fd_St - \
        (Fd_FA*Fd_fHydr_FA) - Fd_TP - Fd_NPNDM     # Line 468
    return Fd_rOM


def calculate_Fd_GEIn(Fd_GE, Fd_DMIn):
    Fd_GEIn = Fd_GE * Fd_DMIn   # Line 544
    return Fd_GEIn


def calculate_Fd_DigNDFIn_Base(Fd_NDFIn, TT_dcFdNDF_Base):
    Fd_DigNDFIn_Base = TT_dcFdNDF_Base/100 * Fd_NDFIn    # Line 481
    return Fd_DigNDFIn_Base


def calculate_Fd_NPNCPIn(Fd_CPIn, Fd_NPN_CP):
    Fd_NPNCPIn = Fd_CPIn * Fd_NPN_CP / 100      # Line 491
    return Fd_NPNCPIn


def calculate_Fd_NPNIn(Fd_NPNCPIn):
    Fd_NPNIn = Fd_NPNCPIn * 0.16        # Line 492
    return Fd_NPNIn


def calculate_Fd_NPNDMIn(Fd_NPNCPIn):
    Fd_NPNDMIn = Fd_NPNCPIn / 2.81      # Line 493
    return Fd_NPNDMIn


def calculate_Fd_CPAIn(Fd_CPIn, Fd_CPARU):
    Fd_CPAIn = Fd_CPIn * Fd_CPARU / 100     # Line 494
    return Fd_CPAIn


def calculate_Fd_CPBIn(Fd_CPIn, Fd_CPBRU):
    Fd_CPBIn = Fd_CPIn * Fd_CPBRU / 100     # Line 495
    return Fd_CPBIn


def calculate_Fd_CPBIn_For(Fd_CPIn, Fd_CPBRU, Fd_For):
    Fd_CPBIn_For = Fd_CPIn * Fd_CPBRU / 100 * Fd_For / 100       # Line 496
    return Fd_CPBIn_For


def calculate_Fd_CPBIn_Conc(Fd_CPIn, Fd_CPBRU, Fd_Conc):
    Fd_CPBIn_Conc = Fd_CPIn * Fd_CPBRU / 100 * Fd_Conc / 100     # Line 497
    return Fd_CPBIn_Conc


def calculate_Fd_CPCIn(Fd_CPIn, Fd_CPCRU):
    Fd_CPCIn = Fd_CPIn * Fd_CPCRU / 100     # Line 498
    return Fd_CPCIn


def calculate_Fd_CPIn_ClfLiq(Fd_Category, Fd_DMIn, Fd_CP):
    Fd_CPIn_ClfLiq = np.where(
        Fd_Category == "Calf Liquid Feed", Fd_DMIn * Fd_CP / 100, 0)  # Line 499
    return Fd_CPIn_ClfLiq


def calculate_Fd_CPIn_ClfDry(Fd_Category, Fd_DMIn, Fd_CP):
    Fd_CPIn_ClfDry = np.where(
        Fd_Category == "Calf Liquid Feed", 0, Fd_DMIn * Fd_CP / 100)  # Line 500
    return Fd_CPIn_ClfDry


def calculate_Fd_rdcRUPB(Fd_For, Fd_Conc, Fd_KdRUP, coeff_dict):
    req_coeffs = ['KpFor', 'KpConc']
    check_coeffs_in_coeff_dict(coeff_dict, req_coeffs)

    Fd_rdcRUPB = 100 - (Fd_For * coeff_dict['KpFor'] / (Fd_KdRUP + coeff_dict['KpFor']) +
                        Fd_Conc * coeff_dict['KpConc'] / (Fd_KdRUP + coeff_dict['KpConc']))   # Line 514
    return Fd_rdcRUPB


def calculate_Fd_RUPBIn(Fd_For, Fd_Conc, Fd_KdRUP, Fd_CPBIn, coeff_dict):
    req_coeffs = ['KpFor', 'KpConc']
    check_coeffs_in_coeff_dict(coeff_dict, req_coeffs)

    Fd_RUPBIn = Fd_CPBIn * Fd_For/100 * coeff_dict['KpFor'] / (
        Fd_KdRUP + coeff_dict['KpFor']) + Fd_CPBIn * Fd_Conc/100 * coeff_dict['KpConc'] / (Fd_KdRUP + coeff_dict['KpConc'])      # Line 516
    return Fd_RUPBIn


def calculate_Fd_RUPIn(Fd_CPIn, Fd_CPAIn, Fd_CPCIn, Fd_NPNCPIn, Fd_RUPBIn, coeff_dict):
    req_coeffs = ['refCPIn', 'fCPAdu', 'IntRUP']
    check_coeffs_in_coeff_dict(coeff_dict, req_coeffs)

    Fd_RUPIn = (Fd_CPAIn - Fd_NPNCPIn) * coeff_dict['fCPAdu'] + Fd_RUPBIn + Fd_CPCIn + \
        coeff_dict['IntRUP'] / coeff_dict['refCPIn'] * Fd_CPIn       # Line 518
    return Fd_RUPIn


def calculate_Fd_RUP_CP(Fd_CPIn, Fd_RUPIn):
    Fd_RUP_CP = np.where(Fd_CPIn > 0, Fd_RUPIn / Fd_CPIn * 100, 0)
    return Fd_RUP_CP


def calculate_Fd_RUP(Fd_CPIn, Fd_RUPIn, Fd_DMIn):
    Fd_RUP = np.where(Fd_CPIn > 0, Fd_RUPIn / Fd_DMIn * 100, 0)  # Line 522
    return Fd_RUP


def calculate_Fd_RDP(Fd_CPIn, Fd_CP, Fd_RUP):
    Fd_RDP = np.where(Fd_CPIn > 0, Fd_CP - Fd_RUP, 0)  # Line 523
    return Fd_RDP


def calculate_Fd_OMIn(Fd_DMIn, Fd_AshIn):
    Fd_OMIn = Fd_DMIn - Fd_AshIn        # Line 543
    return Fd_OMIn


def calculate_Fd_DE_base_1(Fd_NDF, Fd_Lg, Fd_St, Fd_dcSt, Fd_FA, Fd_dcFA, Fd_Ash, Fd_CP, Fd_NPNCP, Fd_RUP, Fd_dcRUP):
    adjusted_NDF = np.where(Fd_NDF == 0, 1e-9, Fd_NDF)
    # if Fd_NDF == 0:
    #     adjusted_NDF = 1e-9
    # else:
    #     adjusted_NDF = Fd_NDF
    # # Standard Equation 1 - IVNDF not used
    # Line 548-552
    Fd_DE_base_1 = 0.75 * (Fd_NDF - Fd_Lg) * (1 - ((Fd_Lg / adjusted_NDF)**0.667)) * 0.042 \
        + Fd_St * Fd_dcSt/100 * 0.0423 \
        + Fd_FA * Fd_dcFA/100 * 0.094 \
        + (100 - (Fd_FA/1.06) - Fd_Ash - Fd_NDF - Fd_St - (Fd_CP - (Fd_NPNCP - Fd_NPNCP/2.81))) * 0.96 * 0.04 \
        + ((Fd_CP - Fd_RUP/100 * Fd_CP) + Fd_RUP/100 * Fd_CP * Fd_dcRUP/100 - Fd_NPNCP) * 0.0565 \
        + Fd_NPNCP * 0.0089 - (0.137 + 0.093 + 0.088)
    return Fd_DE_base_1


def calculate_Fd_DE_base_2(Fd_NDF, Fd_St, Fd_dcSt, Fd_FA, Fd_dcFA, Fd_Ash, Fd_CP, Fd_NPNCP, Fd_RUP, Fd_dcRUP, Fd_DNDF48_NDF):
    # Standard equation 2 - based on setting of IVNDF use switch
    # Line 554-557
    Fd_DE_base_2 = ((0.12 + 0.0061 * Fd_DNDF48_NDF) * Fd_NDF * 0.042) \
        + (Fd_St * Fd_dcSt/100 * 0.0423) \
        + (Fd_FA * Fd_dcFA/100 * 0.094) \
        + ((100 - (Fd_FA/1.06) - (Fd_CP - (Fd_NPNCP - Fd_NPNCP/2.81))
            - Fd_Ash - Fd_NDF - Fd_St) * 0.96 * 0.04) \
        + ((Fd_CP - Fd_RUP/100 * Fd_CP)
           + Fd_RUP/100 * Fd_CP * Fd_dcRUP/100 - Fd_NPNCP) * 0.0565 \
        + Fd_NPNCP * 0.0089 - (0.137 + 0.093 + 0.088)
    return Fd_DE_base_2


def calculate_Fd_DE_base(Use_DNDF_IV, Fd_DE_base_1, Fd_DE_base_2, Fd_For, Fd_FA, Fd_RDP, Fd_RUP, Fd_dcRUP, Fd_CP, Fd_Ash, Fd_dcFA, Fd_NPN, Fd_Category):
    Fd_DE_base = np.where(Use_DNDF_IV == 0, Fd_DE_base_1,
                          Fd_DE_base_2)  # Line 559

    condition = (Use_DNDF_IV == 1) & (Fd_For == 0)
    Fd_DE_base = np.where(condition, Fd_DE_base_1, Fd_DE_base)  # Line 560

    Fd_DE_base = np.where(Fd_Category == "Animal Protein",  # Line 561-563
                          0.73 * Fd_FA * 0.094 + (Fd_RDP + (Fd_RUP * Fd_dcRUP)) * 0.056 +
                          (0.96 * (100 - Fd_FA/1.06 - Fd_CP - Fd_Ash) * 0.04) - 0.318,
                          Fd_DE_base)

    Fd_DE_base = np.where(Fd_Category == "Fat Supplement",  # Line 564-565
                          Fd_FA * Fd_dcFA/100 * 0.094 + \
                          (100 - Fd_Ash - (Fd_FA/1.06) * 0.96) * 0.043 - 0.318,
                          Fd_DE_base)

    Fd_DE_base = np.where(Fd_Category == "Fatty Acid Supplement",  # Line 566
                          Fd_FA * Fd_dcFA/100 * 0.094 - 0.318,
                          Fd_DE_base)

    Fd_DE_base = np.where(Fd_Category == "Calf Liquid Feed",  # Line 567
                          (0.094 * Fd_FA + 0.057 * Fd_CP + 0.04 * \
                           (100 - Fd_Ash - Fd_CP - Fd_FA)) * 0.95,
                          Fd_DE_base)

    Fd_DE_base = np.where(Fd_Category == "Sugar/Sugar Alcohol",  # Line 568
                          (100 - Fd_Ash) * 0.04 * 0.96 - 0.318,
                          Fd_DE_base)

    Fd_DE_base = np.where(Fd_Category == "Vitamin/Mineral",  # Line 569
                          0,
                          Fd_DE_base)

    condition_2 = (Fd_Category == "Vitamin/Mineral") & (Fd_NPN > 0)
    Fd_DE_base = np.where(condition_2,  # Line 570
                          (Fd_CP * 0.089) - 0.318,
                          Fd_DE_base)
    # According to Weiss, need to set urea, ammonium phoshate and other NPN sources to: (Fd_CP * 0.089) - 0.318.
    # It appears they are set to 0 in the software, rather than as Bill specified. MDH

    return Fd_DE_base


def calculate_Fd_DEIn_base(Fd_DE_base, Fd_DMIn):
    Fd_DEIn_base = Fd_DE_base * Fd_DMIn     # Line 574
    return Fd_DEIn_base


def calculate_Fd_DEIn_base_ClfLiq(Fd_Category, Fd_DEIn_base):
    Fd_DEIn_base_ClfLiq = np.where(Fd_Category == "Calf Liquid Feed",  # Line 575
                                   Fd_DEIn_base,
                                   0)
    return Fd_DEIn_base_ClfLiq


def calculate_Fd_DEIn_base_ClfDry(Fd_Category, Fd_DEIn_base):
    Fd_DEIn_base_ClfDry = np.where(Fd_Category == "Calf Liquid Feed",  # Line 576
                                   0,
                                   Fd_DEIn_base)
    return Fd_DEIn_base_ClfDry


def calculate_Fd_DMIn_ClfLiq(An_StatePhys, Fd_DMIn, Fd_Category):
    condition = (An_StatePhys == "Calf") & (
        Fd_Category == "Calf Liquid Feed")  # Line 283
    Fd_DMIn_ClfLiq = np.where(condition, Fd_DMIn, 0)  # milk intake
    return Fd_DMIn_ClfLiq


def calculate_Fd_DE_ClfLiq(An_StatePhys, Fd_Category, Fd_GE):
    condition = (An_StatePhys == "Calf") & (
        Fd_Category == "Calf Liquid Feed")  # Line 284
    # prelim estimate for DMI only, mcal/kg, nutrients are in %
    Fd_DE_ClfLiq = np.where(condition, 0.95 * Fd_GE, 0)
    return Fd_DE_ClfLiq


def calculate_Fd_ME_ClfLiq(An_StatePhys, Fd_Category, Fd_DE_ClfLiq):
    condition = (An_StatePhys == "Calf") & (
        Fd_Category == "Calf Liquid Feed")  # Line 285
    Fd_ME_ClfLiq = np.where(condition, Fd_DE_ClfLiq *
                            0.96, 0)  # mcal/kg, nutrients are in %
    return Fd_ME_ClfLiq


def calculate_Fd_DMIn_ClfFor(DMI, Fd_Conc, Fd_DMInp):
    Fd_DMIn_ClfFor = (1 - Fd_Conc/100) * DMI * Fd_DMInp  # Line 296
    return Fd_DMIn_ClfFor


def calculate_Fd_PinorgIn(Fd_PIn, Fd_Pinorg_P):
    Fd_PinorgIn = Fd_PIn * Fd_Pinorg_P / 100  # Line 731, ??Check Bill's text
    return Fd_PinorgIn


def calculate_Fd_PorgIn(Fd_PIn, Fd_Porg_P):
    # Line 732 Fd_PphytIn = Fd_PIn*Fd_Pphyt_P/100 #Depracated by Bill.  Reduced to inorganic and organic.
    Fd_PorgIn = Fd_PIn * Fd_Porg_P / 100
    return Fd_PorgIn


def calculate_Fd_MgIn_min(Fd_Category, Fd_MgIn):
    Fd_MgIn_min = np.where(Fd_Category == "Vitamin/Mineral",    # Line 735
                           Fd_MgIn,
                           0)
    return Fd_MgIn_min


def calculate_Fd_acCa(An_StatePhys, Fd_acCa, Dt_DMIn_ClfLiq):
    condition = (An_StatePhys == "Calf") & (Dt_DMIn_ClfLiq > 0)  # Line 1839
    Fd_acCa = np.where(condition,
                       1,
                       Fd_acCa)
    condition2 = (An_StatePhys == "Calf") & (Dt_DMIn_ClfLiq == 0)   # Line 1840
    Fd_acCa = np.where(condition2,
                       0.60,
                       Fd_acCa)
    return Fd_acCa


def calculate_Fd_acPtot(An_StatePhys, Fd_Category, Fd_Pinorg_P, Fd_Porg_P, Fd_acPtot, Dt_DMIn_ClfLiq):
    Fd_acPtot = np.where(Fd_Category == "Vitamin/Mineral",  # Line 1841
                         Fd_acPtot,
                         Fd_Pinorg_P * 0.0084 + Fd_Porg_P * 0.0068)
    condition = (An_StatePhys == "Calf") & (Dt_DMIn_ClfLiq > 0)  # Line 1842
    Fd_acPtot = np.where(condition,
                         1,
                         Fd_acPtot)
    condition2 = (An_StatePhys == "Calf") & (Dt_DMIn_ClfLiq == 0)  # Line 1843
    Fd_acPtot = np.where(condition2,
                         0.75,
                         Fd_acPtot)

    return Fd_acPtot


def calculate_Fd_acMg(An_StatePhys, Fd_acMg, Dt_DMIn_ClfLiq):
    condition = (An_StatePhys == "Calf") & (Dt_DMIn_ClfLiq > 0)  # Line 1844
    Fd_acMg = np.where(condition,
                       1,
                       Fd_acMg)
    condition2 = (An_StatePhys == "Calf") & (Dt_DMIn_ClfLiq == 0)   # line 1845
    Fd_acMg = np.where(condition2,
                       0.26,
                       Fd_acMg)
    return Fd_acMg


def calculate_Fd_acNa(An_StatePhys, Fd_acNa):
    Fd_acNa = np.where(An_StatePhys == "Calf",  # Line 1846
                       1.0,
                       Fd_acNa)
    return Fd_acNa


def calculate_Fd_acK(An_StatePhys, Fd_acK):
    Fd_acK = np.where(An_StatePhys == "Calf",   # Line 1847
                      1.0,
                      Fd_acK)
    return Fd_acK


def calculate_Fd_acCl(An_StatePhys, Fd_acCl, Dt_DMIn_ClfLiq):
    condition = (An_StatePhys == "Calf") & (Dt_DMIn_ClfLiq > 0)  # Line 1848
    Fd_acCl = np.where(condition,
                       1,
                       Fd_acCl)
    condition2 = (An_StatePhys == "Calf") & (Dt_DMIn_ClfLiq == 0)   # line 1849
    Fd_acCl = np.where(condition2,
                       0.92,
                       Fd_acCl)
    return Fd_acCl


def calculate_Fd_absCaIn(Fd_CaIn, Fd_acCa):
    Fd_absCaIn = Fd_CaIn * Fd_acCa  # line 1851
    return Fd_absCaIn


def calculate_Fd_absPIn(Fd_PIn, Fd_acPtot):
    Fd_absPIn = Fd_PIn * Fd_acPtot  # line 1852
    return Fd_absPIn


def calculate_Fd_absMgIn_base(Fd_MgIn, Fd_acMg):
    Fd_absMgIn_base = Fd_MgIn * Fd_acMg     # line 1853
    return Fd_absMgIn_base


def calculate_Fd_absNaIn(Fd_NaIn, Fd_acNa):
    Fd_absNaIn = Fd_NaIn * Fd_acNa      # line 1854
    return Fd_absNaIn


def calculate_Fd_absKIn(Fd_KIn, Fd_acK):
    Fd_absKIn = Fd_KIn * Fd_acK     # line 1855
    return Fd_absKIn


def calculate_Fd_absClIn(Fd_ClIn, Fd_acCl):
    Fd_absClIn = Fd_ClIn * Fd_acCl      # line 1856
    return Fd_absClIn


def calculate_Fd_acCo(An_StatePhys):
    Fd_acCo = np.where(An_StatePhys == "Calf",  # Line 1860
                       0,
                       1.0)
    return Fd_acCo


def calculate_Fd_acCu(An_StatePhys, Fd_acCu, Dt_DMIn_ClfLiq):
    Fd_acCu = np.where(An_StatePhys == "Calf",  # Line 1861
                       1.0,
                       Fd_acCu)
    condition = (An_StatePhys == "Calf") & (Dt_DMIn_ClfLiq == 0)
    Fd_acCu = np.where(condition,               # Line 1862
                       0.10,
                       Fd_acCu)
    return Fd_acCu


def calculate_Fd_acFe(An_StatePhys, Fd_acFe, Dt_DMIn_ClfLiq):
    Fd_acFe = np.where(An_StatePhys == "Calf",  # Line 1863
                       1.0,
                       Fd_acFe)
    condition = (An_StatePhys == "Calf") & (Dt_DMIn_ClfLiq == 0)
    Fd_acFe = np.where(condition,               # Line 1864
                       0.10,
                       Fd_acFe)
    return Fd_acFe


def calculate_Fd_acMn(An_StatePhys, Fd_acMn, Dt_DMIn_ClfLiq):
    Fd_acMn = np.where(An_StatePhys == "Calf",  # Line 1865
                       1.0,
                       Fd_acMn)
    condition = (An_StatePhys == "Calf") & (Dt_DMIn_ClfLiq == 0)
    Fd_acMn = np.where(condition,   # Line 1866
                       0.005,
                       Fd_acMn)
    return Fd_acMn


def calculate_Fd_acZn(An_StatePhys, Fd_acZn, Dt_DMIn_ClfLiq):
    Fd_acZn = np.where(An_StatePhys == " Calf",     # Line 1867
                       1.0,
                       Fd_acZn)
    condition = (An_StatePhys == "Calf") & (Dt_DMIn_ClfLiq == 0)
    Fd_acZn = np.where(condition,                   # Line 1868
                       0.20,
                       Fd_acZn)
    return Fd_acZn


def calculate_Fd_DigSt(Fd_St, Fd_dcSt):
    Fd_DigSt = Fd_St * Fd_dcSt / 100       # Line 1014
    return Fd_DigSt


def calculate_Fd_DigStIn_Base(Fd_DigSt, Fd_DMIn):
    Fd_DigStIn_Base = Fd_DigSt / 100 * Fd_DMIn  # Line 1015
    return Fd_DigStIn_Base


def calculate_Fd_DigrOMt(Fd_rOM, coeff_dict):
    req_coeff = ['Fd_dcrOM']
    check_coeffs_in_coeff_dict(coeff_dict, req_coeff)
    # Truly digested rOM in each feed, % of DM
    Fd_DigrOMt = coeff_dict['Fd_dcrOM'] / 100 * Fd_rOM
    return Fd_DigrOMt


def calculate_Fd_DigrOMtIn(Fd_DigrOMt, Fd_DMIn):
    Fd_DigrOMtIn = Fd_DigrOMt / 100 * Fd_DMIn		# Line 1010, kg/d
    return Fd_DigrOMtIn


def calculate_Fd_idRUPIn(Fd_dcRUP, Fd_RUPIn):
    # Line 1072, dcRUP is the RUP DC by feed read in from the Feed Matrix.
    Fd_idRUPIn = (Fd_dcRUP / 100) * Fd_RUPIn
    return Fd_idRUPIn


def calculate_TT_dcFdFA(An_StatePhys, Fd_Category, Fd_Type, Fd_dcFA, coeff_dict):
    req_coeff = ['TT_dcFA_Base', 'TT_dcFat_Base',
                 'TT_dcFA_ClfDryFd', 'TT_dcFA_ClfLiqFd']
    check_coeffs_in_coeff_dict(coeff_dict, req_coeff)

    TT_dcFdFA = Fd_dcFA  # Line 1251

    condition_1 = (np.isnan(TT_dcFdFA).any()) and (
        Fd_Category == "Fatty Acid Supplement")
    TT_dcFdFA = np.where(
        condition_1, coeff_dict['TT_dcFA_Base'], TT_dcFdFA)    # Line 1252

    condition_2 = (np.isnan(TT_dcFdFA).any()) and (
        Fd_Category == "Fat Supplement")
    TT_dcFdFA = np.where(
        condition_2, coeff_dict['TT_dcFat_Base'], TT_dcFdFA)   # Line 1253

    # Lien 1254, Fill in any remaining missing values with fat dc
    TT_dcFdFA = np.where(np.isnan(TT_dcFdFA).any(),
                         coeff_dict['TT_dcFat_Base'], TT_dcFdFA)

    condition_3 = (An_StatePhys == "Calf") and (
        Fd_Category != "Calf Liquid Feed") and (Fd_Type == "Concentrate")
    # Line 1255, likely an over estimate for forage
    TT_dcFdFA = np.where(
        condition_3, coeff_dict['TT_dcFA_ClfDryFd'], TT_dcFdFA)

    condition_4 = (np.isnan(TT_dcFdFA).any()) and (
        An_StatePhys == "Calf") and (Fd_Category == "Calf Liquid Feed")
    # Line 1256, Default if dc is not entered.
    TT_dcFdFA = np.where(condition_4, ['TT_dcFA_ClfLiqFd'], TT_dcFdFA)

    # Convert back into a Pandas series, using np.isnan converts to a numpy array
    TT_dcFdFA = pd.Series(TT_dcFdFA)
    TT_dcFdFA = pd.to_numeric(
        TT_dcFdFA, errors='coerce').fillna(0).astype(float)
    return TT_dcFdFA


def calculate_Fd_DigFAIn(TT_dcFdFA, Fd_FA, Fd_DMIn):
    Fd_DigFAIn = TT_dcFdFA / 100 * Fd_FA / 100 * Fd_DMIn
    return Fd_DigFAIn


def calculate_Fd_DigrOMa(Fd_DigrOMt: float, coeff_dict: dict) -> float:
    """
    Fd_DigrOMa: Apparently digested residual organic matter, % DM
    """
    req_coeff = ['Fe_rOMend_DMI']
    check_coeffs_in_coeff_dict(coeff_dict, req_coeff)
    Fd_DigrOMa = Fd_DigrOMt - coeff_dict['Fe_rOMend_DMI'] # Line 1008
    # Apparently digested (% DM). Generates some negative values for minerals and other low rOM feeds.
    return Fd_DigrOMa


def calculate_Fd_DigrOMaIn(Fd_DigrOMa: float, Fd_DMIn: float) -> float:  
    """
    Fd_DigrOMaIn: Apparently digested residual organic matter intkae, kg/d
    """
    Fd_DigrOMaIn = Fd_DigrOMa / 100 * Fd_DMIn   # kg/d, Line 1009
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
    Fd_DigWSCIn = Fd_DigWSC / 100 * Fd_DMIn # Line 1012
    return Fd_DigWSCIn


def calculate_Fd_idRUP(Fd_CPIn: float | pd.Series, Fd_idRUPIn: float | pd.Series, Fd_DMIn: float | pd.Series) -> float | pd.Series:
    """
    Fd_idRUP: Intestinally digested RUP, % DM
    """
    Fd_idRUP = np.where(Fd_CPIn > 0, Fd_idRUPIn / Fd_DMIn * 100, 0) # Line 1073
    return Fd_idRUP


def calculate_Fd_Fe_RUPout(Fd_RUPIn: float | pd.Series, Fd_dcRUP: float | pd.Series) -> float | pd.Series:
    """
    Fd_Fe_RUPout: Fecal RUP output, kg/d
    """
    Fd_Fe_RUPout = Fd_RUPIn * (1 - Fd_dcRUP / 100)  # Line 1078
    return Fd_Fe_RUPout


####################
# Functions for Diet Intakes
####################


def calculate_Dt_ForDNDF48(Fd_DMInp, Fd_Conc, Fd_NDF, Fd_DNDF48):
    Dt_ForDNDF48 = ((1 - Fd_Conc/100) * Fd_NDF * Fd_DNDF48 /
                    100 * Fd_DMInp).sum()    # Line 259
    return Dt_ForDNDF48


def calculate_Dt_ForDNDF48_ForNDF(Dt_ForDNDF48, Dt_ForNDF):
    Dt_ForDNDF48_ForNDF = Dt_ForDNDF48 / Dt_ForNDF * 100    # Line 260
    return Dt_ForDNDF48_ForNDF


def calculate_Dt_ADF_NDF(Dt_ADF, Dt_NDF):
    Dt_ADF_NDF = Dt_ADF/Dt_NDF     # Line 261
    return Dt_ADF_NDF


def calculate_Dt_DE_ClfLiq(Dt_DEIn_ClfLiq, Dt_DMIn_ClfLiq):
    # Line 289, DE content of the liquid feed
    Dt_DE_ClfLiq = Dt_DEIn_ClfLiq / Dt_DMIn_ClfLiq
    Dt_DE_ClfLiq = np.where(Dt_DE_ClfLiq.isnan(), 0, Dt_DE_ClfLiq)  # Line 290
    return Dt_DE_ClfLiq


def calculate_Dt_ME_ClfLiq(Dt_MEIn_ClfLiq, Dt_DMIn_ClfLiq):
    # Line 291, ME content of the liquid feed
    Dt_ME_ClfLiq = Dt_MEIn_ClfLiq / Dt_DMIn_ClfLiq
    Dt_ME_ClfLiq = np.where(Dt_ME_ClfLiq.isnan())   # Line 292
    return Dt_ME_ClfLiq


def calculate_Dt_NDFnfIn(Fd_DMIn, Fd_NDFnf):
    Dt_NDFnfIn = (Fd_NDFnf / 100 * Fd_DMIn).sum()   # Line 588
    return Dt_NDFnfIn


def calculate_Dt_Lg_NDF(Dt_LgIn, Dt_NDFIn):
    Dt_Lg_NDF = Dt_LgIn / Dt_NDFIn * 100  # Line 591
    return Dt_Lg_NDF


def calculate_Dt_ForNDFIn(Fd_DMIn, Fd_ForNDF):
    Dt_ForNDFIn = (Fd_ForNDF / 100 * Fd_DMIn).sum()  # Line 592
    return Dt_ForNDFIn


def calculate_Dt_PastSupplIn(Dt_DMInSum, Dt_PastIn):
    # Line 597, Could be supplemental concentrate or forage
    Dt_PastSupplIn = Dt_DMInSum - Dt_PastIn
    return Dt_PastSupplIn


def calculate_Dt_NIn(Dt_CPIn):
    Dt_NIn = Dt_CPIn / 6.25  # Line 614
    return Dt_NIn


def calculate_Dt_RUPIn(Dt_CPAIn, Dt_NPNIn, Dt_RUPBIn, Dt_CPCIn, coeff_dict, Fd_RUPIn=None):
    req_coeffs = ['fCPAdu', 'IntRUP']
    check_coeffs_in_coeff_dict(coeff_dict, req_coeffs)
    # The feed summation is not as accurate as the equation below
    Dt_RUPIn = Fd_RUPIn.sum()   # Line 616
    Dt_RUPIn = np.where(Dt_RUPIn < 0, 0, Dt_RUPIn)  # Line 617

    # The following diet level RUPIn is slightly more accurate than the feed level summation as the intercept exactly matches the regression equations, but feed level is very close.
    # if concerned about intercept, switch to using this eqn for RUP
    # Dt_RUPIn = (Dt_CPAIn - Dt_NPNIn) * coeff_dict['fCPAdu'] + Dt_RUPBIn + Dt_CPCIn + coeff_dict['IntRUP']   # Line 619
    return Dt_RUPIn


def calculate_Dt_RUP_CP(Dt_CPIn, Dt_RUPIn):
    Dt_RUP_CP = Dt_RUPIn / Dt_CPIn * 100    # Line 621
    return Dt_RUP_CP


def calculate_Dt_fCPBdu(Dt_RUPBIn, Dt_CPBIn):
    Dt_fCPBdu = Dt_RUPBIn / Dt_CPBIn    # Line 622
    return Dt_fCPBdu


def calculate_Dt_UFAIn(Dt_C161In, Dt_C181tIn, Dt_C181cIn, Dt_C182In, Dt_C183In):
    Dt_UFAIn = Dt_C161In + Dt_C181tIn + Dt_C181cIn + \
        Dt_C182In + Dt_C183In   # Line 639
    return Dt_UFAIn


def calculate_Dt_MUFAIn(Dt_C161In, Dt_C181tIn, Dt_C181cIn):
    Dt_MUFAIn = Dt_C161In + Dt_C181tIn + Dt_C181cIn  # Line 640
    return Dt_MUFAIn


def calculate_Dt_PUFAIn(Dt_UFAIn, Dt_C161In, Dt_C181tIn, Dt_C181cIn):
    Dt_PUFAIn = Dt_UFAIn - (Dt_C161In + Dt_C181tIn + Dt_C181cIn)  # Line 641
    return Dt_PUFAIn


def calculate_Dt_SatFAIn(Dt_FAIn, Dt_UFAIn):
    Dt_SatFAIn = Dt_FAIn - Dt_UFAIn     # Line 642
    return Dt_SatFAIn


def calculate_Dt_OMIn(DMI, Dt_AshIn):
    Dt_OMIn = DMI - Dt_AshIn    # Line 645
    return Dt_OMIn


def calculate_Dt_rOMIn(DMI, Dt_AshIn, Dt_NDFIn, Dt_StIn, Dt_FAhydrIn, Dt_TPIn, Dt_NPNDMIn):
    Dt_rOMIn = DMI - Dt_AshIn - Dt_NDFIn - Dt_StIn - \
        Dt_FAhydrIn - Dt_TPIn - Dt_NPNDMIn     # Line 646
    # Is negative on some diets. Some Ash and CP in NDF, and water from FAhydr in TAG contributes.
    # Trap negative Dt values. More likely due to entry errors or bad analyses of other nutrients
    Dt_rOMIn = np.where(Dt_rOMIn < 0, 0, Dt_rOMIn)  # Line 647
    return Dt_rOMIn


def calculate_Dt_DM(DMI, Dt_AFIn):
    Dt_DM = DMI / Dt_AFIn * 100     # Line 655
    return Dt_DM


def calculate_Dt_NDFIn_BW(An_BW, Dt_NDFIn):
    Dt_NDFIn_BW = Dt_NDFIn / An_BW * 100    # Line 658
    return Dt_NDFIn_BW


def calculate_Dt_ForNDF_NDF(Dt_ForNDF, Dt_NDF):
    Dt_ForNDF_NDF = Dt_ForNDF / Dt_NDF * 100    # Line 663
    return Dt_ForNDF_NDF


def calculate_Dt_ForNDFIn_BW(An_BW, Dt_ForNDFIn):
    Dt_ForNDFIn_BW = Dt_ForNDFIn / An_BW * 100  # Line 664
    return Dt_ForNDFIn_BW


def calculate_Dt_DMInSum(Fd_DMIn):
    Dt_DMInSum = Fd_DMIn.sum()  # Line 579
    return Dt_DMInSum


def calculate_Dt_DEIn_ClfLiq(Fd_DE_ClfLiq, Fd_DMIn_ClfLiq):
    Dt_DEIn_ClfLiq = (Fd_DE_ClfLiq * Fd_DMIn_ClfLiq).sum()  # Line 287
    return Dt_DEIn_ClfLiq


def calculate_Dt_MEIn_ClfLiq(Fd_ME_ClfLiq, Fd_DMIn_ClfLiq):
    Dt_MEIn_ClfLiq = (Fd_ME_ClfLiq * Fd_DMIn_ClfLiq).sum()  # Line 288
    return Dt_MEIn_ClfLiq


def calculate_Dt_CPA_CP(Dt_CPAIn, Dt_CPIn):
    Dt_CPA_CP = Dt_CPAIn / Dt_CPIn * 100    # Line 684
    return Dt_CPA_CP


def calculate_Dt_CPB_CP(Dt_CPBIn, Dt_CPIn):
    Dt_CPB_CP = Dt_CPBIn / Dt_CPIn * 100    # Line 685
    return Dt_CPB_CP


def calculate_Dt_CPC_CP(Dt_CPCIn, Dt_CPIn):
    Dt_CPC_CP = Dt_CPCIn / Dt_CPIn * 100    # Line 686
    return Dt_CPC_CP


def calculate_Dt_RDPIn(Dt_CPIn, Dt_RUPIn):
    Dt_RDPIn = Dt_CPIn - Dt_RUPIn   # Line 1101
    return Dt_RDPIn


def calculate_Dt_DigNDFIn(TT_dcNDF, Dt_NDFIn):
    Dt_DigNDFIn = TT_dcNDF / 100 * Dt_NDFIn
    return Dt_DigNDFIn


def calculate_Dt_DigStIn(Dt_StIn, TT_dcSt):
    Dt_DigStIn = Dt_StIn * TT_dcSt / 100    # Line 1032
    return Dt_DigStIn


def calculate_Dt_DigrOMaIn(Dt_DigrOMtIn, Fe_rOMend):
    Dt_DigrOMaIn = Dt_DigrOMtIn - Fe_rOMend
    return Dt_DigrOMaIn


def calculate_Dt_dcCP_ClfDry(An_StatePhys, Dt_DMIn_ClfLiq):
    condition = (An_StatePhys == "Calf") and (Dt_DMIn_ClfLiq < 0.01)
    Dt_dcCP_ClfDry = np.where(condition, 0.70, 0.75)    # Line 1199
    return Dt_dcCP_ClfDry


def calculate_Dt_DENDFIn(Dt_DigNDFIn, coeff_dict):
    req_coeff = ['En_NDF']
    check_coeffs_in_coeff_dict(coeff_dict, req_coeff)
    Dt_DENDFIn = Dt_DigNDFIn * coeff_dict['En_NDF']
    return Dt_DENDFIn


def calculate_Dt_DEStIn(Dt_DigStIn, coeff_dict):
    req_coeff = ['En_St']
    check_coeffs_in_coeff_dict(coeff_dict, req_coeff)
    Dt_DEStIn = Dt_DigStIn * coeff_dict['En_St']
    return Dt_DEStIn


def calculate_Dt_DErOMIn(Dt_DigrOMaIn, coeff_dict):
    req_coeff = ['En_rOM']
    check_coeffs_in_coeff_dict(coeff_dict, req_coeff)
    Dt_DErOMIn = Dt_DigrOMaIn * coeff_dict['En_rOM']    # Line 1344
    return Dt_DErOMIn


def calculate_Dt_DENPNCPIn(Dt_NPNCPIn, coeff_dict):
    req_coeff = ['En_NPNCP']
    check_coeffs_in_coeff_dict(coeff_dict, req_coeff)
    Dt_DENPNCPIn = Dt_NPNCPIn * \
        coeff_dict['dcNPNCP'] / 100 * coeff_dict['En_NPNCP']
    return Dt_DENPNCPIn


def calculate_Dt_DEFAIn(Dt_DigFAIn, coeff_dict):
    req_coeff = ['En_FA']
    check_coeffs_in_coeff_dict(coeff_dict, req_coeff)
    Dt_DEFAIn = Dt_DigFAIn * coeff_dict['En_FA']
    return Dt_DEFAIn


# This function is invovled in the calf DMIn prediction. In the future we will liekly need to pull a few of the calf intake calculations 
# out of the wrappers to run DMI prediciton properly. It all depends on how we handle the calf calculations which hasn't been decided yet
def calculate_Dt_DMIn_ClfStrt(An_BW, Dt_MEIn_ClfLiq, Dt_DMIn_ClfLiq, Dt_DMIn_ClfFor, An_AgeDryFdStart, Env_TempCurr, DMIn_eqn, Trg_Dt_DMIn, coeff_dict):
    req_coeff = ['UCT']
    check_coeffs_in_coeff_dict(coeff_dict, req_coeff)
    # Predict Calf Starter Intake, kg/d
    # Temperate Environment Predicted Starter Intake
    Dt_DMIn_ClfStrt = (-652.5 + 14.734 * An_BW + 18.896 * Dt_MEIn_ClfLiq    # Line 301
                       + 73.3 * An_AgeDryFdStart / 7 
                       + 13.496 * (An_AgeDryFdStart/7)**2 
                       - 29.614 * An_AgeDryFdStart / 7 * Dt_MEIn_ClfLiq) / 1000
    #Tropical Environment Predicted Starter Intake, TempCurr > UCT + 10 degrees C. 
    Dt_DMIn_ClfStrt = np.where(Env_TempCurr > (coeff_dict['UCT'] + 10),     # Line 305
                               (600.1 * (1 + 14863.7 * np.exp(-1.553 * An_AgeDryFdStart / 7))**-1 + 9.951 * An_BW - 130.434 * Dt_MEIn_ClfLiq) / 1000,
                               Dt_DMIn_ClfStrt)
    condition = (DMIn_eqn==0) and ((Dt_DMIn_ClfLiq + Dt_DMIn_ClfStrt + Dt_DMIn_ClfFor) != Trg_Dt_DMIn)
    Dt_DMIn_ClfStrt = np.where(condition,   # Line 311
                               Trg_Dt_DMIn - Dt_DMIn_ClfLiq - Dt_DMIn_ClfFor,
                               Dt_DMIn_ClfStrt) # Adjust Starter Intake based on target intake if DMIeqn=0.
    return Dt_DMIn_ClfStrt


def calculate_Dt_DigCPaIn(Dt_CPIn, Fe_CP):
    Dt_DigCPaIn = Dt_CPIn - Fe_CP  # kg CP/d, apparent total tract digested CP
    return Dt_DigCPaIn


def calculate_Dt_DECPIn(Dt_DigCPaIn, coeff_dict):
    req_coeff = ['En_CP']
    check_coeffs_in_coeff_dict(coeff_dict, req_coeff)
    Dt_DECPIn = Dt_DigCPaIn * coeff_dict['En_CP']
    return Dt_DECPIn


def calculate_Dt_DETPIn(Dt_DECPIn, Dt_DENPNCPIn, coeff_dict):
    req_coeff = ['En_NPNCP', 'En_CP']
    check_coeffs_in_coeff_dict(coeff_dict, req_coeff)
    # Line 1348, Caution! DigTPaIn not clean so subtracted DE for CP equiv of NPN to correct. Not a true DE_TP.
    Dt_DETPIn = Dt_DECPIn - Dt_DENPNCPIn / \
        coeff_dict['En_NPNCP'] * coeff_dict['En_CP']
    return Dt_DETPIn


def calculate_Dt_DEIn(An_StatePhys, Dt_DENDFIn, Dt_DEStIn, Dt_DErOMIn, Dt_DETPIn, Dt_DENPNCPIn, Dt_DEFAIn, Dt_DMIn_ClfLiq, Dt_DEIn_base_ClfLiq, Dt_DEIn_base_ClfDry, Monensin_eqn):
    Dt_DEIn = Dt_DENDFIn + Dt_DEStIn + Dt_DErOMIn + \
        Dt_DETPIn + Dt_DENPNCPIn + Dt_DEFAIn   # Line 1365
    condition = (An_StatePhys == "Calf") and (Dt_DMIn_ClfLiq > 0)
    Dt_DEIn = np.where(condition, Dt_DEIn_base_ClfLiq +
                       Dt_DEIn_base_ClfDry, Dt_DEIn)   # Line 1371
    Dt_DEIn = np.where(Monensin_eqn == 1, Dt_DEIn *
                       1.02, Dt_DEIn)       # Line 1374
    return Dt_DEIn


def calculate_Dt_acMg(An_StatePhys: str, Dt_K: float, Dt_MgIn_min: float, Dt_MgIn: float) -> float:
    Dt_acMg = np.where(An_StatePhys == "Calf",  # Line 1880
                       1,
                       (44.1 - 5.42 * math.log(Dt_K * 10) - 0.08 * Dt_MgIn_min / Dt_MgIn * 100) / 100)
    return Dt_acMg


def calculate_Abs_MgIn(Dt_acMg: float, Dt_MgIn: float) -> float:
    Abs_MgIn = Dt_acMg * Dt_MgIn    # Mg absorption is inhibited by K, Line 1881
    return Abs_MgIn


def calculate_Dt_DigWSCIn(Fd_DigWSCIn: float) -> float:
    """
    Dt_DigWSCIn: Digestable water soluble carbohydrate intake, kg/d
    """
    Dt_DigWSCIn = sum(Fd_DigWSCIn)	# This is not used as it isn't additive with St, MDH. Line 1019
    return Dt_DigWSCIn


def calculate_Dt_DigSt(Dt_DigStIn: float, Dt_DMIn: float) -> float:
    """
    Dt_DigSt: Digestable starch, % DM
    """
    Dt_DigSt = Dt_DigStIn / Dt_DMIn * 100   # Line 1036
    return Dt_DigSt


def calculate_Dt_DigWSC(Dt_DigWSCIn: float, Dt_DMIn: float) -> float:
    """
    Dt_DigWSC: Digestable water soluble carbohydrate, % DM
    """
    Dt_DigWSC = Dt_DigWSCIn / Dt_DMIn * 100 # line 1038
    return Dt_DigWSC


def calculate_Dt_DigrOMa(Dt_DigrOMaIn: float, Dt_DMIn: float) -> float:
    """
    Dt_DigrOMa: Apparently digestable residual organic matter, % DM
    """
    Dt_DigrOMa = Dt_DigrOMaIn / Dt_DMIn * 100   # Line 1040
    return Dt_DigrOMa


def calculate_Dt_DigrOMa_Dt(Dt_rOM: float, coeff_dict: dict) -> float:
    """
    Dt_DigrOMa_Dt: Apparently digestable residual organic matter, % DM???
    
    This variable is not used anywhere, used as crosscheck? (see comment)
    """
    req_coeff = ['Fe_rOMend_DMI']
    check_coeffs_in_coeff_dict(coeff_dict, req_coeff)
    # In R code variable is Dt_DigrOMa.Dt
    Dt_DigrOMa_Dt = Dt_rOM * 0.96 - coeff_dict['Fe_rOMend_DMI']   # Crosscheck the feed level calculation and summation., Line 1041
    return Dt_DigrOMa_Dt


def calculate_Dt_DigrOMt(Dt_DigrOMtIn: float, Dt_DMIn: float) -> float:
    """
    Dt_DigrOMt: Truly digested residual organic matter, % DM
    """
    Dt_DigrOMt = Dt_DigrOMtIn / Dt_DMIn * 100   # Line 1042
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
    Dt_idcRUP = Dt_idRUPIn / Dt_RUPIn * 100  # Intestinal digestibility of RUP, Line 1075
    return Dt_idcRUP


def calculate_Dt_Fe_RUPout(Fd_Fe_RUPout: float | pd.Series) -> float:
    """
    Dt_Fe_RUPout: Fecal rumed undegradable protein output from diet, kg/d
    """
    Dt_Fe_RUPout  = Fd_Fe_RUPout.sum()  # Line 1081 
    return Dt_Fe_RUPout


def calculate_Dt_RDTPIn(Dt_RDPIn: float, Dt_NPNCPIn: float, coeff_dict: dict) -> float:
    """
    Dt_RDTPIn: Rumed degradable true protein intake, kg/d
    """
    req_coeff = ['dcNPNCP']
    check_coeffs_in_coeff_dict(coeff_dict, req_coeff)
    Dt_RDTPIn = Dt_RDPIn - (Dt_NPNCPIn * coeff_dict['dcNPNCP'] / 100)  # assumes all NPN is soluble.  Reflects only urea and ammonium salt NPN sources, Line 1102
    return Dt_RDTPIn


def calculate_Dt_RDP(Dt_RDPIn: float, Dt_DMIn: float) -> float:
    """
    Dt_RDP: Diet rumed degradable protein, % DM
    """
    Dt_RDP = Dt_RDPIn / Dt_DMIn * 100   # Line 1103
    return Dt_RDP


def calculate_Dt_RDP_CP(Dt_RDP: float, Dt_CP: float) -> float:
    """
    Dt_RDP_CP: Diet rumed degradable protein % of crude protein
    """
    Dt_RDP_CP = Dt_RDP / Dt_CP * 100   # Line 1104
    return Dt_RDP_CP


####################
# Functions for Digestability Coefficients
####################
# These values are used for calculating Dt_ level intakes
# They could be put in a seperate .py file or be run seperately but that would
# mean diet_data is calculated in two steps


def calculate_TT_dcNDF_Base(Dt_DigNDFIn_Base, Dt_NDFIn):
    TT_dcNDF_Base = Dt_DigNDFIn_Base / Dt_NDFIn * 100               # Line 1056
    if math.isnan(TT_dcNDF_Base) is True:
        TT_dcNDF_Base = 0
    return TT_dcNDF_Base


def calculate_TT_dcNDF(TT_dcNDF_Base, Dt_StIn, Dt_DMIn, An_DMIn_BW):
    TT_dcNDF = np.where(TT_dcNDF_Base == 0,
                        0,
                        (TT_dcNDF_Base / 100 - 0.59 * (Dt_StIn / Dt_DMIn - 0.26) - 1.1 * (An_DMIn_BW - 0.035)) * 100)  # Line 1060
    return TT_dcNDF


def calculate_TT_dcSt_Base(Dt_DigStIn_Base, Dt_StIn):
    TT_dcSt_Base = Dt_DigStIn_Base / Dt_StIn * 100                    # Line 1030
    if math.isnan(TT_dcSt_Base) is True:
        TT_dcSt_Base = 0
    return TT_dcSt_Base


def calculate_TT_dcSt(TT_dcSt_Base, An_DMIn_BW):
    TT_dcSt = np.where(TT_dcSt_Base == 0, 0, TT_dcSt_Base -
                       (1.0 * (An_DMIn_BW - 0.035)) * 100)
    return TT_dcSt


def calculate_TT_dcAnSt(An_DigStIn: float, Dt_StIn: float, Inf_StIn: float) -> float:
    """
    TT_dcAnSt: Starch total tract digestability coefficient
    """
    TT_dcAnSt = An_DigStIn / (Dt_StIn + Inf_StIn) * 100 # Line 1034
    if np.isnan(TT_dcAnSt):   # Line 1035
        TT_dcAnSt = 0
    return TT_dcAnSt


def calculate_TT_dcrOMa(An_DigrOMaIn: float, Dt_rOMIn: float, InfRum_GlcIn: float, InfRum_AcetIn: float, InfRum_PropIn: float, InfRum_ButrIn: float, InfSI_GlcIn: float, InfSI_AcetIn: float, InfSI_PropIn: float, InfSI_ButrIn: float) -> float:
    """
    TT_dcrOMa: Apparent digested residual organic matter total tract digestability coefficient
    """
    TT_dcrOMa = An_DigrOMaIn / (Dt_rOMIn + InfRum_GlcIn + InfRum_AcetIn + InfRum_PropIn + InfRum_ButrIn + InfSI_GlcIn + InfSI_AcetIn + InfSI_PropIn + InfSI_ButrIn) * 100   # Line 1047-1048
    return TT_dcrOMa


def calculate_TT_dcrOMt(An_DigrOMtIn: float, Dt_rOMIn: float, InfRum_GlcIn: float, InfRum_AcetIn: float, InfRum_PropIn: float, InfRum_ButrIn: float, InfSI_GlcIn: float, InfSI_AcetIn: float, InfSI_PropIn: float, InfSI_ButrIn: float) -> float:
    """
    TT_dcrOMt: Truly digested residual organic matter total tract digestability coefficient
    """
    TT_dcrOMt = An_DigrOMtIn / (Dt_rOMIn + InfRum_GlcIn + InfRum_AcetIn + InfRum_PropIn + InfRum_ButrIn + InfSI_GlcIn + InfSI_AcetIn + InfSI_PropIn + InfSI_ButrIn) * 100   # Line 1049-1050
    return TT_dcrOMt


def calculate_Dt_DigCPtIn(An_StatePhys: str, Dt_DigCPaIn: float, Fe_CPend: float, Dt_RDPIn: float, Dt_idRUPIn: float) -> float:
    """
    Dt_DigCPtIn: True total tract digested CP, kg/d
    """
    if An_StatePhys == "Calf":
        Dt_DigCPtIn = Dt_DigCPaIn + Fe_CPend    # Line 1210
    else:
        Dt_DigCPtIn = Dt_RDPIn + Dt_idRUPIn	# kg CP/d, true total tract digested CP, Line 1209
    return Dt_DigCPtIn

    
def calculate_Dt_DigTPaIn(Dt_RDTPIn: float, Fe_MiTP: float, Dt_idRUPIn: float, Fe_NPend: float) -> float:
    """
    Dt_DigTPaIn: Apparent total tract digested true protein, kg/d 
    """
    Dt_DigTPaIn = Dt_RDTPIn - Fe_MiTP + Dt_idRUPIn - Fe_NPend  # Doesn't apply to calves, Line 1211
    return Dt_DigTPaIn

    
def calculate_Dt_DigTPtIn(Dt_RDTPIn: float, Dt_idRUPIn: float) -> float:
    """
    Dt_DigTPtIn: True total tract digested true protein, kg/d
    """
    Dt_DigTPtIn = Dt_RDTPIn + Dt_idRUPIn    # Line 1212
    return Dt_DigTPtIn

    
def calculate_Dt_DigCPa(Dt_DigCPaIn: float, Dt_DMIn: float) -> float:
    """
    Dt_DigCPa: Dietary apparent total tract CP as % of DM
    """
    Dt_DigCPa = Dt_DigCPaIn / Dt_DMIn * 100    # Dietary Apparrent total tract % of DM, Line 1213
    return Dt_DigCPa

    
def calculate_TT_dcDtCPa(Dt_DigCPaIn: float, Dt_CPIn: float) -> float:
    """
    TT_dcDtCPa: Digestability coefficient apparent total tract CP, % CP
    """
    TT_dcDtCPa = Dt_DigCPaIn / Dt_CPIn * 100		# % of CP, Line 1214
    return TT_dcDtCPa

    
def calculate_Dt_DigCPt(Dt_DigCPtIn: float, Dt_DMIn: float) -> float:
    """
    Dt_DigCPt: Dietary true total tract digested CP, % DM    
    """
    Dt_DigCPt = Dt_DigCPtIn / Dt_DMIn * 100 	# Dietary True total tract % of DM, Line 1215
    return Dt_DigCPt

    
def calculate_Dt_DigTPt(Dt_DigTPtIn: float, Dt_DMIn: float) -> float:
    """
    Dt_DigTPt: Dietary true total tract digested true protein, % DM
    """
    Dt_DigTPt = Dt_DigTPtIn / Dt_DMIn * 100 	# True total tract % of DM, Line 1216
    return Dt_DigTPt

    
def calculate_TT_dcDtCPt(Dt_DigCPtIn: float, Dt_CPIn: float) -> float:
    """
    TT_dcDtCPt: Digestability coefficient true total tract CP, % CP
    """
    TT_dcDtCPt = Dt_DigCPtIn / Dt_CPIn * 100    # % of CP, Line 1217
    return TT_dcDtCPt

    
def calculate_Dt_MPIn(An_StatePhys: str, Dt_CPIn: float, Fe_CP: float, Fe_CPend: float, Dt_idRUPIn: float, Du_idMiTP: float) -> float:
    """
    Dt_MPIn: Dietary metabolizable protein intake, kg/d
    """
    if An_StatePhys == "Calf":
        Dt_MPIn = Dt_CPIn - Fe_CP + Fe_CPend    # ignores all ruminal activity, Line 1219
    else:
        Dt_MPIn = Dt_idRUPIn + Du_idMiTP    # Line 1218
    return Dt_MPIn

    
def calculate_Dt_MP(Dt_MPIn: float, Dt_DMIn: float) -> float:
    """
    Dt_MP: Dietary metabolizable protein, % DM 
    """
    Dt_MP = Dt_MPIn / Dt_DMIn * 100 # % of DM, Line 1220
    return Dt_MP


def calculate_Dt_DigUFAIn(Dt_DigC161In: float, Dt_DigC181tIn: float, Dt_DigC181cIn: float, Dt_DigC182In: float, Dt_DigC183In: float) -> float:
    """
    Dt_DigUFAIn: Dietary digestable unsaturated FA intake, kg/d 
    """
    Dt_DigUFAIn = Dt_DigC161In + Dt_DigC181tIn + Dt_DigC181cIn + Dt_DigC182In + Dt_DigC183In    # Line 1282
    return Dt_DigUFAIn


def calculate_Dt_DigMUFAIn(Dt_DigC161In: float, Dt_DigC181tIn: float, Dt_DigC181cIn: float) -> float:
    """
    Dt_DigMUFAIn: Dietary digestable monounsaturated fatty acid intake, kg/d
    """
    Dt_DigMUFAIn = Dt_DigC161In + Dt_DigC181tIn + Dt_DigC181cIn # Line 1283
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
    Dt_DigSatFAIn = Dt_DigFAIn - Dt_DigUFAIn    # Line 1285
    return Dt_DigSatFAIn


def calculate_Dt_DigFA(Dt_DigFAIn: float, Dt_DMIn: float) -> float:
    """
    Dt_DigFA: Dietary digested FA, % of DMI
    """
    Dt_DigFA = Dt_DigFAIn / Dt_DMIn * 100   # Line 1313
    return Dt_DigFA


def calculate_Dt_DigOMaIn(Dt_DigNDFIn: float, Dt_DigStIn: float, Dt_DigFAIn: float, Dt_DigrOMaIn: float, Dt_DigCPaIn: float) -> float:
    """
    Dt_DigOMaIn: Apparent digested organic matter intake (kg/d)
    """
    Dt_DigOMaIn = Dt_DigNDFIn + Dt_DigStIn + Dt_DigFAIn + Dt_DigrOMaIn + Dt_DigCPaIn    # Line 1320
    return Dt_DigOMaIn


def calculate_Dt_DigOMtIn(Dt_DigNDFIn: float, Dt_DigStIn: float, Dt_DigFAIn: float, Dt_DigrOMtIn: float, Dt_DigCPtIn: float) -> float:
    """
    Dt_DigOMtIn: True digested organic matter intake (kg/d)
    """
    Dt_DigOMtIn = Dt_DigNDFIn + Dt_DigStIn + Dt_DigFAIn + Dt_DigrOMtIn + Dt_DigCPtIn    # Line 1321
    return Dt_DigOMtIn


def calculate_Dt_DigOMa(Dt_DigOMaIn: float, Dt_DMIn: float) -> float:
    """
    Dt_DigOMa: Apparent digested dietary organic matter, % DMI
    """
    Dt_DigOMa = Dt_DigOMaIn / Dt_DMIn * 100 # Line 1327
    return Dt_DigOMa


def calculate_Dt_DigOMt(Dt_DigOMtIn: float, Dt_DMIn: float) -> float:
    """
    Dt_DigOMt: True digested dietary organic matter, % DMI
    """
    Dt_DigOMt = Dt_DigOMtIn / Dt_DMIn * 100 # Line 1328
    return Dt_DigOMt


def calculate_TT_dcDtFA(Dt_DigFAIn: float, Dt_FAIn: float) -> float:
    """
    TT_dcDtFA: Digestability coefficient for total tract dietary FA 
    """
    TT_dcDtFA = Dt_DigFAIn / Dt_FAIn * 100  # Line 1311
    return TT_dcDtFA


####################
# Wrapper functions for feed and diet intakes
####################


def calculate_diet_info(DMI, An_StatePhys, Use_DNDF_IV, diet_info, coeff_dict):
    # Start with copy of diet_info
    complete_diet_info = diet_info.copy()

    # Calculate all aditional feed data columns
    complete_diet_info['Fd_DMIn'] = calculate_Fd_DMIn(
        DMI, diet_info['Fd_DMInp'])
    complete_diet_info['Fd_GE'] = calculate_Fd_GE(An_StatePhys,
                                                  diet_info['Fd_Category'],
                                                  diet_info['Fd_CP'],
                                                  diet_info['Fd_FA'],
                                                  diet_info['Fd_Ash'],
                                                  diet_info['Fd_St'],
                                                  diet_info['Fd_NDF'],
                                                  coeff_dict)
    complete_diet_info['Fd_AFIn'] = calculate_Fd_AFIn(
        diet_info['Fd_DM'], diet_info['Fd_DMIn'])
    complete_diet_info['Fd_For'] = calculate_Fd_For(diet_info['Fd_Conc'])
    complete_diet_info['Fd_ForWet'] = calculate_Fd_ForWet(
        diet_info['Fd_DM'], complete_diet_info['Fd_For'])
    complete_diet_info['Fd_ForDry'] = calculate_Fd_ForDry(
        diet_info['Fd_DM'], complete_diet_info['Fd_For'])
    complete_diet_info['Fd_Past'] = calculate_Fd_Past(diet_info['Fd_Category'])
    complete_diet_info['Fd_LiqClf'] = calculate_Fd_LiqClf(
        diet_info['Fd_Category'])
    complete_diet_info['Fd_ForNDF'] = calculate_Fd_ForNDF(
        diet_info['Fd_NDF'], diet_info['Fd_Conc'])
    complete_diet_info['Fd_NDFnf'] = calculate_Fd_NDFnf(
        diet_info['Fd_NDF'], diet_info['Fd_NDFIP'])
    complete_diet_info['Fd_NPNCP'] = calculate_Fd_NPNCP(
        diet_info['Fd_CP'], diet_info['Fd_NPN_CP'])
    complete_diet_info['Fd_NPN'] = calculate_Fd_NPN(
        complete_diet_info['Fd_NPNCP'])
    complete_diet_info['Fd_NPNDM'] = calculate_Fd_NPNDM(
        complete_diet_info['Fd_NPNCP'])
    complete_diet_info['Fd_TP'] = calculate_Fd_TP(
        diet_info['Fd_CP'], complete_diet_info['Fd_NPNCP'])
    complete_diet_info['Fd_fHydr_FA'] = calculate_Fd_fHydr_FA(
        diet_info['Fd_Category'])
    complete_diet_info['Fd_FAhydr'] = calculate_Fd_FAhydr(
        diet_info['Fd_FA'], complete_diet_info['Fd_fHydr_FA'])
    complete_diet_info['Fd_NFC'] = calculate_Fd_NFC(diet_info['Fd_NDF'],
                                                    complete_diet_info['Fd_TP'],
                                                    diet_info['Fd_Ash'],
                                                    complete_diet_info['Fd_FAhydr'],
                                                    complete_diet_info['Fd_NPNDM'])
    complete_diet_info['Fd_rOM'] = calculate_Fd_rOM(diet_info['Fd_NDF'],
                                                    diet_info['Fd_St'],
                                                    complete_diet_info['Fd_TP'],
                                                    diet_info['Fd_FA'],
                                                    complete_diet_info['Fd_fHydr_FA'],
                                                    diet_info['Fd_Ash'],
                                                    complete_diet_info['Fd_NPNDM'])
    complete_diet_info['Fd_GEIn'] = calculate_Fd_GEIn(complete_diet_info['Fd_GE'], 
                                                      complete_diet_info['Fd_DMIn'])
    # Loop through identical calculations
    column_names_XIn = ['Fd_ADF',
                        'Fd_NDF',
                        'Fd_St',
                        'Fd_NFC',
                        'Fd_WSC',
                        'Fd_rOM',
                        'Fd_Lg',
                        'Fd_Conc',
                        'Fd_For',
                        'Fd_ForWet',
                        'Fd_ForDry',
                        'Fd_Past',
                        'Fd_CP',
                        'Fd_TP',
                        'Fd_CFat',
                        'Fd_FA',
                        'Fd_FAhydr',
                        'Fd_Ash'
                        ]

    complete_diet_info = complete_diet_info.assign(
        **{f"{col}In": lambda df, col=col: df[col] / 100 * df['Fd_DMIn'] for col in column_names_XIn}
    )

    # Calculate nutrient intakes for each feed
    complete_diet_info['TT_dcFdNDF_Lg'] = calculate_TT_dcFdNDF_Lg(diet_info['Fd_NDF'],
                                                                  diet_info['Fd_Lg'])
    complete_diet_info['Fd_DNDF48'] = calculate_Fd_DNDF48(diet_info['Fd_Conc'],
                                                          diet_info['Fd_DNDF48'])
    complete_diet_info['TT_dcFdNDF_48h'] = calculate_TT_dcFdNDF_48h(
        complete_diet_info['Fd_DNDF48'])
    complete_diet_info['TT_dcFdNDF_Base'] = calculate_TT_dcFdNDF_Base(Use_DNDF_IV,
                                                                      diet_info['Fd_Conc'],
                                                                      complete_diet_info['TT_dcFdNDF_Lg'],
                                                                      complete_diet_info['TT_dcFdNDF_48h'])
    complete_diet_info['Fd_DigNDFIn_Base'] = calculate_Fd_DigNDFIn_Base(complete_diet_info['Fd_NDFIn'],
                                                                        complete_diet_info['TT_dcFdNDF_Base'])
    complete_diet_info['Fd_NPNCPIn'] = calculate_Fd_NPNCPIn(
        complete_diet_info['Fd_CPIn'], complete_diet_info['Fd_NPN_CP'])
    complete_diet_info['Fd_NPNIn'] = calculate_Fd_NPNIn(
        complete_diet_info['Fd_NPNCPIn'])
    complete_diet_info['Fd_NPNDMIn'] = calculate_Fd_NPNDMIn(
        complete_diet_info['Fd_NPNCPIn'])
    complete_diet_info['Fd_CPAIn'] = calculate_Fd_CPAIn(
        complete_diet_info['Fd_CPIn'], complete_diet_info['Fd_CPARU'])
    complete_diet_info['Fd_CPBIn'] = calculate_Fd_CPBIn(
        complete_diet_info['Fd_CPIn'], complete_diet_info['Fd_CPBRU'])
    complete_diet_info['Fd_CPBIn_For'] = calculate_Fd_CPBIn_For(complete_diet_info['Fd_CPIn'],
                                                                complete_diet_info['Fd_CPBRU'],
                                                                complete_diet_info['Fd_For'])
    complete_diet_info['Fd_CPBIn_Conc'] = calculate_Fd_CPBIn_Conc(complete_diet_info['Fd_CPIn'],
                                                                  complete_diet_info['Fd_CPBRU'],
                                                                  complete_diet_info['Fd_Conc'])
    complete_diet_info['Fd_CPCIn'] = calculate_Fd_CPCIn(
        complete_diet_info['Fd_CPIn'], complete_diet_info['Fd_CPCRU'])
    complete_diet_info['Fd_CPIn_ClfLiq'] = calculate_Fd_CPIn_ClfLiq(diet_info['Fd_Category'],
                                                                    complete_diet_info['Fd_DMIn'],
                                                                    diet_info['Fd_CP'])
    complete_diet_info['Fd_CPIn_ClfDry'] = calculate_Fd_CPIn_ClfDry(diet_info['Fd_Category'],
                                                                    complete_diet_info['Fd_DMIn'],
                                                                    diet_info['Fd_CP'])
    complete_diet_info['Fd_OMIn'] = calculate_Fd_OMIn(
        complete_diet_info['Fd_DMIn'], complete_diet_info['Fd_AshIn'])

    # Rumen Degraded and Undegraded Protein
    complete_diet_info['Fd_rdcRUPB'] = calculate_Fd_rdcRUPB(complete_diet_info['Fd_For'],
                                                            complete_diet_info['Fd_Conc'],
                                                            complete_diet_info['Fd_KdRUP'],
                                                            coeff_dict)
    complete_diet_info['Fd_RUPBIn'] = calculate_Fd_RUPBIn(complete_diet_info['Fd_For'],
                                                          complete_diet_info['Fd_Conc'],
                                                          complete_diet_info['Fd_KdRUP'],
                                                          complete_diet_info['Fd_CPBIn'],
                                                          coeff_dict)
    complete_diet_info['Fd_RUPIn'] = calculate_Fd_RUPIn(complete_diet_info['Fd_CPIn'],
                                                        complete_diet_info['Fd_CPAIn'],
                                                        complete_diet_info['Fd_CPCIn'],
                                                        complete_diet_info['Fd_NPNCPIn'],
                                                        complete_diet_info['Fd_RUPBIn'],
                                                        coeff_dict)
    complete_diet_info['Fd_RUP_CP'] = calculate_Fd_RUP_CP(complete_diet_info['Fd_CPIn'],
                                                          complete_diet_info['Fd_RUPIn'])
    complete_diet_info['Fd_RUP'] = calculate_Fd_RUP(complete_diet_info['Fd_CPIn'],
                                                    complete_diet_info['Fd_RUPIn'],
                                                    complete_diet_info['Fd_DMIn'])
    complete_diet_info['Fd_RDP'] = calculate_Fd_RDP(complete_diet_info['Fd_CPIn'],
                                                    complete_diet_info['Fd_CP'],
                                                    complete_diet_info['Fd_RUP'])

    # FA Intakes
    column_names_FAIn = ['Fd_C120',
                         'Fd_C140',
                         'Fd_C160',
                         'Fd_C161',
                         'Fd_C180',
                         'Fd_C181t',
                         'Fd_C181c',
                         'Fd_C182',
                         'Fd_C183',
                         'Fd_OtherFA'
                         ]

    complete_diet_info = complete_diet_info.assign(
        **{f"{col}In": lambda df, col=col: df[f"{col}_FA"] / 100 * df['Fd_FA'] / 100 * df['Fd_DMIn'] for col in column_names_FAIn}
    )

    complete_diet_info['Fd_DE_base_1'] = calculate_Fd_DE_base_1(diet_info['Fd_NDF'],
                                                                diet_info['Fd_Lg'],
                                                                diet_info['Fd_St'],
                                                                diet_info['Fd_dcSt'],
                                                                diet_info['Fd_FA'],
                                                                diet_info['Fd_dcFA'],
                                                                diet_info['Fd_Ash'],
                                                                diet_info['Fd_CP'],
                                                                complete_diet_info['Fd_NPNCP'],
                                                                complete_diet_info['Fd_RUP'],
                                                                diet_info['Fd_dcRUP'])
    complete_diet_info['Fd_DE_base_2'] = calculate_Fd_DE_base_2(diet_info['Fd_NDF'],
                                                                diet_info['Fd_St'],
                                                                diet_info['Fd_dcSt'],
                                                                diet_info['Fd_FA'],
                                                                diet_info['Fd_dcFA'],
                                                                diet_info['Fd_Ash'],
                                                                diet_info['Fd_CP'],
                                                                complete_diet_info['Fd_NPNCP'],
                                                                complete_diet_info['Fd_RUP'],
                                                                diet_info['Fd_dcRUP'],
                                                                diet_info['Fd_DNDF48_NDF'])
    complete_diet_info['Fd_DE_base'] = calculate_Fd_DE_base(Use_DNDF_IV,
                                                            complete_diet_info['Fd_DE_base_1'],
                                                            complete_diet_info['Fd_DE_base_2'],
                                                            complete_diet_info['Fd_For'],
                                                            diet_info['Fd_FA'],
                                                            complete_diet_info['Fd_RDP'],
                                                            complete_diet_info['Fd_RUP'],
                                                            diet_info['Fd_dcRUP'],
                                                            diet_info['Fd_CP'],
                                                            diet_info['Fd_Ash'],
                                                            diet_info['Fd_dcFA'],
                                                            complete_diet_info['Fd_NPN'],
                                                            diet_info['Fd_Category'])
    complete_diet_info['Fd_DEIn_base'] = calculate_Fd_DEIn_base(complete_diet_info['Fd_DE_base'],
                                                                complete_diet_info['Fd_DMIn'])
    complete_diet_info['Fd_DEIn_base_ClfLiq'] = calculate_Fd_DEIn_base_ClfLiq(diet_info['Fd_Category'],
                                                                              complete_diet_info['Fd_DEIn_base'])
    complete_diet_info['Fd_DEIn_base_ClfDry'] = calculate_Fd_DEIn_base_ClfDry(diet_info['Fd_Category'],
                                                                              complete_diet_info['Fd_DEIn_base'])
    complete_diet_info['Fd_DMIn_ClfLiq'] = calculate_Fd_DMIn_ClfLiq(An_StatePhys,
                                                                    diet_info['Fd_DMIn'],
                                                                    diet_info['Fd_Category'])
    complete_diet_info['Fd_DE_ClfLiq'] = calculate_Fd_DE_ClfLiq(An_StatePhys,
                                                                diet_info['Fd_Category'],
                                                                complete_diet_info['Fd_GE'])
    complete_diet_info['Fd_ME_ClfLiq'] = calculate_Fd_ME_ClfLiq(An_StatePhys,
                                                                diet_info['Fd_Category'],
                                                                complete_diet_info['Fd_DE_ClfLiq'])
    complete_diet_info['Fd_DMIn_ClfFor'] = calculate_Fd_DMIn_ClfFor(DMI,
                                                                    diet_info['Fd_Conc'],
                                                                    complete_diet_info['Fd_DMInp'])
    macro_mineral_intakes = ['Fd_Ca',
                             'Fd_P',
                             'Fd_Na',
                             'Fd_Mg',
                             'Fd_K',
                             'Fd_Cl',
                             'Fd_S'
                             ]

    complete_diet_info = complete_diet_info.assign(
        **{f"{col}In": lambda df, col=col: df['Fd_DMIn'] * df[col] / 100 * 1000 for col in macro_mineral_intakes}
    )

    complete_diet_info['Fd_PinorgIn'] = calculate_Fd_PinorgIn(complete_diet_info['Fd_PIn'],
                                                              complete_diet_info['Fd_Pinorg_P'])
    complete_diet_info['Fd_PorgIn'] = calculate_Fd_PorgIn(complete_diet_info['Fd_PIn'],
                                                          complete_diet_info['Fd_Porg_P'])
    complete_diet_info['Fd_MgIn_min'] = calculate_Fd_MgIn_min(diet_info['Fd_Category'],
                                                              diet_info['Fd_Mg'])

    micro_mineral_intakes = ['Fd_Co',
                             'Fd_Cr',
                             'Fd_Cu',
                             'Fd_Fe',
                             'Fd_I',
                             'Fd_Mn',
                             'Fd_Mo',
                             'Fd_Se',
                             'Fd_Zn'
                             ]

    # Line 741-749
    complete_diet_info = complete_diet_info.assign(
        **{f"{col}In": lambda df, col=col: df['Fd_DMIn'] * df[col] for col in micro_mineral_intakes}
    )

    vitamin_intakes = ['Fd_VitA',
                       'Fd_VitD',
                       'Fd_VitE',
                       'Fd_Choline',
                       'Fd_Biotin',
                       'Fd_Niacin',
                       'Fd_B_Carotene'
                       ]
    # Line 752-759
    complete_diet_info = complete_diet_info.assign(
        **{f"{col}In": lambda df, col=col: df['Fd_DMIn'] * df[col] for col in vitamin_intakes}
    )

    Dt_DMIn_ClfLiq = complete_diet_info['Fd_DMIn_ClfLiq'].sum()
    # Dt_DMIn_ClfLiq is needed for the calf mineral absorption calculations

    complete_diet_info['Fd_acCa'] = calculate_Fd_acCa(
        An_StatePhys, complete_diet_info['Fd_acCa'], Dt_DMIn_ClfLiq)
    complete_diet_info['Fd_acPtot'] = calculate_Fd_acPtot(An_StatePhys,
                                                          diet_info['Fd_Category'],
                                                          complete_diet_info['Fd_Pinorg_P'],
                                                          complete_diet_info['Fd_Porg_P'],
                                                          complete_diet_info['Fd_acPtot'],
                                                          Dt_DMIn_ClfLiq)
    complete_diet_info['Fd_acMg'] = calculate_Fd_acMg(An_StatePhys,
                                                      complete_diet_info['Fd_acMg'],
                                                      Dt_DMIn_ClfLiq)
    complete_diet_info['Fd_acNa'] = calculate_Fd_acNa(
        An_StatePhys, complete_diet_info['Fd_acNa'])
    complete_diet_info['Fd_acK'] = calculate_Fd_acK(
        An_StatePhys, complete_diet_info['Fd_acK'])
    complete_diet_info['Fd_acCl'] = calculate_Fd_acCl(
        An_StatePhys, complete_diet_info['Fd_acCl'], Dt_DMIn_ClfLiq)
    complete_diet_info['Fd_absCaIn'] = calculate_Fd_absCaIn(
        complete_diet_info['Fd_CaIn'], complete_diet_info['Fd_acCa'])
    complete_diet_info['Fd_absPIn'] = calculate_Fd_absPIn(
        complete_diet_info['Fd_PIn'], complete_diet_info['Fd_acPtot'])
    complete_diet_info['Fd_absMgIn_base'] = calculate_Fd_absMgIn_base(
        complete_diet_info['Fd_MgIn'], complete_diet_info['Fd_acMg'])
    complete_diet_info['Fd_absNaIn'] = calculate_Fd_absNaIn(
        complete_diet_info['Fd_NaIn'], complete_diet_info['Fd_acNa'])
    complete_diet_info['Fd_absKIn'] = calculate_Fd_absKIn(
        complete_diet_info['Fd_KIn'], complete_diet_info['Fd_acK'])
    complete_diet_info['Fd_absClIn'] = calculate_Fd_absClIn(
        complete_diet_info['Fd_ClIn'], complete_diet_info['Fd_acCl'])
    complete_diet_info['Fd_acCo'] = calculate_Fd_acCo(An_StatePhys)
    complete_diet_info['Fd_acCu'] = calculate_Fd_acCu(
        An_StatePhys, complete_diet_info['Fd_acCu'], Dt_DMIn_ClfLiq)
    complete_diet_info['Fd_acFe'] = calculate_Fd_acFe(
        An_StatePhys, complete_diet_info['Fd_acFe'], Dt_DMIn_ClfLiq)
    complete_diet_info['Fd_acMn'] = calculate_Fd_acMn(
        An_StatePhys, complete_diet_info['Fd_acMn'], Dt_DMIn_ClfLiq)
    complete_diet_info['Fd_acZn'] = calculate_Fd_acZn(
        An_StatePhys, complete_diet_info['Fd_acZn'], Dt_DMIn_ClfLiq)

    micro_absorption = ['Co',
                        'Cu',
                        'Fe',
                        'Mn',
                        'Zn']

    complete_diet_info = complete_diet_info.assign(
        **{f"Fd_abs{col}In": lambda df, col=col: df[f"Fd_{col}In"] * df[f"Fd_ac{col}"] for col in micro_absorption}
    )

    # Digested endogenous protein is ignored as it is a recycle of previously absorbed AA.
    # SI Digestibility of AA relative to RUP digestibility ([g dAA / g AA] / [g dRUP / g RUP])
    # All set to 1 due to lack of clear evidence for deviations.
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

    req_coeffs = ['RecArg', 'RecHis', 'RecIle', 'RecLeu',
                  'RecLys', 'RecMet', 'RecPhe', 'RecThr',
                  'RecTrp', 'RecVal']
    check_coeffs_in_coeff_dict(coeff_dict, req_coeffs)

    AA_list = ['Arg', 'His', 'Ile', 'Leu',
               'Lys', 'Met', 'Phe', 'Thr', 'Trp', 'Val']
    # for AA in AA_list:
    #     # Fd_AAt_CP
    #     complete_diet_info[f"Fd_{AA}t_CP"] = complete_diet_info[f"Fd_{AA}_CP"] / coeff_dict[f"Rec{AA}"]

    #     # Fd_AARUPIn
    #     complete_diet_info[f"Fd_{AA}RUPIn"] = complete_diet_info[f"Fd_{AA}t_CP"] / 100 * complete_diet_info['Fd_RUPIn'] * 1000

    #     # Fd_IdAARUPIn
    #     # Note: eval() is used to access SIDig__ values defined above
    #     complete_diet_info[f"Fd_Id{AA}RUPIn"] = complete_diet_info['Fd_dcRUP'] / 100 * complete_diet_info[f"Fd_{AA}RUPIn"] * eval(f"SIDig{AA}RUPf")

    complete_diet_info = complete_diet_info.assign(
        **{f"Fd_{AA}t_CP": lambda df, AA=AA: df[f"Fd_{AA}_CP"] / coeff_dict[f"Rec{AA}"] for AA in AA_list},
        **{f"Fd_{AA}RUPIn": lambda df, AA=AA: df[f"Fd_{AA}t_CP"] / 100 * df['Fd_RUPIn'] * 1000 for AA in AA_list},
        **{f"Fd_Id{AA}RUPIn": lambda df, AA=AA: df['Fd_dcRUP'] / 100 * df[f"Fd_{AA}RUPIn"] * SIDig_values[AA] for AA in AA_list}
    )

    complete_diet_info['Fd_DigSt'] = calculate_Fd_DigSt(diet_info['Fd_St'],
                                                        diet_info['Fd_dcSt'])
    complete_diet_info['Fd_DigStIn_Base'] = calculate_Fd_DigStIn_Base(complete_diet_info['Fd_DigSt'],
                                                                      diet_info['Fd_DMIn'])
    complete_diet_info['Fd_DigrOMt'] = calculate_Fd_DigrOMt(complete_diet_info['Fd_rOM'],
                                                            coeff_dict)
    complete_diet_info['Fd_DigrOMtIn'] = calculate_Fd_DigrOMtIn(complete_diet_info['Fd_DigrOMt'],
                                                                diet_info['Fd_DMIn'])
    complete_diet_info['Fd_idRUPIn'] = calculate_Fd_idRUPIn(diet_info['Fd_dcRUP'],
                                                            complete_diet_info['Fd_RUPIn'])
    complete_diet_info['TT_dcFdFA'] = calculate_TT_dcFdFA(An_StatePhys,
                                                          diet_info['Fd_Category'],
                                                          diet_info['Fd_Type'],
                                                          diet_info['Fd_dcFA'],
                                                          coeff_dict)
    complete_diet_info['Fd_DigFAIn'] = calculate_Fd_DigFAIn(complete_diet_info['TT_dcFdFA'],
                                                            diet_info['Fd_FA'],
                                                            diet_info['Fd_DMIn'])
    
    Dig_FA_list = [
        'C120',
        'C140',
        'C160',
        'C161',
        'C180',
        'C181t',
        'C181c',
        'C182',
        'C183',
        'OtherFA'
    ]
    complete_diet_info = complete_diet_info.assign(
        **{f"Fd_Dig{FA}In": lambda df, FA=FA: df['TT_dcFdFA'] / 100 * df[f"Fd_{FA}_FA"] / 100 * df['Fd_FA'] / 100 * df['Fd_DMIn'] for FA in Dig_FA_list}
    )   
    
    complete_diet_info['Fd_DigrOMa'] = calculate_Fd_DigrOMa(complete_diet_info['Fd_DigrOMt'],
                                                            coeff_dict)
    complete_diet_info['Fd_DigrOMaIn'] = calculate_Fd_DigrOMaIn(complete_diet_info['Fd_DigrOMa'],
                                                                complete_diet_info['Fd_DMIn'])
    complete_diet_info['Fd_DigWSC'] = calculate_Fd_DigWSC(complete_diet_info['Fd_WSC'])
    complete_diet_info['Fd_DigWSCIn'] = calculate_Fd_DigWSCIn(complete_diet_info['Fd_DigWSC'],
                                                              complete_diet_info['Fd_DMIn'])
    complete_diet_info['Fd_idRUP'] = calculate_Fd_idRUP(complete_diet_info['Fd_CPIn'],
                                                        complete_diet_info['Fd_idRUPIn'],
                                                        complete_diet_info['Fd_DMIn'])    
    complete_diet_info['Fd_Fe_RUPout'] = calculate_Fd_Fe_RUPout(complete_diet_info['Fd_RUPIn'],
                                                                complete_diet_info['Fd_dcRUP'])
    return complete_diet_info


def calculate_diet_data_initial(df, DMI, An_BW, An_StatePhys, An_DMIn_BW, An_AgeDryFdStart, Env_TempCurr, DMIn_eqn, Fe_rOMend, coeff_dict):
    diet_data = {}

    # Diet Intakes
    column_names_DMInp = [
        'ADF',
        'NDF',
        'For',
        'ForNDF'
    ]
    # Lines 255, 256
    for col_name in column_names_DMInp:
        diet_data[f'Dt_{col_name}'] = (
            df['Fd_DMInp'] * df[f'Fd_{col_name}']).sum()

    column_names_sum = [
        'DMIn_ClfLiq',
        'DMIn_ClfFor',
        'AFIn',
        'NDFIn',
        'ADFIn',
        'LgIn',
        'DigNDFIn_Base',
        'ForWetIn',
        'ForDryIn',
        'PastIn',
        'ForIn',
        'ConcIn',
        'NFCIn',
        'StIn',
        'WSCIn',
        'CPIn',
        'CPIn_ClfLiq',
        'TPIn',
        'NPNCPIn',
        'NPNIn',
        'NPNDMIn',
        'CPAIn',
        'CPBIn',
        'CPCIn',
        'RUPBIn',
        'CFatIn',
        'FAIn',
        'FAhydrIn',
        'C120In',
        'C140In',
        'C160In',
        'C161In',
        'C180In',
        'C181tIn',
        'C181cIn',
        'C182In',
        'C183In',
        'OtherFAIn',
        'AshIn',
        'GEIn',
        'DEIn_base',
        'DEIn_base_ClfLiq',
        'DEIn_base_ClfDry',
        'DigStIn_Base',
        'DigrOMtIn',
        'idRUPIn',
        'DigFAIn',
        'DMIn_ClfFor'
    ]
    # Lines 286, 297, 580, 587, 589, 590, 593-596, 598-614, 615, 626-638, 644, 649-652
    for col_name in column_names_sum:
        diet_data[f'Dt_{col_name}'] = (df[f'Fd_{col_name}']).sum()

    diet_data['Dt_DMInSum'] = calculate_Dt_DMInSum(df['Fd_DMIn'])
    diet_data['Dt_DEIn_ClfLiq'] = calculate_Dt_DEIn_ClfLiq(df['Fd_DE_ClfLiq'],
                                                           df['Fd_DMIn_ClfLiq'])
    diet_data['Dt_MEIn_ClfLiq'] = calculate_Dt_MEIn_ClfLiq(df['Fd_ME_ClfLiq'],
                                                           df['Fd_DMIn_ClfLiq'])
    diet_data['Dt_ForDNDF48'] = calculate_Dt_ForDNDF48(df['Fd_DMInp'],
                                                       df['Fd_Conc'],
                                                       df['Fd_NDF'],
                                                       df['Fd_DNDF48'])
    diet_data['Dt_ForDNDF48_ForNDF'] = calculate_Dt_ForDNDF48_ForNDF(diet_data['Dt_ForDNDF48'],
                                                                     diet_data['Dt_ForNDF'])
    diet_data['Dt_ADF_NDF'] = calculate_Dt_ADF_NDF(diet_data['Dt_ADF'],
                                                   diet_data['Dt_NDF'])
    diet_data['Dt_NDFnfIn'] = calculate_Dt_NDFnfIn(df['Fd_DMIn'],
                                                   df['Fd_NDFnf'])
    diet_data['Dt_Lg_NDF'] = calculate_Dt_Lg_NDF(diet_data['Dt_LgIn'],
                                                 diet_data['Dt_NDFIn'])
    diet_data['Dt_ForNDFIn'] = calculate_Dt_ForNDFIn(df['Fd_DMIn'],
                                                     df['Fd_ForNDF'])
    diet_data['Dt_PastSupplIn'] = calculate_Dt_PastSupplIn(diet_data['Dt_DMInSum'],
                                                           diet_data['Dt_PastIn'])
    diet_data['Dt_NIn'] = calculate_Dt_NIn(diet_data['Dt_CPIn'])
    diet_data['Dt_RUPIn'] = calculate_Dt_RUPIn(diet_data['Dt_CPAIn'],
                                               diet_data['Dt_NPNIn'],
                                               diet_data['Dt_RUPBIn'],
                                               diet_data['Dt_CPCIn'],
                                               coeff_dict,
                                               Fd_RUPIn=df['Fd_RUPIn'])
    diet_data['Dt_RUP_CP'] = calculate_Dt_RUP_CP(diet_data['Dt_CPIn'],
                                                 diet_data['Dt_RUPIn'])
    diet_data['Dt_fCPBdu'] = calculate_Dt_fCPBdu(diet_data['Dt_RUPBIn'],
                                                 diet_data['Dt_CPBIn'])
    diet_data['Dt_UFAIn'] = calculate_Dt_UFAIn(diet_data['Dt_C161In'],
                                               diet_data['Dt_C181tIn'],
                                               diet_data['Dt_C181cIn'],
                                               diet_data['Dt_C182In'],
                                               diet_data['Dt_C183In'])
    diet_data['Dt_MUFAIn'] = calculate_Dt_MUFAIn(diet_data['Dt_C161In'],
                                                 diet_data['Dt_C181tIn'],
                                                 diet_data['Dt_C181cIn'])
    diet_data['Dt_PUFAIn'] = calculate_Dt_PUFAIn(diet_data['Dt_UFAIn'],
                                                 diet_data['Dt_C161In'],
                                                 diet_data['Dt_C181tIn'],
                                                 diet_data['Dt_C181cIn'])
    diet_data['Dt_SatFAIn'] = calculate_Dt_SatFAIn(diet_data['Dt_FAIn'],
                                                   diet_data['Dt_UFAIn'])
    diet_data['Dt_OMIn'] = calculate_Dt_OMIn(DMI,
                                             diet_data['Dt_AshIn'])
    diet_data['Dt_rOMIn'] = calculate_Dt_rOMIn(DMI,
                                               diet_data['Dt_AshIn'],
                                               diet_data['Dt_NDFIn'],
                                               diet_data['Dt_StIn'],
                                               diet_data['Dt_FAhydrIn'],
                                               diet_data['Dt_TPIn'],
                                               diet_data['Dt_NPNDMIn'])
    diet_data['Dt_DM'] = calculate_Dt_DM(DMI,
                                         diet_data['Dt_AFIn'])
    diet_data['Dt_NDFIn_BW'] = calculate_Dt_NDFIn_BW(An_BW,
                                                     diet_data['Dt_NDFIn'])

    column_names_DMI = [
        'RUP',
        'OM',
        'NDF',
        'NDFnf',
        'ADF',
        'Lg',
        'ForNDF',
        'NFC',
        'St',
        'WSC',
        'rOM',
        'CFat',
        'FA',
        'FAhydr',
        'CP',
        'TP',
        'NPNCP',
        'NPN',
        'NPNDM',
        'CPA',
        'CPB',
        'CPC',
        'Ash',
        'ForWet',
        'ForDry',
        'For',
        'Conc',
        'C120',
        'C140',
        'C160',
        'C161',
        'C180',
        'C181t',
        'C181c',
        'C182',
        'C183',
        'OtherFA',
        'UFA',
        'MUFA',
        'PUFA',
        'SatFA'
    ]
    # Lines 620, 656, 657, 659-662, 666-709
    for col_name in column_names_DMI:
        diet_data[f'Dt_{col_name}'] = diet_data[f'Dt_{col_name}In'] / DMI * 100

    column_names_FA = [
        'C120',
        'C140',
        'C160',
        'C161',
        'C180',
        'C181t',
        'C181c',
        'C182',
        'C183',
        'OtherFA',
        'UFA',
        'MUFA',
        'PUFA',
        'SatFA'
    ]
    # Lines 712-725
    for col_name in column_names_FA:
        diet_data[f'Dt_{col_name}_FA'] = diet_data[f'Dt_{col_name}In'] / \
            diet_data['Dt_FAIn'] * 100

    diet_data['Dt_ForNDF_NDF'] = calculate_Dt_ForNDF_NDF(diet_data['Dt_ForNDF'],
                                                         diet_data['Dt_NDF'])
    diet_data['Dt_ForNDFIn_BW'] = calculate_Dt_ForNDFIn_BW(An_BW,
                                                           diet_data['Dt_ForNDFIn'])
    diet_data['Dt_CPA_CP'] = calculate_Dt_CPA_CP(diet_data['Dt_CPAIn'],
                                                 diet_data['Dt_CPIn'])
    diet_data['Dt_CPB_CP'] = calculate_Dt_CPB_CP(diet_data['Dt_CPBIn'],
                                                 diet_data['Dt_CPIn'])
    diet_data['Dt_CPC_CP'] = calculate_Dt_CPC_CP(diet_data['Dt_CPCIn'],
                                                 diet_data['Dt_CPIn'])

    column_names_micronutrients = ['CaIn',
                                   'PIn',
                                   'PinorgIn',
                                   'PorgIn',
                                   'NaIn',
                                   'MgIn',
                                   'MgIn_min',
                                   'KIn',
                                   'ClIn',
                                   'SIn',
                                   'CoIn',
                                   'CrIn',
                                   'CuIn',
                                   'FeIn',
                                   'IIn',
                                   'MnIn',
                                   'MoIn',
                                   'SeIn',
                                   'ZnIn',
                                   'VitAIn',
                                   'VitDIn',
                                   'VitEIn',
                                   'CholineIn',
                                   'BiotinIn',
                                   'NiacinIn',
                                   'B_CaroteneIn'
                                   ]
    for column_name in column_names_micronutrients:
        # Lines 762-791
        diet_data[f'Dt_{column_name}'] = df[f'Fd_{column_name}'].sum()

    column_names_macro = ['Dt_Ca',
                          'Dt_P',
                          'Dt_Pinorg',
                          'Dt_Porg',
                          'Dt_Na',
                          'Dt_Mg',
                          'Dt_K',
                          'Dt_Cl',
                          'Dt_S']
    for column_name in column_names_macro:
        # Line 795-804
        diet_data[f'{column_name}'] = diet_data[f'{column_name}In'] / \
            DMI / 1000 * 100

    column_names_micro_vitamin = ['Dt_Co',
                                  'Dt_Cr',
                                  'Dt_Cu',
                                  'Dt_Fe',
                                  'Dt_I',
                                  'Dt_Mn',
                                  'Dt_Mo',
                                  'Dt_Se',
                                  'Dt_Zn',
                                  'Dt_VitA',
                                  'Dt_VitD',
                                  'Dt_VitE',
                                  'Dt_Choline',
                                  'Dt_Biotin',
                                  'Dt_Niacin',
                                  'Dt_B_Carotene']
    for column_name in column_names_micro_vitamin:
        # Line 807 - 825
        diet_data[f'{column_name}'] = diet_data[f'{column_name}In'] / DMI

    AA_list = ['Arg', 'His', 'Ile', 'Leu',
               'Lys', 'Met', 'Phe', 'Thr', 'Trp', 'Val']
    for AA in AA_list:
        # Dt_IdAARUPIn
        diet_data[f'Dt_Id{AA}RUPIn'] = df[f'Fd_Id{AA}RUPIn'].sum()
    diet_data['Dt_RDPIn'] = calculate_Dt_RDPIn(diet_data['Dt_CPIn'],
                                               diet_data['Dt_RUPIn'])

    # NOTE TT_dc values are calculated here as they are required for calculating Dt_ values
    # The could be calculated outside of this function but then diet_data would need to be calculated in 2 steps
    diet_data['TT_dcNDF_Base'] = calculate_TT_dcNDF_Base(diet_data['Dt_DigNDFIn_Base'],
                                                         diet_data['Dt_NDFIn'])
    diet_data['TT_dcNDF'] = calculate_TT_dcNDF(diet_data['TT_dcNDF_Base'],
                                               diet_data['Dt_StIn'],
                                               DMI,
                                               An_DMIn_BW)
    diet_data['TT_dcSt_Base'] = calculate_TT_dcSt_Base(diet_data['Dt_DigStIn_Base'],
                                                       diet_data['Dt_StIn'])
    diet_data['TT_dcSt'] = calculate_TT_dcSt(diet_data['TT_dcSt_Base'],
                                             An_DMIn_BW)
    diet_data['Dt_DigNDFIn'] = calculate_Dt_DigNDFIn(diet_data['TT_dcNDF'],
                                                     diet_data['Dt_NDFIn'])
    diet_data['Dt_DigStIn'] = calculate_Dt_DigStIn(diet_data['Dt_StIn'],
                                                   diet_data['TT_dcSt'])

    diet_data['Dt_DigrOMaIn'] = calculate_Dt_DigrOMaIn(diet_data['Dt_DigrOMtIn'],
                                                       Fe_rOMend)
    diet_data['Dt_dcCP_ClfDry'] = calculate_Dt_dcCP_ClfDry(An_StatePhys,
                                                           diet_data['Dt_DMIn_ClfLiq'])
    diet_data['Dt_DENDFIn'] = calculate_Dt_DENDFIn(diet_data['Dt_DigNDFIn'],
                                                   coeff_dict)
    diet_data['Dt_DEStIn'] = calculate_Dt_DEStIn(diet_data['Dt_DigStIn'],
                                                 coeff_dict)
    diet_data['Dt_DErOMIn'] = calculate_Dt_DErOMIn(diet_data['Dt_DigrOMaIn'],
                                                   coeff_dict)
    diet_data['Dt_DENPNCPIn'] = calculate_Dt_DENPNCPIn(diet_data['Dt_NPNCPIn'],
                                                       coeff_dict)
    diet_data['Dt_DEFAIn'] = calculate_Dt_DEFAIn(diet_data['Dt_DigFAIn'],
                                                 coeff_dict)
    diet_data['Dt_DMIn_ClfStrt'] = calculate_Dt_DMIn_ClfStrt(An_BW,
                                                             diet_data['Dt_MEIn_ClfLiq'],
                                                             diet_data['Dt_DMIn_ClfLiq'],
                                                             diet_data['Dt_DMIn_ClfFor'],
                                                             An_AgeDryFdStart,
                                                             Env_TempCurr,
                                                             DMIn_eqn,
                                                             DMI,
                                                             coeff_dict)
    
    Dig_FA_list = [
        'C120',
        'C140',
        'C160',
        'C161',
        'C180',
        'C181t',
        'C181c',
        'C182',
        'C183',
        'OtherFA'
    ]
    for FA in Dig_FA_list:
        # Dt_DigFAIn
        diet_data[f'Dt_Dig{FA}In'] = df[f'Fd_Dig{FA}In'].sum()

    Abs_micro_list = [
        'CaIn',
        'PIn',
        'NaIn',
        'KIn',
        'ClIn',
        'CoIn',
        'CuIn',
        'FeIn',
        'MnIn',
        'ZnIn'
    ]
    for micro in Abs_micro_list:
        diet_data[f"Abs_{micro}"] = df[f"Fd_abs{micro}"].sum()

    diet_data['Dt_acMg'] = calculate_Dt_acMg(An_StatePhys,
                                             diet_data['Dt_K'],
                                             diet_data['Dt_MgIn_min'],
                                             diet_data['Dt_MgIn'])
    diet_data['Abs_MgIn'] = calculate_Abs_MgIn(diet_data['Dt_acMg'],
                                               diet_data['Dt_MgIn'])
    diet_data['Dt_DigWSCIn'] = calculate_Dt_DigWSCIn(df['Fd_DigWSCIn'])
    diet_data['Dt_DigSt'] = calculate_Dt_DigSt(diet_data['Dt_DigStIn'],
                                               DMI)
    diet_data['Dt_DigWSC'] = calculate_Dt_DigWSC(diet_data['Dt_DigWSCIn'],
                                                 DMI)
    diet_data['Dt_DigrOMa'] = calculate_Dt_DigrOMa(diet_data['Dt_DigrOMaIn'],
                                                   DMI)
    diet_data['Dt_DigrOMa_Dt'] = calculate_Dt_DigrOMa_Dt(diet_data['Dt_rOM'],
                                                         coeff_dict)
    diet_data['Dt_DigrOMt'] = calculate_Dt_DigrOMt(diet_data['Dt_DigrOMtIn'],
                                                   DMI)  
    diet_data['Dt_DigNDFnfIn'] = calculate_Dt_DigNDFnfIn(diet_data['TT_dcNDF'],
                                                         diet_data['Dt_NDFnfIn'])
    diet_data['Dt_DigNDF'] = calculate_Dt_DigNDF(diet_data['Dt_DigNDFIn'],
                                                 DMI)
    diet_data['Dt_DigNDFnf'] = calculate_Dt_DigNDFnf(diet_data['Dt_DigNDFnfIn'],
                                                     DMI)
    diet_data['Dt_idcRUP'] = calculate_Dt_idcRUP(diet_data['Dt_idRUPIn'],
                                                 diet_data['Dt_RUPIn'])
    diet_data['Dt_Fe_RUPout'] = calculate_Dt_Fe_RUPout(df['Fd_Fe_RUPout'])
    diet_data['Dt_RDTPIn'] = calculate_Dt_RDTPIn(diet_data['Dt_RDPIn'],
                                                 diet_data['Dt_NPNCPIn'],
                                                 coeff_dict)
    diet_data['Dt_RDP'] = calculate_Dt_RDP(diet_data['Dt_RDPIn'],
                                           DMI)
    diet_data['Dt_RDP_CP'] = calculate_Dt_RDP_CP(diet_data['Dt_RDP'],
                                                 diet_data['Dt_CP'])
    
    diet_data['Dt_DigUFAIn'] = calculate_Dt_DigUFAIn(diet_data['Dt_DigC161In'],
                                                     diet_data['Dt_DigC181tIn'],
                                                     diet_data['Dt_DigC181cIn'],
                                                     diet_data['Dt_DigC182In'],
                                                     diet_data['Dt_DigC183In'])
    diet_data['Dt_DigMUFAIn'] = calculate_Dt_DigMUFAIn(diet_data['Dt_DigC161In'],
                                                       diet_data['Dt_DigC181tIn'],
                                                       diet_data['Dt_DigC181cIn'])
    diet_data['Dt_DigPUFAIn'] = calculate_Dt_DigPUFAIn(diet_data['Dt_DigC182In'],
                                                       diet_data['Dt_DigC183In'])
    diet_data['Dt_DigSatFAIn'] = calculate_Dt_DigSatFAIn(diet_data['Dt_DigFAIn'],
                                                         diet_data['Dt_DigUFAIn'])
    diet_data['Dt_DigFA'] = calculate_Dt_DigFA(diet_data['Dt_DigFAIn'],
                                               DMI)
    DigFA_FA_list = [
        'DigFA',
        'DigC120',
        'DigC140',
        'DigC160',
        'DigC161',
        'DigC180',
        'DigC181t',
        'DigC181c',
        'DigC182',
        'DigC183',
        'DigUFA',
        'DigMUFA',
        'DigPUFA',
        'DigSatFA',
        'DigOtherFA'
    ]
    for FA in DigFA_FA_list:
        diet_data[f'Dt_{FA}_FA'] = diet_data[f'Dt_{FA}In'] / diet_data['Dt_FAIn'] * 100 # Line 1288-1302
    
    diet_data['TT_dcDtFA'] = calculate_TT_dcDtFA(diet_data['Dt_DigFAIn'],
                                                 diet_data['Dt_FAIn'])
    return diet_data


def calculate_diet_data_complete(
        diet_data_initial: dict, 
        An_StatePhys: str, 
        DMI: float,
        Fe_CP: float,
        Fe_CPend: float, 
        Fe_MiTP: float,
        Fe_NPend: float,
        Monensin_eqn: int, #equation_selection['Monensin_eqn'] 
        Du_IdAAMic: pd.Series,
        Du_idMiTP: float,
        coeff_dict: dict
        ):
    """
    Du_IdAAMic is a series passed from the AA_values dataframe, used to calculate Dt_IdAAIn
    """
    complete_diet_data = diet_data_initial.copy()

    complete_diet_data['Dt_DigCPaIn'] = calculate_Dt_DigCPaIn(complete_diet_data['Dt_CPIn'],
                                                              Fe_CP)
    complete_diet_data['Dt_DigCPtIn'] = calculate_Dt_DigCPtIn(An_StatePhys,
                                                 complete_diet_data['Dt_DigCPaIn'],
                                                 Fe_CPend,
                                                 complete_diet_data['Dt_RDPIn'],
                                                 complete_diet_data['Dt_idRUPIn'])
    complete_diet_data['Dt_DigTPaIn'] = calculate_Dt_DigTPaIn(complete_diet_data['Dt_RDTPIn'],
                                                              Fe_MiTP,
                                                              complete_diet_data['Dt_idRUPIn'],
                                                              Fe_NPend)
    complete_diet_data['Dt_DigTPtIn'] = calculate_Dt_DigTPtIn(complete_diet_data['Dt_RDTPIn'],
                                                              complete_diet_data['Dt_idRUPIn'])
    complete_diet_data['Dt_DigCPa'] = calculate_Dt_DigCPa(complete_diet_data['Dt_DigCPaIn'],
                                                          DMI)
    complete_diet_data['TT_dcDtCPa'] = calculate_TT_dcDtCPa(complete_diet_data['Dt_DigCPaIn'],
                                                            complete_diet_data['Dt_CPIn'])
    complete_diet_data['Dt_DigCPt'] = calculate_Dt_DigCPt(complete_diet_data['Dt_DigCPtIn'],
                                                          DMI)
    complete_diet_data['Dt_DigTPt'] = calculate_Dt_DigTPt(complete_diet_data['Dt_DigTPtIn'],
                                                          DMI)
    complete_diet_data['TT_dcDtCPt'] = calculate_TT_dcDtCPt(complete_diet_data['Dt_DigCPtIn'],
                                                            complete_diet_data['Dt_CPIn'])
    complete_diet_data['Dt_MPIn'] = calculate_Dt_MPIn(An_StatePhys,
                                                      complete_diet_data['Dt_CPIn'],
                                                      Fe_CP,
                                                      Fe_CPend,
                                                      complete_diet_data['Dt_idRUPIn'],
                                                      Du_idMiTP)
    complete_diet_data['Dt_MP'] = calculate_Dt_MP(complete_diet_data['Dt_MPIn'], 
                                       DMI)
    complete_diet_data['Dt_DECPIn'] = calculate_Dt_DECPIn(complete_diet_data['Dt_DigCPaIn'],
                                                          coeff_dict)
    complete_diet_data['Dt_DETPIn'] = calculate_Dt_DETPIn(complete_diet_data['Dt_DECPIn'],
                                                          complete_diet_data['Dt_DENPNCPIn'],
                                                          coeff_dict)
    complete_diet_data['Dt_DEIn'] = calculate_Dt_DEIn(An_StatePhys,
                                                      complete_diet_data['Dt_DENDFIn'],
                                                      complete_diet_data['Dt_DEStIn'],
                                                      complete_diet_data['Dt_DErOMIn'],
                                                      complete_diet_data['Dt_DETPIn'],
                                                      complete_diet_data['Dt_DENPNCPIn'],
                                                      complete_diet_data['Dt_DEFAIn'],
                                                      complete_diet_data['Dt_DMIn_ClfLiq'],
                                                      complete_diet_data['Dt_DEIn_base_ClfLiq'],
                                                      complete_diet_data['Dt_DEIn_base_ClfDry'],
                                                      Monensin_eqn
                                                      )
    AA_list = ['Arg', 'His', 'Ile', 'Leu','Lys', 'Met', 'Phe', 'Thr', 'Trp', 'Val']
    for AA in AA_list:
        # Dt_IdAAIn
        complete_diet_data[f'Dt_Id{AA}In'] = Du_IdAAMic[f'{AA}'] + complete_diet_data[f'Dt_Id{AA}RUPIn']
    complete_diet_data['Dt_DigOMaIn'] = calculate_Dt_DigOMaIn(complete_diet_data['Dt_DigNDFIn'],
                                                              complete_diet_data['Dt_DigStIn'],
                                                              complete_diet_data['Dt_DigFAIn'],
                                                              complete_diet_data['Dt_DigrOMaIn'],
                                                              complete_diet_data['Dt_DigCPaIn'])
    complete_diet_data['Dt_DigOMtIn'] = calculate_Dt_DigOMtIn(complete_diet_data['Dt_DigNDFIn'],
                                                              complete_diet_data['Dt_DigStIn'],
                                                              complete_diet_data['Dt_DigFAIn'],
                                                              complete_diet_data['Dt_DigrOMtIn'],
                                                              complete_diet_data['Dt_DigCPtIn'])
    complete_diet_data['Dt_DigOMa'] = calculate_Dt_DigOMa(complete_diet_data['Dt_DigOMaIn'],
                                                          DMI)
    complete_diet_data['Dt_DigOMt'] = calculate_Dt_DigOMt(complete_diet_data['Dt_DigOMtIn'],
                                                          DMI)
    return complete_diet_data
