"""
This script takes variables.txt, which contains the names of all variables in the NSAEM python model and 
compares it with a sbset of the R code in R_code.txt. Any matching variables are commented out to indicate
what still needs to be added. 
"""
# Read the variables from variables.txt
with open('variables.txt', 'r') as variables_file:
    variables_list = [line.strip() for line in variables_file]

# Process the R code and comment out lines starting with variables
with open('R_code.txt', 'r') as r_code_file:
    lines = r_code_file.readlines()

# Open the R code file in write mode to overwrite it
with open('R_code.txt', 'w') as r_code_file:
    for line in lines:
        # Check if any variable from the list starts the line
        if any(line.strip().startswith(variable) for variable in variables_list):
            # If yes, insert '#' to comment out the line
            line = '#' + line

        # Write the processed line to the file
        r_code_file.write(line)

print("Done Processing")
