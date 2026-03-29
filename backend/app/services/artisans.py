# backend/app/services/artisans.py
 
def greet_artisan(name, skill):
    """
    Welcomes a new artisan to the platform.
    """
    message = f"Welcome to ArtisanConnect, {name}!"
    message += f" Your registered skill is: {skill}."
    message += " Your profile is now live."
    return message
