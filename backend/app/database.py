from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from app.config import settings
from app.models.user import User
from app.models.trip import Trip
from app.models.preferences import UserPreferences

async def initiate_database():
    """Initializes MongoDB connection and Beanie ODM."""
    try:
        client = AsyncIOMotorClient(settings.MONGODB_URI)
        await init_beanie(database=client[settings.DB_NAME], document_models=[
            User,
            Trip,
            UserPreferences,
            # Add other Beanie Documents here as they are defined
        ])
        print(f"Successfully connected to MongoDB database: {settings.DB_NAME}")
    except Exception as e:
        print(f"Error connecting to MongoDB: {e}")
        # Depending on criticality, you might want to exit or retry here
        raise