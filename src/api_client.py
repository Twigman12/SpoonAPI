"""
Spoonacular API Client Module

This module provides a client for interacting with the Spoonacular API.
It handles all direct communication with the API, including:
- API key management
- Request handling
- Error handling
- Response validation

The client uses environment variables for secure API key storage and
implements proper error handling for API requests.
"""

import os
import requests
from typing import Dict, Optional, Any, List
from dotenv import load_dotenv

# Load API key from environment variables
load_dotenv()

class SpoonacularClient:
    """
    Client for interacting with the Spoonacular API.
    
    This class encapsulates all API interaction logic, providing a clean interface
    for searching recipes and getting detailed recipe information.
    
    Attributes:
        BASE_URL (str): Base URL for all Spoonacular API endpoints
        api_key (str): API key loaded from environment variables
    """
    
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
        """
        Initialize the Spoonacular API client.
        
        Raises:
            ValueError: If the SPOONACULAR_API_KEY environment variable is not set
        """
        # Load API key from environment variables
        self.api_key = os.getenv("SPOONACULAR_API_KEY")
        if not self.api_key:
            raise ValueError("Spoonacular API key not found in environment variables")
    
    def _make_request(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Make a request to the Spoonacular API.
        
        This is a private helper method that handles:
        1. Adding the API key to parameters
        2. Constructing the full URL
        3. Making the HTTP request
        4. Handling response validation
        5. Converting response to JSON
        
        Args:
            endpoint (str): API endpoint to call (e.g., "/recipes/search")
            params (Dict[str, Any], optional): Query parameters for the request
            
        Returns:
            Dict[str, Any]: JSON response from the API
            
        Raises:
            requests.exceptions.RequestException: If the API request fails
            ValueError: If the response is not valid JSON
        """
        if params is None:
            params = {}
        
        # Always include API key in parameters
        params["apiKey"] = self.api_key
        
        # Make the request and validate response
        response = requests.get(f"{self.BASE_URL}{endpoint}", params=params)
        response.raise_for_status()  # Raises an HTTPError for bad responses (4xx, 5xx)
        
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
        
        This method uses the /recipes/complexSearch endpoint which provides:
        - Basic recipe information
        - Filtering capabilities
        - Sorting options
        
        Args:
            query (str): Search query (e.g., "chicken curry", "vegetarian pasta")
            number (int, optional): Number of results to return. Defaults to 5.
            diet (str, optional): Specific diet (e.g., "vegetarian", "vegan")
            intolerances (List[str], optional): List of intolerances
            max_ready_time (int, optional): Maximum total minutes for recipe
            difficulty (str, optional): Recipe difficulty ("easy", "medium", "hard")
            min_calories (int, optional): Minimum calories per serving
            max_calories (int, optional): Maximum calories per serving
            
        Returns:
            Dict[str, Any]: Search results containing:
                - results: List of recipe previews
                - offset: Starting position of results
                - number: Number of results returned
                - totalResults: Total number of matches
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
        
        This method uses the /recipes/{id}/information endpoint to fetch:
        - Complete ingredient list with amounts
        - Step-by-step instructions
        - Nutritional information
        - Cooking time and servings
        - Dietary information (vegetarian, vegan, etc.)
        
        Args:
            recipe_id (int): ID of the recipe to fetch
            
        Returns:
            Dict[str, Any]: Complete recipe information including
                ingredients, instructions, and nutritional data
        """
        endpoint = f"/recipes/{recipe_id}/information"
        params = {
            "includeNutrition": False  # Exclude nutritional info to reduce response size
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