# This file contains all of the functions used to execute the NASEM model in python
# import nasem_dairy.ration_balancer.ration_balancer_functions as ration_funcs
from typing import Dict, Tuple, Union

import pandas as pd


def get_feed_rows_feedlibrary(feeds_to_get: list,
                              feed_lib_df: pd.DataFrame
) -> pd.DataFrame:
    '''
    Filter the NASEM feed library DataFrame based on a list of feed names. 

    Parameters
    ----------
    feeds_to_get : list
        List of feed names to filter the feed library.
    feed_lib_df : pd.DataFrame
        DataFrame containing the NASEM feed library.

    Returns
    -------
    pd.DataFrame
        DataFrame containing subset of NASEM feed library based on a list of feed names.

    Notes
    -----
    - The resulting DataFrame is indexed by feed names after stripping leading and trailing whitespaces.

    Examples
    --------
    Filter the NASEM feed library for specific feeds:
    
    ```{python}
    # Import default feed library
    import importlib_resources
    import pandas as pd
    feed_library_df = pd.read_csv(importlib_resources.files('nasem_dairy.data').joinpath("NASEM_feed_library.csv")) 
    ```

    ```{python}
    import nasem_dairy as nd
    selected_feeds_df = nd.get_feed_rows_feedlibrary(
        feeds_to_get=['Corn silage, typical', 'Canola meal'],
        feed_lib_df=feed_library_df)

    selected_feeds_df.info()
    ```
    '''

    # # Filter df using list from user
    # selected_feed_data = feed_lib_df[feed_lib_df["Fd_Name"].isin(feeds_to_get)]

    # # set names as index for downstream
    # selected_feed_data = selected_feed_data.set_index('Fd_Name')

    # # Clean names:
    # selected_feed_data.index = selected_feed_data.index.str.strip()

    selected_feed_data = (
        feed_lib_df.assign(
            Fd_Name=lambda df: df["Fd_Name"].str.strip())  # clean whitespace
        # filter Fd_Name to match feeds_to_get
        .loc[lambda df: df["Fd_Name"].isin(feeds_to_get)]  
        .rename(columns={'Fd_Name': 'Feedstuff'})
        .pipe(lambda df: df[['Feedstuff'] +
                            [col for col in df.columns if col != 'Feedstuff']])
    )  #reorder columns
    return selected_feed_data


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
