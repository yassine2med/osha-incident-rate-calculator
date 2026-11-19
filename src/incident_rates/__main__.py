"""Command line entry point."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .core import format_table, load_periods, summarize


def main(argv: list[str] | None = None) -> int:
    """Print the TRIR and DART table for a CSV file."""
    parser = argparse.ArgumentParser(prog="incident_rates")
    parser.add_argument("csv_file", type=Path)
    args = parser.parse_args(argv)
    try:
        print(format_table(summarize(load_periods(args.csv_file))))
    except (OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
