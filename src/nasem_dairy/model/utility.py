"""Utility functions for using the NASEM model in Python.

This module provides various utility functions that support the execution of 
the NASEM Nutrient Requirements of Dairy Cattle model. These functions handle 
tasks such as reading input data from CSV and JSON files, filtering feed data, 
and providing demo scenarios.

Functions:
    get_feed_data: Filters the NASEM feed library DataFrame based on 
                   user-entered diet.
    read_csv_input: Reads input data from a CSV file and organizes it into a 
                    DataFrame and dictionaries.
    read_json_input: Reads input data from a JSON file and returns it as a 
                     DataFrame and dictionaries.
    demo: Provides input data for a given scenario from the demo directory.
    select_feeds: Selects specific feeds from the NASEM feed library based on 
                  a list of feed names.
"""
import importlib
import json
from typing import Dict, Tuple, Union, Optional, List

import pandas as pd

import nasem_dairy.nasem_equations.nutrient_intakes as diet
from nasem_dairy.model.nasem import nasem

def get_feed_data(
    Trg_Dt_DMIn: float,
    user_diet: pd.DataFrame,
    feed_library: pd.DataFrame
) -> pd.DataFrame:
    """
    Filters the NASEM feed library DataFrame based on the user-entered diet.

    Args:
        Trg_Dt_DMIn (float): Target dry matter intake (kg) for the diet.
        user_diet (pd.DataFrame): DataFrame containing the user's diet with 
            feed names and their respective amounts.
        feed_library (pd.DataFrame): DataFrame containing the NASEM feed library.

    Returns:
        pd.DataFrame: DataFrame containing the subset of the NASEM feed library 
        based on the user's diet, with additional calculated columns for dry 
        matter intake.

    Notes:
        - The resulting DataFrame includes feed names after stripping leading 
          and trailing whitespaces.
        - Additional columns 'Fd_DMInp' and 'Fd_DMIn' are added based on user 
          input and target dry matter intake.

    Example:
        ```python
        import pandas as pd
        
        user_diet_df = pd.DataFrame({
            'Feedstuff': ['Corn silage, typical', 'Canola meal'],
            'kg_user': [10, 5]
        })
            
        Trg_Dt_DMIn = 15.0
        
        selected_feeds_df = get_feed_data(Trg_Dt_DMIn, user_diet_df, feed_library)

        selected_feeds_df.info()
        ```
    """
    feeds = user_diet["Feedstuff"].tolist()
    selected_feeds = (
        feed_library.assign(Fd_Name=lambda df: df["Fd_Name"].str.strip())
        .loc[lambda df: df["Fd_Name"].isin(feeds)]
        .rename(columns={"Fd_Name": "Feedstuff"})
        .pipe(lambda df: df[
            ["Feedstuff"] + [col for col in df.columns if col != "Feedstuff"]
            ])
        )
    user_diet["Fd_DMInp"] = diet.calculate_Fd_DMInp(user_diet["kg_user"])
    user_diet["Trg_Fd_DMIn"] = diet.calculate_Trg_Fd_DMIn(
        user_diet["Fd_DMInp"], Trg_Dt_DMIn
        )
    feed_data = user_diet.merge(selected_feeds, how="left", on="Feedstuff")
    return feed_data


