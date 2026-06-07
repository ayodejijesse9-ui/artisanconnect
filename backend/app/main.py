# ============================================
# ArtisanConnect Nigeria — main.py
# ============================================

from fastapi import FastAPI, HTTPException, Depends, Request
from typing import List, Optional
from pydantic import BaseModel
from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler
from fastapi.middleware.cors import CORSMiddleware
from app.ai_match import extract_job_details, match_artisans
from app.routes.auth_routes import get_current_user, require_role, router as auth_router
from app.models.artisan import Artisan, ArtisanCreate, NINVerifyRequest
from app.models.booking import BookingRequest, BookingResponse
from app.models.customer import Customer, CustomerCreate
from app.services.artisans import search_artisans_by_rating, filter_artisans, search_bookings
from app.services.data_store import (
    load_artisans, load_artisan_by_id, save_single_artisan, 
    load_bookings, save_new_booking, update_booking_status,
    load_customers, save_single_customer, update_artisan_verified
)
from app.limiter import limiter
from app.nin_verify import verify_nin

class MatchRequest(BaseModel):
    job_description: str

app = FastAPI(
    title="ArtisanConnect Nigeria",
    description="API for connecting verified skilled artisans to customers",
    version="1.0.0",
)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.include_router(auth_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://artisanconnect.ng"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {
        "message": "ArtisanConnect Nigeria API is live",
        "version": "1.0.0",
        "status": "running",
    }

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "api": "ArtisanConnect Nigeria",
        "version": "1.0.0",
        "total_artisans": len(load_artisans()),
        "total_bookings": len(load_bookings()),
        "total_customers": len(load_customers()),
    }

@app.get("/artisans", response_model=List[Artisan])
@limiter.limit("30/minute")
def get_artisans(
    request: Request,
    city: Optional[str] = None,
    skill: Optional[str] = None,
    verified_only: Optional[bool] = None,
):
    # Fetch live data stream on request
    live_artisans = load_artisans()
    results = filter_artisans(
        live_artisans, city=city, skill=skill, verified_only=verified_only
    )
    return results

@app.get("/artisans/search/by-rating")
def search_by_rating(min_rating: float = 4.0):
    live_artisans = load_artisans()
    results = search_artisans_by_rating(live_artisans, min_rating)
    return {"min_rating": min_rating, "count": len(results), "artisans": results}

@app.get("/artisans/{artisan_id}", response_model=Artisan)
def get_artisan(artisan_id: int):
    artisan = load_artisan_by_id(artisan_id)
    if artisan:
        return artisan
    raise HTTPException(
        status_code=404, detail=f"Artisan with id {artisan_id} not found"
    )

@app.get("/artisans/verified/names")
def get_verified_names():
    live_artisans = load_artisans()
    names = [a["name"] for a in live_artisans if a.get("verified") == True]
    return {"count": len(names), "names": names, "verified": True}

@app.post("/artisans/register", response_model=Artisan, status_code=201)
def register_artisan(artisan: ArtisanCreate, current_user: dict = Depends(require_role("artisan"))):
    live_artisans = load_artisans()
    new_id = max((a["id"] for a in live_artisans), default=0) + 1
    new_artisan = {
        "id": new_id,
        "name": artisan.name,
        "skill": artisan.skill,
        "city": artisan.city,
        "verified": False,
        "rating": artisan.rating,
        "jobs_completed": artisan.jobs_completed,
    }
    try:
        save_single_artisan(new_artisan)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Artisan data not saved")
    return new_artisan

@app.get("/bookings")
def get_bookings():
    return load_bookings()

@app.get("/bookings/search")
def search_bookings_endpoint(
    customer_name: Optional[str] = None,
    status: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    results = search_bookings(load_bookings(), customer_name=customer_name, status=status)
    return {"count": len(results), "bookings": results}

@app.post("/bookings/create", status_code=201)
@limiter.limit("10/minute")
def create_booking(booking: BookingRequest, request: Request, current_user: dict = Depends(require_role("customer"))):
    try:
        # Fetch the artisan directly from Firestore right now to verify state security
        artisan = load_artisan_by_id(booking.artisan_id)

        if not artisan:
            raise HTTPException(
                status_code=404,
                detail=f"Artisan with id {booking.artisan_id} not found",
            )

        if not artisan.get("verified"):
            raise HTTPException(
                status_code=400,
                detail=f"Artisan {artisan['name']} is not yet verified by KYC systems"
            )

        # Prepare payload dictionary — placeholder value for booking_id will be overwritten by Firestore auto-ID
        response_data = {
            "booking_id": "PENDING",
            "customer_name": booking.customer_name,
            "artisan_id": artisan["id"],
            "artisan_name": artisan["name"],
            "service_description": booking.service_description,
            "location": booking.location,
            "urgent": booking.urgent,
            "status": "requested",
            "message": f"Booking confirmed. {artisan['name']} will contact you shortly.",
        }

        # Save to Cloud and get back the auto-generated unique string ID
        generated_string_id = save_new_booking(response_data)
        response_data["booking_id"] = generated_string_id

        return response_data

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="Booking transaction generation failed")

@app.get("/customers", response_model=List[Customer])
def get_customers():
    return load_customers()

@app.post("/customers/create", response_model=Customer, status_code=201)
def create_customer(customer: CustomerCreate, current_user: dict = Depends(require_role("customer"))):
    live_customers = load_customers()
    new_id = len(live_customers) + 1
    new_customer = {
        "id": new_id,
        "name": customer.name,
        "phone": customer.phone,
        "address": customer.address,
        "city": customer.city,
    }
    try:
        save_single_customer(new_customer)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Customer data not saved")
    return new_customer

@app.post("/artisans/verify-nin")
def verify_artisan_nin(data: NINVerifyRequest, current_user: dict = Depends(require_role("artisan"))):
    if not verify_nin(data.nin):
        raise HTTPException(status_code=400, detail="Invalid NIN or verification failed")
    updated = update_artisan_verified(data.artisan_id)
    if not updated:
        raise HTTPException(status_code=404, detail="Artisan not found")
    return {"message": "NIN verified successfully", "artisan_id": data.artisan_id}

@app.post("/artisans/match")
def match_artisans_endpoint(data: MatchRequest):
    live_artisans = load_artisans()
    job_details = extract_job_details(data.job_description)
    matches = match_artisans(job_details, live_artisans)
    return {
        "job_details": job_details,
        "matches": matches,
        "count": len(matches)
    }

@app.post("/bookings/{booking_id}/accept")
def accept_booking(booking_id: str, current_user: dict = Depends(require_role("artisan"))):
    updated = update_booking_status(booking_id, "confirmed")
    if not updated:
        raise HTTPException(status_code=404, detail="Booking record not found")
    return {"message": "Booking accepted by artisan", "booking_id": booking_id}

@app.post("/bookings/{booking_id}/reject")
def reject_booking(booking_id: str, current_user: dict = Depends(require_role("artisan"))):
    updated = update_booking_status(booking_id, "rejected")
    if not updated:
        raise HTTPException(status_code=404, detail="Booking record not found")
    return {"message": "Booking rejected by artisan", "booking_id": booking_id}