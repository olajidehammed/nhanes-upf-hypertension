"""
Multiple imputation for the missing covariates (education, income-to-poverty
ratio, BMI, smoking status - each missing in roughly 0.1-12% of the sample).

We didn't have statsmodels or a proper survey package available, so this
leans on sklearn's IterativeImputer (a MICE-style approach: each variable
with missing data gets modeled as a function of the others, cycling through
until things stabilize). Running it once gives you a single "best guess"
per missing value, which understates how uncertain those guesses are -
you're not supposed to be as confident about an imputed income as you are
about an observed one, and if you only impute once, downstream models don't
know that. Twenty separate imputations (a different random draw each time),
combined afterward with Rubin's rules in survey_stats.py, is the standard
fix.

Outcome is included in the imputation model, which is generally recommended
practice - excluding it tends to attenuate the very association you're
trying to estimate.
"""

import pandas as pd
from sklearn.experimental import enable_iterative_imputer  # noqa: F401 - required for the import below
from sklearn.impute import IterativeImputer
from sklearn.linear_model import BayesianRidge

IMPUTE_VARS = [
    "RIDAGEYR", "male", "race_mexam", "race_otherhisp", "race_nhblack", "race_other",
    "educ", "INDFMPIR", "BMXBMI", "smoke_ord", "pct_upf", "total_kcal",
    "DR1TSODI", "DR1TPOTA", "DR1TALCO", "n_antihtn_classes", "uncontrolled",
]


def add_model_dummies(df):
    """A few of the imputation predictors are dummy/ordinal recodes of the
    raw NHANES variables - split out here so it's obvious what's happening
    rather than burying it inside the imputation call."""
    df = df.copy()
    df["male"] = (df["RIAGENDR"] == 1).astype(float)
    df["race_mexam"] = (df["RIDRETH1"] == 1).astype(float)
    df["race_otherhisp"] = (df["RIDRETH1"] == 2).astype(float)
    df["race_nhblack"] = (df["RIDRETH1"] == 4).astype(float)
    df["race_other"] = (df["RIDRETH1"] == 5).astype(float)
    df["smoke_ord"] = df["smoke_status"].map({"never": 0, "former": 1, "current": 2})
    return df


def run_multiple_imputation(df, n_imputations=20, random_state_start=1000):
    """Returns a list of n_imputations completed dataframes (same index as
    df, same columns as IMPUTE_VARS), each a plausible fill-in of the
    missing values drawn from its posterior rather than a single point
    estimate."""
    X = df[IMPUTE_VARS].copy()
    completed = []
    for i in range(n_imputations):
        imputer = IterativeImputer(
            estimator=BayesianRidge(),
            max_iter=15,
            random_state=random_state_start + i,
            sample_posterior=True,
        )
        filled = imputer.fit_transform(X)
        completed.append(pd.DataFrame(filled, columns=IMPUTE_VARS, index=X.index))
    return completed
