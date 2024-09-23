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
    
    report = output.get_report("table7_1")
    # print(report.applymap(type))
    for column in report.columns:
        print(report[column].apply(type))
        print(report[column])


    print("\nModel has finished running!\n")
  