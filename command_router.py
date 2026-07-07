"""
SEVAGOTH Command Router
───────────────────────
Loads command definitions from commands_config.json and dispatches
incoming voice queries to the matching handler in command_handlers.py.

This replaces the long if/elif chain that used to live in main.py.
Trigger phrases are checked in the order they appear in the config file,
so the first match wins (same behavior as the old elif chain).
"""

import json
from pathlib import Path

import command_handlers as handlers

_CONFIG_PATH = Path(__file__).parent / "commands_config.json"


def _load_commands():
    with open(_CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


_COMMANDS = _load_commands()


def reload_commands():
    """Reload commands_config.json without restarting SEVAGOTH."""
    global _COMMANDS
    _COMMANDS = _load_commands()


def dispatch(query: str, ctx: dict) -> bool:
    """
    Match `query` against configured trigger phrases and run the
    corresponding handler.

    Args:
        query: Lowercased user voice command.
        ctx: Context dict (see command_handlers.py docstring).

    Returns:
        True if a command was matched and handled, False otherwise.
    """
    for command in _COMMANDS:
        triggers = command.get("triggers", [])
        if any(trigger in query for trigger in triggers):
            handler_name = command["handler"]
            handler_fn = getattr(handlers, handler_name, None)
            if handler_fn is None:
                print(f"[SEVAGOTH] Warning: handler '{handler_name}' "
                      f"not found for command '{command['name']}'.")
                return False
            try:
                handler_fn(query, ctx)
            except SystemExit:
                raise
            except Exception as e:
                print(f"[SEVAGOTH] Error running '{command['name']}': {e}")
                ctx['speak']("Something went wrong running that command.")
            return True
    return False
