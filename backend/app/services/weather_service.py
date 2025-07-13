import requests
from datetime import datetime, date, timedelta, timezone
from typing import Dict, Any, Optional
from app.config import settings
import pytz  # Will need this for proper timezone handling


class WeatherService:
    def __init__(self):
        self.api_key = settings.OPENWEATHER_API_KEY
        self.base_url = "http://api.openweathermap.org/data/2.5/"
        # Map some common cities to their IANA timezones if not using a dedicated TZ service
        self.city_timezones = {
            # USA
            "new_york": "America/New_York",
            "chicago": "America/Chicago",
            "denver": "America/Denver",
            "los_angeles": "America/Los_Angeles",
            "anchorage": "America/Anchorage",
            "honolulu": "Pacific/Honolulu",
            # Australia
            "sydney": "Australia/Sydney",
            "melbourne": "Australia/Melbourne",
            "brisbane": "Australia/Brisbane",
            "adelaide": "Australia/Adelaide",
            "perth": "Australia/Perth",
            "darwin": "Australia/Darwin",
            # India
            "new_delhi": "Asia/Kolkata",
        }

    async def _get_coordinates(self, city_name: str) -> Optional[Dict[str, float]]:
        """Fetches latitude and longitude for a given city name."""
        # Using the direct geocoding API for more reliable lat/lon and potentially timezone info
        # Note: The free tier Geocoding API may not return 'timezone' field directly from /direct endpoint.
        # It's usually in /weather or /forecast. Let's stick to the main weather endpoint for now
        # as it was implicitly providing timezone (though not consistently documented for direct use).
        # We'll primarily rely on a manual map or an external library for timezones.

        geo_url = f"{self.base_url}weather?q={city_name}&appid={self.api_key}"
        try:
            response = requests.get(geo_url)
            response.raise_for_status()
            data = response.json()
            if data and data.get("coord"):
                return {
                    "lat": data["coord"]["lat"],
                    "lon": data["coord"]["lon"],
                    # Don't rely on 'timezone' from this endpoint for offset, use pytz
                }
            return None
        except requests.exceptions.RequestException as e:
            print(f"WeatherService: Error fetching coordinates for {city_name}: {e}")
            return None

    async def get_weather_forecast(
        self, city_name: str, target_date: date
    ) -> Dict[str, Any]:
        coords = await self._get_coordinates(city_name)
        if not coords:
            print(f"WeatherService: Could not get coordinates for {city_name}.")
            return {
                "summary": "Could not retrieve weather data for this city. Check city name or API key.",
                "raw_data": {},
            }

        lat, lon = coords["lat"], coords["lon"]

        # --- IMPORTANT: Get city's timezone using pytz ---
        city_tz_str = self.city_timezones.get(city_name.lower())
        if not city_tz_str:
            print(
                f"WeatherService: Timezone for city '{city_name}' not found in map. Defaulting to UTC for forecast interpretation."
            )
            # Fallback for unknown cities, might cause issues
            city_tz = pytz.utc
        else:
            city_tz = pytz.timezone(city_tz_str)
        # --- END IMPORTANT ---

        forecast_url = f"{self.base_url}forecast?lat={lat}&lon={lon}&appid={self.api_key}&units=imperial"

        try:
            print(f"WeatherService: Attempting to fetch forecast from: {forecast_url}")
            response = requests.get(forecast_url)
            response.raise_for_status()
            data = response.json()

            print(
                f"WeatherService: Number of forecast items received: {len(data.get('list', []))}"
            )

            closest_forecast = None
            min_time_diff = float("inf")

            # Define the start and end of the target day in the city's local timezone
            # and then convert them to UTC for comparison with OWM data
            target_start_of_day_local = datetime(
                target_date.year, target_date.month, target_date.day, 0, 0, 0
            )
            target_end_of_day_local = datetime(
                target_date.year, target_date.month, target_date.day, 23, 59, 59
            )

            # Make them timezone aware and convert to UTC
            target_start_of_day_utc = city_tz.localize(
                target_start_of_day_local
            ).astimezone(pytz.utc)
            target_end_of_day_utc = city_tz.localize(
                target_end_of_day_local
            ).astimezone(pytz.utc)

            for item in data.get("list", []):
                dt_txt = item["dt_txt"]  # This is UTC time from OWM
                forecast_dt_utc = datetime.strptime(
                    dt_txt, "%Y-%m-%d %H:%M:%S"
                ).replace(tzinfo=pytz.utc)  # Make it UTC-aware

                # Check if the UTC forecast time falls within our target local day's UTC window
                if target_start_of_day_utc <= forecast_dt_utc <= target_end_of_day_utc:
                    # If it's within the day, find the one closest to *midday local time*
                    # Convert the forecast_dt_utc to local for time diff calculation
                    forecast_dt_local = forecast_dt_utc.astimezone(city_tz)
                    target_dt_midday_local = city_tz.localize(
                        datetime(
                            target_date.year,
                            target_date.month,
                            target_date.day,
                            12,
                            0,
                            0,
                        )
                    )

                    time_diff = abs(
                        (forecast_dt_local - target_dt_midday_local).total_seconds()
                    )

                    if time_diff < min_time_diff:
                        min_time_diff = time_diff
                        closest_forecast = item

            if closest_forecast:
                main_data = closest_forecast["main"]
                weather_desc = closest_forecast["weather"][0]["description"]
                temp = main_data["temp"]
                feels_like = main_data["feels_like"]
                humidity = main_data["humidity"]
                wind_speed = closest_forecast["wind"]["speed"]

                summary = (
                    f"On {target_date.strftime('%A, %B %d')}: "
                    f"Expected conditions: {weather_desc}, temperature {temp}°F (feels like {feels_like}°F). "
                    f"Humidity around {humidity}%. Winds at {wind_speed} mph."
                )
                print(
                    f"WeatherService: Found forecast for {target_date.strftime('%Y-%m-%d')} - {summary}"
                )
                return {
                    "summary": summary,
                    "temperature_f": temp,
                    "feels_like_f": feels_like,
                    "description": weather_desc,
                    "humidity": humidity,
                    "wind_speed_mph": wind_speed,
                    "umbrella_recommended": False
                    if not (200 <= closest_forecast["weather"][0]["id"] < 600)
                    else True,
                    "raw_data": closest_forecast,
                }
            else:
                print(
                    f"WeatherService: No forecast found for exact local date {target_date.strftime('%Y-%m-%d')} within OWM data."
                )
                return {
                    "summary": f"Detailed weather forecast for {target_date.strftime('%A, %B %d')} is not available (OpenWeatherMap free tier provides 5-day forecast or timezone mismatch).",
                    "raw_data": {},
                }

        except requests.exceptions.RequestException as e:
            print(
                f"WeatherService: Error fetching weather forecast for {city_name}: {e}"
            )
            return {"summary": "Error fetching weather data.", "raw_data": {}}
        except pytz.UnknownTimeZoneError:
            print(
                f"WeatherService: Unknown timezone for city '{city_name}'. Please add it to city_timezones map."
            )
            return {
                "summary": f"Could not determine timezone for {city_name}. Weather forecast unavailable.",
                "raw_data": {},
            }
        except Exception as e:
            print(f"WeatherService: An unexpected error occurred: {e}")
            return {
                "summary": "An unexpected error occurred while fetching weather data.",
                "raw_data": {},
            }
