import importlib.resources

import pandas as pd
import pytest

import nasem_dairy as nd
from nasem_dairy.model.input_validation import validate_feed_library_df

path_to_package_data = importlib.resources.files("nasem_dairy.data")
feed_library_in = pd.read_csv(
    path_to_package_data.joinpath("feed_library/NASEM_feed_library.csv")
)

def create_minimal_valid_user_diet():
    return pd.DataFrame({
        "Feedstuff": ["Barley hay", "Canola meal"],
        "kg_user": [5, 3]
    })


def test_not_a_dataframe():
    with pytest.raises(TypeError, match="feed_library must be a DataFrame"):
        validate_feed_library_df(["not", "a", "dataframe"], pd.DataFrame())


def test_wrong_columns():
    feed_library = pd.DataFrame(columns=["Wrong", "Columns"])
    user_diet = create_minimal_valid_user_diet()
    with pytest.raises(KeyError, match="The following keys are missing: "):
        validate_feed_library_df(feed_library, user_diet)


def test_missing_feeds():
    feed_library = feed_library_in.copy()
    user_diet = pd.DataFrame({"Feedstuff": ["Feed1", "Feed3"]})
    with pytest.raises(ValueError, match="The following feeds are missing in the feed library:"):
        validate_feed_library_df(feed_library, user_diet)


def test_valid_input():
    feed_library = feed_library_in.copy()
    user_diet = create_minimal_valid_user_diet()
    result = validate_feed_library_df(feed_library, user_diet)
    pd.testing.assert_frame_equal(result, feed_library)
    