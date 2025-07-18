"""
News Parser Module for The Guardian API

This module handles fetching and parsing news data from The Guardian
API, focusing on food, cooking, and culinary culture.
"""

import requests
import re
from typing import Dict, List, Any

GUARDIAN_API_URL = "https://content.guardianapis.com/search"

class NewsParser:
    def __init__(self, api_key: str):
        if not api_key:
            raise ValueError("API key for The Guardian API is required.")
        self.api_key = api_key

    def fetch_food_news(self, query: str = "food,recipes", page_size: int = 5) -> List[Dict[str, Any]]:
        """
        Fetch food-related news articles from The Guardian.
        
        Args:
            query (str): The search query. Defaults to "food,recipes".
            page_size (int): The number of articles to return.
            
        Returns:
            List[Dict[str, Any]]: A list of parsed news articles.
        """
        params = {
            "q": query,
            "api-key": self.api_key,
            "show-fields": "thumbnail,trailText",
            "page-size": page_size,
            "order-by": "relevance"
        }
        
        try:
            response = requests.get(GUARDIAN_API_URL, params=params)
            response.raise_for_status()  # Raise an exception for bad status codes
            data = response.json().get("response", {}).get("results", [])
            return self._parse_articles(data)
        except requests.exceptions.RequestException as e:
            print(f"Error fetching news from The Guardian API: {e}")
            return []

    def fetch_popular_recipe_articles(self, page_size: int = 20) -> List[Dict[str, Any]]:
        """
        Fetch articles about popular, trending, or featured recipes.
        
        Args:
            page_size (int): The number of articles to return.
            
        Returns:
            List[Dict[str, Any]]: A list of articles about popular recipes.
        """
        # Broaden the search query to just 'recipes' for more results
        query = "recipes"
        params = {
            "q": query,
            "api-key": self.api_key,
            "show-fields": "thumbnail,trailText,body",
            "page-size": page_size,
            "order-by": "newest"
        }
        
        try:
            response = requests.get(GUARDIAN_API_URL, params=params)
            response.raise_for_status()
            data = response.json().get("response", {}).get("results", [])
            return self._parse_articles(data)
        except requests.exceptions.RequestException as e:
            print(f"Error fetching popular recipe articles: {e}")
            return []

    def extract_recipe_names_from_articles(self, articles: List[Dict[str, Any]]) -> List[str]:
        """
        Extract potential recipe names from article titles and previews.
        
        Args:
            articles (List[Dict[str, Any]]): List of articles to analyze.
            
        Returns:
            List[str]: List of potential recipe names found in the articles.
        """
        recipe_names = []
        
        # Common food-related keywords to help identify recipes
        food_keywords = [
            "recipe", "dish", "pasta", "cake", "bread", "soup", "salad", "chicken", 
            "beef", "fish", "curry", "pizza", "sandwich", "burger", "pie", "cookie",
            "muffin", "stew", "risotto", "lasagna", "pancake", "waffle", "taco"
        ]
        
        for article in articles:
            title = article.get("title", "").lower()
            preview = article.get("preview", "").lower()
            
            # Extract potential recipe names from titles
            # Look for patterns like "Best [Food Name] recipe" or "[Food Name]: the perfect recipe"
            title_recipes = self._extract_recipes_from_text(title, food_keywords)
            preview_recipes = self._extract_recipes_from_text(preview, food_keywords)
            
            recipe_names.extend(title_recipes)
            recipe_names.extend(preview_recipes)
        
        # Remove duplicates and return unique recipe names
        return list(set(recipe_names))

    def _extract_recipes_from_text(self, text: str, food_keywords: List[str]) -> List[str]:
        """
        Extract recipe names from a piece of text using keyword matching and patterns.
        """
        recipes = []
        
        # Pattern 1: "best [food] recipe" or "perfect [food] recipe"
        pattern1 = r'\b(?:best|perfect|ultimate|easy|simple)\s+([a-zA-Z\s]+?)\s+recipe\b'
        matches1 = re.findall(pattern1, text, re.IGNORECASE)
        
        # Pattern 2: "[food] recipe" (simpler pattern)
        pattern2 = r'\b([a-zA-Z\s]+?)\s+recipe\b'
        matches2 = re.findall(pattern2, text, re.IGNORECASE)
        
        # Pattern 3: Food keywords mentioned with context
        for keyword in food_keywords:
            if keyword in text:
                # Extract surrounding words to form potential recipe names
                pattern = rf'\b([a-zA-Z\s]*{keyword}[a-zA-Z\s]*)\b'
                matches = re.findall(pattern, text, re.IGNORECASE)
                recipes.extend([match.strip() for match in matches if len(match.strip()) > 3])
        
        # Clean up the extracted names
        cleaned_recipes = []
        for recipe in matches1 + matches2 + recipes:
            recipe = recipe.strip()
            # Remove common stop words and clean up
            if len(recipe) > 2 and recipe not in ['the', 'and', 'or', 'for', 'with']:
                cleaned_recipes.append(recipe.title())
        
        return cleaned_recipes[:3]  # Return top 3 matches per text

    def _parse_articles(self, articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Parse a list of raw article data into a simplified format.
        """
        parsed_articles = []
        for article in articles:
            fields = article.get("fields", {})
            parsed_articles.append({
                "title": article.get("webTitle", "No Title"),
                "url": article.get("webUrl", "#"),
                "preview": fields.get("trailText", "No preview available."),
                "thumbnail": fields.get("thumbnail", None),
                "body": fields.get("body", "")
            })
        return parsed_articles

    def parse_trending_ingredients(self, articles: List[Dict[str, Any]]) -> List[str]:
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

    def match_news_to_recipe(self, recipe: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Find relevant news articles based on recipe ingredients or cuisine type.
        """
        pass

    def get_regional_highlights(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Get trending recipes and food stories by region.
        """
        pass 