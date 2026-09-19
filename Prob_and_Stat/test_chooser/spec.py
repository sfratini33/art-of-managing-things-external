"""Study description collected from the Section 5 questionnaire."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, Optional

Parameter = Literal["one_mean", "two_means", "one_proportion", "two_proportions"]
Alternative = Literal["two-sided", "greater", "less"]
DataMode = Literal["summary", "paste", "file"]


@dataclass
class StudySpec:
    parameter: Parameter
    alternative: Alternative = "two-sided"
    hypothesized: float = 0.0
    alpha: float = 0.05
    designed_experiment: bool = False
    paired: bool = False
    sigma_known: bool = False
    sigma: Optional[float] = None
    equal_variances: bool = True
    large_sample_z: bool = False
    sample_a_name: str = "Sample A"
    sample_b_name: str = "Sample B"
