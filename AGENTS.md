# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a sandbox environment for experimenting with Google Places API using Python and Anthropic's Claude API. The project contains two main components:

1. **main.py** - Simple example script demonstrating direct Google Places API usage
2. **chatbot.py** - Interactive chatbot with tool calling capabilities, memory management, and integration with both Google Places API and Anthropic's Claude API

## Environment Setup

The project uses Conda for dependency management:

```bash
# Create environment
conda env create -f environment.yml

# Activate environment
conda activate sandbox-google-places-api
```

Environment file: `environment.yml`
- Python 3.9
- Key dependencies: python-dotenv, anthropic, googlemaps==4.10.0

## Configuration

Required environment variables in `.env`:
- `GOOGLE_MAPS_API_KEY` - Google Maps API key from Google Cloud Console
- `ANTHROPIC_API_KEY` - Anthropic API key for Claude

Use `.env.example` as a template.

## Running the Code

Simple example:
```bash
python main.py
```

Interactive chatbot:
```bash
python chatbot.py
```

The chatbot supports conversational interaction and tool calling. Type 'quit' to exit.

## Architecture

### Chatbot Tool System (chatbot.py)

The chatbot implements Anthropic's tool calling pattern with several custom tools:

**Memory Tools:**
- `tool_save_memory` - Stores user information with optional index-based updates. Limited to `SYSTEM_MEMORY_MAX_SIZE` (5) entries
- `tool_delete_memory` - Removes stored memories by index

**Location Tools:**
- `tool_geocode` - Converts addresses to lat/lng coordinates using Google Geocoding API
- `tool_places_nearby` - Searches for places using Google Places API Nearby Search with extensive filtering (radius, keywords, price level, type, etc.)
- `tool_place_details` - Retrieves detailed information about a specific place using its place_id

**Other Tools:**
- `tool_weather` - Mock weather tool (returns hardcoded data)
- `tool_calculator` - Basic arithmetic operations

### Tool Calling Pattern

The chatbot uses a conversation loop:
1. User input is added to `conversation_history`
2. Messages sent to Claude with tools and system prompt (includes memory context)
3. Claude's response processed for tool calls
4. Tool results added back to history
5. Loop continues until user types 'quit'

### System Prompt Behavior

The system prompt dynamically includes enumerated memories and instructs the chatbot to:
- Automatically geocode locations mentioned by users
- Save geocoded coordinates in memory
- Use saved coordinates for subsequent nearby searches

### Prompt Caching

The system uses Anthropic's prompt caching with `cache_control: {"type": "ephemeral"}` on the system prompt to optimize API usage.

## Key Implementation Details

- All tool definitions use JSON schema format in `input_schema`
- Tool functions are called dynamically via `globals()[func_name](**func_args)`
- Content blocks from Claude's responses are converted to dicts using `content_block_to_dict()`
- Google Maps client is instantiated per tool call (not globally cached)
- Tool results are printed to console for debugging

## README.md Maintenance

README.md must be kept up to date with any significant project changes.
