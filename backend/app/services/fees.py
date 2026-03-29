# backend/app/services/fees.py
 
def calculate_booking_fee(job_amount, commission_rate=0.10):
    """
    Calculates ArtisanConnect fee breakdown per booking.
    """
    platform_fee = job_amount * commission_rate
    artisan_receives = job_amount - platform_fee
    return {
        "job_amount": job_amount,
        "platform_fee": platform_fee,
        "artisan_receives": artisan_receives,
        "commission_percentage": commission_rate * 100
    }
