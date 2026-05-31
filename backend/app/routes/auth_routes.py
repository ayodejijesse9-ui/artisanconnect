import os
from dotenv import load_dotenv
from pydantic import BaseModel, EmailStr, Field
from fastapi import APIRouter, HTTPException, Header, Depends, Request
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from app.auth import hash_password, verify_password, create_access_token,verify_token
from app.services.data_store import load_user_by_email, load_users, save_user
from app.limiter import limiter

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
load_dotenv("/Users/JESSE/Desktop/artisanconnect/.env")

SECRET_KEY = os.getenv("JWT_SECRET_KEY")

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    role: str = Field(..., pattern="^(customer|artisan)$")


router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register")           
@limiter.limit("5/minute")
def auth_register(request: Request, user: UserRegister):
    existing_user = load_user_by_email(user.email)
    if existing_user:
        raise HTTPException(status_code=409, detail="User with this email already exists")
    hashed_password = hash_password(user.password)
    new_user = {
        "id": len(load_users()) + 1,
        "email": user.email,
        "password": hashed_password,
        "role": user.role
    }
    save_user(new_user)
    return {"message": "User registered successfully"}

@router.post("/login")
@limiter.limit("5/minute")
def auth_login(request: Request, user: UserLogin):
    existing_user = load_user_by_email(user.email)
    if not existing_user:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    if not verify_password(user.password, existing_user["password"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    token = create_access_token({"sub": existing_user["email"], "role": existing_user["role"]})
    return {"access_token": token, "token_type": "bearer"}

def get_current_user(authorization: str = Header(None)):
    try:
        if not authorization:
            raise HTTPException(status_code=401, detail="Authorization header missing")
        token = authorization.split(" ")[1]
        payload = verify_token(token)
        email = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        user = load_user_by_email(email)
        if user is None:
            raise HTTPException(status_code=401, detail="User not found")
        return {"email": user["email"], "role": user["role"]}
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid token")

@router.get("/current-user")
def current_user_route(current_user: dict = Depends(get_current_user)):
    return current_user