import importlib_resources
import pandas as pd
import nasem_dairy as nd
path_to_package_data = importlib_resources.files("nasem_dairy.data")

# Read_csv to load required data into env
user_diet_in, animal_input_in, equation_selection_in = nd.read_csv_input(path_to_package_data.joinpath("./input.csv"))

# Load feed library
feed_library_in = pd.read_csv(path_to_package_data.joinpath("NASEM_feed_library.csv"))

# Prepare infusion data (This will be optional as a default dict of 0 is provided to function otherwise)
infusion_custom = nd.read_infusion_input(path_to_package_data.joinpath("infusion_input.csv"))


nd.execute_model(
    user_diet = user_diet_in, 
    animal_input = animal_input_in, 
    equation_selection = equation_selection_in, 
    feed_library_df = feed_library_in, 
    coeff_dict = nd.coeff_dict)

# @profile needs to be added to function defs in source code
# run profiling by running this in terminal: kernprof -l -v ./dev_scripts/dev_files/min_run_example.py   