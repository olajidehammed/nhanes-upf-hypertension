# MICE convergence diagnostics and longer-burn-in sensitivity — 30 October 2026

## Design

The analytic sample contained 2,683 participants. Missingness was education 8 (0.3%), income-to-poverty ratio 318 (11.9%), BMI 35 (1.3%), and ordinal smoking status 3 (0.1%).

Four independently initialized chains used the primary imputation specification: predictive mean matching with k=10, Gaussian parameter perturbation, and all other model variables as predictors, including numeric-coded SDMVSTRA/SDMVPSU and log dietary weight. Initial missing values were randomized from observed donor values within each chain. Each chain used 30 complete burn-in sweeps followed by 150 monitored sweeps (600 monitored chain-sweep summaries in total).

## Trace summary diagnostics

The monitored statistics were the mean and SD among originally missing cells for income-to-poverty ratio and BMI, and the mean among originally missing cells for education and smoking status.

| Trace statistic | R-hat | Split R-hat |
|---|---:|---:|
| Income-to-poverty ratio mean | 0.9981 | 0.9999 |
| Income-to-poverty ratio SD | 1.0006 | 1.0043 |
| BMI mean | 0.9998 | 0.9974 |
| BMI SD | 0.9999 | 0.9990 |
| Education mean | 0.9979 | 1.0063 |
| Smoking-status mean | 0.9995 | 0.9959 |

All monitored scalar summaries had conventional and split R-hat values below 1.01. Trace plots showed substantial chain overlap without an obvious sustained trend during the monitored period. R-hat estimates slightly below 1 can occur with finite-sample estimators and should be interpreted as approximately 1.

These results support adequate mixing for the monitored scalar summaries under this specification. They do not establish that every element of the joint imputed-data distribution has converged, that the conditional models are correctly specified, or that missingness assumptions are valid. Education and smoking have very few missing cells, so their summary traces are coarse. The primary imputation model still treats survey strata and PSU as numeric auxiliary predictors; factor-coded and stratum–PSU-cell alternatives remain targeted specification sensitivities.

## Longer-burn-in production sensitivity

The 20-imputation production workflow was rerun with the original seed, predictor set, PMM donor count, Gaussian perturbation, and five updates between saved imputations, but with 30 rather than 10 burn-in sweeps. All focal regression models converged, with a maximum of five IRLS iterations.

| Model/term | Original 10-sweep OR (95% CI), p | 30-sweep OR (95% CI), p |
|---|---|---|
| Primary UPF Q4 vs Q1 | 0.8292 (0.5431–1.2661), 0.3726 | 0.8299 (0.5436–1.2671), 0.3747 |
| Historical BP threshold Q4 vs Q1 | 1.0755 (0.6847–1.6892), 0.7438 | 1.0763 (0.6850–1.6910), 0.7415 |
| Continuous UPF per 10 percentage points | 0.9895 (0.9166–1.0682), 0.7797 | 0.9897 (0.9168–1.0685), 0.7846 |
| UPF-by-male interaction ratio | 0.8512 (0.7492–0.9672), 0.0153 | 0.8510 (0.7491–0.9668), 0.0150 |

The largest absolute odds-ratio change was 0.00077. The primary UPF quartile and continuous associations remained statistically non-significant; the sex interaction remained exploratory and hypothesis-generating.

## Remaining checks

The previously completed independent R cross-check covers the original 20 completed datasets, not the new 30-burn-in datasets. The newer completed datasets have been refitted in Python only. The standardized NHANES NOVA food-/ingredient-code classification remains pending from NCI; the current broad WWEIA-category-level mapping is an approximation. When standardized files are received, rebuild the exposure and rerun the complete analysis, including imputation, tables, figures, and manuscript text.

This diagnostic update is not a declaration that the manuscript is submission-ready.
