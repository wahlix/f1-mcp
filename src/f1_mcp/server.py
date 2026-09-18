"""
server.py — MCP transport layer. Wraps pure functions from tools/ in
@mcp.tool() decorators. Do NOT put F1 logic here — that belongs in tools/.

Run locally:
    python -m f1_mcp.server
"""

from mcp.server.fastmcp import FastMCP

from f1_mcp.tools.tyre_strategy import get_tyre_strategy

mcp = FastMCP("f1-data")


@mcp.tool()
def tyre_strategy(year: int, gp: str, driver: str, session_type: str = "R") -> dict:
    """
    Fetches the tyre strategy (stint by stint) for a driver in an F1 session.

    Args:
        year: Season, e.g. 2026.
        gp: Grand Prix name, e.g. "Spain" (Madrid/Madring) or "Monza".
        driver: Driver's 3-letter code, e.g. "ANT", "NOR", "VER".
        session_type: "R" (race), "Q" (quali), "FP1"/"FP2"/"FP3", "S" (sprint).

    Returns:
        Dict with driver, team, gp, session, total_pit_stops, and a list
        of stints (compound, fresh_tyre, lap range, avg time, degradation).
    """
    result = get_tyre_strategy(year=year, gp=gp, driver=driver, session_type=session_type)
    return result.to_dict()


# Next tool gets added the same way:
#
# from f1_mcp.tools.race_results import get_race_results
#
# @mcp.tool()
# def race_results(year: int, gp: str) -> dict:
#     """..."""
#     return get_race_results(year=year, gp=gp).to_dict()


if __name__ == "__main__":
    mcp.run()
