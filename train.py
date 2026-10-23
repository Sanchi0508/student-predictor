import joblib
from sklearn.dummy import DummyRegressor
from sklearn.model_selection import cross_val_score, train_test_split

from src.data import clean_data, load_data, split_features_target, validate_data
from src.model import build_pipeline, evaluate_model

# ("G1", "G2") = early warning, no grades needed
# ("G2",)      = mid-term prediction, uses G1
DROP_COLS = ("G1", "G2")

# 1. Load, clean, validate
df = validate_data(clean_data(load_data("data/student-mat.csv")))
X, y = split_features_target(df, DROP_COLS)

# 2. Split first, so the test set stays unseen
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# 3. Baseline: always predict the average grade
baseline = DummyRegressor(strategy="mean").fit(X_train, y_train)
print("Baseline:", evaluate_model(baseline, X_test, y_test))

# 4. Real model
pipe = build_pipeline(X_train)
pipe.fit(X_train, y_train)
print("Model   :", evaluate_model(pipe, X_test, y_test))

# 5. Cross-validation on training data only
cv = cross_val_score(build_pipeline(X_train), X_train, y_train, cv=5, scoring="r2")
print("CV R2   : %.3f (+/- %.3f)" % (cv.mean(), cv.std()))

# 6. Save the model and the default values the app will need
defaults = {}
for col in X.columns:
    if X[col].dtype.kind in "iuf":
        defaults[col] = float(X[col].median())
    else:
        defaults[col] = X[col].mode()[0]

joblib.dump(pipe, "models/model.joblib")
joblib.dump({"columns": X.columns.tolist(), "defaults": defaults},
            "models/meta.joblib")
print("Saved model to models/")