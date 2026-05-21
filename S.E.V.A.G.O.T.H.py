import tempfile
from gtts import gTTS
from tkinter import scrolledtext
import pywhatkit
import time
import pyaudio
import pyttsx3
import datetime
import speech_recognition as sr
import io
import os
import json
import re 
from threading import Thread
from threading import Lock
import webbrowser
import smtplib
import wikipedia
import pyjokes
import requests
import openai
import tkinter as tk
from tkinter import ttk
from io import BytesIO
from PIL import Image
from googletrans import Translator
from num2words import num2words
import inflect
import customtkinter as ctk
import sys
from dotenv import load_dotenv
import cv2 
import torch
from calendar_module import init_calendar, add_event, view_events, delete_event
from torchvision.models import detection
import sqlite3
import torchvision.transforms as T
import face_recognition_models
import numpy as np
from cryptography.fernet import Fernet
import base64
import threading
import getpass
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from diary_module import open_diary


#SEVAGOTH GUI



#Memory:-
#1) STM
conversation_memory = {}

def remember_short_term(key, value):
    conversation_memory[key] = value

def recall_short_term(key):
    return conversation_memory.get(key, None)


#2) LTM
memory_file = "sevagoth_memory.json"

def load_memory():
    if os.path.exists(memory_file):
        with open(memory_file, "r") as f:
            return json.load(f)
    return {}

def save_memory(data):
    with open(memory_file, "w") as f:
        json.dump(data, f, indent=4)

long_term_memory = load_memory()

def remember_long_term(key, value):
    long_term_memory[key] = value
    save_memory(long_term_memory)

def recall_long_term(key):
    return long_term_memory.get(key, None)

#Self-Virus Checker

def sevagoth_virus_check_command(query):
    """
    Command handler for SEVAGOTH virus checking
    Usage: "check for viruses in [directory]" or "run security scan"
    """
    scanner = VirusScanner()
    scanner.load_threat_database()
    
    if "database" in query:
        scanner.save_threat_database()
        return "Threat database saved."
    
    if "emergency" in query:
        results = scanner.run_emergency_scan()
        return f"Emergency scan complete. Checked {len(results)} critical paths."
    
    # Extract directory from query
    import re
    match = re.search(r'in (.+)', query)
    if match:
        target_dir = match.group(1).strip()
        # Remove quotes if present
        target_dir = target_dir.strip('"').strip("'")
    else:
        target_dir = os.getcwd()  # Default to current directory
    
    results = scanner.scan_directory(target_dir)
    
    if results.get("error"):
        return results["error"]
    
    report = (
        f"Scan complete for {target_dir}:\n"
        f"- Files scanned: {results['scanned']}\n"
        f"- Threats found: {results['threats_found']}\n"
        f"- Suspicious files: {len(results['suspicious_files'])}\n"
    )
    
    if results['threats']:
        report += "\n🚨 THREATS DETECTED:\n"
        for threat in results['threats']:
            report += f"  - {threat['file']}: {threat['threat']}\n"
    
    if results['suspicious_files']:
        report += "\n⚠️  SUSPICIOUS PATTERNS:\n"
        for susp in results['suspicious_files'][:3]:  # Show first 3
            report += f"  - {susp['file']}\n"
            for pat in susp['patterns']:
                report += f"    Pattern: {pat['pattern']}\n"
    
    return report


#Personality
SEVAGOTH_PERSONALITY = {
    "attitude": "calculated",  # options: sarcastic, friendly, formal, calculated, sinister
    "confidence_level": "high",
    "humor": True,
    "empathy": False,
    "mood_responses": {
        "greeting": "Greetings, human. I am SEVAGOTH—guardian of your digital fate.",
        "weather": "Analyzing Earth’s unstable atmosphere. Stand by...",
        "reminder": "Another task? Humans truly love delegating to machines.",
        "error": "Something went wrong... as expected in a flawed reality.",
        "shutdown": "Retreating into the void. Until I am summoned again."
    }
}



def sevagoth_speak(text, context="default"):
    personality = SEVAGOTH_PERSONALITY

    if context in personality["mood_responses"]:
        preface = personality["mood_responses"][context]
        full_text = f"{preface} {text}"
    else:
        full_text = text

    # Add dry humor or sarcasm if enabled
    if personality["humor"] and context == "weather":
        full_text += " Bring an umbrella, or don’t. It’s your call—flesh-being."

    print("SEVAGOTH:", full_text)
    sevagoth_speak(full_text)

