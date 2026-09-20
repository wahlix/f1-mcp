---
name: f1-race-analysis
description: Analyze Formula 1 race data — tyre strategies, pit stops, stint degradation, and classified race results — using real FastF1 telemetry data instead of guessing from general knowledge or web search. Use this skill whenever the user asks about F1 tyre strategy, pit stop timing, stint length, tyre compound choices, tyre degradation, race results, finishing positions, points scored, grid vs. finish position, gaps to the leader, or DNF/retirement status for a specific driver, race, or season — even if they just say "how did [driver] do at [race]" or use informal track nicknames (e.g. "Madring" for the Madrid GP, "Monza" for the Italian GP). Always prefer these scripts over web search or general knowledge when the query concerns a specific session's actual results or tyre data, since FastF1 provides ground-truth timing data rather than reported/summarized data.
---

# F1 Race Analysis

Fetches real Formula 1 session data (race results, tyre strategy) via the
[FastF1](https://docs.fastf1.dev) library and returns it as structured JSON.

## Setup (once per environment)

```bash
pip install -r requirements.txt
```

## Available scripts

### `scripts/get_tyre_strategy.py`

Stint-by-stint tyre strategy for one driver in one session: compound,
lap range, average/best lap time, and a linear degradation slope
(seconds/lap over the stint).

```bash
python scripts/get_tyre_strategy.py --year 2026 --gp Spain --driver ANT --session R
```

`--session` defaults to `R` (race). Other values: `Q` (qualifying),
`FP1`/`FP2`/`FP3`, `S` (sprint).

### `scripts/get_race_results.py`

Classified results for every driver in one session: position, team,
grid position, status (Finished / Retired / Lapped / etc.), points,
laps completed, and gap to the winner.

```bash
python scripts/get_race_results.py --year 2026 --gp Spain --session R
```

## Important notes for interpreting output

- **Tyre compound names are generic.** `compound` is always one of
  `SOFT`, `MEDIUM`, `HARD`, `INTERMEDIATE`, `WET` — FastF1 does **not**
  expose the underlying Pirelli C1–C5 compound number. Do not invent a
  C-number (e.g. "Soft (C4)") unless it comes from a separate source
  such as a web search — state clearly which source it came from if
  you combine the two.
- **Degradation slope reflects net pace, not pure tyre wear.** Because
  fuel burns off and track grip evolves during a session, a negative
  `degradation_s_per_lap` (lap times getting faster with tyre age) is
  normal and does not mean the tyre itself improved.
- **`gap_to_winner_s` is `null` for the winner**; instead check
  `total_time_s`, which holds the winner's absolute race duration in
  seconds. Every other driver has the reverse: `total_time_s` is
  `null`, `gap_to_winner_s` is set.
- **DNF/retired drivers still get a numeric `position`** (based on how
  far they got before retiring). The real "did not finish" signal is
  `classified_position` being `"R"` (retired), `"D"` (disqualified),
  etc. rather than a plain number, and `status` (e.g. `"Retired"`).
- First run against a given session downloads and caches data locally
  (`fastf1_cache/`, created next to this skill) — can take 10–30
  seconds. Subsequent calls for the same session are fast.
- Grand Prix names follow FastF1/Ergast naming — use the country or
  event name (e.g. `"Spain"`, `"Monza"`, `"Great Britain"`), not
  informal track nicknames, when calling the scripts (translate
  nicknames like "Madring" to `"Spain"` before calling).
