from beanie import Document
from pydantic import Field
from typing import List, Literal

class UserPreferences(Document):
    """MongoDB Document for storing user trip preferences."""
    user_id: str = Field(..., description="ID of the associated user.") # Reference to User._id
    interests: List[Literal["Culture & Museums", "Outdoor & Nature", "Food & Drink", "Architecture & City Views", "Family-Friendly", "Shopping & Entertainment"]] = Field(default_factory=list, description="List of preferred interests.")
    pace: Literal["fast-paced", "relaxed"] = Field("relaxed", description="Preferred trip pace.")
    preferred_transport: List[Literal["driving", "public_transit", "walking", "ride_share"]] = Field(default_factory=list, description="List of preferred transportation modes.")
    budget_range: Literal["budget", "mid-range", "luxury"] = Field("mid-range", description="Preferred budget range.")

    class Settings:
        name = "user_preferences"