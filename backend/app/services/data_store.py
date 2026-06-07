# ============================================
# ArtisanConnect Nigeria — data_store.py
# ============================================
import os
from typing import Optional
import firebase_admin
from firebase_admin import credentials, firestore
from dotenv import load_dotenv


load_dotenv()

# Initialize Firebase
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
cred_path = os.path.join(BASE_DIR, "firebase-credentials.json")

if not firebase_admin._apps:
    cred = credentials.Certificate(cred_path)
    firebase_admin.initialize_app(cred)

db = firestore.client()

# --- ARTISAN OPERATIONS ---

def load_artisans() -> list:
    """Loads all artisans dynamically from Firestore."""
    try:
        docs = db.collection("artisans").stream()
        return [doc.to_dict() for doc in docs]
    except Exception as e:
        print(f"Error loading artisans: {e}")
        return []

def load_artisan_by_id(artisan_id: int) -> dict | None:
    """Fetches a single artisan document directly using constant time lookup."""
    try:
        # Querying by the 'id' field inside the document
        docs = db.collection("artisans").where("id", "==", artisan_id).limit(1).stream()
        for doc in docs:
            return doc.to_dict()
        return None
    except Exception as e:
        print(f"Error loading artisan by id {artisan_id}: {e}")
        return None

def save_single_artisan(artisan_dict: dict) -> None:
    """Saves or updates a single artisan record using its field ID as the Document Key."""
    try:
        doc_id = str(artisan_dict["id"])
        db.collection("artisans").document(doc_id).set(artisan_dict)
    except Exception as e:
        print(f"Error saving individual artisan: {e}")

def update_artisan_verified(artisan_id: int) -> bool:
    """Permanently marks an artisan as verified inside Firestore."""
    try:
        docs = db.collection("artisans").where("id", "==", artisan_id).stream()
        for doc in docs:
            db.collection("artisans").document(doc.id).update({"verified": True})
            return True
        return False
    except Exception as e:
        print(f"Error updating artisan verification: {e}")
        return False

# --- BOOKING OPERATIONS ---

def load_bookings() -> list:
    """Loads all system transactions from Firestore."""
    try:
        docs = db.collection("bookings").stream()
        return [doc.to_dict() for doc in docs]
    except Exception as e:
        print(f"Error loading bookings: {e}")
        return []

def save_new_booking(booking_dict: dict) -> str:
    """
    Saves a transaction payload to Firestore and allows the cloud 
    engine to auto-generate a secure, random unique string Document ID.
    """
    try:
        # .add() automatically generates a unique string key like 'Bk9JzL2pQxB7m'
        doc_ref = db.collection("bookings").add(booking_dict)
        # Store that auto-generated unique string directly inside the record field too
        db.collection("bookings").document(doc_ref[1].id).update({"booking_id": doc_ref[1].id})
        return doc_ref[1].id
    except Exception as e:
        print(f"Error executing cloud auto-id booking write: {e}")
        raise

def update_booking_status(booking_id: str, status: str) -> bool:
    """Updates status using the string-based Auto-ID reference key."""
    try:
        doc_ref = db.collection("bookings").document(booking_id)
        if doc_ref.get().exists:
            doc_ref.update({"status": status})
            return True
        return False
    except Exception as e:
        print(f"Error modifying status on booking {booking_id}: {e}")
        return False

# --- CUSTOMER OPERATIONS ---

def load_customers() -> list:
    """Loads all customers from Firestore."""
    try:
        docs = db.collection("customers").stream()
        return [doc.to_dict() for doc in docs]
    except Exception as e:
        print(f"Error loading customers: {e}")
        return []

def save_single_customer(customer_dict: dict) -> None:
    """Saves an individual customer using their integer identifier as the key."""
    try:
        doc_id = str(customer_dict["id"])
        db.collection("customers").document(doc_id).set(customer_dict)
    except Exception as e:
        print(f"Error saving customer document: {e}")

# --- USER & ACCOUNT OPERATIONS ---

def load_users() -> list:
    try:
        docs = db.collection("users").stream()
        return [doc.to_dict() for doc in docs]
    except Exception as e:
        print(f"Error loading users: {e}")
        return []

def load_user_by_email(email: str) -> dict | None:
    try:
        docs = db.collection("users").where("email", "==", email).limit(1).stream()
        for doc in docs:
            return doc.to_dict()
        return None
    except Exception as e:
        print(f"Error loading user by email: {e}")
        return None

def save_user(data: dict) -> None:
    try:
        doc_id = str(data["id"])
        db.collection("users").document(doc_id).set(data)
    except Exception as e:
        print(f"Error saving user: {e}")

def update_user_password(email: str, new_password: str) -> dict | None:
    try:
        docs = db.collection("users").where("email", "==", email).stream()
        for doc in docs:
            db.collection("users").document(doc.id).update({"password": new_password})
            return doc.to_dict()
        return None
    except Exception as e:
        print(f"Error updating user password: {e}")
        return None

        # Append this to your app/services/data_store.py file

def fetch_artisan_profile_from_db(artisan_id: str) -> Optional[dict]:
    """
    Fetches raw artisan document map attributes directly from cloud Firestore collections.
    """
    try:
        doc_ref = db.collection("artisans").document(artisan_id).get()
        if doc_ref.exists:
            profile_data = doc_ref.to_dict()
            profile_data["artisan_id"] = artisan_id
            return profile_data
    except Exception as e:
        print(f"[DATABASE ERROR]: Failed to pull artisan profile: {e}")
    
    return None