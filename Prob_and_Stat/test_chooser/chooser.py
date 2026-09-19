"""Name the test from the questionnaire. Data are not used here."""

from __future__ import annotations

from .spec import StudySpec

TEST_NAMES = {
    "one_sample_z": "One-sample z-test for a mean",
    "one_sample_t": "One-sample t-test for a mean",
    "two_sample_pooled_t": "Two-sample t-test, pooled (equal-variance) form",
    "welch_t": "Two-sample t-test, Welch (unequal-variance) form",
    "paired_t": "Paired t-test",
    "one_prop_z": "One-sample z-test for a proportion",
    "two_prop_z": "Two-sample z-test for a difference of proportions",
}


def choose_test(spec: StudySpec) -> str:
    if spec.parameter == "one_mean":
        if spec.sigma_known or spec.large_sample_z:
            return "one_sample_z"
        return "one_sample_t"
    if spec.parameter == "two_means":
        if spec.paired:
            return "paired_t"
        if spec.equal_variances:
            return "two_sample_pooled_t"
        return "welch_t"
    if spec.parameter == "one_proportion":
        return "one_prop_z"
    if spec.parameter == "two_proportions":
        return "two_prop_z"
    raise ValueError(f"Unknown parameter: {spec.parameter}")
