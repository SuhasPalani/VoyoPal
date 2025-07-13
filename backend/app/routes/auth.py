from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import (
    BaseModel,
    EmailStr,
)  # Keep EmailStr if you fixed the Pydantic error in user.py, otherwise it should be just 'str' now
from datetime import timedelta
from typing import Dict, Optional

from app.models.user import User
from app.utils.auth_utils import (
    create_access_token,
    verify_password,
    get_password_hash,
)  # get_current_user is REMOVED from here now
from app.config import settings

router = APIRouter()


class UserCreate(BaseModel):
    email: str  # Ensure this matches what's in models/user.py
    password: str
    full_name: str | None = None


class Token(BaseModel):
    access_token: str
    token_type: str


@router.post(
    "/register", response_model=Dict[str, str], status_code=status.HTTP_201_CREATED
)
async def register_user(user: UserCreate):
    """Register a new user."""
    existing_user = await User.find_one(User.email == user.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered"
        )
    hashed_password = get_password_hash(user.password)
    new_user = User(
        email=user.email, hashed_password=hashed_password, full_name=user.full_name
    )
    await new_user.insert()
    return {"message": "User registered successfully"}


@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """Login and get an access token."""
    user = await User.find_one(User.email == form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = await create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}
