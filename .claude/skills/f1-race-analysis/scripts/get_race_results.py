#!/usr/bin/env python3
"""
get_race_results.py — CLI wrapper around f1_lib.race_results.get_race_results().

Usage:
    python scripts/get_race_results.py --year 2026 --gp Spain --session R

Prints the result as JSON to stdout. Errors go to stderr with a non-zero exit code.
"""

import argparse
import json
import sys
from pathlib import Path

# f1_lib is a standalone package living alongside this script, not pip-installed —
# make sure Python can find it regardless of the working directory this is run from.
sys.path.insert(0, str(Path(__file__).resolve().parent))

from f1_lib.race_results import get_race_results  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description="Fetch classified F1 race results for a session.")
    parser.add_argument("--year", type=int, required=True, help="Season, e.g. 2026")
    parser.add_argument("--gp", type=str, required=True, help='Grand Prix name, e.g. "Spain"')
    parser.add_argument(
        "--session",
        type=str,
        default="R",
        help='Session type: R (race, default), Q, FP1/FP2/FP3, S (sprint)',
    )
    args = parser.parse_args()

    try:
        result = get_race_results(
            year=args.year,
            gp=args.gp,
            session_type=args.session,
        )
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)

    print(json.dumps(result.to_dict(), indent=2))


if __name__ == "__main__":
    main()