# dev_milk_equations
# All calculations related to milk production, milk components, and milk energy

def calculate_Trg_NEmilk_Milk(Trg_MilkTPp, 
                              Trg_MilkFatp, 
                              Trg_MilkLacp):
    if Trg_MilkLacp is None or Trg_MilkTPp is None:         # If milk protein or milk lactose are missing use Tyrrell and Reid (1965) eqn.
        Trg_NEmilk_Milk = 0.36 + 9.69 * Trg_MilkFatp/100    # Line 385/2888
    else:
        Trg_NEmilk_Milk = 9.29*Trg_MilkFatp/100 + 5.85*Trg_MilkTPp/100 + 3.95*Trg_MilkLacp/100  # Line 383/2887
    return Trg_NEmilk_Milk