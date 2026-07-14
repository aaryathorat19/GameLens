"""Domain models for match statistics dashboards."""

from dataclasses import dataclass


@dataclass(frozen=True)
class MatchEvent:
    """A chronological on-pitch moment for timeline display."""

    minute: int
    event_type: str
    team: str
    player: str
    detail: str = ""


@dataclass(frozen=True)
class TeamStats:
    """Aggregate counting stats for one side of a fixture."""

    name: str
    score: int | None
    possession_pct: float | None = None
    shots: int | None = None
    shots_on_target: int | None = None
    corners: int | None = None
    fouls: int | None = None
    yellow_cards: int | None = None
    red_cards: int | None = None


@dataclass(frozen=True)
class MatchStatistics:
    """Normalized match summary returned by any statistics provider."""

    match_id: str
    competition: str
    status: str
    kickoff_utc: str
    home: TeamStats
    away: TeamStats
    events: tuple[MatchEvent, ...]
    provider_name: str


def format_optional(value: int | float | None, *, suffix: str = "") -> str:
    """Render missing provider fields as an em dash for Streamlit cards."""
    if value is None:
        return "—"
    if isinstance(value, float):
        return f"{value:.0f}{suffix}"
    return f"{value}{suffix}"


def scoreline(stats: MatchStatistics) -> str:
    """Return a compact home–away score string when both sides are known."""
    home = format_optional(stats.home.score)
    away = format_optional(stats.away.score)
    return f"{home} – {away}"
