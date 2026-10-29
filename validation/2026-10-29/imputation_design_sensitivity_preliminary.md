# Preliminary imputation design-coding sensitivity (internal status)

A separate exploratory run replaced numeric survey design identifiers in the imputation predictors with factor-coded terms for `SDMVSTRA` and `SDMVPSU`, retaining log dietary weight as an auxiliary predictor.

| Model/term | Main OR (95% CI), p | Factor-coded sensitivity OR (95% CI), p |
|---|---|---|
| Primary Q4 vs Q1 | 0.829 (0.543–1.266), p=0.373 | 0.827 (0.542–1.263), p=0.367 |
| Historical threshold Q4 vs Q1 | 1.075 (0.685–1.689), p=0.744 | 1.073 (0.683–1.686), p=0.753 |
| Continuous UPF per 10 percentage points | 0.989 (0.917–1.068), p=0.780 | 0.989 (0.916–1.068), p=0.772 |
| Sex interaction | 0.851 (0.749–0.967), p=0.0153 | 0.851 (0.749–0.967), p=0.0151 |

The sensitivity run used 5 burn-in cycles and 2 update cycles between saved imputations for runtime reasons. The estimates are reassuringly similar, but this is not a convergence-certified replacement of the primary imputation. Do not present it as definitive in the manuscript. Before submission, either run a longer factor-coded chain and inspect diagnostics or retain the imputation-model limitation explicitly.
