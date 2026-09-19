"""Data from Section 4, for the notebook sessions and the bundled CSV files."""

from __future__ import annotations

import csv
from pathlib import Path

from .io_data import sample_from_summary, sample_from_values
from .report import format_report
from .spec import StudySpec
from .tests import run_test

EXAMPLES_DIR = Path(__file__).resolve().parent.parent / "examples"

BATTERY_X = [
    29.9389, 28.6328, 31.5358, 29.5931, 25.2887, 28.1834, 25.6264, 30.8459, 20.3379, 27.4113,
    23.1402, 27.8455, 19.7259, 30.2547, 35.4607, 26.3644, 26.8253, 34.5251, 29.3185, 29.9598,
    26.2742, 31.0308, 27.1553, 25.9372, 28.5168, 26.6379, 31.6680, 25.8408, 27.5514, 27.9000,
]
BATTERY_Y = [
    23.6183, 22.9001, 26.7005, 21.5633, 22.8037, 22.4295, 29.2587, 24.0003, 21.0254, 25.4782,
    22.5474, 23.0955, 16.1366, 22.3171, 22.4769, 17.1468, 22.1785, 20.2322, 20.8528, 16.6673,
    22.9132, 28.8552, 20.4779, 21.0232, 26.0684, 24.0126, 22.5906, 25.0016, 26.5045, 22.3598,
]

PING_PONG = [
    47, 44, 44, 47, 49, 47, 45, 48, 48, 46,
    49, 50, 44, 44, 48, 49, 49, 49, 46, 45,
]


def write_example_files(directory: Path | None = None, overwrite: bool = False) -> Path:
    """Write the bundled example files if they are missing. Existing files are left alone."""
    directory = Path(directory) if directory else EXAMPLES_DIR
    directory.mkdir(parents=True, exist_ok=True)
    battery_file = directory / "batteries.csv"
    if overwrite or not battery_file.exists():
        with battery_file.open("w", newline="", encoding="utf-8") as fh:
            writer = csv.writer(fh, lineterminator="\n")
            writer.writerow(["TypeX", "TypeY"])
            writer.writerows(zip(BATTERY_X, BATTERY_Y))
    ping_file = directory / "ping_pong.csv"
    if overwrite or not ping_file.exists():
        with ping_file.open("w", newline="", encoding="utf-8") as fh:
            writer = csv.writer(fh, lineterminator="\n")
            writer.writerow(["blue_count"])
            for value in PING_PONG:
                writer.writerow([value])
    return directory


def battery_spec() -> StudySpec:
    return StudySpec(
        parameter="two_means",
        alternative="greater",
        hypothesized=3.0,
        alpha=0.05,
        designed_experiment=False,
        paired=False,
        equal_variances=True,
        sample_a_name="TypeX",
        sample_b_name="TypeY",
    )


def ping_pong_spec(mu0: float = 50.0) -> StudySpec:
    return StudySpec(
        parameter="one_mean",
        alternative="two-sided",
        hypothesized=mu0,
        alpha=0.05,
        designed_experiment=False,
        sample_a_name="blue_count",
    )


def material_spec(use_z: bool = True) -> StudySpec:
    return StudySpec(
        parameter="one_mean",
        alternative="greater",
        hypothesized=25.0,
        alpha=0.05,
        designed_experiment=False,
        large_sample_z=use_z,
        sample_a_name="strength",
    )


def proportion_spec(all_samples: bool = False) -> StudySpec:
    return StudySpec(
        parameter="one_proportion",
        alternative="two-sided",
        hypothesized=0.5,
        alpha=0.05,
        designed_experiment=False,
        sample_a_name="all twenty samples" if all_samples else "first sample of Table 21",
    )


def battery_report() -> str:
    a = sample_from_values("TypeX", BATTERY_X)
    b = sample_from_values("TypeY", BATTERY_Y)
    return format_report(run_test(battery_spec(), a, b), battery_spec())


def ping_pong_report(mu0: float = 50.0) -> str:
    a = sample_from_values("blue_count", PING_PONG)
    spec = ping_pong_spec(mu0)
    return format_report(run_test(spec, a), spec)


def material_report(use_z: bool = True) -> str:
    spec = material_spec(use_z)
    a = sample_from_summary("strength", n=50, mean=25.9, sd=4.3)
    return format_report(run_test(spec, a), spec)


def proportion_report(all_samples: bool = False) -> str:
    """One-sample proportion test: the first sample of Table 21 (47 of 100), or all twenty (938 of 2000)."""
    spec = proportion_spec(all_samples)
    if all_samples:
        a = sample_from_summary(spec.sample_a_name, n=100 * len(PING_PONG), successes=sum(PING_PONG))
    else:
        a = sample_from_summary(spec.sample_a_name, n=100, successes=PING_PONG[0])
    return format_report(run_test(spec, a), spec)