def read_csv_input(
    path_to_file: str = "input.csv"
) -> Tuple[pd.DataFrame, Dict[str, float], Dict[str, Union[str, float]]]:
    """
    Reads input data from a CSV file and organizes it into dictionaries and a DataFrame.

    This is a convenience function for preparing the required inputs for the 
    run_NASEM() function from a CSV file that follows a specific structure.

    Args:
        path_to_file: The path to the CSV file containing input data.

    Returns:
        tuple: A tuple containing:
            - A DataFrame (`user_diet`) with the user's diet information.
            - A dictionary (`animal_input`) with animal input data.
            - A dictionary (`equation_selection`) with selected equations.

    Example:
        Read input data from a CSV file:
        
        ```python
        import importlib_resources
        path_to_csv = importlib_resources.files('nasem_dairy.data').joinpath('lactating_cow_test.csv') 
        
        import nasem_dairy as nd
        user_diet_in, animal_input_in, equation_selection_in, infusion_input = nd.read_csv_input(path_to_csv)
        
        print(user_diet_in)
        print(animal_input_in)
        print(equation_selection_in)
        print(infusion_input)
        ```
    """
    animal_input = {}
    equation_selection = {}
    user_diet_data = {'Feedstuff': [], 'kg_user': []}
    infusion_input = {}

    input_data = pd.read_csv(path_to_file)

    for index, row in input_data.iterrows():
        location = row['Location']
        variable = row['Variable']
        value = row['Value']

        if location == 'equation_selection':
            equation_selection[variable] = (
                float(value) 
                if isinstance(value, str) and value.replace('.', '', 1).isdigit() 
                else value
                )

        elif location == 'animal_input':
            animal_input[variable] = (
                float(value) 
                if isinstance(value, str) and value.replace('.', '', 1).isdigit() 
                else value
                )
            
        elif location == 'user_diet':
            user_diet_data['Feedstuff'].append(variable)
            user_diet_data['kg_user'].append(value)

        elif location == "infusion_input":
            infusion_input[variable] = (
                float(value) 
                if isinstance(value, str) and value.replace('.', '', 1).isdigit() 
                else value
                )
            
    user_diet = pd.DataFrame(user_diet_data)
    user_diet['kg_user'] = pd.to_numeric(user_diet['kg_user'])

    return user_diet, animal_input, equation_selection, infusion_input


def read_json_input(file_path: str) -> Tuple[pd.DataFrame, Dict, Dict, Dict]:
    """
    Reads input data from a JSON file and organizes it into a DataFrame and dictionaries.

    This function reads a JSON file containing input data for the NASEM model 
    and converts it into a pandas DataFrame for the user's diet and dictionaries 
    for equation selection, animal input, and infusion input.

    Args:
        file_path: The path to the JSON file containing the input data.

    Returns:
        tuple: A tuple containing:
            - user_diet_df (pd.DataFrame): A DataFrame with Feedstuff and kg_user columns.
            - animal_input (Dict): A dictionary with animal input data.
            - equation_selection (Dict): A dictionary with equation selection inputs.
            - infusion_input (Dict): A dictionary with infusion input data.

    Example:
        Read input data from a JSON file:
        
        ```python
        user_diet_df, animal_input, equation_selection, infusion_input = read_json_input("input_data.json")
        
        print(user_diet_df)
        print(animal_input)
        print(equation_selection)
        print(infusion_input)
        ```
    """
    with open(file_path, "r") as f:
        data = json.load(f)
    
    user_diet = data["user_diet"]
    user_diet_df = pd.DataFrame({
        "Feedstuff": user_diet["Feedstuff"],
        "kg_user": user_diet["kg_user"]
    })

    equation_selection = data["equation_selection"]
    animal_input = data["animal_input"]
    infusion_input = data["infusion_input"]
    
    return user_diet_df, animal_input, equation_selection, infusion_input


def demo(scenario_name: str) -> Tuple[pd.DataFrame, Dict, Dict, Dict]:
    """
    Loads input data for a given scenario from the demo directory.

    This function takes the name of a scenario file located in the 
    `nasem_dairy/data/demo` directory and returns the corresponding input data 
    required to run the NASEM model.

    Args:
        scenario_name: The name of the scenario file (without the `.json` extension) 
                       located in the `nasem_dairy/data/demo` directory.

    Returns:
        tuple: A tuple containing:
            - user_diet_df (pd.DataFrame): A DataFrame with Feedstuff and kg_user columns.
            - equation_selection (Dict): A dictionary with equation selection inputs.
            - animal_input (Dict): A dictionary with animal input data.
            - infusion_input (Dict): A dictionary with infusion input data.

    Example:
        Load input data for the "dry_cow" scenario:
        
        ```python
        import nasem_dairy as nd
        
        user_diet_df, animal_input, equation_selection, infusion_input = nd.demo("dry_cow")
        
        print(user_diet_df)
        print(animal_input)
        print(equation_selection)
        print(infusion_input)
        ```
    """
    path_to_package_data = importlib.resources.files(
        "nasem_dairy.data.demo"
        )
    return read_json_input(
        path_to_package_data.joinpath(f"{scenario_name}.json")
        )


