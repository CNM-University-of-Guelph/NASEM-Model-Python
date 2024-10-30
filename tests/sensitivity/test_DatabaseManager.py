import datetime
import pickle
import pytest
import tempfile
import sqlite3

import pandas as pd

from nasem_dairy.sensitivity.DatabaseManager import DatabaseManager
from nasem_dairy.sensitivity.response_variables_config import RESPONSE_VARIABLE_NAMES

EXPECTED_SCHEMAS = {
    'Coefficients': [
        ('coeff_id', 'INTEGER', 0, None, 1),
        ('name', 'TEXT', 1, None, 0),
    ],
    'Problems': [
        ('problem_id', 'INTEGER', 0, None, 1),
        ('date_run', 'DATETIME', 1, None, 0),
        ('filename', 'TEXT', 1, None, 0),
        ('user_diet', 'BLOB', 1, None, 0),
        ('animal_input', 'BLOB', 1, None, 0),
        ('equation_selection', 'BLOB', 1, None, 0),
        ('infusion_input', 'BLOB', 1, None, 0),
        ('problem', 'BLOB', 1, None, 0),
    ],
    'ProblemCoefficients': [
        ('problem_id', 'INTEGER', 1, None, 1),
        ('coeff_id', 'INTEGER', 1, None, 2),
    ],
    'Samples': [
        ('sample_id', 'INTEGER', 0, None, 1),
        ('problem_id', 'INTEGER', 1, None, 0),
        ('sample_index', 'INTEGER', 1, None, 0),
        ('parameter_values', 'BLOB', 1, None, 0),
        ('result_file_path', 'TEXT', 0, None, 0),
    ],
    'ResponseVariables': [
        ('response_id', 'INTEGER', 0, None, 1),
        ('problem_id', 'INTEGER', 1, None, 0),
        ('sample_id', 'INTEGER', 1, None, 0),
    ] + [(var, 'REAL', 0, None, 0) for var in RESPONSE_VARIABLE_NAMES],
    'Results': [
        ('result_id', 'INTEGER', 0, None, 1),
        ('problem_id', 'INTEGER', 1, None, 0),
        ('response_variable', 'TEXT', 1, None, 0),
        ('S1', 'BLOB', 0, None, 0),
        ('ST', 'BLOB', 0, None, 0),
        ('S2', 'BLOB', 0, None, 0),
        ('S1_conf', 'BLOB', 0, None, 0),
        ('ST_conf', 'BLOB', 0, None, 0),
        ('S2_conf', 'BLOB', 0, None, 0),
        ('method', 'TEXT', 1, None, 0),
        ('analysis_parameters', 'BLOB', 0, None, 0),
    ],
}

@pytest.fixture
def temp_db():
    with tempfile.TemporaryDirectory() as temp_dir:
        db_path = f"{temp_dir}/test.db"
        db_manager = DatabaseManager(db_path)
        yield db_manager


def test_create_tables(temp_db):
    conn = sqlite3.connect(temp_db.db_path)
    cursor = conn.cursor()

    expected_tables = EXPECTED_SCHEMAS.keys()

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row[0] for row in cursor.fetchall()]

    for table in expected_tables:
        assert table in tables, f"Table {table} was not created"

    for table, expected_schema in EXPECTED_SCHEMAS.items():
        cursor.execute(f"PRAGMA table_info({table});")
        schema_info = cursor.fetchall()
        actual_schema = [
            (col[1], col[2], col[3], col[4], col[5]) for col in schema_info
            ]
        assert actual_schema == expected_schema, f"Schema for {table} is incorrect."
        
    conn.close()


