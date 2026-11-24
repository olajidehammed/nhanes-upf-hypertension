## Current status — 24 November 2026

Standardized NHANES NOVA respondent-level files were shared by Dr Euridice Martinez-Steele on 23 November 2026 and supplied by the author as a ZIP on 24 November. The archive contains data from multiple NHANES cycles; only the four 2015–2016 and 2017–2018 Day 1/Day 2 files are relevant to this project. The corresponding 2017–2018 SAS CONTENTS PDFs were also supplied.

The four target CSVs each contain 180 variables and one row per respondent per recall day. For Day 1, the pooled 2015–2018 extraction contains 18,248 unique respondent records (9,544 in 2015–2016 and 8,704 in 2017–2018). No duplicate SEQN values were found within either cycle or across the pooled Day 1 files. NOVA group energy shares sum to 1 for positive-energy records; the supplied NOVA group-4 energy proportion agrees with the ratio calculated from group-level kcal to numerical precision. See [the standardized NOVA receipt and QA report](validation/2026-11-24/STANDARDIZED_NOVA_FILES_RECEIVED_QA.md).

The primary Day 1 exposure is now taken directly from the supplied `DR1T_Propcal_Novag4` variable and expressed as a percentage (0–100) in the merge-ready file. These are already NOVA-classified respondent-level group/subgroup summaries, not a food-code lookup table. The prior manual WWEIA-category-level classification is superseded for the final analysis.

**The new NOVA file has not yet been merged with the project's analytic NHANES dataset, and none of the regression estimates or manuscript results have yet been rerun using it.** The previous estimates based on the broad WWEIA approximation must therefore remain provisional and must not be presented as the standardized-NOVA results. The next checks are to merge on SEQN, compare summed NOVA-group kcal with official NHANES `DR1TKCAL`, verify dietary reliability and energy filters, then rebuild the analytic sample, weighted quartiles, imputed datasets, models, tables, figures, and manuscript text.

The standardized respondent-level files and merge-ready person-level exposure CSV are kept outside this public repository because they were shared directly for the research request. This PR adds documentation/aggregate QA only; it does not upload the individual-level NOVA data or synchronize the complete analysis pipeline.

The prior 30 October imputation trace diagnostics and independent R model cross-check remain conditional on the earlier analysis/exposure and completed datasets. They will need to be checked or rerun as appropriate after the standardized-NOVA analytic sample and models are rebuilt.

---

# Ultra-processed food intake and blood pressure control (NHANES 2015-2018)

Analysis code for a cross-sectional study of ultra-processed food (UPF) intake
and blood pressure control among US adults with treated hypertension, using
pooled 2015-2016 and 2017-2018 NHANES data. Manuscript in preparation; the standardized NOVA files have been received, but the new exposure has not yet been merged into the analytic sample or used to refit the models.

**Pre-standardized-NOVA finding (provisional; not the final result):** no significant association between UPF intake and blood
pressure control in this population, robust to two different blood pressure
guideline definitions (2017 ACC/AHA and the earlier JNC-8 standard), adjustment
for dietary sodium/potassium and antihypertensive medication intensity, and a
sensitivity check for BMI as a potential mediator. Sociodemographic factors
(race, income, education) showed more consistent associations with blood
pressure control than diet in this sample.

## What's here
All files sit in the repo root (not in a subfolder) - run everything from there.

## Setup
No `statsmodels` dependency - the environment this was developed in didn't
have internet access to install it, so the survey-weighted regression and
variance estimation in `survey_stats.py` are implemented directly with numpy/
scipy. If you have `statsmodels` or a proper survey package available, you're
better off using those; this is here because we didn't have the option.

## Data

NHANES data is public but not included in this repo (the individual foods
file alone is ~80MB, and it's easy enough to pull fresh). Download these into
a `data/` folder:

**From `https://wwwn.cdc.gov/nchs/nhanes/<cycle>/<FILE>.XPT`**, for cycles
`2015-2016` (suffix `_I`) and `2017-2018` (suffix `_J`):
`DEMO`, `BPQ`, `BPX`, `DR1TOT`, `DR1IFF`, `BMX`, `SMQ`, `RXQ_RX`

**Plus one shared file** (not cycle-specific): `RXQ_DRUG` from the 2017-2018
folder.

**And the WWEIA food category crosswalks** (USDA ARS, not CDC):
`WWEIA1516_foodcat_FNDDS.xlsx` and `WWEIA1718_foodcat_FNDDS.xlsx` from
`https://www.ars.usda.gov/ARSUserFiles/80400530/apps/`

Then:
## Notes on a couple of non-obvious things in here

**The SAS sentinel bug.** `pandas.read_sas()` misreads certain NHANES values
as a tiny denormalized float (`5.397605...e-79`) instead of the value it's
actually supposed to represent. For most variables that's a genuine missing
value, but for at least one (`DR1TALCO`, daily alcohol intake) it's a
corrupted *zero* - most people just don't drink on their recall day, and that
legitimate 0 gets mangled the same way a true missing value would. Worth
checking for this in any NHANES XPT file before trusting a "0" or a "NaN" at
face value. `clean_data.py` has the details and a validation check
(`verify_alcohol_fix`) that confirms this empirically rather than just
asserting it.

**Blood pressure averaging.** NHANES's own convention is to exclude the first
reading from the average (it tends to run high). Easy to miss if you're
averaging `BPXSY1-4` by hand instead of using the pre-derived variables -
this pipeline follows the official convention explicitly.

**Why two guideline thresholds.** The 2015-2016 cycle predates the 2017
ACC/AHA blood pressure guideline (<130/80 mmHg); the standard of care at the
time was JNC-8 (<140/90 mmHg). Applying the newer threshold retroactively to
older data is a real interpretability issue, not just a technicality - a
sensitivity analysis using the guideline that was actually in use at the time
is included, and it matters: the modest signal seen under the newer threshold
did not hold up under the older one.

**Multiple imputation is stochastic.** Missing covariates (education, income,
BMI, smoking status) are imputed 20 times and pooled with Rubin's rules rather
than dropped via complete-case analysis. Because this involves random draws,
re-running the pipeline will give you slightly different point estimates each
time - expected behavior for a near-null effect, not a bug. The direction and
significance of the main findings are stable across runs; the third decimal
place of an odds ratio isn't going to be.

## Use of generative AI

Generative AI tools (Claude by Anthropic and ChatGPT by OpenAI) assisted with portions of the code development, validation workflow, and repository documentation. All outputs were critically reviewed, verified, and, where necessary, modified by the author, who takes full responsibility for the repository and its contents
