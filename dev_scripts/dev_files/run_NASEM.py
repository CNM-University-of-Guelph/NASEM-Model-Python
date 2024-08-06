import nasem_dairy as nd
import pandas as pd

import importlib.resources
import os

if __name__ == "__main__":
    path_to_package_data = importlib.resources.files("nasem_dairy.data")
    user_diet_in, animal_input_in, equation_selection_in, infusion_input = nd.demo("input")

    feed_library_in = pd.read_csv(
        path_to_package_data.joinpath("feed_library/NASEM_feed_library.csv")
        )

    output = nd.nasem(
        user_diet = user_diet_in, 
        animal_input = animal_input_in, 
        equation_selection = equation_selection_in, 
        feed_library_df = feed_library_in, 
        coeff_dict = nd.coeff_dict
        )
    

    # print(output.get_value("An_VitA_bal"))
    # print(output.search("Abs_AA_g"))

    # print(output.get_report("table8_2"))

    print("Model has finsihed running! \n")

