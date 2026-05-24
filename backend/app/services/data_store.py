import json
import os

# Always resolve paths relative to this file's location
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))


def save_data(filename, data):
    """Saves a Python list to a JSON file."""
    filepath = os.path.join(BASE_DIR, filename)
    with open(filepath, "w") as f:
        json.dump(data, f, indent=4)


def load_data(filename):
    """Loads a JSON file and returns a Python list."""
    filepath = os.path.join(BASE_DIR, filename)
    try:
        with open(filepath, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_artisans(data):
    save_data("artisans.json", data)

def load_artisans():
    return load_data("artisans.json")

def save_bookings(data):
    save_data("bookings.json", data)

def load_bookings():
    return load_data("bookings.json")