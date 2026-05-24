from pydantic import BaseModel, Field
from typing import Optional


class Customer(BaseModel):
    id: int
    name: str = Field(min_length=2)
    address: str
    phone: str
    city: str


class CustomerCreate(BaseModel):
    name: str = Field(min_length=2, max_length=50)
    address: str = Field(min_length=2)
    phone: str = Field(min_length=0, max_length=15)
    city: str = Field(min_length=2)
