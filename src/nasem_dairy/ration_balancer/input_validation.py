import pandas as pd

def validate_user_diet(user_diet: pd.DataFrame) -> pd.DataFrame:
    """
    Check that the use_diet DataFrame is formatted properly and contains the
    required data for execute_model.
    """
    if not isinstance(user_diet, pd.DataFrame):
        raise TypeError("user_diet must be a pandas DataFrame")
    expected_columns = ["Feedstuff", "kg_user"]
    if list(user_diet.columns) != expected_columns:
        raise ValueError(f"user_diet must have the columns {expected_columns}")
    user_diet["kg_user"] = pd.to_numeric(user_diet["kg_user"], errors="coerce")
    if user_diet["kg_user"].isna().any():
        raise ValueError("kg_user column must contain only numeric values")
    if not user_diet["Feedstuff"].apply(lambda x: isinstance(x, str)).all():
        raise ValueError("Feedstuff column must contain only string values")
    user_diet = (user_diet  # Combine duplicate Feedstuff entries
                 .groupby("Feedstuff", as_index=False)
                 .agg({"kg_user": "sum"})
                 )
    user_diet = user_diet.dropna()
    if user_diet.empty:
        raise ValueError(f"user_diet is an empty DataFrame")
    return user_diet


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
    corrected_input = {}
    for key, value in animal_input.items():
        if key in type_mapping:
            try:
                corrected_input[key] = type_mapping[key](value)
            except ValueError as e:
                raise ValueError(f"Error converting {key}: {value} to {type_mapping[key].__name__}") from e
        else:
            corrected_input[key] = value
# - An_StatePhys and An_Breed are valid strings
# 



    return corrected_input


def validate_equation_selection(equation_selection):
    pass


def validate_feed_library_df(feed_library_df):
    pass


def validate_coeff_dict(coeff_dict):
    pass


def validate_infusion_input(infusion_input):
    pass


def validate_MP_NP_efficiency_input(MP_NP_efficiency_input):
    pass


def validate_mPrt_coeff_list(mPrt_coeff_list):
    pass


def validate_f_Imb(f_Imb):
    pass
