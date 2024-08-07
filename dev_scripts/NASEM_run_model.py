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
# diet_info, animal_input, equation_selection = nd.read_csv_input("../src/nasem_dairy/data/input.csv")

diet_info, animal_input, equation_selection = nd.read_csv_input("./input_2.csv")
# diet_info, animal_input, equation_selection = nd.read_csv_input('./dev_files/input_drycow.csv')

# Load feed library
feed_library = pd.read_csv("../src/nasem_dairy/data/NASEM_feed_library.csv")

# import description strings for variable names in model
var_desc = pd.read_csv('../src/nasem_dairy/data/variable_descriptions.csv').query('Description != "Duplicate"')




# Execute function

# Assign values here so they can be see in environment
# coeff_dict is imported from ration_balancer, see coeff_dict.py
NASEM_out = nd.NASEM_model(diet_info, animal_input, equation_selection, feed_library, nd.coeff_dict)

# View results:
pd.DataFrame.from_dict(NASEM_out['model_results_short'],orient='index', columns=['Value']).reset_index()


# Testing animal_inputs for dry cow flag
animal_input['An_StatePhys'] = 'Dry Cow'
animal_input['Trg_MilkProd'] = 0 # fails with an error
animal_input['Trg_MilkProd'] = 35

animal_input['Trg_MilkFatp'] = 4.1
animal_input['Trg_MilkTPp'] = 3.8
animal_input['Trg_MilkLacp'] = 4.5
# if setting all to 0 it throws an error at the same error as when Trg_MilkProd is 0, except it still runs
animal_input['Trg_MilkLacp'] = 0
animal_input['Trg_MilkTPp'] = 0
animal_input['Trg_MilkFatp'] = 0

NASEM_out = nd.NASEM_model(diet_info, animal_input, equation_selection, feed_library, nd.coeff_dict)

# View results:
pd.DataFrame.from_dict(NASEM_out['model_results_short'],orient='index', columns=['Value']).reset_index()


NASEM_out['animal_input']
# Display results, temporary
def display_diet_values(df):
    components = ['Fd_CP', 'Fd_RDP_base','Fd_RUP_base', 'Fd_NDF', 'Fd_ADF', 'Fd_St', 'Fd_CFat', 'Fd_Ash']
    rows = []

    for component in components:
        percent_diet = round(df.loc['Diet', component + '_%_diet'],3) #.values[0], 2)
        kg_diet = round(df.loc['Diet', component + '_kg/d'],3)    #.values[0], 2)
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

NASEM_out['diet_info'].info()


NASEM_out['mineral_requirements_dict']

NASEM_out['vitamin_intakes']

df_minerals = NASEM_out['mineral_intakes']

# format minerals to show properly
df_minerals.assign(
    Diet_percent = lambda df: df['Dt_micro'].fillna(df['Dt_macro'])
).drop(columns=['Dt_macro', 'Dt_micro','Abs_mineralIn'])




component_dict = {
        'Fd_CP': 'Crude Protein',
        'Fd_RUP_base': 'Rumen Undegradable Protein',
        'Fd_RDP_base': 'Rumen Degradable Protein',
        'Fd_NDF': 'Neutral Detergent Fiber',
        'Fd_ADF': 'Acid Detergent Fiber',
        'Fd_St': 'Starch',
        'Fd_CFat': 'Crude Fat',
        'Fd_Ash': 'Ash',
        'Fd_FA': 'Fatty Acids',
        'Fd_DigNDFIn_Base': 'Digestable NDF Intake',
        'Fd_DigStIn_Base': 'Digestable Starch Intake',
        'Fd_DigrOMtIn': 'Digestable Residual Organic Matter Intake',
        'Fd_idRUPIn': 'Digested RUP',
        'Fd_DigFAIn': 'Digested Fatty Acid Intake',
        'Fd_ForWet': 'Wet Forage',
        'Fd_ForNDFIn': ' Forage NDF Intake',
        'Fd_FAIn': 'Fatty Acid Intake',
        'Fd_DigC160In': 'C160 FA Intake',
        'Fd_DigC183In': 'C183 FA Intake',
        'Fd_TPIn': 'True Protein Intake',
        'Fd_GEIn': 'Gross Energy Intake'
    }


# import numpy as np
diet_long = (
    NASEM_out["diet_info"].loc['Diet',:]
    .to_frame()
    .iloc[1:,:]
    .reset_index(names='component')
    .assign(
        component_long = lambda df: df['component'].map(component_dict)
        )
        )

print(diet_long)


# Amino Acids
NASEM_out['AA_values']
