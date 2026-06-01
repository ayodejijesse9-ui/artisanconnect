import os
import resend
from dotenv import load_dotenv

load_dotenv("/Users/JESSE/Desktop/artisanconnect/.env")

resend.api_key = os.getenv("RESEND_API_KEY")
FROM_EMAIL = os.getenv("RESEND_FROM_EMAIL")

def send_password_reset_email(to_email: str, reset_token: str):
    reset_link = f"https://artisanconnect.ng/reset-password?token={reset_token}"
    
    params = {
        "from": FROM_EMAIL,
        "to": [to_email],
        "subject": "ArtisanConnect — Reset Your Password",
        "html": f"""
            <h2>Password Reset Request</h2>
            <p>You requested a password reset for your ArtisanConnect account.</p>
            <p>Click the link below to reset your password. This link expires in 15 minutes.</p>
            <a href="{reset_link}">Reset My Password</a>
            <p>If you did not request this, ignore this email.</p>
        """
    }
    
    try:
        response = resend.Emails.send(params)
        return response
    except Exception as e:
        print(f"Email sending failed: {e}")
        return None