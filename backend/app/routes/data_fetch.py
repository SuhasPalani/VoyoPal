from fastapi import APIRouter, Depends, HTTPException, status
from datetime import datetime
from typing import Dict, Any

from app.services.weather_service import WeatherService
from app.utils.auth_utils import get_current_user
from app.models.user import User # <--- ADD THIS IMPORT

router = APIRouter()
weather_service = WeatherService()

@router.get("/weather/{city_name}/{date_str}", response_model=Dict[str, Any])
async def get_weather_data(
    city_name: str,
    date_str: str, # YYYY-MM-DD
    current_user: User = Depends(get_current_user) # Example: requires authentication
):
    """
    Fetch weather forecast for a specific city and date.
    """
    try:
        # datetime.strptime will handle date parsing, then .date() extracts only the date part
        target_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        weather_info = await weather_service.get_weather_forecast(city_name, target_date)
        if not weather_info:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Weather data not available for this date.")
        return weather_info
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid date format. Use YYYY-MM-DD.")
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching weather data: {e}"
        )