"""
Recipe Details Finder - Main application entry point

This module serves as the main entry point for the Recipe Details Finder application.
It handles user interaction, recipe searching, and displaying results in a user-friendly format.

Flow:
1. Initialize API client
2. Get search query from user
3. Search for recipes
4. Display results and get user selection
5. Show detailed recipe information
6. Repeat or quit
"""

import sys
from src.api_client import SpoonacularClient
from src.data_parser import parse_recipe_search_results, parse_recipe_details, format_recipe_display
from typing import List, Optional

def get_valid_number(prompt: str, min_val: int, max_val: int) -> int:
    """Get a valid number input from the user within the specified range."""
    while True:
        try:
            value = int(input(prompt))
            if min_val <= value <= max_val:
                return value
            print(f"Please enter a number between {min_val} and {max_val}")
        except ValueError:
            print("Please enter a valid number")

def get_filters() -> dict:
    """Get search filters from user input."""
    filters = {}
    
    print("\nWould you like to add any filters? (Enter 'no' to skip)")
    print("Available filters:")
    print("1. Dietary restrictions")
    print("2. Cooking time/difficulty")
    print("3. Calorie range")
    print("0. No filters")
    
    choice = get_valid_number("Enter your choice (0-3): ", 0, 3)
    
    if choice == 0:
        return filters
    
    if choice == 1:
        # Dietary restrictions
        print("\nDietary Options:")
        print("Available diets:")
        for i, diet in enumerate(SpoonacularClient.VALID_DIETS, 1):
            print(f"{i}. {diet.title()}")
        print("0. Skip diet")
        
        diet_choice = get_valid_number("Choose a diet (0 to skip): ", 0, len(SpoonacularClient.VALID_DIETS))
        if diet_choice > 0:
            filters["diet"] = SpoonacularClient.VALID_DIETS[diet_choice - 1]
        
        print("\nIntolerances (enter numbers separated by spaces, 0 to skip):")
        for i, intolerance in enumerate(SpoonacularClient.VALID_INTOLERANCES, 1):
            print(f"{i}. {intolerance.title()}")
        
        intol_input = input("Choose intolerances: ").strip()
        if intol_input != "0":
            try:
                intol_choices = [int(x) for x in intol_input.split()]
                valid_choices = [x for x in intol_choices if 1 <= x <= len(SpoonacularClient.VALID_INTOLERANCES)]
                if valid_choices:
                    filters["intolerances"] = [SpoonacularClient.VALID_INTOLERANCES[i - 1] for i in valid_choices]
            except ValueError:
                print("Invalid input, skipping intolerances")
    
    elif choice == 2:
        # Cooking time/difficulty
        print("\nDifficulty Levels:")
        print("1. Easy (up to 30 minutes)")
        print("2. Medium (up to 60 minutes)")
        print("3. Hard (up to 120 minutes)")
        print("4. Custom time")
        print("0. Skip")
        
        time_choice = get_valid_number("Choose difficulty/time option (0-4): ", 0, 4)
        if time_choice in [1, 2, 3]:
            filters["difficulty"] = list(SpoonacularClient.DIFFICULTY_LEVELS.keys())[time_choice - 1]
        elif time_choice == 4:
            max_time = get_valid_number("Enter maximum cooking time in minutes: ", 1, 300)
            filters["max_ready_time"] = max_time
    
    elif choice == 3:
        # Calorie range
        print("\nCalorie Range (press Enter to skip):")
        try:
            min_cal = input("Minimum calories per serving: ").strip()
            if min_cal:
                filters["min_calories"] = int(min_cal)
            
            max_cal = input("Maximum calories per serving: ").strip()
            if max_cal:
                filters["max_calories"] = int(max_cal)
        except ValueError:
            print("Invalid calorie input, skipping calorie filter")
    
    return filters

def main():
    """
    Main application function that orchestrates the recipe search and display process.
    
    The function implements a continuous loop that:
    1. Takes user input for recipe search
    2. Retrieves recipes from Spoonacular API
    3. Displays results and gets user selection
    4. Shows detailed recipe information
    5. Allows for new searches or exit
    
    Error handling is implemented at multiple levels:
    - API client initialization (checks for API key)
    - Recipe search (handles API errors)
    - User input validation (handles invalid selections)
    """
    try:
        # Initialize the API client - This will validate the API key exists
        client = SpoonacularClient()
        
        # Main application loop - continues until user types 'quit'
        query = input("\nEnter a recipe to search for (or 'quit' to exit): ").strip()
        
        while query.lower() != 'quit':
            try:
                # Search for recipes using the API client
                print("\nSearching for recipes...")
                search_results = client.search_recipes(query)
                recipes = parse_recipe_search_results(search_results)
                
                # Handle case where no recipes are found
                if not recipes:
                    print("\nNo recipes found. Please try a different search term.")
                    query = input("\nEnter a recipe to search for (or 'quit' to exit): ").strip()
                    continue
                
                # Display numbered list of found recipes
                print("\nFound the following recipes:")
                for i, recipe in enumerate(recipes, 1):
                    print(f"{i}. {recipe['title']} ({recipe['ready_in_minutes']} minutes)")
                
                # Get and validate user selection
                while True:
                    try:
                        selection = int(input("\nEnter the number of the recipe you want to view (0 to search again): "))
                        if 0 <= selection <= len(recipes):
                            break
                        print("Invalid selection. Please try again.")
                    except ValueError:
                        print("Please enter a valid number.")
                
                # Handle user choosing to search again
                if selection == 0:
                    query = input("\nEnter a recipe to search for (or 'quit' to exit): ").strip()
                    continue
                
                # Get and display detailed recipe information
                selected_recipe = recipes[selection - 1]
                # Make a separate API call to get full recipe details
                recipe_details = client.get_recipe_information(selected_recipe['id'])
                # Parse the detailed information into a structured format
                structured_recipe = parse_recipe_details(recipe_details)
                
                # Display the formatted recipe
                print(format_recipe_display(structured_recipe))
                
                # Prompt for next action
                query = input("\nEnter a recipe to search for (or 'quit' to exit): ").strip()
                
            except Exception as e:
                # Handle any errors during recipe search and display
                print(f"\nError while processing request: {str(e)}")
                query = input("\nEnter a recipe to search for (or 'quit' to exit): ").strip()
    
    except ValueError as e:
        # Handle API key configuration errors
        print(f"Error: {str(e)}")
        print("Please make sure you have set up your SPOONACULAR_API_KEY in the .env file.")
        sys.exit(1)
    except Exception as e:
        # Handle any unexpected errors
        print(f"An unexpected error occurred: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 