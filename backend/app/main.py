# ============================================
# ArtisanConnect Nigeria — main.py
# ============================================

from fastapi import FastAPI, HTTPException
from typing import List, Optional
from backend.app.services.data_store import save_artisans, load_artisans, save_bookings, load_bookings, save_customers, load_customers
from backend.app.models.artisan import Artisan, ArtisanCreate
from backend.app.models.booking import BookingRequest, BookingResponse
from backend.app.models.customer import Customer, CustomerCreate
from backend.app.services.artisans import search_artisans_by_rating, filter_artisans, search_bookings


app = FastAPI(
    title="ArtisanConnect Nigeria",
    description="API for connecting verified skilled artisans to customers",
    version="1.0.0",
)

# Mock databases
ARTISANS = load_artisans()
verified_names = [a["name"] for a in ARTISANS if a["verified"] == True]

CUSTOMERS = load_customers()

BOOKINGS = load_bookings()

# Unique booking ID counter
booking_counter = 0


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
        "total_artisans": len(ARTISANS),
        "total_bookings": len(BOOKINGS),
        "total_customers": len(CUSTOMERS),
    }


@app.get("/artisans", response_model=List[Artisan])
def get_artisans(
    city: Optional[str] = None,
    skill: Optional[str] = None,
    verified_only: Optional[bool] = None,
):
    results = filter_artisans(
        ARTISANS, city=city, skill=skill, verified_only=verified_only
    )
    return results


@app.get("/artisans/search/by-rating")
def search_by_rating(min_rating: float = 4.0):
    results = search_artisans_by_rating(ARTISANS, min_rating)
    return {"min_rating": min_rating, "count": len(results), "artisans": results}


@app.get("/artisans/{artisan_id}", response_model=Artisan)
def get_artisan(artisan_id: int):
    for artisan in ARTISANS:
        if artisan["id"] == artisan_id:
            return artisan
    raise HTTPException(
        status_code=404, detail=f"Artisan with id {artisan_id} not found"
    )


@app.get("/artisans/verified/names")
def get_verified_names():
    names = [a["name"] for a in ARTISANS if a["verified"] == True]
    return {"count": len(names), "names": names, "verified": True}


@app.post("/artisans/register", response_model=Artisan, status_code=201)
def register_artisan(artisan: ArtisanCreate):
    new_id = max((a["id"] for a in ARTISANS), default=0) + 1
    new_artisan = {
        "id": new_id,
        "name": artisan.name,
        "skill": artisan.skill,
        "city": artisan.city,
        "verified": artisan.verified,
        "rating": artisan.rating,
        "jobs_completed": artisan.jobs_completed,
    }
    ARTISANS.append(new_artisan)
    try:
        save_artisans(ARTISANS)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Artisan data not saved")
    return new_artisan


@app.get("/bookings", response_model=List[BookingResponse])
def get_bookings():
    return BOOKINGS


@app.get("/bookings/search")
def search_bookings_endpoint(
    customer_name: Optional[str] = None,
    status: Optional[str] = None
):
    results = search_bookings(BOOKINGS, customer_name = customer_name, status= status)
    return {
        "count": len(results), 
        "bookings": results}

@app.post("/bookings/create", response_model=BookingResponse, status_code=201)
def create_booking(booking: BookingRequest):
    global booking_counter
    try:
        artisan = None
        for a in ARTISANS:
            if a["id"] == booking.artisan_id:
                artisan = a
                break

        if not artisan:
            raise HTTPException(
                status_code=404,
                detail=f"Artisan with id {booking.artisan_id} not found",
            )

        if not artisan["verified"]:
            raise HTTPException(
                status_code=400,
                detail=f"Artisan {artisan['name']} is not yet verified"
            )

        booking_counter += 1

        response = {
            "booking_id": booking_counter,
            "customer_name": booking.customer_name,
            "artisan_id": artisan["id"],
            "artisan_name": artisan["name"],
            "service_description": booking.service_description,
            "location": booking.location,
            "urgent": booking.urgent,
            "status": "pending",
            "message": f"Booking confirmed. {artisan['name']} will contact you shortly.",
        }

        BOOKINGS.append(response)
        save_bookings(BOOKINGS)
        return response

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="Booking creation failed")


@app.get("/customers", response_model=List[Customer])
def get_customers():
    return CUSTOMERS


@app.post("/customers/create", response_model=Customer, status_code=201)
def create_customer(customer: CustomerCreate):
    new_id = len(CUSTOMERS) + 1
    new_customer = {
        "id": new_id,
        "name": customer.name,
        "phone": customer.phone,
        "address": customer.address,
        "city": customer.city,
    }
    CUSTOMERS.append(new_customer)
    try:
        save_customers(CUSTOMERS)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Customer data not saved")
    return new_customer
