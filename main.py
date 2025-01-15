import os
import googlemaps
from dotenv import load_dotenv

def main():
    # Load environment variables
    load_dotenv()
    
    # Initialize Google Maps client
    gmaps = googlemaps.Client(key=os.getenv('GOOGLE_MAPS_API_KEY'))
    
    # Example location (New York City coordinates)
    location = (40.7128, -74.0060)
    
    # Search for nearby restaurants
    places_result = gmaps.places_nearby(
        location=location,
        radius=1000,  # Search within 1000 meters
        type='restaurant'
    )
    
    # Print results
    for place in places_result.get('results', []):
        print(f"Name: {place['name']}")
        print(f"Rating: {place.get('rating', 'N/A')}")
        print(f"Address: {place.get('vicinity', 'N/A')}")
        print("-" * 50)

if __name__ == "__main__":
    main()
