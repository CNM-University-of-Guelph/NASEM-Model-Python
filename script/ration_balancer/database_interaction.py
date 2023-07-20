# These functions can be imported into other scripts and allow for interaction with the diet_database.db
# without the user needing to write SQL code

import pandas as pd
import sqlite3 

# 1a. Save dataframe to a new table
def db_new_table(df, table_name, index=None):
    """
    Create a table in the database.

    This function will take a dataframe and save it to a table in the database. If the table
    name does not exist a new table will be created. If there is an existing table with that 
    name a ValueError will be raised. This is to prevent users from accidentally overwriting their data. 
    
    If you need to overwrite a table use :py:func:`db_overwrite_table`

    Parameters:
        df (dataframe): A dataframe with the data to go into the database table
        table_name (str): The name of the new table
        index (str): A column of the dataframe that will be used to index the table. By default there is no index.
    """
    conn = sqlite3.connect('../diet_database.db')
    cursor = conn.cursor()

    if index is not None:
        df.set_index(index, inplace=True)
        df.to_sql(table_name, conn, if_exists='fail')
    else:
        df.to_sql(table_name, conn, if_exists='fail', index=False)
    
    conn.close()


# 1b. Save dataframe to table and overwrite an existing table
def db_overwrite_table(df, table_name, index=None):
    """
    Overwrite a table in the database.

    This function will take a dataframe and save it to a table in the database. If there is an existing table with that 
    name it will be overwritten. If the table name does not exist a new table will be created.

    Be careful using this function as it is possible to lose the data previously stored in the table.

    Parameters:
        df (dataframe): A dataframe with the data to go into the database table
        table_name (str): The name of the new table
        index (str): A column of the dataframe that will be used to index the table. By default there is no index.
    """
    conn = sqlite3.connect('../diet_database.db')
    cursor = conn.cursor()

    if index is not None:
        df.set_index(index, inplace=True)
        df.to_sql(table_name, conn, if_exists='replace')
    else:
        df.to_sql(table_name, conn, if_exists='replace', index=False)
    
    conn.close()


# 2. Print a table
def db_print_table(table_name, head=None):
    """
    Prints out the specified table.

    By default all rows are printed. The head parameter can be used to set the number of rows.

    Parameters:
        table_name (str): Name of a table in the database
        head (int): The number of rows to print
    """
    conn = sqlite3.connect('../diet_database.db')
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM {}'.format(table_name))
    rows = cursor.fetchall()

     # Get the column names
    column_names = [description[0] for description in cursor.description]
    print(column_names)
            
    if head is not None:
        rows = rows[:head]
    for row in rows:
        print(row)

    conn.close()


# 3. Read a table to a dataframe
def db_get_table(table_name, columns=None):
    """
    Query database and save the table to a dataframe.

    By default the entire table is selected. If only specific columns are needed a list 
    of the columns to get must be added. The columns will be added to the dataframe in the order
    they are listed. The function should be used as follows:

    new_df = db_get_table('insert_table_name', columns=list_of_columns)

    Parameters:
        table_name (str): Name of a table in the database
        columns (list): List of the column names to get from the table    
    """
    conn = sqlite3.connect('../diet_database.db')

    # If there is no list given or the list is empty select the entire table
    if columns is None or len(columns) == 0:
        query = f"SELECT * FROM {table_name}"
    else:
        cols_str = ', '.join(columns)
        query = f"SELECT {cols_str} FROM {table_name}"
    
    df = pd.read_sql_query(query, conn)

    conn.close()
    return df


# 4. Add new rows to an existing table
def db_add_rows(table_name, df, index=None):
    """
    Append new data to existing table.

    The data can be indexed or not. The new data will be added to the bottom of the table.

    Parameters:
        table_name (str): Name of a table in the database
        df (dataframe): Dataframe to add to table
        index (str): Index to use for table
    """
    conn = sqlite3.connect('../diet_database.db')

    if index is not None:
        df.set_index(index, inplace=True)

    df.to_sql(table_name, conn, if_exists='append')

    conn.close()


# 5. Add new column to an existing table
def db_add_columns(table_name, new_column_names, df):
    conn = sqlite3.connect('../diet_database.db')
    cursor = conn.cursor()

    for column_name, data_type in new_column_names.items():
        
        # PRAGMA table_info returns a table of values where each row in the table describes a different column
        # The first column in this table is the name of the column 
        cursor.execute(f"PRAGMA table_info({table_name})")
        # Create a list of the existing columns
        existing_columns = [column[1] for column in cursor.fetchall()]

        # Check if the column already exists
        if column_name in existing_columns:
            print(f"Column '{column_name}' already exists in table '{table_name}'")
        else:
            # Add the new column to the table
            cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {data_type}")

    # Convert the DataFrame to a temporary table in the database
    df.to_sql('temp_table', conn, if_exists='replace', index=False)

    # Update the new column in the main table with the values from the temporary table
    cursor.execute(f"UPDATE {table_name} SET {', '.join(new_column_names.keys())} = (SELECT {', '.join(new_column_names.keys())} FROM temp_table WHERE {table_name}.[animal_ID] = temp_table.animal_ID)")
    cursor.execute("DROP TABLE temp_table")

    conn.commit()
    conn.close()


# 6. Pull specific rows from a table
def db_get_rows(table_name, rows_to_get):
    conn = sqlite3.connect('../diet_database.db')
    cursor = conn.cursor()

    # Get the primary key column name for the table
    cursor.execute(f"SELECT sql FROM sqlite_master WHERE name='{table_name}'")
    create_table_query = cursor.fetchone()[0]
    index_column = create_table_query.split('(')[1].split(' ')[0]

    # Create a comma-separated string of index values enclosed in quotes for the SQL query
    index_str = ', '.join([f"'{idx}'" for idx in rows_to_get])

    # Formulate the SQL query to retrieve the rows based on index values
    query = f"SELECT * FROM {table_name} WHERE {index_column} IN ({index_str})"

    # Execute the query and fetch all the rows
    cursor.execute(query)
    rows = cursor.fetchall()

    # Get the column names from the table
    cursor.execute(f"PRAGMA table_info({table_name})")
    column_names = [column[1] for column in cursor.fetchall()]

    # Create a DataFrame from the retrieved rows with column names
    df = pd.DataFrame(rows, columns=column_names)

    conn.close()

    return df


