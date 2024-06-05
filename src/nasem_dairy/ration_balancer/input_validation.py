def validate_animal_input(animal_input):
    type_mapping = {
            'An_Parity_rl': float,
            'Trg_MilkProd': float,
            'An_BW': float,
            'An_BCS': float,
            'An_LactDay': int,
            'Trg_MilkFatp': float,
            'Trg_MilkTPp': float,
            'Trg_MilkLacp': float,
            'DMI': float,  # aka. Trg_Dt_DMIn
            'An_BW_mature': float,
            'Trg_FrmGain': float,
            'An_GestDay': int,
            'An_GestLength': int,
            'Trg_RsrvGain': float,
            'Fet_BWbrth': float,
            'An_AgeDay': int,
            'An_305RHA_MlkTP': float,
            'An_StatePhys': str,
            'An_Breed': str,
            'An_AgeDryFdStart': int,
            'Env_TempCurr': float,
            'Env_DistParlor': float,
            'Env_TripsParlor': int,
            'Env_Topo': float
    }
    corrected_input = {}
    for key, value in animal_input.items():
        if key in type_mapping:
            try:
                corrected_input[key] = type_mapping[key](value)
            except ValueError as e:
                raise ValueError(f"Error converting {key}: {value} to {type_mapping[key].__name__}") from e
        else:
            corrected_input[key] = value

    return corrected_input

