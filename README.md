# Ultra-processed food intake and blood pressure control (NHANES 2015-2018)

Analysis code for a cross-sectional study of ultra-processed food (UPF) intake
and blood pressure control among US adults with treated hypertension, using
pooled 2015-2016 and 2017-2018 NHANES data. Manuscript submitted to *Nutrients*.

**Main finding:** no significant association between UPF intake and blood
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

Generative AI (Claude, Anthropic) was used to assist with portions of the code development and repository documentation. All outputs were critically reviewed, verified, and, where necessary, modified by the author, who takes full responsibility for the repository and its contents
