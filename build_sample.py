"""
Building the analytic sample: eligibility criteria, the blood pressure
outcome, and the covariate set.

A couple of things worth flagging if you're adapting this for your own
NHANES project:

1. Blood pressure averaging follows the official NHANES convention of
   dropping the first reading (it tends to run high - white-coat effect).
   This is easy to get wrong; the derived BPXSAR/BPXDAR variables handle it
   correctly but if you're averaging BPXSY1-4 by hand, as we needed to do
   here for readings 2-4 specifically, it's on you to drop reading 1.

2. Antihypertensive medication class count comes from linking the
   prescription files (RXQ_RX) to the drug classification reference file
   (RXQ_DRUG) and counting distinct therapeutic classes per person that
   fall under a hand-picked list of antihypertensive-relevant categories.
"""

import numpy as np
import pandas as pd

ANTIHYPERTENSIVE_CLASSES = {
    "ANGIOTENSIN CONVERTING ENZYME (ACE) INHIBITORS", "ANGIOTENSIN II INHIBITORS",
    "BETA-ADRENERGIC BLOCKING AGENTS", "CALCIUM CHANNEL BLOCKING AGENTS", "DIURETICS",
    "LOOP DIURETICS", "POTASSIUM-SPARING DIURETICS", "THIAZIDE AND THIAZIDE-LIKE DIURETICS",
    "VASODILATORS", "PERIPHERAL VASODILATORS", "RENIN INHIBITORS", "ANTIHYPERTENSIVE COMBINATIONS",
    "MISCELLANEOUS ANTIHYPERTENSIVE COMBINATIONS", "ACE INHIBITORS WITH CALCIUM CHANNEL BLOCKING AGENTS",
    "ACE INHIBITORS WITH THIAZIDES", "ANGIOTENSIN II INHIBITORS WITH CALCIUM CHANNEL BLOCKERS",
    "ANGIOTENSIN II INHIBITORS WITH THIAZIDES", "ANGIOTENSIN RECEPTOR BLOCKERS AND NEPRILYSIN INHIBITORS",
    "POTASSIUM SPARING DIURETICS WITH THIAZIDES",
}


def restrict_to_treated_hypertensives(pooled_df):
    adults = pooled_df[pooled_df["RIDAGEYR"] >= 18]
    diagnosed = adults[adults["BPQ020"] == 1]
    return diagnosed[diagnosed["BPQ050A"] == 1].copy()


def average_blood_pressure(df):
    """Average readings 2-4, falling back to reading 1 alone for the small
    number of people who only have one valid reading. Returns two new
    columns (avg_sbp, avg_dbp) and drops anyone left with no usable BP."""
    df = df.copy()
    sy_cols, di_cols = ["BPXSY2", "BPXSY3", "BPXSY4"], ["BPXDI2", "BPXDI3", "BPXDI4"]

    df["avg_sbp"] = df[sy_cols].mean(axis=1, skipna=True)
    df["avg_dbp"] = df[di_cols].mean(axis=1, skipna=True)

    only_first = df["avg_sbp"].isna() & df["BPXSY1"].notna()
    df.loc[only_first, "avg_sbp"] = df.loc[only_first, "BPXSY1"]
    df.loc[only_first, "avg_dbp"] = df.loc[only_first, "BPXDI1"]

    return df[df["avg_sbp"].notna() & df["avg_dbp"].notna()].copy()


def classify_control_status(df):
    df = df.copy()
    df["bp_controlled"] = ((df["avg_sbp"] < 130) & (df["avg_dbp"] < 80)).astype(int)
    df["bp_controlled_jnc8"] = ((df["avg_sbp"] < 140) & (df["avg_dbp"] < 90)).astype(int)
    df["uncontrolled"] = 1 - df["bp_controlled"]
    df["uncontrolled_jnc8"] = 1 - df["bp_controlled_jnc8"]
    return df


def restrict_dietary_reliability(df, min_kcal=600, max_kcal=6000):
    reliable = df[df["DR1DRSTZ"] == 1]
    return reliable[(reliable["total_kcal"] >= min_kcal) & (reliable["total_kcal"] <= max_kcal)].copy()


def antihypertensive_class_counts(rxq_rx_paths, rxq_drug_path):
    """rxq_rx_paths: list of paths to the per-cycle prescription files.
    Returns a SEQN -> n_antihtn_classes lookup, filled with 0 for anyone
    with no medication matched to our antihypertensive category list."""
    drug = pd.read_sas(rxq_drug_path, format="xport")
    level_cols = ["RXDDCN1A", "RXDDCN1B", "RXDDCN1C"]
    for c in level_cols:
        drug[c] = drug[c].apply(lambda x: x.decode() if isinstance(x, bytes) else x)

    def matched_class(row):
        for c in level_cols:
            if row[c] in ANTIHYPERTENSIVE_CLASSES:
                return row[c]
        return None

    drug["antihtn_class"] = drug.apply(matched_class, axis=1)
    drug_lookup = drug.loc[drug["antihtn_class"].notna(), ["RXDDRGID", "antihtn_class"]]

    rx = pd.concat(
        [pd.read_sas(p, format="xport")[["SEQN", "RXDDRGID"]] for p in rxq_rx_paths],
        ignore_index=True,
    )
    rx = rx.merge(drug_lookup, on="RXDDRGID", how="inner")
    counts = rx.groupby("SEQN")["antihtn_class"].nunique().rename("n_antihtn_classes").reset_index()
    return counts


def build_covariates(df, bmx_df, smq_df, med_class_counts):
    """Attach BMI, smoking status, and medication class count. Sodium,
    potassium, and alcohol intake are already present in df at this point
    (they come along with the original DR1TOT merge in clean_data.py), so
    they're not re-merged here - doing so would just collide with the
    existing columns and get silently suffixed by pandas."""
    df = df.merge(bmx_df[["SEQN", "BMXBMI"]], on="SEQN", how="left")
    df = df.merge(smq_df[["SEQN", "SMQ020", "SMQ040"]], on="SEQN", how="left")
    df = df.merge(med_class_counts, on="SEQN", how="left")
    df["n_antihtn_classes"] = df["n_antihtn_classes"].fillna(0)

    def smoke_status(row):
        if pd.isna(row["SMQ020"]):
            return np.nan
        if row["SMQ020"] == 2:
            return "never"
        if row["SMQ020"] == 1:
            return "current" if row["SMQ040"] in (1, 2) else "former"
        return np.nan

    df["smoke_status"] = df.apply(smoke_status, axis=1)
    df["educ"] = df["DMDEDUC2"].replace({7: np.nan, 9: np.nan})
    return df
