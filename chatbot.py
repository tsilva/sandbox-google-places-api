# https://docs.anthropic.com/en/docs/build-with-claude/tool-use
# TODO: cache prompts
# TODO: add geocoding tool, tell to store geocode user's location and store in memory

from dotenv import load_dotenv
load_dotenv()

import os
import json
import anthropic

SYSTEM_MEMORY_MAX_SIZE = 5

system_memory = []

TOOL_SAVE_MEMORY = {
    "name" : "tool_save_memory",
    "description": "Used to store information the user requested to remember. Opt to call tool multiple times to store facts one by one. Memorized information will be used in system prompt.",
    "input_schema": {
        "type": "object",
        "properties": {
            "memory_data": {
                "type": "string",
                "description": "Summarized version of the information to remember, compressed to use the least tokens possible while preserving all relevant facts"
            }
        },
        "required": ["memory_data"]
    }
}
def tool_save_memory(memory_data: str):
    system_memory.append(memory_data)
    system_memory[:] = system_memory[:SYSTEM_MEMORY_MAX_SIZE]

TOOL_DELETE_MEMORY = {
    "name": "tool_delete_memory",
    "description": "Used to discard information that was previously stored in memory.",
    "input_schema": {
        "type": "object",
        "properties": {
            "memory_index": {
                "type": "integer",
                "description": "The index of the memory slot to discard. The system prompt enumerates all memories at all times, prefixed by their memory slot, this is what should be referenced."
            }
        },
        "required": ["memory_index"]
    }

}
def tool_delete_memory(memory_index: int):
    system_memory.pop(memory_index)

TOOL_PLACES_NEARBY = {
    "name": "tool_places_nearby",
    "description": "Search for places using Google Places API with various filtering options",
    "input_schema": {
        "type": "object",
        "properties": {
            "location": {
                "type": "object",
                "properties": {
                    "latitude": {"type": "number", "minimum": -90, "maximum": 90},
                    "longitude": {"type": "number", "minimum": -180, "maximum": 180}
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
            "keyword": {
                "type": "string",
                "description": "Term to match against all content indexed for this place"
            },
            "language": {
                "type": "string",
                "description": "The language code for the results (e.g., 'en', 'pt')"
            },
            "min_price": {
                "type": "integer",
                "minimum": 0,
                "maximum": 4,
                "description": "Minimum price level (0=most affordable, 4=most expensive)"
            },
            "max_price": {
                "type": "integer",
                "minimum": 0,
                "maximum": 4,
                "description": "Maximum price level (0=most affordable, 4=most expensive)"
            },
            "name": {
                "type": "string",
                "description": "Terms to match against place names"
            },
            "open_now": {
                "type": "boolean",
                "description": "Return only places that are currently open"
            },
            "rank_by": {
                "type": "string",
                "enum": ["prominence", "distance"],
                "description": "Order in which to rank results"
            },
            "place_type": {
                "type": "string",
                "description": "Type of place to search for",
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
            },
            "page_token": {
                "type": "string",
                "description": "Token for retrieving the next page of results"
            }
        },
        "required": ["location"]
    }
}
def tool_places_nearby(
    location: dict,
    radius: int = None,
    keyword: str = None,
    language: str = None,
    min_price: int = None,
    max_price: int = None,
    name: str = None,
    open_now: bool = False,
    rank_by: str = None,
    place_type: str = None,
    page_token: str = None
) -> dict:
    import googlemaps

    gmaps = googlemaps.Client(key=os.getenv('GOOGLE_MAPS_API_KEY'))
    
    # Convert location dict to tuple
    loc = (location['latitude'], location['longitude'])
    
    # Build params dict with only non-None values
    params = {
        'location': loc,
        'type': place_type,
        'keyword': keyword,
        'language': language,
        'min_price': min_price,
        'max_price': max_price,
        'name': name,
        'open_now': open_now,
        'rank_by': rank_by,
        'page_token': page_token
    }
    
    # Add radius if specified (required unless rank_by=distance)
    if radius is not None:
        params['radius'] = radius
    elif rank_by != 'distance':
        params['radius'] = 1000  # Default radius
        
    # Remove None values
    params = {k: v for k, v in params.items() if v is not None}
    
    # Make the API call
    places_result = gmaps.places_nearby(**params)
    
    print(json.dumps(places_result, indent=2))
    #results = places_result.get('results', [])

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

ALL_TOOLS = [
    TOOL_SAVE_MEMORY, 
    TOOL_DELETE_MEMORY, 
    TOOL_WEATHER, 
    TOOL_CALCULATOR, 
    TOOL_PLACES_NEARBY
]

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

    # Build the system prompt including all memories the user asked to remember
    system_prompt_memory_str = "\n".join([f"{index}: {value}" for index, value in enumerate(list(system_memory))]).strip()
    system_prompt_text = f"""
You are a digital assistant that can help with a variety of tasks. You can provide information about the weather, perform mathematical calculations, and search for places nearby. 
Never mention that you use tools or that you are a digital assistant. Just focus on solving the user's problem.
""".strip()
    if system_prompt_memory_str: system_prompt_text += f"\n\nHere are the memories the user asked you to remember:\n{system_prompt_memory_str}"

    # Send message to Claude
    message = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=1024,
        temperature=0.0, 
        tools=ALL_TOOLS,
        system=[{
            "type": "text", 
            "text": system_prompt_text, 
            "cache_control": {"type": "ephemeral"} # Prompt caching references the entire prompt - tools, system, and messages (in that order) up to and including the block designated with cache_control.
        }],
        messages=conversation_history
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