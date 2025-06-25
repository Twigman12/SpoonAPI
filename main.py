"""
Recipe Details Finder - Main application entry point
"""

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
    """Main function for recipe search and display."""
    try:
        # Initialize the client
        client = SpoonacularClient()
        print("\n=== Welcome to Recipe Search ===")
        print("Type 'quit' at any time to exit\n")
        
        while True:
            # Get search query
            query = input("Enter a recipe to search for: ").strip()
            if query.lower() == 'quit':
                print("\nThank you for using Recipe Search!")
                return 0
            
            if not query:
                print("Please enter a search term")
                continue
            
            try:
                # Get filters
                filters = get_filters()
                
                # Search for recipes
                print("\nSearching for recipes...")
                search_results = client.search_recipes(query, number=5, **filters)
                recipes = parse_recipe_search_results(search_results)
                
                if not recipes:
                    print("\nNo recipes found. Please try different search terms or filters.")
                    continue
                
                # Display search results
                print("\nFound Recipes:")
                print("=" * 50)
                for i, recipe in enumerate(recipes, 1):
                    print(f"{i}. {recipe['title']}")
                    print(f"   Ready in: {recipe['ready_in_minutes']} minutes")
                    if recipe.get('vegetarian'):
                        print("   • Vegetarian")
                    if recipe.get('vegan'):
                        print("   • Vegan")
                    if recipe.get('gluten_free'):
                        print("   • Gluten-free")
                print("\n0. Search for different recipes")
                
                # Get user selection
                selection = get_valid_number("\nEnter the number of the recipe you want to view: ", 0, len(recipes))
                
                if selection == 0:
                    continue
                
                # Get and display detailed recipe information
                selected_recipe = recipes[selection - 1]
                print(f"\nFetching details for {selected_recipe['title']}...")
                recipe_details = client.get_recipe_information(selected_recipe['id'])
                structured_recipe = parse_recipe_details(recipe_details)
                print(format_recipe_display(structured_recipe))
                
                # Ask if user wants to continue
                print("\nWhat would you like to do next?")
                print("1. Search for more recipes")
                print("2. Exit")
                
                choice = get_valid_number("Enter your choice (1-2): ", 1, 2)
                if choice == 2:
                    print("\nThank you for using Recipe Search!")
                    return 0
                
            except Exception as e:
                print(f"\nError while processing request: {str(e)}")
                print("Please try again with different search terms or filters.")
                
    except Exception as e:
        print(f"\nError: {str(e)}")
        if "API key" in str(e):
            print("Please make sure you have set up your SPOONACULAR_API_KEY in the .env file.")
        return 1
    
    return 0

if __name__ == "__main__":
    main() 