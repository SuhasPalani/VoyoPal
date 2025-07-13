from jose import JWTError, jwt
from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext
from typing import Optional

from fastapi import Depends, HTTPException, status  # Import FastAPI related parts
from fastapi.security import OAuth2PasswordBearer  # Import OAuth2PasswordBearer
from pydantic import BaseModel  # Import BaseModel

from app.config import settings
from app.models.user import (
    User,
)  # This import is crucial for get_current_user to find User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2PasswordBearer for handling token in headers
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="api/v1/auth/token"
)  # This matches your auth router prefix


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a plain password against a hashed password."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hashes a password."""
    return pwd_context.hash(password)


async def create_access_token(
    data: dict, expires_delta: Optional[timedelta] = None
) -> str:
    """Creates a JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt


# --- MOVE THIS FUNCTION HERE ---
class TokenData(BaseModel):
    email: Optional[str] = None


async def get_current_user(token: str = Depends(oauth2_scheme)):
    """Decodes JWT token and retrieves current user."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except JWTError:
        raise credentials_exception

    # This is the crucial part: User.find_one is an async database call
    # Ensure MongoDB is initialized before this runs
    user = await User.find_one(User.email == token_data.email)
    if user is None:
        raise credentials_exception
    return user


# --- END MOVE ---
