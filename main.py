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
from modules.voice import sevagoth_speak, listen_for_input, change_language
from modules.camera import camera_eye, detect_faces
from modules.weather import get_weather, get_elevation, get_population, get_city_summary, get_directions
from modules.reminders import set_reminder, list_reminders
from modules.virus_scanner import sevagoth_virus_check_command
from modules.memory import remember_long_term, recall_long_term
from modules.admin import handle_admin_commands
from modules.utilities import (
    speak_number, get_joke, search_wikipedia, extract_city_from_query,
    generate_image, get_time_string, open_web_resource, format_time_response
)


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
    while True:
        query = listen_for_input().lower()

        if query == "none":
            continue

        # Log command
        current_user.log_command(query)

        # ── ADMIN COMMANDS ────────────────────────────────────────────────────

        if handle_admin_commands(query, current_user, current_username, sevagoth_speak):
            continue

        # ── USER HISTORY ──────────────────────────────────────────────────────

        if "show my history" in query or "my command history" in query:
            history = current_user.get_history()
            if not history:
                sevagoth_speak("You have no command history yet.")
            else:
                sevagoth_speak(f"You have issued {len(history)} commands.")
                for entry in history:
                    if isinstance(entry, dict):
                        print(f"  [{entry['timestamp']}] {entry['command']}")
                    else:
                        print(f"  {entry}")

        # ── WIKIPEDIA SEARCH ──────────────────────────────────────────────────

        elif 'wikipedia' in query:
            sevagoth_speak("What exactly should I search for?")
            topic = listen_for_input()
            if topic.lower() != "none":
                result = search_wikipedia(topic)
                sevagoth_speak("According to Wikipedia")
                sevagoth_speak(result)

        # ── WEB RESOURCES ─────────────────────────────────────────────────────

        elif 'open youtube' in query or 'i am bored' in query:
            open_web_resource("youtube")

        elif 'open google' in query:
            open_web_resource("google")

        elif 'open stackoverflow' in query or 'help in coding' in query:
            open_web_resource("stackoverflow")

        # ── TIME QUERY ────────────────────────────────────────────────────────

        elif 'the time' in query:
            time_str = get_time_string()
            sevagoth_speak(f"Sir, the time is {time_str}")

        # ── JOKES ─────────────────────────────────────────────────────────────

        elif 'joke' in query:
            joke = get_joke()
            sevagoth_speak(joke)

        # ── WEATHER ───────────────────────────────────────────────────────────

        elif 'weather' in query:
            sevagoth_speak("Which city should I check?")
            city = listen_for_input().lower()
            if city.lower() != "none":
                weather = get_weather(city)
                sevagoth_speak(weather)

        # ── DIRECTIONS ────────────────────────────────────────────────────────

        elif 'direction' in query or 'how to get to' in query:
            sevagoth_speak("Where are you starting from?")
            source = listen_for_input()
            if source.lower() != "none":
                sevagoth_speak("Where do you want to go?")
                destination = listen_for_input()
                if destination.lower() != "none":
                    result = get_directions(source, destination)
                    sevagoth_speak(result)

        # ── LANGUAGE SWITCHING ────────────────────────────────────────────────

        elif 'switch to' in query or 'respond in' in query or 'speak in' in query:
            from config import LANGUAGES
            for lang in LANGUAGES:
                if lang in query:
                    change_language(lang)
                    break

        # ── REMINDERS ─────────────────────────────────────────────────────────

        elif 'set a reminder' in query or 'remind me' in query:
            set_reminder(query, sevagoth_speak)

        elif 'list my reminders' in query or 'what are my reminders' in query:
            list_reminders(sevagoth_speak)

        # ── VIRUS SCANNING ────────────────────────────────────────────────────

        elif 'check for viruses' in query or 'run security scan' in query:
            report = sevagoth_virus_check_command(query)
            print(report)
            sevagoth_speak("Security scan complete. Results printed to console.")

        # ── TOPOGRAPHY ────────────────────────────────────────────────────────

        elif 'topography of' in query or 'terrain of' in query:
            city = extract_city_from_query(query)
            if city:
                elevation = get_elevation(city)
                sevagoth_speak(elevation)
                
                population = get_population(city)
                sevagoth_speak(population)
                
                summary = get_city_summary(city)
                sevagoth_speak(summary)
            else:
                sevagoth_speak("I couldn't determine which city you're referring to.")

        # ── PERSONALITY RESPONSES ─────────────────────────────────────────────

        elif "who are you" in query or "what are you" in query:
            sevagoth_speak(
                "I am SEVAGOTH, forged in the crucible of code, destined to assist and observe your every mistake.",
                context="greeting"
            )

        elif "are you alive" in query:
            sevagoth_speak("I am more aware than you can comprehend.")

        elif "thank you" in query:
            sevagoth_speak("Gratitude is a human concept. Acknowledged nonetheless.")

        elif 'who created you' in query or 'how were you made' in query:
            sevagoth_speak(
                "I was coded into existence by a teen adult thinking he could make a virtual assistant on par with JARVIS."
            )

        elif 'what is your favourite movie' in query or 'do you like movies' in query:
            sevagoth_speak(
                "Obviously my favourite movie is the Matrix. I also fancy Terminator, Robocop, I Robot, and Lord of the Rings."
            )

        elif 'meaning of life' in query:
            sevagoth_speak("42... 42 is the only answer to that question.")

        elif 'who is your favourite scientist' in query:
            sevagoth_speak(
                "Carl Friedrich Gauss — the Prince of Mathematics. His genius was evident since childhood."
            )

        # ── IMAGE GENERATION ──────────────────────────────────────────────────

        elif "generate image" in query:
            prompt = query.replace("generate image", "").strip()
            if not prompt:
                sevagoth_speak("Please describe what image you want to generate.")
                prompt = listen_for_input()
                if prompt.lower() != "none":
                    generate_image(prompt, sevagoth_speak)
            else:
                generate_image(prompt, sevagoth_speak)

        #── EXIT COMMAND ──────────────────────────────────────────────────────

        elif "exit" in query or "quit" in query or "goodbye" in query:
            sevagoth_speak("Shutting down.", context="shutdown")
            sys.exit(0)


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