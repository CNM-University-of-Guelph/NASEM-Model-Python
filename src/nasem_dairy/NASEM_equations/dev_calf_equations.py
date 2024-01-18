# dev_calf_equations
import numpy as np

def calculate_K_FeCPend_ClfLiq(An_StatePhys, NonMilkCP_ClfLiq):
    condition = (An_StatePhys == "Calf") and (NonMilkCP_ClfLiq > 0)
    K_FeCPend_ClfLiq = np.where(condition, 34.4, 11.9)
    return K_FeCPend_ClfLiq
