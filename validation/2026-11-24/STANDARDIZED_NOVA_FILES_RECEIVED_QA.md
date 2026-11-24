# Standardized NHANES NOVA files received — receipt and initial QA

**Date of ZIP received:** 24 November 2026  
**Source:** The author-provided ZIP containing the folder shared by Dr Euridice Martinez-Steele. Her email of 23 November 2026 lists the four NOVA CSVs and two codebook files below.

## Files received for the study cycles

- `nh1516_day1_nova_v20250131.csv` — NHANES 2015–2016, Day 1
- `nh1516_day2_nova_v20250131.csv` — NHANES 2015–2016, Day 2
- `nh1718_day1_nova_v20250131.csv` — NHANES 2017–2018, Day 1
- `nh1718_day2_nova_v20250131.csv` — NHANES 2017–2018, Day 2
- `nh1718_day1_content.pdf` — SAS CONTENTS output for Day 1 variables
- `nh1718_day2_content.pdf` — SAS CONTENTS output for Day 2 variables

The ZIP also contains NOVA summary files for other NHANES cycles. Those were inventoried but not pooled into this 2015–2018 study.

## File structure

Each CSV contains 180 columns and one respondent-level record for each recall day, keyed by `seqn`. The cycle identifier is `SDDSRVYR` (9 for 2015–2016 and 10 for 2017–2018); the recall-day identifier is `DAY` (1 or 2). The Day 1 and Day 2 schemas correspond after the DR1/DR2 variable-prefix change. The two cycle-specific schemas were checked for consistency.

These files are already respondent-level NOVA group and subgroup summaries. They are **not** item-level food records and are **not** a food-code-to-NOVA lookup table. The prior manual mapping from broad WWEIA categories is no longer needed for deriving the respondent's Day 1 NOVA group-4 energy share.

## Initial file-level quality checks

| File | Rows | Columns | Unique SEQN | Duplicate SEQN | SDDSRVYR | DAY |
|---|---:|---:|---:|---:|---:|---:|
| 2015–2016 Day 1 | 9,544 | 180 | 9,544 | 0 | 9 | 1 |
| 2015–2016 Day 2 | 9,544 | 180 | 9,544 | 0 | 9 | 2 |
| 2017–2018 Day 1 | 8,704 | 180 | 8,704 | 0 | 10 | 1 |
| 2017–2018 Day 2 | 8,704 | 180 | 8,704 | 0 | 10 | 2 |

No duplicate respondent identifiers were found within files or across the pooled Day 1 cycles.

For positive-energy records:

- The four group-level energy proportions sum to 1 within a tolerance of (10^{-8}).
- The supplied group-4 proportion, `DR1T_Propcal_Novag4`, agrees with group-4 kcal divided by the sum of kcal for NOVA groups 1–4 with a maximum absolute difference of approximately (6.2\times10^{-11}) in share units.
- Group-level kcal values agree with the sum of the corresponding subgroup kcal values to within approximately (1.4\times10^{-7}) kcal.
- No negative group-energy or energy-proportion values were found.

## Day 1 recall and energy-flow counts

| Cycle | All respondents | Reliable recall status 1 | Positive NOVA kcal | Reliable and 600–6,000 kcal |
|---|---:|---:|---:|---:|
| 2015–2016 | 9,544 | 8,327 | 8,326 | 8,096 |
| 2017–2018 | 8,704 | 7,484 | 7,483 | 7,256 |

These are general NHANES Day 1 data-file counts before restricting to adults with diagnosed and treated hypertension and before applying blood-pressure eligibility criteria. They must not be confused with the study's final analytic sample.

The unweighted mean group-4 energy share among all positive-energy Day 1 records was 57.17% in 2015–2016 and 59.08% in 2017–2018. These are descriptive file-level checks only, not nationally representative weighted estimates and not estimates for the treated-hypertension study population.

## Primary exposure and merge-ready file

The main Day 1 exposure is:

`pct_upf = 100 × DR1T_Propcal_Novag4`

where the source variable is the proportion (0–1) of respondent's Day 1 energy classified as NOVA group 4. The source also provides absolute group-4 energy as `DR1T_Abscal_Novag4`.

A local one-row-per-respondent table was prepared with 18,248 records and a unique `SEQN` key. It includes `pct_upf`, group-specific kcal, and `nova_total_kcal_from_groups` (the sum of group 1–4 energy). It has **not yet** been merged with the project's analytic dataset. The next integration check must compare `nova_total_kcal_from_groups` against official NHANES Day 1 total energy, `DR1TKCAL`, after merging by `SEQN`.

## Interpretation and remaining work

1. Merge the Day 1 table 1:1 by `SEQN` and verify cycle agreement.
2. Compare the NOVA-derived group-kcal total with official `DR1TKCAL`; investigate any systematic or material discrepancies before using `pct_upf`.
3. Reconcile reliable-recall status and the prespecified 600–6,000 kcal rule with the existing sample construction.
4. Rebuild weighted quartiles and the full analysis using the standardized exposure.
5. Recreate imputed datasets, refit and independently validate the survey models, and regenerate all tables, figures, and manuscript results.

No new association estimates are reported here. The existing regression results were derived using the earlier broad WWEIA-category approximation and are not final standardized-NOVA findings.

## Data handling

The raw CSVs and merge-ready respondent-level exposure file are intentionally not committed to this public repository. The source files were shared directly for this specific research request. The author has a separate local extraction package containing the original files, derived merge-ready exposure, data dictionary, source checksums, and QA reports.
