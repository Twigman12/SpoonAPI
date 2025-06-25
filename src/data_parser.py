"""
Parser for Spoonacular API response data.
"""

from typing import Dict, List, Any

def parse_recipe_search_results(search_results: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Parse recipe search results into a simplified format.
    
    Args:
        search_results (Dict[str, Any]): Raw search results from the API
        
    Returns:
        List[Dict[str, Any]]: List of simplified recipe information
    """
    recipes = []
    
    for result in search_results.get("results", []):
        recipe = {
            "id": result.get("id"),
            "title": result.get("title"),
            "image": result.get("image"),
            "ready_in_minutes": result.get("readyInMinutes"),
            "servings": result.get("servings")
        }
        recipes.append(recipe)
    
    return recipes

def parse_recipe_details(recipe_details: Dict[str, Any]) -> Dict[str, Any]:
    """
    Parse detailed recipe information into a structured format.
    
    Args:
        recipe_details (Dict[str, Any]): Raw recipe details from the API
        
    Returns:
        Dict[str, Any]: Structured recipe information
    """
    # Parse ingredients
    ingredients = []
    for ingredient in recipe_details.get("extendedIngredients", []):
        ingredients.append({
            "name": ingredient.get("name", ""),
            "amount": ingredient.get("amount", 0),
            "unit": ingredient.get("unit", ""),
            "original": ingredient.get("original", "")
        })
    
    # Parse instructions
    instructions = []
    for instruction_set in recipe_details.get("analyzedInstructions", []):
        for step in instruction_set.get("steps", []):
            instructions.append({
                "number": step.get("number", 0),
                "step": step.get("step", "")
            })
    
    # Create structured recipe data
    structured_recipe = {
        "id": recipe_details.get("id"),
        "title": recipe_details.get("title"),
        "ready_in_minutes": recipe_details.get("readyInMinutes"),
        "servings": recipe_details.get("servings"),
        "image": recipe_details.get("image"),
        "summary": recipe_details.get("summary"),
        "ingredients": ingredients,
        "instructions": instructions,
        "vegetarian": recipe_details.get("vegetarian", False),
        "vegan": recipe_details.get("vegan", False),
        "gluten_free": recipe_details.get("glutenFree", False),
        "dairy_free": recipe_details.get("dairyFree", False)
    }
    
    return structured_recipe

def parse_nutrition_data(nutrition_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Parse nutritional information into a structured format.
    
    Args:
        nutrition_data (Dict[str, Any]): Raw nutrition data from the API
        
    Returns:
        Dict[str, Any]: Structured nutrition information
    """
    # Parse nutrients
    nutrients = {}
    for nutrient in nutrition_data.get("nutrients", []):
        nutrients[nutrient.get("name", "").lower()] = {
            "amount": nutrient.get("amount", 0),
            "unit": nutrient.get("unit", ""),
            "percent_daily_needs": nutrient.get("percentOfDailyNeeds", 0)
        }
    
    # Parse caloric breakdown
    cals = nutrition_data.get("caloricBreakdown", {})
    caloric_breakdown = {
        "percent_protein": cals.get("percentProtein", 0),
        "percent_fat": cals.get("percentFat", 0),
        "percent_carbs": cals.get("percentCarbs", 0)
    }
    
    return {
        "calories": nutrients.get("calories", {}).get("amount", 0),
        "protein": nutrients.get("protein", {}).get("amount", 0),
        "fat": nutrients.get("fat", {}).get("amount", 0),
        "carbohydrates": nutrients.get("carbohydrates", {}).get("amount", 0),
        "nutrients": nutrients,
        "caloric_breakdown": caloric_breakdown
    }

def parse_wine_pairing(wine_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Parse wine pairing information into a structured format.
    
    Args:
        wine_data (Dict[str, Any]): Raw wine pairing data from the API
        
    Returns:
        Dict[str, Any]: Structured wine pairing information
    """
    paired_wines = wine_data.get("pairedWines", [])
    pairings = []
    
    for wine in wine_data.get("productMatches", []):
        pairings.append({
            "title": wine.get("title", ""),
            "description": wine.get("description", ""),
            "price": wine.get("price", ""),
            "average_rating": wine.get("averageRating", 0),
            "rating_count": wine.get("ratingCount", 0),
            "score": wine.get("score", 0)
        })
    
    return {
        "paired_wines": paired_wines,
        "pairing_text": wine_data.get("pairingText", ""),
        "recommended_wines": pairings
    }

def format_recipe_display(recipe: Dict[str, Any]) -> str:
    """
    Format recipe information for display.
    
    Args:
        recipe (Dict[str, Any]): Structured recipe information
        
    Returns:
        str: Formatted recipe string for display
    """
    # Format basic information
    display = [
        f"\n{'='*50}",
        f"\n{recipe['title'].upper()}\n",
        f"Ready in {recipe['ready_in_minutes']} minutes | Serves {recipe['servings']}\n",
        f"{'='*50}\n"
    ]
    
    # Add dietary information
    diet_info = []
    if recipe["vegetarian"]:
        diet_info.append("Vegetarian")
    if recipe["vegan"]:
        diet_info.append("Vegan")
    if recipe["gluten_free"]:
        diet_info.append("Gluten-free")
    if recipe["dairy_free"]:
        diet_info.append("Dairy-free")
    
    if diet_info:
        display.append(f"Dietary Info: {', '.join(diet_info)}\n")
    
    # Add ingredients
    display.append("\nINGREDIENTS:\n")
    for ingredient in recipe["ingredients"]:
        display.append(f"• {ingredient['original']}")
    
    # Add instructions
    display.append("\nINSTRUCTIONS:\n")
    for instruction in recipe["instructions"]:
        display.append(f"{instruction['number']}. {instruction['step']}")
    
    return "\n".join(display)

def format_nutrition_display(nutrition: Dict[str, Any]) -> str:
    """
    Format nutrition information for display.
    
    Args:
        nutrition (Dict[str, Any]): Structured nutrition information
        
    Returns:
        str: Formatted nutrition string for display
    """
    display = [
        "\nNUTRITIONAL INFORMATION:",
        f"Calories: {nutrition['calories']} kcal",
        "\nMacronutrients:",
        f"• Protein: {nutrition['protein']}g",
        f"• Fat: {nutrition['fat']}g",
        f"• Carbohydrates: {nutrition['carbohydrates']}g",
        "\nCaloric Breakdown:",
        f"• Protein: {nutrition['caloric_breakdown']['percent_protein']}%",
        f"• Fat: {nutrition['caloric_breakdown']['percent_fat']}%",
        f"• Carbs: {nutrition['caloric_breakdown']['percent_carbs']}%"
    ]
    
    # Add important vitamins and minerals
    vitamins = ["vitamin a", "vitamin c", "vitamin d", "vitamin b12"]
    minerals = ["iron", "calcium", "potassium", "magnesium"]
    
    display.append("\nVitamins & Minerals:")
    for nutrient in nutrition["nutrients"]:
        if nutrient in vitamins + minerals:
            info = nutrition["nutrients"][nutrient]
            display.append(f"• {nutrient.title()}: {info['amount']}{info['unit']} ({info['percent_daily_needs']}% DV)")
    
    return "\n".join(display)

def format_wine_pairing_display(pairing: Dict[str, Any]) -> str:
    """
    Format wine pairing information for display.
    
    Args:
        pairing (Dict[str, Any]): Structured wine pairing information
        
    Returns:
        str: Formatted wine pairing string for display
    """
    display = [
        "\nWINE PAIRING SUGGESTIONS:",
        "\nRecommended Wine Types:"
    ]
    
    # Add paired wines
    for wine in pairing["paired_wines"]:
        display.append(f"• {wine.title()}")
    
    # Add pairing explanation
    if pairing["pairing_text"]:
        display.extend(["\nPairing Notes:", pairing["pairing_text"]])
    
    # Add specific wine recommendations
    if pairing["recommended_wines"]:
        display.append("\nSpecific Wine Recommendations:")
        for wine in pairing["recommended_wines"]:
            display.extend([
                f"\n• {wine['title']}",
                f"  Price: {wine['price']}",
                f"  Rating: {wine['average_rating']}/5 ({wine['rating_count']} reviews)",
                f"  {wine['description']}"
            ])
    
    return "\n".join(display) 