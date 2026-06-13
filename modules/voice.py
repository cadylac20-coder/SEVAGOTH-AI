"""
SEVAGOTH Voice Module
Handles text-to-speech, speech recognition, and language support
"""

import pyttsx3
import speech_recognition as sr
from threading import Lock
import time
from config import (
    LANGUAGES, DEFAULT_LANGUAGE, SEVAGOTH_PERSONALITY,
    TTS_ENGINE, TTS_RATE, TTS_VOLUME,
    SPEECH_PAUSE_THRESHOLD, SPEECH_LANGUAGE
)

# ── TTS ENGINE INITIALIZATION ─────────────────────────────────────────────────

current_language = DEFAULT_LANGUAGE
engine = pyttsx3.init(TTS_ENGINE)
engine.setProperty('voice', LANGUAGES[current_language][0])
engine.setProperty('rate', TTS_RATE)
engine.setProperty('volume', TTS_VOLUME)

# Lock prevents multiple threads from using TTS simultaneously (avoids deadlock)
speak_lock = Lock()


def speak(audio: str):
    """
    Raw text-to-speech function
    Handles engine state and error recovery
    """
    global engine, current_language
    with speak_lock:
        try:
            engine.setProperty('voice', LANGUAGES[current_language][0])
            engine.say(audio)
            engine.runAndWait()
        except RuntimeError as rt_error:
            # Engine crashed - reinitialize completely
            try:
                engine = pyttsx3.init(TTS_ENGINE)
                engine.setProperty('voice', LANGUAGES[current_language][0])
                engine.setProperty('rate', TTS_RATE)
                engine.setProperty('volume', TTS_VOLUME)
                engine.say(audio)
                engine.runAndWait()
            except Exception as e:
                print(f"[SEVAGOTH VOICE ERROR - CRITICAL] {e}")
        except Exception as e:
            print(f"[SEVAGOTH VOICE ERROR] {e}")


def sevagoth_speak(text: str, context: str = "default"):
    """
    Enhanced speech function with personality
    Adds personality mood responses based on context
    
    Args:
        text: The text to speak
        context: The context (greeting, weather, reminder, etc.)
    """
    personality = SEVAGOTH_PERSONALITY
    prefix = ""
    
    # Get mood response for context
    if context in personality["mood_responses"]:
        prefix = personality["mood_responses"][context]
    
    # Combine mood response with text
    full_text = f"{prefix} {text}".strip() if prefix else text
    
    # Add humor for weather context
    if personality["humor"] and context == "weather":
        full_text += " Bring an umbrella, or don't. It's your call—flesh-being."
    
    # Print and speak
    print("SEVAGOTH:", full_text)
    speak(full_text)


def change_language(language: str):
    """
    Change TTS language dynamically
    
    Args:
        language: Language code (english, hindi, spanish, french, japanese)
    """
    global current_language, engine
    language = language.lower()
    
    if language in LANGUAGES:
        current_language = language
        with speak_lock:
            try:
                engine = pyttsx3.init(TTS_ENGINE)
                engine.setProperty('voice', LANGUAGES[language][0])
                engine.setProperty('rate', TTS_RATE)
                engine.setProperty('volume', TTS_VOLUME)
            except Exception as e:
                print(f"[SEVAGOTH] Language change error: {e}")
        
        # Language-specific greetings
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


def listen_for_input() -> str:
    """
    Listen for voice input using speech recognition
    
    Returns:
        The recognized text as a string, or "None" if recognition failed
    """
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        r.pause_threshold = SPEECH_PAUSE_THRESHOLD
        try:
            audio = r.listen(source, timeout=10)
        except sr.RequestError as e:
            print(f"[SEVAGOTH] Microphone error: {e}")
            return "None"
        except sr.UnknownValueError:
            print("Would you be kind to repeat that sir...")
            return "None"
    
    try:
        print("Recognising...")
        query = r.recognize_google(audio, language=SPEECH_LANGUAGE)
        print(f"User said: {query}\n")
        return query
    except sr.UnknownValueError:
        print("Would you be kind to repeat that sir...")
        return "None"
    except sr.RequestError as e:
        print(f"[SEVAGOTH] Recognition error: {e}")
        return "None"


def get_current_language() -> str:
    """Get the currently active language"""
    return current_language


def list_supported_languages() -> list:
    """Get list of supported languages"""
    return list(LANGUAGES.keys())