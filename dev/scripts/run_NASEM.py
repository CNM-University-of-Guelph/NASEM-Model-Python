import nasem_dairy as nd
import pandas as pd

import importlib.resources
import os
import inspect


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

    # Create subset of feed library
    feed_names = [
        "Alfalfa meal",
        "Canola meal",
        "Corn silage, typical",
        "Corn grain HM, coarse grind"
    ]
    filtered_feeds = feed_library_in[feed_library_in["Fd_Name"].isin(feed_names)].reset_index()


    # Testing variables
    # variable = "Rsrv_Gain_empty"   
    # variable = "Du_MiCP"
    variable = "GrUter_Wt"          
    # variable = "Fd_ForNDF"
    # variable = "Fd_ADFIn"
    expected_output = output.get_value(variable)  
    

    dag = nd.nasem_dag()
    order = dag.get_calculation_order(variable)
    # print(order)


    generated_function = dag.create_function(variable)
    print("\nGenerated Function Signature")
    print(inspect.signature(generated_function))
    print(generated_function.__name__,"\n")
    print(generated_function.__doc__,"\n")


    print("\nModel has finished running!")
    dynamic_func_output = generated_function(
        animal_input_in, filtered_feeds, equation_selection_in
        )
    # print(expected_output)
    # print(dynamic_func_output)
    assert expected_output == dynamic_func_output, "Values should be equal"
    # assert expected_output.equals(dynamic_func_output), "Values should be equal"
