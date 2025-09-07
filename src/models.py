from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, date

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
    inventory_items = db.relationship('InventoryItem', backref='user', lazy=True)
    storage_locations = db.relationship('StorageLocation', backref='user', lazy=True)
    inventory_history = db.relationship('InventoryHistory', backref='user', lazy=True)

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

class StorageLocation(db.Model):
    """User-defined storage locations (fridge, pantry, freezer, etc.)"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)  # "Refrigerator", "Pantry"
    location_type = db.Column(db.String(50), nullable=False)  # "fridge", "pantry", "freezer"
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    items = db.relationship('InventoryItem', backref='storage_location', lazy=True, cascade='all, delete-orphan')
    
    # Ensure unique location names per user
    __table_args__ = (db.UniqueConstraint('user_id', 'name', name='_user_location_name_uc'),)

class InventoryItem(db.Model):
    """Individual items in user's inventory"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    storage_location_id = db.Column(db.Integer, db.ForeignKey('storage_location.id'), nullable=False)
    
    # Item details
    name = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(50), nullable=False)  # "produce", "dairy", "meat", etc.
    quantity = db.Column(db.Float, nullable=False, default=0)
    unit = db.Column(db.String(20), nullable=False)  # "pcs", "kg", "l", etc.
    
    # Tracking
    expiry_date = db.Column(db.Date)
    purchase_date = db.Column(db.Date, default=date.today)
    notes = db.Column(db.Text)
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Recipe integration
    recipe_ingredient_id = db.Column(db.Integer)  # Link to Spoonacular ingredient ID
    
    # Ensure unique items per user per location
    __table_args__ = (db.UniqueConstraint('user_id', 'storage_location_id', 'name', name='_user_location_item_uc'),)

class InventoryHistory(db.Model):
    """Track inventory changes for analytics"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    item_id = db.Column(db.Integer, db.ForeignKey('inventory_item.id'), nullable=False)
    action = db.Column(db.String(20), nullable=False)  # "add", "use", "expire", "delete"
    quantity_change = db.Column(db.Float)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    notes = db.Column(db.Text) 