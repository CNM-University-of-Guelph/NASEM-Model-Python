import nasem_dairy as nd
import pandas as pd

import inspect

def call_with_dict_args(func, args_dict):
    """
    Calls the given function with arguments automatically extracted from args_dict.

    Parameters:
    - func: The function to be called.
    - args_dict: A dictionary mapping argument names to their values.

    Returns:
    - The result of calling func with the provided arguments.
    """
    func_signature = inspect.signature(func)
    func_args = func_signature.parameters.keys()
    func_call_args = {arg: args_dict[arg] for arg in func_args if arg in args_dict}
    return func(**func_call_args)


if __name__ == "__main__":
    user_diet_in, animal_input_in, equation_selection_in, infusion_input = nd.demo("lactating_cow_test")
    
    output = nd.nasem(
        user_diet = user_diet_in, 
        animal_input = animal_input_in, 
        equation_selection = equation_selection_in, 
        coeff_dict = nd.coeff_dict
        )
    
    print (nd.coeff_dict['Kr_ME_RE_Gain'])
    print (nd.coeff_dict['Kr_ME_RE_Loss'])

    # Create subset of feed library
    feed_names = [
        "Alfalfa meal",
        "Canola meal",
        "Corn silage, typical",
        "Corn grain HM, coarse grind"
    ]
    filtered_feeds = nd.select_feeds(feed_names)

    # Testing variables
    # variable = "Rsrv_Gain_empty"   
    variable = "Du_MiCP"
    # variable = "GrUter_Wt"          
    # variable = "Fd_ForNDF"
    # variable = "Fd_ADFIn"
    # variable = "Fd_C160In"
    # variable = "Dt_AARUPIn"

    expected_output = output.get_value(variable)  
    

    # order = dag.get_calculation_order(variable)
    # # print(order)


    # generated_function = dag.create_function(variable)
    # print("\nGenerated Function Signature")
    # print(inspect.signature(generated_function))


    print("\nModel has finished running!\n")
    # args_dict = {
    #     "animal_input": animal_input_in, 
    #     "coeff_dict": nd.coeff_dict, 
    #     "equation_selection": equation_selection_in, 
    #     "feed_library": filtered_feeds, 
    #     "user_diet": user_diet_in,
    #     "infusion_input": infusion_input
    #     }
    # dynamic_func_output = call_with_dict_args(generated_function, args_dict)

    print(f"Expected Output: {output.get_value(variable)}")
    # print(f"Actual Output: {dynamic_func_output.get_value(variable)}")

    # # print(f"Expected output: \n{expected_output}\n")
    # # print(dynamic_func_output)

    # assert output.get_value(variable) == dynamic_func_output.get_value(variable), "Values should be equal"
    # assert expected_output.equals(dynamic_func_output), "Values should be equal"


   # if nd.ModelDAG is None:
       # raise ImportError(
        #    "ModelDAG requires the 'graph-tool' package. Please install it with `poetry run bash setup-dag.sh`."
        #)
    # dag = nd.ModelDAG()
    
    