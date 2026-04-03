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
    name: str = Field(min_length=2, max_length=50)
    skill: str = Field(min_length=2)
    city: str = Field(min_length=2)
    verified: bool = False
    rating: Optional[float] = Field(default=None, ge=0.0, le=5.0)
    jobs_completed: Optional[int] = Field(default=0, ge=0)