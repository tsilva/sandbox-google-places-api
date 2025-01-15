# https://docs.anthropic.com/en/docs/build-with-claude/tool-use
# TODO: cache prompts

from dotenv import load_dotenv
load_dotenv()

import os
import json
import anthropic

SYSTEM_PROMPT = """
You are a digital assistant that can help with a variety of tasks. You can provide information about the weather, perform mathematical calculations, and search for places nearby. 
The user that is interacting with you is located in Porto, Portugal.
""".strip()

TOOL_PLACES_NEARBY = {
    "name": "tool_places_nearby",
    "description": "Search for places of a specific type within a given radius of a location using Google Places API",
    "input_schema": {
        "type": "object",
        "properties": {
            "location": {
                "type": "object",
                "properties": {
                    "latitude": {
                        "type": "number",
                        "description": "Latitude coordinate of the center point",
                        "minimum": -90,
                        "maximum": 90
                    },
                    "longitude": {
                        "type": "number",
                        "description": "Longitude coordinate of the center point",
                        "minimum": -180,
                        "maximum": 180
                    }
                },
                "required": ["latitude", "longitude"],
                "description": "Geographic coordinates of the search center point"
            },
            "radius": {
                "type": "integer",
                "description": "Search radius in meters",
                "minimum": 1,
                "maximum": 50000
            },
            "place_type": {
                "type": "string",
                "description": "Type of place to search for (e.g., restaurant, cafe, park)",
                "enum": [
                    "accounting", "airport", "amusement_park", "aquarium", "art_gallery", 
                    "atm", "bakery", "bank", "bar", "beauty_salon", "bicycle_store", 
                    "book_store", "bowling_alley", "bus_station", "cafe", "campground",
                    "car_dealer", "car_rental", "car_repair", "car_wash", "casino",
                    "cemetery", "church", "city_hall", "clothing_store", "convenience_store",
                    "courthouse", "dentist", "department_store", "doctor", "drugstore",
                    "electrician", "electronics_store", "embassy", "fire_station", 
                    "florist", "funeral_home", "furniture_store", "gas_station", 
                    "gym", "hair_care", "hardware_store", "hindu_temple", "home_goods_store",
                    "hospital", "insurance_agency", "jewelry_store", "laundry", 
                    "lawyer", "library", "light_rail_station", "liquor_store", 
                    "local_government_office", "locksmith", "lodging", "meal_delivery",
                    "meal_takeaway", "mosque", "movie_rental", "movie_theater", 
                    "moving_company", "museum", "night_club", "painter", "park",
                    "parking", "pet_store", "pharmacy", "physiotherapist", "plumber",
                    "police", "post_office", "primary_school", "real_estate_agency",
                    "restaurant", "roofing_contractor", "rv_park", "school", 
                    "secondary_school", "shoe_store", "shopping_mall", "spa", 
                    "stadium", "storage", "store", "subway_station", "supermarket",
                    "synagogue", "taxi_stand", "tourist_attraction", "train_station",
                    "transit_station", "travel_agency", "university", "veterinary_care",
                    "zoo"
                ]
            }
        },
        "required": ["location", "radius", "place_type"]
    }
}
def tool_places_nearby(location: dict, radius: int, place_type: str) -> dict:
    import googlemaps

    # Initialize Google Maps client
    gmaps = googlemaps.Client(key=os.getenv('GOOGLE_MAPS_API_KEY'))

    # Example location (New York City coordinates)
    #location = (40.7128, -74.0060)

    # Search for nearby restaurants
    places_result = gmaps.places_nearby(
        location=location,
        radius=radius,
        type=place_type
    )
    
    return places_result.get('results', [])

TOOL_WEATHER = {
    "name": "tool_weather",
    "description": "Get detailed weather forecast for a specific location and date range",
    "input_schema": {
        "type": "object",
        "properties": {
            "location": {
                "type": "object",
                "properties": {
                    "city": {"type": "string", "description": "City name"},
                    "country": {"type": "string", "description": "Country name"},
                    "coordinates": {
                        "type": "object",
                        "properties": {
                            "latitude": {"type": "number"},
                            "longitude": {"type": "number"}
                        }
                    }
                },
                "required": ["city"]
            },
            "date_range": {
                "type": "object",
                "properties": {
                    "start_date": {"type": "string", "format": "date"},
                    "end_date": {"type": "string", "format": "date"}
                },
                "required": ["start_date"]
            }
        },
        "required": ["location", "date_range"]
    }
}
def tool_weather(location: dict, date_range: dict) -> dict:
    return {
        "location": location["city"],
        "date": date_range["start_date"],
        "forecast": {
            "temperature": 22,
            "conditions": "Sunny",
            "confidence": 0.95
        }
    }

TOOL_CALCULATOR = {
    "name": "tool_calculator",
    "description": "Perform mathematical operations with error handling and precision tracking",
    "input_schema": {
        "type": "object",
        "properties": {
            "first_number": {
                "type": "number",
                "description": "First operand for the calculation"
            },
            "second_number": {
                "type": "number",
                "description": "Second operand for the calculation"
            },
            "operation": {
                "type": "string",
                "description": "Mathematical operation to perform",
                "enum": ["add", "subtract", "multiply", "divide"]
            }
        },
        "required": ["first_number", "second_number", "operation"]
    }
}
def tool_calculator(first_number, second_number, operation: str):
    x, y = first_number, second_number
    
    result = None
    if operation == "add":
        result = x + y
    elif operation == "subtract":
        result = x - y
    elif operation == "multiply":
        result = x * y
    elif operation == "divide":
        result = x / y if y != 0 else None
    
    return result

ALL_TOOLS = [TOOL_WEATHER, TOOL_CALCULATOR, TOOL_PLACES_NEARBY]

def add_to_history(message):
    global conversation_history
    print(json.dumps(message, indent=2))
    conversation_history.append(message)

def content_block_to_dict(content):
    if content.type == "text":
        return {
            "type": "text",
            "text": content.text
        }
    elif content.type == "tool_use":
        return {
            "type": "tool_use",
            "id": content.id,
            "name": content.name,
            "input": content.input
        }

print("ChatBot initialized. Type 'quit' to exit.")

client = anthropic.Anthropic()
conversation_history = []

while True:
    # In case the last message was from the assistant, prompt the user
    last_message = conversation_history[-1] if conversation_history else None
    if last_message is None or last_message["role"] == "assistant":
        user_input = input("You: ")
        if user_input.lower() == 'quit': break
        add_to_history({"role": "user", "content": user_input})

    # Send message to Claude
    message = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=1024,
        temperature=0.0, 
        system=[{
            "type": "text", 
            "text": SYSTEM_PROMPT, 
            "cache_control": {"type": "ephemeral"}
        }],
        messages=conversation_history,
        tools=ALL_TOOLS
    )

    # Add response to history
    add_to_history({
        "role": "assistant",
        "content": [content_block_to_dict(x) for x in message.content]
    })
    
    # Process tool calls
    for content in message.content:
        if not content.type == "tool_use": continue

        tool_id = content.id
        func_name = content.name
        func_args = content.input
        print(f"Calling {func_name}({json.dumps(func_args, indent=2)})")
        func = globals()[func_name]
        result = func(**func_args)

        add_to_history({
            "role": "user",
            "content": [
                {
                    "type": "tool_result",
                    "tool_use_id": tool_id,
                    "content": str(result)
                }
            ]
        })