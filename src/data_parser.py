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