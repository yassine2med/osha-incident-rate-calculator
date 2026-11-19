"""Compute OSHA TRIR and DART incident rates from period totals."""
from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path

BASE_HOURS = 200_000  # 100 full-time workers, 40 hours, 50 weeks
REQUIRED = ("period", "hours_worked", "recordable_cases", "dart_cases")


@dataclass(frozen=True)
class Period:
    """Totals for one reporting period."""

    period: str
    hours: float
    recordable: int
    dart: int


def rate(cases: int, hours: float) -> float:
    """Return cases per 200,000 hours worked, rounded to 2 decimals."""
    if hours <= 0:
        raise ValueError("hours worked must be greater than zero")
    if cases < 0:
        raise ValueError("case count cannot be negative")
    return round(cases * BASE_HOURS / hours, 2)


def validate(p: Period) -> None:
    """Reject data that cannot be right (DART cases are a subset of recordables)."""
    if p.dart > p.recordable:
        raise ValueError(f"{p.period}: DART cases ({p.dart}) exceed recordable cases ({p.recordable})")


def load_periods(path: Path) -> list[Period]:
    """Read periods from CSV with columns period, hours_worked, recordable_cases, dart_cases."""
    with open(path, newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        missing = [c for c in REQUIRED if c not in (reader.fieldnames or [])]
        if missing:
            raise ValueError(f"missing columns: {', '.join(missing)}")
        periods = []
        for line_no, row in enumerate(reader, start=2):
            try:
                p = Period(row["period"].strip(), float(row["hours_worked"]),
                           int(row["recordable_cases"]), int(row["dart_cases"]))
            except ValueError as exc:
                raise ValueError(f"line {line_no}: {exc}") from exc
            validate(p)
            periods.append(p)
    if not periods:
        raise ValueError("no data rows")
    return periods


def summarize(periods: list[Period]) -> list[tuple[str, float, int, int, float, float]]:
    """Return one row per period plus a TOTAL row: name, hours, recordable, dart, TRIR, DART rate."""
    rows = [(p.period, p.hours, p.recordable, p.dart,
             rate(p.recordable, p.hours), rate(p.dart, p.hours)) for p in periods]
    hours = sum(p.hours for p in periods)
    rec = sum(p.recordable for p in periods)
    dart = sum(p.dart for p in periods)
    rows.append(("TOTAL", hours, rec, dart, rate(rec, hours), rate(dart, hours)))
    return rows


def format_table(rows: list[tuple[str, float, int, int, float, float]]) -> str:
    """Render summary rows as a text table."""
    lines = [f"{'PERIOD':<10} {'HOURS':>10} {'RECORD.':>8} {'DART':>5} {'TRIR':>6} {'DART RATE':>10}"]
    for name, hours, rec, dart, trir, dart_rate in rows:
        lines.append(f"{name:<10} {hours:>10,.0f} {rec:>8} {dart:>5} {trir:>6.2f} {dart_rate:>10.2f}")
    return "\n".join(lines)
