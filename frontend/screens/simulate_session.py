import random
import json

def add_random_id_to_json(json_data):
    """
    Adds a 10-digit random numeric ID field to the JSON data at the top level.

    Args:
        json_data: The JSON data (either as dict or JSON string)

    Returns:
        Modified JSON with added 'random_id' field
    """
    # If input is string, parse to dict first
    if isinstance(json_data, str):
        data = json.loads(json_data)
    else:
        data = json_data.copy()

    # Generate 10-digit random number (leading zeros possible)
    random_id = str(random.randint(0, 9999999999)).zfill(10)

    # Add the field at top level
    data['random_id'] = random_id

    return data
