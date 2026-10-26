import pandas as pd
import shap


def get_explainer(model):
    """Build a SHAP explainer for the Random Forest inside the pipeline."""
    return shap.TreeExplainer(model.named_steps["model"])


def _clean_name(name):
    """'num__age' -> 'age', 'cat__sex_F' -> 'sex_F'."""
    return name.split("__", 1)[1] if "__" in name else name


def explain_rows(model, explainer, X):
    """SHAP value of every feature for every row in X."""
    pre = model.named_steps["pre"]
    X_t = pre.transform(X)
    names = [_clean_name(n) for n in pre.get_feature_names_out()]
    values = explainer.shap_values(X_t)
    return pd.DataFrame(values, columns=names, index=X.index)


def top_reasons(model, explainer, row, n=8):
    """Top n features that moved the prediction for ONE student (one-row DataFrame).

    Positive impact = pushes the grade up, negative = pushes it down.
    """
    shap_df = explain_rows(model, explainer, row)
    s = shap_df.iloc[0]
    top = s.reindex(s.abs().sort_values(ascending=False).index).head(n)
    return pd.DataFrame({"feature": top.index, "impact": top.values.round(3)})