import io

import numpy as np
import pandas as pd
import streamlit as st
from sklearn.model_selection import train_test_split

from src.artifacts import load_all
from src.auth import require_role
from src.data import clean_data, load_data, split_features_target
from src.db import list_users
from src.drift import drift_report
from src.fairness import gap_warning, group_report
from src.model import evaluate_model

st.set_page_config(page_title="Admin Monitoring", page_icon="🛡️", layout="wide")
user = require_role("admin")

st.title("🛡️ Admin Monitoring")
st.caption("Model quality, fairness and data drift. Admin only.")

model, meta, explainer = load_all()


@st.cache_data
def get_split():
    df = clean_data(load_data("data/student-mat.csv"))
    X, y = split_features_target(df)
    return train_test_split(X, y, test_size=0.2, random_state=42)


X_train, X_test, y_train, y_test = get_split()

# ---------- 1. Model performance ----------
st.subheader("1. Model performance (held-out test set)")
scores = evaluate_model(model, X_test, y_test)
c1, c2, c3, c4 = st.columns(4)
c1.metric("MAE", scores["MAE"])
c2.metric("RMSE", scores["RMSE"])
c3.metric("R²", scores["R2"])
c4.metric("Test students", len(X_test))
st.caption("A student counts as flagged when the predicted grade is below 11.5 "
           "(Medium or High risk).")

# ---------- 2. Fairness ----------
st.subheader("2. Fairness check")
st.caption("Compares errors across groups. The test set is small (about 79 "
           "students), so small gaps are not proof of bias.")
for column in ["sex", "school", "address"]:
    report = group_report(model, X_test, y_test, column)
    st.write(f"**By {column}**")
    st.dataframe(report, use_container_width=True, hide_index=True)
    warn = gap_warning(report)
    if warn:
        st.warning(warn)
    else:
        st.success("No large accuracy gap found between these groups.")

# ---------- 3. Drift ----------
st.subheader("3. Data drift check")
st.caption("Upload a new class CSV to compare it with the training data. "
           "PSI below 0.10 is stable, 0.10 to 0.25 is watch, above 0.25 is drift.")
file = st.file_uploader("Upload a class CSV", type="csv")

if file is not None:
    try:
        text = file.getvalue().decode("utf-8-sig")
        first_line = text.splitlines()[0]
        sep = ";" if first_line.count(";") > first_line.count(",") else ","
        new = clean_data(pd.read_csv(io.StringIO(text), sep=sep))
        missing = [c for c in meta["columns"] if c not in new.columns]
        if missing:
            st.error(f"Missing columns: {missing}")
        else:
            rep = drift_report(X_train, new[meta["columns"]], meta["columns"])
            n_drift = int((rep["status"] == "drift").sum())
            n_watch = int((rep["status"] == "watch").sum())
            m1, m2 = st.columns(2)
            m1.metric("Features with drift", n_drift)
            m2.metric("Features to watch", n_watch)
            if n_drift:
                st.error("This class looks different from the training data. "
                         "Predictions may be less reliable. Consider retraining "
                         "on your own college data.")
            elif n_watch:
                st.warning("Some features are shifting. Keep an eye on them.")
            else:
                st.success("This class looks similar to the training data.")
            st.dataframe(rep, use_container_width=True, hide_index=True)
    except Exception as e:
        st.error(f"Could not process the file: {e}")

# ---------- 4. Users ----------
st.subheader("4. Users")
users = list_users()
st.dataframe(
    pd.DataFrame(users, columns=["username", "role", "full_name", "created_at"]),
    use_container_width=True, hide_index=True)