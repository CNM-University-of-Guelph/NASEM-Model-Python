from typing import Any, Type, Union, List, Dict, Literal, get_args

import pandas as pd

import nasem_dairy as nd
import nasem_dairy.model.input_definitions as expected

# Helper Function
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

            # Check if the expected type is a Literal
            if hasattr(expected_type, '__origin__') and expected_type.__origin__ is Literal:
                valid_values = get_args(expected_type)
                valid_type = type(valid_values[0])
                if not isinstance(value, valid_type):
                    try:
                        corrected_value = valid_type(value)
                    except (ValueError, TypeError) as e:
                        raise TypeError(
                            f"Value for {key} must be of type {valid_type.__name__}. "
                            f"Got {type(value).__name__} instead and failed to convert."
                        ) from e
                else:
                    corrected_value = value

                check_value_is_valid(corrected_value, valid_values, key)
                corrected_input[key] = corrected_value
           
            else:
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

# Validation Functions 
def validate_user_diet(user_diet: pd.DataFrame) -> pd.DataFrame:
    check_input_type(user_diet, pd.DataFrame, "user_diet")
    
    expected_columns = expected.UserDietSchema.keys()
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

    type_mapping = expected.AnimalInput.__annotations__.copy()

    if animal_input["An_StatePhys"] != "Heifer":
        type_mapping.pop("An_AgeConcept1st") # Heifers have an extra input

    check_keys_presence(animal_input, type_mapping.keys())
    corrected_input = check_and_convert_type(animal_input, type_mapping)
    
    if corrected_input["An_StatePhys"] == "Heifer":
        if "An_AgeConcept1st" not in corrected_input.keys():
            raise KeyError("The An_AgeConcept1st key is missing")        
        if not isinstance(corrected_input["An_AgeConcept1st"], int):
            raise TypeError("An_AgeConcept1st must be an int")
    return corrected_input


def validate_equation_selection(equation_selection: dict) -> dict:
    check_input_type(equation_selection, dict, "equation_selection")
    
    input_mapping = expected.EquationSelection.__annotations__.copy()
    
    check_keys_presence(equation_selection, input_mapping.keys())
    corrected_input = check_and_convert_type(
        equation_selection, input_mapping
        )       
    return corrected_input


def validate_feed_library_df(feed_library_df: pd.DataFrame, 
                             user_diet: pd.DataFrame
) -> pd.DataFrame:
    check_input_type(feed_library_df, pd.DataFrame, "feed_library_df")
    check_input_type(user_diet, pd.DataFrame, "user_diet")

    expected_columns = expected.FeedLibrarySchema.keys()

    check_keys_presence(feed_library_df.columns, expected_columns)
    missing_feeds = set(user_diet["Feedstuff"]) - set(feed_library_df["Fd_Name"])
    if missing_feeds:
        raise ValueError(
            f"The following feeds are missing in the feed library: {missing_feeds}"
            )
    return feed_library_df


def validate_coeff_dict(coeff_dict: dict) -> dict:
    expected_coeff_dict = expected.CoeffDict.__annotations__.copy()

    check_input_type(coeff_dict, dict, "coeff_dict")
    check_keys_presence(coeff_dict, expected_coeff_dict.keys())
    corrected_dict = check_and_convert_type(
        coeff_dict, 
        expected_coeff_dict
        )
    
    # Use the default coeff_dict to check for differing values
    default_coeff_dict = nd.coeff_dict
    differing_keys = [
        key for key in default_coeff_dict 
        if corrected_dict[key] != default_coeff_dict[key]
        ]
    if differing_keys:
        print("The following keys differ from their default values: ")
        for key in differing_keys:
            print(f"{key}: User: {corrected_dict[key]}, "
                  f"Default: {default_coeff_dict[key]}")
    return corrected_dict


def validate_infusion_input(infusion_input: dict) -> dict:
    expected_infusion_dict = expected.InfusionDict.__annotations__.copy()

    check_input_type(infusion_input, dict, "infusion_input")
    check_keys_presence(infusion_input, expected_infusion_dict.keys())
    corrected_input = check_and_convert_type(
        infusion_input,
        expected_infusion_dict
    )    
    return corrected_input


def validate_MP_NP_efficiency_input(MP_NP_efficiency_input: dict) -> dict:
    expected_MP_NP_efficiency = expected.MPNPEfficiencyDict.__annotations__.copy()
    check_input_type(MP_NP_efficiency_input, dict, "MP_NP_efficiency_input")
    check_keys_presence(
        MP_NP_efficiency_input.keys(), expected_MP_NP_efficiency.keys()
        )
    corrected_values = check_and_convert_type(
        MP_NP_efficiency_input, expected_MP_NP_efficiency
        )
    return corrected_values


def validate_mPrt_coeff_list(mPrt_coeff_list: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    default_keys = expected.mPrtCoeffDict.__annotations__.copy()
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
    expected_f_Imb = expected.f_Imb
    check_input_type(f_Imb, pd.Series, "f_Imb")
    check_keys_presence(f_Imb.index, expected_f_Imb.index)
    if not f_Imb.apply(lambda x: isinstance(x, (int, float))).all():
        raise TypeError("All values in f_Imb must be int or float")
    return f_Imb
    