import os
import json
from groq import Groq
from dotenv import load_dotenv

load_dotenv("/Users/JESSE/Desktop/artisanconnect/.env")

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def extract_job_details(description: str) -> dict:
    message = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        max_tokens=200,
        messages=[
            {
                "role": "system",
                "content": 
                    "Return ONLY a valid JSON object with exactly these keys: skill, location, urgent. "
                    "urgent must be a boolean. "
                    "For location, always return the major city name only — never a district, area, or neighborhood. "
                    "For example: Lekki, Victoria Island, Surulere, Ikeja → Lagos. Wuse, Maitama, Garki → Abuja. "
                    "No markdown, no explanation, just raw JSON."
            },
            {
                "role": "user",
                "content": description
            }
        ]
    )
    return json.loads(message.choices[0].message.content)

def match_artisans(job_details: dict, artisans: list) -> list:
    skill = job_details.get("skill", "").lower()
    location = job_details.get("location", "").lower()
    
    matches = [
        a for a in artisans
        if a.get("verified") == True
        and (skill in a.get("skill", "").lower() or a.get("skill", "").lower() in skill)
        and location in a.get("city", "").lower()
    ]
    
    matches.sort(key=lambda a: a.get("rating") or 0, reverse=True)
    return matches[:3]
