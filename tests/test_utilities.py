"""
Tests for the pure-logic helper functions in modules/utilities.py.

These don't touch the network, TTS engine, or camera - just string/logic
functions - so they're safe to run anywhere, including CI.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from modules.utilities import (
    extract_city_from_query,
    format_time_response,
    open_web_resource,
    get_time_string,
)


class TestExtractCityFromQuery:
    def test_topography_phrasing(self):
        assert extract_city_from_query("what is the topography of London") == "London"

    def test_terrain_phrasing(self):
        assert extract_city_from_query("tell me the terrain of New York") == "New York"

    def test_falls_back_to_last_word_when_no_pattern_matches(self):
        # No "topography of" / "terrain of" pattern present
        assert extract_city_from_query("Tokyo") == "Tokyo"

    def test_empty_query_returns_none(self):
        assert extract_city_from_query("") is None


class TestFormatTimeResponse:
    def test_morning(self):
        assert format_time_response(0) == "Morning"
        assert format_time_response(11) == "Morning"

    def test_afternoon(self):
        assert format_time_response(12) == "Afternoon"
        assert format_time_response(17) == "Afternoon"

    def test_evening(self):
        assert format_time_response(18) == "Evening"
        assert format_time_response(23) == "Evening"


class TestOpenWebResource:
    def test_known_resource_returns_true(self, monkeypatch):
        opened_urls = []
        monkeypatch.setattr(
            "modules.utilities.webbrowser.open",
            lambda url: opened_urls.append(url),
        )
        result = open_web_resource("youtube")
        assert result is True
        assert opened_urls == ["https://www.youtube.com"]

    def test_unknown_resource_returns_false(self, monkeypatch):
        monkeypatch.setattr("modules.utilities.webbrowser.open", lambda url: None)
        assert open_web_resource("not-a-real-site") is False

    def test_is_case_insensitive(self, monkeypatch):
        monkeypatch.setattr("modules.utilities.webbrowser.open", lambda url: None)
        assert open_web_resource("YouTube") is True


class TestGetTimeString:
    def test_returns_hh_mm_ss_format(self):
        result = get_time_string()
        parts = result.split(":")
        assert len(parts) == 3
        assert all(part.isdigit() for part in parts)
