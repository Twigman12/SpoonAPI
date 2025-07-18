from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    preferences = db.relationship('UserPreference', backref='user', lazy=True)
    favorites = db.relationship('Favorite', backref='user', lazy=True)
    meal_plans = db.relationship('MealPlan', backref='user', lazy=True)
    collections = db.relationship('RecipeCollection', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class UserPreference(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    diet = db.Column(db.String(50))
    intolerances = db.Column(db.JSON)
    max_cooking_time = db.Column(db.Integer)
    calorie_range_min = db.Column(db.Integer)
    calorie_range_max = db.Column(db.Integer)

class Favorite(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    recipe_id = db.Column(db.Integer, nullable=False)
    recipe_title = db.Column(db.String(200), nullable=False)
    recipe_image = db.Column(db.String(500))
    added_at = db.Column(db.DateTime, default=datetime.utcnow)

class RecipeRating(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    recipe_id = db.Column(db.Integer, nullable=False)
    rating = db.Column(db.Integer, nullable=False)  # 1-5 stars
    review = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Ensure one rating per user per recipe
    __table_args__ = (db.UniqueConstraint('user_id', 'recipe_id', name='_user_recipe_rating_uc'),)

class RecipeCollection(db.Model):
    """Model for organizing recipes into user-defined collections/categories."""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    color = db.Column(db.String(7), default='#007bff')  # Hex color code
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    recipes = db.relationship('CollectionRecipe', backref='collection', lazy=True, cascade='all, delete-orphan')

class CollectionRecipe(db.Model):
    """Junction table for recipes in collections."""
    id = db.Column(db.Integer, primary_key=True)
    collection_id = db.Column(db.Integer, db.ForeignKey('recipe_collection.id'), nullable=False)
    recipe_id = db.Column(db.Integer, nullable=False)
    recipe_title = db.Column(db.String(200), nullable=False)
    recipe_image = db.Column(db.String(500))
    added_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Ensure unique recipe per collection
    __table_args__ = (db.UniqueConstraint('collection_id', 'recipe_id', name='_collection_recipe_uc'),)

class MealPlan(db.Model):
    """Model for weekly meal planning."""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    week_start = db.Column(db.Date, nullable=False)  # Monday of the week
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    meals = db.relationship('MealPlanItem', backref='meal_plan', lazy=True, cascade='all, delete-orphan')

class MealPlanItem(db.Model):
    """Individual meal items in a meal plan."""
    id = db.Column(db.Integer, primary_key=True)
    meal_plan_id = db.Column(db.Integer, db.ForeignKey('meal_plan.id'), nullable=False)
    day_of_week = db.Column(db.Integer, nullable=False)  # 0=Monday, 1=Tuesday, etc.
    meal_type = db.Column(db.String(20), nullable=False)  # breakfast, lunch, dinner, snack
    recipe_id = db.Column(db.Integer, nullable=False)
    recipe_title = db.Column(db.String(200), nullable=False)
    recipe_image = db.Column(db.String(500))
    servings = db.Column(db.Integer, default=1)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Ensure one meal per type per day
    __table_args__ = (db.UniqueConstraint('meal_plan_id', 'day_of_week', 'meal_type', name='_meal_plan_day_type_uc'),) 