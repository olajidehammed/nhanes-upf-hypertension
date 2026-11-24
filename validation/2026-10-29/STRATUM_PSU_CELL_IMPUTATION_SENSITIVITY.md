# Stratum–PSU cell factor imputation sensitivity — 29 October 2026

## Purpose and procedure

A second post hoc imputation sensitivity represented each of the 60 observed stratum–PSU combinations as a categorical auxiliary predictor, rather than including stratum and PSU codes as numeric values. The analysis used N=2,683, predictive mean matching for education, income-to-poverty ratio, BMI and smoking ordinal status, 20 completed datasets, 10 burn-in sweeps, and five chained-equation updates between saved imputations.

All focal survey-weighted outcome models converged (maximum 5 IRLS iterations).

## Focal results

| Model/term | Primary OR (95% CI), p | 60-cell sensitivity OR (95% CI), p |
|---|---|---|
| Primary Q4 vs Q1 | 0.829 (0.543–1.266), p=0.373 | 0.828 (0.542–1.265), p=0.370 |
| Historical threshold Q4 vs Q1 | 1.075 (0.685–1.689), p=0.744 | 1.073 (0.683–1.687), p=0.751 |
| Continuous UPF per 10 percentage points | 0.989 (0.917–1.068), p=0.780 | 0.989 (0.916–1.068), p=0.777 |
| UPF slope among women in interaction model | 1.055 (0.959–1.161), p=0.259 | 1.055 (0.959–1.161), p=0.256 |
| Sex-interaction ratio of ORs | 0.851 (0.749–0.967), p=0.0153 | 0.850 (0.748–0.966), p=0.0146 |

The main UPF associations remain statistically non-significant, and their estimates barely changed. The sex interaction remains exploratory.

## Saved-draw descriptive summaries

Across the first 10 versus last 10 completed datasets, means among originally missing cells were:

| Variable | First 10 mean | Last 10 mean | Absolute difference |
|---|---:|---:|---:|
| Education score | 3.238 | 3.113 | 0.125 |
| Income-to-poverty ratio | 2.426 | 2.383 | 0.043 |
| BMI (kg/m²) | 30.400 | 31.084 | 0.684 |
| Smoking ordinal score | 0.500 | 0.567 | 0.067 |

These are descriptive summaries across saved draws, not formal convergence diagnostics. The full per-sweep trace was not retained because the run was completed in chunks after a runtime timeout. Multiple-chain R-hat diagnostics were not performed.

## Interpretation

This sensitivity reduces concern that the key estimates depend on the numeric coding of survey-design identifiers. It is a targeted specification sensitivity and does not establish full convergence, independently validate the imputation model, or validate the approximate WWEIA-category-level NOVA exposure. The standardized NHANES NOVA request was sent to NCI on 29 October 2026; response/proposal form is pending.
