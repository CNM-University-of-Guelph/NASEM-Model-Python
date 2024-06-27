from typing import Any, Type, Union, List, Dict

import pandas as pd
import nasem_dairy as nd

def check_input_type(input_value: Any, 
                     expected_type: Type, 
                     var_name: str
) -> None:
    """
    Check the input data has the expected type
    """
    if not isinstance(input_value, expected_type):
        raise TypeError(f"{var_name} must be a {expected_type.__name__}")


def check_and_convert_type(input_dict: dict, type_mapping: dict) -> dict:
    """
    For each value in a dictionary check that the type is correct. Atttempt to
    convert to the correct type and raise a TypeError if this fails.
    """
    corrected_input = {}
    for key, expected_type in type_mapping.items():
        if key in input_dict:
            value = input_dict[key]
            if not isinstance(value, expected_type):
                try:
                    corrected_value = expected_type(value)
                except (ValueError, TypeError) as e:
                    raise TypeError(
                        f"Value for {key} must be of type {expected_type.__name__}. "
                        f"Got {type(value).__name__} instead and failed to convert."
                    ) from e
                corrected_input[key] = corrected_value
            else:
                corrected_input[key] = value
    return corrected_input


def check_keys_presence(input_keys: list, required_keys: list) -> None:
    """
    Checks that required keys are present in a given iterable.
    """
    missing_keys = set(required_keys) - set(input_keys)
    if missing_keys:
        raise KeyError(f"The following keys are missing: {missing_keys}")


def check_value_is_valid(input_value: Union[str, int], 
                         valid_values: list, 
                         value_name: str
) -> None:
    """
    Check that the input value is included in a list of valid values.
    """
    if input_value not in valid_values:
        raise ValueError(f"{value_name} must be one of {valid_values}, "
                         f"{input_value} was given")


def validate_user_diet(user_diet: pd.DataFrame) -> pd.DataFrame:
    check_input_type(user_diet, pd.DataFrame, "user_diet")
    
    expected_columns = ["Feedstuff", "kg_user"]
    check_keys_presence(user_diet.columns, expected_columns)
    
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
    check_input_type(animal_input, dict, "animal_input")
    
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
    
    check_keys_presence(animal_input, type_mapping.keys())
    corrected_input = check_and_convert_type(animal_input, type_mapping)
    check_value_is_valid(animal_input["An_StatePhys"],
                         ["Calf", "Heifer", "Dry Cow", "Lactating Cow", "Other"],
                         "An_StatePhys"
                         )
    check_value_is_valid(animal_input["An_Breed"],
                         ["Holstein", "Jersey", "Other"],
                         "An_Breed"
                         )
    return corrected_input


def validate_equation_selection(equation_selection: dict) -> dict:
    check_input_type(equation_selection, dict, "equation_selection")
    
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
    
    check_keys_presence(equation_selection, input_mapping.keys())
    corrected_input = check_and_convert_type(
        equation_selection, {key: int for key in input_mapping.keys()}
        )
    for key, value in corrected_input.items():
        if value not in input_mapping[key]:
            raise ValueError(
                f"{value} is not a valid input for {key}, "
                f"select from {input_mapping[key]}"
                )
    return corrected_input


def validate_feed_library_df(feed_library_df: pd.DataFrame, 
                             user_diet: pd.DataFrame
) -> pd.DataFrame:
    check_input_type(feed_library_df, pd.DataFrame, "feed_library_df")
    check_input_type(user_diet, pd.DataFrame, "user_diet")
    
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
    
    check_keys_presence(feed_library_df.columns, expected_columns)
    missing_feeds = set(user_diet["Feedstuff"]) - set(feed_library_df["Fd_Name"])
    if missing_feeds:
        raise ValueError(
            f"The following feeds are missing in the feed library: {missing_feeds}"
            )
    return feed_library_df


def validate_coeff_dict(coeff_dict: dict) -> dict:
    default_coeff_dict = nd.coeff_dict
    check_input_type(coeff_dict, dict, "coeff_dict")
    check_keys_presence(coeff_dict, default_coeff_dict.keys())
    corrected_dict = check_and_convert_type(
        coeff_dict, 
        {key: type(value) for key, value in default_coeff_dict.items()}
        )
    differing_keys = [
        key for key in default_coeff_dict 
        if corrected_dict[key] != default_coeff_dict[key]
        ]
    if differing_keys:
        print("The following keys differ from their default values: ")
        for key in differing_keys:
            print(f"{key}: User: {corrected_dict[key]}, "
                  f"Default: {default_coeff_dict[key]}")
    else:
        print("All values match the default coefficients.")
    return corrected_dict


def validate_infusion_input(infusion_input: dict) -> dict:
    default_infusion_dict = nd.infusion_dict
    check_input_type(infusion_input, dict, "infusion_input")
    check_keys_presence(infusion_input, default_infusion_dict.keys())
    corrected_input = check_and_convert_type(
        infusion_input,
        {key: type(value) for key, value in default_infusion_dict.items()}
    )
    check_value_is_valid(infusion_input["Inf_Location"],
                         ["Rumen", "Abomasum", "Duodenum", "Jugular",
                          "Arterial", "Iliac Artery" , "Blood"],
                          "Inf_Location"
                          )
    return corrected_input


def validate_MP_NP_efficiency_input(MP_NP_efficiency_input: dict) -> dict:
    default_MP_NP_efficiency = nd.MP_NP_efficiency_dict
    check_input_type(MP_NP_efficiency_input, dict, "MP_NP_efficiency_input")
    check_keys_presence(
        MP_NP_efficiency_input.keys(), default_MP_NP_efficiency.keys()
        )
    corrected_values = check_and_convert_type(
        MP_NP_efficiency_input, 
        {key: type(value) for key, value in default_MP_NP_efficiency.items()}
        )
    return corrected_values


def validate_mPrt_coeff_list(mPrt_coeff_list: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    default_keys = nd.mPrt_coeff_list[0].keys()
    check_input_type(mPrt_coeff_list, list, "mPrt_coeff_list")
    for index, coeffs in enumerate(mPrt_coeff_list):
        check_input_type(coeffs, dict, f"mPrt_coeff_list[{index}]")
        check_keys_presence(coeffs, default_keys)
        for key, value in coeffs.items():
            if not isinstance(value, (int, float)):
                raise TypeError(
                    f"Value for {key} in mPrt_coeff_list[{index}] must be int "
                    f"or float. Got {type(value).__name__} instead."
                )
    return mPrt_coeff_list


def validate_f_Imb(f_Imb: pd.Series) -> pd.Series:
    required_index = [
        'Arg', 'His', 'Ile', 'Leu', 'Lys', 'Met', 'Phe', 'Thr', 'Trp', 'Val'
    ]
    check_input_type(f_Imb, pd.Series, "f_Imb")
    check_keys_presence(f_Imb.index, required_index)
    if not f_Imb.apply(lambda x: isinstance(x, (int, float))).all():
        raise TypeError("All values in f_Imb must be int or float")
    return f_Imb
    