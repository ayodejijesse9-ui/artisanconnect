# ============================================
# ArtisanConnect Nigeria
# File: backend/app/main.py
# Author: Ayodeji Oluwajomiloju Jesse
# Purpose: Entry point for the ArtisanConnect server
# ============================================
 
 
def greet_artisan(name, skill):
    """
    Welcomes a new artisan to the ArtisanConnect platform.
    Parameters:
        name  -> the artisan full name e.g. Emeka Obi
        skill -> their primary trade e.g. electrician, plumber
    Returns:
        A welcome string
    """
    message = f"Welcome to ArtisanConnect, {name}!"
    message += f" Your registered skill is: {skill}."
    message += " Your profile is now live."
    return message
 
 
def calculate_booking_fee(job_amount, commission_rate=0.10):
    """
    Calculates the fee breakdown for a completed booking.
    Parameters:
        job_amount      -> total amount customer pays in Naira
        commission_rate -> ArtisanConnect percentage (default 10%)
    Returns:
        A dictionary with the full breakdown
    """
    platform_fee = job_amount * commission_rate
    artisan_receives = job_amount - platform_fee
 
    breakdown = {
        "job_amount": job_amount,
        "platform_fee": platform_fee,
        "artisan_receives": artisan_receives,
        "commission_percentage": commission_rate * 100
    }
    return breakdown
 
 
def display_booking_summary(artisan_name, skill, job_amount):
    """
    Displays a full booking summary to the terminal.
    Combines both functions above into one clean output.
    """
    print("=" * 50)
    print("ARTISANCONNECT — BOOKING SUMMARY")
    print("=" * 50)
    print(greet_artisan(artisan_name, skill))
    print()
    fee = calculate_booking_fee(job_amount)
    print(f"Job Amount:            N{fee['job_amount']:,}")
    print(f"Platform Commission:   {fee['commission_percentage']}%")
    print(f"Platform Earns:        N{fee['platform_fee']:,}")
    print(f"Artisan Receives:      N{fee['artisan_receives']:,}")
    print("=" * 50)
 
 
# ============================================
# This block only runs when you execute this
# file directly. It will not run when FastAPI
# imports this file as a module later.
# ============================================
if __name__ == "__main__":
 
    # Test 1 — Small job
    display_booking_summary("Emeka Obi", "Electrician", 10000)
    print()
 
    # Test 2 — Bigger job
    display_booking_summary("Bola Adeyemi", "Plumber", 45000)
    print()
 
    # Test 3 — Custom commission rate
    print("Custom 15% commission rate:")
    fee = calculate_booking_fee(80000, commission_rate=0.15)
    print(f"Platform earns: N{fee['platform_fee']:,}")
    print(f"Artisan earns:  N{fee['artisan_receives']:,}")
