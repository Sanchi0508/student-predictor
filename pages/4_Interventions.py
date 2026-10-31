import pandas as pd
import streamlit as st

from src.auth import require_role
from src.db import (add_intervention, list_interventions,
                    update_intervention_status)

st.set_page_config(page_title="Interventions", page_icon="🤝", layout="wide")
user = require_role("teacher", "admin")

st.title("🤝 Interventions")
st.caption("Record support given to a student and track follow-ups. "
           "These notes are private to teachers and admins.")

ACTIONS = ["Counselling", "Extra class", "Parent meeting",
           "Study plan", "Mentor assigned", "Other"]
STATUSES = ["open", "in_progress", "done"]

# ---------- Add a new intervention ----------
st.subheader("Log a new intervention")
with st.form("new_intervention", clear_on_submit=True):
    c1, c2 = st.columns(2)
    student_row = c1.number_input("Student row (from the dashboard)",
                                  min_value=0, max_value=394, value=0, step=1)
    action = c2.selectbox("Action", ACTIONS)
    notes = st.text_area("Notes (keep them factual and respectful)")
    follow_up = st.date_input("Follow-up date", value=None)
    submitted = st.form_submit_button("Save intervention", type="primary")

if submitted:
    add_intervention(int(student_row), action, notes.strip(), follow_up,
                     user["username"])
    st.success(f"Saved for student row {int(student_row)}.")

# ---------- Show and update ----------
st.subheader("All interventions")
rows = list_interventions()

if not rows:
    st.info("No interventions logged yet.")
else:
    df = pd.DataFrame(rows, columns=[
        "id", "student_row", "action", "notes", "status",
        "follow_up_date", "created_by", "created_at"])

    f1, f2 = st.columns(2)
    status_filter = f1.multiselect("Status", STATUSES,
                                   default=["open", "in_progress"])
    only_row = f2.number_input("Only student row (-1 for all)",
                               min_value=-1, max_value=394, value=-1, step=1)

    shown = df[df["status"].isin(status_filter)]
    if only_row >= 0:
        shown = shown[shown["student_row"] == only_row]
    st.dataframe(shown, use_container_width=True, hide_index=True)

    st.subheader("Update a status")
    if len(shown):
        u1, u2, u3 = st.columns([2, 2, 1])
        pick = u1.selectbox("Intervention id", shown["id"].tolist())
        new_status = u2.selectbox("New status", STATUSES)
        if u3.button("Update"):
            update_intervention_status(int(pick), new_status)
            st.success("Status updated. Reload the page to see it in the table.")