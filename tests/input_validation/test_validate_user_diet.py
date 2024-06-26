import pandas as pd
import pytest

from nasem_dairy.ration_balancer.input_validation import validate_user_diet

def test_wrong_column_names():
    data = {
        "WrongName1": ["corn", "soybean"],
        "WrongName2": [10, 5]
    }
    df = pd.DataFrame(data)
    with pytest.raises(ValueError, match="user_diet must have the columns"):
        validate_user_diet(df)


def test_duplicate_feedstuff():
    data = {
        "Feedstuff": ["corn", "soybean", "corn"],
        "kg_user": [10, 5, 15]
    }
    df = pd.DataFrame(data)
    result = validate_user_diet(df)
    expected_data = {
        "Feedstuff": ["corn", "soybean"],
        "kg_user": [25, 5]
    }
    expected_df = pd.DataFrame(expected_data)
    pd.testing.assert_frame_equal(result, expected_df)


def test_missing_kg_user():
    data = {
        "Feedstuff": ["corn", "soybean"],
        "kg_user": [None, 5]
    }
    df = pd.DataFrame(data)
    with pytest.raises(ValueError, match="kg_user column must contain only numeric values"):
        validate_user_diet(df)


def test_missing_feedstuff():
    data = {
        "Feedstuff": ["corn", None],
        "kg_user": [5, 5]
    }
    df = pd.DataFrame(data)
    with pytest.raises(ValueError, match="Feedstuff column must contain only string values"):
        validate_user_diet(df)


def test_empty_dataframe():
    data = {
        "Feedstuff": [],
        "kg_user": []
    }
    df = pd.DataFrame(data)
    with pytest.raises(ValueError, match="user_diet is an empty DataFrame"):
        validate_user_diet(df)


def test_no_issues():
    data = {
        "Feedstuff": ["corn", "soybean"],
        "kg_user": [10, 5]
    }
    df = pd.DataFrame(data)
    result = validate_user_diet(df)
    expected_data = {
        "Feedstuff": ["corn", "soybean"],
        "kg_user": [10, 5]
    }
    expected_df = pd.DataFrame(expected_data)
    pd.testing.assert_frame_equal(result, expected_df)
