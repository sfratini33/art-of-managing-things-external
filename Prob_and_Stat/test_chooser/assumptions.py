"""Checks named in the book, not a second testing package."""

from __future__ import annotations

from typing import Optional

import numpy as np
from scipy import stats

from .io_data import Sample


def skewness(values: np.ndarray) -> float:
    # m3 / s^3 with central moments divided by n, the sample skewness of Section 4.2.3.
    return float(stats.skew(values, bias=True))


def kurtosis(values: np.ndarray) -> float:
    # m4 / s^4 with central moments divided by n, as in Section 4.2.3; 3 for a normal distribution.
    return float(stats.kurtosis(values, fisher=False, bias=True))


def normality_check(sample: Sample) -> str:
    if not sample.has_raw():
        return (
            "Raw values were not supplied, so skewness and kurtosis cannot be computed. "
            "The test still assumes each population is normal, or that n is large enough "
            "for the central limit theorem to stand in."
        )
    sk = skewness(sample.values)
    ku = kurtosis(sample.values)
    return (
        f"{sample.name}: sample skewness = {sk:.3f} (normal is 0); "
        f"sample kurtosis = {ku:.3f} (normal is 3). "
        "Values near those targets support the assumption; a large departure is a warning, "
        "not a replacement for the test."
    )


def variance_ratio_check(a: Sample, b: Sample) -> str:
    if a.sd is None or b.sd is None or a.sd == 0 or b.sd == 0:
        return "Sample standard deviations are needed to compare the variances."
    ratio = (a.sd ** 2) / (b.sd ** 2)
    return (
        f"Sample variance ratio s_{a.name}^2 / s_{b.name}^2 = {ratio:.3f}. "
        "A ratio far from 1 is a reason to prefer the Welch form rather than the pooled t-test."
    )


def proportion_conditions(n: int, p: float, label: str, cutoff: float = 10.0) -> tuple[bool, str]:
    np_ = n * p
    nq = n * (1 - p)
    ok = np_ >= cutoff and nq >= cutoff
    text = (
        f"{label}: n p = {np_:.2f}, n(1-p) = {nq:.2f}. "
        f"The normal approximation is used in the book when both are at least {cutoff:.0f}."
    )
    return ok, text
