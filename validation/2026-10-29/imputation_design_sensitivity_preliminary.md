# Factor-coded stratum imputation sensitivity analysis

Date: 2026-10-29

A second multiple-imputation sensitivity run was completed on the same N=2,683 analysis sample and used 20 completed datasets. It factor-coded survey strata (`SDMVSTRA`) rather than treating stratum IDs as a numeric trend. The log dietary weight remained an auxiliary predictor; the two-level PSU code (`SDMVPSU`, 1/2) remained binary/numeric. The run used 10 burn-in cycles and 5 chained-equation updates between each saved dataset, matching the iteration schedule in the primary workflow.

| Model/term | Main OR (95% CI), p | Factor-coded stratum sensitivity OR (95% CI), p |
|---|---|---|
| Primary Q4 vs Q1 | 0.829 (0.543–1.266), p=0.373 | 0.828 (0.543–1.264), p=0.369 |
| Historical threshold Q4 vs Q1 | 1.075 (0.685–1.689), p=0.744 | 1.074 (0.684–1.687), p=0.749 |
| Continuous UPF per 10 percentage points | 0.989 (0.917–1.068), p=0.780 | 0.989 (0.917–1.068), p=0.779 |
| UPF slope among women in interaction model | 1.055 (0.959–1.161), p=0.259 | 1.055 (0.959–1.161), p=0.257 |
| Sex interaction ratio of ORs | 0.851 (0.749–0.967), p=0.0153 | 0.851 (0.749–0.967), p=0.0149 |

The targeted sensitivity produced essentially unchanged focal estimates and substantive conclusions. It reduces concern that treating the stratum identifier as a linear numeric predictor alone drives the results.

This is not a complete design-aware imputation model: PSU is not represented by 60 nested stratum–PSU cell indicators, and formal MICE trace-plot/convergence diagnostics were not completed. The imputation-model limitation should remain explicit. The R cross-check validates model fitting and inference conditional on completed datasets; it does not validate the imputation process or the NOVA exposure classification.
