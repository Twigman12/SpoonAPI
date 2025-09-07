import os
import sys
import logging
import random
from datetime import datetime, timedelta
from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify, Blueprint, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models import db, User, UserPreference, RecipeRating, Favorite, RecipeCollection, CollectionRecipe, MealPlan, MealPlanItem
from api_client import SpoonacularClient
from data_parser import parse_recipe_search_results, parse_recipe_details
from news_parser import NewsParser
from auth import auth
from routes.favorites import favorites_bp
from routes.inventory import inventory_bp
from routes.storage import storage_bp

load_dotenv()

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s'
)

def create_app() -> Flask:
    """
    Flask application factory. Registers blueprints and initializes extensions.
    """
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///recipes.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize extensions
    db.init_app(app)
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    @login_manager.user_loader
    def load_user(user_id: str):
        return db.session.get(User, int(user_id))

    # Register blueprints
    app.register_blueprint(auth)
    app.register_blueprint(favorites_bp)
    app.register_blueprint(inventory_bp)
    app.register_blueprint(storage_bp)

    # Initialize database tables
    with app.app_context():
        db.create_all()

    # Main routes
    @app.route('/')
    def index():
        """Home page with recipe search and popular recipes."""
        # Define the filter options that the template expects
        diets = ['vegetarian', 'vegan', 'gluten-free', 'keto', 'paleo', 'mediterranean', 'low-carb']
        intolerances = ['dairy', 'egg', 'gluten', 'grain', 'peanut', 'seafood', 'shellfish', 'soy', 'sulfite', 'tree nut', 'wheat']
        difficulty_levels = {
            'easy': '30',
            'medium': '60', 
            'hard': '120'
        }
        return render_template('index.html', 
                             diets=diets, 
                             intolerances=intolerances, 
                             difficulty_levels=difficulty_levels)

    @app.route('/dashboard')
    @login_required
    def dashboard():
        """User dashboard with personalized content."""
        # Get user's recent favorites
        user_favorites = Favorite.query.filter_by(user_id=current_user.id).order_by(Favorite.added_at.desc()).limit(6).all()
        
        # Get user's collections
        user_collections = RecipeCollection.query.filter_by(user_id=current_user.id).all()
        
        # Get current meal plan
        today = datetime.today()
        week_start = (today - timedelta(days=today.weekday())).date()
        current_meal_plan = MealPlan.query.filter_by(user_id=current_user.id, week_start=week_start).first()
        
        # Get user preferences
        user_pref = UserPreference.query.filter_by(user_id=current_user.id).first()
        
        # Get counts for stats
        total_favorites = Favorite.query.filter_by(user_id=current_user.id).count()
        total_collections = RecipeCollection.query.filter_by(user_id=current_user.id).count()
        
        # Get inventory stats
        from services.inventory_service import InventoryService
        inventory_service = InventoryService()
        inventory_stats = inventory_service.get_inventory_stats(current_user.id)
        
        return render_template('dashboard.html', 
                             favorites=user_favorites,
                             collections=user_collections,
                             current_meal_plan=current_meal_plan,
                             user_pref=user_pref,
                             total_favorites=total_favorites,
                             total_collections=total_collections,
                             inventory_stats=inventory_stats)

    @app.route('/collections')
    @login_required
    def collections():
        """Display user's recipe collections."""
        user_collections = RecipeCollection.query.filter_by(user_id=current_user.id).all()
        return render_template('collections.html', collections=user_collections)

    @app.route('/create_collection', methods=['GET', 'POST'])
    @login_required
    def create_collection():
        """Create a new recipe collection."""
        if request.method == 'POST':
            name = request.form.get('name')
            description = request.form.get('description')
            color = request.form.get('color', '#007bff')
            
            new_collection = RecipeCollection(
                user_id=current_user.id,
                name=name,
                description=description,
                color=color
            )
            db.session.add(new_collection)
            db.session.commit()
            flash('Collection created successfully!', 'success')
            return redirect(url_for('collections'))
        
        return render_template('create_collection.html')

    @app.route('/view_collection/<int:collection_id>')
    @login_required
    def view_collection(collection_id):
        """View a specific recipe collection."""
        collection = RecipeCollection.query.filter_by(id=collection_id, user_id=current_user.id).first_or_404()
        return render_template('view_collection.html', collection=collection)

    @app.route('/meal-plan')
    @login_required
    def meal_plan():
        from datetime import datetime, timedelta
        week_start_str = request.args.get('week_start')
        if week_start_str:
            week_start = datetime.strptime(week_start_str, '%Y-%m-%d').date()
        else:
            today = datetime.today()
            week_start = (today - timedelta(days=today.weekday())).date()

        meal_plan = MealPlan.query.filter_by(user_id=current_user.id, week_start=week_start).first()
        meals = meal_plan.meals if meal_plan else []
        meal_types = ['breakfast', 'lunch', 'dinner', 'snack']
        days = []
        for i in range(7):
            day_date = week_start + timedelta(days=i)
            day_short = day_date.strftime('%a')
            day_number = i
            day_meals = {mt: None for mt in meal_types}
            for meal in meals:
                if meal.day_of_week == i:
                    day_meals[meal.meal_type] = meal
            days.append({'date': day_date, 'day_short': day_short, 'day_number': day_number, 'meals': day_meals})
        prev_week = week_start - timedelta(days=7)
        next_week = week_start + timedelta(days=7)
        return render_template('meal_plan.html', days=days, meal_types=meal_types, meal_plan=meal_plan, week_start=week_start, prev_week=prev_week, next_week=next_week, timedelta=timedelta)

    @app.route('/meal-plan/add', methods=['POST'])
    @login_required
    def add_meal():
        data = request.get_json()
        week_start = datetime.strptime(data['week_start'], '%Y-%m-%d').date()
        day_of_week = data['day_of_week']
        meal_type = data['meal_type']
        recipe_id = data['recipe_id']
        recipe_title = data['recipe_title']
        recipe_image = data.get('recipe_image', '')
        servings = data.get('servings', 1)
        notes = data.get('notes', '')
        meal_plan = MealPlan.query.filter_by(user_id=current_user.id, week_start=week_start).first()
        if not meal_plan:
            meal_plan = MealPlan(user_id=current_user.id, week_start=week_start)
            db.session.add(meal_plan)
            db.session.commit()
        # Remove existing meal for this slot
        MealPlanItem.query.filter_by(meal_plan_id=meal_plan.id, day_of_week=day_of_week, meal_type=meal_type).delete()
        meal = MealPlanItem(
            meal_plan_id=meal_plan.id,
            day_of_week=day_of_week,
            meal_type=meal_type,
            recipe_id=recipe_id,
            recipe_title=recipe_title,
            recipe_image=recipe_image,
            servings=servings,
            notes=notes
        )
        db.session.add(meal)
        db.session.commit()
        return jsonify({'status': 'added'})

    @app.route('/meal-plan/remove', methods=['POST'])
    @login_required
    def remove_meal():
        data = request.get_json()
        week_start = datetime.strptime(data['week_start'], '%Y-%m-%d').date()
        day_of_week = data['day_of_week']
        meal_type = data['meal_type']
        meal_plan = MealPlan.query.filter_by(user_id=current_user.id, week_start=week_start).first()
        if meal_plan:
            MealPlanItem.query.filter_by(meal_plan_id=meal_plan.id, day_of_week=day_of_week, meal_type=meal_type).delete()
            db.session.commit()
        return jsonify({'status': 'removed'})

    @app.route('/kitchen-inventory')
    @login_required
    def kitchen_inventory():
        """Kitchen inventory management page."""
        from services.storage_service import StorageService
        from services.inventory_service import InventoryService
        
        # Get storage locations and inventory stats
        storage_service = StorageService()
        inventory_service = InventoryService()
        
        storage_locations = storage_service.get_user_storage_locations(current_user.id)
        inventory_stats = inventory_service.get_inventory_stats(current_user.id)
        
        # If no storage locations exist, create default ones
        if not storage_locations:
            storage_service.create_default_storage_locations(current_user.id)
            storage_locations = storage_service.get_user_storage_locations(current_user.id)
        
        return render_template('kitchen_inventory.html', 
                             storage_locations=storage_locations,
                             inventory_stats=inventory_stats)

    @app.route('/meal-plan/clear', methods=['POST'])
    @login_required
    def clear_meal_plan():
        """Clear all meals for a specific week."""
        data = request.get_json()
        week_start = datetime.strptime(data['week_start'], '%Y-%m-%d').date()
        meal_plan = MealPlan.query.filter_by(user_id=current_user.id, week_start=week_start).first()
        if meal_plan:
            # Delete all meal items for this plan
            MealPlanItem.query.filter_by(meal_plan_id=meal_plan.id).delete()
            # Delete the meal plan itself
            db.session.delete(meal_plan)
            db.session.commit()
        return jsonify({'status': 'cleared'})

    @app.route('/preferences')
    @login_required
    def preferences():
        """User preferences page."""
        return render_template('preferences.html')

    @app.route('/food-news')
    def food_news():
        articles = []
        try:
            from news_parser import NewsParser
            import os
            api_key = os.getenv('GUARDIAN_API_KEY')
            articles = NewsParser(api_key).fetch_popular_recipe_articles()
        except Exception as e:
            print(f"Error fetching articles: {e}")
        return render_template('food_news.html', articles=articles)

    @app.route('/recipe/<int:recipe_id>')
    def recipe(recipe_id):
        """Display detailed recipe information."""
        try:
            # Get recipe details from API
            api_client = SpoonacularClient()
            recipe_data = api_client.get_recipe_information(recipe_id)
            recipe = parse_recipe_details(recipe_data)
            avg_rating = 0
            total_ratings = 0
            ratings = []
            related_news = []
            return render_template(
                'recipe.html',
                recipe=recipe,
                recipe_id=recipe_id,
                avg_rating=avg_rating,
                total_ratings=total_ratings,
                ratings=ratings,
                related_news=related_news
            )
        except Exception as e:
            logging.error(f"Error getting recipe {recipe_id}: {str(e)}")
            flash('Error loading recipe details', 'error')
            return redirect(url_for('index'))

    @app.route('/food-culture')
    def food_culture():
        """Food culture and news page."""
        diets = ['vegetarian', 'vegan', 'gluten-free', 'keto', 'paleo', 'mediterranean', 'low-carb']
        intolerances = ['dairy', 'egg', 'gluten', 'grain', 'peanut', 'seafood', 'shellfish', 'soy', 'sulfite', 'tree nut', 'wheat']
        difficulty_levels = {
            'easy': '30',
            'medium': '60', 
            'hard': '120'
        }
        return render_template('index.html', 
                              diets=diets, 
                              intolerances=intolerances, 
                              difficulty_levels=difficulty_levels)

    @app.route('/create-test-users')
    def create_test_users():
        """Create test users for development."""
        try:
            # Check if test user already exists
            test_user = User.query.filter_by(username='testuser').first()
            if not test_user:
                test_user = User(username='testuser', email='test@example.com')
                test_user.set_password('testpass123')
                db.session.add(test_user)
                db.session.commit()
                flash('Test user created successfully! Username: testuser, Password: testpass123', 'success')
            else:
                flash('Test user already exists! Username: testuser, Password: testpass123', 'info')
            
            return redirect(url_for('auth.login'))
        except Exception as e:
            flash(f'Error creating test user: {str(e)}', 'error')
            return redirect(url_for('auth.login'))

    @app.route('/search', methods=['POST'])
    def search_recipes():
        """Search for recipes with filters."""
        try:
            # Get form data
            query = request.form.get('query')
            diet = request.form.get('diet')
            intolerances = request.form.getlist('intolerances')
            difficulty = request.form.get('difficulty')
            max_time = request.form.get('max_time')
            min_calories = request.form.get('min_calories')
            max_calories = request.form.get('max_calories')
            
            if not query:
                return jsonify({'error': 'Please enter a search query'})
            
            # Convert difficulty to max_ready_time if provided
            max_ready_time = None
            if difficulty and difficulty != 'custom':
                difficulty_levels = {
                    'easy': 30,
                    'medium': 60,
                    'hard': 120
                }
                max_ready_time = difficulty_levels.get(difficulty.lower())
            elif max_time:
                max_ready_time = int(max_time)
            
            # Initialize API client
            api_client = SpoonacularClient()
            
            # Search for recipes
            result = api_client.search_recipes(
                query=query,
                number=12,  # Show more results for search
                diet=diet if diet != 'none' else None,
                intolerances=intolerances if intolerances else None,
                max_ready_time=max_ready_time,
                min_calories=int(min_calories) if min_calories else None,
                max_calories=int(max_calories) if max_calories else None
            )
            
            # Parse the results
            recipes = parse_recipe_search_results(result)
            
            return jsonify({
                'success': True,
                'recipes': recipes
            })
                
        except Exception as e:
            logging.error(f"Error searching recipes: {str(e)}")
            return jsonify({
                'success': False,
                'error': f'Error searching recipes: {str(e)}'
            })

    @app.route('/random-recipe', methods=['POST'])
    def random_recipe():
        """Get a random recipe with optional filters."""
        # Comprehensive ingredient-specific dad jokes
        ingredient_jokes = {
            # Pasta & Noodles
            'pasta': ["What do you call a fake noodle? An impasta! 🍝", "Why did the spaghetti go to the doctor? Because it was feeling a little saucy! 🍝"],
            'spaghetti': ["What do you call a fake noodle? An impasta! 🍝", "Why did the spaghetti go to the doctor? Because it was feeling a little saucy! 🍝"],
            'noodle': ["What do you call a fake noodle? An impasta! 🍝", "Why did the noodle go to therapy? It had too many issues to work through! 🍜"],
            'penne': ["What do you call a fake noodle? An impasta! 🍝", "Why did the penne pasta feel left out? Because it was tubular! 🍝"],
            
            # Meats
            'chicken': ["Why did the chicken go to the doctor? Because it was feeling a little under the weather! 🌤️", "What do you call a chicken that crosses the road? A road runner! 🐔"],
            'beef': ["What do you call a cow that plays hide and seek? A moo-ving target! 🐄", "Why did the cow go to the gym? To get some beef-cake! 💪"],
            'pork': ["What do you call a pig that does karate? A pork chop! 🥋", "Why did the pig go to the spa? To get a mud bath! 🐷"],
            'lamb': ["What do you call a sheep that's been in the sun? A sun-baa! 🌞", "Why did the lamb go to school? To get a little sheep-diploma! 🐑"],
            'turkey': ["What do you call a turkey on Thanksgiving? Dinner! 🦃", "Why did the turkey cross the road? To prove it wasn't chicken! 🦃"],
            
            # Fish & Seafood
            'salmon': ["What do you call a fish wearing a bowtie? So-fish-ticated! 🐟", "Why did the salmon blush? Because it saw the ocean's bottom! 🐠"],
            'tuna': ["What do you call a fish that's good at math? A calcu-lator! 🧮", "Why did the tuna go to the doctor? Because it was feeling a little fishy! 🐟"],
            'shrimp': ["What do you call a shrimp that's been in the gym? A prawn! 💪", "Why did the shrimp go to the party? Because it was a little shellfish! 🦐"],
            'cod': ["What do you call a fish that's been in the fridge too long? Cold fish! 🐟", "Why did the cod go to the bank? To get some fishy money! 🐟"],
            
            # Vegetables
            'tomato': ["Why did the tomato turn red? Because it saw the salad dressing! 🍅", "What do you call a tomato that's been in the sun? A sun-dried tomato! 🍅"],
            'lettuce': ["Why did the lettuce win the race? Because it was ahead! 🥬", "What do you call lettuce that's been in the fridge too long? Wilted! 🥬"],
            'carrot': ["What do you call a carrot that's been in the gym? A buff carrot! 🥕", "Why did the carrot go to the doctor? Because it was feeling a little orange! 🥕"],
            'onion': ["Why did the onion go to the doctor? Because it was feeling a little tearful! 🧅", "What do you call an onion that's been in the sun? A sun-burned onion! 🧅"],
            'garlic': ["What do you call garlic that's been in the fridge? Cold garlic! 🧄", "Why did the garlic go to the party? Because it was a little spicy! 🧄"],
            'potato': ["What do you call a lazy vegetable? A couch potato! 🥔", "Why did the potato go to the doctor? Because it was feeling a little mashed! 🥔"],
            'broccoli': ["What do you call broccoli that's been in the gym? Buff broccoli! 🥦", "Why did the broccoli go to the doctor? Because it was feeling a little green! 🥦"],
            'spinach': ["What do you call spinach that's been in the sun? Sun-dried spinach! 🥬", "Why did the spinach go to the party? Because it was a little leafy! 🥬"],
            'mushroom': ["Why did the mushroom go to the party? Because he was a fungi! 🍄", "What do you call a mushroom that's been in the rain? A wet one! 🍄"],
            
            # Dairy
            'cheese': ["What do you call cheese that isn't yours? Nacho cheese! 🧀", "Why did the cheese go to the doctor? Because it was feeling a little blue! 🧀"],
            'milk': ["What do you call milk that's been in the fridge too long? Sour milk! 🥛", "Why did the milk go to the doctor? Because it was feeling a little curdled! 🥛"],
            'butter': ["What do you call butter that's been in the sun? Melted butter! 🧈", "Why did the butter go to the party? Because it was a little spread! 🧈"],
            'cream': ["What do you call cream that's been in the fridge? Cold cream! 🥛", "Why did the cream go to the doctor? Because it was feeling a little whipped! 🥛"],
            
            # Eggs
            'egg': ["Why don't eggs tell jokes? They'd crack each other up! 🥚", "What do you call an egg that's been in the fridge too long? Hard-boiled! 🥚"],
            'eggs': ["Why don't eggs tell jokes? They'd crack each other up! 🥚", "What do you call an egg that's been in the fridge too long? Hard-boiled! 🥚"],
            
            # Grains & Bread
            'bread': ["Why did the baker go to the bank? To get some dough! 🥖", "What do you call bread that's been in the oven too long? Toast! 🍞"],
            'rice': ["What do you call rice that's been in the sun? Sun-dried rice! 🍚", "Why did the rice go to the doctor? Because it was feeling a little grainy! 🍚"],
            'quinoa': ["What do you call quinoa that's been in the gym? Buff quinoa! 🍚", "Why did the quinoa go to the party? Because it was a little nutty! 🍚"],
            'oat': ["What do you call oats that's been in the sun? Sun-dried oats! 🥣", "Why did the oats go to the doctor? Because they were feeling a little rolled! 🥣"],
            
            # Fruits
            'apple': ["What do you call an apple that's been in the sun? A sun-burned apple! 🍎", "Why did the apple go to the doctor? Because it was feeling a little bruised! 🍎"],
            'banana': ["What do you call a banana that's been in the sun? A sun-burned banana! 🍌", "Why did the banana go to the doctor? Because it was feeling a little yellow! 🍌"],
            'orange': ["What do you call an orange that's been in the sun? A sun-burned orange! 🍊", "Why did the orange go to the doctor? Because it was feeling a little peely! 🍊"],
            'lemon': ["What do you call a lemon that's been in the sun? A sun-burned lemon! 🍋", "Why did the lemon go to the doctor? Because it was feeling a little sour! 🍋"],
            'lime': ["What do you call a lime that's been in the sun? A sun-burned lime! 🍋", "Why did the lime go to the doctor? Because it was feeling a little green! 🍋"],
            'grape': ["Why did the grape stop in the middle of the road? Because it ran out of juice! 🍇", "What do you call a grape that's been in the sun? A raisin! 🍇"],
            
            # Herbs & Spices
            'basil': ["What do you call basil that's been in the sun? Sun-dried basil! 🌿", "Why did the basil go to the party? Because it was a little herby! 🌿"],
            'oregano': ["What do you call oregano that's been in the sun? Sun-dried oregano! 🌿", "Why did the oregano go to the doctor? Because it was feeling a little spicy! 🌿"],
            'thyme': ["What do you call thyme that's been in the sun? Sun-dried thyme! 🌿", "Why did the thyme go to the party? Because it was a little herby! 🌿"],
            'rosemary': ["What do you call rosemary that's been in the sun? Sun-dried rosemary! 🌿", "Why did the rosemary go to the doctor? Because it was feeling a little woody! 🌿"],
            'pepper': ["What do you call pepper that's been in the sun? Sun-dried pepper! 🌶️", "Why did the pepper go to the party? Because it was a little spicy! 🌶️"],
            'salt': ["What do you call salt that's been in the sun? Sun-dried salt! 🧂", "Why did the salt go to the doctor? Because it was feeling a little salty! 🧂"],
            
            # Nuts & Seeds
            'almond': ["What do you call an almond that's been in the sun? A sun-burned almond! 🥜", "Why did the almond go to the doctor? Because it was feeling a little nutty! 🥜"],
            'walnut': ["What do you call a walnut that's been in the sun? A sun-burned walnut! 🥜", "Why did the walnut go to the party? Because it was a little nutty! 🥜"],
            'peanut': ["What do you call a peanut that's been in the sun? A sun-burned peanut! 🥜", "Why did the peanut go to the doctor? Because it was feeling a little nutty! 🥜"],
            
            # Desserts & Sweeteners
            'chocolate': ["What do you call chocolate that's been in the sun? Melted chocolate! 🍫", "Why did the chocolate go to the doctor? Because it was feeling a little sweet! 🍫"],
            'sugar': ["What do you call sugar that's been in the sun? Sun-dried sugar! 🍯", "Why did the sugar go to the party? Because it was a little sweet! 🍯"],
            'honey': ["What do you call honey that's been in the sun? Sun-dried honey! 🍯", "Why did the honey go to the doctor? Because it was feeling a little sticky! 🍯"],
            
            # Beverages
            'coffee': ["Why did the coffee file a police report? It got mugged! ☕", "What do you call coffee that's been in the fridge? Cold brew! ☕"],
            'tea': ["What do you call tea that's been in the sun? Sun tea! ☕", "Why did the tea go to the doctor? Because it was feeling a little steeped! ☕"],
            'wine': ["What do you call wine that's been in the sun? Sun-dried wine! 🍷", "Why did the wine go to the party? Because it was a little grape! 🍷"],
            
            # General fallbacks
            'general': [
                "Why did the chef go to the doctor? Because he was feeling a little under the weather! 🌤️",
                "What do you call a can opener that doesn't work? A can't opener! 🥫",
                "Why did the grape stop in the middle of the road? Because it ran out of juice! 🍇",
                "What do you call a lazy kangaroo? A pouch potato! 🦘",
                "Why did the scarecrow win an award? Because he was outstanding in his field! 🌾",
                "What do you call a dinosaur that crashes his car? Tyrannosaurus wrecks! 🦖",
                "Why did the math book look so sad? Because it had too many problems! 📚",
                "What do you call a bear with no teeth? A gummy bear! 🐻",
                "Why did the cookie go to the doctor? Because it was feeling crumbly! 🍪",
                "What do you call a fish wearing a bowtie? So-fish-ticated! 🐟"
            ]
        }
        
        try:
            # Get form data
            diet = request.form.get('diet')
            intolerances = request.form.getlist('intolerances')
            difficulty = request.form.get('difficulty')
            max_time = request.form.get('max_time')
            
            # Convert difficulty to max_ready_time if provided
            max_ready_time = None
            if difficulty and difficulty != 'custom':
                difficulty_levels = {
                    'easy': 30,
                    'medium': 60,
                    'hard': 120
                }
                max_ready_time = difficulty_levels.get(difficulty.lower())
            elif max_time:
                max_ready_time = int(max_time)
            
            # Initialize API client
            api_client = SpoonacularClient()
            
            # Get random recipe
            result = api_client.get_random_recipes(
                number=1,
                diet=diet if diet != 'none' else None,
                intolerances=intolerances if intolerances else None,
                max_ready_time=max_ready_time
            )
            
            import re
            
            # Function to find the most relevant ingredient joke based on recipe ingredients
            def find_ingredient_joke(recipe_data):
                """Find the most relevant joke based on the actual ingredients in the recipe."""
                # Extract ingredients from the recipe data
                ingredients_text = ""
                
                # Check for ingredients in different possible locations
                if 'extendedIngredients' in recipe_data:
                    for ingredient in recipe_data['extendedIngredients']:
                        if 'name' in ingredient:
                            ingredients_text += " " + ingredient['name'].lower()
                        if 'original' in ingredient:
                            ingredients_text += " " + ingredient['original'].lower()
                
                # Also check title and summary for additional context
                title_lower = recipe_data.get('title', '').lower()
                summary_lower = recipe_data.get('summary', '').lower()
                combined_text = title_lower + " " + summary_lower + " " + ingredients_text
                
                # Priority order for ingredient matching (most specific first)
                ingredient_priorities = [
                    # Specific ingredients that should take priority
                    'salmon', 'tuna', 'shrimp', 'cod', 'pork', 'lamb', 'turkey',
                    'tomato', 'lettuce', 'carrot', 'onion', 'garlic', 'potato', 'broccoli', 'spinach',
                    'mushroom', 'apple', 'banana', 'orange', 'lemon', 'lime', 'grape',
                    'basil', 'oregano', 'thyme', 'rosemary', 'pepper', 'salt',
                    'almond', 'walnut', 'peanut', 'chocolate', 'honey',
                    'quinoa', 'oat', 'tea', 'wine',
                    # General categories
                    'pasta', 'spaghetti', 'noodle', 'penne',
                    'chicken', 'beef', 'fish', 'cheese', 'milk', 'butter', 'cream',
                    'egg', 'eggs', 'bread', 'rice', 'coffee', 'sugar'
                ]
                
                # Find the first matching ingredient
                for ingredient in ingredient_priorities:
                    if ingredient in combined_text:
                        if ingredient in ingredient_jokes:
                            return ingredient, ingredient_jokes[ingredient]
                
                # If no specific ingredient found, try broader categories
                if any(word in combined_text for word in ['pasta', 'spaghetti', 'noodle', 'penne', 'fettuccine', 'linguine']):
                    return 'pasta', ingredient_jokes['pasta']
                elif any(word in combined_text for word in ['chicken', 'poultry', 'breast', 'thigh', 'wing']):
                    return 'chicken', ingredient_jokes['chicken']
                elif any(word in combined_text for word in ['beef', 'steak', 'burger', 'meatball', 'roast']):
                    return 'beef', ingredient_jokes['beef']
                elif any(word in combined_text for word in ['fish', 'seafood']):
                    return 'fish', ingredient_jokes['salmon']  # Use salmon jokes as default fish
                elif any(word in combined_text for word in ['dessert', 'cake', 'cookie', 'pie', 'ice cream']):
                    return 'dessert', ingredient_jokes['chocolate']  # Use chocolate jokes as default dessert
                elif any(word in combined_text for word in ['bread', 'toast', 'sandwich', 'bun', 'roll']):
                    return 'bread', ingredient_jokes['bread']
                elif any(word in combined_text for word in ['cheese', 'cheddar', 'mozzarella', 'parmesan']):
                    return 'cheese', ingredient_jokes['cheese']
                elif any(word in combined_text for word in ['egg', 'omelette', 'scrambled']):
                    return 'eggs', ingredient_jokes['eggs']
                elif any(word in combined_text for word in ['vegetarian', 'vegan', 'salad', 'vegetable', 'tofu']):
                    return 'vegetarian', ingredient_jokes['tomato']  # Use tomato jokes as default vegetarian
                else:
                    return 'general', ingredient_jokes['general']
            
            # Parse the recipe data
            if result.get('recipes') and len(result['recipes']) > 0:
                recipe = result['recipes'][0]
                
                # Find the most relevant ingredient joke
                ingredient_name, ingredient_joke_list = find_ingredient_joke(recipe)
                selected_joke = random.choice(ingredient_joke_list)
                
                parsed_recipe = parse_recipe_details(recipe)
                
                return jsonify({
                    'success': True,
                    'recipe': parsed_recipe,
                    'dad_joke': selected_joke,
                    'ingredient_match': ingredient_name  # For debugging/fun - shows which ingredient matched
                })
            else:
                # If no recipe found, use a general joke
                selected_joke = random.choice(ingredient_jokes['general'])
                return jsonify({
                    'success': False,
                    'error': 'No random recipe found. Try adjusting your filters!',
                    'dad_joke': selected_joke
                })
                
        except Exception as e:
            logging.error(f"Error getting random recipe: {str(e)}")
            return jsonify({
                'success': False,
                'error': f'Error getting random recipe: {str(e)}',
                'dad_joke': random.choice(ingredient_jokes['general'])
            })

    return app

# For development only
if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5001) 

# Expose app for Gunicorn
app = create_app() 