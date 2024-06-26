import nasem_dairy as nd
import pandas as pd

import importlib.resources
import os

if __name__ == "__main__":
    path_to_package_data = importlib.resources.files("nasem_dairy.data")
    user_diet_in, animal_input_in, equation_selection_in = nd.read_csv_input(
        path_to_package_data.joinpath("input.csv")
        )
    feed_library_in = pd.read_csv(
        path_to_package_data.joinpath("NASEM_feed_library.csv")
        )

    output = nd.execute_model(
        user_diet = user_diet_in, 
        animal_input = animal_input_in, 
        equation_selection = equation_selection_in, 
        feed_library_df = feed_library_in, 
        coeff_dict = nd.coeff_dict
        )
    
    print("Model has finsihed running! \n")
    print(output.search("Zn"))
