from pydantic import BaseModel, Field
from typing import Optional, List, Literal, Dict, Any

class Location(BaseModel):
    """Pydantic model for a generic location, used in requests and internal logic."""
    name: str = Field(description="Name of the location.")
    address: Optional[str] = Field(None, description="Physical address of the location.")
    place_id: Optional[str] = Field(None, description="Google Places ID or similar external ID.")
    type: Literal["attraction", "restaurant", "transport_hub", "park", "museum", "landmark", "tour", "other"] = Field(description="Type of the location.")
    estimated_time_spent_minutes: int = Field(description="Estimated time needed to visit/experience this location in minutes.")
    admission_cost_usd: Optional[float] = Field(None, description="Estimated admission cost in USD. Null if free.")
    # The following fields are often returned by AI/external services
    reasons_for_suggestion: Optional[List[str]] = Field(None, description="Reasons why this location was suggested (from AI).")
    operating_hours_summary: Optional[str] = Field(None, description="Summary of typical operating hours.")
    # Add other relevant details like coordinates, phone number, website, etc.