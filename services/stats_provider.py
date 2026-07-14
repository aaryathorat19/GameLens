"""Match-statistics providers with a shared interface and safe failure mapping."""

from __future__ import annotations

from abc import ABC, abstractmethod
import json
import os
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from config import API_FOOTBALL_BASE, STATS_HTTP_TIMEOUT_SECONDS
from modules.match_stats import MatchEvent, MatchStatistics, TeamStats


class StatsProviderError(RuntimeError):
    """Raised when match statistics cannot be loaded for the user."""


class StatsProvider(ABC):
    """Abstraction over football statistics backends."""

    name: str

    @abstractmethod
    def get_match(self, match_id: str) -> MatchStatistics:
        """Fetch normalized statistics for a fixture identifier."""


class DemoStatsProvider(StatsProvider):
    """Offline sample fixture so the dashboard works without an API key."""

    name = "Demo"

    _DEMO = MatchStatistics(
        match_id="demo-2024-final",
        competition="Premier League",
        status="FINISHED",
        kickoff_utc="2024-05-19T15:00:00Z",
        home=TeamStats(
            name="Northbridge FC",
            score=2,
            possession_pct=54.0,
            shots=14,
            shots_on_target=6,
            corners=7,
            fouls=11,
            yellow_cards=2,
            red_cards=0,
        ),
        away=TeamStats(
            name="Riverside United",
            score=1,
            possession_pct=46.0,
            shots=9,
            shots_on_target=3,
            corners=4,
            fouls=13,
            yellow_cards=3,
            red_cards=0,
        ),
        events=(
            MatchEvent(12, "Goal", "Northbridge FC", "A. Khan", "Right-footed shot"),
            MatchEvent(28, "Yellow Card", "Riverside United", "J. Ortega", "Foul"),
            MatchEvent(51, "Goal", "Riverside United", "M. Silva", "Header"),
            MatchEvent(67, "Substitution", "Northbridge FC", "L. Park", "On for R. Cole"),
            MatchEvent(81, "Goal", "Northbridge FC", "A. Khan", "Penalty"),
            MatchEvent(88, "Yellow Card", "Northbridge FC", "T. Adeyemi", "Time wasting"),
        ),
        provider_name="Demo",
    )

    def get_match(self, match_id: str) -> MatchStatistics:
        requested = match_id.strip() or self._DEMO.match_id
        if requested not in {self._DEMO.match_id, "demo"}:
            raise StatsProviderError(
                f"Demo provider only serves '{self._DEMO.match_id}' (or 'demo')."
            )
        return self._DEMO


class ApiFootballStatsProvider(StatsProvider):
    """HTTP client for API-Football (api-sports.io / dashboard.api-football.com)."""

    name = "API-Football"

    def __init__(
        self,
        api_key: str,
        *,
        base_url: str = API_FOOTBALL_BASE,
        timeout_seconds: float = STATS_HTTP_TIMEOUT_SECONDS,
    ) -> None:
        token = api_key.strip()
        if not token:
            raise StatsProviderError(
                "Set API_FOOTBALL_KEY in `.env` to load live match statistics from API-Football."
            )
        self._api_key = token
        self._base_url = base_url.rstrip("/")
        self._timeout_seconds = timeout_seconds

    def get_match(self, match_id: str) -> MatchStatistics:
        cleaned_id = match_id.strip()
        if not cleaned_id.isdigit():
            raise StatsProviderError("Live match IDs must be numeric API-Football fixture IDs.")

        fixture_payload = self._request_json("/fixtures", {"id": cleaned_id})
        fixtures = fixture_payload.get("response") or []
        if not fixtures:
            raise StatsProviderError("No match was found for that fixture ID.")

        statistics_payload = self._request_json("/fixtures/statistics", {"fixture": cleaned_id})
        events_payload = self._request_json("/fixtures/events", {"fixture": cleaned_id})
        return _parse_api_football_match(
            fixtures[0],
            statistics_payload.get("response") or [],
            events_payload.get("response") or [],
        )

    def _request_json(self, path: str, params: dict[str, str]) -> dict[str, Any]:
        query = urlencode(params)
        request = Request(
            f"{self._base_url}{path}?{query}",
            headers={
                "x-apisports-key": self._api_key,
                "Accept": "application/json",
            },
        )
        try:
            with urlopen(request, timeout=self._timeout_seconds) as response:
                body = response.read().decode("utf-8")
        except HTTPError as error:
            raise StatsProviderError(_map_http_error(error)) from error
        except URLError as error:
            raise StatsProviderError(
                "Could not reach the API-Football service. Check your network connection."
            ) from error
        except TimeoutError as error:
            raise StatsProviderError(
                f"API-Football timed out after {self._timeout_seconds:.0f}s."
            ) from error

        try:
            payload = json.loads(body)
        except json.JSONDecodeError as error:
            raise StatsProviderError("API-Football returned an unreadable response.") from error
        if not isinstance(payload, dict):
            raise StatsProviderError("API-Football returned an unexpected payload.")

        errors = payload.get("errors")
        if errors:
            raise StatsProviderError(_map_api_football_errors(errors))
        return payload


