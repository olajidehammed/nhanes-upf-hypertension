"""
End-to-end pipeline: raw NHANES files in, manuscript tables out.

Run as a script from the repo root:

    python src/run_models.py --data-dir data/

Expects the raw NHANES XPT files and the two USDA WWEIA crosswalk
spreadsheets to already be sitting in --data-dir (see the README for exact
filenames and download links - they're public but too large to check into
the repo). Everything else is derived.

This reproduces, in order: the NOVA-classified exposure, the corrected
blood pressure outcome (both the 2017 ACC/AHA and JNC-8 definitions), the
antihypertensive medication class covariate, multiple imputation of missing
covariates, and three model specifications - primary (with BMI), a
sensitivity model without BMI to check for over-adjustment given BMI's
plausible role as a mediator, and the JNC-8 outcome sensitivity analysis.
"""

import argparse

import numpy as np
import pandas as pd

from clean_data import load_pooled
from nova_classification import load_wweia_crosswalk, classify_food_records, upf_share_per_person
from build_sample import (
    restrict_to_treated_hypertensives, average_blood_pressure, classify_control_status,
    restrict_dietary_reliability, antihypertensive_class_counts, build_covariates,
)
from impute import add_model_dummies, run_multiple_imputation, IMPUTE_VARS
from survey_stats import weighted_logit_irls, taylor_linearized_vcov, pool_rubin, summarize


def weighted_quartiles(pct_upf, weights):
    order = pct_upf.sort_values().index
    cum_wt = weights.loc[order].cumsum()
    pctile = cum_wt / weights.sum()
    return pd.cut(pctile, bins=[0, 0.25, 0.5, 0.75, 1.0], labels=[1, 2, 3, 4], include_lowest=True).reindex(pct_upf.index)


def build_design(imp_df, quartiles, include_bmi=True):
    X = pd.DataFrame(index=imp_df.index)
    X["intercept"] = 1.0
    X["age"] = imp_df["RIDAGEYR"]
    X["male"] = imp_df["male"]
    X["race_mexam"] = imp_df["race_mexam"]
    X["race_otherhisp"] = imp_df["race_otherhisp"]
    X["race_nhblack"] = imp_df["race_nhblack"]
    X["race_other"] = imp_df["race_other"]
    educ = imp_df["educ"].round().clip(1, 5)
    X["educ_hs"] = (educ == 3).astype(float)
    X["educ_somecollege"] = (educ == 4).astype(float)
    X["educ_collegegrad"] = (educ == 5).astype(float)
    X["pir"] = imp_df["INDFMPIR"]
    if include_bmi:
        X["bmi"] = imp_df["BMXBMI"]
    smoke = imp_df["smoke_ord"].round().clip(0, 2)
    X["smoke_former"] = (smoke == 1).astype(float)
    X["smoke_current"] = (smoke == 2).astype(float)
    X["energy_kcal_per500"] = imp_df["total_kcal"] / 500.0
    X["sodium_per1000mg"] = imp_df["DR1TSODI"] / 1000.0
    X["potassium_per1000mg"] = imp_df["DR1TPOTA"] / 1000.0
    X["alcohol_g"] = imp_df["DR1TALCO"]
    X["n_antihtn_classes"] = imp_df["n_antihtn_classes"]
    X["upf_q2"] = (quartiles.values == 2).astype(float)
    X["upf_q3"] = (quartiles.values == 3).astype(float)
    X["upf_q4"] = (quartiles.values == 4).astype(float)
    return X


