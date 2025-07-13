from pydantic import BaseModel, Field
from typing import List, Literal, Optional, Dict, Any
from app.models.location import Location  # Use the common Location model

# --- Models for Gemini's structured output ---


class SuggestedLocation(Location):
    """Represents a suggested location from Gemini, inheriting from Location."""

    reasons_for_suggestion: List[str] = Field(
        description="Reasons why this location is suggested based on user preferences."
    )
    operating_hours_summary: str = Field(
        description="Summary of typical operating hours for the day of the trip."
    )
    # The base Location model already has: name, type, description, estimated_visit_time_minutes, admission_cost_usd


class InitialTripSuggestions(BaseModel):
    """Response model for initial Gemini suggestions."""

    general_weather_advice: str = Field(
        description="General advice about the weather for the trip day."
    )
    clothing_suggestion: str = Field(description="Suggestion for what to wear.")
    umbrella_needed: bool = Field(
        description="True if an umbrella or rain gear is recommended."
    )
    location_suggestions: List[SuggestedLocation] = Field(
        description="List of suggested locations based on user preferences."
    )


# --- NEW MODEL ADDED HERE ---
class InitialTripResponse(InitialTripSuggestions):
    """
    Response model for initial Gemini suggestions endpoint, including the new trip_id.
    Inherits all fields from InitialTripSuggestions.
    """

    trip_id: str = Field(
        description="The unique ID of the newly created draft trip in the database."
    )


# --- END NEW MODEL ---


class OptimizedItineraryStep(BaseModel):
    """Represents a single step in the optimized itinerary."""

    activity: str = Field(
        description="Description of the activity (e.g., 'Visit The Art Institute of Chicago')."
    )
    start_time: str = Field(
        description="Start time of the activity (e.g., '10:30 AM')."
    )
    end_time: str = Field(description="End time of the activity (e.g., '2:00 PM').")
    location_name: str = Field(description="Name of the location for this activity.")
    address: Optional[str] = Field(None, description="Address of the location.")
    transport_mode_to_next: Optional[
        Literal["walk", "public_transit", "ride_share", "drive"]
    ] = Field(None, description="Recommended mode of transport to the next step.")
    estimated_travel_time_minutes: Optional[int] = Field(
        None, description="Estimated travel time to the next step in minutes."
    )
    notes: Optional[str] = Field(
        None,
        description="Any specific notes for this step (e.g., 'Buy tickets online').",
    )


class OptimizedItinerary(BaseModel):
    """Response model for the full optimized itinerary."""

    itinerary_steps: List[OptimizedItineraryStep] = Field(
        description="Ordered list of itinerary steps."
    )
    total_estimated_cost_usd: float = Field(
        description="Total estimated cost for the entire itinerary."
    )
    feasibility_status: Literal["possible", "tight_but_possible", "not_possible"] = (
        Field(description="Assessment of whether the itinerary is feasible.")
    )
    feasibility_notes: Optional[str] = Field(
        None,
        description="Notes on feasibility, e.g., if it's tight, what to prioritize.",
    )
    total_travel_time_minutes: int = Field(
        description="Total estimated travel time for the day."
    )
    total_activity_time_minutes: int = Field(
        description="Total estimated time spent at activities."
    )


class TripPlanningAnalysis(BaseModel):
    """Comprehensive analysis from Gemini for trip planning details."""

    weather_summary: str = Field(
        description="Summary of the weather, including temperature, conditions, and any warnings."
    )
    clothing_suggestion: str = Field(description="Detailed clothing recommendation.")
    carry_umbrella: bool = Field(
        description="True if an umbrella or rain gear is recommended."
    )
    estimated_gas_cost_usd: Optional[float] = Field(
        None, description="Estimated gas cost if driving."
    )
    estimated_public_transit_cost_usd: Optional[float] = Field(
        None, description="Estimated public transit cost."
    )
    estimated_ride_share_cost_usd: Optional[float] = Field(
        None, description="Estimated ride-share cost."
    )
    general_money_tips: str = Field(
        description="General advice on managing money for the trip."
    )
    transportation_tips: str = Field(
        description="General tips for chosen transportation methods (e.g., parking, bus routes)."
    )
    other_carry_items: List[str] = Field(
        description="Other essential items to carry (e.g., sunscreen, water bottle)."
    )
    location_info: List[Dict[str, Any]] = Field(
        description="Detailed information about each selected location, including general info, typical hours, etc."
    )
