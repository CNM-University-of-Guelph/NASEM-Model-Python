# This file contains all of the functions used to execute the NASEM model in python


import pandas as pd
import sqlite3
import numpy as np


def check_coeffs_in_coeff_dict(input_coeff_dict, required_coeffs):
    # Convert the list to a set for faster lookup
    req_coef = set(required_coeffs)
    dict_in = set(input_coeff_dict)

    # Return coeffs that are not in dict_in
    missing_coeffs = [value for value in req_coef if value not in dict_in]

    # Check if all values are present in the dictionary
    result = not bool(missing_coeffs)

    # Raise an AssertionError with a custom message containing missing values if the condition is False
    assert result, f"Missing values in coeff_dict: {missing_coeffs}"

    return



def read_input(input):
    """
    Reads a .txt file and gets the input parameters

    Uses the leading character on each line to read the text file. * indicates an animal parameter, $ is for selecting different equations and
    # skips the line. No leading character is used for the diet inputs.

    Parameters:
        input (str): pathway to the text file where users input parameters
    """
    # User will type the ration into input.txt
    # This function reads that file and creates a dataframe with all of the feeds and % DM  
    data = []
    animal_input = {}
    equation_selection = {}

    with open(input, 'r') as file:
        for line in file:
            line = line.strip()

            if line.startswith('#') or ':' not in line:
                continue

            if line.startswith('*'):
                key, value = line[1:].split(":")
                animal_input[key.strip()] = float(value.strip())
                continue

            if line.startswith('$'):
                key, value = line[1:].split(":")
                equation_selection[key.strip()] = int(value.strip())
                continue

            feedstuff, per_DM = line.split(":")
            data.append([feedstuff.strip(), per_DM.strip()])

    diet_info = pd.DataFrame(data, columns=["Feedstuff", "%_DM_user"])
    diet_info['%_DM_user'] = diet_info['%_DM_user'].astype(float)
    
    diet_info['Feedstuff'] = diet_info['Feedstuff'].str.strip()

    diet_info['Index'] = diet_info['Feedstuff']
    diet_info = diet_info.set_index('Index') 

    return diet_info, animal_input, equation_selection


def fl_get_feed_rows(feeds_to_get: list, 
                     feed_lib_df: pd.DataFrame) -> pd.DataFrame:
    '''
    A function that takes a list of feed names to filter the nasem feed library (as a pandas dataframe).
    This was originally implemented using a database but this is an alternative that uses only a df and produces the same output.
    '''

    # Filter df using list from user
    selected_feed_data = feed_lib_df[feed_lib_df["Fd_Name"].isin(feeds_to_get)]

    # set names as index for downstream
    selected_feed_data = selected_feed_data.set_index('Fd_Name')

    # Clean names:
    selected_feed_data.index = selected_feed_data.index.str.strip()

    return selected_feed_data



def fl_get_rows(feeds_to_get, path_to_db):
    conn = sqlite3.connect(path_to_db)

    """
    Modified version of :py:func:`db_get_rows` that queries NASEM feed library only

    Parameters:
        feeds_to_get (list): List of feed names 
    """
    cursor = conn.cursor()

    index_str = ', '.join([f"'{idx}'" for idx in feeds_to_get])

    query = f"SELECT * FROM NASEM_feed_library WHERE Fd_Name IN ({index_str})"

    cursor.execute(query)
    rows = cursor.fetchall()

    cursor.execute(f"PRAGMA table_info(NASEM_feed_library)")
    column_names = [column[1] for column in cursor.fetchall()]

    # Create a DataFrame from the retrieved rows with column names
    feed_data = pd.DataFrame(rows, columns=column_names)
    feed_data = feed_data.set_index('Fd_Name')
    feed_data.index = feed_data.index.str.strip()

    conn.close()

    return feed_data


