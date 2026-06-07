import json
import hmac
import hashlib
import requests

URL = "http://127.0.0.1:8000/auth/paystack-webhook"
SECRET_KEY = "sk_test_50b5d144ae5fccc831b29b47a48c2d53efbcd5f8"

mock_payload = {
    "event": "charge.success",
    "data": {
        "reference": "ART-TX-998822",
        "amount": 1500000,
        "currency": "NGN",
        "metadata": {
            "booking_id": "MOCK_BOOKING_123"
        }
    }
}

payload_bytes = json.dumps(mock_payload, separators=(',', ':')).encode('utf-8')

print("🚀 Starting Webhook Gateway Security Testing...\n")

# --- SIMULATION A: LEGITIMATE PAYSTACK TRANSACTION ---
correct_signature = hmac.new(
    SECRET_KEY.encode('utf-8'),
    payload_bytes,
    hashlib.sha512
).hexdigest()

headers_legit = {
    "Content-Type": "application/json",
    "x-paystack-signature": correct_signature
}

print("[SIMULATION A]: Sending valid signed transaction stream...")
response_a = requests.post(URL, data=payload_bytes, headers=headers_legit)
print(f"Result Status: {response_a.status_code} | Raw Text: {response_a.text}\n")

# --- SIMULATION B: TAMPERED FORGERY ATTACK ---
headers_malicious = {
    "Content-Type": "application/json",
    "x-paystack-signature": "fake_forged_signature_hash_123456"
}

print("[SIMULATION B]: Launching unverified signature brute-force injection...")
response_b = requests.post(URL, data=payload_bytes, headers=headers_malicious)
print(f"Result Status: {response_b.status_code} | Server Response: {response_b.text}\n")
