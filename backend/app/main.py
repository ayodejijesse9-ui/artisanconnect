from fastapi import FastAPI, HTTPException

from typing import List, Optional
from backend.app.services.artisans import filter_artisans, search_artisans_by_rating 
from backend.app.models.artisan import Artisan, ArtisanCreate
from backend.app.models.booking import BookingRequest, BookingResponse
from backend.app.services.artisans import filter_artisans
from backend.app.services.artisans import filter_artisans, search_artisans_by_rating, search_bookings
from .services.artisans import search_artisans_by_rating

app = FastAPI(
    title="ArtisanConnect Nigeria",
    description="API for connecting verified skilled artisans to customers",
    version="1.0.0"
)

# Mock database
ARTISANS = [
    {
        "id": 1,
        "name": "Emeka Obi",
        "skill": "Electrician",
        "city": "Lagos",
        "verified": True,
        "rating": 4.8,
        "jobs_completed": 47
    },
    {
        "id": 2,
        "name": "Sadiq Musa",
        "skill": "Plumber",
        "city": "Abuja",
        "verified": False,
        "rating": 4.1,
        "jobs_completed": 9
    },
    {
        "id": 3,
        "name": "Chioma Okafor",
        "skill": "Painter",
        "city": "Lagos",
        "verified": True,
        "rating": 4.6,
        "jobs_completed": 31
    }
]

# Mock bookings storage
BOOKINGS = []