def fit_pooled_model(imputed_datasets, weights, strata, psu, quartiles, outcome_col,
                      include_bmi=True, outcome_override=None):
    """outcome_override lets you swap in a fully-observed outcome (like the
    JNC-8 classification) that doesn't need imputing, since it's identical
    across every imputed dataset."""
    betas, vcovs = [], []
    for imp_df in imputed_datasets:
        X = build_design(imp_df, quartiles, include_bmi)
        y = outcome_override.values if outcome_override is not None else imp_df[outcome_col].round().clip(0, 1).values
        w_norm = weights.values * (len(weights) / weights.sum())
        beta, mu = weighted_logit_irls(X, y, w_norm)
        vcov = taylor_linearized_vcov(X, y, w_norm, mu, beta, strata, psu)
        betas.append(beta)
        vcovs.append(vcov)
    beta_pooled, se_pooled = pool_rubin(betas, vcovs)
    return summarize(build_design(imputed_datasets[0], quartiles, include_bmi).columns, beta_pooled, se_pooled)


def main(data_dir):
    pooled = load_pooled(data_dir)
    sample = restrict_to_treated_hypertensives(pooled)
    sample = average_blood_pressure(sample)
    sample = classify_control_status(sample)

    crosswalks = load_wweia_crosswalk(
        f"{data_dir}/WWEIA1516_foodcat_FNDDS.xlsx", f"{data_dir}/WWEIA1718_foodcat_FNDDS.xlsx"
    )
    iff_i = pd.read_sas(f"{data_dir}/DR1IFF_I.xpt", format="xport")
    iff_j = pd.read_sas(f"{data_dir}/DR1IFF_J.xpt", format="xport")
    iff_i["cycle"], iff_j["cycle"] = "2015-2016", "2017-2018"
    iff = pd.concat([iff_i, iff_j], ignore_index=True)
    classified = classify_food_records(iff, crosswalks)
    upf = upf_share_per_person(classified)

    sample = sample.merge(upf, on="SEQN", how="left")
    sample = restrict_dietary_reliability(sample)

    bmx = pd.concat([
        pd.read_sas(f"{data_dir}/BMX_I.xpt", format="xport"),
        pd.read_sas(f"{data_dir}/BMX_J.xpt", format="xport"),
    ], ignore_index=True)
    smq = pd.concat([
        pd.read_sas(f"{data_dir}/SMQ_I.xpt", format="xport"),
        pd.read_sas(f"{data_dir}/SMQ_J.xpt", format="xport"),
    ], ignore_index=True)
    med_classes = antihypertensive_class_counts(
        [f"{data_dir}/RXQ_RX_I.xpt", f"{data_dir}/RXQ_RX_J.xpt"], f"{data_dir}/RXQ_DRUG.xpt"
    )

    sample = build_covariates(sample, bmx, smq, med_classes)
    sample = add_model_dummies(sample)
    print(f"Final analytic sample: n={len(sample)}")

    imputed = run_multiple_imputation(sample)
    weights = sample["WTDRD1"] / 2  # pooled 2-cycle dietary weight
    quartiles = weighted_quartiles(sample["pct_upf"], weights)

    primary = fit_pooled_model(imputed, weights, sample["SDMVSTRA"], sample["SDMVPSU"],
                                quartiles, "uncontrolled", include_bmi=True)
    no_bmi = fit_pooled_model(imputed, weights, sample["SDMVSTRA"], sample["SDMVPSU"],
                               quartiles, "uncontrolled", include_bmi=False)
    jnc8 = fit_pooled_model(imputed, weights, sample["SDMVSTRA"], sample["SDMVPSU"],
                             quartiles, "uncontrolled_jnc8", include_bmi=True,
                             outcome_override=sample["uncontrolled_jnc8"])

    print("\n=== Primary model (ACC/AHA <130/80, with BMI) ===")
    print(primary.to_string(index=False))
    print("\n=== Sensitivity: without BMI (mediator check) ===")
    print(no_bmi[no_bmi["var"].str.startswith("upf")].to_string(index=False))
    print("\n=== Sensitivity: JNC-8 threshold (<140/90) ===")
    print(jnc8[jnc8["var"].str.startswith("upf")].to_string(index=False))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", default="data")
    args = parser.parse_args()
    main(args.data_dir)
