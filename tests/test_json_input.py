# Read in .csv files with inputs and expected outputs for functions
# tets_from_csv() iterates through the .csv file to perform unit tests
import pytest
import nasem_dairy as nd
import pandas as pd

@pytest.fixture
def nutrient_intakes_data():
    return pd.read_json("./tests/nutrient_intakes_test.json")

def test_from_json(nutrient_intakes_data):
    """
    df(Dataframe): Expecting 3 columns; Name(name of function to test),
                    Input(Dictionary with all input values),
                    Output(Expected function output for given inputs)
    
    Since tests are executed by calling pytest at the terminal function calls are not required.
    Pytest will detect this function and execute it as it follows the naming convention (test_)
    The data for running the tests is stored in .JSON files, and are sourced by decorating functions 
    as fixtures (@pytest.fixture) and returning dataframe
    """
    for index, row in nutrient_intakes_data.iterrows():
        try:
            func = getattr(nd, row.Name)
            assert func(**row.Input) == pytest.approx(row.Output), f"{func(**row.Input)} does not equal {row.Output}"
        except AttributeError:
            print(f"Function {row.Name} not found in module.")

