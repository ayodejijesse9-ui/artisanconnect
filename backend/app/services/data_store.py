import os
import firebase_admin
from firebase_admin import credentials, firestore
from dotenv import load_dotenv
from pydantic import BaseModel, Field

load_dotenv()

# Initialize Firebase
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
cred_path = os.path.join(BASE_DIR, "firebase-credentials.json")
cred = credentials.Certificate(cred_path)
firebase_admin.initialize_app(cred)

db = firestore.client()


def load_artisans() -> list:
    """Loads all artisans from Firestore."""
    try:
        docs = db.collection("artisans").stream()
        return [doc.to_dict() for doc in docs]
    except Exception as e:
        print(f"Error loading artisans: {e}")
        return []


def save_artisans(data: list) -> None:
    """Saves artisans to Firestore — overwrites entire collection."""
    try:
        for artisan in data:
            doc_id = str(artisan["id"])
            db.collection("artisans").document(doc_id).set(artisan)
    except Exception as e:
        print(f"Error saving artisans: {e}")


def load_bookings() -> list:
    """Loads all bookings from Firestore."""
    try:
        docs = db.collection("bookings").stream()
        return [doc.to_dict() for doc in docs]
    except Exception as e:
        print(f"Error loading bookings: {e}")
        return []


def save_bookings(data: list) -> None:
    """Saves bookings to Firestore."""
    try:
        for booking in data:
            doc_id = str(booking["booking_id"])
            db.collection("bookings").document(doc_id).set(booking)
    except Exception as e:
        print(f"Error saving bookings: {e}")


def load_customers() -> list:
    """Loads all customers from Firestore."""
    try:
        docs = db.collection("customers").stream()
        return [doc.to_dict() for doc in docs]
    except Exception as e:
        print(f"Error loading customers: {e}")
        return []


def save_customers(data: list) -> None:
    """Saves customers to Firestore."""
    try:
        for customer in data:
            doc_id = str(customer["id"])
            db.collection("customers").document(doc_id).set(customer)
    except Exception as e:
        print(f"Error saving customers: {e}")

def load_users() -> list:
    try:
        docs = db.collection("users").stream()
        return [doc.to_dict() for doc in docs]
    except Exception as e:
        print(f"Error loading users: {e}")
        return []


def save_user(data: dict) -> None:
    """Saves a single user to Firestore."""
    try:
        doc_id = str(data["id"])
        db.collection("users").document(doc_id).set(data)
    except Exception as e:
        print(f"Error saving user: {e}")

def load_user_by_email(email: str) -> dict | None:
    try:
        docs = db.collection("users").where("email", "==", email).stream()
        for doc in docs:
            return doc.to_dict()
        return None
    except Exception as e:
        print(f"Error loading user by email: {e}")
        return None
        
def update_user_password(email: str, new_password: str) -> dict | None:
    try:
        docs = db.collection("users").where("email", "==", email).stream()
        for doc in docs:
            doc_id = doc.id
            db.collection("users").document(doc_id).update({"password": new_password})
            return doc.to_dict()
        return None
    except Exception as e:
        print(f"Error updating user password: {e}")
        return None
    
def update_artisan_verified(artisan_id: int) -> bool:
    try:
        docs = db.collection("artisans").where("id", "==", artisan_id).stream()
        for doc in docs:
            db.collection("artisans").document(doc.id).update({"verified": True})
            return True
        return False
    except Exception as e:
        print(f"Error updating artisan verification: {e}")
        return False
    
