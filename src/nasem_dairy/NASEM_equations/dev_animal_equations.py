# dev_animal_equations

def calculate_An_RDPIn(Dt_RDPIn, InfRum_RDPIn):
    An_RDPIn = Dt_RDPIn + InfRum_RDPIn
    return An_RDPIn

def calculate_An_RDP(An_RDPIn, Dt_DMIn, InfRum_DMIn):
    An_RDP = An_RDPIn / (Dt_DMIn + InfRum_DMIn) * 100
    return An_RDP

def calculate_An_RDPIn_g(An_RDPIn):
    An_RDPIn_g = An_RDPIn * 1000
    return An_RDPIn_g

def calculate_An_data(animal_input, diet_data, infusion_data):
    # Could use a better name, An_data for now
    An_data = {}
    An_data['An_RDPIn'] = calculate_An_RDPIn(diet_data['Dt_RDPIn'], 
                                             infusion_data['InfRum_RDPIn'])
    An_data['An_RDP'] = calculate_An_RDP(An_data['An_RDPIn'],
                                         animal_input['DMI'],
                                         infusion_data['InfRum_DMIn'])
    An_data['An_RDPIn_g'] = calculate_An_RDPIn_g(An_data['An_RDPIn'])
    return An_data
