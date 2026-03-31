from pydnatic import BaseModel

class Booking(BaseModel):
    customer_name: str
    artisan_name: str
    service: str
    amount: float
    is_paid: bool = False
    