"""
Validation functions for input data.

This module provides functions to validate and correct input data according to 
the expected schemas defined in `input_definitions.py`. These functions ensure 
that the input data is correctly typed, complete, and consistent with the 
model's requirements.

Functions:
    validate_user_diet: Validates the structure and content of a user diet DataFrame.
    validate_animal_input: Validates the structure and content of the animal input dictionary.
    validate_equation_selection: Validates the structure and content of the equation selection dictionary.
    validate_feed_library_df: Validates the structure and content of the feed library DataFrame.
    validate_coeff_dict: Validates and corrects the coefficient dictionary.
    validate_infusion_input: Validates the structure and content of the infusion input dictionary.
    validate_MP_NP_efficiency_input: Validates the MP/NP efficiency input dictionary.
    validate_mPrt_coeff_list: Validates a list of mPrt coefficient dictionaries.
    validate_f_Imb: Validates the structure and content of the f_Imb pandas Series.
"""

from typing import Any, Type, Union, List, Dict, Literal, get_args

import pandas as pd

import nasem_dairy as nd
import nasem_dairy.model.input_definitions as expected


def check_input_type(
    input_value: Any, 
    expected_type: Type, 
    var_name: str
) -> None:
    """
    Validates that the input data has the expected type.

    Args:
        input_value: The value to be checked.
        expected_type: The type that input_value is expected to be.
        var_name: The name of the variable being checked.

    Raises:
        TypeError: If input_value is not of the expected type.
    """
    if not isinstance(input_value, expected_type):
        raise TypeError(f"{var_name} must be a {expected_type.__name__}")


def check_and_convert_type(input_dict: dict, type_mapping: dict) -> dict:
    """
    Validates and attempts to convert the types of values in a dictionary.

    This function checks that each value in the input dictionary has the 
    expected type as specified in the type_mapping. If a value does not 
    have the expected type, it attempts to convert it. If conversion 
    fails, a TypeError is raised.

    Args:
        input_dict: The dictionary containing values to be checked.
        type_mapping: A dictionary mapping keys to expected types.

    Returns:
        dict: A dictionary with corrected values where types were successfully converted.

    Raises:
        TypeError: If a value cannot be converted to the expected type.
    """
    corrected_input = {}
    for key, expected_type in type_mapping.items():
        if key in input_dict:
            value = input_dict[key]

            # Check if the expected type is a Literal
            if hasattr(expected_type, '__origin__') and \
               expected_type.__origin__ is Literal:
                valid_values = get_args(expected_type)
                valid_type = type(valid_values[0])
                if not isinstance(value, valid_type):
                    try:
                        corrected_value = valid_type(value)
                    except (ValueError, TypeError) as e:
                        raise TypeError(
                            f"Value for {key} must be of type "
                            f"{valid_type.__name__}. Got {type(value).__name__}"
                            f" instead and failed to convert."
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
                            f"Value for {key} must be of type "
                            f"{expected_type.__name__}. Got {type(value).__name__}"
                            f" instead and failed to convert."
                        ) from e
                    corrected_input[key] = corrected_value
                else:
                    corrected_input[key] = value

    return corrected_input


def check_keys_presence(input_keys: list, required_keys: list) -> None:
    """
    Checks that required keys are present in a given iterable.

    Args:
        input_keys: A list of keys present in the input.
        required_keys: A list of keys that must be present.

    Raises:
        KeyError: If any required keys are missing.
    """
    missing_keys = set(required_keys) - set(input_keys)
    if missing_keys:
        raise KeyError(f"The following keys are missing: {missing_keys}")


def check_value_is_valid(
    input_value: Union[str, int], 
    valid_values: list, 
    value_name: str
) -> None:
    """
    Validates that the input value is included in a list of valid values.

    Args:
        input_value: The value to be validated.
        valid_values: A list of valid values.
        value_name: The name of the value being checked.

    Raises:
        ValueError: If input_value is not in valid_values.
    """
    if input_value not in valid_values:
        raise ValueError(f"{value_name} must be one of {valid_values}, "
                         f"{input_value} was given")

