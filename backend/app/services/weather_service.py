import requests
from datetime import datetime, date, timedelta
from typing import Dict, Any, Optional
from app.config import settings

class WeatherService:
    """
    Service to fetch weather data using OpenWeatherMap API.
    Uses the "forecast" endpoint for 5-day / 3-hour forecast.
    """
    def __init__(self):
        self.api_key = settings.OPENWEATHER_API_KEY
        self.base_url = "http://api.openweathermap.org/data/2.5/"

    async def _get_coordinates(self, city_name: str) -> Optional[Dict[str, float]]:
        """Fetches latitude and longitude for a given city name using OpenWeatherMap's geocoding."""
        # OpenWeatherMap's direct geocoding is part of their Geocoding API, which has a free tier.
        # However, the `weather` endpoint also implicitly handles city names and returns coords.
        # For simplicity, we'll use the 'weather' endpoint for coordinates if it works.
        # A dedicated Geocoding API call would be: http://api.openweathermap.org/geo/1.0/direct?q={city_name}&limit=1&appid={API key}
        
        geo_url = f"{self.base_url}weather?q={city_name}&appid={self.api_key}"
        try:
            response = requests.get(geo_url)
            response.raise_for_status() # Raise an HTTPError for bad responses (4xx or 5xx)
            data = response.json()
            if data and data.get('coord'):
                return {
                    "lat": data['coord']['lat'],
                    "lon": data['coord']['lon']
                }
            return None
        except requests.exceptions.RequestException as e:
            print(f"Error fetching coordinates for {city_name}: {e}")
            return None

    async def get_weather_forecast(self, city_name: str, target_date: date) -> Dict[str, Any]:
        """
        Fetches weather forecast for a specific city and date.
        OpenWeatherMap free tier provides 5-day / 3-hour forecast.
        For dates beyond 5 days, it will return current weather or a general message.
        """
        coords = await self._get_coordinates(city_name)
        if not coords:
            return {"summary": "Could not retrieve weather data for this city. Check city name or API key.", "raw_data": {}}

        lat, lon = coords['lat'], coords['lon']
        
        # Use the "forecast" endpoint for 5-day / 3-hour forecast.
        # units=imperial for Fahrenheit, units=metric for Celsius.
        forecast_url = f"{self.base_url}forecast?lat={lat}&lon={lon}&appid={self.api_key}&units=imperial"

        try:
            response = requests.get(forecast_url)
            response.raise_for_status()
            data = response.json()

            # Find the forecast for the closest time on the target_date
            # OpenWeatherMap provides data in 3-hour intervals, 'list' contains multiple forecasts
            
            # Convert target_date to a datetime object for comparison (e.g., midday for the target date)
            target_dt_midday = datetime(target_date.year, target_date.month, target_date.day, 12, 0, 0)
            
            closest_forecast = None
            min_time_diff = float('inf')

            for item in data.get('list', []):
                dt_txt = item['dt_txt'] # e.g., "2025-07-12 12:00:00"
                forecast_dt = datetime.strptime(dt_txt, "%Y-%m-%d %H:%M:%S")
                
                # Check if the forecast is for the target date
                if forecast_dt.date() == target_date:
                    time_diff = abs((forecast_dt - target_dt_midday).total_seconds())
                    if time_diff < min_time_diff:
                        min_time_diff = time_diff
                        closest_forecast = item
            
            if closest_forecast:
                main_data = closest_forecast['main']
                weather_desc = closest_forecast['weather'][0]['description']
                temp = main_data['temp']
                feels_like = main_data['feels_like']
                humidity = main_data['humidity']
                wind_speed = closest_forecast['wind']['speed']

                summary = (
                    f"On {target_date.strftime('%A, %B %d')}: "
                    f"Expected conditions: {weather_desc}, temperature {temp}°F (feels like {feels_like}°F). "
                    f"Humidity around {humidity}%. Winds at {wind_speed} mph."
                )
                
                # Simple rain check based on weather ID (https://openweathermap.org/weather-conditions#Weather-condition-codes-2)
                umbrella_recommended = False
                weather_id = closest_forecast['weather'][0]['id']
                if 200 <= weather_id < 600: # Thunderstorm, Drizzle, Rain
                    umbrella_recommended = True
                elif weather_id == 801 or weather_id == 802: # Few clouds, scattered clouds (might get light rain)
                    umbrella_recommended = False # Or set to True if you want to be very cautious

                return {
                    "summary": summary,
                    "temperature_f": temp,
                    "feels_like_f": feels_like,
                    "description": weather_desc,
                    "humidity": humidity,
                    "wind_speed_mph": wind_speed,
                    "umbrella_recommended": umbrella_recommended,
                    "raw_data": closest_forecast # Store raw data for debugging/more detail
                }
            else:
                # If target_date is beyond the 5-day forecast, or no data found
                return {"summary": f"Detailed weather forecast for {target_date.strftime('%A, %B %d')} is not available (OpenWeatherMap free tier provides 5-day forecast).", "raw_data": {}}

        except requests.exceptions.RequestException as e:
            print(f"Error fetching weather forecast for {city_name}: {e}")
            return {"summary": "Error fetching weather data.", "raw_data": {}}
        except Exception as e:
            print(f"An unexpected error occurred in WeatherService: {e}")
            return {"summary": "An unexpected error occurred while fetching weather data.", "raw_data": {}}