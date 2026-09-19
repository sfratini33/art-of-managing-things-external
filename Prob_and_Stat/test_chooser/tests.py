"""Run the named test with SciPy and statsmodels; keep the arithmetic visible."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

import numpy as np
from scipy import stats
from statsmodels.stats.proportion import (
    confint_proportions_2indep,
    proportion_confint,
    proportions_ztest,
)

from .assumptions import normality_check, proportion_conditions, variance_ratio_check
from .chooser import TEST_NAMES, choose_test
from .io_data import Sample
from .spec import Alternative, StudySpec


@dataclass
class AssumptionLine:
    name: str
    committed: str
    check: str


@dataclass
class TestResult:
    test_id: str
    test_name: str
    hypotheses_symbols: str
    hypotheses_words: str
    alternative: Alternative
    alpha: float
    statistic_name: str
    statistic: float
    df: Optional[float]
    pvalue: float
    critical_low: Optional[float]
    critical_high: Optional[float]
    reject: bool
    ci_low: Optional[float]
    ci_high: Optional[float]
    ci_level: float
    formula_lines: list[str]
    sample_summaries: list[str]
    assumptions: list[AssumptionLine]
    notes: list[str] = field(default_factory=list)
    refused: bool = False


def _hyp_mean(name: str, mu0: float, alt: Alternative) -> tuple[str, str]:
    if alt == "two-sided":
        return f"H0: μ = {mu0:g}    H1: μ ≠ {mu0:g}", f"The mean of {name} is {mu0:g}."
    if alt == "greater":
        return (
            f"H0: μ ≤ {mu0:g}    H1: μ > {mu0:g}",
            f"The mean of {name} is at most {mu0:g}; the test is carried out at the boundary {mu0:g}.",
        )
    return (
        f"H0: μ ≥ {mu0:g}    H1: μ < {mu0:g}",
        f"The mean of {name} is at least {mu0:g}; the test is carried out at the boundary {mu0:g}.",
    )


def _hyp_diff(a: str, b: str, d: float, alt: Alternative) -> tuple[str, str]:
    if alt == "two-sided":
        return (
            f"H0: μ_{a} − μ_{b} = {d:g}    H1: μ_{a} − μ_{b} ≠ {d:g}",
            f"The two means differ by {d:g}.",
        )
    if alt == "greater":
        return (
            f"H0: μ_{a} − μ_{b} ≤ {d:g}    H1: μ_{a} − μ_{b} > {d:g}",
            f"The mean of {a} exceeds the mean of {b} by at most {d:g}; "
            f"the test is carried out at the boundary {d:g}.",
        )
    return (
        f"H0: μ_{a} − μ_{b} ≥ {d:g}    H1: μ_{a} − μ_{b} < {d:g}",
        f"The mean of {a} exceeds the mean of {b} by at least {d:g}; "
        f"the test is carried out at the boundary {d:g}.",
    )


def _hyp_prop(p0: float, alt: Alternative) -> tuple[str, str]:
    if alt == "two-sided":
        return f"H0: p = {p0:g}    H1: p ≠ {p0:g}", f"The population proportion is {p0:g}."
    if alt == "greater":
        return (
            f"H0: p ≤ {p0:g}    H1: p > {p0:g}",
            f"The population proportion is at most {p0:g}; the test is carried out at the boundary {p0:g}.",
        )
    return (
        f"H0: p ≥ {p0:g}    H1: p < {p0:g}",
        f"The population proportion is at least {p0:g}; the test is carried out at the boundary {p0:g}.",
    )


def _hyp_two_prop(d: float, alt: Alternative) -> tuple[str, str]:
    if alt == "two-sided":
        return f"H0: p1 − p2 = {d:g}    H1: p1 − p2 ≠ {d:g}", f"The two proportions differ by {d:g}."
    if alt == "greater":
        return (
            f"H0: p1 − p2 ≤ {d:g}    H1: p1 − p2 > {d:g}",
            f"p1 exceeds p2 by at most {d:g}; the test is carried out at the boundary {d:g}.",
        )
    return (
        f"H0: p1 − p2 ≥ {d:g}    H1: p1 − p2 < {d:g}",
        f"p1 exceeds p2 by at least {d:g}; the test is carried out at the boundary {d:g}.",
    )


def _crit_from_dist(dist, df, alpha: float, alt: Alternative) -> tuple[Optional[float], Optional[float]]:
    if alt == "two-sided":
        c = float(dist.ppf(1 - alpha / 2, df)) if df is not None else float(dist.ppf(1 - alpha / 2))
        return -c, c
    if alt == "greater":
        c = float(dist.ppf(1 - alpha, df)) if df is not None else float(dist.ppf(1 - alpha))
        return None, c
    c = float(dist.ppf(alpha, df)) if df is not None else float(dist.ppf(alpha))
    return c, None


def _reject(pvalue: float, alpha: float) -> bool:
    return pvalue <= alpha


def _design_note(spec: StudySpec) -> str:
    if spec.designed_experiment:
        return (
            "You recorded that the treatments were assigned by the investigator. "
            "A difference, if the test finds one, can be laid at the door of that assignment, "
            "subject to the usual caveats about randomization and the factors built into the design."
        )
    return (
        "You recorded that these data are observational. A statistical difference does not, "
        "by itself, say what caused it. Any factor that differs between the groups is a rival "
        "explanation. See the close of Section 4.9."
    )


def _need_sd(sample: Sample, what: str) -> None:
    if sample.sd is None or sample.n is None or sample.n < 2:
        raise ValueError(f"{what} needs a sample standard deviation and n at least 2.")


def run_test(spec: StudySpec, a: Sample, b: Optional[Sample] = None) -> TestResult:
    a = a.resolved()
    if b is not None:
        b = b.resolved()
    test_id = choose_test(spec)
    dispatch = {
        "one_sample_z": _one_sample_z,
        "one_sample_t": _one_sample_t,
        "two_sample_pooled_t": _two_sample_t,
        "welch_t": _two_sample_t,
        "paired_t": _paired_t,
        "one_prop_z": _one_prop_z,
        "two_prop_z": _two_prop_z,
    }
    result = dispatch[test_id](spec, a, b, test_id)
    result.notes.append(_design_note(spec))
    return result


def _one_sample_t(spec: StudySpec, a: Sample, b: Optional[Sample], test_id: str) -> TestResult:
    _need_sd(a, "A one-sample t-test")
    mu0 = spec.hypothesized
    n, mean, sd = a.n, a.mean, a.sd
    if sd == 0:
        if mean == mu0:
            t_stat, pvalue, df = 0.0, 1.0, n - 1
        else:
            t_stat = float("inf") if mean > mu0 else float("-inf")
            df = n - 1
            if spec.alternative == "two-sided":
                pvalue = 0.0
            elif spec.alternative == "greater":
                pvalue = 0.0 if t_stat > 0 else 1.0
            else:
                pvalue = 0.0 if t_stat < 0 else 1.0
        tcrit = float(stats.t.ppf(1 - spec.alpha / 2, df))
        ci_low, ci_high = mean, mean
        crit_low, crit_high = _crit_from_dist(stats.t, df, spec.alpha, spec.alternative)
        sym, words = _hyp_mean(a.name, mu0, spec.alternative)
        return TestResult(
            test_id=test_id,
            test_name=TEST_NAMES[test_id],
            hypotheses_symbols=sym,
            hypotheses_words=words,
            alternative=spec.alternative,
            alpha=spec.alpha,
            statistic_name="t",
            statistic=float(t_stat),
            df=df,
            pvalue=pvalue,
            critical_low=crit_low,
            critical_high=crit_high,
            reject=_reject(pvalue, spec.alpha),
            ci_low=ci_low,
            ci_high=ci_high,
            ci_level=1 - spec.alpha,
            formula_lines=[
                f"s = 0, so the t statistic is undefined as a ratio. "
                f"All observations equal {mean:g}.",
            ],
            sample_summaries=[f"{a.name}: n = {n}, x̄ = {mean:.6g}, s = 0"],
            assumptions=[
                AssumptionLine(
                    "Variation",
                    "A t-test needs a sample standard deviation.",
                    "Every value in the sample is the same, so s = 0.",
                )
            ],
            notes=[],
        )
    se = sd / np.sqrt(n)
    if a.has_raw():
        res = stats.ttest_1samp(a.values, mu0, alternative=spec.alternative)
        t_stat, pvalue, df = float(res.statistic), float(res.pvalue), float(res.df)
        ci = stats.ttest_1samp(a.values, mu0, alternative="two-sided").confidence_interval(
            confidence_level=1 - spec.alpha
        )
        ci_low, ci_high = float(ci.low), float(ci.high)
    else:
        t_stat = (mean - mu0) / se
        df = n - 1
        dist = stats.t
        if spec.alternative == "two-sided":
            pvalue = float(2 * dist.sf(abs(t_stat), df))
        elif spec.alternative == "greater":
            pvalue = float(dist.sf(t_stat, df))
        else:
            pvalue = float(dist.cdf(t_stat, df))
        tcrit = float(stats.t.ppf(1 - spec.alpha / 2, df))
        ci_low, ci_high = mean - tcrit * se, mean + tcrit * se
    crit_low, crit_high = _crit_from_dist(stats.t, df, spec.alpha, spec.alternative)
    sym, words = _hyp_mean(a.name, mu0, spec.alternative)
    return TestResult(
        test_id=test_id,
        test_name=TEST_NAMES[test_id],
        hypotheses_symbols=sym,
        hypotheses_words=words,
        alternative=spec.alternative,
        alpha=spec.alpha,
        statistic_name="t",
        statistic=float(t_stat),
        df=df,
        pvalue=pvalue,
        critical_low=crit_low,
        critical_high=crit_high,
        reject=_reject(pvalue, spec.alpha),
        ci_low=ci_low,
        ci_high=ci_high,
        ci_level=1 - spec.alpha,
        formula_lines=[
            f"t = (x̄ − μ0) / (s / √n) = ({mean:.6g} − {mu0:g}) / ({sd:.6g} / √{n}) = {float(t_stat):.6g}",
            f"degrees of freedom = n − 1 = {n} − 1 = {df:g}",
        ],
        sample_summaries=[
            f"{a.name}: n = {n}, x̄ = {mean:.6g}, s = {sd:.6g} (Bessel-corrected)"
        ],
        assumptions=[
            AssumptionLine(
                "Normality (or large n)",
                "The population is normal, or n is large enough that the sampling distribution of the mean is approximately normal.",
                normality_check(a),
            ),
            AssumptionLine(
                "Unknown σ",
                "The population standard deviation is estimated by s, so the t distribution is used.",
                "If n > 30, Section 4.5 also allows a large-sample z approximation; that is a separate choice in the questionnaire.",
            ),
            AssumptionLine(
                "Independence",
                "The observations are a random sample.",
                "This is taken from how the data were collected; it is not tested by the program.",
            ),
        ],
        notes=[],
    )


def _one_sample_z(spec: StudySpec, a: Sample, b: Optional[Sample], test_id: str) -> TestResult:
    mu0 = spec.hypothesized
    n, mean = a.n, a.mean
    if spec.sigma_known:
        if spec.sigma is None:
            raise ValueError("A z-test with known σ needs the population standard deviation.")
        sigma = spec.sigma
        sigma_label = "σ"
        sigma_note = "The population standard deviation was supplied."
    else:
        _need_sd(a, "A large-sample z-test")
        sigma = a.sd
        sigma_label = "s"
        sigma_note = (
            f"σ is unknown. With n = {n} > 30, the book’s large-sample approximation uses s in place of σ "
            "and a normal reference distribution. The t-test is still available and is the more conservative choice."
        )
    se = sigma / np.sqrt(n)
    z = (mean - mu0) / se
    if spec.alternative == "two-sided":
        pvalue = float(2 * stats.norm.sf(abs(z)))
    elif spec.alternative == "greater":
        pvalue = float(stats.norm.sf(z))
    else:
        pvalue = float(stats.norm.cdf(z))
    zc = float(stats.norm.ppf(1 - spec.alpha / 2))
    ci_low, ci_high = mean - zc * se, mean + zc * se
    crit_low, crit_high = _crit_from_dist(stats.norm, None, spec.alpha, spec.alternative)
    sym, words = _hyp_mean(a.name, mu0, spec.alternative)
    return TestResult(
        test_id=test_id,
        test_name=TEST_NAMES[test_id],
        hypotheses_symbols=sym,
        hypotheses_words=words,
        alternative=spec.alternative,
        alpha=spec.alpha,
        statistic_name="z",
        statistic=float(z),
        df=None,
        pvalue=pvalue,
        critical_low=crit_low,
        critical_high=crit_high,
        reject=_reject(pvalue, spec.alpha),
        ci_low=ci_low,
        ci_high=ci_high,
        ci_level=1 - spec.alpha,
        formula_lines=[
            f"z = (x̄ − μ0) / ({sigma_label} / √n) = ({mean:.6g} − {mu0:g}) / ({sigma:.6g} / √{n}) = {float(z):.6g}",
        ],
        sample_summaries=[
            f"{a.name}: n = {n}, x̄ = {mean:.6g}, {sigma_label} = {sigma:.6g}, SE = {se:.6g}"
        ],
        assumptions=[
            AssumptionLine(
                "Normal sampling distribution",
                "Either the population is normal with known σ, or n is large enough for a normal approximation.",
                normality_check(a) if a.has_raw() else sigma_note,
            ),
            AssumptionLine("Scale of the SE", sigma_note, f"SE = {sigma_label}/√n = {se:.6g}."),
        ],
        notes=[],
    )


def _two_sample_t(spec: StudySpec, a: Sample, b: Optional[Sample], test_id: str) -> TestResult:
    if b is None:
        raise ValueError("A two-sample test needs two samples.")
    _need_sd(a, "A two-sample t-test")
    _need_sd(b, "A two-sample t-test")
    d = spec.hypothesized
    equal_var = test_id == "two_sample_pooled_t"
    n1, n2 = a.n, b.n
    m1, m2 = a.mean, b.mean
    s1, s2 = a.sd, b.sd
    if a.has_raw() and b.has_raw():
        res = stats.ttest_ind(
            a.values, b.values + d, equal_var=equal_var, alternative=spec.alternative
        )
        t_stat, pvalue, df = float(res.statistic), float(res.pvalue), float(res.df)
        ci0 = stats.ttest_ind(
            a.values, b.values, equal_var=equal_var, alternative="two-sided"
        ).confidence_interval(confidence_level=1 - spec.alpha)
        ci_low, ci_high = float(ci0.low), float(ci0.high)
    else:
        res = stats.ttest_ind_from_stats(
            m1, s1, n1, m2 + d, s2, n2, equal_var=equal_var, alternative=spec.alternative
        )
        t_stat, pvalue = float(res.statistic), float(res.pvalue)
        df = float(res.df)
        se_diff = np.sqrt(s1 ** 2 / n1 + s2 ** 2 / n2) if not equal_var else None
        if equal_var:
            sp2 = ((n1 - 1) * s1 ** 2 + (n2 - 1) * s2 ** 2) / (n1 + n2 - 2)
            se_diff = np.sqrt(sp2 * (1 / n1 + 1 / n2))
        tcrit = float(stats.t.ppf(1 - spec.alpha / 2, df))
        diff = m1 - m2
        ci_low, ci_high = diff - tcrit * se_diff, diff + tcrit * se_diff

    if equal_var:
        sp2 = ((n1 - 1) * s1 ** 2 + (n2 - 1) * s2 ** 2) / (n1 + n2 - 2)
        se = np.sqrt(sp2 * (1 / n1 + 1 / n2))
        formula = [
            f"s_p^2 = [({n1}-1)s_{a.name}^2 + ({n2}-1)s_{b.name}^2] / ({n1}+{n2}-2) = {sp2:.6g}",
            f"t = (x̄_{a.name} − x̄_{b.name} − {d:g}) / √(s_p^2 (1/n1 + 1/n2)) = {t_stat:.6g}",
            f"degrees of freedom = n1 + n2 − 2 = {df:g}",
        ]
        var_commit = "The two populations have a common variance. The pooled sample variance is used."
    else:
        se = np.sqrt(s1 ** 2 / n1 + s2 ** 2 / n2)
        formula = [
            f"t = (x̄_{a.name} − x̄_{b.name} − {d:g}) / √(s1^2/n1 + s2^2/n2) = {t_stat:.6g}",
            f"Welch degrees of freedom = {df:.4g}",
        ]
        var_commit = (
            "The two populations need not have the same variance. This is the unequal-variance "
            "counterpart of the pooled t-test in Section 4.6. The book works the pooled form; "
            "Welch is offered here because the questionnaire asks what is assumed about the variances."
        )

    crit_low, crit_high = _crit_from_dist(stats.t, df, spec.alpha, spec.alternative)
    sym, words = _hyp_diff(a.name, b.name, d, spec.alternative)
    return TestResult(
        test_id=test_id,
        test_name=TEST_NAMES[test_id],
        hypotheses_symbols=sym,
        hypotheses_words=words,
        alternative=spec.alternative,
        alpha=spec.alpha,
        statistic_name="t",
        statistic=t_stat,
        df=df,
        pvalue=pvalue,
        critical_low=crit_low,
        critical_high=crit_high,
        reject=_reject(pvalue, spec.alpha),
        ci_low=ci_low,
        ci_high=ci_high,
        ci_level=1 - spec.alpha,
        formula_lines=formula,
        sample_summaries=[
            f"{a.name}: n = {n1}, x̄ = {m1:.6g}, s^2 = {s1 ** 2:.6g}",
            f"{b.name}: n = {n2}, x̄ = {m2:.6g}, s^2 = {s2 ** 2:.6g}",
            f"Observed difference x̄_{a.name} − x̄_{b.name} = {m1 - m2:.6g}",
        ],
        assumptions=[
            AssumptionLine(
                "Independence of samples",
                "The two samples are independent of each other.",
                "Taken from your answer that the samples are not paired.",
            ),
            AssumptionLine(
                "Normality",
                "Each population is normal, or both samples are large.",
                f"{normality_check(a)} {normality_check(b)}",
            ),
            AssumptionLine("Variances", var_commit, variance_ratio_check(a, b)),
        ],
        notes=[],
    )


def _paired_t(spec: StudySpec, a: Sample, b: Optional[Sample], test_id: str) -> TestResult:
    if b is None or not a.has_raw() or not b.has_raw():
        raise ValueError("A paired t-test needs two raw lists of equal length, in matching order.")
    if a.n != b.n:
        raise ValueError("Paired samples must have the same number of observations.")
    diffs = a.values - b.values
    diff_sample = Sample(name=f"{a.name} − {b.name}", values=diffs).resolved()
    inner = StudySpec(
        parameter="one_mean",
        alternative=spec.alternative,
        hypothesized=spec.hypothesized,
        alpha=spec.alpha,
        designed_experiment=spec.designed_experiment,
        sample_a_name=diff_sample.name,
    )
    result = _one_sample_t(inner, diff_sample, None, "one_sample_t")
    result.test_id = test_id
    result.test_name = TEST_NAMES[test_id]
    result.hypotheses_symbols = result.hypotheses_symbols.replace("μ", "μ_D")
    result.hypotheses_words = (
        f"The mean of the paired differences ({a.name} minus {b.name}) is {spec.hypothesized:g}."
    )
    result.assumptions = [
        AssumptionLine(
            "Pairing",
            "Each observation in the first sample is matched with one observation in the second.",
            "Taken from your answer. The test is a one-sample t-test on the differences.",
        ),
        AssumptionLine(
            "Normality of differences",
            "The population of differences is normal, or the number of pairs is large.",
            normality_check(diff_sample),
        ),
    ]
    result.notes = []
    return result


def _one_prop_z(spec: StudySpec, a: Sample, b: Optional[Sample], test_id: str) -> TestResult:
    n = a.n
    if a.successes is not None:
        count = int(a.successes)
    elif a.has_raw() and np.all((a.values == 0) | (a.values == 1)):
        count = int(np.sum(a.values))
    elif a.mean is not None:
        count = int(round(a.mean * n))
        if abs(count / n - a.mean) > 1e-8:
            raise ValueError("For a proportion, give successes and n, or a 0/1 sample.")
    else:
        raise ValueError("A one-sample proportion test needs the number of successes and n.")
    p0 = spec.hypothesized
    phat = count / n
    ok0, check0 = proportion_conditions(n, p0, "Under H0")
    okh, checkh = proportion_conditions(n, phat, "Using p̂")
    if not ok0:
        return TestResult(
            test_id=test_id,
            test_name=TEST_NAMES[test_id],
            hypotheses_symbols="",
            hypotheses_words="",
            alternative=spec.alternative,
            alpha=spec.alpha,
            statistic_name="z",
            statistic=float("nan"),
            df=None,
            pvalue=float("nan"),
            critical_low=None,
            critical_high=None,
            reject=False,
            ci_low=None,
            ci_high=None,
            ci_level=1 - spec.alpha,
            formula_lines=[],
            sample_summaries=[f"{a.name}: {count} successes in {n} trials, p̂ = {phat:.6g}"],
            assumptions=[],
            notes=[
                "The program did not run the z-test. "
                + check0
                + " Both products should be at least 10 before the normal approximation of Section 4.5.3 is used."
            ],
            refused=True,
        )
    zstat, pvalue = proportions_ztest(count, n, value=p0, alternative=spec.alternative, prop_var=p0)
    zstat, pvalue = float(zstat), float(pvalue)
    ci_low, ci_high = proportion_confint(count, n, alpha=spec.alpha, method="normal")
    se0 = np.sqrt(p0 * (1 - p0) / n)
    crit_low, crit_high = _crit_from_dist(stats.norm, None, spec.alpha, spec.alternative)
    sym, words = _hyp_prop(p0, spec.alternative)
    notes = []
    if not okh:
        notes.append("Warning for the confidence interval: " + checkh)
    return TestResult(
        test_id=test_id,
        test_name=TEST_NAMES[test_id],
        hypotheses_symbols=sym,
        hypotheses_words=words,
        alternative=spec.alternative,
        alpha=spec.alpha,
        statistic_name="z",
        statistic=zstat,
        df=None,
        pvalue=pvalue,
        critical_low=crit_low,
        critical_high=crit_high,
        reject=_reject(pvalue, spec.alpha),
        ci_low=float(ci_low),
        ci_high=float(ci_high),
        ci_level=1 - spec.alpha,
        formula_lines=[
            f"p̂ = {count}/{n} = {phat:.6g}",
            f"z = (p̂ − p0) / √(p0(1-p0)/n) = ({phat:.6g} − {p0:g}) / {se0:.6g} = {zstat:.6g}",
        ],
        sample_summaries=[f"{a.name}: {count} successes in {n} trials, p̂ = {phat:.6g}"],
        assumptions=[
            AssumptionLine(
                "Normal approximation",
                "n p0 and n(1-p0) are large enough for a normal reference distribution.",
                check0 + " " + checkh,
            ),
            AssumptionLine(
                "Independence",
                "The trials are independent Bernoulli trials, or a random sample from a large population.",
                "Taken from how the data were collected.",
            ),
        ],
        notes=notes,
    )


def _two_prop_z(spec: StudySpec, a: Sample, b: Optional[Sample], test_id: str) -> TestResult:
    if b is None:
        raise ValueError("A two-sample proportion test needs two samples.")
    if spec.hypothesized != 0:
        raise ValueError("This draft tests H0: p1 − p2 = 0 only. A nonzero difference is not yet supported.")

    def _count(s: Sample) -> tuple[int, int]:
        n = s.n
        if s.successes is not None:
            return int(s.successes), n
        if s.has_raw() and np.all((s.values == 0) | (s.values == 1)):
            return int(np.sum(s.values)), n
        if s.mean is not None:
            return int(round(s.mean * n)), n
        raise ValueError(f"{s.name}: give successes and n, or a 0/1 sample.")

    c1, n1 = _count(a)
    c2, n2 = _count(b)
    p1, p2 = c1 / n1, c2 / n2
    pooled = (c1 + c2) / (n1 + n2)
    ok1, t1 = proportion_conditions(n1, pooled, a.name)
    ok2, t2 = proportion_conditions(n2, pooled, b.name)
    if not (ok1 and ok2):
        return TestResult(
            test_id=test_id,
            test_name=TEST_NAMES[test_id],
            hypotheses_symbols="",
            hypotheses_words="",
            alternative=spec.alternative,
            alpha=spec.alpha,
            statistic_name="z",
            statistic=float("nan"),
            df=None,
            pvalue=float("nan"),
            critical_low=None,
            critical_high=None,
            reject=False,
            ci_low=None,
            ci_high=None,
            ci_level=1 - spec.alpha,
            formula_lines=[],
            sample_summaries=[
                f"{a.name}: {c1}/{n1} = {p1:.6g}",
                f"{b.name}: {c2}/{n2} = {p2:.6g}",
            ],
            assumptions=[],
            notes=[
                "The program did not run the z-test. Both samples need n p̂ and n(1-p̂) at least 10 "
                "under the pooled estimate. " + t1 + " " + t2
            ],
            refused=True,
        )
    zstat, pvalue = proportions_ztest([c1, c2], [n1, n2], alternative=spec.alternative)
    zstat, pvalue = float(zstat), float(pvalue)
    ci_low, ci_high = confint_proportions_2indep(
        c1, n1, c2, n2, compare="diff", alpha=spec.alpha, method="wald"
    )
    se = np.sqrt(pooled * (1 - pooled) * (1 / n1 + 1 / n2))
    crit_low, crit_high = _crit_from_dist(stats.norm, None, spec.alpha, spec.alternative)
    sym, words = _hyp_two_prop(0.0, spec.alternative)
    return TestResult(
        test_id=test_id,
        test_name=TEST_NAMES[test_id],
        hypotheses_symbols=sym,
        hypotheses_words=words,
        alternative=spec.alternative,
        alpha=spec.alpha,
        statistic_name="z",
        statistic=zstat,
        df=None,
        pvalue=pvalue,
        critical_low=crit_low,
        critical_high=crit_high,
        reject=_reject(pvalue, spec.alpha),
        ci_low=float(ci_low),
        ci_high=float(ci_high),
        ci_level=1 - spec.alpha,
        formula_lines=[
            f"p̂1 = {c1}/{n1} = {p1:.6g},   p̂2 = {c2}/{n2} = {p2:.6g},   p̂ = {pooled:.6g}",
            f"z = (p̂1 − p̂2) / √(p̂(1-p̂)(1/n1 + 1/n2)) = {zstat:.6g}",
        ],
        sample_summaries=[
            f"{a.name}: {c1} successes in {n1} trials",
            f"{b.name}: {c2} successes in {n2} trials",
        ],
        assumptions=[
            AssumptionLine(
                "Normal approximation",
                "For each sample, n p̂ and n(1-p̂) are large enough, using the pooled p̂ under H0.",
                t1 + " " + t2,
            ),
            AssumptionLine(
                "Independence",
                "The two samples are independent of each other.",
                "Taken from how the data were collected.",
            ),
        ],
        notes=[],
    )
