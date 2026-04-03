from pydantic import BaseModel, Field
from typing import Optional


class BookingRequest(BaseModel):
    customer_name: str = Field(min_length=2, max_length=50)
    artisan_id: int
    service_description: str = Field(min_length=5)
    location: str = Field(min_length=2)
    urgent: bool = False


class BookingResponse(BaseModel):
    booking_id: int
    customer_name: str
    artisan_id: int
    artisan_name: str
    service_description: str
    location: str
    urgent: bool
    status: str
    message: str