# Standardized-NOVA NHANES reanalysis — aggregate results

**Updated:** 24 November 2026  
**Data source:** NOVA-coded NHANES Day 1 respondent-level files for 2015–2016 and 2017–2018, supplied by Dr Euridice Martínez-Steele.  
**Analytic cohort:** previously constructed 2,683-person treated-hypertension cohort.

## Merge and denominator QA

- 2,683/2,683 analytic participants matched to a Day 1 NOVA record by SEQN.
- No duplicate SEQN values or cycle mismatches.
- Sum of NOVA group 1–4 kcal matched the previous total-kcal denominator exactly for all 2,683 records.
- Existing total energy range remained within 600–6,000 kcal.
- Survey design represented 30 strata and 60 PSUs (30 design degrees of freedom).

The merge used the recovered analysis-ready cohort from the prior validation bundle. The bundle README referred to a separate 19-file raw NHANES/USDA input ZIP that was not present in the recovered files; therefore this rerun did not reconstruct the upstream raw-file participant flow.

## Exposure change

The survey-weighted mean group-4 energy share increased from 48.14% under the prior broad WWEIA-category approximation to 55.45% using the standardized respondent-level NOVA summaries. The Pearson correlation between participant-level exposures was 0.707, and 46.8% changed weighted-quartile assignment.

New survey-weighted cut-points: 40.34%, 55.69%, and 71.01%.

## Initial Python model results

| Analysis | OR | 95% CI | p |
|---|---:|---:|---:|
| Primary adjusted Q4 vs Q1 | 1.002 | 0.676–1.486 | 0.991 |
| No-BMI sensitivity Q4 vs Q1 | 0.997 | 0.674–1.476 | 0.988 |
| Historical BP threshold Q4 vs Q1 | 0.904 | 0.576–1.420 | 0.652 |
| Continuous UPF per 10 percentage points | 1.026 | 0.952–1.107 | 0.486 |
| UPF-by-male interaction ratio | 0.904 | 0.776–1.053 | 0.186 |

All focal Python outcome-model fits converged, with a maximum of five IRLS iterations. The previous category-mapping model estimates are not retained as the main results. The old nominal sex interaction did not persist with the standardized NOVA exposure.

## Validation limitations

- The new 20-imputation datasets have not yet been independently refitted in R with `survey::svyglm()` and `mitools::MIcombine()`. The previous R validation applied to the old category-mapped exposure and does not transfer.
- Formal multi-chain trace/R-hat diagnostics have not yet been rerun with the standardized exposure; the previous trace diagnostics were also for the earlier exposure. Saved-draw means are descriptive only.
- The recovered earlier validation ZIP included the 2,683-person analysis-ready dataset, but referred to a separate 19-file raw NHANES/USDA input archive that was not present in the recovered files. This reanalysis retained the existing sample and did not reconstruct the original raw-data exclusion flow.
- The imputation specification still treats SDMVSTRA and SDMVPSU as numeric auxiliary predictors.
- The manuscript, tables, figures and discussion have not yet been fully revised to reflect the standardized-NOVA estimates.

The public repository does not contain any participant-level NOVA files or merged analytic records. The reanalysis package is retained privately by the author.