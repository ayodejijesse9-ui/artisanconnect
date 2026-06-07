# ============================================
# ArtisanConnect Nigeria — auth_routes.py
# ============================================

import os
from dotenv import load_dotenv
from pydantic import BaseModel, EmailStr, Field
from fastapi import APIRouter, HTTPException, Header, Depends, Request
from app.email import send_password_reset_email 
from app.services.data_store import load_user_by_email, load_users, save_user, update_user_password, update_booking_status
from app.limiter import limiter
from app.auth import create_reset_token, verify_reset_token, hash_password, verify_password, create_access_token, verify_token
from app.services.fraud_agent import verify_paystack_signature

load_dotenv("/Users/JESSE/Desktop/artisanconnect/.env")

SECRET_KEY = os.getenv("JWT_SECRET_KEY")

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    role: str = Field(..., pattern="^(customer|artisan)$")

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str = Field(min_length=8, max_length=100)

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

def require_role(role: str):
    def check_role(current_user: dict = Depends(get_current_user)):
        if current_user["role"] != role:
            raise HTTPException(status_code=403, detail="Access forbidden")
        return current_user
    return check_role

@router.post("/forgot-password")           
def forgot_password(request: Request, forgot_password_request: ForgotPasswordRequest):
    existing_user = load_user_by_email(forgot_password_request.email)
    if not existing_user:
        return {"message": "If this email exists, a reset link has been sent"}
    reset_token = create_reset_token({"sub": existing_user["email"]})
    send_password_reset_email(forgot_password_request.email, reset_token)
    return {"message": "If this email exists, a reset link has been sent"}

@router.post("/reset-password")
def reset_password(request: Request, data: ResetPasswordRequest):
    email = verify_reset_token(data.token)
    if not email:
        raise HTTPException(status_code=400, detail="Invalid or expired reset token")
    existing_user = load_user_by_email(email)
    if not existing_user:
        raise HTTPException(status_code=400, detail="Invalid or expired reset token")
    hashed = hash_password(data.new_password)
    update_user_password(email, hashed)
    return {"message": "Password reset successful"}

@router.post("/paystack-webhook")
async def paystack_webhook_gateway(request: Request, x_paystack_signature: str = Header(None)):
    """
    Public Webhook Entrypoint monitored by the Fraud Detection Agent.
    """
    # 1. Grab the raw unparsed payload body bytes directly from the network stream
    raw_body = await request.body()
    
    # 2. If the header is missing entirely, drop the request instantly
    if not x_paystack_signature:
        raise HTTPException(status_code=401, detail="Security validation headers missing")

    # 3. Invoke the Fraud Detection Agent to analyze signatures
    is_legitimate = verify_paystack_signature(raw_body, x_paystack_signature)
    
    if not is_legitimate:
        # Flagging the request as unauthorized fraud attempt
        raise HTTPException(status_code=400, detail="Security signature confirmation failed")

    # 4. If verified, unpack payload safely and complete the business logic execution
    payload = await request.json()
    event = payload.get("event")
    
    if event == "charge.success":
        data = payload.get("data", {})
        reference = data.get("reference")
        metadata = data.get("metadata", {})
        booking_id = metadata.get("booking_id") # We pass this from the mobile app during checkout

        print(f"[PAYMENT SUCCESS]: Processing clear checkout for Reference {reference}")
        
        if booking_id:
            try:
                # Try to run the database function if defined
                update_booking_status(booking_id, "paid")
                print(f"[DATABASE SUCCESS]: Booking {booking_id} marked as paid.")
            except NameError:
                # Catching the missing import gracefully during our webhook testing stage
                print(f"[DATABASE WARNING]: 'update_booking_status' function is not imported yet, but payment was verified successfully!")
            except Exception as db_err:
                print(f"[DATABASE ERROR]: {db_err}")
            
    return {"status": "success", "message": "Webhook processed cleanly"}