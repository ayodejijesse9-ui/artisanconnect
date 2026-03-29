# ============================================
# ArtisanConnect Nigeria — FastAPI Server
# File: backend/app/main.py
# Author: Ayodeji Oluwajomiloju Jesse
# ============================================
 
from fastapi import FastAPI, HTTPException
from typing import Optional
 
# Create the FastAPI application instance
app = FastAPI(
    title="ArtisanConnect Nigeria API",
    description="Connecting verified artisans to customers across Nigeria",
    version="1.0.0"
)
 
 
# ============================================
# TEST DATA — replaced with Firebase in Week 8
# ============================================
ARTISANS = [
    {
        "id": "art_001",
        "name": "Emeka Obi",
        "skill": "electrician",
        "city": "Lagos",
        "rating": 4.8,
        "verified": True,
        "jobs_completed": 47
    },
    {
        "id": "art_003",
        "name": "Chidi Nwosu",
        "skill": "carpenter",
        "city": "Abuja",
        "rating": 4.9,
        "verified": True,
        "jobs_completed": 89
    },
    {
        "id": "art_004",
        "name": "Taiwo Ojo",
        "skill": "electrician",
        "city": "Lagos",
        "rating": 4.3,
        "verified": False,
        "jobs_completed": 12
    },
]
 
 
# ============================================
# ENDPOINT 1 — Root: confirm server is running
# ============================================
@app.get("/")
def read_root():
    """Root endpoint — confirms the API is live"""
    return {
        "message": "ArtisanConnect Nigeria API is live",
        "version": "1.0.0",
        "status": "running"
    }
 
 
# ============================================
# ENDPOINT 2 — Get all artisans with filters
# ============================================
@app.get("/artisans")
def get_artisans(
    city: Optional[str] = None,
    skill: Optional[str] = None,
    verified_only: bool = False
):
    """
    Returns artisans. Filter by city, skill, or verified status.
    Example: /artisans?city=Lagos&skill=plumber&verified_only=true
    """
    results = ARTISANS
 
    if city:
        results = [a for a in results if a['city'].lower() == city.lower()]
 
    if skill:
        results = [a for a in results if a['skill'].lower() == skill.lower()]
 
    if verified_only:
        results = [a for a in results if a['verified'] == True]
 
    return {
        "count": len(results),
        "artisans": results
    }
 
 
# ============================================
# ENDPOINT 3 — Get one artisan by ID
# ============================================
@app.get("/artisans/{artisan_id}")
def get_artisan(artisan_id: str):
    """
    Returns one artisan by their ID.
    Example: /artisans/art_001
    """
    for artisan in ARTISANS:
        if artisan['id'] == artisan_id:
            return artisan
 
    raise HTTPException(status_code=404, detail='Artisan not found')

