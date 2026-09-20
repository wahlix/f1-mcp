"""
cache.py — the single place that configures FastF1's cache for this skill.

All f1_lib modules should import and call `ensure_cache()` before making
calls against fastf1, instead of setting up the cache themselves.
This keeps the cache directory consistent no matter which script runs first.
"""

from pathlib import Path
import fastf1

_CACHE_DIR = Path(__file__).resolve().parent.parent.parent / "fastf1_cache"
_cache_enabled = False

def ensure_cache() -> None:
    """Enable FastF1 cache once, no matter how many scripts call this."""
    global _cache_enabled
    if _cache_enabled:
        return
    _CACHE_DIR.mkdir(parents=True, exist_ok=True)
    fastf1.Cache.enable_cache(str(_CACHE_DIR))
    _cache_enabled = True