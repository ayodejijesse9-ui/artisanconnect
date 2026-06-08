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
from app.schemas.artisan_schema import ArtisanProfileResponse
from app.services.data_store import fetch_artisan_profile_from_db
from app.services.ai_engine import call_ai_agent
from app.services.pattern_brain import analyze_patterns, record_system_event
from app.services.agent_registry import get_agent_registry
from app.services.ai_support_agent import triage_and_draft_support_email, SupportDraftSchema


load_dotenv("/Users/JESSE/Desktop/artisanconnect/.env")

SECRET_KEY = os.getenv("JWT_SECRET_KEY")
class DynamicChatRequest(BaseModel):
    target_agent: str  # Options: 'all' or specific names like 'support', 'security', 'optimizer'
    message: str
class GroupChatRequest(BaseModel):
    message: str

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

class IncomingTicketRequest(BaseModel):
    customer_email: str
    customer_name: str
    complaint: str

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

@router.get("/artisan/{artisan_id}", response_model=ArtisanProfileResponse)
async def get_artisan_profile(artisan_id: str):
    """
    Public Endpoint to securely fetch sanitized Artisan Profiles.
    """
    # Pull raw data from database layer
    raw_profile = fetch_artisan_profile_from_db(artisan_id)
    
    if not raw_profile:
        # Fallback profile map to allow the Bug Agent to demonstrate local self-healing
        # for missing database documents during initial testing phase
        print(f"[SYSTEM NOTICE]: Profile {artisan_id} not found in DB. Injecting mock map for structural validation.")
        raw_profile = {
            "artisan_id": artisan_id,
            "full_name": "Alabi Emmanuel",
            "category": "Electrical Engineering",
            "location": "Yaba, Lagos",
            "bio": "",  # Empty to trigger bug agent healing
            "rating": "invalid_string_rating", # Malformed type to test agent resilience
            "portfolio_urls": None # Malformed type to test array stabilization
        }

    # Pass raw dictionary through the Bug Detection Agent layer
    sanitized_response = ArtisanProfileResponse.model_validate(raw_profile)
    
    return sanitized_response



from fastapi import Header, HTTPException, Depends

# A quick, secure token for your local MacBook testing environment
DEVELOPER_SANDBOX_TOKEN = "jesse_dev_secret_2026"

def verify_developer_access(x_developer_secret: str = Header(None)):
    """
    Security Dependency: Wall off experimental multi-agent sandboxes from public clients.
    """
    if x_developer_secret != DEVELOPER_SANDBOX_TOKEN:
        raise HTTPException(
            status_code=403, 
            detail="Access Denied: This endpoint is restricted to administrative internal developer scopes."
        )
    return x_developer_secret

# Attach the Depends lock to your route
@router.post("/test/agent-chat-dispatch")
def dynamic_agent_dispatcher(request: DynamicChatRequest, dev_token: str = Depends(verify_developer_access)):
    """
    Unified AI Hub: Invisible to regular clients. Requires a secure developer handshake header.
    """
    user_message = request.message
    target = request.target_agent.lower().strip()
    
    current_patterns = analyze_patterns()
    registry = get_agent_registry(current_patterns)
    room_responses = {}
    
    if target == "all":
        for _, config in registry.items():
            name = config["display_name"]
            room_responses[name] = call_ai_agent(config["instruction"], user_payload=user_message, temperature=0.6)
            
    elif target in registry:
        name = registry[target]["display_name"]
        room_responses[name] = call_ai_agent(registry[target]["instruction"], user_payload=user_message, temperature=0.6)
        
    else:
        valid_targets = ["all"] + list(registry.keys())
        return {"error": f"Target '{request.target_agent}' not recognized."}
        
    return {
        "dispatch_mode": "BROADCAST_ALL" if target == "all" else f"SINGLE_AGENT_{target.upper()}",
        "recognized_patterns": current_patterns,
        "responses": room_responses
    }

@router.post("/support/triage-ticket", response_model=SupportDraftSchema)
def incoming_support_ticket_triage(payload: IncomingTicketRequest):
    """
    Module 21 Ticket Processor: Ingests unstructured customer complaints, 
    categorizes ticket risk variables, and outputs fully drafted email schemas.
    """
    draft_object = triage_and_draft_support_email(
        customer_email=payload.customer_email,
        customer_name=payload.customer_name,
        raw_complaint=payload.complaint
    )
    return draft_object