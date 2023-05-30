#' Clean Input Data frame
#'
#' This function takes an input data frame and modifies it to work with the model.
#' The existing columns are renamed and additional default values are added. 
#' Animal age and NDF intake are calculated based on data in the input file.
#'
#' @param df Data frame. File containing all recorded information on animals 
#'
#' @return input_data_nested. A modified data frame where all data is nested based
#'  on animal ID and week of observations.
#' 
#' @export
#'
def clean_data(df):
    # Rename existing columns needed for the model
    df = df.rename(columns={
    'lactation_number': 'An_Parity_rl',
    'days_in_milk': 'An_LactDay',
    'MY': 'Trg_MilkProd',
    'BW_smooth': 'An_BW',
    'DMI': 'Dt_DMIn',
    'Fat %': 'Trg_MilkFatp',
    'Protein %': 'Trg_MilkTPp',
    'days_preg': 'An_GestDay'
})
    # Add columns with default values
    df['An_BW_mature'] = 700
    df['Trg_FrmGain'] = 0
    df['An_GestLength'] = 280
    df['Fet_BWbrth'] = 44.1
    df['Trg_MilkLacp'] = 4.85
    df['Trg_RsrvGain'] = 0

    # Add columns based on other columns
    df['An_AgeDay'] = df['age_m'] * 30.436875
    # 30.436875 converts months into days
  
    df['Dt_NDFIn'] = df['Dt_DMIn'] * 0.30
    # Assume ration is 30% NDF on DM basis, use DMI to get an NDF intake
    # This is temporary until we can add real NDF intake

# Create a nested data frame

    # data = df.drop(df.columns[:2], axis=1)
    # ID = df.drop(df.columns[2:], axis=1)
    # input_data_clean = pd.DataFrame({'idx':[1,2], 'dfs':[ID, data]})

# print(input_data_clean['dfs'].iloc[0]) # This will access the 'ID' Dataframe
# print(input_data_clean['dfs'].iloc[1]) # This will access the 'data' Dataframe
    
    # data_dict = data.to_dict()
    # input_data_clean = df.iloc[:, :2]
    # input_data_clean['data'] = data_dict

 # This does not work the same in python as in R. There is a way to store all the
 # data as a dictionary in the dataframe but I'm not sure how easy the data
 # would be to access if done this way

    # input_data_nested = df.groupby(['cow_id', 'DIM_bins_w'])
    input_data_clean = df
    return(input_data_clean)
