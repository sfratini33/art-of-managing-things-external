"""Choose and run a test, in the language of the book."""

from .chooser import TEST_NAMES, choose_test
from .examples import (
    battery_report,
    material_report,
    ping_pong_report,
    proportion_report,
    write_example_files,
)
from .io_data import load_file, parse_list, sample_from_summary, sample_from_values
from .notebook_ui import analyze, show_chooser
from .spec import StudySpec

__all__ = [
    "StudySpec",
    "TEST_NAMES",
    "analyze",
    "choose_test",
    "show_chooser",
    "sample_from_summary",
    "sample_from_values",
    "parse_list",
    "load_file",
    "battery_report",
    "ping_pong_report",
    "material_report",
    "proportion_report",
    "write_example_files",
]
