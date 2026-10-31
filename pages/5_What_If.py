import streamlit as st

from src.artifacts import load_all
from src.auth import require_role
from src.data import clean_data, load_data
from src.risk import risk_level, risk_message
from src.whatif import tips, what_if

st.set_page_config(page_title="What-If Simulator", page_icon="🔮", layout="wide")
user = require_role("student", "teacher", "admin")

st.title("🔮 What-If Simulator")
st.caption("See how the predicted grade changes if study habits change. "
           "These are model estimates, not promises.")

model, meta, explainer = load_all()


@st.cache_data
def load_students():
    df = clean_data(load_data("data/student-mat.csv"))
    return df[meta["columns"]]


students = load_students()

# Students see only their own record. Teachers and admins can choose.
if user["role"] == "student":
    row_id = user["student_row"]
    if row_id is None or row_id not in students.index:
        st.warning("Your account is not linked to a student record yet. "
                   "Please ask an admin.")
        st.stop()
    st.info(f"Showing your record ({user['full_name']}).")
else:
    row_id = st.number_input("Student row", min_value=0,
                             max_value=len(students) - 1, value=0, step=1)

base = students.loc[[int(row_id)]]
r = base.iloc[0]

current, _, _ = what_if(model, base, {})
c1, c2 = st.columns(2)
c1.metric("Current predicted grade", f"{current:.1f}")
c2.metric("Current risk level", risk_level(current))

# ---------- Sliders ----------
st.subheader("Change something")
s1, s2, s3 = st.columns(3)
studytime = s1.slider("Weekly study time (1: <2h, 4: >10h)", 1, 4,
                      int(r["studytime"]))
absences = s2.slider("Absences", 0, 93, int(r["absences"]))
goout = s3.slider("Going out with friends (1 to 5)", 1, 5, int(r["goout"]))

changes = {"studytime": studytime, "absences": absences, "goout": goout}
before, after, diff = what_if(model, base, changes)
new_level = risk_level(after)

m1, m2, m3 = st.columns(3)
m1.metric("New predicted grade", f"{after:.1f}", f"{diff:+.1f}")
m2.metric("New risk level", new_level)
m3.metric("Change", f"{diff:+.1f} points")

msg = risk_message(new_level)
if new_level == "High":
    st.error(msg)
elif new_level == "Medium":
    st.warning(msg)
else:
    st.success(msg)

if absences < int(r["absences"]) and diff < 0:
    st.caption("Note: the model sometimes predicts a lower grade for fewer "
               "absences. That is a quirk of this small dataset (students with "
               "0 absences include several with a final grade of 0), not "
               "advice to skip class.")

# ---------- Tips ----------
st.subheader("Ideas the model thinks could help")
suggestions = tips(model, base)
if suggestions:
    for s in suggestions:
        st.write(f"- **{s['tip']}**: about {s['gain']:+.1f} points "
                 f"(predicted {s['new_grade']:.1f})")
else:
    st.write("No single change shows a clear gain for this student.")
st.caption("Tips come from a model trained on a small public dataset and are "
           "not guaranteed. A teacher or counsellor should review them.")