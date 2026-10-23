import numpy as np
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


def build_pipeline(X):
    """Preprocessing + model in one Pipeline, so nothing leaks from test data."""
    num_cols = X.select_dtypes(include="number").columns.tolist()
    cat_cols = X.select_dtypes(exclude="number").columns.tolist()

    pre = ColumnTransformer([
        ("num", StandardScaler(), num_cols),
        ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), cat_cols),
    ])
    return Pipeline([
        ("pre", pre),
        ("model", RandomForestRegressor(n_estimators=300, random_state=42)),
    ])


def evaluate_model(pipe, X_test, y_test):
    """Return MAE, RMSE and R2 for a fitted model."""
    pred = pipe.predict(X_test)
    return {
        "MAE": round(float(mean_absolute_error(y_test, pred)), 3),
        "RMSE": round(float(np.sqrt(mean_squared_error(y_test, pred))), 3),
        "R2": round(float(r2_score(y_test, pred)), 3),
    }