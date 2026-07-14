from modules.match_stats import MatchEvent, MatchStatistics, TeamStats, format_optional, scoreline
from services.stats_provider import (
    ApiFootballStatsProvider,
    DemoStatsProvider,
    StatsProviderError,
    _parse_api_football_match,
    get_stats_provider,
)


def test_demo_provider_returns_sample_match() -> None:
    stats = DemoStatsProvider().get_match("demo")

    assert stats.provider_name == "Demo"
    assert stats.home.score == 2
    assert stats.away.score == 1
    assert len(stats.events) == 6
    assert scoreline(stats) == "2 – 1"


def test_demo_provider_rejects_unknown_ids() -> None:
    try:
        DemoStatsProvider().get_match("999")
        assert False, "Expected StatsProviderError"
    except StatsProviderError as error:
        assert "Demo provider" in str(error)


def test_format_optional_handles_missing_values() -> None:
    assert format_optional(None) == "—"
    assert format_optional(54.2, suffix="%") == "54%"
    assert format_optional(7) == "7"


def test_get_stats_provider_defaults_to_demo_without_token(monkeypatch) -> None:
    monkeypatch.delenv("API_FOOTBALL_KEY", raising=False)

    provider = get_stats_provider()

    assert isinstance(provider, DemoStatsProvider)


def test_get_stats_provider_prefers_live_when_requested(monkeypatch) -> None:
    monkeypatch.setenv("API_FOOTBALL_KEY", "test-token")

    provider = get_stats_provider(prefer_live=True)

    assert isinstance(provider, ApiFootballStatsProvider)


def test_api_football_provider_requires_token() -> None:
    try:
        ApiFootballStatsProvider("   ")
        assert False, "Expected StatsProviderError"
    except StatsProviderError as error:
        assert "API_FOOTBALL_KEY" in str(error)


def test_parse_api_football_match_maps_fixture_stats_and_events() -> None:
    fixture_row = {
        "fixture": {
            "id": 867946,
            "date": "2024-03-01T20:00:00+00:00",
            "status": {"long": "Match Finished", "short": "FT"},
        },
        "league": {"name": "Premier League"},
        "teams": {"home": {"name": "Alpha"}, "away": {"name": "Beta"}},
        "goals": {"home": 2, "away": 1},
    }
    statistics_rows = [
        {
            "team": {"name": "Alpha"},
            "statistics": [
                {"type": "Ball Possession", "value": "57%"},
                {"type": "Total Shots", "value": 12},
                {"type": "Shots on Goal", "value": 5},
                {"type": "Corner Kicks", "value": 6},
                {"type": "Fouls", "value": 9},
                {"type": "Yellow Cards", "value": 1},
                {"type": "Red Cards", "value": 0},
            ],
        },
        {
            "team": {"name": "Beta"},
            "statistics": [
                {"type": "Ball Possession", "value": "43%"},
                {"type": "Total Shots", "value": 8},
                {"type": "Shots on Goal", "value": 3},
                {"type": "Corner Kicks", "value": 2},
                {"type": "Fouls", "value": 11},
                {"type": "Yellow Cards", "value": 2},
                {"type": "Red Cards", "value": None},
            ],
        },
    ]
    event_rows = [
        {
            "time": {"elapsed": 61},
            "team": {"name": "Alpha"},
            "player": {"name": "C. Ruiz"},
            "assist": {"name": "D. Ng"},
            "type": "Goal",
            "detail": "Normal Goal",
        },
        {
            "time": {"elapsed": 12},
            "team": {"name": "Beta"},
            "player": {"name": "E. Shaw"},
            "assist": {"name": None},
            "type": "Card",
            "detail": "Yellow Card",
        },
    ]

    stats = _parse_api_football_match(fixture_row, statistics_rows, event_rows)

    assert stats == MatchStatistics(
        match_id="867946",
        competition="Premier League",
        status="Match Finished",
        kickoff_utc="2024-03-01T20:00:00+00:00",
        home=TeamStats(
            name="Alpha",
            score=2,
            possession_pct=57.0,
            shots=12,
            shots_on_target=5,
            corners=6,
            fouls=9,
            yellow_cards=1,
            red_cards=0,
        ),
        away=TeamStats(
            name="Beta",
            score=1,
            possession_pct=43.0,
            shots=8,
            shots_on_target=3,
            corners=2,
            fouls=11,
            yellow_cards=2,
            red_cards=None,
        ),
        events=(
            MatchEvent(12, "Card", "Beta", "E. Shaw", "Yellow Card"),
            MatchEvent(61, "Goal", "Alpha", "C. Ruiz", "Normal Goal · Assist: D. Ng"),
        ),
        provider_name="API-Football",
    )
