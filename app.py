import joblib
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Student Performance Predictor", page_icon="🎓")
st.title("🎓 Student Performance Predictor")
st.caption("Predicts the final grade (0 to 20) from background and study habits.")


@st.cache_resource
def load_artifacts():
    model = joblib.load("models/model.joblib")
    meta = joblib.load("models/meta.joblib")
    return model, meta


model, meta = load_artifacts()
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