import redis
from typing import Dict, List, Any, Optional
from api_client import SpoonacularClient
from news_parser import NewsParser
import os

class RecipeService:
    def __init__(self):
        self.client = SpoonacularClient()
        self.redis_client = redis.from_url(os.getenv('REDIS_URL', 'redis://localhost:6379/0'))
        self.news_parser = NewsParser(api_key=os.getenv("NEWS_API_KEY")) if os.getenv("NEWS_API_KEY") else None

    def build_search_filters(self, data: Dict, user) -> Dict:
        """Build search filters with user preferences."""
        filters = {}
        
        # Basic filters from form
        diet = data.get('diet')
        if diet and diet != 'none':
            filters['diet'] = diet
        
        intolerances = data.getlist('intolerances')
        if intolerances:
            filters['intolerances'] = intolerances
        
        # Time/difficulty filter
        difficulty = data.get('difficulty')
        if difficulty and difficulty != 'custom':
            filters['difficulty'] = difficulty
        else:
            max_time = data.get('max_time')
            if max_time:
                filters['max_ready_time'] = int(max_time)
        
        # Calorie range
        min_calories = data.get('min_calories')
        if min_calories:
            filters['min_calories'] = int(min_calories)
            
        max_calories = data.get('max_calories')
        if max_calories:
            filters['max_calories'] = int(max_calories)
        
        # Add user preferences if available
        if user.is_authenticated:
            user_prefs = user.preferences.first()
            if user_prefs:
                if not filters.get('diet') and user_prefs.diet:
                    filters['diet'] = user_prefs.diet
                if not filters.get('intolerances') and user_prefs.intolerances:
                    filters['intolerances'] = user_prefs.intolerances
                if not filters.get('max_ready_time') and user_prefs.max_cooking_time:
                    filters['max_ready_time'] = user_prefs.max_cooking_time
        
        return filters

    def search_recipes(self, query: str, number: int = 12, **filters) -> Dict[str, Any]:
        """Search recipes with caching."""
        cache_key = f"search:{query}:{hash(frozenset(filters.items()))}"
        cached_result = self.redis_client.get(cache_key)
        
        if cached_result:
            return cached_result
        
        results = self.client.search_recipes(query, number=number, **filters)
        
        # Cache for 5 minutes
        self.redis_client.setex(cache_key, 300, results)
        return results

    def get_recipe_details(self, recipe_id: int) -> Dict[str, Any]:
        """Get recipe details with caching."""
        cache_key = f"recipe:{recipe_id}"
        cached_result = self.redis_client.get(cache_key)
        
        if cached_result:
            return cached_result
        
        recipe_data = self.client.get_recipe_information(recipe_id)
        
        # Cache for 1 hour
        self.redis_client.setex(cache_key, 3600, recipe_data)
        return recipe_data

    def get_similar_recipes(self, recipe_id: int, limit: int = 6) -> List[Dict]:
        """Get similar recipes based on current recipe."""
        try:
            # This would use Spoonacular's similar recipes endpoint
            # For now, return empty list
            return []
        except Exception as e:
            print(f"Error getting similar recipes: {e}")
            return []

    def get_related_news(self, query: str, limit: int = 3) -> List[Dict]:
        """Get related news articles."""
        if not self.news_parser:
            return []
        
        try:
            return self.news_parser.fetch_food_news(query=query, page_size=limit)
        except Exception as e:
            print(f"Error fetching related news: {e}")
            return []

    def add_user_data(self, recipes: List[Dict], user_id: int) -> List[Dict]:
        """Add user-specific data to recipes (favorites, ratings, etc.)."""
        # This would be implemented to add user-specific data
        return recipes 