# Validation Functions 
def validate_user_diet(user_diet: pd.DataFrame) -> pd.DataFrame:
    """
    Validates the structure and content of a user diet DataFrame.

    This function ensures that the user diet DataFrame conforms to the expected 
    schema, including checking for the presence of required columns and validating 
    data types. It also combines duplicate feedstuff entries and removes any 
    rows with missing data.

    Args:
        user_diet: A pandas DataFrame representing the user's diet input.

    Returns:
        A cleaned and validated pandas DataFrame.

    Raises:
        TypeError: If the user_diet is not a pandas DataFrame.
        KeyError: If required columns are missing from the user_diet.
        ValueError: If the kg_user column contains non-numeric values, if the 
                    Feedstuff column contains non-string values, or if the 
                    resulting DataFrame is empty.
    """
    check_input_type(user_diet, pd.DataFrame, "user_diet")
    
    expected_columns = expected.UserDietSchema.keys()
    check_keys_presence(user_diet.columns, expected_columns)
    
    user_diet["kg_user"] = pd.to_numeric(user_diet["kg_user"], errors="coerce")
    if user_diet["kg_user"].isna().any():
        raise ValueError("kg_user column must contain only numeric values")
    if not user_diet["Feedstuff"].apply(lambda x: isinstance(x, str)).all():
        raise ValueError("Feedstuff column must contain only string values")
    user_diet = (user_diet  # Combine duplicate Feedstuff entries
                 .groupby("Feedstuff", as_index=False, sort=False)
                 .agg({"kg_user": "sum"})
                 )
    user_diet = user_diet.dropna()
    if user_diet.empty:
        raise ValueError(f"user_diet is an empty DataFrame")
    return user_diet


def validate_animal_input(animal_input: dict) -> dict:
    """
    Validates the structure and content of the animal input dictionary.

    This function ensures that the animal input dictionary contains the correct 
    keys and values according to the expected schema. It checks for the presence 
    of required keys, validates types, and attempts to convert values to the 
    correct type if necessary.

    Args:
        animal_input: A dictionary containing animal input data.

    Returns:
        A corrected dictionary with validated and possibly converted values.

    Raises:
        TypeError: If the animal_input is not a dictionary or if any value 
                   cannot be converted to the expected type.
        KeyError: If required keys are missing from the animal_input.
    """
    check_input_type(animal_input, dict, "animal_input")

    type_mapping = expected.AnimalInput.__annotations__.copy()

    if animal_input["An_StatePhys"] != "Heifer":
        type_mapping.pop("An_AgeConcept1st") # Heifers have an extra input

    check_keys_presence(animal_input, type_mapping.keys())
    corrected_input = check_and_convert_type(animal_input, type_mapping)
    
    return corrected_input


def validate_equation_selection(equation_selection: dict) -> dict:
    """
    Validates the structure and content of the equation selection dictionary.

    This function ensures that the equation selection dictionary contains the 
    correct keys and values according to the expected schema. It checks for 
    the presence of required keys, validates types, and attempts to convert 
    values to the correct type if necessary.

    Args:
        equation_selection: A dictionary containing equation selection data.

    Returns:
        A corrected dictionary with validated and possibly converted values.

    Raises:
        TypeError: If the equation_selection is not a dictionary or if any value 
                   cannot be converted to the expected type.
        KeyError: If required keys are missing from the equation_selection.
    """
    check_input_type(equation_selection, dict, "equation_selection")
    
    input_mapping = expected.EquationSelection.__annotations__.copy()
    
    check_keys_presence(equation_selection, input_mapping.keys())
    corrected_input = check_and_convert_type(
        equation_selection, input_mapping
        )       
    return corrected_input


def validate_feed_library_df(
    feed_library: pd.DataFrame, 
    user_diet: pd.DataFrame
) -> pd.DataFrame:
    """
    Validates the structure and content of the feed library DataFrame.

    This function ensures that the feed library DataFrame contains the correct 
    columns according to the expected schema and checks for the presence of 
    all feeds listed in the user diet DataFrame.

    Args:
        feed_library: A pandas DataFrame representing the feed library.
        user_diet: A pandas DataFrame representing the user's diet input.

    Returns:
        The validated feed library DataFrame.

    Raises:
        TypeError: If feed_library or user_diet is not a pandas DataFrame.
        KeyError: If required columns are missing from the feed_library.
        ValueError: If any feeds listed in the user_diet are missing from the 
                    feed_library.
    """
    check_input_type(feed_library, pd.DataFrame, "feed_library")
    check_input_type(user_diet, pd.DataFrame, "user_diet")

    expected_columns = expected.FeedLibrarySchema.keys()

    check_keys_presence(feed_library.columns, expected_columns)
    missing_feeds = set(user_diet["Feedstuff"]) - set(feed_library["Fd_Name"])
    if missing_feeds:
        raise ValueError(
            f"The following feeds are missing in the feed library: {missing_feeds}"
            )
    return feed_library


