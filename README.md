# sandbox-google-places

This repository contains sample code to experiment with Google Places API using Python.

## Setup

1. Install Conda if you haven't already
2. Create the environment:
   ```bash
   conda env create -f environment.yml
   ```
3. Activate the environment:
   ```bash
   conda activate google-places
   ```
4. Get a Google Maps API key from the Google Cloud Console
5. Copy the `.env.example` file to `.env` and add your API key
6. Run the sample script:
   ```bash
   python search_restaurants.py
   ```

## Features

- Search for nearby restaurants within a specified radius
- Display basic information about each restaurant (name, rating, address)