def select_feeds(names: list) -> pd.DataFrame:
    """
    Selects specific feeds from the NASEM feed library based on a list of feed names.

    This function filters the NASEM feed library to include only the feeds specified 
    in the provided list of names. It ensures that the rows in the resulting DataFrame 
    are in the same order as the names in the input list.

    Args:
        names: A list of feed names to select from the NASEM feed library.

    Returns:
        pd.DataFrame: A DataFrame containing only the selected feeds, with rows 
                      ordered according to the input list.

    Example:
        Select specific feeds from the feed library:
        
        ```python
        selected_feeds = select_feeds(["Corn silage, typical", "Canola meal"])
        
        print(selected_feeds)
        ```
    """
    path_to_package_data = importlib.resources.files(
        "nasem_dairy.data.feed_library"
        )
    feed_library = pd.read_csv(
        path_to_package_data.joinpath("NASEM_feed_library.csv")
        )
    selected_feeds = feed_library[feed_library["Fd_Name"]
                                  .isin(names)].reset_index()
    # Ensure the rows are in the same order as names list
    selected_feeds["Fd_Name"] = pd.Categorical(
        selected_feeds["Fd_Name"], categories=names, ordered=True
        )
    selected_feeds = selected_feeds.sort_values("Fd_Name").reset_index(drop=True)
    return selected_feeds


def adjust_nutrient(
        feed_column: str,
        feed_library: pd.DataFrame,
        expected_value: float,
        observed_value: float,
    ) -> Tuple[pd.Series, float]:
    """Adjust a feed column so that the output value matches the expected value.

    Implements the method described in Li et al., 2018 (doi: https://doi.org/10.3168/jds.2017-14182)
    
    Args:
    ----
    feed_column: str
        The name of the feed column to adjust.
    feed_library: pd.DataFrame
        The diet to adjust, with proportions of feeds in kg DM.
    expected_value: float
        The expected % DM of the nutrient in the diet.
    observed_value: float
        The observed % DM of the nutrient in the diet.

    Returns:
    -------
    Tuple[pd.Series, float]
        The adjusted feed column and the adjustment factor.
    """    
    bias = observed_value - expected_value
    adjustment = bias / observed_value
    adjusted_nutrient = feed_library[feed_column] * (1 - adjustment) 
    return (adjusted_nutrient, adjustment)


def adjust_diet(
        animal_input: dict,
        equation_selection: dict,
        diet: pd.DataFrame,
        expected_nutrients: dict,
        nutrients_to_adjust: List[Tuple[str, str]],
        feed_library: Optional[pd.DataFrame] = None
    ) -> pd.DataFrame:
    """
    Adjust the diet to match the expected nutrient values.

    Args:
    ----
    animal_input: dict
        The animal input data.
    equation_selection: dict
        The equation selection data.
    diet: pd.DataFrame
        The diet to adjust.
    expected_nutrients: dict
        The expected nutrient values.
    nutrients_to_adjust: List[Tuple[str, str]]
        The nutrients to adjust.
    feed_library: Optional[pd.DataFrame]
        The feed library to use.

    Returns:
    -------
    Tuple[pd.DataFrame, dict]
        The adjusted feed library and the adjustment factors.
    """
    if feed_library is None:
        feed_library = select_feeds(list(diet["Feedstuff"]))

    adjusted_feed_library = feed_library.copy(deep=True)
    adjustment_dict = {}

    for feed_column, output_name in nutrients_to_adjust:
        output = nasem(diet, animal_input, equation_selection, feed_library)
        adjusted_nutrient, adjustment = adjust_nutrient(
            feed_column, feed_library, expected_nutrients[output_name], 
            output.get_value(output_name)
        )
        adjusted_feed_library[feed_column] = adjusted_nutrient
        adjustment_dict[feed_column] = adjustment

    return adjusted_feed_library, adjustment_dict
