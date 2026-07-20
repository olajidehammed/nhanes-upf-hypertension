"""
Loading and cleaning raw NHANES files.

The main gotcha here: pandas.read_sas() has a known issue with NHANES's XPT
files where certain SAS-encoded values (both true missing codes and, in some
columns, true zeros) get misread as a tiny denormalized float instead of NaN
or 0. If you don't catch this, it silently corrupts things like blood
pressure readings and alcohol intake.

The fix isn't one-size-fits-all: for some variables the corrupted value
really is "missing" (e.g. a diastolic reading of 0 is physiologically
impossible), but for others it's a genuine zero that got mangled (e.g. most
people report 0g of alcohol on their recall day, and there's no reason that
should be missing). See fix_alcohol_zeros() below for how that was resolved
for DR1TALCO specifically - it required cross-checking against the
individual foods file to confirm.
"""

import numpy as np
import pandas as pd

SAS_SENTINEL = 5.397605346934028e-79


def load_xpt(path):
    return pd.read_sas(path, format="xport")


def clean_sentinel(df, treat_as_zero=None):
    """Replace the corrupted SAS sentinel with NaN (default) or 0.0 for any
    columns listed in treat_as_zero, where we've separately confirmed the
    true value should be zero rather than missing."""
    treat_as_zero = treat_as_zero or []
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    for col in numeric_cols:
        vals = df[col].values
        mask = (vals != 0) & (np.abs(vals) < 1e-60)
        if mask.sum() == 0:
            continue
        df.loc[mask, col] = 0.0 if col in treat_as_zero else np.nan
    return df


def load_cycle(data_dir, suffix):
    """Load and merge the core files (demographics, BP questionnaire, BP
    exam, dietary totals) for one NHANES cycle, e.g. suffix='I' for 2015-16
    or 'J' for 2017-18."""
    demo = clean_sentinel(load_xpt(f"{data_dir}/DEMO_{suffix}.xpt"))
    bpq = clean_sentinel(load_xpt(f"{data_dir}/BPQ_{suffix}.xpt"))
    bpx = clean_sentinel(load_xpt(f"{data_dir}/BPX_{suffix}.xpt"))
    tot = clean_sentinel(load_xpt(f"{data_dir}/DR1TOT_{suffix}.xpt"), treat_as_zero=["DR1TALCO"])

    merged = demo.merge(bpq, on="SEQN").merge(bpx, on="SEQN").merge(tot, on="SEQN")
    merged["cycle"] = "2015-2016" if suffix == "I" else "2017-2018"
    return merged


def load_pooled(data_dir):
    """Pool the 2015-16 and 2017-18 cycles into one dataframe."""
    c1 = load_cycle(data_dir, "I")
    c2 = load_cycle(data_dir, "J")
    return pd.concat([c1, c2], ignore_index=True)


def verify_alcohol_fix(iff_path, tot_df, wweia_food_categories):
    """Sanity check for the DR1TALCO zero-vs-missing question: people whose
    alcohol total shows the sentinel pattern should have (a) no food items
    logged under an alcohol WWEIA category, and (b) a complete, plausible
    total calorie count. If both hold, the sentinel really was a corrupted
    zero, not a corrupted missing value. Used during development - not part
    of the main pipeline, kept here for reproducibility."""
    iff = load_xpt(iff_path)
    affected = tot_df.loc[np.isclose(tot_df["DR1TALCO"], SAS_SENTINEL, atol=1e-80), "SEQN"]
    alcohol_codes = set(
        wweia_food_categories.loc[
            wweia_food_categories["category_number"].isin([7502, 7504, 7506]), "food_code"
        ]
    )
    logged_alcohol = iff.loc[iff["SEQN"].isin(affected) & iff["DR1IFDCD"].isin(alcohol_codes), "SEQN"]
    return {
        "n_affected": len(affected),
        "n_with_alcohol_item_logged": logged_alcohol.nunique(),  # should be 0
    }