def validate_coeff_dict(coeff_dict: dict) -> dict:
    """
    Validates and corrects the coefficient dictionary.

    This function checks that the coefficient dictionary contains the correct 
    keys and values according to the expected schema. It also compares the 
    dictionary against a default set of coefficients to identify any differences.

    Args:
        coeff_dict: A dictionary containing coefficient data.

    Returns:
        A corrected dictionary with validated and possibly converted values.

    Raises:
        TypeError: If coeff_dict is not a dictionary or if any value cannot be 
                   converted to the expected type.
        KeyError: If required keys are missing from the coeff_dict.
    """
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
    """
    Validates the structure and content of the infusion input dictionary.

    This function ensures that the infusion input dictionary contains the correct 
    keys and values according to the expected schema. It checks for the presence 
    of required keys, validates types, and attempts to convert values to the 
    correct type if necessary.

    Args:
        infusion_input: A dictionary containing infusion input data.

    Returns:
        A corrected dictionary with validated and possibly converted values.

    Raises:
        TypeError: If infusion_input is not a dictionary or if any value cannot be 
                   converted to the expected type.
        KeyError: If required keys are missing from the infusion_input.
    """
    expected_infusion_dict = expected.InfusionDict.__annotations__.copy()

    check_input_type(infusion_input, dict, "infusion_input")
    check_keys_presence(infusion_input, expected_infusion_dict.keys())
    corrected_input = check_and_convert_type(
        infusion_input,
        expected_infusion_dict
    )    
    return corrected_input


def validate_MP_NP_efficiency_input(MP_NP_efficiency_input: dict) -> dict:
    """
    Validates the MP/NP efficiency input dictionary.

    This function ensures that the MP/NP efficiency input dictionary contains 
    the correct keys and values according to the expected schema. It checks for 
    the presence of required keys, validates types, and attempts to convert 
    values to the correct type if necessary.

    Args:
        MP_NP_efficiency_input: A dictionary containing MP/NP efficiency data.

    Returns:
        A corrected dictionary with validated and possibly converted values.

    Raises:
        TypeError: If MP_NP_efficiency_input is not a dictionary or if any value 
                   cannot be converted to the expected type.
        KeyError: If required keys are missing from the MP_NP_efficiency_input.
    """
    expected_MP_NP_efficiency = expected.MPNPEfficiencyDict.__annotations__.copy()
    check_input_type(MP_NP_efficiency_input, dict, "MP_NP_efficiency_input")
    check_keys_presence(
        MP_NP_efficiency_input.keys(), expected_MP_NP_efficiency.keys()
        )
    corrected_values = check_and_convert_type(
        MP_NP_efficiency_input, expected_MP_NP_efficiency
        )
    return corrected_values


def validate_mPrt_coeff_list(
    mPrt_coeff_list: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    Validates a list of mPrt coefficient dictionaries.

    This function ensures that each dictionary in the list contains the correct 
    keys and values according to the expected schema. It checks for the presence 
    of required keys, validates types, and raises an error if any value is not 
    of the expected type.

    Args:
        mPrt_coeff_list: A list of dictionaries containing microbial protein 
                         coefficient data.

    Returns:
        The validated list of dictionaries.

    Raises:
        TypeError: If mPrt_coeff_list is not a list, if any dictionary in the 
                   list is not a dictionary, or if any value is not of the 
                   expected type.
        KeyError: If required keys are missing from any dictionary in the list.
    """
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
    """
    Validates the structure and content of the f_Imb pandas Series.

    This function ensures that the f_Imb pandas Series contains the correct 
    indices and that all values are of the correct type (int or float). 

    Args:
        f_Imb: A pandas Series representing imbalance factors for amino acids.

    Returns:
        The validated pandas Series.

    Raises:
        TypeError: If f_Imb is not a pandas Series or if any value is not of 
                   the expected type.
        KeyError: If required indices are missing from the f_Imb Series.
    """
    expected_f_Imb = expected.f_Imb
    check_input_type(f_Imb, pd.Series, "f_Imb")
    check_keys_presence(f_Imb.index, expected_f_Imb.index)
    if not f_Imb.apply(lambda x: isinstance(x, (int, float))).all():
        raise TypeError("All values in f_Imb must be int or float")
    return f_Imb
    