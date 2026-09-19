"""Read sample values from summaries, pasted text, CSV, or Excel."""

from __future__ import annotations

import csv
from dataclasses import dataclass
from io import BytesIO, StringIO
from pathlib import Path
from typing import Optional, Sequence, Union

import numpy as np


@dataclass
class Sample:
    name: str = "Sample"
    values: Optional[np.ndarray] = None
    n: Optional[int] = None
    mean: Optional[float] = None
    sd: Optional[float] = None
    successes: Optional[int] = None

    def has_raw(self) -> bool:
        return self.values is not None and len(self.values) > 0

    def resolved(self) -> "Sample":
        if self.has_raw():
            v = np.asarray(self.values, dtype=float)
            n = int(v.size)
            mean = float(np.mean(v))
            sd = float(np.std(v, ddof=1)) if n > 1 else None
            successes = self.successes
            if successes is None and np.all((v == 0) | (v == 1)):
                successes = int(np.sum(v))
            return Sample(self.name, v, n, mean, sd, successes)
        if self.n is None:
            raise ValueError(f"{self.name}: provide either a list of values or a summary (n, mean, s).")
        n = int(self.n)
        mean = self.mean
        sd = self.sd
        successes = self.successes
        if successes is not None and mean is None:
            mean = successes / n
        if mean is None:
            raise ValueError(f"{self.name}: summary input needs a mean, or successes for a proportion.")
        return Sample(self.name, None, n, float(mean), None if sd is None else float(sd), successes)


def parse_list(text: str) -> np.ndarray:
    raw = text.replace(";", ",").replace("\t", " ").replace("\n", " ").replace("\r", " ")
    parts = [p.strip() for p in raw.split(",") if p.strip()]
    if len(parts) <= 1:
        parts = [p for p in raw.split() if p]
    if not parts:
        raise ValueError("No numbers were found in the pasted text.")
    try:
        return np.array([float(p) for p in parts], dtype=float)
    except ValueError as exc:
        raise ValueError(f"Could not parse a number in the pasted text: {exc}") from exc


def sample_from_summary(
    name: str,
    n: int,
    mean: Optional[float] = None,
    sd: Optional[float] = None,
    successes: Optional[int] = None,
) -> Sample:
    return Sample(name=name, n=n, mean=mean, sd=sd, successes=successes).resolved()


def sample_from_values(name: str, values: Sequence[float]) -> Sample:
    return Sample(name=name, values=np.asarray(values, dtype=float)).resolved()


def _samples_from_columns(headers: list[str], columns: list[list[float]]) -> list[Sample]:
    samples = []
    for header, col in zip(headers, columns):
        if col:
            samples.append(sample_from_values(header, col))
    if not samples:
        raise ValueError("The file has no numeric columns.")
    return samples


def _read_csv_table(text_lines) -> list[Sample]:
    rows = list(csv.reader(text_lines))
    if not rows:
        raise ValueError("The file has no data rows.")
    first = rows[0]

    def _is_float(s: str) -> bool:
        try:
            float(s)
            return True
        except ValueError:
            return False

    if all(_is_float(cell) for cell in first if cell.strip()):
        headers = [f"Sample {i + 1}" for i in range(len(first))]
        data_rows = rows
    else:
        headers = [cell.strip() or f"Sample {i + 1}" for i, cell in enumerate(first)]
        data_rows = rows[1:]
    columns: list[list[float]] = [[] for _ in headers]
    for row in data_rows:
        for i, cell in enumerate(row):
            if i >= len(columns) or not str(cell).strip():
                continue
            columns[i].append(float(cell))
    return _samples_from_columns(headers, columns)


def load_file(path: Union[str, Path]) -> list[Sample]:
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(path)
    suffix = path.suffix.lower()
    if suffix in {".csv", ".txt"}:
        with path.open(encoding="utf-8-sig", newline="") as fh:
            return _read_csv_table(fh)
    if suffix in {".xlsx", ".xls"}:
        import pandas as pd

        df = pd.read_excel(path)
        headers = [str(c) for c in df.columns]
        columns = []
        for col in df.columns:
            series = pd.to_numeric(df[col], errors="coerce").dropna()
            columns.append([float(x) for x in series.tolist()])
        return _samples_from_columns(headers, columns)
    raise ValueError("Use a CSV or Excel file.")


def load_bytes(content: bytes, filename: str) -> list[Sample]:
    name = filename.lower()
    if name.endswith((".xlsx", ".xls")):
        import pandas as pd

        df = pd.read_excel(BytesIO(content))
        headers = [str(c) for c in df.columns]
        columns = []
        for col in df.columns:
            series = pd.to_numeric(df[col], errors="coerce").dropna()
            columns.append([float(x) for x in series.tolist()])
        return _samples_from_columns(headers, columns)
    text = content.decode("utf-8-sig")
    return _read_csv_table(StringIO(text))
