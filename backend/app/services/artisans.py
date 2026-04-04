from typing import List, Optional
from backend.app.models.artisan import Artisan


def greet_artisan(name: str, skill: str) -> str:
    """
    Welcomes a new artisan to the platform.
    """
    message = f"Welcome to ArtisanConnect, {name}!"
    message += f" Your registered skill is: {skill}."
    message += " Your profile is now live."
    return message


def filter_artisans(
    artisans: List[dict],
    city: Optional[str] = None,
    skill: Optional[str] = None,
    verified_only: Optional[bool] = None
) -> List[dict]:
    """
    Filters a list of artisan dicts by city, skill, and verified status.
    All string comparisons are case-insensitive.
    """
    results = artisans

    if city:
        results = [a for a in results if a["city"].lower() == city.lower()]

    if skill:
        results = [a for a in results if a["skill"].lower() == skill.lower()]

    if verified_only:
        results = [a for a in results if a["verified"] is True]

    return results

def search_artisans_by_rating(artisans: list, min_rating: float) -> list:
    """
    Returns artisans with rating at or above the minimum.
    """
    return [a for a in artisans if a.get("rating") and a["rating"] >= min_rating]

def search_bookings(bookings: list, customer_name: str = None, status: str = None) -> list:
    """
    Filters bookings by customer name or status.
    Both comparisons are case-insensitive.
    """
    results = bookings

    if customer_name:
        results = [b for b in results if customer_name.lower() in b["customer_name"].lower()]

    if status:
        results = [b for b in results if b["status"].lower() == status.lower()]

    return results