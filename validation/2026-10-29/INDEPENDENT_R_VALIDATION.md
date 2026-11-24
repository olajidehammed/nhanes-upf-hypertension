# NHANES independent R cross-check and imputation sensitivity — 29 October 2026

## Independent R cross-check

The corrected Python analysis was cross-checked against R `survey::svyglm()` and `mitools::MIcombine()` using the same 20 completed datasets.

- Analytic sample: 2,683 participants.
- Survey design represented: 30 strata, 60 PSUs, 30 design degrees of freedom.
- All 85 coefficient rows matched one-to-one between R and Python.
- Maximum absolute differences across all terms: OR 9.36e-09; SE 8.41e-06; lower CI limit 1.13e-05; upper CI limit 2.85e-04; p-value 1.85e-05.

This cross-check validates model fitting and pooled inference conditional on the same completed datasets. It does not independently validate the imputation process or the manual NOVA exposure classification.

## Focal estimates

| Analysis | OR (95% CI) | p-value |
|---|---:|---:|
| Primary, UPF Q4 vs Q1 | 0.829 (0.543–1.266) | 0.373 |
| Historical BP threshold, Q4 vs Q1 | 1.075 (0.685–1.689) | 0.744 |
| Continuous UPF per 10 percentage points | 0.989 (0.917–1.068) | 0.780 |
| UPF-by-male interaction | 0.851 (0.749–0.967) | 0.0153 |

The main UPF associations remain non-significant. The sex interaction is exploratory and hypothesis-generating.

## Factor-coded stratum imputation sensitivity

A second sensitivity run used 20 completed datasets with factor-coded `SDMVSTRA`, binary/numeric `SDMVPSU`, log dietary weight as an auxiliary predictor, 10 burn-in cycles, and 5 chained-equation updates before each saved imputation. This matches the iteration schedule of the primary workflow.

- Primary Q4 vs Q1: OR 0.828 (95% CI 0.543–1.264), p=0.369.
- Historical threshold: OR 1.074 (95% CI 0.684–1.687), p=0.749.
- Continuous UPF per 10 percentage points: OR 0.989 (95% CI 0.917–1.068), p=0.779.
- Sex-interaction ratio: OR 0.851 (95% CI 0.749–0.967), p=0.0149.

These estimates were essentially unchanged. However, this is a targeted coding sensitivity rather than a complete design-aware imputation model: PSU is not represented as 60 nested stratum–PSU cell indicators, and formal MICE trace/convergence diagnostics were not completed. Keep the imputation-model limitation explicit.

## Remaining blockers

1. Request the standardized NHANES NOVA classification files through the National Cancer Institute proposal process. The existing broad WWEIA-category-level mapping is an approximation, not the standardized method. The data have not yet been requested/received.
2. Once standardized NOVA files are received, reconstruct the exposure and rerun the full analysis, tables, figures, and manuscript results.
3. After the exposure method is settled, sync the definitive source code and outputs to the repository. This PR documents the validation milestone, not a full source-code synchronization.

The initial Colab run failed because `svyglm()` was passed `df.resid = df_design`. Removing that explicit argument allowed the validation to run using the survey package's default residual-df handling.
