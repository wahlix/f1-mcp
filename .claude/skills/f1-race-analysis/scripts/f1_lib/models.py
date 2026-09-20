"""
models.py — shared dataclasses for f1_lib scripts.

Keep these dependency-free (no argparse/json here) so the CLI wrapper
scripts are the only place that touches stdin/stdout/argv.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class StintSummary:
    stint: int
    compound: str
    fresh_tyre: bool
    lap_start: int
    lap_end: int
    laps_on_tyre: int
    avg_lap_time_s: float
    best_lap_time_s: float
    degradation_s_per_lap: float  # positive = losing time per lap


@dataclass
class TyreStrategyResult:
    driver: str
    team: str
    year: int
    gp: str
    session: str
    stints: list[StintSummary] = field(default_factory=list)
    total_pit_stops: int = 0

    def to_dict(self) -> dict:
        return {
            "driver": self.driver,
            "team": self.team,
            "year": self.year,
            "gp": self.gp,
            "session": self.session,
            "total_pit_stops": self.total_pit_stops,
            "stints": [s.__dict__ for s in self.stints],
        }


@dataclass
class RaceResultEntry:
    position: int | None  # None if unclassified (e.g. disqualified)
    classified_position: str  # e.g. "1", "R" (retired), "D" (disqualified)
    driver: str
    driver_number: str
    team: str
    grid_position: int | None
    status: str  # "Finished", "+1 Lap", "Retired", etc.
    points: float
    laps_completed: int
    gap_to_winner_s: float | None  # seconds behind the winner
    total_time_s: float | None  # winner's total race time in seconds (winner only)


@dataclass
class RaceResultsSummary:
    year: int
    gp: str
    session: str
    results: list[RaceResultEntry] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "year": self.year,
            "gp": self.gp,
            "session": self.session,
            "results": [r.__dict__ for r in self.results],
        }