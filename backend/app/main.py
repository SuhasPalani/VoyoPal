from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.database import initiate_database
from .routes import auth, trip_planning, data_fetch, user_preferences
from app.config import settings  # Import settings to get CORS origins


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Handles startup and shutdown events for the FastAPI application.
    Initializes the database connection.
    """
    await initiate_database()
    yield


app = FastAPI(
    title="VoyagePal AI Trip Planner API",
    description="Backend API for AI-powered trip planning using Google Gemini and MongoDB.",
    version="0.1.0",
    lifespan=lifespan,  # Attach the lifespan context manager
)

# Configure CORS (important for frontend to communicate)
# In production, replace "*" with your actual frontend domain(s)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
    ],  # Example: React development servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(trip_planning.router, prefix="/api/v1/trip", tags=["Trip Planning"])
app.include_router(data_fetch.router, prefix="/api/v1/data", tags=["Data Fetching"])
app.include_router(
    user_preferences.router, prefix="/api/v1/user", tags=["User Preferences"]
)


@app.get("/")
async def read_root():
    return {"message": "Welcome to VoyagePal API! Go to /docs for API documentation."}
