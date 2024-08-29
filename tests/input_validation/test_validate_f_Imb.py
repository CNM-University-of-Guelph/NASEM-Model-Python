import pandas as pd
import pytest

from nasem_dairy.model.input_validation import validate_f_Imb

def test_not_a_series():
    with pytest.raises(TypeError, match="f_Imb must be a Series"):
        validate_f_Imb("not a series")


def test_incorrect_index():
    incorrect_index_series = pd.Series(
        [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0],
        index=[
            'Arg', 'His', 'Ile', 'Leu', 'Lys', 'Met', 
            'Phe', 'Thr', 'Trp', 'Invalid'
            ])
    with pytest.raises(KeyError, match="The following keys are missing: "):
        validate_f_Imb(incorrect_index_series)


def test_non_numeric_values():
    non_numeric_series = pd.Series(
        [1.0, 1.0, 1.0, 1.0, 'non-numeric', 1.0, 1.0, 1.0, 1.0, 1.0],
        index=[
            'Arg', 'His', 'Ile', 'Leu', 'Lys', 'Met', 'Phe', 'Thr', 'Trp', 'Val'
            ])
    with pytest.raises(
        TypeError, match="All values in f_Imb must be int or float"
        ):
        validate_f_Imb(non_numeric_series)


def test_valid_series():
    valid_series = pd.Series(
        [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0],
        index=[
            'Arg', 'His', 'Ile', 'Leu', 'Lys', 'Met', 'Phe', 'Thr', 'Trp', 'Val'
            ])
    result = validate_f_Imb(valid_series)
    assert result.equals(valid_series)
