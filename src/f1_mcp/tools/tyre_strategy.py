"""
tools/tyre_strategy.py — extracts tyre strategy per driver from FastF1 data.

Pure function, no MCP dependency here. server.py wraps get_tyre_strategy()
in a @mcp.tool() and returns .to_dict().
"""

from __future__ import annotations

import fastf1
import numpy as np
import pandas as pd

from f1_mcp.cache import ensure_cache
from f1_mcp.models import StintSummary, TyreStrategyResult


def _lap_time_to_seconds(series: pd.Series) -> pd.Series:
    return series.dt.total_seconds()


def get_tyre_strategy(
    year: int,
    gp: str,
    driver: str,
    session_type: str = "R",
) -> TyreStrategyResult:
    """
    Fetches and summarizes the tyre strategy for a driver in a given session.

    Parameters
    ----------
    year : int
        Season, e.g. 2026.
    gp : str
        Grand Prix name, e.g. "Spain" (Madrid/Madring) or "Monza".
    driver : str
        Driver's 3-letter code, e.g. "ANT", "NOR", "VER".
    session_type : str
        "R" (race), "Q" (quali), "FP1"/"FP2"/"FP3", "S" (sprint).
    """
    ensure_cache()

    session = fastf1.get_session(year, gp, session_type)
    session.load(telemetry=False, weather=False, messages=False)

    laps = session.laps.pick_driver(driver).copy()
    if laps.empty:
        raise ValueError(f"No lap data found for {driver} in {year} {gp} ({session_type})")

    laps["LapTimeSeconds"] = _lap_time_to_seconds(laps["LapTime"])

    team = laps["Team"].iloc[0]
    result = TyreStrategyResult(driver=driver, team=team, year=year, gp=gp, session=session_type)

    for stint_num, stint_laps in laps.groupby("Stint"):
        stint_laps = stint_laps.sort_values("LapNumber")
        valid_laps = stint_laps.dropna(subset=["LapTimeSeconds"])

        if valid_laps.empty:
            continue

        # Degradation: simple linear slope (seconds/lap) over the stint's valid laps.
        # Positive slope = lap times getting worse = tyre degrading.
        if len(valid_laps) >= 2:
            x = valid_laps["TyreLife"].to_numpy(dtype=float)
            y = valid_laps["LapTimeSeconds"].to_numpy(dtype=float)
            slope = float(np.polyfit(x, y, 1)[0])
        else:
            slope = float("nan")

        result.stints.append(
            StintSummary(
                stint=int(stint_num),
                compound=stint_laps["Compound"].iloc[0],
                fresh_tyre=bool(stint_laps["FreshTyre"].iloc[0]),
                lap_start=int(stint_laps["LapNumber"].min()),
                lap_end=int(stint_laps["LapNumber"].max()),
                laps_on_tyre=len(stint_laps),
                avg_lap_time_s=round(float(valid_laps["LapTimeSeconds"].mean()), 3),
                best_lap_time_s=round(float(valid_laps["LapTimeSeconds"].min()), 3),
                degradation_s_per_lap=round(slope, 4),
            )
        )

    result.total_pit_stops = max(len(result.stints) - 1, 0)
    return result
