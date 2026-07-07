"""
SEVAGOTH Utilities Module
Contains helper functions for various tasks
"""

import re
import wikipedia
import pyjokes
import openai
import webbrowser
from config import OPENAI_API_KEY

try:
    import inflect
    p = inflect.engine()
except:
    p = None


def speak_number(number, sevagoth_speak_func):
    """
    Speak a number in words
    
    Args:
        number: Number to speak
        sevagoth_speak_func: Function to call for voice output
    """
    if not p:
        sevagoth_speak_func("Number conversion not available.")
        return
    
    try:
        number = int(str(number).replace(",", "").strip())
        words = p.number_to_words(number, andword="")
        sevagoth_speak_func(words)
    except Exception as e:
        sevagoth_speak_func(f"An error occurred while speaking the number: {e}")


def get_joke() -> str:
    """
    Get a random joke
    
    Returns:
        String with a joke
    """
    try:
        return pyjokes.get_joke()
    except:
        return "I couldn't fetch a joke right now."


def search_wikipedia(topic: str) -> str:
    """
    Search Wikipedia for a topic
    
    Args:
        topic: Topic to search
        
    Returns:
        Wikipedia summary or error message
    """
    try:
        results = wikipedia.summary(topic, sentences=3, auto_suggest=False, redirect=True)
        return results
    except wikipedia.exceptions.DisambiguationError as e:
        return f"There are multiple entries for that. Please be more specific. Options: {', '.join(e.options[:5])}"
    except wikipedia.exceptions.PageError:
        return "Sorry, I couldn't find anything on that topic."
    except Exception as e:
        return f"Wikipedia search error: {e}"


def extract_city_from_query(query: str) -> str:
    """
    Extract city name from topography query
    
    Args:
        query: Voice command containing location
        
    Returns:
        City name or None
    """
    match = re.search(r'(topography|terrain).*?of\s+([\w\s]+)', query)
    if match:
        return match.group(2).strip()
    
    words = query.split()
    return words[-1] if words else None


def generate_image(prompt: str, sevagoth_speak_func):
    """
    Generate image using DALL-E API
    
    Args:
        prompt: Image description
        sevagoth_speak_func: Function to call for voice feedback
    """
    if not OPENAI_API_KEY:
        sevagoth_speak_func("OpenAI API key is missing. Add OPENAI_API_KEY to your .env file.")
        return
    
    try:
        client = openai.OpenAI(api_key=OPENAI_API_KEY)
        response = client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            n=1,
            size="1024x1024"
        )
        image_url = response.data[0].url
        print(f"Image URL: {image_url}")
        sevagoth_speak_func("Image has been generated. Opening it now.")
        webbrowser.open(image_url)
    except Exception as e:
        print(f"Error generating image: {e}")
        sevagoth_speak_func("Failed to generate the image.")


def translate_and_speak(text: str, target_language: str, sevagoth_speak_func):
    """
    Translate text and speak it
    
    Args:
        text: Text to translate
        target_language: Target language code
        sevagoth_speak_func: Function to call for voice output
    """
    try:
        from googletrans import Translator
        translator = Translator()
        translated = translator.translate(text, dest=target_language)
        sevagoth_speak_func(translated.text)
    except Exception as e:
        sevagoth_speak_func(f"Translation error: {e}")


def get_time_string() -> str:
    """
    Get current time as formatted string
    
    Returns:
        Current time in HH:MM:SS format
    """
    import datetime
    return datetime.datetime.now().strftime("%H:%M:%S")


def open_web_resource(resource_type: str) -> bool:
    """
    Open various web resources
    
    Args:
        resource_type: Type of resource (youtube, google, stackoverflow, etc.)
        
    Returns:
        True if opened successfully
    """
    urls = {
        "youtube": "https://www.youtube.com",
        "google": "https://www.google.com",
        "stackoverflow": "https://stackoverflow.com/questions",
        "wikipedia": "https://www.wikipedia.org"
    }
    
    resource_type = resource_type.lower()
    if resource_type in urls:
        webbrowser.open(urls[resource_type])
        return True
    return False


def format_time_response(hour: int) -> str:
    """
    Get time-appropriate greeting
    
    Args:
        hour: Hour of day (0-23)
        
    Returns:
        Time period string (Morning, Afternoon, Evening)
    """
    if 0 <= hour < 12:
        return "Morning"
    elif 12 <= hour < 18:
        return "Afternoon"
    else:
        return "Evening"