def get_nutrient_intakes(df, feed_data, DMI, equation_selection, coeff_dict):
    """
    Takes the feeds in the diet and the % dry matter intake and calculates nutrient supplies

    Parameters:
        df (Dataframe): The dataframe all the results will be stored in, must contain feed names and % DMI
        feed_data (Dataframe): Individual feed compositions
        DMI (number): Dry Matter Intake - normally from the animal_input dictionary
        equation_selection (Dict): Dictionary with values for every selectable equation
        coeff_dict (Dict): Dictionary containing all coefficients for the model
    
    Returns:
        df (Dataframe): The dataframe all the results will be stored in, must contain feed names and % DMI
    """
    # This function should get a better name
    # This function will perform ALL feed related calculations for the model
    # ALL of the feed related vairables needed by future calculations will come from the diet_info dataframe
    # Anything in the R code that references f$"variable" should be included here where "variable" is a column
    # Any values in the R code where Dt_"variable" = sum(f$"variable") are equivalent to the column "variable" in the 'Diet' row
    req_coeffs = ['Fd_dcrOM', 'fCPAdu', 'KpFor', 'KpConc', 'IntRUP', 
                  'refCPIn', 'TT_dcFA_Base', 'TT_dcFat_Base', 'En_CP',
                  'En_FA', 'En_St', 'En_NDF', 'En_rOM']
    check_coeffs_in_coeff_dict(coeff_dict, req_coeffs)
    
    # Remove the 'Diet' row if it exists before recalculating, otherwise, the new sum includes the old sum when calculated
    if 'Diet' in df.index:
        df = df.drop(index='Diet')

    # Adjust kg_user so that the sum is equal to animal_input['DMI'], which may have been adjusted by the DMI predictions the user selected
    df['kg_user'] = df['Fd_DMInp'] * DMI


    # Define the dictionary of component names, this is the list of all the values you need to calculate
    # Some values will be calculated as an intermediate step for other values and therefore do no need to be listed
    # Use Ctrl-F to check before adding to this dictionary
    component_dict = {
        'Fd_CP': 'Crude Protein',
        'Fd_RUP_base': 'Rumen Undegradable Protein',
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
   
    # List any values that have the units % DM
    units_DM = ['Fd_CP', 'Fd_NDF', 'Fd_ADF', 'Fd_St', 'Fd_CFat', 'Fd_Ash', 'Fd_FA'] 

    for intake, full_name in component_dict.items():
        if intake in units_DM:
            df[intake] = df['Feedstuff'].map(feed_data[intake]) / 100                       # Get value from feed_data as a percentage
            df[intake + '_%_diet'] = df[intake] * df['Fd_DMInp']                            # Calculate component intake on %DM basis
            df[intake + '_kg/d'] = df[intake + '_%_diet'] * df['kg_user'].sum()             # Calculate component kg intake 


        elif intake == 'Fd_RUP_base':                                                                # RUP is in % CP, so an extra conversion is needed
            df[intake] = df['Feedstuff'].map(feed_data[intake]) / 100
            df['Fd_RUP_base_%_CP'] = df[intake] * df['Fd_DMInp']
            df['Fd_RUP_base_%_CP'] = df[intake] * df['Fd_DMInp']
            df['Fd_RUP_base_%_diet'] = df['Fd_RUP_base_%_CP'] * df['Fd_CP']
            df['Fd_RUP_base_kg/d'] = df['Fd_RUP_base_%_diet'] * df['kg_user'].sum() 
        

        elif intake == 'Fd_DigNDFIn_Base':
            df['Fd_NDFIn'] = (df['Feedstuff'].map(feed_data['Fd_NDF']) / 100) * df['kg_user'] 
            df['Fd_NDFIn'] = (df['Feedstuff'].map(feed_data['Fd_NDF']) / 100) * df['kg_user'] 
            df['TT_dcFdNDF_48h'] = 12 + 0.61 * df['Feedstuff'].map(feed_data['Fd_DNDF48_NDF'])
            Use_DNDF_IV = equation_selection['Use_DNDF_IV']
            if Use_DNDF_IV == 1 and df['Feedstuff'].map(feed_data['Fd_Conc']) < 100 and not np.isnan(df['TT_dcFdNDF_48h']):
                df['TT_dcFdNDF_Base'] = df['TT_dcFdNDF_48h']
            elif Use_DNDF_IV == 2 and not np.isnan(df['TT_dcFdNDF_48h']):
                df['TT_dcFdNDF_Base'] = df['TT_dcFdNDF_48h']
            else:
                def calculate_TT_dcFdNDF_Lg(Fd_NDF, Fd_Lg):
                    TT_dcFdNDF_Lg = 0.75 * (Fd_NDF - Fd_Lg) * (1 - (Fd_Lg / np.where(Fd_NDF == 0, 1e-6, Fd_NDF)) ** 0.667) / np.where(Fd_NDF == 0, 1e-6, Fd_NDF) * 100
                    return TT_dcFdNDF_Lg
                df['TT_dcFdNDF_Lg'] = calculate_TT_dcFdNDF_Lg(df['Feedstuff'].map(feed_data['Fd_NDF']), df['Feedstuff'].map(feed_data['Fd_Lg']))
                df['TT_dcFdNDF_Base'] = df['TT_dcFdNDF_Lg']
            df['Fd_DigNDFIn_Base'] = df['TT_dcFdNDF_Base'] / 100 * df['Fd_NDFIn']
        

        elif intake == 'Fd_DigStIn_Base':
            df['Fd_DigSt'] = df['Feedstuff'].map(feed_data['Fd_St']) * df['Feedstuff'].map(feed_data['Fd_dcSt']) / 100
            df['Fd_DigStIn_Base'] = df['Fd_DigSt'] / 100 * df['kg_user']
            df['Fd_DigStIn_Base'] = df['Fd_DigSt'] / 100 * df['kg_user']


        elif intake == 'Fd_DigrOMtIn':
            # Fd_dcrOM = 96				                                                # Line 1005, this is a true digestbility.  There is a neg intercept of -3.43% of DM
            df['Fd_fHydr_FA'] = 1 / 1.06                                                # Line 461
            df.loc[df['Feedstuff'].map(feed_data['Fd_Category']) == "Fatty Acid Supplement", 'Fd_fHydr_FA'] = 1
            df['Fd_NPNCP'] = df['Feedstuff'].map(feed_data['Fd_CP']) * df['Feedstuff'].map(feed_data['Fd_NPN_CP']) / 100
            df['Fd_TP'] = df['Feedstuff'].map(feed_data['Fd_CP']) - df['Fd_NPNCP']
            df['Fd_NPNDM'] = df['Fd_NPNCP'] / 2.81
            df['Fd_rOM'] = 100 - df['Feedstuff'].map(feed_data['Fd_Ash']) - df['Feedstuff'].map(feed_data['Fd_NDF']) - df['Feedstuff'].map(feed_data['Fd_St']) - (df['Feedstuff'].map(feed_data['Fd_FA']) * df['Fd_fHydr_FA']) - df['Fd_TP'] - df['Fd_NPNDM'] 
            df['Fd_DigrOMt'] = coeff_dict['Fd_dcrOM'] / 100 * df['Fd_rOM']
            df['Fd_DigrOMtIn'] = df['Fd_DigrOMt'] / 100 * df['kg_user']
            df['Fd_DigrOMtIn'] = df['Fd_DigrOMt'] / 100 * df['kg_user']
        

        elif intake == 'Fd_idRUPIn':
            # fCPAdu = 0.064
            # KpFor = 4.87        #%/h
            # KpConc = 5.28	    #From Bayesian fit to Digesta Flow data with Seo Kp as priors, eqn. 26 in Hanigan et al.
            # IntRUP = -0.086 	#Intercept, kg/d
            # refCPIn = 3.39  	#average CPIn for the DigestaFlow dataset, kg/d.  3/21/18, MDH
            df['Fd_CPIn'] = df['Feedstuff'].map(feed_data['Fd_CP']) / 100 * df['kg_user'] 
            df['Fd_CPIn'] = df['Feedstuff'].map(feed_data['Fd_CP']) / 100 * df['kg_user'] 
            df['Fd_CPAIn'] = df['Fd_CPIn'] * df['Feedstuff'].map(feed_data['Fd_CPARU']) / 100
            df['Fd_NPNCPIn'] = df['Fd_CPIn'] * df['Feedstuff'].map(feed_data['Fd_NPN_CP']) / 100
            df['Fd_CPBIn'] = df['Fd_CPIn'] * df['Feedstuff'].map(feed_data['Fd_CPBRU']) / 100
            df['Fd_For'] = 100 - df['Feedstuff'].map(feed_data['Fd_Conc'])
            
            df['Fd_RUPBIn'] = (
                df['Fd_CPBIn'] * df['Fd_For'] / 100 * coeff_dict['KpFor'] / 
                (df['Feedstuff'].map(feed_data['Fd_KdRUP']) + coeff_dict['KpFor']) + 
                df['Fd_CPBIn'] * df['Feedstuff'].map(feed_data['Fd_Conc']) / 
                100 * coeff_dict['KpConc'] / (df['Feedstuff'].map(feed_data['Fd_KdRUP']) + coeff_dict['KpConc'])
                )
            
            df['Fd_CPCIn'] = df['Fd_CPIn'] * df['Feedstuff'].map(feed_data['Fd_CPCRU']) / 100
            df['Fd_RUPIn'] = (df['Fd_CPAIn'] - df['Fd_NPNCPIn']) * coeff_dict['fCPAdu'] + df['Fd_RUPBIn'] + df['Fd_CPCIn'] + coeff_dict['IntRUP'] / coeff_dict['refCPIn'] * df['Fd_CPIn'] 
            df['Fd_idRUPIn'] = df['Feedstuff'].map(feed_data['Fd_dcRUP']) / 100 * df['Fd_RUPIn']
        

        elif intake == 'Fd_DigFAIn':
            # TT_dcFA_Base = 73
            # TT_dcFat_Base = 68 
            df['TT_dcFdFA'] = df['Feedstuff'].map(feed_data['Fd_dcFA'])
            df.loc[df['Feedstuff'].map(feed_data['Fd_Category']) == "Fatty Acid Supplement", 'TT_dcFdFA'] = coeff_dict['TT_dcFA_Base']
            df.loc[df['Feedstuff'].map(feed_data['Fd_Category']) == "Fat Supplement", 'TT_dcFdFA'] = coeff_dict['TT_dcFat_Base']
            df['Fd_DigFAIn'] = (df['TT_dcFdFA'] / 100) * (df['Feedstuff'].map(feed_data['Fd_FA']) / 100) * df['kg_user']
            df['Fd_DigFAIn'] = (df['TT_dcFdFA'] / 100) * (df['Feedstuff'].map(feed_data['Fd_FA']) / 100) * df['kg_user']

        
        elif intake == 'Fd_ForWet':
            # df['Fd_For'] = 100 - df['Feedstuff'].map(feed_data['Fd_Conc'])
            
            condition = (df['Fd_For'] > 50) & (df['Feedstuff'].map(feed_data['Fd_DM']) < 71)
            df['Fd_ForWet'] = np.where(condition, df['Fd_For'], 0)
            df['Fd_ForWetIn'] = df['Fd_ForWet'] / 100 * df['kg_user']
            df['Fd_ForWetIn'] = df['Fd_ForWet'] / 100 * df['kg_user']


        elif intake == 'Fd_ForNDFIn':
            df['Fd_ForNDF'] = (1 - df['Feedstuff'].map(feed_data['Fd_Conc']) / 100) * df['Feedstuff'].map(feed_data['Fd_NDF'])
            df['Fd_ForNDFIn'] = df['Fd_ForNDF'] / 100 * df['kg_user']
            df['Fd_ForNDFIn'] = df['Fd_ForNDF'] / 100 * df['kg_user']


        elif intake == 'Fd_FAIn':
            df['Fd_FAIn'] = df['Feedstuff'].map(feed_data['Fd_FA']) / 100 * df['kg_user']
            df['Fd_FAIn'] = df['Feedstuff'].map(feed_data['Fd_FA']) / 100 * df['kg_user']

        elif intake == 'Fd_DigC160In':
            df['Fd_DigC160In'] = df['TT_dcFdFA'] / 100 * df['Feedstuff'].map(feed_data['Fd_C160_FA']) / 100 * df['Feedstuff'].map(feed_data['Fd_FA']) / 100 * df['kg_user']
            df['Fd_DigC160In'] = df['TT_dcFdFA'] / 100 * df['Feedstuff'].map(feed_data['Fd_C160_FA']) / 100 * df['Feedstuff'].map(feed_data['Fd_FA']) / 100 * df['kg_user']
            # These DigC___In calculations can be made into a loop if the rest are needed at some point 

        elif intake == 'Fd_DigC183In':
            df['Fd_DigC183In'] = df['TT_dcFdFA'] / 100 * df['Feedstuff'].map(feed_data['Fd_C183_FA']) / 100 * df['Feedstuff'].map(feed_data['Fd_FA']) / 100 * df['kg_user']
            df['Fd_DigC183In'] = df['TT_dcFdFA'] / 100 * df['Feedstuff'].map(feed_data['Fd_C183_FA']) / 100 * df['Feedstuff'].map(feed_data['Fd_FA']) / 100 * df['kg_user']

        elif intake == 'Fd_TPIn':
            df['Fd_TPIn'] = df['Fd_TP'] / 100 * df['kg_user']

        elif intake == 'Fd_GEIn':
            df['Fd_GE'] = (df['Fd_CP'] * coeff_dict['En_CP']) + (df['Fd_FA'] * coeff_dict['En_FA']) + (df['Fd_St'] * coeff_dict['En_St']) + (df['Fd_NDF'] * coeff_dict['En_NDF']) + ((1 - df['Fd_CP'] - df['Fd_FA'] - df['Fd_St'] - df['Fd_NDF'] - df['Fd_Ash']) * coeff_dict['En_rOM'])
            df['Fd_GEIn'] = df['Fd_GE'] * df['kg_user']

    # Sum component intakes
    df.loc['Diet'] = df.sum()
    df.at['Diet', 'Feedstuff'] = 'Diet'

    # Perform calculations on summed columns
    df.loc['Diet', 'Dt_RDPIn'] = df.loc['Diet', 'Fd_CPIn'] - df.loc['Diet', 'Fd_RUPIn']

    # Rename columns using the dictionary of component names
    # df.columns = df.columns.str.replace('|'.join(component_dict.keys()), lambda x: component_dict[x.group()], regex=True)
    
    return df


def read_csv_input(path_to_file):
    
    animal_input = {}
    equation_selection = {}
    diet_info_data = {'Feedstuff': [], 'kg_user': []}

    input_data = pd.read_csv(path_to_file)

    for index, row in input_data.iterrows():
        location = row['Location']
        variable = row['Variable']
        value = row['Value']
        
        if location == 'equation_selection':
            equation_selection[variable] = float(value) if value.replace('.', '', 1).isdigit() else value
        elif location == 'animal_input':
            animal_input[variable] = float(value) if value.replace('.', '', 1).isdigit() else value
        elif location == 'diet_info':
            diet_info_data['Feedstuff'].append(variable)
            diet_info_data['kg_user'].append(value)
      
    diet_info = pd.DataFrame(diet_info_data)
    diet_info['kg_user'] = pd.to_numeric(diet_info['kg_user'], downcast="float")

    return diet_info, animal_input, equation_selection


def NDF_precalculation(diet_info, feed_data):
    # Create df to perform calculations with
    df_NDF = pd.DataFrame()
    # Copy feed names from diet_info
    df_NDF['Feedstuff'] = diet_info['Feedstuff'].copy()
    df_NDF['kg_user'] = diet_info['kg_user'].copy()
    # Drop the diet row from this df if it exists, this will prevent errors if a user called this function after running get_nutrient_intakes
    df_NDF = df_NDF[df_NDF['Feedstuff'] != 'Diet']
    # Get a % intake based on user entered kg/d
    df_NDF['user_%_intake'] = df_NDF['kg_user'] / df_NDF['kg_user'].sum()
    # Get NDF% of each feed as a decimal
    df_NDF['Fd_NDF'] = df_NDF['Feedstuff'].map(feed_data['Fd_NDF']) / 100
    # Calculate % NDF of diet
    Dt_NDF = (df_NDF['Fd_NDF'] * df_NDF['user_%_intake']).sum()
    # Cleanup
    del(df_NDF)
   
    return Dt_NDF

