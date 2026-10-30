HIGH_BELOW = 8.5
LOW_FROM = 11.5


def risk_level(grade):
    """Turn a predicted grade (0 to 20) into High, Medium or Low risk."""
    if grade < HIGH_BELOW:
        return "High"
    if grade < LOW_FROM:
        return "Medium"
    return "Low"


def risk_message(level):
    """Short human-readable advice for each level."""
    return {
        "High": "High risk: recommend support (counselling or extra classes).",
        "Medium": "Medium risk: result is uncertain, teacher should review.",
        "Low": "Low risk: likely to pass, keep monitoring.",
    }[level]