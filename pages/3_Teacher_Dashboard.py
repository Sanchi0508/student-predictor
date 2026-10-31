import pandas as pd
import streamlit as st

from src.artifacts import load_all
from src.auth import require_role
from src.data import clean_data, load_data
from src.db import list_interventions
from src.explain import top_reasons
from src.risk import risk_level, risk_message

st.set_page_config(page_title="Teacher Dashboard", page_icon="📊", layout="wide")
user = require_role("teacher", "admin")

st.title("📊 Teacher Dashboard")
st.caption("Class ranked by predicted risk. The model flags, the teacher decides.")

model, meta, explainer = load_all()


@st.cache_data
def load_class():
    df = clean_data(load_data("data/student-mat.csv"))
    X = df[meta["columns"]]
    preds = model.predict(X).clip(0, 20)
    out = pd.DataFrame({
        "student_row": df.index,
        "age": df["age"].values,
        "sex": df["sex"].values,
        "failures": df["failures"].values,
        "absences": df["absences"].values,
        "studytime": df["studytime"].values,
        "predicted_grade": preds.round(1),
        "risk_level": [risk_level(p) for p in preds],
    })
    return X, out


X, board = load_class()

# Count open interventions per student
try:
    rows = list_interventions()
    open_counts = {}
    for r in rows:
        if r[4] != "done":
            open_counts[r[1]] = open_counts.get(r[1], 0) + 1
except Exception:
    open_counts = {}
board["open_interventions"] = board["student_row"].map(open_counts).fillna(0).astype(int)

# ---------- Summary ----------
counts = board["risk_level"].value_counts()
c1, c2, c3, c4 = st.columns(4)
c1.metric("Students", len(board))
c2.metric("High risk", int(counts.get("High", 0)))
c3.metric("Medium risk", int(counts.get("Medium", 0)))
c4.metric("Low risk", int(counts.get("Low", 0)))

st.bar_chart(counts.reindex(["High", "Medium", "Low"]).fillna(0))

# ---------- Ranked list ----------
st.subheader("Risk-ranked students")
levels = st.multiselect("Show levels", ["High", "Medium", "Low"],
                        default=["High", "Medium"])
shown = board[board["risk_level"].isin(levels)].sort_values("predicted_grade")
st.dataframe(shown, use_container_width=True, hide_index=True)
st.download_button("Download this list (CSV)", shown.to_csv(index=False),
                   "risk_list.csv", "text/csv")

# ---------- Why one student is flagged ----------
st.subheader("Why is this student flagged?")
if len(shown):
    pick = st.selectbox("Student row", shown["student_row"].tolist())
    pred = float(board.loc[board["student_row"] == pick, "predicted_grade"].iloc[0])
    level = risk_level(pred)
    st.write(f"Predicted grade **{pred:.1f}**. {risk_message(level)}")
    reasons = top_reasons(model, explainer, X.loc[[pick]], n=8)
    st.caption("Positive = pushes the grade up. Negative = pushes it down. "
               "This explains the model, not real-world cause and effect.")
    st.bar_chart(reasons.set_index("feature")["impact"])
    st.info("To record support for this student, open the **Interventions** page "
            "(built in the next step).")
else:
    st.write("No students match the selected levels.")