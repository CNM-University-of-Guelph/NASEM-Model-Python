# These calculations are part of the NASEM model but never get used anywhere in the model
# import nasem_dairy.nasem_equations.unused as unused 


def calculate_Dt_DMIn_BW(Dt_DMIn: float, An_BW: float) -> float:
    """
    Dt_DMIn_BW: Ratio of DMI to bodyweight
    """
    Dt_DMIn_BW = Dt_DMIn / An_BW  # Line 437
    return Dt_DMIn_BW


def calculate_Dt_DMIn_MBW(Dt_DMIn: float, An_BW: float) -> float:
    """
    Dt_DMIn_MBW: Ratio of DMI to metabolic BW
    """
    Dt_DMIn_MBW = Dt_DMIn / An_BW**0.75  # Line 438
    return Dt_DMIn_MBW
