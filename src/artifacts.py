import joblib
import streamlit as st

from src.explain import get_explainer


@st.cache_resource
def load_all():
    """Load the model, its metadata and the SHAP explainer once."""
    model = joblib.load("models/model.joblib")
    meta = joblib.load("models/meta.joblib")
    explainer = get_explainer(model)
    return model, meta, explainer



postgresql://neondb_owner:npg_2FJkGseU3Wtg@ep-long-leaf-a1sv7ilf-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require