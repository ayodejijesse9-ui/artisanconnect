from pydantic import BaseModel, Field
from typing import Optional


class Customer(BaseModel):
    id: int
    name: str = Field(min_length=2)
    address: str
    phone: str
    city: str


class CustomerCreate(BaseModel):
    name: str = Field(
        min_length=2, 
        max_length=50,
        pattern=r'^[a-zA-Z\s]+$',
        description="Name must be between 2 and 50 characters and contain only letters and spaces."
        )
    address: str = Field(
    min_length=2,
    max_length=100,
    pattern=r"^[a-zA-Z0-9 .,'-]+$"
)
    phone: str = Field(
    min_length=7,
    max_length=15,
    pattern=r"^\+?[0-9 ]{7,15}$"
)
    city: str = Field(
        min_length=2,
        max_length=20,
        pattern=r'^[a-zA-Z\s]+$'
    )
