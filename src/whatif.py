def predict_one(model, row_df):
    """Predicted grade for a one-row DataFrame, kept between 0 and 20."""
    return float(max(0.0, min(20.0, model.predict(row_df)[0])))


def what_if(model, base_row, changes):
    """Predict before and after changing some fields.

    base_row: one-row DataFrame, changes: dict like {"absences": 2}.
    Returns (before, after, difference).
    """
    new_row = base_row.copy()
    for col, value in changes.items():
        new_row[col] = value
    before = predict_one(model, base_row)
    after = predict_one(model, new_row)
    return round(before, 1), round(after, 1), round(after - before, 1)


def tips(model, base_row, min_gain=0.2):
    """Try a few realistic single changes and keep those that raise the grade."""
    r = base_row.iloc[0]
    candidates = []
    if r["studytime"] < 4:
        candidates.append(("Study one band more each week",
                           {"studytime": int(r["studytime"]) + 1}))
    if r["absences"] > 0:
        candidates.append(("Halve the number of absences",
                           {"absences": int(r["absences"] // 2)}))
    if r["goout"] > 1:
        candidates.append(("Go out one notch less",
                           {"goout": int(r["goout"]) - 1}))

    results = []
    for label, change in candidates:
        before, after, diff = what_if(model, base_row, change)
        if diff >= min_gain:
            results.append({"tip": label, "new_grade": after, "gain": diff})
    return sorted(results, key=lambda t: -t["gain"])