@app.get("/")
def read_root():
    return {
        "message": "ArtisanConnect Nigeria API is live",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/artisans", response_model=List[Artisan])
def get_artisans(
    city: Optional[str] = None,
    skill: Optional[str] = None,
    verified_only: Optional[bool] = None
):
    results = filter_artisans(ARTISANS, city=city, skill=skill, verified_only=verified_only)
    return results


@app.get("/artisans/{artisan_id}", response_model=Artisan)
def get_artisan(artisan_id: int):
    for artisan in ARTISANS:
        if artisan["id"] == artisan_id:
            return artisan
    raise HTTPException(status_code=404, detail=f"Artisan with id {artisan_id} not found")


@app.post("/artisans/register", response_model=Artisan, status_code=201)
def register_artisan(artisan: ArtisanCreate):
    new_id = max(a["id"] for a in ARTISANS) + 1
    new_artisan = {
        "id": new_id,
        "name": artisan.name,
        "skill": artisan.skill,
        "city": artisan.city,
        "verified": artisan.verified,
        "rating": artisan.rating,
        "jobs_completed": artisan.jobs_completed
    }
    ARTISANS.append(new_artisan)
    return new_artisan


@app.post("/bookings/", response_model=BookingResponse, status_code=201)
def create_booking(booking: BookingRequest):
    # Check artisan exists
    artisan = None
    for a in ARTISANS:
        if a["id"] == booking.artisan_id:
            artisan = a
            break

    if not artisan:
        raise HTTPException(
            status_code=404,
            detail=f"Artisan with id {booking.artisan_id} not found"
        )

    # Check artisan is verified
    if not artisan["verified"]:
        raise HTTPException(
            status_code=400,
            detail=f"Artisan {artisan['name']} is not yet verified"
        )

    # Generate booking ID
    new_booking_id = len(BOOKINGS) + 1

    # Build response
    response = {
        "booking_id": new_booking_id,
        "customer_name": booking.customer_name,
        "artisan_id": artisan["id"],
        "artisan_name": artisan["name"],
        "service_description": booking.service_description,
        "location": booking.location,
        "urgent": booking.urgent,
        "status": "pending",
        "message": f"Booking confirmed. {artisan['name']} will contact you shortly."
    }

    BOOKINGS.append(response)
    return response


@app.get("/bookings/", response_model=List[BookingResponse])
def get_bookings():from fastapi import FastAPI, HTTPException
from typing import List, Optional

from backend.app.models.artisan import Artisan, ArtisanCreate
from backend.app.models.booking import BookingRequest, BookingResponse
from backend.app.services.artisans import filter_artisans

app = FastAPI(
    title="ArtisanConnect Nigeria",
    description="API for connecting verified skilled artisans to customers",
    version="1.0.0"
)

# Mock database
ARTISANS = [
    {
        "id": 1,
        "name": "Emeka Obi",
        "skill": "Electrician",
        "city": "Lagos",
        "verified": True,
        "rating": 4.8,
        "jobs_completed": 47
    },
    {
        "id": 2,
        "name": "Sadiq Musa",
        "skill": "Plumber",
        "city": "Abuja",
        "verified": False,
        "rating": 4.1,
        "jobs_completed": 9
    },
    {
        "id": 3,
        "name": "Chioma Okafor",
        "skill": "Painter",
        "city": "Lagos",
        "verified": True,
        "rating": 4.6,
        "jobs_completed": 31
    }
]

# Mock bookings storage
BOOKINGS = []

# Unique booking ID counter — only ever goes up
booking_counter = 0


@app.get("/")
def read_root():
    return {
        "message": "ArtisanConnect Nigeria API is live",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/artisans", response_model=List[Artisan])
def get_artisans(
    city: Optional[str] = None,
    skill: Optional[str] = None,
    verified_only: Optional[bool] = None
):
    results = filter_artisans(ARTISANS, city=city, skill=skill, verified_only=verified_only)
    return results


@app.get("/artisans/{artisan_id}", response_model=Artisan)
def get_artisan(artisan_id: int):
    for artisan in ARTISANS:
        if artisan["id"] == artisan_id:
            return artisan
    raise HTTPException(status_code=404, detail=f"Artisan with id {artisan_id} not found")


@app.post("/artisans/register", response_model=Artisan, status_code=201)
def register_artisan(artisan: ArtisanCreate):
    new_id = max(a["id"] for a in ARTISANS) + 1
    new_artisan = {
        "id": new_id,
        "name": artisan.name,
        "skill": artisan.skill,
        "city": artisan.city,
        "verified": artisan.verified,
        "rating": artisan.rating,
        "jobs_completed": artisan.jobs_completed
    }
    ARTISANS.append(new_artisan)
    return new_artisan


@app.get("/bookings", response_model=List[BookingResponse])
def get_bookings():
    return BOOKINGS


@app.post("/bookings/create", response_model=BookingResponse, status_code=201)
def create_booking(booking: BookingRequest):
    global booking_counter

    # Check artisan exists
    artisan = None
    for a in ARTISANS:
        if a["id"] == booking.artisan_id:
            artisan = a
            break

    if not artisan:
        raise HTTPException(
            status_code=404,
            detail=f"Artisan with id {booking.artisan_id} not found"
        )

    # Check artisan is verified
    if not artisan["verified"]:
        raise HTTPException(
            status_code=400,
            detail=f"Artisan {artisan['name']} is not yet verified"
        )

    # Increment counter — always unique
    booking_counter += 1

    # Build response
    response = {
        "booking_id": booking_counter,
        "customer_name": booking.customer_name,
        "artisan_id": artisan["id"],
        "artisan_name": artisan["name"],
        "service_description": booking.service_description,
        "location": booking.location,
        "urgent": booking.urgent,
        "status": "pending",
        "message": f"Booking confirmed. {artisan['name']} will contact you shortly."
    }

    BOOKINGS.append(response)
    return response
    return BOOKINGS

@app.get("/artisans/search/by-rating")
def search_by_rating(min_rating: float = 4.0):
    results = search_artisans_by_rating(ARTISANS, min_rating)
    return {
        "min_rating": min_rating,
        "count": len(results),
        "artisans": results
    }

@app.get("/bookings/search")
def search_bookings_endpoint(
    customer_name: Optional[str] = None,
    status: Optional[str] = None
):
    results = search_bookings(BOOKINGS, customer_name=customer_name, status=status)
    return {
        "count": len(results),
        "bookings": results
    }