# ============================================
# ArtisanConnect Nigeria — fraud_agent.py
# ============================================

import os
import hmac
import hashlib

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