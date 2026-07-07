"""
Tests for modules/weather.py.

classify_aqi is pure logic. The get_* functions make real HTTP calls, so we
only test their error-handling paths (missing API key, request failure) using
monkeypatched requests - never hitting the real network in tests.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import modules.weather as weather


class TestClassifyAqi:
    def test_good(self):
        assert weather.classify_aqi(10) == "Good"

    def test_moderate(self):
        assert weather.classify_aqi(75) == "Moderate"

    def test_hazardous_above_all_thresholds(self):
        assert weather.classify_aqi(1000) == "Hazardous"

    def test_boundary_value(self):
        # 50 is the "Good" threshold itself
        assert weather.classify_aqi(50) == "Good"


class TestGetWeatherMissingKey:
    def test_missing_api_key_returns_friendly_message(self, monkeypatch):
        monkeypatch.setattr(weather, "OPENWEATHER_API_KEY", None)
        result = weather.get_weather("Paris")
        assert "API key missing" in result

    def test_network_failure_does_not_raise(self, monkeypatch):
        monkeypatch.setattr(weather, "OPENWEATHER_API_KEY", "fake-key")

        def raise_timeout(*args, **kwargs):
            raise weather.requests.exceptions.Timeout("simulated timeout")

        monkeypatch.setattr(weather.requests, "get", raise_timeout)
        result = weather.get_weather("Paris")
        assert "Could not retrieve weather data" in result


class TestGetPopulationMissingKey:
    def test_missing_rapidapi_key_returns_friendly_message(self, monkeypatch):
        monkeypatch.setattr(weather, "RAPIDAPI_KEY", None)
        result = weather.get_population("Paris")
        assert "RapidAPI key missing" in result
