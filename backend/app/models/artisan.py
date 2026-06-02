from pydantic import BaseModel, Field
from typing import Optional


class Artisan(BaseModel):
    id: int
    name: str = Field(min_length=2)
    skill: str
    city: str
    verified: bool = False
    rating: Optional[float] = None
    jobs_completed: Optional[int] = 0


class ArtisanCreate(BaseModel):
    name: str = Field(
        min_length=2, 
        max_length=50,
        pattern=r'^[a-zA-Z\s]+$',
        description="Name must be between 2 and 50 characters and contain only letters and spaces."
    )
    skill: str = Field(
        min_length=2,
        max_length=50,
        pattern=r'^[a-zA-Z\s]+$',
    )
    city: str = Field(
        min_length=2,
        max_length=20,
        pattern=r'^[a-zA-Z\s]+$'
    )
    rating: Optional[float] = Field(default=None, ge=0.0, le=5.0)
    jobs_completed: Optional[int] = Field(default=0, ge=0)

class NINVerifyRequest(BaseModel):
    artisan_id: int
    nin: str = Field(min_length=11, max_length=11)
