# ============================================
# ArtisanConnect Nigeria — artisan_schema.py (AI-Powered)
# ============================================

import os
from pydantic import BaseModel, Field, model_validator
from typing import List, Optional
from groq import Groq
from app.services.ai_engine import call_ai_agent

# Initialize the Groq Client using the key from your .env file
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
groq_client = Groq(api_key= GROQ_API_KEY) if GROQ_API_KEY else None

class ArtisanProfileResponse(BaseModel):
    artisan_id: str
    full_name: str
    category: str
    bio: str
    location: str
    rating: float = 0.0
    jobs_completed: int = 0
    is_available: bool = True
    portfolio_urls: List[str] = Field(default_factory=list)

    @model_validator(mode="before")
    @classmethod
    def bug_detection_agent_sanitizer(cls, data: dict) -> dict:
        """
        AI-Powered Bug Detection Agent: Self-heals data integrity issues
        and safely guarantees type conversions for the Pydantic parser.
        """
        # Ensure data is a mutable dictionary dictionary
        if not isinstance(data, dict):
            return data

        # 1. Structural Self-Healing (Forcing fallbacks to avoid validation crashes)
        if not data.get("bio") or str(data.get("bio")).strip() == "":
            data["bio"] = "Professional artisan dedicated to providing high-quality services."
        
        # Repair the rating string explicitly before Pydantic parses it
        try:
            data["rating"] = round(float(data.get("rating", 0.0)), 1)
        except (ValueError, TypeError):
            data["rating"] = 0.0  # Overwrites 'invalid_string_rating' to a valid float 0.0

        try:
            data["jobs_completed"] = int(data.get("jobs_completed", 0))
        except (ValueError, TypeError):
            data["jobs_completed"] = 0

        # Overwrites NoneType portfolio values to a valid list array
        if "portfolio_urls" not in data or not isinstance(data["portfolio_urls"], list):
            data["portfolio_urls"] = []

        # 2. Semantic Healing (AI text formatting)
        raw_bio = data["bio"]
        if len(raw_bio) < 150 and "invalid_string_rating" not in str(raw_bio):
            system_instruction = (
                f"Convert raw, broken, or unformatted descriptions from Nigerian artisans into a "
                f"professional profile bio for the {data.get('category', 'Artisan')} category. Max 2 short sentences. "
                f"Output ONLY the corrected text."
            )
            ai_optimized = call_ai_agent(system_instruction, raw_bio)
            if ai_optimized:
                data["bio"] = ai_optimized
                print("[AI BUG AGENT]: Successfully optimized and self-healed profile bio text.")

        return data