"""
This script takes variables.txt, which contains the names of all variables in the NSAEM python model and 
compares it with a sbset of the R code in R_code.txt. Any matching variables are commented out to indicate
what still needs to be added. 
"""
def check_variables(input_variables):
    # Read the contents of variables.txt and store variable names in a set
    with open('variables.txt', 'r') as file:
        variable_names = {line.strip() for line in file}

    # Check if input variables are in the set of variable names
    for variable in input_variables:
        if variable in variable_names:
            # print(f"{variable} is present in variables.txt")
            pass
        else:
            print(f"{variable} is not present in variables.txt")

if __name__ == "__main__":
    # Get input variables from the user
    input_variables_str = input("Enter a list of variable names (comma-separated): ")
    
    # Split the input string into a list of variables
    input_variables = [var.strip() for var in input_variables_str.split(',')]

    # Call the function to check if input variables are in variables.txt
    check_variables(input_variables)
    