def test_insert_coefficients(temp_db):
    coefficient_names = ["Coeff_1", "Coeff_2", "Coeff_3"]
    temp_db.insert_coefficients(coefficient_names)
    conn = sqlite3.connect(temp_db.db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT name FROM Coefficients")
    results = [row[0] for row in cursor.fetchall()]
    assert set(results) == set(coefficient_names), "Coefficients were not inserted correctly."

    conn.close()


def test_insert_problem(temp_db):
    filename = "test_file.txt"
    user_diet = {"corn silage": 15.5, "soybean meal": 22.1}
    animal_input = {"weight": 650, "age": 3}
    equation_selection = {"method": "A", "parameters": [1, 2, 3]}
    infusion_input = {"infusion_rate": 0.5}
    problem = {"var1": (0.0, 1.0)}
    coefficient_names = ["Coeff_1", "Coeff_2"]

    problem_id = temp_db.insert_problem(
        filename, user_diet, animal_input, equation_selection,
        infusion_input, problem, coefficient_names
    )

    conn = sqlite3.connect(temp_db.db_path)
    cursor = conn.cursor()

    # Verify that problem is inserted
    cursor.execute("SELECT * FROM Problems WHERE problem_id = ?", (problem_id,))
    row = cursor.fetchone()

    assert row is not None, "Problem was not inserted correctly."

    # Verify each field in the Problems table
    (date_run, db_filename, db_user_diet, db_animal_input, 
    db_equation_selection, db_infusion_input, db_problem) = row[1:8]
    
    assert db_filename == filename, "Filename is incorrect."
    
    # Verify serialization/deserialization
    assert pickle.loads(db_user_diet) == user_diet, "User diet is not correctly deserialized."
    assert pickle.loads(db_animal_input) == animal_input, "Animal input is not correctly deserialized."
    assert pickle.loads(db_equation_selection) == equation_selection, "Equation selection is not correctly deserialized."
    assert pickle.loads(db_infusion_input) == infusion_input, "Infusion input is not correctly deserialized."
    assert pickle.loads(db_problem) == problem, "Problem is not correctly deserialized."
    
    # Verify date_run (tolerance of 1 minute)
    assert isinstance(date_run, str), "date_run should be a string."
    date_run = datetime.datetime.strptime(date_run, '%Y-%m-%d %H:%M:%S.%f')
    assert abs((datetime.datetime.now() - date_run).total_seconds()) < 60, "date_run is incorrect."

    # Verify coefficients are inserted in the Coefficients table
    cursor.execute("SELECT name FROM Coefficients")
    coeff_results = [row[0] for row in cursor.fetchall()]
    for coeff in coefficient_names:
        assert coeff in coeff_results, f"Coefficient '{coeff}' was not inserted."

    # Verify problem-coefficient linking
    cursor.execute("SELECT coeff_id FROM ProblemCoefficients WHERE problem_id = ?", (problem_id,))
    coeff_ids = [row[0] for row in cursor.fetchall()]
   
    # Check that all linked coefficients exist in the Coefficients table
    cursor.execute("SELECT coeff_id FROM Coefficients WHERE name IN (?, ?)", coefficient_names)
    expected_coeff_ids = [row[0] for row in cursor.fetchall()]
    assert set(coeff_ids) == set(expected_coeff_ids), "Problem-Coefficient linking is incorrect."

    conn.close()


def test_insert_response_variables(temp_db):
    problem_id = 1
    sample_id = 1
    response_variables = {var: i for i, var in enumerate(RESPONSE_VARIABLE_NAMES)}

    temp_db.insert_response_variables(problem_id, sample_id, response_variables)

    conn = sqlite3.connect(temp_db.db_path)
    cursor = conn.cursor()

    # Verify that response variables are inserted
    cursor.execute(
        "SELECT * FROM ResponseVariables WHERE problem_id = ? AND sample_id = ?", 
        (problem_id, sample_id)
        )
    row = cursor.fetchone()
    assert row is not None, "Response variables were not inserted."
    
    # Verify problem_id and sample_id fields
    assert row[1] == problem_id, "problem_id is incorrect."
    assert row[2] == sample_id, "sample_id is incorrect."

    # Check each response variable's value
    for i, var in enumerate(RESPONSE_VARIABLE_NAMES, start=3): 
        assert row[i] == i - 3, f"Value for {var} is incorrect."

    conn.close()


def test_insert_sample(temp_db):
    problem_id = 1
    sample_index = 0
    parameter_values = {"param1": 0.1, "param2": 0.2}
    result_file_path = "results.json"

    sample_id = temp_db.insert_sample(
        problem_id, sample_index, parameter_values, result_file_path
        )

    conn = sqlite3.connect(temp_db.db_path)
    cursor = conn.cursor()

    # Verify that sample is inserted
    cursor.execute(
        "SELECT * FROM Samples WHERE sample_id = ?", 
        (sample_id,)
        )
    row = cursor.fetchone()
    assert row is not None, "Sample was not inserted."
    assert row[1] == problem_id, "Problem ID is incorrect."
    assert row[2] == sample_index, "Sample index is incorrect."
    assert row[4] == result_file_path, "Result file path is incorrect."

    # Check serialization/deserialization of parameter_values
    stored_parameter_values = pickle.loads(row[3])
    assert stored_parameter_values == parameter_values, "Parameter values are not correctly serialized or deserialized."

    # Insert another sample with result_file_path set to None
    parameter_values_2 = {"param3": 0.3, "param4": 0.4}
    sample_id_2 = temp_db.insert_sample(
        problem_id, sample_index + 1, parameter_values_2, None
    )

    # Verify that sample is inserted with result_file_path = None
    cursor.execute(
        "SELECT * FROM Samples WHERE sample_id = ?", 
        (sample_id_2,)
    )
    row = cursor.fetchone()

    assert row is not None, "Sample with None result_file_path was not inserted."
    assert row[1] == problem_id, "Problem ID for second sample is incorrect."
    assert row[2] == sample_index + 1, "Sample index for second sample is incorrect."
    assert row[4] is None, "Result file path should be None."

    # Check serialization/deserialization of parameter_values for the second sample
    stored_parameter_values_2 = pickle.loads(row[3])
    assert stored_parameter_values_2 == parameter_values_2, "Parameter values for the second sample are not correctly serialized or deserialized."

    conn.close()


def test_insert_results(temp_db):
    problem_id = 1
    response_variable = "Mlk_Prod"
    method = "Sobol"
    analysis_parameters = pickle.dumps({"param": "value"})
    results_data = {
        'S1': pickle.dumps([0.1, 0.2, 0.3]),
        'ST': pickle.dumps([0.4, 0.5, 0.6]),
        'S2': pickle.dumps([0.7, 0.8, 0.9]),
        'S1_conf': pickle.dumps([0.01, 0.02, 0.03]),
        'ST_conf': pickle.dumps([0.04, 0.05, 0.06]),
        'S2_conf': pickle.dumps([0.07, 0.08, 0.09]),
    }

    temp_db.insert_results(
        problem_id, response_variable, method, analysis_parameters, 
        **results_data
        )

    conn = sqlite3.connect(temp_db.db_path)
    cursor = conn.cursor()

    # Verify that results are inserted
    cursor.execute(
        "SELECT * FROM Results WHERE problem_id = ? AND response_variable = ?", 
        (problem_id, response_variable)
        )
    row = cursor.fetchone()

    assert row is not None, "Results were not inserted."
    assert row[1] == problem_id, "Problem ID is incorrect."
    assert row[2] == response_variable, "Response variable is incorrect."
    assert row[9] == method, "Method is incorrect."

    # Check serialization/deserialization of result arrays
    assert pickle.loads(row[3]) == [0.1, 0.2, 0.3], "S1 data is incorrect."
    assert pickle.loads(row[4]) == [0.4, 0.5, 0.6], "ST data is incorrect."
    assert pickle.loads(row[5]) == [0.7, 0.8, 0.9], "S2 data is incorrect."
    assert pickle.loads(row[6]) == [0.01, 0.02, 0.03], "S1_conf data is incorrect."
    assert pickle.loads(row[7]) == [0.04, 0.05, 0.06], "ST_conf data is incorrect."
    assert pickle.loads(row[8]) == [0.07, 0.08, 0.09], "S2_conf data is incorrect."
    assert pickle.loads(row[10]) == {"param": "value"}, "Analysis parameters are incorrect."

    conn.close()


def test_get_all_problems(temp_db):
    temp_db.insert_problem(
        "test_file1.txt", {"diet": 1}, {"animal": 1}, {"eq": 1}, {"infusion": 1},
        {"prob": 1}, ["Coeff_1"]
    )
    temp_db.insert_problem(
        "test_file2.txt", {"diet": 2}, {"animal": 2}, {"eq": 2}, {"infusion": 2},
        {"prob": 2}, ["Coeff_2"]
    )

    df = temp_db.get_all_problems()

    assert len(df) == 2, "Number of problems retrieved is incorrect."
    assert set(df['filename']) == {
        "test_file1.txt", "test_file2.txt"
        }, "Problem filenames are incorrect."


def test_get_samples_for_problem(temp_db):
    problem_id = temp_db.insert_problem(
        "test_file.txt", {"diet": 1}, {"animal": 1}, {"eq": 1}, {"infusion": 1},
        {"prob": 1}, ["Coeff_1"]
    )
    sample_id = temp_db.insert_sample(problem_id, 0, {"param1": 0.1})

    df = temp_db.get_samples_for_problem(problem_id)

    # Verify results
    assert len(df) == 1, "Number of samples retrieved is incorrect."
    assert df.loc[0, 'sample_id'] == sample_id, "Sample ID is incorrect."
    assert df.loc[0, 'param1'] == 0.1, "Parameter value is incorrect."


def test_get_problem_details(temp_db):
    problem_id = temp_db.insert_problem(
        "test_file.txt", {"diet": 1}, {"animal": 1}, {"eq": 1}, {"infusion": 1},
        {"prob": 1}, ["Coeff_1"]
    )

    df = temp_db.get_problem_details(problem_id)

    assert len(df) == 1, "Problem details retrieval failed."
    assert df.loc[0, 'filename'] == "test_file.txt", "Problem filename is incorrect."


def test_get_response_variables(temp_db):
    problem_id = temp_db.insert_problem(
        "test_file.txt", {"diet": 1}, {"animal": 1}, {"eq": 1}, {"infusion": 1},
        {"prob": 1}, ["Coeff_1"]
    )
    sample_id = temp_db.insert_sample(problem_id, 0, {"param1": 0.1})
    temp_db.insert_response_variables(problem_id, sample_id, {"Mlk_Prod": 10.0})

    df = temp_db.get_response_variables(problem_id, ["Mlk_Prod"])

    assert len(df) == 1, "Number of response variables retrieved is incorrect."
    assert df.loc[0, 'Mlk_Prod'] == 10.0, "Response variable value is incorrect."


def test_get_response_variable_summary(temp_db):
    problem_id = temp_db.insert_problem(
        "test_file.txt", {"diet": 1}, {"animal": 1}, {"eq": 1}, {"infusion": 1},
        {"prob": 1}, ["Coeff_1"]
    )
    sample_id = temp_db.insert_sample(problem_id, 0, {"param1": 0.1})
    temp_db.insert_response_variables(problem_id, sample_id, {"Mlk_Prod": 10.0, "Mlk_Fat_g": 5.0})

    summary_df = temp_db.get_response_variable_summary(problem_id)

    assert "mean" in summary_df.columns, "Summary statistics failed."
    assert summary_df.loc['Mlk_Prod', 'mean'] == 10.0, "Mean value for Mlk_Prod is incorrect."


def test_list_response_variables(temp_db):
    problem_id = temp_db.insert_problem(
        "test_file.txt", {"diet": 1}, {"animal": 1}, {"eq": 1}, {"infusion": 1},
        {"prob": 1}, ["Coeff_1"]
    )
    sample_id = temp_db.insert_sample(problem_id, 0, {"param1": 0.1})
    temp_db.insert_response_variables(problem_id, sample_id, {"Mlk_Prod": 10.0})

    variables = temp_db.list_response_variables()

    assert "Mlk_Prod" in variables, "Response variable not listed."


def test_get_problems_by_coefficient(temp_db):
    temp_db.insert_problem(
        "test_file1.txt", {"diet": 1}, {"animal": 1}, {"eq": 1}, {"infusion": 1},
        {"prob": 1}, ["Coeff_1"]
    )

    df = temp_db.get_problems_by_coefficient("Coeff_1")

    assert len(df) == 1, "Number of problems by coefficient is incorrect."
    assert df.loc[0, 'filename'] == "test_file1.txt", "Problem filename is incorrect."


def test_get_coefficients_by_problem(temp_db):
    problem_id = temp_db.insert_problem(
        "test_file.txt", {"diet": 1}, {"animal": 1}, {"eq": 1}, {"infusion": 1},
        {"prob": 1}, ["Coeff_1"]
    )

    df = temp_db.get_coefficients_by_problem(problem_id)

    assert len(df) == 1, "Number of coefficients by problem is incorrect."
    assert df.loc[0, 'name'] == "Coeff_1", "Coefficient name is incorrect."
