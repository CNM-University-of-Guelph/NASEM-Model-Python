####################
# Packages used by modules
####################
# import pandas as pd
# import sqlite3
# import math
# import numpy as np
# import sys
# import os

####################
# Import Functions
####################


'''
This uses the poetry package to build the nasem_dairy package.
To use it during dev, run:
poetry install

This installs the package locally. See notes:
poetry install actually installs packages in “editable mode”, which means that it installs a link to your package’s code on your computer (rather than installing it as a independent piece of software). Editable installs are commonly used by developers because it means that any edits made to the package’s source code are immediately available the next time it is imported, without having to poetry install again. We’ll talk more about installing packages in Section 3.10.
More details: 
https://py-pkgs.org/ 
'''
import nasem_dairy as nd

import pandas as pd

# # Reload the module
# import importlib
# nd = importlib.reload(nd)


###############################

# animal_input is a dictionary with all animal specific parameters
# diet_info is a dataframe with the user entered feed ingredients and %DM intakes
diet_info, animal_input, equation_selection = nd.read_input('../src/nasem_dairy/data/input.txt')

# import description strings for variable names in model
var_desc = pd.read_csv('../src/nasem_dairy/data/variable_descriptions.csv').query('Description != "Duplicate"')



# Execute function

# Assign values here so they can be see in environment
# coeff_dict is imported from ration_balancer, see coeff_dict.py
NASEM_out = nd.NASEM_model(diet_info, animal_input, equation_selection, '../src/nasem_dairy/data/diet_database.db', nd.coeff_dict)


# Display results, temporary
def display_diet_values(df):
    components = ['Fd_CP', 'Fd_RUP_base', 'Fd_NDF', 'Fd_ADF', 'Fd_St', 'Fd_CFat', 'Fd_Ash']
    rows = []

    for component in components:
        percent_diet = round(df.loc['Diet', component + '_%_diet']) #.values[0], 2)
        kg_diet = round(df.loc['Diet', component + '_kg/d'])    #.values[0], 2)
        rows.append([component, percent_diet, kg_diet])

    headers = ['Component', '% DM', 'kg/d']

    table = pd.DataFrame(rows, columns = headers)

    return table



model_data_short = pd.DataFrame.from_dict(NASEM_out['model_results_short'],orient='index', columns=['Value']).reset_index()

all_calculated_values = pd.DataFrame.from_dict(
    NASEM_out['model_results_full'],orient='index', columns=['Value']
    ).reset_index(names="Model Variable"
                  ).merge(var_desc, how = 'left')

diet_data  = display_diet_values(NASEM_out["diet_info"])

print(model_data_short)
print(all_calculated_values)
print(diet_data)