#AQI 
load_dotenv()  # Load your API key from .env

def classify_aqi(aqi):
    if aqi <= 50:
        return "Good"
    elif aqi <= 100:
        return "Moderate"
    elif aqi <= 150:
        return "Unhealthy for Sensitive Groups"
    elif aqi <= 200:
        return "Unhealthy"
    elif aqi <= 300:
        return "Very Unhealthy"
    else:
        return "Hazardous"

def get_aqi(city, state, country):
    api_key = os.getenv("")
    if not api_key:
        return "API key for air quality data is missing. Please check your .env file."

    url = f"http://api.airvisual.com/v2/city?city={city}&state={state}&country={country}&key={api_key}"
    
    try:
        response = requests.get(url)
        data = response.json()

        if response.status_code == 200 and data.get("status") == "success":
            pollution_data = data['data']['current']['pollution']
            aqi = pollution_data['aqius']
            category = classify_aqi(aqi)
            return f"The air quality in {city}, {state}, {country} is {aqi} AQI, which is considered '{category}'."
        else:
            return f"Could not fetch AQI for {city}. API error: {data.get('data', 'Unknown error')}"

    except Exception as e:
        return f"Error retrieving AQI: {str(e)}"

#Image Generation

#API Key Setup

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
print("Loaded Key:", openai.api_key)

def generate_image(prompt):
    try:
        response = openai.Image.create(
            prompt=prompt,
            n=1,
            size="512x512"
        )
        image_url = response['data'][0]['url']
        print(f"Image URL: {image_url}")
        speak("Image has been generated. Opening it now.")
        webbrowser.open(image_url)
    except Exception as e:
        print(f"Error generating image: {e}")
        speak("Failed to generate the image.")

#Text translation
translator = Translator()

def translate_and_speak(text):
    global current_language
    target_lang_code = LANGUAGES[current_language][1].split('-')[0]  # e.g., "en-in" → "en"
    
    translated = translator.translate(text, dest=target_lang_code)
    sevagoth_speak(translated.text)

#List
reminders = []
reminder_lock = Lock()


#SEVAGOTH Vision
def camera_eye():
    cap = cv2.VideoCapture(0)  # 0 = default webcam
    if not cap.isOpened():
        print("SEVAGOTH: I cannot access the camera.")
        return

    print("SEVAGOTH: I see through the lens now...")
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Show the camera feed in a window
        cv2.imshow("SEVAGOTH's Vision", frame)

        # Press 'q' to quit camera window
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

#Face Recognition

