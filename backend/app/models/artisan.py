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