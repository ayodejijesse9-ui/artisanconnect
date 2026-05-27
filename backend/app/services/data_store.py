import os
import firebase_admin
from firebase_admin import credentials, firestore
from dotenv import load_dotenv

load_dotenv()

# Initialize Firebase
cred_path = os.getenv("FIREBASE_CREDENTIALS")
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