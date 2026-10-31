import numpy as np
import pandas as pd

from src.drift import category_psi, drift_status, numeric_psi
from src.fairness import gap_warning, group_report
from src.risk import risk_level
from src.whatif import tips, what_if


class FakeModel:
    """Predicts 3 x studytime, so results are easy to check by hand."""
    def predict(self, df):
        return df["studytime"].to_numpy(dtype=float) * 3.0


def one_row(studytime=2):
    return pd.DataFrame([{"studytime": studytime, "absences": 4, "goout": 3}])


def test_risk_boundaries():
    assert risk_level(8.4) == "High"
    assert risk_level(8.5) == "Medium"
    assert risk_level(11.4) == "Medium"
    assert risk_level(11.5) == "Low"


def test_same_data_is_stable():
    a = pd.Series(np.random.default_rng(0).normal(10, 2, 500))
    b = pd.Series(np.random.default_rng(1).normal(10, 2, 500))
    assert numeric_psi(a, b) < 0.10


def test_shifted_data_is_drift():
    a = pd.Series(np.random.default_rng(0).normal(10, 2, 500))
    assert numeric_psi(a, a + 10) > 0.25


def test_category_psi_identical_is_zero():
    s = pd.Series(["a", "b"] * 50)
    assert category_psi(s, s) == 0


def test_drift_status_levels():
    assert drift_status(0.05) == "stable"
    assert drift_status(0.15) == "watch"
    assert drift_status(0.30) == "drift"


def test_group_report_and_gap_warning():
    X = pd.DataFrame({"sex": ["F"] * 25 + ["M"] * 25, "studytime": [3] * 50})
    y = pd.Series([9] * 25 + [15] * 25)
    report = group_report(FakeModel(), X, y, "sex")
    assert len(report) == 2
    assert gap_warning(report) is not None


def test_small_group_gets_a_note():
    X = pd.DataFrame({"sex": ["F"] * 5 + ["M"] * 30, "studytime": [3] * 35})
    y = pd.Series([9] * 35)
    report = group_report(FakeModel(), X, y, "sex")
    assert report.loc[report["sex"] == "F", "note"].iloc[0] != ""


def test_what_if_changes_grade():
    before, after, diff = what_if(FakeModel(), one_row(2), {"studytime": 3})
    assert (before, after, diff) == (6.0, 9.0, 3.0)


def test_tips_only_suggest_real_gains():
    result = tips(FakeModel(), one_row(2))
    assert [t["tip"] for t in result] == ["Study one band more each week"]