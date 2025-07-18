#!/usr/bin/env python3
"""
Test script for recipe-relevant dad jokes
"""

def get_recipe_category(recipe_title, recipe_summary=""):
    """Test the recipe category detection function"""
    title_lower = recipe_title.lower()
    summary_lower = recipe_summary.lower() if recipe_summary else ""
    combined_text = title_lower + " " + summary_lower
    
    # Check for specific food categories
    if any(word in combined_text for word in ['pasta', 'spaghetti', 'noodle', 'penne', 'fettuccine', 'linguine']):
        return 'pasta'
    elif any(word in combined_text for word in ['chicken', 'poultry', 'breast', 'thigh', 'wing']):
        return 'chicken'
    elif any(word in combined_text for word in ['beef', 'steak', 'burger', 'meatball', 'roast']):
        return 'beef'
    elif any(word in combined_text for word in ['fish', 'salmon', 'tuna', 'cod', 'shrimp', 'seafood']):
        return 'fish'
    elif any(word in combined_text for word in ['dessert', 'cake', 'cookie', 'pie', 'ice cream', 'chocolate']):
        return 'dessert'
    elif any(word in combined_text for word in ['bread', 'toast', 'sandwich', 'bun', 'roll']):
        return 'bread'
    elif any(word in combined_text for word in ['cheese', 'cheddar', 'mozzarella', 'parmesan']):
        return 'cheese'
    elif any(word in combined_text for word in ['egg', 'omelette', 'scrambled']):
        return 'eggs'
    elif any(word in combined_text for word in ['mushroom', 'fungi']):
        return 'mushroom'
    elif any(word in combined_text for word in ['coffee', 'espresso', 'latte']):
        return 'coffee'
    elif any(word in combined_text for word in ['vegetarian', 'vegan', 'salad', 'vegetable', 'tofu']):
        return 'vegetarian'
    else:
        return 'general'

def test_recipe_categories():
    """Test various recipe categories"""
    test_cases = [
        ("Spaghetti Carbonara", "Classic Italian pasta dish"),
        ("Grilled Chicken Breast", "Healthy protein option"),
        ("Beef Burger", "Classic American dish"),
        ("Salmon Teriyaki", "Japanese fish dish"),
        ("Chocolate Cake", "Sweet dessert"),
        ("Cheese Pizza", "Italian favorite"),
        ("Scrambled Eggs", "Breakfast classic"),
        ("Mushroom Risotto", "Creamy rice dish"),
        ("Coffee Cake", "Morning treat"),
        ("Vegetable Salad", "Healthy option"),
        ("Random Recipe", "Unknown dish")
    ]
    
    print("🧪 Testing Recipe Category Detection...")
    print("=" * 50)
    
    for title, summary in test_cases:
        category = get_recipe_category(title, summary)
        print(f"🍳 Recipe: {title}")
        print(f"📝 Summary: {summary}")
        print(f"🏷️  Category: {category}")
        print("-" * 30)

if __name__ == "__main__":
    test_recipe_categories() 