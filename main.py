"""
Recipe Details Finder - Main application entry point
"""

from src.api_client import SpoonacularClient
from src.data_parser import parse_recipe_search_results, parse_recipe_details, format_recipe_display

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
                # Search for recipes
                print("\nSearching for recipes...")
                search_results = client.search_recipes(query, number=5)
                recipes = parse_recipe_search_results(search_results)
                
                if not recipes:
                    print("\nNo recipes found. Please try a different search term.")
                    continue
                
                # Display search results
                print("\nFound Recipes:")
                print("=" * 50)
                for i, recipe in enumerate(recipes, 1):
                    print(f"{i}. {recipe['title']} (Ready in {recipe['ready_in_minutes']} minutes)")
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
                print("Please try again with a different search term.")
                
    except Exception as e:
        print(f"\nError: {str(e)}")
        if "API key" in str(e):
            print("Please make sure you have set up your SPOONACULAR_API_KEY in the .env file.")
        return 1
    
    return 0

if __name__ == "__main__":
    main() 