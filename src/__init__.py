"""
Recipe Details Finder Package

This package provides functionality to search and display recipes using the Spoonacular API.
It consists of three main components:

1. API Client (api_client.py):
   - Handles all communication with the Spoonacular API
   - Manages API key and authentication
   - Provides methods for searching recipes and getting details

2. Data Parser (data_parser.py):
   - Parses API responses into structured formats
   - Handles complex nested JSON data
   - Formats recipe information for display

3. Main Application (main.py):
   - Provides the command-line interface
   - Orchestrates the flow between user input and API calls
   - Displays formatted results to the user

Usage:
    from src.api_client import SpoonacularClient
    from src.data_parser import parse_recipe_search_results, parse_recipe_details

Version and maintenance information
"""

__version__ = "0.1.0"
__author__ = "Recipe Details Finder Team"
__description__ = "A Python application for searching and displaying recipes using the Spoonacular API" 