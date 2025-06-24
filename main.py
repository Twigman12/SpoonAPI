"""
Recipe Details Finder - Main application entry point
"""

import sys
from src.api_client import SpoonacularClient
from src.data_parser import parse_recipe_search_results, parse_recipe_details, format_recipe_display

def main():
    """Main application function."""
    try:
        # Initialize the API client
        client = SpoonacularClient()
        
        # Get search query from user
        query = input("\nEnter a recipe to search for (or 'quit' to exit): ").strip()
        
        while query.lower() != 'quit':
            try:
                # Search for recipes
                print("\nSearching for recipes...")
                search_results = client.search_recipes(query)
                recipes = parse_recipe_search_results(search_results)
                
                if not recipes:
                    print("\nNo recipes found. Please try a different search term.")
                    query = input("\nEnter a recipe to search for (or 'quit' to exit): ").strip()
                    continue
                
                # Display search results
                print("\nFound the following recipes:")
                for i, recipe in enumerate(recipes, 1):
                    print(f"{i}. {recipe['title']} ({recipe['ready_in_minutes']} minutes)")
                
                # Get user selection
                while True:
                    try:
                        selection = int(input("\nEnter the number of the recipe you want to view (0 to search again): "))
                        if 0 <= selection <= len(recipes):
                            break
                        print("Invalid selection. Please try again.")
                    except ValueError:
                        print("Please enter a valid number.")
                
                if selection == 0:
                    query = input("\nEnter a recipe to search for (or 'quit' to exit): ").strip()
                    continue
                
                # Get and display detailed recipe information
                selected_recipe = recipes[selection - 1]
                recipe_details = client.get_recipe_information(selected_recipe['id'])
                structured_recipe = parse_recipe_details(recipe_details)
                
                # Display formatted recipe
                print(format_recipe_display(structured_recipe))
                
                # Ask for next action
                query = input("\nEnter a recipe to search for (or 'quit' to exit): ").strip()
                
            except Exception as e:
                print(f"\nError while processing request: {str(e)}")
                query = input("\nEnter a recipe to search for (or 'quit' to exit): ").strip()
    
    except ValueError as e:
        print(f"Error: {str(e)}")
        print("Please make sure you have set up your SPOONACULAR_API_KEY in the .env file.")
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 