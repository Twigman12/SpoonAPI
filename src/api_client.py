"""
Spoonacular API client for recipe search and information retrieval.
"""

import os
import requests
from typing import Dict, Optional, Any, List
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class SpoonacularClient:
    """Client for interacting with the Spoonacular API."""
    
    BASE_URL = "https://api.spoonacular.com"
    
    # Valid diet options from Spoonacular API
    VALID_DIETS = [
        "gluten free", "ketogenic", "vegetarian", "lacto-vegetarian",
        "ovo-vegetarian", "vegan", "pescetarian", "paleo", "primal", "low fodmap", "whole30"
    ]
    
    # Valid intolerances from Spoonacular API
    VALID_INTOLERANCES = [
        "dairy", "egg", "gluten", "grain", "peanut", "seafood",
        "sesame", "shellfish", "soy", "sulfite", "tree nut", "wheat"
    ]
    
    # Difficulty levels mapped to max preparation minutes
    DIFFICULTY_LEVELS = {
        "easy": 30,
        "medium": 60,
        "hard": 120
    }
    
    def __init__(self):
        """Initialize the Spoonacular API client."""
        self.api_key = os.getenv("SPOONACULAR_API_KEY")
        if not self.api_key:
            raise ValueError("Spoonacular API key not found in environment variables")
    
    def _make_request(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Make a request to the Spoonacular API.
        
        Args:
            endpoint (str): API endpoint to call
            params (Dict[str, Any], optional): Query parameters for the request
            
        Returns:
            Dict[str, Any]: JSON response from the API
            
        Raises:
            requests.exceptions.RequestException: If the API request fails
        """
        if params is None:
            params = {}
        
        # Add API key to parameters
        params["apiKey"] = self.api_key
        
        # Make the request
        response = requests.get(f"{self.BASE_URL}{endpoint}", params=params)
        response.raise_for_status()
        
        return response.json()
    
    def search_recipes(self, 
                      query: str,
                      number: int = 5,
                      diet: Optional[str] = None,
                      intolerances: Optional[List[str]] = None,
                      max_ready_time: Optional[int] = None,
                      difficulty: Optional[str] = None,
                      min_calories: Optional[int] = None,
                      max_calories: Optional[int] = None) -> Dict[str, Any]:
        """
        Search for recipes with advanced filtering options.
        
        Args:
            query (str): Search query
            number (int): Number of results to return
            diet (str, optional): Specific diet (e.g., "vegetarian", "vegan")
            intolerances (List[str], optional): List of intolerances
            max_ready_time (int, optional): Maximum total minutes for recipe
            difficulty (str, optional): Recipe difficulty ("easy", "medium", "hard")
            min_calories (int, optional): Minimum calories per serving
            max_calories (int, optional): Maximum calories per serving
            
        Returns:
            Dict[str, Any]: Search results
            
        Raises:
            ValueError: If invalid diet, intolerances, or difficulty level provided
        """
        # Validate diet
        if diet and diet.lower() not in self.VALID_DIETS:
            raise ValueError(f"Invalid diet. Valid options are: {', '.join(self.VALID_DIETS)}")
        
        # Validate intolerances
        if intolerances:
            invalid_intolerances = [i for i in intolerances if i.lower() not in self.VALID_INTOLERANCES]
            if invalid_intolerances:
                raise ValueError(f"Invalid intolerances: {', '.join(invalid_intolerances)}. "
                               f"Valid options are: {', '.join(self.VALID_INTOLERANCES)}")
        
        # Validate difficulty and convert to max_ready_time if provided
        if difficulty:
            if difficulty.lower() not in self.DIFFICULTY_LEVELS:
                raise ValueError(f"Invalid difficulty. Valid options are: {', '.join(self.DIFFICULTY_LEVELS.keys())}")
            max_ready_time = self.DIFFICULTY_LEVELS[difficulty.lower()]
        
        # Build search parameters
        params = {
            "query": query,
            "number": number,
            "addRecipeInformation": True,
            "fillIngredients": True,
            "instructionsRequired": True
        }
        
        # Add optional filters
        if diet:
            params["diet"] = diet.lower()
        
        if intolerances:
            params["intolerances"] = ",".join(intolerances)
        
        if max_ready_time:
            params["maxReadyTime"] = max_ready_time
        
        if min_calories:
            params["minCalories"] = min_calories
        
        if max_calories:
            params["maxCalories"] = max_calories
        
        endpoint = "/recipes/complexSearch"
        return self._make_request(endpoint, params)
    
    def get_recipe_information(self, recipe_id: int) -> Dict[str, Any]:
        """
        Get detailed information about a specific recipe.
        
        Args:
            recipe_id (int): ID of the recipe
            
        Returns:
            Dict[str, Any]: Recipe details
        """
        endpoint = f"/recipes/{recipe_id}/information"
        params = {
            "includeNutrition": True  # Now including nutritional information
        }
        
        return self._make_request(endpoint, params)

    def get_recipe_nutrition(self, recipe_id: int) -> Dict[str, Any]:
        """
        Get detailed nutritional information for a recipe.
        
        Args:
            recipe_id (int): ID of the recipe
            
        Returns:
            Dict[str, Any]: Nutritional information including:
                - Macronutrients (protein, fat, carbs)
                - Micronutrients (vitamins, minerals)
                - Caloric breakdown
                - Weight per serving
        """
        endpoint = f"/recipes/{recipe_id}/nutritionWidget.json"
        return self._make_request(endpoint)

    def get_wine_pairing(self, food: str) -> Dict[str, Any]:
        """
        Get wine pairing suggestions for a food or recipe.
        
        Args:
            food (str): Food or dish to pair with wine
            
        Returns:
            Dict[str, Any]: Wine pairing suggestions including:
                - Paired wines
                - Pairing explanation
                - Recommended wines with prices and ratings
        """
        endpoint = "/food/wine/pairing"
        params = {
            "food": food
        }
        return self._make_request(endpoint, params) 