"""Functions for adjusting coefficient values used in the model. 
"""

def adjust_LCT(An_AgeDay: int) -> int:
    """
    An_AgeDay: Animal age in days
    LCT: Lower critical temperature in degrees celcius
    """
    if An_AgeDay > 21:
        LCT = 5  # calf > 3 wks of age, Line 229
    else:
        LCT = 15
    return LCT
