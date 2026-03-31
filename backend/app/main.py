from fastapi import FastAPI, HTTPException
from typing import List, Optional

from backend.app.models.artisan import Artisan
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
    # BUG FIX 1: filter logic moved to service layer, not repeated inline
    results = filter_artisans(ARTISANS, city=city, skill=skill, verified_only=verified_only)
    return results


@app.get("/artisans/{artisan_id}", response_model=Artisan)
def get_artisan(artisan_id: int):
    for artisan in ARTISANS:
        # BUG FIX 2: was comparing string IDs to int in your curl tests
        if artisan["id"] == artisan_id:
            return artisan

    # BUG FIX 3: HTTPException was missing status_code on some paths
    raise HTTPException(status_code=404, detail=f"Artisan with id {artisan_id} not found")