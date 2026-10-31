import numpy as np
import pandas as pd

STABLE_BELOW = 0.10
DRIFT_FROM = 0.25


def _psi_from_shares(train_share, new_share):
    t = np.clip(np.asarray(train_share, dtype=float), 1e-4, None)
    n = np.clip(np.asarray(new_share, dtype=float), 1e-4, None)
    return float(np.sum((n - t) * np.log(n / t)))


def category_psi(train, new):
    """PSI for text columns and numeric columns with few distinct values."""
    cats = sorted(set(train.astype(str)) | set(new.astype(str)))
    t = train.astype(str).value_counts(normalize=True)
    n = new.astype(str).value_counts(normalize=True)
    return _psi_from_shares([t.get(c, 0) for c in cats],
                            [n.get(c, 0) for c in cats])


def numeric_psi(train, new, bins=5):
    """PSI for numeric columns with many distinct values (age, absences)."""
    edges = np.unique(np.quantile(train, np.linspace(0, 1, bins + 1)))
    if len(edges) < 3:
        return category_psi(train, new)
    edges[0], edges[-1] = -np.inf, np.inf
    t = np.histogram(train, edges)[0] / len(train)
    n = np.histogram(new, edges)[0] / len(new)
    return _psi_from_shares(t, n)


def drift_status(psi):
    if psi < STABLE_BELOW:
        return "stable"
    if psi < DRIFT_FROM:
        return "watch"
    return "drift"


def drift_report(train_df, new_df, columns):
    """One row per feature, biggest drift first."""
    rows = []
    for col in columns:
        is_number = pd.api.types.is_numeric_dtype(train_df[col])
        if is_number and train_df[col].nunique() > 6:
            psi = numeric_psi(train_df[col], new_df[col])
        else:
            psi = category_psi(train_df[col], new_df[col])
        rows.append({"feature": col, "psi": round(psi, 3),
                     "status": drift_status(psi)})
    return pd.DataFrame(rows).sort_values("psi", ascending=False).reset_index(drop=True)