def get_stats_provider(prefer_live: bool = False) -> StatsProvider:
    """Return a live provider when configured; otherwise the offline demo."""
    token = os.getenv("API_FOOTBALL_KEY", "").strip()
    if prefer_live:
        return ApiFootballStatsProvider(token)
    if token:
        return ApiFootballStatsProvider(token)
    return DemoStatsProvider()


def _map_http_error(error: HTTPError) -> str:
    if error.code == 400:
        return "API-Football rejected that fixture ID."
    if error.code in {401, 403}:
        return "The API-Football key is invalid or missing permissions for this request."
    if error.code == 404:
        return "No match was found for that fixture ID."
    if error.code == 429:
        return "API-Football rate limit was hit. Wait a minute and try again."
    return f"API-Football failed with HTTP {error.code}."


def _map_api_football_errors(errors: Any) -> str:
    if isinstance(errors, dict) and errors:
        first = next(iter(errors.values()))
        return f"API-Football error: {first}"
    if isinstance(errors, list) and errors:
        return f"API-Football error: {errors[0]}"
    return "API-Football returned an error for this request."


def _parse_api_football_match(
    fixture_row: dict[str, Any],
    statistics_rows: list[dict[str, Any]],
    event_rows: list[dict[str, Any]],
) -> MatchStatistics:
    fixture = fixture_row.get("fixture") or {}
    league = fixture_row.get("league") or {}
    teams = fixture_row.get("teams") or {}
    goals = fixture_row.get("goals") or {}
    status = (fixture.get("status") or {}).get("long") or (
        (fixture.get("status") or {}).get("short") or "UNKNOWN"
    )

    home_team = teams.get("home") or {}
    away_team = teams.get("away") or {}
    home_name = str(home_team.get("name") or "Home")
    away_name = str(away_team.get("name") or "Away")
    home_stats_map = _statistics_map_for_team(statistics_rows, home_name)
    away_stats_map = _statistics_map_for_team(statistics_rows, away_name)

    events = tuple(
        sorted(
            (_parse_api_football_event(event) for event in event_rows),
            key=lambda item: item.minute,
        )
    )

    return MatchStatistics(
        match_id=str(fixture.get("id") or ""),
        competition=str(league.get("name") or "Unknown competition"),
        status=str(status),
        kickoff_utc=str(fixture.get("date") or ""),
        home=_team_stats_from_map(home_name, _optional_int(goals.get("home")), home_stats_map),
        away=_team_stats_from_map(away_name, _optional_int(goals.get("away")), away_stats_map),
        events=events,
        provider_name="API-Football",
    )


def _statistics_map_for_team(rows: list[dict[str, Any]], team_name: str) -> dict[str, Any]:
    for row in rows:
        team = row.get("team") or {}
        if str(team.get("name") or "") == team_name:
            return {
                str(item.get("type") or ""): item.get("value")
                for item in (row.get("statistics") or [])
            }
    return {}


def _team_stats_from_map(name: str, score: int | None, stats_map: dict[str, Any]) -> TeamStats:
    return TeamStats(
        name=name,
        score=score,
        possession_pct=_optional_percent(stats_map.get("Ball Possession")),
        shots=_optional_int(stats_map.get("Total Shots")),
        shots_on_target=_optional_int(stats_map.get("Shots on Goal")),
        corners=_optional_int(stats_map.get("Corner Kicks")),
        fouls=_optional_int(stats_map.get("Fouls")),
        yellow_cards=_optional_int(stats_map.get("Yellow Cards")),
        red_cards=_optional_int(stats_map.get("Red Cards")),
    )


def _parse_api_football_event(event: dict[str, Any]) -> MatchEvent:
    time_info = event.get("time") or {}
    team = event.get("team") or {}
    player = event.get("player") or {}
    assist = event.get("assist") or {}
    detail = str(event.get("detail") or "")
    assist_name = assist.get("name")
    if assist_name:
        detail = f"{detail} · Assist: {assist_name}" if detail else f"Assist: {assist_name}"
    return MatchEvent(
        minute=int(time_info.get("elapsed") or 0),
        event_type=str(event.get("type") or "Event"),
        team=str(team.get("name") or ""),
        player=str(player.get("name") or "Unknown"),
        detail=detail,
    )


def _optional_int(value: Any) -> int | None:
    if value is None or value == "":
        return None
    try:
        return int(str(value).replace("%", "").strip())
    except (TypeError, ValueError):
        return None


def _optional_percent(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(str(value).replace("%", "").strip())
    except (TypeError, ValueError):
        return None
