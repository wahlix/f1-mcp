"""
models.py — shared dataclasses for f1_mcp tools.

Keep these MCP-agnostic (no dependency on the `mcp` package here) so that
tool modules are testable and runnable completely standalone from the server.
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
    degradation_s_per_lap: float # positive = loosing time per lap

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
