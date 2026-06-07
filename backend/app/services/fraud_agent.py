# ============================================
# ArtisanConnect Nigeria — fraud_agent.py
# ============================================

import os
import hmac
import json
import hashlib
from app.services.ai_engine import call_ai_agent


def verify_paystack_signature(raw_payload_bytes: bytes, incoming_signature: str) -> bool:
    """
    Fraud Detection Agent Layer: Generates a local HMAC SHA512 signature 
    using the system's secret key to verify request legitimacy.
    """
    secret_key = os.getenv("PAYSTACK_SECRET_KEY")
    if not secret_key:
        print("[FRAUD AGENT CRITICAL]: Paystack Secret Key missing from environment configurations.")
        return False

    # Compute local hash signature from raw request bytes
    computed_signature = hmac.new(
        secret_key.encode('utf-8'),
        raw_payload_bytes,
        hashlib.sha512
    ).hexdigest()

    # Compare local signature with the incoming header securely
    if hmac.compare_digest(computed_signature, incoming_signature):
        return True
        
    print("[FRAUD WARNING]: Unauthorized signature mismatch intercepted by security layer.")
    return False


def analyze_transaction_behavior(payload_dict: dict) -> bool:
    """
    AI Fraud Extension: Analyzes payload parameters for systemic risk behavior.
    """
    system_instruction = (
        "You are the ArtisanConnect Financial Risk Agent. Analyze the following metadata payload "
        "for payment transaction fraud or extreme manipulation (e.g., suspicious pricing scale or spoofed metadata values). "
        "Respond with exactly one word: 'SAFE' or 'SUSPICIOUS'. No commentary."
    )
    
    user_payload = json.dumps(payload_dict)
    assessment = call_ai_agent(system_instruction, user_payload, temperature=0.1)
    
    if "SUSPICIOUS" in assessment.upper():
        print("[AI FRAUD WARNING]: Transaction pattern flagged as an anomaly by semantic analysis.")
        return False
    return True