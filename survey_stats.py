"""
Weighted logistic regression for complex survey data, built from scratch
because statsmodels wasn't available in the environment this analysis was
run in.

Two pieces here:

1. weighted_logit_irls - fits a survey-weighted logistic regression via
   iteratively reweighted least squares. Nothing unusual about this part.

2. taylor_linearized_vcov - the more involved piece. NHANES uses a
   stratified, multistage design where (in the pooled 2015-2018 sample we
   used) each stratum contains exactly two sampled primary sampling units
   (PSUs). Naively clustering standard errors on PSU ignores the variance
   reduction from stratification and understates uncertainty. The standard
   fix, "Taylor series linearization" via the ultimate-cluster method, is
   what R's survey package and Stata's svy commands do under the hood. This
   reimplements that: linearize the estimating equations, sum contributions
   within each stratum-PSU cell, then compute the between-PSU contrast
   within each stratum and sum across strata.

   Singleton PSUs (a stratum where only one PSU ended up in your particular
   subsample) get a zero variance contribution here, which is the same
   conservative convention used by most survey software when you don't
   want to collapse strata by hand. Worth checking your own subsample for
   these before assuming the default is fine - see run_models.py for how
   we checked (all 30 strata in this analysis had both PSUs represented, so
   it never came up in practice here).

Point estimates and variances from multiple imputed datasets are combined
elsewhere (see pool_rubin below) using standard Rubin's rules: pooled
variance = average within-imputation variance + (1 + 1/m) * between-
imputation variance.
"""

import numpy as np
import pandas as pd
from scipy import stats


def weighted_logit_irls(X, y, weights, max_iter=100, tol=1e-8):
    Xm = X.values
    n, p = Xm.shape
    beta = np.zeros(p)
    for _ in range(max_iter):
        eta = Xm @ beta
        mu = np.clip(1 / (1 + np.exp(-eta)), 1e-10, 1 - 1e-10)
        w_iter = weights * mu * (1 - mu)
        z = eta + (y - mu) / (mu * (1 - mu))
        XtWX = Xm.T @ (Xm * w_iter[:, None])
        XtWz = (Xm * w_iter[:, None]).T @ z
        beta_new = np.linalg.solve(XtWX + 1e-10 * np.eye(p), XtWz)
        if np.max(np.abs(beta_new - beta)) < tol:
            beta = beta_new
            break
        beta = beta_new
    mu = np.clip(1 / (1 + np.exp(-(Xm @ beta))), 1e-10, 1 - 1e-10)
    return beta, mu


def taylor_linearized_vcov(X, y, weights, mu, beta, strata, psu):
    Xm = X.values
    n, p = Xm.shape
    w_iter = weights * mu * (1 - mu)
    bread = np.linalg.inv(Xm.T @ (Xm * w_iter[:, None]) + 1e-10 * np.eye(p))

    resid = weights * (y - mu)
    linearized = Xm * resid[:, None]

    contributions = pd.DataFrame(linearized, columns=[f"h{i}" for i in range(p)])
    contributions["stratum"] = strata.values
    contributions["psu"] = psu.values
    cluster_sums = contributions.groupby(["stratum", "psu"]).sum()

    meat = np.zeros((p, p))
    for _, group in cluster_sums.groupby(level=0):
        n_psu = len(group)
        if n_psu < 2:
            continue  # singleton stratum, conservative zero contribution
        vals = group.values
        deviations = vals - vals.mean(axis=0)
        meat += (n_psu / (n_psu - 1)) * (deviations.T @ deviations)

    return bread @ meat @ bread


def pool_rubin(betas, vcovs):
    """betas: list of coefficient arrays (one per imputation). vcovs: list
    of the corresponding variance-covariance matrices. Returns pooled
    point estimates, standard errors, and a results dataframe once you
    attach variable names."""
    m = len(betas)
    betas = np.array(betas)
    beta_pooled = betas.mean(axis=0)
    within = np.mean(vcovs, axis=0)
    between = np.cov(betas.T, ddof=1)
    total = within + (1 + 1 / m) * between
    se = np.sqrt(np.diag(total))
    return beta_pooled, se


def summarize(varnames, beta, se):
    z = beta / se
    p = 2 * (1 - stats.norm.cdf(np.abs(z)))
    return pd.DataFrame({
        "var": varnames,
        "OR": np.exp(beta),
        "CI_low": np.exp(beta - 1.96 * se),
        "CI_high": np.exp(beta + 1.96 * se),
        "p": p,
    })
