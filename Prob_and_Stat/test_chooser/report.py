"""Book-style report for a completed test."""

from __future__ import annotations

from .spec import StudySpec
from .tests import TestResult


def _fmt(x: float, digits: int = 6) -> str:
    if x is None:
        return "—"
    ax = abs(x)
    if ax != 0 and (ax < 1e-4 or ax >= 1e6):
        return f"{x:.4e}"
    return f"{x:.{digits}g}"


def _conclusion(result: TestResult) -> str:
    alpha = result.alpha
    if result.refused:
        return "No decision. The test was not run."
    if result.reject:
        return (
            f"Reject H0 at α = {alpha:g}. The data are statistically significant at this level. "
            "That is evidence against the null hypothesis, not a probability that H0 is false."
        )
    return (
        f"Do not reject H0 at α = {alpha:g}. The result is not statistically significant at this level. "
        "Failing to reject is not the same as showing that H0 is true. It often means only that "
        "the sample was too small to tell, or that the data are compatible with H0."
    )


def _critical_line(result: TestResult) -> str:
    if result.critical_low is not None and result.critical_high is not None:
        return (
            f"Critical values (two-tailed): ±{_fmt(result.critical_high)} "
            f"(cut off α/2 = {result.alpha / 2:g} in each tail)"
        )
    if result.critical_high is not None:
        return f"Critical value (upper tail): {_fmt(result.critical_high)}"
    return f"Critical value (lower tail): {_fmt(result.critical_low)}"


def format_report(result: TestResult, spec: StudySpec) -> str:
    lines: list[str] = []
    lines.append("CHOOSING AND RUNNING A TEST")
    lines.append("=" * 72)
    if result.refused:
        lines.append("TEST NOT RUN")
        lines.append(result.test_name)
        lines.extend(result.sample_summaries)
        lines.extend(result.notes)
        return "\n".join(lines)

    lines.append("TEST CHOSEN")
    lines.append(result.test_name)
    lines.append("")
    lines.append("HYPOTHESES")
    lines.append(result.hypotheses_symbols)
    lines.append(result.hypotheses_words)
    lines.append(f"Level of significance α = {spec.alpha:g}")
    lines.append("")
    lines.append("ASSUMPTIONS THIS CHOICE COMMITS YOU TO")
    for i, item in enumerate(result.assumptions, start=1):
        lines.append(f"{i}. {item.name}")
        lines.append(f"   Committed: {item.committed}")
        lines.append(f"   Check:     {item.check}")
    lines.append("")
    lines.append("SAMPLE")
    lines.extend(result.sample_summaries)
    lines.append("")
    lines.append("ARITHMETIC")
    lines.extend(result.formula_lines)
    extra = f"{result.statistic_name} = {_fmt(result.statistic)}"
    if result.df is not None:
        extra += f",   df = {_fmt(result.df, 4)}"
    lines.append(extra)
    lines.append(_critical_line(result))
    lines.append(f"p-value = {_fmt(result.pvalue)}")
    lines.append("")
    lines.append("CONCLUSION")
    lines.append(_conclusion(result))
    if result.ci_low is not None and result.ci_high is not None:
        pct = 100 * result.ci_level
        lines.append("")
        lines.append("MATCHING TWO-SIDED CONFIDENCE INTERVAL")
        lines.append(
            f"A {pct:g}% interval for the parameter of the test is "
            f"({_fmt(result.ci_low)}, {_fmt(result.ci_high)})."
        )
        if spec.alternative == "two-sided":
            inside = result.ci_low <= spec.hypothesized <= result.ci_high
            if inside:
                lines.append(
                    "The hypothesized value lies inside the interval, which agrees with not rejecting H0 "
                    "in a two-sided test at this α (Section 4.6.8)."
                    if not result.reject
                    else "Check the numbers: a two-sided test and the matching CI should agree about H0."
                )
            else:
                lines.append(
                    "The hypothesized value lies outside the interval, which agrees with rejecting H0 "
                    "in a two-sided test at this α (Section 4.6.8)."
                    if result.reject
                    else "Check the numbers: a two-sided test and the matching CI should agree about H0."
                )
        else:
            lines.append(
                "The test itself is one-sided. The interval above is the ordinary two-sided interval "
                "for the same data; the exact match to a one-sided test is a one-sided bound "
                "(Section 4.6.8)."
            )
    if result.notes:
        lines.append("")
        lines.append("CAVEATS")
        lines.extend(result.notes)
    return "\n".join(lines)
