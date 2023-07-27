# This is a function meant to clean sensor data before it is input into the model. This was used to run ME_calculations and MP_calculations.

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
def clean_input_data(df):
    # Rename existing columns
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
    
    # Add default values
    df['An_BW_mature'] = 700
    df['Trg_FrmGain'] = 0
    df['An_GestLength'] = 280
    df['Fet_BWbrth'] = 44.1
    df['Trg_MilkLacp'] = 4.85
    df['Trg_RsrvGain'] = 0
    df['An_AgeDay'] = df['age_m'] * 30.436875
    
    # Remove diet information
    diet_columns = ['location', 'Acid Detergent Fibre (%)', 'Ash (%)', 'Calcium (%)', 'Copper (ug/g)', 'Crude Fat (%)', 'Crude Protein (%)', 'Dry Matter (%)', 'Iron (ug/g)', 'Magnesium (%)', 'Manganese (ug/g)', 'Moisture (%)', 'NE Gain (MCal/Kg)', 'NE Lactation (MCal/Kg)', 'NE Maintenance (MCal/Kg)', 'NFC (%)', 'Neutral Detergent Fibre (%)', 'Phosphorus (%)', 'Potassium (%)', 'Sodium (%)', 'Starch (%)', 'Sulphur (%)', 'Total Digestible Nutrients (%)', 'Zinc (ug/g)', 'DIM_bins_w']
    df = df.drop(columns = diet_columns)

    # Assign Diet_ID
    df = df.assign(
        Diet_ID = lambda df: df['sampleId'] + '_' + df['reportDate'].dt.strftime('%Y-%m-%d')
        )

    # Calculate NDF intake by getting NDF (% DM) from database
    conn = sqlite3.connect('../diet_database.db')
    query = "SELECT Diet_ID, `Neutral Detergent Fibre (%)` FROM current_diets"
    # create data frame from query:
    df_NDF = pd.read_sql_query(query, conn)
    conn.close()
    # Merge dataframes
    clean_data = pd.merge(
        df,
        df_NDF,
        on = 'Diet_ID'
    )
    # Calculate NDF intake in kg
    clean_data = clean_data.assign(
    Dt_NDFIn = lambda df: df['Neutral Detergent Fibre (%)']/100 * df['Dt_DMIn']
    )

    # Drop unneeded columns
    columns_to_drop = ['date', 'weight', 'asfed_intake', 'bcs_value', 'Birth Date', 'Test Day Date',
                       'Lact Start Date', 'SCC', 'Pregnancy Indicator', 'Days to Last Breeding', 
                       'conception_date', 'age_m', 'sampleId', 'reportDate']
    clean_data = clean_data.drop(columns = columns_to_drop)

    return clean_data
