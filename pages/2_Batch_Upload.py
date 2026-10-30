import io

import pandas as pd
import streamlit as st

from src.artifacts import load_all
from src.data import clean_data
from src.risk import risk_level

st.set_page_config(page_title="Batch Upload", page_icon="📄", layout="wide")
st.title("📄 Batch Upload")
st.caption("Upload a whole class. Semicolon or comma separated CSV both work.")

model, meta, explainer = load_all()

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
            preds = model.predict(raw[meta["columns"]]).clip(0, 20)

            out = raw.copy()
            out["predicted_grade"] = preds.round(1)
            out["risk_level"] = [risk_level(p) for p in preds]
            out = out.sort_values("predicted_grade")

            counts = out["risk_level"].value_counts()
            c1, c2, c3 = st.columns(3)
            c1.metric("High risk", int(counts.get("High", 0)))
            c2.metric("Medium risk", int(counts.get("Medium", 0)))
            c3.metric("Low risk", int(counts.get("Low", 0)))

            choice = st.multiselect(
                "Show only these levels",
                ["High", "Medium", "Low"],
                default=["High", "Medium", "Low"])
            shown = out[out["risk_level"].isin(choice)]

            st.dataframe(shown, use_container_width=True)
            st.download_button("Download results (CSV)",
                               shown.to_csv(index=False),
                               "predictions.csv", "text/csv")
    except Exception as e:
        st.error(f"Could not process the file: {e}")