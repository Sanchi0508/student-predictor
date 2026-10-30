from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Get database URL
DATABASE_URL = os.getenv("postgresql://neondb_owner:npg_2FJkGseU3Wtg@ep-long-leaf-a1sv7ilf-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require")

print("Database URL loaded:", DATABASE_URL is not None)
import streamlit as st

from src.artifacts import load_all

st.set_page_config(page_title="Student Success Platform", page_icon="🎓",
                   layout="wide")

st.title("🎓 Student Success Platform")
st.caption("Early-warning support for students and teachers (demo with sample data).")

model, meta, explainer = load_all()

st.markdown(
    """
### What this app does
- **Student View:** enter a student's details, get a predicted grade, a risk level
  (Low, Medium, High) and the reasons behind it.
- **Batch Upload:** upload a whole class and get a risk-ranked list to download.

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

st.info("Use the sidebar on the left to open a page.")