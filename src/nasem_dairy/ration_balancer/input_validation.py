import pandas as pd
import nasem_dairy as nd

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


def validate_animal_input(animal_input: dict) -> dict:
    if not isinstance(animal_input, dict):
        raise TypeError("animal_input must be a dictionary")
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
    an_statephys_values = ["Calf", "Heifer", "Dry Cow", "Lactating Cow", "Other"]
    an_breed_values = ["Holstein", "Jersey", "Other"]
    corrected_input = {}

    for key in type_mapping.keys():
        if key not in animal_input:
            raise KeyError(f"Missing required key: {key}")
        value = animal_input[key]
        expected_type = type_mapping[key]
        try:
            corrected_value = expected_type(value)
        except ValueError as e:
            raise ValueError(
                f"Error converting {key}: {value} to {expected_type.__name__}"
                ) from e
        
        if key == "An_StatePhys" and corrected_value not in an_statephys_values:
            raise ValueError(f"An_StatePhys must be one of {an_statephys_values}")
        
        if key == "An_Breed" and corrected_value not in an_breed_values:
            raise ValueError(f"An_Breed must be one of {an_breed_values}")

        corrected_input[key] = corrected_value
    return corrected_input


def validate_equation_selection(equation_selection: dict) -> dict:
    if not isinstance(equation_selection, dict):
        raise TypeError("equation_selection must be a dictionary")
    input_mapping = {
        "Use_DNDF_IV": (0, 1, 2),
        "DMIn_eqn": tuple(range(0, 18)),
        "mProd_eqn": (0, 1, 2, 3, 4),
        "MiN_eqn": (1, 2, 3),
        "use_infusions": (0, 1),
        "NonMilkCP_ClfLiq": (0, 1),
        "Monensin_eqn": (0, 1),
        "mPrt_eqn": (0, 1, 2, 3),
        "mFat_eqn": (0, 1),
        "RumDevDisc_Clf": (0, 1)
    }
    corrected_input = {}
    for key in input_mapping.keys():
        if key not in equation_selection:
            raise KeyError(f"Missing required key: {key}")
        value = equation_selection[key]
        try:
            corrected_value = int(value)
        except ValueError as e:
            raise ValueError(f"Error converting {key}: {value} to int") from e
        if corrected_value not in input_mapping[key]:
            raise ValueError(
                f"{corrected_value} is not a valid input for {key}, select from"
                f" {input_mapping[key]}"
                )
        corrected_input[key] = corrected_value
    return corrected_input


def validate_feed_library_df(feed_library_df: pd.DataFrame, 
                             user_diet: pd.DataFrame
) -> pd.DataFrame:
    # NOTE Should also check types of columns but should make decision about
    # empty cells in feed library first
    if not isinstance(feed_library_df, pd.DataFrame):
        raise TypeError("feed_library_df must be a pandas DataFrame")
    expected_columns = [
        "Fd_Libr", "UID", "Fd_Index", "Fd_Name", "Fd_Category", "Fd_Type", 
        "Fd_DM", "Fd_Conc", "Fd_Locked", "Fd_DE_Base", "Fd_ADF", "Fd_NDF", 
        "Fd_DNDF48", "Fd_DNDF48_NDF", "Fd_Lg", "Fd_CP", "Fd_St", "Fd_dcSt", 
        "Fd_WSC", "Fd_CPARU", "Fd_CPBRU", "Fd_CPCRU", "Fd_dcRUP", "Fd_CPs_CP", 
        "Fd_KdRUP", "Fd_RUP_base", "Fd_NPN_CP", "Fd_NDFIP", "Fd_ADFIP", 
        "Fd_Arg_CP", "Fd_His_CP", "Fd_Ile_CP", "Fd_Leu_CP", "Fd_Lys_CP", 
        "Fd_Met_CP", "Fd_Phe_CP", "Fd_Thr_CP", "Fd_Trp_CP", "Fd_Val_CP", 
        "Fd_CFat", "Fd_FA", "Fd_dcFA", "Fd_Ash", "Fd_C120_FA", "Fd_C140_FA", 
        "Fd_C160_FA", "Fd_C161_FA", "Fd_C180_FA", "Fd_C181t_FA", "Fd_C181c_FA", 
        "Fd_C182_FA", "Fd_C183_FA", "Fd_OtherFA_FA", "Fd_Ca", "Fd_P", 
        "Fd_Pinorg_P", "Fd_Porg_P", "Fd_Na", "Fd_Cl", "Fd_K", "Fd_Mg", "Fd_S", 
        "Fd_Cr", "Fd_Co", "Fd_Cu", "Fd_Fe", "Fd_I", "Fd_Mn", "Fd_Mo", "Fd_Se", 
        "Fd_Zn", "Fd_B_Carotene", "Fd_Biotin", "Fd_Choline", "Fd_Niacin", 
        "Fd_VitA", "Fd_VitD", "Fd_VitE", "Fd_acCa", "Fd_acPtot", "Fd_acNa", 
        "Fd_acCl", "Fd_acK", "Fd_acCu", "Fd_acFe", "Fd_acMg", "Fd_acMn", 
        "Fd_acZn"
        ]
    if list(feed_library_df.columns) != expected_columns:
        raise ValueError(
            f"feed_library_df must have the columns {expected_columns}"
            )
    missing_feeds = set(user_diet["Feedstuff"]) - set(feed_library_df["Fd_Name"])
    if missing_feeds:
        raise ValueError(
            f"The following feeds are missing in the feed library: {missing_feeds}"
            )
    return feed_library_df


def validate_coeff_dict(coeff_dict: dict) -> dict:
    default_coeff_dict = nd.coeff_dict
    if not isinstance(coeff_dict, dict):
        raise TypeError("coeff_dict must be a dictionary")
    
    missing_keys = set(default_coeff_dict) - set(coeff_dict)
    if missing_keys:
        raise KeyError("The following keys are missing from the user entered " 
                       f"coeff_dict: {missing_keys}")
    
    differing_keys = []
    for key, default_value in default_coeff_dict.items():
        user_value = coeff_dict[key]
        if not isinstance(user_value, type(default_value)):
            raise TypeError(
                f"Value for {key} must be of type {type(default_value).__name__}."
                f" Got {type(user_value).__name__} instead"
                )
        if user_value != default_value:
            differing_keys.append(key)
    
    if differing_keys:
        print("The following keys differ from their default values: ")
        for key in differing_keys:
            print(f"{key}: User: {coeff_dict[key]}, "
                  f"Default: {default_coeff_dict[key]}")
    else:
        print("All values match the default coefficients.")
    return coeff_dict


def validate_infusion_input(infusion_input):
    pass


def validate_MP_NP_efficiency_input(MP_NP_efficiency_input):
    pass


def validate_mPrt_coeff_list(mPrt_coeff_list):
    pass


def validate_f_Imb(f_Imb):
    pass
