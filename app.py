import streamlit as st

from src.artifacts import load_all
from src.auth import current_user, login, logout

st.set_page_config(page_title="Student Success Platform", page_icon="🎓",
                   layout="wide")

st.title("🎓 Student Success Platform")
st.caption("Early-warning support for students and teachers (demo with sample data).")

user = current_user()

# ---------- Login screen ----------
if user is None:
    st.subheader("Log in")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Log in", type="primary"):
        if login(username, password):
            st.rerun()
        else:
            st.error("Wrong username or password.")
    st.stop()

# ---------- Logged-in home page ----------
st.sidebar.write(f"Logged in as **{user['full_name']}** ({user['role']})")
if st.sidebar.button("Log out"):
    logout()
    st.rerun()

model, meta, explainer = load_all()

st.success(f"Welcome, {user['full_name']}!")

st.markdown(
    """
### What this app does
- **Student View:** predicted grade, risk level (Low, Medium, High) and the reasons.
- **Batch Upload (teachers and admins):** upload a whole class and get a risk-ranked list.

### How to use it responsibly
1. The model **flags and suggests**. A teacher makes the decision.
2. Results near the pass line are **uncertain** (Medium risk).
3. The reasons show what the **model** learned, not real-world cause and effect.
4. This demo uses the UCI Student Performance dataset (Portuguese secondary schools).
   A real college should retrain on its own data.
"""
)

c1, c2, c3 = st.columns(3)
c1.metric("Model", "Random Forest")
c2.metric("Test R²", "0.31")
c3.metric("Avg error (MAE)", "3.0 grade points")