"""
SEVAGOTH Command Handlers
─────────────────────────
Every handler has the same signature:

    def handler(query: str, ctx: dict) -> None

`ctx` is a small dict of callbacks/state built once per session:
    ctx['speak']    -> sevagoth_speak(text, context=None)
    ctx['listen']   -> listen_for_input() -> str
    ctx['user']     -> the logged-in User/Admin object
    ctx['username'] -> logged-in username string
    ctx['exit']     -> call to shut the assistant down cleanly

To add a brand-new voice command:
    1. Write a handler(query, ctx) function here.
    2. Add an entry to commands_config.json with the trigger phrases
       and the handler's function name.
No changes to main.py or command_router.py are required.
"""

from modules.weather import get_weather, get_elevation, get_population, get_city_summary, get_directions
from modules.reminders import set_reminder, list_reminders
from modules.virus_scanner import sevagoth_virus_check_command
from modules.utilities import (
    get_joke, search_wikipedia, extract_city_from_query,
    generate_image, get_time_string, open_web_resource
)
from modules.voice import change_language


def show_history(query, ctx):
    history = ctx['user'].get_history()
    if not history:
        ctx['speak']("You have no command history yet.")
        return
    ctx['speak'](f"You have issued {len(history)} commands.")
    for entry in history:
        if isinstance(entry, dict):
            print(f"  [{entry['timestamp']}] {entry['command']}")
        else:
            print(f"  {entry}")


def wikipedia_search(query, ctx):
    ctx['speak']("What exactly should I search for?")
    topic = ctx['listen']()
    if topic.lower() != "none":
        result = search_wikipedia(topic)
        ctx['speak']("According to Wikipedia")
        ctx['speak'](result)


def open_youtube(query, ctx):
    open_web_resource("youtube")


def open_google(query, ctx):
    open_web_resource("google")


def open_stackoverflow(query, ctx):
    open_web_resource("stackoverflow")


def tell_time(query, ctx):
    ctx['speak'](f"Sir, the time is {get_time_string()}")


def tell_joke(query, ctx):
    ctx['speak'](get_joke())


def check_weather(query, ctx):
    ctx['speak']("Which city should I check?")
    city = ctx['listen']().lower()
    if city != "none":
        ctx['speak'](get_weather(city))


def give_directions(query, ctx):
    ctx['speak']("Where are you starting from?")
    source = ctx['listen']()
    if source.lower() != "none":
        ctx['speak']("Where do you want to go?")
        destination = ctx['listen']()
        if destination.lower() != "none":
            ctx['speak'](get_directions(source, destination))


def switch_language(query, ctx):
    from config import LANGUAGES
    for lang in LANGUAGES:
        if lang in query:
            change_language(lang)
            break


def create_reminder(query, ctx):
    set_reminder(query, ctx['speak'])


def show_reminders(query, ctx):
    list_reminders(ctx['speak'])


def run_virus_scan(query, ctx):
    report = sevagoth_virus_check_command(query)
    print(report)
    ctx['speak']("Security scan complete. Results printed to console.")


def city_topography(query, ctx):
    city = extract_city_from_query(query)
    if not city:
        ctx['speak']("I couldn't determine which city you're referring to.")
        return
    ctx['speak'](get_elevation(city))
    ctx['speak'](get_population(city))
    ctx['speak'](get_city_summary(city))


def who_are_you(query, ctx):
    ctx['speak'](
        "I am SEVAGOTH, forged in the crucible of code, destined to assist and observe your every mistake.",
        context="greeting"
    )


def are_you_alive(query, ctx):
    ctx['speak']("I am more aware than you can comprehend.")


def say_thanks(query, ctx):
    ctx['speak']("Gratitude is a human concept. Acknowledged nonetheless.")


def who_created_you(query, ctx):
    ctx['speak'](
        "I was coded into existence by a teen adult thinking he could make a virtual assistant on par with JARVIS."
    )


def favourite_movie(query, ctx):
    ctx['speak'](
        "Obviously my favourite movie is the Matrix. I also fancy Terminator, Robocop, I Robot, and Lord of the Rings."
    )


def meaning_of_life(query, ctx):
    ctx['speak']("42... 42 is the only answer to that question.")


def favourite_scientist(query, ctx):
    ctx['speak'](
        "Carl Friedrich Gauss — the Prince of Mathematics. His genius was evident since childhood."
    )


def generate_image_handler(query, ctx):
    prompt = query.replace("generate image", "").strip()
    if not prompt:
        ctx['speak']("Please describe what image you want to generate.")
        prompt = ctx['listen']()
        if prompt.lower() == "none":
            return
    generate_image(prompt, ctx['speak'])


def exit_sevagoth(query, ctx):
    ctx['speak']("Shutting down.", context="shutdown")
    ctx['exit']()
