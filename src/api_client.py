"""
Spoonacular API client for recipe search and information retrieval.
"""

import os
import requests
from typing import Dict, Optional, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class SpoonacularClient:
    """Client for interacting with the Spoonacular API."""
    
    BASE_URL = "https://api.spoonacular.com"
    
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
    
    def search_recipes(self, query: str, number: int = 5) -> Dict[str, Any]:
        """
        Search for recipes using a query string.
        
        Args:
            query (str): Search query
            number (int, optional): Number of results to return. Defaults to 5.
            
        Returns:
            Dict[str, Any]: Search results
        """
        endpoint = "/recipes/complexSearch"
        params = {
            "query": query,
            "number": number,
            "addRecipeInformation": True
        }
        
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
            "includeNutrition": False
        }
        
        return self._make_request(endpoint, params) 