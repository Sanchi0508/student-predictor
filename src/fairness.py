import numpy as np
import pandas as pd


def group_report(model, X_test, y_test, column, pass_mark=10,
                 flag_below=11.5, min_size=20):
    """Compare model errors across the groups of one column (e.g. sex).

    Returns one row per group with:
    - MAE: average size of the error, in grade points
    - avg_error: predicted minus actual (negative = model is too pessimistic)
    - recall: share of truly failing students that the model also flagged
    - note: warns when a group is too small to trust
    """
    pred = np.clip(model.predict(X_test), 0, 20)
    d = pd.DataFrame({
        "group": X_test[column].values,
        "actual": y_test.values,
        "pred": pred,
    })

    rows = []
    for group, part in d.groupby("group"):
        err = part["pred"] - part["actual"]
        failing = part["actual"] < pass_mark
        flagged = part["pred"] < flag_below
        n_fail = int(failing.sum())
        caught = int((failing & flagged).sum())
        rows.append({
            column: group,
            "students": len(part),
            "MAE": round(float(err.abs().mean()), 2),
            "avg_error": round(float(err.mean()), 2),
            "failing": n_fail,
            "caught": caught,
            "recall": round(caught / n_fail, 2) if n_fail else None,
            "note": "small group, treat with care" if len(part) < min_size else "",
        })
    return pd.DataFrame(rows)


def gap_warning(report, max_mae_gap=0.75):
    """Return a warning text if the MAE differs a lot between groups, else None."""
    usable = report[report["note"] == ""]
    if len(usable) < 2:
        return None
    gap = usable["MAE"].max() - usable["MAE"].min()
    if gap > max_mae_gap:
        return (f"The average error differs by {gap:.2f} grade points between "
                f"groups. Review before relying on the model for all groups.")
    return None