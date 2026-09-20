"""
f1_lib/race_results.py — fetches classified race results per driver from FastF1 data.
"""

from __future__ import annotations

import math

import fastf1
import pandas as pd

from f1_lib.cache import ensure_cache
from f1_lib.models import RaceResultEntry, RaceResultsSummary


def _nan_to_none(value):
    """FastF1/pandas represents missing numeric values as NaN, not None."""
    if value is None:
        return None
    if isinstance(value, float) and math.isnan(value):
        return None
    return value


def _timedelta_to_seconds(value) -> float | None:
    if value is None or pd.isna(value):
        return None
    return float(value.total_seconds())


def get_race_results(
    year: int,
    gp: str,
    session_type: str = "R",
) -> RaceResultsSummary:
    """
    Fetches classified results for every driver in a given session.

    Parameters
    ----------
    year : int
        Season, e.g. 2026.
    gp : str
        Grand Prix name, e.g. "Spain" (Madrid/Madring) or "Monza".
    session_type : str
        "R" (race), "Q" (quali), "FP1"/"FP2"/"FP3", "S" (sprint).
    """
    ensure_cache()

    session = fastf1.get_session(year, gp, session_type)
    session.load(telemetry=False, weather=False, messages=False)

    results = session.results
    if results.empty:
        raise ValueError(f"No results found for {year} {gp} ({session_type})")

    # Laps aren't part of the results table itself — derive completed laps
    # per driver from the lap data we already loaded above.
    laps_completed_by_driver: dict[str, int] = {}
    if not session.laps.empty:
        laps_completed_by_driver = (
            session.laps.groupby("Driver")["LapNumber"].max().astype(int).to_dict()
        )

    summary = RaceResultsSummary(year=year, gp=gp, session=session_type)

    for _, row in results.iterrows():
        abbreviation = row["Abbreviation"]
        position = _nan_to_none(row["Position"])
        time_value = _timedelta_to_seconds(row["Time"])

        # FastF1 convention: the winner's Time is the total race duration;
        # every other driver's Time is their gap behind the winner.
        is_winner = position == 1
        total_time_s = time_value if is_winner else None
        gap_to_winner_s = None if is_winner else time_value

        summary.results.append(
            RaceResultEntry(
                position=int(position) if position is not None else None,
                classified_position=str(row["ClassifiedPosition"]),
                driver=abbreviation,
                driver_number=str(row["DriverNumber"]),
                team=row["TeamName"],
                grid_position=(
                    int(row["GridPosition"])
                    if _nan_to_none(row["GridPosition"]) is not None
                    else None
                ),
                status=row["Status"],
                points=float(row["Points"]),
                laps_completed=laps_completed_by_driver.get(abbreviation, 0),
                gap_to_winner_s=gap_to_winner_s,
                total_time_s=total_time_s,
            )
        )

    # Sort by position, with unclassified drivers (None) pushed to the end.
    summary.results.sort(key=lambda r: (r.position is None, r.position))
    return summary