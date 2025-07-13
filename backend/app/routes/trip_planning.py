from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Dict, Any, Optional, Literal

from app.services.gemini_service import GeminiService
from app.services.weather_service import WeatherService
from app.services.maps_routing_service import MapsRoutingService  # Placeholder
from app.services.attractions_service import AttractionsService  # Placeholder
from app.services.public_transit_service import PublicTransitService  # Placeholder
from app.services.budget_calculator import BudgetCalculator  # Placeholder
from app.services.recommendation_engine import RecommendationEngine

from app.models.user import User
from app.models.preferences import UserPreferences
from app.models.trip import Trip, TripLocation
from app.models.location import Location  # Base Location model
from app.utils.auth_utils import get_current_user
from app.models.gemini_models import (
    InitialTripSuggestions,
    TripPlanningAnalysis,
    OptimizedItinerary,
    SuggestedLocation,  # Used in request body
    InitialTripResponse,  # <--- ADDED THIS IMPORT
)

router = APIRouter()
gemini_service = GeminiService()
weather_service = WeatherService()
# Initialize other services (placeholders for now)
maps_routing_service = MapsRoutingService()
attractions_service = AttractionsService()
public_transit_service = PublicTransitService()
budget_calculator = BudgetCalculator()
recommendation_engine = RecommendationEngine(gemini_service)  # Pass gemini service


class InitialPlanRequest(BaseModel):
    destination: str = Field(..., description="The city for the trip, e.g., 'Chicago'.")
    return_time: str = Field(..., description="Desired return time, e.g., '11 PM'.")
    trip_date: str = Field(
        ..., description="Date of the trip in YYYY-MM-DD format, e.g., '2025-07-12'."
    )
    interests: List[
        Literal[
            "Culture & Museums",
            "Outdoor & Nature",
            "Food & Drink",
            "Architecture & City Views",
            "Family-Friendly",
            "Shopping & Entertainment",
        ]
    ] = Field(..., description="List of user interests.")
    pace: Literal["fast-paced", "relaxed"] = Field(
        ..., description="Preferred trip pace."
    )
    # Optional: allow preferred_transport and budget_range from initial request for better suggestions
    preferred_transport: List[
        Literal["driving", "public_transit", "walking", "ride_share"]
    ] = Field(default_factory=list)
    budget_range: Literal["budget", "mid-range", "luxury"] = "mid-range"


class LocationSelectionRequest(BaseModel):
    trip_id: Optional[str] = Field(
        None, description="ID of the existing draft trip to update."
    )
    destination: str = Field(..., description="The city for the trip.")
    trip_date: str = Field(..., description="Date of the trip in YYYY-MM-DD format.")
    return_time: str = Field(..., description="Desired return time.")
    user_preferences: Dict[str, Any] = Field(
        ..., description="Snapshot of user preferences used for this trip."
    )
    selected_locations: List[SuggestedLocation] = Field(
        ...,
        description="List of locations chosen by the user from initial suggestions.",
    )


@router.post(
    "/plan/initial-suggestions", response_model=InitialTripResponse
)  # <--- CHANGED RESPONSE_MODEL
async def get_initial_suggestions(
    request: InitialPlanRequest, current_user: User = Depends(get_current_user)
):
    """
    Get initial trip suggestions from Gemini based on user input and preferences.
    Saves a draft trip to the database.
    """
    try:
        trip_date_obj = datetime.strptime(request.trip_date, "%Y-%m-%d")

        # Fetch weather data for Gemini to consider
        weather_data = await weather_service.get_weather_forecast(
            request.destination, trip_date_obj
        )

        # Use RecommendationEngine which orchestrates GeminiService
        suggestions = await recommendation_engine.get_initial_trip_suggestions(
            city=request.destination,
            interests=request.interests,
            pace=request.pace,
            trip_date=trip_date_obj,
            weather_data=weather_data,  # Pass weather data to the engine
        )

        # Save initial draft trip to DB
        # Note: Beanie Document's _id is auto-generated on insert.
        new_trip = Trip(
            user_id=str(current_user.id),
            destination=request.destination,
            trip_date=trip_date_obj,
            return_time=request.return_time,
            preferences={
                "interests": request.interests,
                "pace": request.pace,
                "preferred_transport": request.preferred_transport,
                "budget_range": request.budget_range,
            },
            selected_locations=[],  # No locations selected yet
            itinerary=[],
            estimated_costs={},
            weather_info={
                "general_advice": suggestions.general_weather_advice,
                "clothing_suggestion": suggestions.clothing_suggestion,
                "umbrella_needed": suggestions.umbrella_needed,
                "raw_weather_data": weather_data,  # Store raw weather data for context
            },
            travel_tips=[],  # Will be filled later
        )
        await new_trip.insert()

        # Augment the response with the new trip's ID so frontend can track it
        response_data = suggestions.model_dump()
        response_data["trip_id"] = str(new_trip.id)  # Convert ObjectId to string

        return response_data  # This now matches InitialTripResponse model

    except Exception as e:
        print(f"Error in initial suggestions endpoint: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting initial suggestions: {e}",
        )


