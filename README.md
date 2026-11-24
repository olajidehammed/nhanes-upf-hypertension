## Current status — 24 November 2026

Dr Euridice Martinez-Steele shared the standardized NHANES NOVA files on 23 November 2026. The author supplied the ZIP on 24 November; the four relevant 2015–2016 and 2017–2018 Day 1/Day 2 files and two codebook PDFs were extracted and checked.

The standardized Day 1 NOVA group-4 energy proportion (`DR1T_Propcal_Novag4`) was merged by SEQN into the previously constructed 2,683-person treated-hypertension analytic cohort. All 2,683 participants matched; cycle labels agreed; there were no duplicate SEQN values; and the sum of NOVA group 1–4 kcal matched the prior `total_kcal` (sourced from NHANES `DR1TKCAL`) exactly in all 2,683 records.

The exposure changed materially relative to the previous broad WWEIA-category mapping: the survey-weighted mean UPF share rose from 48.14% to 55.45%, participant-level Pearson correlation was 0.707, and 46.8% of participants changed exposure quartile. Standardized-NOVA weighted quartile cut-points were 40.34%, 55.69%, and 71.01%.

**Initial standardized-NOVA Python results:** adjusted Q4 vs Q1 OR 1.002 (95% CI 0.676–1.486; p=0.991); continuous UPF per 10 percentage points OR 1.026 (0.952–1.107; p=0.486); historical <140/90 Q4 vs Q1 OR 0.904 (0.576–1.420; p=0.652). The earlier nominal UPF-by-sex interaction did not persist (interaction ratio OR 0.904; 0.776–1.053; p=0.186). These results are provisional pending independent R validation and fresh convergence diagnostics for the new exposure. See [the standardized-NOVA results and audit report](validation/2026-11-24/STANDARDIZED_NOVA_REANALYSIS_RESULTS.md).

The recovered earlier validation ZIP contained the 2,683-person analysis-ready cohort. Its README refers to a separate 19-file `NHANES_data_files.zip`, which was not available in the recovered files. This reanalysis therefore retains the prior selected cohort and verifies the participant merge and energy denominator; it does not independently recreate the original raw XPT/USDA exclusion flow.

The NOVA source files and participant-level merged datasets are intentionally not committed to this public repository. This PR contains only documentation and aggregate QA/results. The full source and analysis package remains with the author.

**Remaining checks:** independent R `survey::svyglm()`/`mitools::MIcombine()` validation of the new 20 imputed datasets; new-exposure multi-chain MICE trace/R-hat diagnostics; and full revision of the abstract, methods, results, discussion, tables and figures. The prior R cross-check and old-exposure MICE traces do not validate the new standardized-NOVA models.

---

# Ultra-processed food intake and blood pressure control (NHANES 2015-2018)

Analysis code for a cross-sectional study of ultra-processed food (UPF) intake
and blood pressure control among US adults with treated hypertension, using
pooled 2015-2016 and 2017-2018 NHANES data. Manuscript in preparation; standardized NOVA models have been refitted in Python, but independent R validation and new-exposure imputation diagnostics remain outstanding.

**Initial standardized-NOVA finding (provisional):** the adjusted Q4-versus-Q1 OR was 1.002 (95% CI 0.676–1.486; p=0.991); continuous UPF per 10 percentage points was OR 1.026 (95% CI 0.952–1.107; p=0.486). The historical <140/90 sensitivity was also non-significant (OR 0.904; 95% CI 0.576–1.420; p=0.652). The prior nominal UPF-by-sex interaction did not persist (interaction ratio OR 0.904; 95% CI 0.776–1.053; p=0.186). These are initial Python results pending independent R validation and new-exposure imputation diagnostics.

## Current analysis-code status
The analysis scripts currently on the main branch still contain the earlier WWEIA-category approximation. The standardized-NOVA reanalysis scripts and completed datasets are retained in the private reanalysis package, not yet synchronized to the public source tree. Do not treat the existing main-branch script as reproducing the new standardized-NOVA estimates.

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
