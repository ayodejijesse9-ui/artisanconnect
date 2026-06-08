# ============================================
# ArtisanConnect Nigeria — ai_engine.py (Updated Model)
# ============================================

import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), "../../../.env"))
load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    print("[SYSTEM CRITICAL]: GROQ_API_KEY missing from environment configurations.")
    groq_client = None
else:
    print("[SYSTEM SUCCESS]: Global AI Agent Engine Initialized cleanly.")
    groq_client = Groq(api_key=GROQ_API_KEY)

def call_ai_agent(system_instruction: str, user_payload: str, temperature: float = 0.2) -> str:
    if not groq_client:
        return ""
    try:
        # UPDATED: Swapped to the active production model identifier
        completion = groq_client.chat.completions.create(
            model="llama-3.1-8b-instant", 
            messages=[
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": user_payload}
            ],
            temperature=temperature,
            max_tokens=400
        )
        return completion.choices[0].message.content.strip()
    except Exception as e:
        print(f"[GLOBAL AI AGENT ERROR]: Inference execution failed: {e}")
        return ""