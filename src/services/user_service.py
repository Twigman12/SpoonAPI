import logging
from typing import Dict, List, Optional
from models import db, User, UserPreference, Favorite

class UserService:
    def get_user_preferences(self, user_id: int) -> Optional[UserPreference]:
        """
        Get user preferences by user ID.
        """
        return UserPreference.query.filter_by(user_id=user_id).first()

    def update_user_preferences(self, user_id: int, preferences: Dict) -> UserPreference:
        """
        Update user preferences for a given user.
        """
        user_pref = self.get_user_preferences(user_id)
        if not user_pref:
            user_pref = UserPreference(user_id=user_id)
            db.session.add(user_pref)
        for key, value in preferences.items():
            if hasattr(user_pref, key):
                setattr(user_pref, key, value)
        db.session.commit()
        return user_pref

    def get_user_favorites(self, user_id: int) -> List[Favorite]:
        """
        Get user's favorite recipes.
        """
        try:
            return Favorite.query.filter_by(user_id=user_id).order_by(Favorite.added_at.desc()).all()
        except Exception as e:
            logging.error(f"Error fetching favorites for user {user_id}: {e}")
            return []

    def is_recipe_favorite(self, user_id: int, recipe_id: int) -> bool:
        """
        Check if recipe is in user's favorites.
        """
        return Favorite.query.filter_by(user_id=user_id, recipe_id=recipe_id).first() is not None

    def toggle_favorite(self, user_id: int, recipe_id: int, recipe_title: str, recipe_image: str) -> bool:
        """
        Toggle favorite status for a recipe. Returns True if added, False if removed.
        """
        favorite = Favorite.query.filter_by(user_id=user_id, recipe_id=recipe_id).first()
        if favorite:
            db.session.delete(favorite)
            db.session.commit()
            logging.info(f"Removed favorite: user_id={user_id}, recipe_id={recipe_id}")
            return False
        else:
            favorite = Favorite(
                user_id=user_id,
                recipe_id=recipe_id,
                recipe_title=recipe_title,
                recipe_image=recipe_image
            )
            db.session.add(favorite)
            db.session.commit()
            logging.info(f"Added favorite: user_id={user_id}, recipe_id={recipe_id}")
            return True

    def get_user_rating(self, user_id: int, recipe_id: int) -> Optional[int]:
        """Get user's rating for a recipe."""
        # This would be implemented with a Rating model
        return None 