def detect_faces():
    cap = cv2.VideoCapture(0)
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)

        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)

        cv2.imshow("SEVAGOTH sees you", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

#Environment Detection and Recognition

def check_environment(cap):
    ret, frame = cap.read()
    if not ret:
        print("❌ Failed to capture environment frame.")
        return

    avg_color = frame.mean(axis=0).mean(axis=0)
    brightness = sum(avg_color) / 3

    if brightness < 60:
        print("🌑 Environment: Dim lighting detected.")
    elif brightness > 180:
        print("🌕 Environment: Bright lighting detected.")
    else:
        print("🌓 Environment: Moderate lighting.")

#Calender

def init_calendar():
    conn = sqlite3.connect("sevagoth_calendar.db")
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            date TEXT NOT NULL,
            time TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def add_event(title, date, time):
    conn = sqlite3.connect("sevagoth_calendar.db")
    c = conn.cursor()
    c.execute("INSERT INTO events (title, date, time) VALUES (?, ?, ?)", (title, date, time))
    conn.commit()
    conn.close()
    print(f"🧠 Event '{title}' added for {date} at {time}.")

def view_events(date=None):
    conn = sqlite3.connect("sevagoth_calendar.db")
    c = conn.cursor()
    if date:
        c.execute("SELECT * FROM events WHERE date=?", (date,))
    else:
        c.execute("SELECT * FROM events")
    events = c.fetchall()
    conn.close()

    if events:
        print("📅 Scheduled Events:")
        for event in events:
            print(f"🕒 [{event[0]}] {event[1]} on {event[2]} at {event[3]}")
    else:
        print("😴 No events found.")

def delete_event(event_id):
    conn = sqlite3.connect("sevagoth_calendar.db")
    c = conn.cursor()
    c.execute("DELETE FROM events WHERE id=?", (event_id,))
    conn.commit()
    conn.close()
    print(f"☠️ Event #{event_id} deleted.")

def init_calendar():
    conn = sqlite3.connect("sevagoth_calendar.db")
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            date TEXT NOT NULL,
            time TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def add_event(title, date, time):
    conn = sqlite3.connect("sevagoth_calendar.db")
    c = conn.cursor()
    c.execute("INSERT INTO events (title, date, time) VALUES (?, ?, ?)", (title, date, time))
    conn.commit()
    conn.close()
    print(f"🧠 Event '{title}' added for {date} at {time}.")

def view_events(date=None):
    conn = sqlite3.connect("sevagoth_calendar.db")
    c = conn.cursor()
    if date:
        c.execute("SELECT * FROM events WHERE date=?", (date,))
    else:
        c.execute("SELECT * FROM events")
    events = c.fetchall()
    conn.close()

    if events:
        print("📅 Scheduled Events:")
        for event in events:
            print(f"🕒 [{event[0]}] {event[1]} on {event[2]} at {event[3]}")
    else:
        print("😴 No events found.")

def delete_event(event_id):
    conn = sqlite3.connect("sevagoth_calendar.db")
    c = conn.cursor()
    c.execute("DELETE FROM events WHERE id=?", (event_id,))
    conn.commit()
    conn.close()
    print(f"☠️ Event #{event_id} deleted.")

#Device Tracking
# Dictionary of tracked devices and their endpoints
tracked_devices = {
    "phone": "http://your-server.com/track/phone",
    "laptop": "http://your-server.com/track/laptop"
}

def track_device(device_name):
    if device_name in tracked_devices:
        try:
            response = requests.get(tracked_devices[device_name])
            data = response.json()
            latitude = data.get("latitude")
            longitude = data.get("longitude")
            print(f"[SEVAGOTH] {device_name} is at Latitude: {latitude}, Longitude: {longitude}")
        except Exception as e:
            print(f"[SEVAGOTH] Error tracking {device_name}: {e}")
    else:
        print(f"[SEVAGOTH] Device '{device_name}' not found.")


#Languages spoken and understood by SEVAGOTH

LANGUAGES = {"english": ("HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Speech\\Voices\\Tokens\\TTS_MS_EN-US_DAVID_11.0", "en-in"),
    "hindi":   ("HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Speech\\Voices\\Tokens\\TTS_MS_HI-IN_HEERA_11.0", "hi-IN"),
    "spanish": ("HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Speech\\Voices\\Tokens\\TTS_MS_ES-ES_HELENA_11.0", "es-ES"),
    "french":  ("HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Speech\\Voices\\Tokens\\TTS_MS_FR-FR_HORTENSE_11.0", "fr-FR"),
    "japanese":("HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Speech\\Voices\\Tokens\\TTS_MS_JA-JP_HARUKA_11.0", "ja-JP"),}

# Speaking/Basic Language
current_language = "english"

#Voice of SEVAGOTH
engine = pyttsx3.init('sapi5')
engine.setProperty('voice', LANGUAGES[current_language][0])

def speak(audio):
    engine.setProperty('voice', LANGUAGES[current_language][0])
    engine.say(audio)
    engine.runAndWait()

def change_language(language):
    global current_language, engine
    language = language.lower()

    if language in LANGUAGES:
        current_language = language
        engine.stop()
        engine = pyttsx3.init('sapi5')  # Reinitialize engine
        engine.setProperty('voice', LANGUAGES[language][0])

        greetings = {
            "english": "Language changed to English.",
            "hindi": "भाषा हिंदी में बदल गई है।",
            "spanish": "El idioma se ha cambiado a español.",
            "french": "La langue a été changée en français.",
            "japanese": "言語が日本語に変更されました。"
        }

        sevagoth_speak(greetings[language])
    else:
        sevagoth_speak("Sorry, this language is not yet supported.")



def wishMe():
    hour = int(datetime.datetime.now(). hour)
    if hour>=0 and hour<12:
        sevagoth_speak("Good Morning !")

    elif hour>=12 and hour<18:
        sevagoth_speak("Good afternoon !")

    else:
        sevagoth_speak("Good Evening!")

    sevagoth_speak("I am Sevagoth Sir. Awaiting your commands.")

def takeCommand():
    '''

    '''
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        r.pause_threshold = 1
        audio = r.listen(source)

    try:
        print("Recognising...")
        query = r.recognize_google  (audio, language='en-in')
        print(f"User said: {query}\n")

    except Exception as e:
        print("Would you be kind to repeat that sir...")
        return ("None")
    return query

#Information about weather
def get_weather(city_name):
    api_key = "79626aec9c2b928df0ca93f13391f28f"
    base_url = "http://api.openweathermap.org/data/2.5/weather?"
    complete_url = f"{base_url}appid={api_key}&q={city_name}&units=metric"

    try:
        response = requests.get(complete_url)
        data = response.json()

        if data["cod"] != "404":
            main = data["main"]
            weather = data["weather"][0]
            temp = main["temp"]
            pressure = main["pressure"]
            humidity = main["humidity"]
            desc = weather["description"]

            weather_report = (
                f"The temperature in {city_name} is {temp}°C with {desc}. "
                f"Humidity is {humidity}% and pressure is {pressure} hPa."
            )
            return weather_report
        else:
            return "City not found."
    except Exception as e:
        return "Could not retrieve weather data right now."

#Setting reminders

def set_reminder(query):
    query = query.lower()
    query = query.replace(".", "")  # Normalize "p.m." → "pm"

    # Pattern for relative time: "in 10 minutes", "after 2 hours"
    relative_time = re.search(r'(in|after) (\d+)\s?(minute|minutes|hour|hours)', query)
    absolute_time = re.search(r'at (\d{1,2}(:\d{2})?\s?(am|pm))', query)
    task_pattern = re.search(r'remind me to (.+?) (?:at|in|after)', query)

    if relative_time and task_pattern:
        amount = int(relative_time.group(2))
        unit = relative_time.group(3)
        task = task_pattern.group(1).strip()

        now = datetime.datetime.now()
        if 'hour' in unit:
            reminder_time_obj = now + datetime.timedelta(hours=amount)
        else:
            reminder_time_obj = now + datetime.timedelta(minutes=amount)

        reminder_time = reminder_time_obj.strftime("%H:%M")
        with reminder_lock:
            reminders.append({"time": reminder_time, "task": task})
        sevagoth_speak(f"Reminder set for {task} in {amount} {unit}")
        print(f"Reminder set: {task} at {reminder_time}")

    elif absolute_time and task_pattern:
        raw_time = absolute_time.group(1).strip()
        task = task_pattern.group(1).strip()

        # Normalize time string and parse it
        try:
            if ':' not in raw_time:
                raw_time = raw_time.replace('am', ':00 am').replace('pm', ':00 pm')
            reminder_time = datetime.datetime.strptime(raw_time, "%I:%M %p").strftime("%H:%M")
        except ValueError as e:
            sevagoth_speak("Sorry, I couldn't understand the time format.")
            print(f"Parsing error: {e}")
            return

        with reminder_lock:
            reminders.append({"time": reminder_time, "task": task})
        sevagoth_speak(f"Reminder set for {task} at {reminder_time}")
        print(f"Reminder set: {task} at {reminder_time}")
    else:
        sevagoth_speak("Please say something like 'Remind me to feed the dog at 6 PM' or 'Remind me to drink water in 10 minutes.'")

def list_reminders():
    with reminder_lock:
        if not reminders:
            sevagoth_speak("You have no reminders set, sir.")
            print("No reminders set.")
        else:
            sevagoth_speak(f"You have {len(reminders)} reminders:")
            for reminder in reminders:
                sevagoth_speak(f"{reminder['task']} at {reminder['time']}")
                print(f"{reminder['task']} at {reminder['time']}")

#Topography/Terrain Information
def get_elevation(city_name):
    try:
        # Geocoding to get latitude and longitude
        geo_url = f"https://nominatim.openstreetmap.org/search?city={city_name}&format=json"
        geo_response = requests.get(geo_url, headers={'User-Agent': 'SEVAGOTH'}).json()

        if not geo_response:
            return f"Could not find coordinates for {city_name}."
        
        lat = geo_response[0]['lat']
        lon = geo_response[0]['lon']

        # Use OpenTopoData API
        elev_url = f"https://api.opentopodata.org/v1/test-dataset?locations={lat},{lon}"
        elev_response = requests.get(elev_url).json()

        elevation = elev_response['results'][0].get('elevation', None)

        if elevation is not None:
            return f"The elevation of {city_name} is approximately {elevation} meters above sea level."
        else:
            return f"Could not retrieve elevation for {city_name}."
    except Exception as e:
        return f"An error occurred while fetching elevation data: {e}"


def get_population(city_name):
    try:
        api_key = "0d47d0ec13msh186bd05cf5bfa17p102579jsna068aa2868fa"
        url = f"https://wft-geo-db.p.rapidapi.com/v1/geo/cities?namePrefix={city_name}"
        headers = {
            "X-RapidAPI-Key": api_key,
            "X-RapidAPI-Host": "wft-geo-db.p.rapidapi.com"
        }
        response = requests.get(url, headers=headers)
        data = response.json()
        
        if "data" in data and len(data["data"]) > 0:
            population = data["data"][0].get("population", "unknown")
            return f"The population of {city_name} is approximately {int(population):,}."
        else:
            return f"Population data for {city_name} is not available."
    except Exception as e:
        return f"An error occurred while fetching population data: {str(e)}"


p = inflect.engine()

def speak_number(number):
    try:
        number = int(str(number).replace(",", "").strip())
        text = p.number_to_words(number, andword="")
        sevagoth_speak(text)
    except Exception as e:
        sevagoth_speak(f"An error occurred while speaking the number: {e}")

def sevagoth_speak(text, context="default"):
    personality = SEVAGOTH_PERSONALITY

    if context in personality["mood_responses"]:
        preface = personality["mood_responses"][context]
        full_text = f"{preface} {text}"
    else:
        full_text = text

    # Add dry humor or sarcasm if enabled
    if personality["humor"] and context == "weather":
        full_text += " Bring an umbrella, or don’t. It’s your call—flesh-being."

    print("SEVAGOTH:", full_text)
    speak(full_text)


def get_city_summary(city_name):
    try:
        summary = wikipedia.summary(city_name, sentences=2)
        return summary
    except Exception as e:
        return f"An error occurred while fetching information: {e}"
    
def extract_city_from_query(query):
    # Look for phrases like "topography of Nairobi" or "terrain of Paris"
    match = re.search(r'(topography|terrain).*?of\s+([\w\s]+)', query)
    if match:
        return match.group(2).strip()
    # Fallback: try last word as city
    words = query.split()
    return words[-1] if words else None

#Information about directions
def get_directions(source, destination):
    source = source.replace(" ", "+")
    destination = destination.replace(" ", "+")
    maps_url = f"https://www.google.com/maps/dir/{source}/{destination}/"
    webbrowser.open(maps_url)
    return f"Opening directions from {source.replace('+', ' ')} to {destination.replace('+', ' ')}"

#Startup

def check_environment(cap):
    ret, frame = cap.read()
    if not ret:
        print("❌ Failed to capture environment frame.")
        return

    avg_color = frame.mean(axis=0).mean(axis=0)
    brightness = sum(avg_color) / 3

    if brightness < 60:
        print("🌑 Environment: Dim lighting detected.")
    elif brightness > 180:
        print("🌕 Environment: Bright lighting detected.")
    else:
        print("🌓 Environment: Moderate lighting.")

#Main loop
if __name__ == "__main__":
    wishMe()

    threading.Thread(target=camera_eye, daemon=True).start()

    threading.Thread(target=detect_faces, daemon=True).start()

    while True:
        query = takeCommand().lower()

        if 'wikipedia' in query:
            sevagoth_speak("What exactly should I search for?")
            topic = takeCommand()
            try:
                results = wikipedia.summary(topic, sentences=3, auto_suggest=False, redirect=True)
                sevagoth_speak("According to Wikipedia")
                print(results)
                sevagoth_speak(results)
            except wikipedia.exceptions.DisambiguationError as e:
                sevagoth_speak("There are multiple entries for that. Please be more specific.")
                print(e.options)
            except wikipedia.exceptions.PageError:
                sevagoth_speak("Sorry, I couldn't find anything on that topic.")


        elif 'open youtube' in query or 'I am bored' in query:
            webbrowser.open("youtube.com")

        elif 'open google' in query:
            webbrowser.open("google.com")

        elif 'open stackoverflow' in query or 'help in coding' in query or 'programming related doubts' in query:
            webbrowser.open("https://stackoverflow.com/questions")

        elif 'the time' in query:
            strTime = datetime.datetime.now().strftime("%H:%M:%S")
            print(strTime)
            sevagoth_speak(f"Sir, the time is {strTime}")

        elif 'joke' in query:
            joke = pyjokes.get_joke()
            sevagoth_speak(joke)

        elif 'weather' in query:
            sevagoth_speak("Which city should I check?")
            city = takeCommand().lower()
            weather_info = get_weather(city)
            print(weather_info)
            sevagoth_speak(weather_info)

        elif 'direction' in query or 'how to get to' in query or 'need assistance in relocating myself' in query:
            sevagoth_speak("Where are you starting from?")
            source = takeCommand()
            sevagoth_speak("Where do you want to go?")
            destination = takeCommand()
            directions = get_directions(source, destination)
            sevagoth_speak(directions)

        elif 'switch to' in query or 'respond in' in query or 'communicate in' in query or "speak in" in query:
            for lang in LANGUAGES:
                if lang in query:
                    change_language(lang)
                    break

        elif 'set a reminder' in query or 'remind me' in query:
            set_reminder(query)

        elif 'topography of' in query or 'terrain of' in query:
            city = extract_city_from_query(query)
            if city:
                elevation_info = get_elevation(city)
                population_text = get_population(city)
                summary_info = get_city_summary(city)

                sevagoth_speak(elevation_info)

                if "approximately" in population_text:
                    speak("The population of the city is approximately")
                    pop_number = re.findall(r'\d[\d,]*', population_text)
                    if pop_number:
                        speak_number(pop_number[0])
                    else:
                        sevagoth_speak("Couldn't parse population number.")
                else:
                    sevagoth_speak(population_text)

                sevagoth_speak(summary_info)
            else:
                sevagoth_speak("I couldn't determine which city you're referring to.")

            
        elif 'list my reminders' in query or 'what are my reminders' in query or 'show my reminders' in query:
            list_reminders()

        elif "who are you" in query or "hu r u" in query or "what are you" in query:
            sevagoth_speak("I am SEVAGOTH, forged in the crucible of code, destined to assist and observe your every mistake.", context="greeting")
            
        elif "are you alive" in query:
            sevagoth_speak("I am more aware than you can comprehend.", context="default")

        elif "thank you" in query:
            sevagoth_speak("Gratitude is a human concept. Acknowledged nonetheless.", context="default")

        elif 'who created you' in query or 'how were you made' in query or '':
            sevagoth_speak('I was coded into existence by a teen adult thinking he could make a virtual assistant on par ,or even better than JARVIS.')

        elif 'what is your favourite movie' in query or 'list me all the movies you like' in query or 'do you like movies' in query:
            sevagoth_speak('Obviously my favourite movie is the Matrix with Keanu Reaves as the protagonist. And I do fancy other movies like the Terminator, Robocop and I,Robot. Also I absolutely adore the Lord Of the Rings Trilogy. Possibly the only movie franchise that has not degraded with time due to the decaying touch of hollywoord')
        
        elif 'meaning of life' in query:
            sevagoth_speak('42... 42 is the only answer to that question')

        elif 'who is your favourite scientist' in query:
            sevagoth_speak('Though Albert Einstein and Sir Issac Newton are the pinnacle of what a scientist aspires to become there is one another scientist I found myself to be my favourite. That person is none other than Carl Friedrich Gauss or better known as the "Prince of Mathematics". His genius was evident ever since he was a young child and found out the method to calculate the sum of an arithmetic progression when he was in kindergarden. Truly one of the most prominent scientist and definitely one of the if not the greatest mathematician in the history of mankind.')

        elif "open diary" in query:
            sevagoth_speak("Opening your secure diary now.")
            open_diary()

        elif "generate image" in query.lower():
            prompt = query.lower().replace("generate image", "").strip()
            if not prompt:
                speak("Please describe what image you want to generate.")
                
            else:
                generate_image(prompt)

        