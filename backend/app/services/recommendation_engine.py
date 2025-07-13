from typing import List, Dict, Any, Literal
from datetime import datetime
from app.services.gemini_service import GeminiService
from app.models.gemini_models import InitialTripSuggestions

class RecommendationEngine:
    """
    Orchestrates the recommendation process, primarily leveraging Gemini.
    In a more complex system, this would also integrate with a database
    of attractions, user history, etc.
    """
    def __init__(self, gemini_service: GeminiService):
        self.gemini_service = gemini_service

    async def get_initial_trip_suggestions(
        self,
        city: str,
        interests: List[str],
        pace: Literal["fast-paced", "relaxed"],
        trip_date: datetime,
        weather_data: Dict[str, Any]
    ) -> InitialTripSuggestions:
        """
        Uses Gemini to generate initial trip suggestions based on user preferences and weather.
        """
        # The core logic for generating suggestions is delegated to GeminiService
        suggestions = await self.gemini_service.get_initial_trip_suggestions(
            city=city,
            interests=interests,
            pace=pace,
            trip_date=trip_date,
            weather_data=weather_data
        )
        return suggestions