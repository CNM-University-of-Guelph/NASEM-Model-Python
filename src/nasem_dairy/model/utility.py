# This file contains all of the functions used to execute the NASEM model in python
# import nasem_dairy.ration_balancer.ration_balancer_functions as ration_funcs
import importlib
import json
from typing import Dict, Tuple, Union

import pandas as pd


def get_feed_data(Trg_Dt_DMIn: float,
                  user_diet: pd.DataFrame,
                  feed_library: pd.DataFrame
) -> pd.DataFrame:
    """
    Filter the NASEM feed library DataFrame based on user entered diet. 

    Parameters
    ----------
    Trg_Dt_DMIn : float
        Target dry matter intake (kg) for the diet.
    user_diet : pd.DataFrame
        DataFrame containing the user's diet with feed names and their 
        respective amounts.
    feed_library : pd.DataFrame
        DataFrame containing the NASEM feed library.

    Returns
    -------
    pd.DataFrame
        DataFrame containing the subset of the NASEM feed library based on the 
        user's diet, with additional calculated columns for dry matter intake.

    Notes
    -----
    - The resulting DataFrame includes feed names after stripping leading and 
      trailing whitespaces.
    - Additional columns 'Fd_DMInp' and 'Fd_DMIn' are added based on user input 
      and target dry matter intake.

    Examples
    --------
    Calculate the feed data based on user diet and target dry matter intake:
    
    ```{python}
    import pandas as pd
    
    user_diet_df = pd.DataFrame({
        'Feedstuff': ['Corn silage, typical', 'Canola meal'],
        'kg_user': [10, 5]
    })
        
    Trg_Dt_DMIn = 15.0
    
    selected_feeds_df = get_feed_data(Trg_Dt_DMIn, user_diet_df, feed_library_df)

    selected_feeds_df.info()
    ```
    """
    feeds = user_diet["Feedstuff"].tolist()
    # Select required rows from feed library
    selected_feeds = (
        feed_library.assign(Fd_Name=lambda df: df["Fd_Name"].str.strip())
        .loc[lambda df: df["Fd_Name"].isin(feeds)]
        .rename(columns={"Fd_Name": "Feedstuff"})
        .pipe(lambda df: df[
            ["Feedstuff"] + [col for col in df.columns if col != "Feedstuff"]
            ])
        )
    feed_data = (user_diet.assign(
        Fd_DMInp=lambda df: df["kg_user"] / df["kg_user"].sum(),
        Fd_DMIn=lambda df: df["Fd_DMInp"] * Trg_Dt_DMIn,
        )
        .merge(selected_feeds, how="left", on="Feedstuff")
    )
    return feed_data


def read_csv_input(path_to_file: str = "input.csv"
) -> Tuple[pd.DataFrame, Dict[str, float], Dict[str, Union[str, float]]]:
    """
    Read input data from a CSV file and organize it into dictionaries and a DataFrame.
    This is a convenience function for preparing the required inputs for the run_NASEM() function from a csv file that follows a particular structure, described below.

    Parameters
    ----------
    path_to_file : str
        The path to the CSV file containing input data.

    Returns
    -------
    tuple
        A tuple containing a DataFrame (user_diet), and dictionaries (animal_input, equation_selection).
   
    Notes
    -----
    The CSV file is expected to have four columns (same as input.csv): Location, Variable, Value, Expected Value

    - **Location** must be: infusions
    - **Variable**: str that starts with 'Inf_'
    - **Value**: number that represents either g or %/h, depending on Variable
    - **Expected Value**: details of units and description of Variable 

    Examples
    --------
    Read input data from a CSV file:

    ```{python}
    # Define file path to input_data.csv
    import importlib_resources
    path_to_csv = importlib_resources.files('nasem_dairy.data').joinpath('input.csv') 

    import nasem_dairy as nd
    user_diet_in, animal_input_in, equation_selection_in = nd.read_csv_input(path_to_csv) 
    ```

    ```{python}
    print(user_diet_in)
    ```

    ```{python}
    print(animal_input_in)
    ```

    ```{python}
    print(equation_selection_in)
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
                float(value) if value.replace('.', '', 1).isdigit() else value
                )

        elif location == 'animal_input':
            animal_input[variable] = (
                float(value) if value.replace('.', '', 1).isdigit() else value
                )
            
        elif location == 'diet_info':
            user_diet_data['Feedstuff'].append(variable)
            user_diet_data['kg_user'].append(value)

        elif location == "infusion_input":
            infusion_input[variable] = (
                float(value) if value.replace('.', '', 1).isdigit() else value
                )
            
    user_diet = pd.DataFrame(user_diet_data)
    user_diet['kg_user'] = pd.to_numeric(user_diet['kg_user'])

    return user_diet, animal_input, equation_selection, infusion_input


def read_json_input(file_path: str) -> Tuple[pd.DataFrame, Dict, Dict, Dict]:
    with open(file_path, "r") as f:
        data = json.load(f)
    
    diet_info = data["diet_info"]
    user_diet = pd.DataFrame({
        "Feedstuff": diet_info["Feedstuff"],
        "kg_user": diet_info["kg_user"]
    })

    equation_selection = data["equation_selection"]
    animal_input = data["animal_input"]
    infusion_input = data["infusion_input"]
    
    return user_diet, animal_input, equation_selection, infusion_input


def demo(scenario_name: str) -> Tuple[pd.DataFrame, Dict, Dict, Dict]:
    """
    Takes the name of a file in nasem_dairy/data/demo and returns the input data.
    
    Parameters:
    scenario_name (str): The name of the scenario file (without extension) located in the nasem_dairy/data/demo directory.
    
    Returns:
    Tuple[pd.DataFrame, Dict, Dict, Dict, pd.DataFrame]: A tuple containing:
        - diet_info_df (pd.DataFrame): A DataFrame with Feedstuff and kg_user columns.
        - equation_selection (Dict): A dictionary of equation selection inputs.
        - animal_input (Dict): A dictionary of animal input data.
        - infusion_input (Dict): A dictionary of infusion input data.
    
    Example:
    --------
    import nasem_dairy as nd
    
    user_diet_in, animal_input_in, equation_selection_in, infusion_input, feed_library_in = nd.demo("dry_cow")
    """
    path_to_package_data = importlib.resources.files(
        "nasem_dairy.data.demo"
        )
    return read_json_input(path_to_package_data.joinpath(f"{scenario_name}.json"))
