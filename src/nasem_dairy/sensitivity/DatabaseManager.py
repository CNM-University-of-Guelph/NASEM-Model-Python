import datetime
import os
import pickle
import sqlite3
from typing import Any, Dict, List, Tuple, Optional

import pandas as pd

from nasem_dairy.sensitivity.response_variables_config import RESPONSE_VARIABLE_NAMES

class DatabaseManager:
    def __init__(self, db_path: str):
        """
        Initialize the DatabaseManager with the path to the database file.
        If the database does not exist, it will be created.

        Args:
            db_path (str): Path to the SQLite database file.
        """
        self.db_path = db_path
        if not os.path.exists(db_path):
            self.create_database()
        else:
            # Verify the database by trying to connect
            self.connect()
            self.close()

    def connect(self):
        """Establish a connection to the SQLite database."""
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()

    def create_database(self):
        """Create a new database with the necessary tables."""
        self.connect()
        self.create_tables()
        self.close()

    def create_tables(self):
        """Create tables in the database based on the schema."""
        # Create Coefficients Table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS Coefficients (
                coeff_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL
            )
        ''')

        # Create Problems Table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS Problems (
                problem_id INTEGER PRIMARY KEY AUTOINCREMENT,
                date_run DATETIME NOT NULL,
                filename TEXT NOT NULL,
                user_diet BLOB NOT NULL,
                animal_input BLOB NOT NULL,
                equation_selection BLOB NOT NULL,
                infusion_input BLOB NOT NULL,
                problem BLOB NOT NULL
            )
        ''')

        # Create Samples Table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS Samples (
                sample_id INTEGER PRIMARY KEY AUTOINCREMENT,
                problem_id INTEGER NOT NULL,
                sample_index INTEGER NOT NULL,
                parameter_values BLOB NOT NULL,
                result_file_path TEXT,
                FOREIGN KEY(problem_id) REFERENCES Problems(problem_id)
            )
        ''')

        # Create ResponseVariables Table
        variable_columns = RESPONSE_VARIABLE_NAMES
        columns_definition = ',\n'.join(
            [f"{col} REAL" for col in variable_columns]
            )
        self.cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS ResponseVariables (
                response_id INTEGER PRIMARY KEY AUTOINCREMENT,
                problem_id INTEGER NOT NULL,
                sample_id INTEGER NOT NULL,
                {columns_definition},
                FOREIGN KEY(problem_id) REFERENCES Problems(problem_id),
                FOREIGN KEY(sample_id) REFERENCES Samples(sample_id)
            )
        ''')

        # Create Results Table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS Results (
                result_id INTEGER PRIMARY KEY AUTOINCREMENT,
                problem_id INTEGER NOT NULL,
                coeff_id INTEGER NOT NULL,
                response_id INTEGER NOT NULL,
                S1 REAL,
                ST REAL,
                S2 REAL,
                method TEXT NOT NULL,
                analysis_parameters BLOB,
                FOREIGN KEY(problem_id) REFERENCES Problems(problem_id),
                FOREIGN KEY(coeff_id) REFERENCES Coefficients(coeff_id),
                FOREIGN KEY(response_id) REFERENCES ResponseVariables(response_id)
            )
        ''')

        # Commit changes to the database
        self.conn.commit()

    def close(self):
        """Close the database connection."""
        if self.conn:
            self.conn.close()

    # Methods for inserting data
    def insert_coefficients(self, coefficient_names: List[str]):
        """
        Insert coefficients into the Coefficients table.

        Args:
            coefficient_names (List[str]): List of coefficient names.
        """
        self.connect()
        for name in coefficient_names:
            try:
                self.cursor.execute('''
                    INSERT OR IGNORE INTO Coefficients (name)
                    VALUES (?)
                ''', (name,))
            except sqlite3.Error as e:
                print(f"An error occurred while inserting coefficient '{name}': {e}")
        self.conn.commit()
        self.close()

    def insert_problem(self, filename: str, user_diet: Any, animal_input: Any,
                   equation_selection: Any, infusion_input: Any,
                   problem: Dict[str, Tuple[float, float]]) -> int:
        """
        Insert a new problem into the Problems table.

        Args:
            filename (str): Name of the input file used.
            user_diet (Any): Data structure representing user diet.
            animal_input (Any): Data structure representing animal input.
            equation_selection (Any): Data structure representing equation selection.
            infusion_input (Any): Data structure representing infusion input.
            problem (Dict[str, Tuple[float, float]]): Coefficients and ranges used.

        Returns:
            int: The problem_id of the newly inserted problem.
        """
        self.connect()
        date_run = datetime.datetime.now()
        # Serialize the inputs and problem
        user_diet_blob = pickle.dumps(user_diet)
        animal_input_blob = pickle.dumps(animal_input)
        equation_selection_blob = pickle.dumps(equation_selection)
        infusion_input_blob = pickle.dumps(infusion_input)
        problem_blob = pickle.dumps(problem)

        self.cursor.execute('''
            INSERT INTO Problems (
                date_run, filename, user_diet, animal_input,
                equation_selection, infusion_input, problem
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            date_run, filename, user_diet_blob, animal_input_blob,
            equation_selection_blob, infusion_input_blob,
            problem_blob
        ))

        self.conn.commit()
        problem_id = self.cursor.lastrowid
        self.close()
        return problem_id

    def insert_response_variables(self, problem_id: int, sample_id: int, response_variables: Dict[str, Any]):
        """
        Insert response variables into the ResponseVariables table.

        Args:
            problem_id (int): The problem_id associated with these response variables.
            sample_id (int): The sample_id associated with these response variables.
            response_variables (List[Dict[str, Any]]): A list of dictionaries containing response variable data.
        """
        self.connect()
        variable_columns = RESPONSE_VARIABLE_NAMES
        columns = ['problem_id', 'sample_id'] + variable_columns
        placeholders = ', '.join(['?'] * len(columns))
        sql = f'''
            INSERT INTO ResponseVariables (
                {', '.join(columns)}
            ) VALUES ({placeholders})
        '''
        values = [problem_id, sample_id] + [response_variables.get(col) for col in variable_columns]
        self.cursor.execute(sql, values)
        self.conn.commit()
        self.close()

    def insert_sample(self, problem_id: int, sample_index: int, parameter_values: Dict[str, float],
                    result_file_path: Optional[str] = None) -> int:
        """
        Insert a sample into the Samples table.

        Args:
            problem_id (int): The problem_id associated with this sample.
            sample_index (int): The index of the sample (from enumerate).
            parameter_values (Dict[str, float]): The parameter values used in this sample.
            result_file_path (Optional[str]): File path to the JSON file with the full model output.

        Returns:
            int: The sample_id of the newly inserted sample.
        """
        self.connect()
        parameter_values_blob = pickle.dumps(parameter_values)

        self.cursor.execute('''
            INSERT INTO Samples (
                problem_id, sample_index, parameter_values, result_file_path
            )
            VALUES (?, ?, ?, ?)
        ''', (
            problem_id, sample_index, parameter_values_blob, result_file_path
        ))

        self.conn.commit()
        sample_id = self.cursor.lastrowid
        self.close()
        return sample_id
    
    # Methods to query database
    def get_all_problems(self) -> pd.DataFrame:
        """
        Retrieve all problems in the database.

        Returns:
            pd.DataFrame: A DataFrame containing problem details.
        """
        self.connect()
        df = pd.read_sql_query('''
            SELECT problem_id, date_run, filename
            FROM Problems
            ORDER BY date_run DESC
        ''', self.conn)
        self.close()
        return df

    def get_samples_for_problem(self, problem_id: int) -> pd.DataFrame:
        """
        Retrieve all samples for a specific problem.

        Args:
            problem_id (int): The ID of the problem.

        Returns:
            pd.DataFrame: A DataFrame containing sample details and parameter values.
        """
        self.connect()
        df = pd.read_sql_query('''
            SELECT sample_id, sample_index, parameter_values
            FROM Samples
            WHERE problem_id = ?
            ORDER BY sample_index
        ''', self.conn, params=(problem_id,))
        # Deserialize parameter_values
        df['parameter_values'] = df['parameter_values'].apply(pickle.loads)
        # Expand parameter_values dict into columns
        parameters_df = pd.DataFrame(df['parameter_values'].tolist(), index=df.index)
        df = df.drop(columns=['parameter_values']).join(parameters_df)
        self.close()
        return df

    def get_problem_details(self, problem_id: int) -> pd.DataFrame:
        """
        Retrieve detailed information about a specific problem.

        Args:
            problem_id (int): The ID of the problem.

        Returns:
            pd.DataFrame: A DataFrame containing problem details.
        """
        self.connect()
        df = pd.read_sql_query('''
            SELECT *
            FROM Problems
            WHERE problem_id = ?
        ''', self.conn, params=(problem_id,))
        self.close()

        pickled_columns = ['user_diet', 'animal_input', 'equation_selection', 'infusion_input', 'problem']
        for col in pickled_columns:
            df[col] = df[col].apply(pickle.loads)

        return df

    def get_response_variables(self, problem_id: int, variable_names: List[str]) -> pd.DataFrame:
        """
        Retrieve multiple response variables for all samples in a problem.

        Args:
            problem_id (int): The ID of the problem.
            variable_names (List[str]): List of variable names to retrieve.

        Returns:
            pd.DataFrame: A DataFrame containing sample_index and the requested variables.
        """
        self.connect()
        if isinstance(variable_names, str):
            variable_names = [variable_names]
        # Validate variable names
        cursor = self.conn.cursor()
        cursor.execute('PRAGMA table_info(ResponseVariables)')
        columns_info = cursor.fetchall()
        column_names = [info[1] for info in columns_info]
        non_variable_columns = ['response_id', 'problem_id', 'sample_id']
        valid_variable_names = [col for col in column_names if col not in non_variable_columns]
        for var in variable_names:
            if var not in valid_variable_names:
                self.close()
                raise ValueError(f"Variable '{var}' not found in ResponseVariables table.")
        sql = f'''
            SELECT rv.sample_id, s.sample_index, {', '.join(['rv.' + var for var in variable_names])}
            FROM ResponseVariables rv
            JOIN Samples s ON rv.sample_id = s.sample_id
            WHERE rv.problem_id = ?
            ORDER BY s.sample_index
        '''
        df = pd.read_sql_query(sql, self.conn, params=(problem_id,))
        self.close()
        return df

    def get_response_variable_summary(self, problem_id: int) -> pd.DataFrame:
        """
        Provide summary statistics for all response variables in a problem.

        Args:
            problem_id (int): The ID of the problem.

        Returns:
            pd.DataFrame: A DataFrame containing summary statistics for each variable.
        """
        self.connect()
        # Retrieve all response variables for the problem
        df = pd.read_sql_query('''
            SELECT *
            FROM ResponseVariables
            WHERE problem_id = ?
        ''', self.conn, params=(problem_id,))
        self.close()
        # Drop non-variable columns
        df = df.drop(columns=['response_id', 'problem_id', 'sample_id'])
        # Compute summary statistics
        summary_df = df.describe().transpose()
        return summary_df

    def list_response_variables(self) -> List[str]:
        """
        List all response variables recorded in the ResponseVariables table.

        Returns:
            List[str]: A list of response variable names.
        """
        self.connect()
        cursor = self.conn.cursor()
        cursor.execute('PRAGMA table_info(ResponseVariables)')
        columns_info = cursor.fetchall()
        column_names = [info[1] for info in columns_info]
        # Exclude non-variable columns
        non_variable_columns = ['response_id', 'problem_id', 'sample_id']
        variable_names = [col for col in column_names if col not in non_variable_columns]
        self.close()
        return variable_names
        