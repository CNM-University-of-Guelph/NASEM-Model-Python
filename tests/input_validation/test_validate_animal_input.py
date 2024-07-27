import pytest

from nasem_dairy.model.input_validation import validate_animal_input

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
    'An_AgeDay': float,
    'An_305RHA_MlkTP': float,
    'An_StatePhys': str,
    'An_Breed': str,
    'An_AgeDryFdStart': int,
    'Env_TempCurr': float,
    'Env_DistParlor': float,
    'Env_TripsParlor': int,
    'Env_Topo': float
}

def test_not_a_dictionary():
    with pytest.raises(TypeError, match="must be a dict"):
        validate_animal_input(["not", "a", "dict"])


def test_missing_key_raises_key_error():
    animal_input = {
        "An_StatePhys": "Lactating Cow",
        "An_Parity_rl": 2.0,
    }
    with pytest.raises(KeyError, match="The following keys are missing: "):
        validate_animal_input(animal_input)


def test_invalid_statephys_value():
    animal_input = {
        "An_Parity_rl": 2.0,
        "Trg_MilkProd": 30.0,
        "An_BW": 600.0,
        "An_BCS": 3.0,
        "An_LactDay": 100,
        "Trg_MilkFatp": 3.5,
        "Trg_MilkTPp": 3.2,
        "Trg_MilkLacp": 4.8,
        "DMI": 22.0,  
        "An_BW_mature": 650.0,
        "Trg_FrmGain": 1.0,
        "An_GestDay": 150,
        "An_GestLength": 280,
        "Trg_RsrvGain": 0.5,
        "Fet_BWbrth": 40.0,
        "An_AgeDay": 900.0,
        "An_305RHA_MlkTP": 3.2,
        "An_StatePhys": "Invalid",
        "An_Breed": "Holstein",
        "An_AgeDryFdStart": 60,
        "Env_TempCurr": 20.0,
        "Env_DistParlor": 0.5,
        "Env_TripsParlor": 3,
        "Env_Topo": 0.2
    }
    with pytest.raises(ValueError, match="An_StatePhys must be one of"):
        validate_animal_input(animal_input)


def test_invalid_breed_value():
    animal_input = {
        "An_Parity_rl": 2.0,
        "Trg_MilkProd": 30.0,
        "An_BW": 600.0,
        "An_BCS": 3.0,
        "An_LactDay": 100,
        "Trg_MilkFatp": 3.5,
        "Trg_MilkTPp": 3.2,
        "Trg_MilkLacp": 4.8,
        "DMI": 22.0,  
        "An_BW_mature": 650.0,
        "Trg_FrmGain": 1.0,
        "An_GestDay": 150,
        "An_GestLength": 280,
        "Trg_RsrvGain": 0.5,
        "Fet_BWbrth": 40.0,
        "An_AgeDay": 900.0,
        "An_305RHA_MlkTP": 3.2,
        "An_StatePhys": "Lactating Cow",
        "An_Breed": "Invalid",
        "An_AgeDryFdStart": 60,
        "Env_TempCurr": 20.0,
        "Env_DistParlor": 0.5,
        "Env_TripsParlor": 3,
        "Env_Topo": 0.2
    }
    with pytest.raises(ValueError, match="An_Breed must be one of"):
        validate_animal_input(animal_input)


def test_correct_data_types():
    animal_input = {
        "An_Parity_rl": "2.0",
        "Trg_MilkProd": "30.0",
        "An_BW": "600.0",
        "An_BCS": "3.0",
        "An_LactDay": "100",
        "Trg_MilkFatp": "3.5",
        "Trg_MilkTPp": "3.2",
        "Trg_MilkLacp": "4.8",
        "DMI": "22.0",  
        "An_BW_mature": "650.0",
        "Trg_FrmGain": "1.0",
        "An_GestDay": "150",
        "An_GestLength": "280",
        "Trg_RsrvGain": "0.5",
        "Fet_BWbrth": "40.0",
        "An_AgeDay": "900.0",
        "An_305RHA_MlkTP": "3.2",
        "An_StatePhys": "Lactating Cow",
        "An_Breed": "Holstein",
        "An_AgeDryFdStart": "60",
        "Env_TempCurr": "20.0",
        "Env_DistParlor": "0.5",
        "Env_TripsParlor": "3",
        "Env_Topo": "0.2"
    }
    result = validate_animal_input(animal_input)
    for key, value in animal_input.items():
        assert isinstance(result[key], type_mapping.get(key, str))


def test_invalid_conversion():
    animal_input = {
        "An_Parity_rl": "two",
        "Trg_MilkProd": "30.0",
        "An_BW": "600.0",
        "An_BCS": "3.0",
        "An_LactDay": "100",
        "Trg_MilkFatp": "3.5",
        "Trg_MilkTPp": "3.2",
        "Trg_MilkLacp": "4.8",
        "DMI": "22.0",  
        "An_BW_mature": "650.0",
        "Trg_FrmGain": "1.0",
        "An_GestDay": "150",
        "An_GestLength": "280",
        "Trg_RsrvGain": "0.5",
        "Fet_BWbrth": "40.0",
        "An_AgeDay": "900.0",
        "An_305RHA_MlkTP": "3.2",
        "An_StatePhys": "Lactating Cow",
        "An_Breed": "Holstein",
        "An_AgeDryFdStart": "60",
        "Env_TempCurr": "20.0",
        "Env_DistParlor": "0.5",
        "Env_TripsParlor": "3",
        "Env_Topo": "0.2"
    }
    with pytest.raises(
        TypeError, 
        match="Value for An_Parity_rl must be of type float. Got str instead "
              "and failed to convert."
         ):
        validate_animal_input(animal_input)


def test_valid_input():
    animal_input = {
        "An_Parity_rl": 2.0,
        "Trg_MilkProd": 30.0,
        "An_BW": 600.0,
        "An_BCS": 3.0,
        "An_LactDay": 100,
        "Trg_MilkFatp": 3.5,
        "Trg_MilkTPp": 3.2,
        "Trg_MilkLacp": 4.8,
        "DMI": 22.0,  
        "An_BW_mature": 650.0,
        "Trg_FrmGain": 1.0,
        "An_GestDay": 150,
        "An_GestLength": 280,
        "Trg_RsrvGain": 0.5,
        "Fet_BWbrth": 40.0,
        "An_AgeDay": 900.0,
        "An_305RHA_MlkTP": 3.2,
        "An_StatePhys": "Lactating Cow",
        "An_Breed": "Holstein",
        "An_AgeDryFdStart": 60,
        "Env_TempCurr": 20.0,
        "Env_DistParlor": 0.5,
        "Env_TripsParlor": 3,
        "Env_Topo": 0.2
    }
    result = validate_animal_input(animal_input)
    assert result == animal_input
