"""
SEVAGOTH Main Entry Point
Startup sequence: Login → Greeting → Cameras → Listening
"""

import threading
import time
import datetime
import sys

# Import all modules
from config import LOGIN_TO_GREETING_DELAY, GREETING_TO_CAMERA_DELAY
from modules.auth import login
from modules.voice import sevagoth_speak, listen_for_input
from modules.camera import camera_eye, detect_faces
from modules.admin import handle_admin_commands
from modules.utilities import format_time_response
import command_router


def wish_user(username: str):
    """
    Greet user based on time of day
    
    Args:
        username: Username of logged-in user
    """
    hour = int(datetime.datetime.now().hour)
    time_period = format_time_response(hour)
    sevagoth_speak(f"Good {time_period}, {username}!")
    sevagoth_speak("I am Sevagoth. Awaiting your commands.")


def main_loop(current_username: str, current_user):
    """
    Main command loop - listens for and processes voice commands

    Args:
        current_username: Username of logged-in user
        current_user: User object (Employee or Admin)
    """
    # Context passed to every command handler - see command_handlers.py
    ctx = {
        'speak': sevagoth_speak,
        'listen': listen_for_input,
        'user': current_user,
        'username': current_username,
        'exit': lambda: sys.exit(0),
    }

    while True:
        query = listen_for_input().lower()

        if query == "none":
            continue

        # Log command
        current_user.log_command(query)

        # ── ADMIN COMMANDS ────────────────────────────────────────────────────

        if handle_admin_commands(query, current_user, current_username, sevagoth_speak):
            continue

        # ── EVERYTHING ELSE ───────────────────────────────────────────────────
        # Matched against commands_config.json and routed to command_handlers.py.
        # To add a new command, edit that config file - no changes needed here.

        if not command_router.dispatch(query, ctx):
            sevagoth_speak("I didn't understand that command.")


def start_camera_systems():
    """Start camera and face detection in background threads"""
    print("[SEVAGOTH] Initializing camera systems...")
    
    camera_thread = threading.Thread(target=camera_eye, daemon=False)
    face_thread = threading.Thread(target=detect_faces, daemon=False)
    
    camera_thread.start()
    face_thread.start()
    
    print("[SEVAGOTH] Camera systems online. Awaiting voice commands...\n")
    time.sleep(GREETING_TO_CAMERA_DELAY)


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print(" " * 15 + "SEVAGOTH v3.0 - AI Assistant")
    print("=" * 60 + "\n")
    
    # STEP 1: LOGIN
    print("[SEVAGOTH] Starting login sequence...")
    current_username, current_user = login()
    
    # STEP 2: Stabilize TTS engine
    print("[SEVAGOTH] Stabilizing voice engine...")
    time.sleep(LOGIN_TO_GREETING_DELAY)
    
    # STEP 3: GREETING
    print("[SEVAGOTH] Initiating greeting...")
    wish_user(current_username)
    
    # STEP 4: Start cameras
    start_camera_systems()
    
    # STEP 5: Begin listening
    print("[SEVAGOTH] Listening for commands...\n")
    main_loop(current_username, current_user)