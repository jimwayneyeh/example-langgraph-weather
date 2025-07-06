import os
import requests
from langchain_core.tools import tool
from typing import Dict
from dotenv import load_dotenv

load_dotenv()

@tool
def get_weather(city: str) -> Dict:
    """Use this tool to get the current weather for a specific city. It takes a city name as input and returns a dictionary with weather description and temperature."""
    api_key = os.getenv("OPENWEATHERMAP_API_KEY")
    if not api_key:
        return "Error: OpenWeatherMap API key not found."
    
    base_url = "http://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": city,
        "appid": api_key,
        "units": "metric",
        "lang": "zh_tw"
    }
    
    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()  # Raise an exception for bad status codes
        data = response.json()
        
        description = data["weather"][0]["description"]
        temp = data["main"]["temp"]
        
        return {"city": city, "description": description, "temperature": temp}
    except requests.exceptions.RequestException as e:
        return f"Error fetching weather data: {e}"
    except KeyError:
        return f"Error: Could not parse weather data for {city}."
