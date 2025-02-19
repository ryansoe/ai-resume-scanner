# backend/user_router.py

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import Optional
from passlib.hash import bcrypt
from db import db
import jwt
import os
from datetime import datetime, timedelta
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

# We'll store the secret key in our .env, e.g., JWT_SECRET=mysupersecret
JWT_SECRET = os.getenv("JWT_SECRET", "testsecret")  # fallback for local dev

user_router = APIRouter()

# Pydantic models
class UserCreate(BaseModel):
    username: str
    password: str
    email: Optional[str] = None

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="users/login")  
# This tokenUrl should match the login endpoint

def create_jwt_token(username: str) -> str:
    """Generate a JWT token with an expiration."""
    expiration = datetime.utcnow() + timedelta(hours=2)
    payload = {
        "sub": username,
        "exp": expiration
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm="HS256")
    return token

@user_router.post("/register")
def register_user(user_data: UserCreate):
    """Register a new user, store hashed password in DB."""
    # Check if user already exists
    existing_user = db.users.find_one({"username": user_data.username})
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")

    hashed_password = bcrypt.hash(user_data.password)
    new_user = {
        "username": user_data.username,
        "password": hashed_password,
        "email": user_data.email
    }
    db.users.insert_one(new_user)

    return {"message": "User registered successfully"}

@user_router.post("/login")
def login_user(form_data: OAuth2PasswordRequestForm = Depends()):
    """User logs in with username & password. Return JWT if valid."""
    username = form_data.username
    password = form_data.password

    user = db.users.find_one({"username": username})
    if not user:
        raise HTTPException(status_code=401, detail="Invalid username or password")

    # Verify password
    if not bcrypt.verify(password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    # Create JWT
    token = create_jwt_token(username)
    return {"access_token": token, "token_type": "bearer"}

def get_current_user(token: str = Depends(oauth2_scheme)):
    """Decode JWT token to get the current user."""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        username = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Could not validate token")

    user = db.users.find_one({"username": username})
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")

    return user
