"""Check the draft against the Section 4.6 numerical examples."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from test_chooser.examples import (
    BATTERY_X,
    BATTERY_Y,
    PING_PONG,
    battery_report,
    battery_spec,
    material_report,
    material_spec,
    ping_pong_report,
    ping_pong_spec,
    proportion_report,
    write_example_files,
)
from test_chooser.assumptions import kurtosis, skewness
from test_chooser.io_data import sample_from_summary, sample_from_values
from test_chooser.spec import StudySpec
from test_chooser.tests import run_test


def main() -> int:
    write_example_files()
    bat = run_test(
        battery_spec(),
        sample_from_values("TypeX", BATTERY_X),
        sample_from_values("TypeY", BATTERY_Y),
    )
    mat = run_test(material_spec(True), sample_from_summary("strength", n=50, mean=25.9, sd=4.3))
    pp = run_test(ping_pong_spec(50), sample_from_values("blue_count", PING_PONG))
    pp47 = run_test(ping_pong_spec(47), sample_from_values("blue_count", PING_PONG))

    print(battery_report())
    print("\n" + "-" * 72 + "\n")
    print(ping_pong_report(50))
    print("\n" + "-" * 72 + "\n")
    print(ping_pong_report(47))
    print("\n" + "-" * 72 + "\n")
    print(material_report(True))
    print("\n" + "-" * 72 + "\n")
    print(proportion_report())
    print("\n" + "-" * 72 + "\n")
    print(proportion_report(all_samples=True))

    x = sample_from_values("TypeX", BATTERY_X)
    y = sample_from_values("TypeY", BATTERY_Y)
    pooled_sum = run_test(
        battery_spec(),
        sample_from_summary("TypeX", n=x.n, mean=x.mean, sd=x.sd),
        sample_from_summary("TypeY", n=y.n, mean=y.mean, sd=y.sd),
    )
    welch_spec = battery_spec()
    welch_spec.equal_variances = False
    welch_sum = run_test(
        welch_spec,
        sample_from_summary("TypeX", n=x.n, mean=x.mean, sd=x.sd),
        sample_from_summary("TypeY", n=y.n, mean=y.mean, sd=y.sd),
    )
    welch_raw = run_test(welch_spec, x, y)
    all_prop = run_test(
        StudySpec(parameter="one_proportion", hypothesized=0.5),
        sample_from_summary("all", n=2000, successes=sum(PING_PONG)),
    )
    try:
        run_test(
            StudySpec(parameter="one_mean", hypothesized=25, large_sample_z=True),
            sample_from_summary("small", n=20, mean=25.9, sd=4.3),
        )
        small_z_refused = False
    except ValueError:
        small_z_refused = True

    checks = [
        ("battery t", abs(bat.statistic - 2.62145) < 5e-4),
        ("battery p", abs(bat.pvalue - 0.005581) < 5e-6),
        ("battery df", abs(bat.df - 58) < 1e-9),
        ("battery reject", bat.reject is True),
        ("battery crit", abs(bat.critical_high - 1.67155) < 5e-4),
        ("material z", abs(mat.statistic - 1.48026) < 5e-4),
        ("material p", abs(mat.pvalue - 0.0694) < 5e-4),
        ("material not reject", mat.reject is False),
        ("ping-pong reject", pp.reject is True),
        ("ping-pong 47 not reject", pp47.reject is False),
        ("battery skewness X (Section 4.6.6: -.2634)", abs(skewness(x.values) + 0.2634) < 5e-5),
        ("battery skewness Y (Section 4.6.6: -.0808)", abs(skewness(y.values) + 0.0808) < 5e-5),
        ("battery kurtosis X (Section 4.6.6: 3.6610)", abs(kurtosis(x.values) - 3.6610) < 5e-5),
        ("battery kurtosis Y (Section 4.6.6: 3.3172)", abs(kurtosis(y.values) - 3.3172) < 5e-5),
        ("pooled t from summaries = from raw", abs(pooled_sum.statistic - bat.statistic) < 1e-9 and pooled_sum.df == 58),
        ("Welch t from summaries = from raw", abs(welch_sum.statistic - welch_raw.statistic) < 1e-9
            and abs(welch_sum.df - welch_raw.df) < 1e-9 and abs(welch_sum.pvalue - welch_raw.pvalue) < 1e-12),
        ("all twenty samples as a proportion: z", abs(all_prop.statistic + 2.7727) < 5e-4),
        ("large-sample z refused for n = 20", small_z_refused),
    ]
    print("\nCHECKS")
    ok = True
    for name, passed in checks:
        print(f"  {'OK' if passed else 'FAIL'}: {name}")
        ok = ok and passed
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
