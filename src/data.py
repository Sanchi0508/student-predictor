import pandas as pd

REQUIRED_COLS = {"school", "sex", "age", "studytime", "failures",
                 "absences", "G1", "G2", "G3"}


def load_data(path):
    """Read the CSV (this dataset uses ; as the separator)."""
    return pd.read_csv(path, sep=";")


def clean_data(df):
    """Remove duplicates, trim text, fill missing values."""
    df = df.drop_duplicates().copy()
    df.columns = df.columns.str.strip()

    num_cols = df.select_dtypes(include="number").columns
    text_cols = df.select_dtypes(exclude="number").columns

    for col in num_cols:
        df[col] = df[col].fillna(df[col].median())
    for col in text_cols:
        df[col] = df[col].astype(str).str.strip()
    return df


def validate_data(df):
    """Raise a clear error if the data is not valid."""
    missing = REQUIRED_COLS - set(df.columns)
    if missing:
        raise ValueError(f"Missing columns: {missing}")
    if not df["G3"].between(0, 20).all():
        raise ValueError("G3 must be between 0 and 20")
    if not (df["absences"] >= 0).all():
        raise ValueError("absences cannot be negative")
    if not df["studytime"].between(1, 4).all():
        raise ValueError("studytime must be 1 to 4")
    if not df["age"].between(10, 30).all():
        raise ValueError("age out of range")
    return df


def split_features_target(df, drop_cols=("G1", "G2")):
    """Return X (inputs) and y (final grade), dropping leaky columns."""
    X = df.drop(columns=["G3", *drop_cols])
    y = df["G3"]
    return X, y