from pathlib import Path

import pytest

from incident_rates.__main__ import main
from incident_rates.core import Period, format_table, load_periods, rate, summarize, validate


def test_rate_basic():
    assert rate(2, 200_000) == 2.0


def test_rate_rounding():
    assert rate(1, 84_500) == 2.37


def test_rate_zero_cases():
    assert rate(0, 50_000) == 0.0


def test_rate_zero_hours_rejected():
    with pytest.raises(ValueError):
        rate(1, 0)


def test_rate_negative_cases_rejected():
    with pytest.raises(ValueError):
        rate(-1, 1000)


def test_dart_cannot_exceed_recordable():
    with pytest.raises(ValueError, match="exceed"):
        validate(Period("Q1", 1000, 1, 2))


def test_load_example():
    periods = load_periods(Path("examples/quarters.csv"))
    assert len(periods) == 4 and periods[1].dart == 1


def test_total_row_uses_combined_hours():
    rows = summarize([Period("a", 100_000, 1, 0), Period("b", 100_000, 1, 1)])
    assert rows[-1][0] == "TOTAL" and rows[-1][4] == 2.0 and rows[-1][5] == 1.0


def test_missing_column(tmp_path):
    f = tmp_path / "x.csv"
    f.write_text("period,hours_worked\nQ1,10\n")
    with pytest.raises(ValueError, match="missing columns"):
        load_periods(f)


def test_bad_number_reports_line(tmp_path):
    f = tmp_path / "x.csv"
    f.write_text("period,hours_worked,recordable_cases,dart_cases\nQ1,abc,0,0\n")
    with pytest.raises(ValueError, match="line 2"):
        load_periods(f)


def test_empty_file_rejected(tmp_path):
    f = tmp_path / "x.csv"
    f.write_text("period,hours_worked,recordable_cases,dart_cases\n")
    with pytest.raises(ValueError, match="no data"):
        load_periods(f)


def test_table_has_header_and_total():
    text = format_table(summarize([Period("Q1", 200_000, 3, 1)]))
    assert "TRIR" in text and "TOTAL" in text


def test_cli_codes(tmp_path):
    assert main(["examples/quarters.csv"]) == 0
    assert main([str(tmp_path / "missing.csv")]) == 2
