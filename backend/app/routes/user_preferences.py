from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from typing import List, Literal, Dict, Any
from app.models.user import User
from app.models.preferences import UserPreferences
from app.utils.auth_utils import get_current_user

router = APIRouter()


class UserPreferencesCreateUpdate(BaseModel):
    interests: List[
        Literal[
            "Culture & Museums",
            "Outdoor & Nature",
            "Food & Drink",
            "Architecture & City Views",
            "Family-Friendly",
            "Shopping & Entertainment",
        ]
    ] = Field(default_factory=list)
    pace: Literal["fast-paced", "relaxed"] = "relaxed"
    preferred_transport: List[
        Literal["driving", "public_transit", "walking", "ride_share"]
    ] = Field(default_factory=list)
    budget_range: Literal["budget", "mid-range", "luxury"] = "mid-range"


@router.get("/preferences", response_model=UserPreferences)
async def get_user_preferences(current_user: User = Depends(get_current_user)):
    """Retrieve user's trip preferences."""
    preferences = await UserPreferences.find_one(
        UserPreferences.user_id == str(current_user.id)
    )
    if not preferences:
        # Create default preferences if none exist
        default_prefs = UserPreferences(user_id=str(current_user.id))
        await default_prefs.insert()
        return default_prefs
    return preferences


@router.post(
    "/preferences", response_model=UserPreferences, status_code=status.HTTP_201_CREATED
)
async def create_user_preferences(
    prefs: UserPreferencesCreateUpdate, current_user: User = Depends(get_current_user)
):
    """Create user's trip preferences (if they don't exist)."""
    existing_prefs = await UserPreferences.find_one(
        UserPreferences.user_id == str(current_user.id)
    )
    if existing_prefs:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Preferences already exist for this user. Use PUT to update.",
        )

    new_prefs = UserPreferences(user_id=str(current_user.id), **prefs.model_dump())
    await new_prefs.insert()
    return new_prefs


@router.put("/preferences", response_model=UserPreferences)
async def update_user_preferences(
    prefs: UserPreferencesCreateUpdate, current_user: User = Depends(get_current_user)
):
    """Update user's trip preferences."""
    existing_prefs = await UserPreferences.find_one(
        UserPreferences.user_id == str(current_user.id)
    )
    if not existing_prefs:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Preferences not found for this user. Use POST to create.",
        )

    # Update fields
    existing_prefs.interests = prefs.interests
    existing_prefs.pace = prefs.pace
    existing_prefs.preferred_transport = prefs.preferred_transport
    existing_prefs.budget_range = prefs.budget_range

    await existing_prefs.save()
    return existing_prefs
