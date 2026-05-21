import json

def save_data(filename, data):
    """Saves a Python list to a JSON file."""
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)

def load_data(filename):
    """Loads a JSON file and returns a Python list."""
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []
