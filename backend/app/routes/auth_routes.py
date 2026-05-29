from pydantic import BaseModel, EmailStr, Field
from fastapi import APIRouter, HTTPException
from app.auth import hash_password
from app.services.data_store import load_user_by_email, load_users, save_user

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    role: str = Field(..., pattern="^(customer|artisan)$")

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register")
def auth_register(user: UserRegister):
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