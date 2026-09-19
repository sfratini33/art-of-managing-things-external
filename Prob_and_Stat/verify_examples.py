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
from test_chooser.io_data import sample_from_summary, sample_from_values
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
    ]
    print("\nCHECKS")
    ok = True
    for name, passed in checks:
        print(f"  {'OK' if passed else 'FAIL'}: {name}")
        ok = ok and passed
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
