"""
Tests for command_router.py.

command_handlers.py transitively imports modules.voice, which initializes a
pyttsx3 TTS engine at import time (Windows-only "sapi5" driver). To keep these
tests runnable on any OS/CI without real audio hardware, we swap in a fake
"command_handlers" module before importing command_router, so the router's
matching/dispatch logic gets tested independently of the real handlers.
"""
import sys
import types
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))


def _install_fake_handlers(monkeypatch, calls):
    fake_handlers = types.ModuleType("command_handlers")

    def make_handler(name):
        def handler(query, ctx):
            calls.append(name)
        return handler

    for name in [
        "show_history", "wikipedia_search", "open_youtube", "open_google",
        "open_stackoverflow", "tell_time", "tell_joke", "check_weather",
        "give_directions", "switch_language", "create_reminder",
        "show_reminders", "run_virus_scan", "city_topography", "who_are_you",
        "are_you_alive", "say_thanks", "who_created_you", "favourite_movie",
        "meaning_of_life", "favourite_scientist", "generate_image_handler",
        "exit_sevagoth",
    ]:
        setattr(fake_handlers, name, make_handler(name))

    monkeypatch.setitem(sys.modules, "command_handlers", fake_handlers)

    # command_router itself may already be imported/cached from a previous
    # test; force a clean re-import so it picks up the fake handlers module.
    monkeypatch.delitem(sys.modules, "command_router", raising=False)
    import command_router
    return command_router


def make_ctx(calls=None):
    if calls is None:
        calls = []
    return {
        "speak": lambda text, context=None: calls.append(("speak", text)),
        "listen": lambda: "none",
        "user": None,
        "username": "tester",
        "exit": lambda: None,
    }


class TestDispatch:
    def test_matches_first_trigger_in_config_order(self, monkeypatch):
        calls = []
        router = _install_fake_handlers(monkeypatch, calls)
        matched = router.dispatch("what's the weather in paris", make_ctx())
        assert matched is True
        assert calls == ["check_weather"]

    def test_joke_trigger(self, monkeypatch):
        calls = []
        router = _install_fake_handlers(monkeypatch, calls)
        router.dispatch("tell me a joke", make_ctx())
        assert calls == ["tell_joke"]

    def test_no_match_returns_false(self, monkeypatch):
        calls = []
        router = _install_fake_handlers(monkeypatch, calls)
        matched = router.dispatch("gibberish that matches nothing at all", make_ctx())
        assert matched is False
        assert calls == []

    def test_exit_phrase_routes_to_exit_handler(self, monkeypatch):
        calls = []
        router = _install_fake_handlers(monkeypatch, calls)
        router.dispatch("goodbye", make_ctx())
        assert calls == ["exit_sevagoth"]

    def test_missing_handler_is_reported_not_raised(self, monkeypatch, capsys):
        calls = []
        router = _install_fake_handlers(monkeypatch, calls)
        # Temporarily point a command at a handler name that doesn't exist
        router._COMMANDS.insert(0, {
            "name": "broken_command",
            "triggers": ["trigger the broken command"],
            "handler": "this_handler_does_not_exist",
        })
        matched = router.dispatch("trigger the broken command", make_ctx())
        assert matched is False
        assert "Warning" in capsys.readouterr().out

    def test_handler_exception_is_caught_and_reported(self, monkeypatch, capsys):
        calls = []
        router = _install_fake_handlers(monkeypatch, calls)

        def blowing_up(query, ctx):
            raise ValueError("boom")

        router._COMMANDS.insert(0, {
            "name": "explodes",
            "triggers": ["please explode now"],
            "handler": "explodes_handler",
        })
        import command_handlers
        command_handlers.explodes_handler = blowing_up

        ctx_calls = []
        matched = router.dispatch("please explode now", make_ctx(ctx_calls))
        assert matched is True  # a handler was found and invoked, even though it errored
        assert ("speak", "Something went wrong running that command.") in ctx_calls
        assert "Error running" in capsys.readouterr().out
