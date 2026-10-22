import pandas as pd

df = pd.read_csv("data/student-mat.csv", sep=";")

print(df.shape)
print(df.head())
print(df.dtypes)
print(df.isnull().sum().sum(), "missing values")
print(df.duplicated().sum(), "duplicate rows")
print(df["G3"].describe())
print(df.corr(numeric_only=True)["G3"].sort_values())