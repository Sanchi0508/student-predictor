import pandas as pd
import pytest

from src.data import clean_data, split_features_target, validate_data


def make_df():
    return pd.DataFrame({
        "school": ["GP", "MS"], "sex": ["F", "M"], "age": [16, 17],
        "studytime": [2, 3], "failures": [0, 1], "absences": [2, 5],
        "G1": [10, 12], "G2": [11, 13], "G3": [12, 14],
    })


def test_valid_data_passes():
    assert validate_data(make_df()) is not None


def test_negative_absences_fails():
    df = make_df()
    df.loc[0, "absences"] = -1
    with pytest.raises(ValueError):
        validate_data(df)


def test_bad_grade_fails():
    df = make_df()
    df.loc[0, "G3"] = 25
    with pytest.raises(ValueError):
        validate_data(df)


def test_missing_column_fails():
    with pytest.raises(ValueError):
        validate_data(make_df().drop(columns=["failures"]))


def test_leakage_columns_dropped():
    X, y = split_features_target(make_df())
    assert "G3" not in X.columns
    assert "G1" not in X.columns
    assert "G2" not in X.columns


def test_clean_fills_missing():
    df = make_df()
    df.loc[0, "age"] = None
    assert clean_data(df)["age"].isnull().sum() == 0