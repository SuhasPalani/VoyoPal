import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    """
    Configuration settings for the application.
    Loads environment variables from a .env file.
    """
    model_config = SettingsConfigDict(env_file='.env', extra='ignore')

    GOOGLE_API_KEY: str = Field(..., description="Your Google Gemini API Key")
    MONGODB_URI: str = Field(..., description="MongoDB connection URI")
    DB_NAME: str = "voyagepal_db" # Default database name
    JWT_SECRET_KEY: str = Field(..., description="Secret key for JWT token encryption. CHANGE THIS IN PRODUCTION!")
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # External API Keys
    OPENWEATHER_API_KEY: str = Field(..., description="Your OpenWeatherMap API Key")
    Maps_API_KEY: str = Field(..., description="Your Google Maps Platform API Key (for Places, Directions, etc.)")
    # Add other API keys as needed

settings = Settings()

