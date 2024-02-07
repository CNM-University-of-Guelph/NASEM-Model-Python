# This file contains all of the functions used to execute the NASEM model in python
import pandas as pd


def check_coeffs_in_coeff_dict(
        input_coeff_dict: dict, 
        required_coeffs: list):
    '''
    Internal function that is used by other functions that require certain model coefficients from a coefficient dictionary. Typically this 
    will be the built-in dictionary in [default_values_dictionaries.py]. 
    This function will check if the required coeffs are in the dictionary provided to the function, and if not it will return a useful error.

    Parameters
    ----------
    input_coeff_dict : dict
        Coefficient dictionary, normally called as `coeff_dict` by functions
    required_coeffs : list
        A list of strings that contain the names of the required coefficients to check for in the dictionary.

    Returns
    -------
    None

    Examples
    --------
    Filter the NASEM feed library for specific feeds:
    
    ```{python}
    import nasem_dairy as nd

    req_coeffs = ['En_CP', 'En_FA', 'En_rOM', 'En_St', 'En_NDF']

    nd.check_coeffs_in_coeff_dict(
        input_coeff_dict = nd.coeff_dict, 
        required_coeffs = req_coeffs)

    ```

    '''
    # Convert the list to a set for faster lookup
    req_coef = set(required_coeffs)
    dict_in = set(input_coeff_dict)

    # Return coeffs that are not in dict_in
    missing_coeffs = [value for value in req_coef if value not in dict_in]

    # Check if all values are present in the dictionary
    result = not bool(missing_coeffs)

    # Raise an AssertionError with a custom message containing missing values if the condition is False
    assert result, f"Missing values in coeff_dict: {missing_coeffs}"

    return




def get_feed_rows_feedlibrary(
        feeds_to_get: list,
        feed_lib_df: pd.DataFrame) -> pd.DataFrame:
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

    # Filter df using list from user
    selected_feed_data = feed_lib_df[feed_lib_df["Fd_Name"].isin(feeds_to_get)]

    # set names as index for downstream
    selected_feed_data = selected_feed_data.set_index('Fd_Name')

    # Clean names:
    selected_feed_data.index = selected_feed_data.index.str.strip()

    return selected_feed_data


def read_csv_input(path_to_file = "input.csv"):
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

    input_data = pd.read_csv(path_to_file) 

    for index, row in input_data.iterrows():
        location = row['Location']
        variable = row['Variable']
        value = row['Value']

        if location == 'equation_selection':
            equation_selection[variable] = float(value) if value.replace('.', '', 1).isdigit() else value
            
        elif location == 'animal_input':
            animal_input[variable] = float(value) if value.replace('.', '', 1).isdigit() else value

        elif location == 'diet_info':
            user_diet_data['Feedstuff'].append(variable)
            user_diet_data['kg_user'].append(value)

    user_diet = pd.DataFrame(user_diet_data)
    user_diet['kg_user'] = pd.to_numeric(user_diet['kg_user'], downcast="float")

    return user_diet, animal_input, equation_selection


def read_infusion_input(path_to_file = 'infusion_input.csv'):
    """
    Read infusion input data from a CSV file and return it as a dictionary. 

    Parameters
    ----------
    path_to_file : str
        The path to the CSV file containing infusion input data.

    Returns
    -------
    dict
        A dictionary containing variable-value pairs parsed from the CSV file.

    Notes
    -----
    The CSV file is expected to have four columns (same as input.csv): Location, Variable, Value, Expected Value

    - **Location** must be: infusions
    - **Variable**: str that starts with 'Inf_'
    - **Value**: number that represents either g or %/h, depending on Variable
    - **Expected Value**: details of units and description of Variable
    
    Examples
    --------
    Read infusion input data from a CSV file:

    ```{python}
    # Define file path to infusion_input.csv
    import importlib_resources
    path_to_inf = importlib_resources.files('nasem_dairy.data').joinpath('infusion_input.csv') 
    ```

    
    ```{python}
    import nasem_dairy as nd
    infusion_data = nd.read_infusion_input(path_to_inf)
    print(infusion_data)
    ```
    """
    
    infusions = {}
    input_data = pd.read_csv(path_to_file)
    input_data['Value'] = pd.to_numeric(input_data['Value'], errors='coerce')
    # Read in user data
    for index, row in input_data.iterrows():
        # Iterate over CSV, convert to a dictionary
        variable = row['Variable']
        value = row['Value']
        # Convert values to float if possible, otherwise leave as a string 
        try:
            value = float(value)
        except ValueError:
            pass

        infusions[variable] = value
    return infusions
