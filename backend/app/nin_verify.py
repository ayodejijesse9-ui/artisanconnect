import os
import requests
from dotenv import load_dotenv
from fastapi import HTTPException

load_dotenv("/Users/JESSE/Desktop/artisanconnect/.env")

DOJAH_APP_ID = os.getenv("DOJAH_APP_ID")
DOJAH_SECRET_KEY = os.getenv("DOJAH_SECRET_KEY")

def verify_nin(nin: str) -> bool:
    if not DOJAH_APP_ID or not DOJAH_SECRET_KEY:
        raise HTTPException(status_code=500, detail="Dojah API credentials not configured")
    
    url = f"https://sandbox.dojah.io/api/v1/kyc/nin?nin={nin}"
    headers = {
        "AppId": DOJAH_APP_ID,
        "Authorization": DOJAH_SECRET_KEY
    }
    
    try:
        response = requests.get(url, headers=headers)
        print(f"Dojah status: {response.status_code}")
        print(f"Dojah response: {response.json()}")
        if response.status_code == 200:
            data = response.json()
            return data.get("entity") is not None
        return False
    except Exception as e:
        print(f"NIN verification error: {e}")
        return False
