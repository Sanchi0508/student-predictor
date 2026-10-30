import io
import joblib
import pandas as pd
import streamlit as st
import joblib
import pandas as pd
import streamlit as st
from src.explain import get_explainer, top_reasons

st.set_page_config(page_title="Student Performance Predictor", page_icon="🎓")
st.title("🎓 Student Performance Predictor")
st.caption("Predicts the final grade (0 to 20) from background and study habits.")


@st.cache_resource
def load_artifacts():
    model = joblib.load("models/model.joblib")
    meta = joblib.load("models/meta.joblib")
    return model, meta


model, meta = load_artifacts()


@st.cache_resource
def load_explainer(_model):
    return get_explainer(_model)


explainer = load_explainer(model)

defaults = meta["defaults"]

st.subheader("Student details")
c1, c2 = st.columns(2)

with c1:
    age = st.slider("Age", 15, 22, 17)
    sex = st.selectbox("Sex", ["F", "M"])
    studytime = st.selectbox(
        "Weekly study time (1: <2h, 2: 2-5h, 3: 5-10h, 4: >10h)",
        [1, 2, 3, 4], index=1)
    failures = st.number_input("Past class failures", 0, 4, 0)

with c2:
    absences = st.number_input("Absences", 0, 93, 4)
    higher = st.selectbox("Wants higher education", ["yes", "no"])
    internet = st.selectbox("Internet at home", ["yes", "no"])
    goout = st.slider("Going out with friends (1 to 5)", 1, 5, 3)

if st.button("Predict", type="primary"):
    # Start with default values for fields that are not on the form
    row = dict(defaults)
    row.update({
        "age": age, "sex": sex, "studytime": studytime,
        "failures": failures, "absences": absences,
        "higher": higher, "internet": internet, "goout": goout,
    })

    # Same column order as in training
    row_df = pd.DataFrame([row])[meta["columns"]]

    pred = float(model.predict(row_df)[0])
    pred = max(0.0, min(20.0, pred))

    st.metric("Predicted final grade (0 to 20)", f"{pred:.1f}")
    if pred >= 10:
        st.success("Likely to pass ✅")
    else:
        st.error("At risk ⚠️")

from src.data import clean_data, validate_data

st.divider()
st.subheader("Batch prediction (upload a whole class)")
st.caption("Upload a CSV with the same columns as the training data. "
           "Semicolon or comma separated both work.")

file = st.file_uploader("Upload CSV", type="csv")

if file is not None:
    try:
        text = file.getvalue().decode("utf-8-sig")
        first_line = text.splitlines()[0]
        sep = ";" if first_line.count(";") > first_line.count(",") else ","
        raw = pd.read_csv(io.StringIO(text), sep=sep)
        raw = clean_data(raw)
        
        missing = [c for c in meta["columns"] if c not in raw.columns]
        if missing:
            st.error(f"Missing columns: {missing}")
        else:
            X_batch = raw[meta["columns"]]
            preds = model.predict(X_batch).clip(0, 20)

            out = raw.copy()
            out["predicted_grade"] = preds.round(1)
            out["status"] = ["At risk" if p < 10 else "Likely pass" for p in preds]
            out = out.sort_values("predicted_grade")

            n_risk = int((out["status"] == "At risk").sum())
            st.metric("Students flagged At risk", f"{n_risk} of {len(out)}")
            st.dataframe(out)
            st.download_button("Download results (CSV)",
                               out.to_csv(index=False),
                               "predictions.csv", "text/csv")
    except Exception as e:
        st.error(f"Could not process the file: {e}")