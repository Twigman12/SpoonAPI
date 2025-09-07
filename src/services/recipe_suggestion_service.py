"""
Recipe Suggestion Service - Provides recipe recommendations based on inventory
"""
from typing import List, Dict, Optional, Tuple
from services.inventory_service import InventoryService
from services.storage_service import StorageService
from api_client import SpoonacularClient
from models import db


class RecipeSuggestionService:
    """Service class for recipe suggestions based on inventory"""
    
    def __init__(self, db_session=None):
        self.db = db_session or db.session
        self.inventory_service = InventoryService()
        self.storage_service = StorageService()
        self.spoonacular_client = SpoonacularClient()
    
    def suggest_recipes_from_inventory(self, user_id: int, max_results: int = 10) -> List[Dict]:
        """
        Suggest recipes based on available ingredients in inventory
        
        Args:
            user_id: ID of the user
            max_results: Maximum number of recipes to return
            
        Returns:
            List of recipe suggestions
        """
        try:
            # Get user's inventory items
            inventory_items = self.inventory_service.search_items(user_id, {})
            
            if not inventory_items:
                return []
            
            # Create ingredient list for API search
            ingredient_names = [item['name'] for item in inventory_items]
            
            # Search for recipes using available ingredients
            recipes = self.spoonacular_client.search_recipes_by_ingredients(
                ingredients=ingredient_names,
                number=max_results
            )
            
            # Enhance recipes with inventory context
            enhanced_recipes = []
            for recipe in recipes:
                recipe['inventory_context'] = self._get_recipe_inventory_context(
                    user_id, recipe, inventory_items
                )
                enhanced_recipes.append(recipe)
            
            return enhanced_recipes
            
        except Exception as e:
            print(f"Error suggesting recipes from inventory: {str(e)}")
            return []
    
    def get_cookable_recipes(self, user_id: int, missing_ingredients_threshold: int = 2) -> List[Dict]:
        """
        Get recipes that can be cooked with current inventory (with minimal missing ingredients)
        
        Args:
            user_id: ID of the user
            missing_ingredients_threshold: Maximum number of missing ingredients allowed
            
        Returns:
            List of cookable recipes
        """
        try:
            # Get user's inventory items
            inventory_items = self.inventory_service.search_items(user_id, {})
            
            if not inventory_items:
                return []
            
            # Create ingredient list for API search
            ingredient_names = [item['name'] for item in inventory_items]
            
            # Search for recipes
            recipes = self.spoonacular_client.search_recipes_by_ingredients(
                ingredients=ingredient_names,
                number=20  # Get more results to filter
            )
            
            # Filter recipes based on missing ingredients threshold
            cookable_recipes = []
            for recipe in recipes:
                inventory_context = self._get_recipe_inventory_context(
                    user_id, recipe, inventory_items
                )
                
                if inventory_context['missing_ingredients_count'] <= missing_ingredients_threshold:
                    recipe['inventory_context'] = inventory_context
                    cookable_recipes.append(recipe)
            
            return cookable_recipes[:10]  # Return top 10 cookable recipes
            
        except Exception as e:
            print(f"Error getting cookable recipes: {str(e)}")
            return []
    
    def suggest_shopping_for_recipe(self, user_id: int, recipe_id: int) -> Dict:
        """
        Suggest what to buy to make a specific recipe
        
        Args:
            user_id: ID of the user
            recipe_id: ID of the recipe
            
        Returns:
            Dictionary with shopping suggestions
        """
        try:
            # Get recipe details
            recipe = self.spoonacular_client.get_recipe_information(recipe_id)
            
            if not recipe:
                return {'error': 'Recipe not found'}
            
            # Get user's inventory
            inventory_items = self.inventory_service.search_items(user_id, {})
            
            # Analyze what's needed vs what's available
            shopping_list = []
            available_ingredients = []
            
            for ingredient in recipe.get('extendedIngredients', []):
                ingredient_name = ingredient['name'].lower()
                needed_amount = ingredient.get('amount', 0)
                unit = ingredient.get('unit', '')
                
                # Check if user has this ingredient
                available_item = None
                for item in inventory_items:
                    if ingredient_name in item['name'].lower() or item['name'].lower() in ingredient_name:
                        available_item = item
                        break
                
                if available_item:
                    if available_item['quantity'] >= needed_amount:
                        available_ingredients.append({
                            'name': ingredient['name'],
                            'amount': needed_amount,
                            'unit': unit,
                            'available': available_item['quantity'],
                            'status': 'sufficient'
                        })
                    else:
                        shopping_list.append({
                            'name': ingredient['name'],
                            'amount': needed_amount - available_item['quantity'],
                            'unit': unit,
                            'available': available_item['quantity'],
                            'status': 'insufficient'
                        })
                else:
                    shopping_list.append({
                        'name': ingredient['name'],
                        'amount': needed_amount,
                        'unit': unit,
                        'available': 0,
                        'status': 'missing'
                    })
            
            return {
                'recipe_id': recipe_id,
                'recipe_title': recipe.get('title', 'Unknown Recipe'),
                'shopping_list': shopping_list,
                'available_ingredients': available_ingredients,
                'can_cook': len(shopping_list) == 0,
                'missing_count': len(shopping_list)
            }
            
        except Exception as e:
            print(f"Error suggesting shopping for recipe: {str(e)}")
            return {'error': str(e)}
    
    def plan_meals_from_inventory(self, user_id: int, days: int = 7) -> List[Dict]:
        """
        Suggest meal plan based on expiring ingredients
        
        Args:
            user_id: ID of the user
            days: Number of days to plan for
            
        Returns:
            List of meal suggestions
        """
        try:
            # Get expiring items
            expiring_items = self.inventory_service.get_expiring_items(user_id, days)
            
            if not expiring_items:
                return []
            
            # Get recipes that use expiring ingredients
            ingredient_names = [item['name'] for item in expiring_items]
            
            recipes = self.spoonacular_client.search_recipes_by_ingredients(
                ingredients=ingredient_names,
                number=15
            )
            
            # Create meal plan suggestions
            meal_suggestions = []
            for recipe in recipes:
                inventory_context = self._get_recipe_inventory_context(
                    user_id, recipe, expiring_items
                )
                
                # Prioritize recipes that use more expiring ingredients
                expiring_ingredients_used = sum(1 for ingredient in inventory_context.get('available_ingredients', [])
                                              if any(exp_item['name'].lower() in ingredient['name'].lower() 
                                                    for exp_item in expiring_items))
                
                meal_suggestions.append({
                    'recipe': recipe,
                    'inventory_context': inventory_context,
                    'expiring_ingredients_used': expiring_ingredients_used,
                    'priority_score': expiring_ingredients_used / len(expiring_items) if expiring_items else 0
                })
            
            # Sort by priority score (recipes using more expiring ingredients first)
            meal_suggestions.sort(key=lambda x: x['priority_score'], reverse=True)
            
            return meal_suggestions[:7]  # Return top 7 meal suggestions
            
        except Exception as e:
            print(f"Error planning meals from inventory: {str(e)}")
            return []
    
    def _get_recipe_inventory_context(self, user_id: int, recipe: Dict, inventory_items: List[Dict]) -> Dict:
        """
        Get inventory context for a recipe (what's available, what's missing)
        
        Args:
            user_id: ID of the user
            recipe: Recipe data
            inventory_items: User's inventory items
            
        Returns:
            Dictionary with inventory context
        """
        available_ingredients = []
        missing_ingredients = []
        
        for ingredient in recipe.get('extendedIngredients', []):
            ingredient_name = ingredient['name'].lower()
            needed_amount = ingredient.get('amount', 0)
            unit = ingredient.get('unit', '')
            
            # Check if user has this ingredient
            available_item = None
            for item in inventory_items:
                if ingredient_name in item['name'].lower() or item['name'].lower() in ingredient_name:
                    available_item = item
                    break
            
            if available_item:
                if available_item['quantity'] >= needed_amount:
                    available_ingredients.append({
                        'name': ingredient['name'],
                        'amount': needed_amount,
                        'unit': unit,
                        'available': available_item['quantity'],
                        'status': 'sufficient'
                    })
                else:
                    available_ingredients.append({
                        'name': ingredient['name'],
                        'amount': needed_amount,
                        'unit': unit,
                        'available': available_item['quantity'],
                        'status': 'insufficient'
                    })
                    missing_ingredients.append({
                        'name': ingredient['name'],
                        'amount': needed_amount - available_item['quantity'],
                        'unit': unit
                    })
            else:
                missing_ingredients.append({
                    'name': ingredient['name'],
                    'amount': needed_amount,
                    'unit': unit
                })
        
        return {
            'available_ingredients': available_ingredients,
            'missing_ingredients': missing_ingredients,
            'missing_ingredients_count': len(missing_ingredients),
            'can_cook': len(missing_ingredients) == 0,
            'completion_percentage': (len(available_ingredients) / (len(available_ingredients) + len(missing_ingredients))) * 100 if (available_ingredients or missing_ingredients) else 0
        }
