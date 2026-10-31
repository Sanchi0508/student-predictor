# Student Performance Predictor# Student Success Platform

An early-warning web app that predicts a student's final grade, flags students who may need support, and explains why. Built with Pandas, scikit-learn, SHAP, Streamlit and a Postgres database.

**Demo with public sample data** (UCI Student Performance dataset, 395 Portuguese secondary-school students). A real college should retrain on its own data.

[![tests](https://github.com/Sanchi0508/student-predictor/actions/workflows/tests.yml/badge.svg)](https://github.com/Sanchi0508/student-predictor/actions)

## Features

| Role | What they can do |
|---|---|
| Student | See own predicted grade and risk level, reasons (SHAP), what-if simulator and tips |
| Teacher | Risk-ranked class dashboard, CSV batch upload, log and track interventions |
| Admin | Model performance, fairness check by group, data drift check, user list |

Passwords are stored as bcrypt hashes. Each role can only open its own pages.

## Screenshots

| Student View | Teacher Dashboard |
|---|---|
| ![student](docs/student.png) | ![dashboard](docs/dashboard.png) |

| What-If Simulator | Admin Monitoring |
|---|---|
| ![whatif](docs/whatif.png) | ![admin](docs/admin.png) |

## Model results

G1 and G2 (earlier period grades) are removed on purpose. An early-warning tool cannot use grades that do not exist yet, so keeping them would be leakage.

| | MAE | RMSE | R2 |
|---|---|---|---|
| Baseline (always the mean) | 3.646 | 4.55 | -0.01 |
| Random Forest | 3.01 | 3.765 | 0.309 |

5-fold cross-validation R2: 0.272 (+/- 0.057).

## Risk levels

| Level | Predicted grade | Meaning |
|---|---|---|
| High | below 8.5 | Recommend support |
| Medium | 8.5 to 11.5 | Uncertain, teacher should review |
| Low | 11.5 and above | Likely to pass |

The model's average error is about 3 grade points, so results near the pass mark are treated as uncertain.

## Fairness check (held-out test set, 79 students)

A student counts as flagged when the predicted grade is below 11.5.

| Group | Students | MAE | Failing students caught |
|---|---|---|---|
| Female | 38 | 3.04 | 13 of 15 |
| Male | 41 | 2.99 | 10 of 12 |

No large gap was found, but the groups are small, so this is not proof of fairness.

## Known limitations

- The model explains only about 31% of the variation in final grades.
- SHAP shows what the **model** learned, not cause and effect. For example, fewer absences can lower the predicted grade, because several students with 0 absences have a final grade of 0 in this dataset.
- Flagging below 11.5 catches most failing students but also flags some who would pass.
- The model flags and suggests. A teacher makes the decision.
- Predictions for a class that looks different from the training data are less reliable. The drift check warns about this.

## Run locally

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python train.py
streamlit run app.py
```

Create `.streamlit/secrets.toml` with your own Postgres connection string (never commit this file):

```toml
DATABASE_URL = "your-connection-string"
```

## Tests

```bash
python -m pytest -q
```

15 tests cover data validation, risk levels, drift, fairness and the what-if logic.