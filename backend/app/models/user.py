from beanie import Document, Indexed
from pydantic import (
    Field,
    EmailStr,
)  # Use EmailStr directly, remove @model_validator workaround
from typing import Optional


class User(Document):
    """MongoDB Document for user data."""

    email: str  # Back to EmailStr directly
    hashed_password: str
    full_name: Optional[str] = None

    class Settings:
        name = "users"
