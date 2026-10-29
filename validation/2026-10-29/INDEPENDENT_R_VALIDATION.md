# NHANES independent R cross-check — 29 October 2026

## Result

The corrected Python analysis was cross-checked against an independent R implementation using `survey::svyglm()` and `mitools::MIcombine()` on the same 20 completed datasets.

- Analytic sample: 2,683 participants.
- Survey design represented: 30 strata, 60 PSUs, 30 design degrees of freedom.
- All 85 coefficients matched one-to-one between the R results and the saved Python model tables.
- Maximum absolute differences across all terms: odds ratio 9.36e-09; standard error 8.41e-06; lower confidence limit 1.13e-05; upper confidence limit 2.85e-04; p-value 1.85e-05.

The comparison is conditional on the same 20 completed datasets. It checks model fitting and pooled inference; it does not independently validate the imputation process or the manual NOVA exposure classification.

## Main results

| Analysis | OR (95% CI) | p-value |
|---|---:|---:|
| Primary, UPF Q4 vs Q1 | 0.829 (0.543–1.266) | 0.373 |
| Historical BP threshold, Q4 vs Q1 | 1.075 (0.685–1.689) | 0.744 |
| Continuous UPF per 10 percentage points | 0.989 (0.917–1.068) | 0.780 |
| UPF-by-male interaction | 0.851 (0.749–0.967) | 0.0153 |

The main UPF associations remain non-significant. The sex interaction is exploratory and hypothesis-generating.

## Remaining items before submission

1. Request the standardized NHANES NOVA classification files from NCI via the proposal process. The current broad WWEIA-category mapping is an approximation and must not be described as the standardized method.
2. Complete a longer factor-coded imputation sensitivity analysis with diagnostics, or explicitly retain the limitation. A preliminary run produced similar estimates but used shorter update spacing and is not convergence-certified.
3. After the exposure method is settled, sync the final corrected pipeline, tables, figures, and manuscript to the repository.

## Reproduction note

The Colab validation failed initially because `svyglm()` was passed `df.resid = df_design`; removing that argument allowed the model to run under the survey package's default residual-df handling. The updated local validation package contains the corrected script and full comparison outputs. This repository PR documents the validation milestone and outstanding work; it does not claim the analysis is fully submission-ready.