@router.post("/plan/detailed-analysis", response_model=TripPlanningAnalysis)
async def get_detailed_analysis(
    request: LocationSelectionRequest, current_user: User = Depends(get_current_user)
):
    """
    Get detailed trip analysis (weather, dress, costs, tips) based on selected locations.
    Updates the draft trip in the database.
    """
    try:
        trip_date_obj = datetime.strptime(request.trip_date, "%Y-%m-%d")

        # Fetch weather data for Gemini to consider
        weather_data = await weather_service.get_weather_forecast(
            request.destination, trip_date_obj
        )

        analysis = await gemini_service.get_detailed_trip_analysis(
            city=request.destination,
            trip_date=trip_date_obj,
            selected_locations=[loc.model_dump() for loc in request.selected_locations],
            return_time=request.return_time,
            user_preferences=request.user_preferences,
            weather_data=weather_data,  # Pass weather data to Gemini
        )

        # Update the draft trip in DB with analysis data
        if request.trip_id:
            existing_trip = await Trip.get(request.trip_id)
            if existing_trip and str(existing_trip.user_id) == str(current_user.id):
                existing_trip.weather_info.update(
                    {
                        "summary": analysis.weather_summary,
                        "clothing_suggestion": analysis.clothing_suggestion,
                        "umbrella_needed": analysis.carry_umbrella,
                    }
                )
                # Using update() for dicts to merge rather than overwrite
                existing_trip.estimated_costs.update(
                    {
                        "gas_usd": analysis.estimated_gas_cost_usd,
                        "public_transit_usd": analysis.estimated_public_transit_cost_usd,
                        "ride_share_usd": analysis.estimated_ride_share_cost_usd,
                        "general_money_tips": analysis.general_money_tips,
                    }
                )
                existing_trip.travel_tips = analysis.other_carry_items + [
                    analysis.transportation_tips
                ]
                existing_trip.selected_locations = [
                    TripLocation(**loc.model_dump())
                    for loc in request.selected_locations
                ]
                existing_trip.updated_at = datetime.utcnow()
                await existing_trip.save()
            else:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Trip not found or unauthorized.",
                )
        else:
            # If trip_id is not provided for analysis, this endpoint expects it to update an existing session.
            # You might choose to make it optional and create a new trip here if no ID is given.
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Trip ID is required for detailed analysis updates.",
            )

        return analysis
    except Exception as e:
        print(f"Error in detailed analysis endpoint: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting detailed analysis: {e}",
        )


@router.post("/plan/optimize-itinerary", response_model=OptimizedItinerary)
async def optimize_and_confirm_itinerary(
    request: LocationSelectionRequest,  # Can reuse this model
    current_user: User = Depends(get_current_user),
):
    """
    Generate and optimize the final itinerary.
    Updates the trip in the database with the final itinerary.
    """
    try:
        trip_date_obj = datetime.strptime(request.trip_date, "%Y-%m-%d")

        optimized_plan = await gemini_service.optimize_itinerary(
            city=request.destination,
            trip_date=trip_date_obj,
            selected_locations=[loc.model_dump() for loc in request.selected_locations],
            return_time=request.return_time,
            user_preferences=request.user_preferences,
        )

        # Update the trip in DB with the final itinerary
        if request.trip_id:
            existing_trip = await Trip.get(request.trip_id)
            if existing_trip and str(existing_trip.user_id) == str(current_user.id):
                existing_trip.itinerary = [
                    step.model_dump() for step in optimized_plan.itinerary_steps
                ]
                # Ensure total_itinerary_cost_usd is updated safely
                if existing_trip.estimated_costs is None:
                    existing_trip.estimated_costs = {}
                existing_trip.estimated_costs["total_itinerary_cost_usd"] = (
                    optimized_plan.total_estimated_cost_usd
                )
                existing_trip.updated_at = datetime.utcnow()
                await existing_trip.save()
            else:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Trip not found or unauthorized.",
                )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Trip ID is required for itinerary optimization.",
            )

        return optimized_plan
    except Exception as e:
        print(f"Error in optimize itinerary endpoint: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error optimizing itinerary: {e}",
        )


@router.get("/trips", response_model=List[Trip])
async def get_saved_trips(current_user: User = Depends(get_current_user)):
    """Retrieve all saved trips for the current user."""
    # Beanie returns Pydantic models which are automatically converted to dicts by FastAPI
    trips = await Trip.find(Trip.user_id == str(current_user.id)).to_list()
    # Manual conversion of ObjectId to string for consistency if needed, but Beanie handles it
    return trips
