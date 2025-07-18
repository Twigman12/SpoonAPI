import logging
from flask import Blueprint, render_template, jsonify, request
from flask_login import login_required, current_user
from services.user_service import UserService

favorites_bp = Blueprint('favorites', __name__)

@favorites_bp.route('/favorites')
@login_required
def favorites():
    """
    Display user's favorite recipes.
    """
    user_favorites = UserService().get_user_favorites(current_user.id)
    return render_template('favorites.html', favorites=user_favorites)

@favorites_bp.route('/favorite/<int:recipe_id>', methods=['POST'])
@login_required
def toggle_favorite(recipe_id: int):
    """
    Add or remove a recipe from user's favorites.
    """
    try:
        # Get recipe details from API (simulate, or use a service)
        data = request.get_json() or {}
        recipe_title = data.get('recipe_title', 'Unknown Recipe')
        recipe_image = data.get('recipe_image', '')
        status = UserService().toggle_favorite(
            user_id=current_user.id,
            recipe_id=recipe_id,
            recipe_title=recipe_title,
            recipe_image=recipe_image
        )
        if status:
            return jsonify({'status': 'added', 'message': 'Recipe added to favorites'})
        else:
            return jsonify({'status': 'removed', 'message': 'Recipe removed from favorites'})
    except Exception as e:
        logging.error(f"Error toggling favorite: {e}")
        return jsonify({'error': str(e)}), 500

@favorites_bp.route('/check-favorite/<int:recipe_id>')
@login_required
def check_favorite(recipe_id: int):
    """
    Check if a recipe is in user's favorites.
    """
    is_fav = UserService().is_recipe_favorite(current_user.id, recipe_id)
    return jsonify({'is_favorite': is_fav}) 