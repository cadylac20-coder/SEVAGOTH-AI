"""
SEVAGOTH Weather & Environment Module
Handles weather data, air quality, elevation, and location information
"""

import requests
from config import OPENWEATHER_API_KEY, AIRVISUAL_API_KEY, AQI_LEVELS


def classify_aqi(aqi: int) -> str:
    """
    Classify Air Quality Index value
    
    Args:
        aqi: Air Quality Index number
        
    Returns:
        String description of air quality level
    """
    for threshold, level in sorted(AQI_LEVELS.items()):
        if aqi <= threshold:
            return level
    return "Hazardous"


def get_aqi(city: str, state: str, country: str) -> str:
    """
    Get Air Quality Index for a location
    
    Args:
        city: City name
        state: State/region name
        country: Country name
        
    Returns:
        String description of air quality
    """
    if not AIRVISUAL_API_KEY:
        return "AirVisual API key missing. Add AIRVISUAL_API_KEY to your .env file."
    
    url = f"http://api.airvisual.com/v2/city?city={city}&state={state}&country={country}&key={AIRVISUAL_API_KEY}"
    try:
        response = requests.get(url)
        data = response.json()
        if response.status_code == 200 and data.get("status") == "success":
            aqi = data['data']['current']['pollution']['aqius']
            return f"The air quality in {city}, {state}, {country} is {aqi} AQI, considered '{classify_aqi(aqi)}'."
        return f"Could not fetch AQI for {city}. API error: {data.get('data', 'Unknown error')}"
    except Exception as e:
        return f"Error retrieving AQI: {str(e)}"


def get_weather(city_name: str) -> str:
    """
    Get current weather for a city
    
    Args:
        city_name: Name of the city
        
    Returns:
        String with weather information
    """
    url = f"http://api.openweathermap.org/data/2.5/weather?appid={OPENWEATHER_API_KEY}&q={city_name}&units=metric"
    try:
        data = requests.get(url).json()
        if data["cod"] != "404":
            main = data["main"]
            weather = data["weather"][0]
            return (f"The temperature in {city_name} is {main['temp']}°C with {weather['description']}. "
                    f"Humidity is {main['humidity']}% and pressure is {main['pressure']} hPa.")
        return "City not found."
    except Exception:
        return "Could not retrieve weather data right now."


def get_elevation(city_name: str) -> str:
    """
    Get elevation of a city
    
    Args:
        city_name: Name of the city
        
    Returns:
        String with elevation information
    """
    try:
        geo = requests.get(
            f"https://nominatim.openstreetmap.org/search?city={city_name}&format=json",
            headers={'User-Agent': 'SEVAGOTH'}
        ).json()
        
        if not geo:
            return f"Could not find coordinates for {city_name}."
        
        elev = requests.get(
            f"https://api.opentopodata.org/v1/test-dataset?locations={geo[0]['lat']},{geo[0]['lon']}"
        ).json()['results'][0].get('elevation')
        
        return (f"The elevation of {city_name} is approximately {elev} meters above sea level."
                if elev is not None else f"Could not retrieve elevation for {city_name}.")
    except Exception as e:
        return f"An error occurred while fetching elevation data: {e}"


def get_population(city_name: str) -> str:
    """
    Get population of a city
    
    Args:
        city_name: Name of the city
        
    Returns:
        String with population information
    """
    try:
        headers = {
            "X-RapidAPI-Key": "0d47d0ec13msh186bd05cf5bfa17p102579jsna068aa2868fa",
            "X-RapidAPI-Host": "wft-geo-db.p.rapidapi.com"
        }
        data = requests.get(
            f"https://wft-geo-db.p.rapidapi.com/v1/geo/cities?namePrefix={city_name}",
            headers=headers
        ).json()
        
        if "data" in data and data["data"]:
            pop = data["data"][0].get("population", "unknown")
            return f"The population of {city_name} is approximately {int(pop):,}."
        return f"Population data for {city_name} is not available."
    except Exception as e:
        return f"An error occurred while fetching population data: {str(e)}"


def get_city_summary(city_name: str) -> str:
    """
    Get Wikipedia summary of a city
    
    Args:
        city_name: Name of the city
        
    Returns:
        Wikipedia summary or error message
    """
    try:
        import wikipedia
        return wikipedia.summary(city_name, sentences=2)
    except Exception as e:
        return f"An error occurred while fetching information: {e}"


def get_directions(source: str, destination: str) -> str:
    """
    Get directions between two locations
    Opens Google Maps in browser
    
    Args:
        source: Starting location
        destination: Destination location
        
    Returns:
        Status message
    """
    import webbrowser
    maps_url = f"https://www.google.com/maps/dir/{source.replace(' ', '+')}/{destination.replace(' ', '+')}/"
    webbrowser.open(maps_url)
    return f"Opening directions from {source} to {destination}"