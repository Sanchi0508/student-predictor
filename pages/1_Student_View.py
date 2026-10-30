import pandas as pd
import streamlit as st

from src.artifacts import load_all
from src.explain import top_reasons
from src.risk import risk_level, risk_message

st.set_page_config(page_title="Student View", page_icon="🎓", layout="wide")
st.title("🎓 Student View")
st.caption("Predicts the final grade (0 to 20) from background and study habits.")

model, meta, explainer = load_all()
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
    row = dict(defaults)
    row.update({
        "age": age, "sex": sex, "studytime": studytime,
        "failures": failures, "absences": absences,
        "higher": higher, "internet": internet, "goout": goout,
    })
    row_df = pd.DataFrame([row])[meta["columns"]]

    pred = float(model.predict(row_df)[0])
    pred = max(0.0, min(20.0, pred))
    level = risk_level(pred)

    m1, m2 = st.columns(2)
    m1.metric("Predicted final grade (0 to 20)", f"{pred:.1f}")
    m2.metric("Risk level", level)

    msg = risk_message(level)
    if level == "High":
        st.error(msg)
    elif level == "Medium":
        st.warning(msg)
    else:
        st.success(msg)

    st.subheader("Why this prediction?")
    st.caption("Positive = pushes the grade up. Negative = pushes it down. "
               "This explains the model, not real-world cause and effect.")
    reasons = top_reasons(model, explainer, row_df, n=8)
    st.bar_chart(reasons.set_index("feature")["impact"])