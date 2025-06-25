import os
from dotenv import load_dotenv

from flask import Flask, render_template, request, jsonify
from api_client import SpoonacularClient
from data_parser import parse_recipe_search_results, parse_recipe_details
from news_parser import NewsParser

load_dotenv()

app = Flask(__name__)
client = SpoonacularClient()

news_api_key = os.getenv("NEWS_API_KEY")
if not news_api_key:
    print("Warning: NEWS_API_KEY not found. News features will be disabled.")
    news_parser = None
else:
    news_parser = NewsParser(api_key=news_api_key)

@app.route('/')
def index():
    """Render the main search page."""
    return render_template('index.html',
                         diets=SpoonacularClient.VALID_DIETS,
                         intolerances=SpoonacularClient.VALID_INTOLERANCES,
                         difficulty_levels=SpoonacularClient.DIFFICULTY_LEVELS)

@app.route('/search', methods=['POST'])
def search():
    """Handle recipe search with filters."""
    try:
        # Get search parameters from form
        data = request.form
        query = data.get('query', '').strip()
        
        if not query:
            return jsonify({'error': 'Please enter a search term'}), 400
        
        # Build filters
        filters = {}
        
        # Diet filter
        diet = data.get('diet')
        if diet and diet != 'none':
            filters['diet'] = diet
        
        # Intolerances filter
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
                try:
                    filters['max_ready_time'] = int(max_time)
                except ValueError:
                    return jsonify({'error': 'Invalid cooking time'}), 400
        
        # Calorie range
        min_calories = data.get('min_calories')
        if min_calories:
            try:
                filters['min_calories'] = int(min_calories)
            except ValueError:
                return jsonify({'error': 'Invalid minimum calories'}), 400
                
        max_calories = data.get('max_calories')
        if max_calories:
            try:
                filters['max_calories'] = int(max_calories)
            except ValueError:
                return jsonify({'error': 'Invalid maximum calories'}), 400
        
        # Search recipes
        results = client.search_recipes(query, number=9, **filters)
        recipes = parse_recipe_search_results(results)
        
        return jsonify({'recipes': recipes})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/recipe/<int:recipe_id>')
def recipe_details(recipe_id):
    """Get detailed information for a specific recipe."""
    try:
        recipe_data = client.get_recipe_information(recipe_id)
        recipe = parse_recipe_details(recipe_data)

        related_news = []
        if news_parser:
            # Fetch news related to the recipe title
            query = recipe.get('title', 'food')
            related_news = news_parser.fetch_food_news(query=query, page_size=3)

        return render_template('recipe.html', recipe=recipe, related_news=related_news)
    except Exception as e:
        return render_template('error.html', error=str(e))

@app.route('/food-culture')
def food_culture():
    """Display popular recipes mentioned in Guardian articles."""
    recipes = []
    source_articles = []
    
    if news_parser:
        try:
            # Fetch articles about popular recipes from The Guardian
            articles = news_parser.fetch_popular_recipe_articles(page_size=15)
            source_articles = articles[:3]  # Keep a few articles for reference
            
            # Extract recipe names from the articles
            recipe_names = news_parser.extract_recipe_names_from_articles(articles)
            
            # For each extracted recipe name, search for actual recipes using Spoonacular
            for recipe_name in recipe_names[:6]:  # Limit to 6 recipes for display
                try:
                    search_results = client.search_recipes(recipe_name, number=1)
                    if search_results.get("results"):
                        recipe_data = search_results["results"][0]
                        # Get full recipe details
                        detailed_recipe = client.get_recipe_information(recipe_data["id"])
                        parsed_recipe = parse_recipe_details(detailed_recipe)
                        recipes.append(parsed_recipe)
                except Exception as e:
                    print(f"Error fetching recipe for '{recipe_name}': {e}")
                    continue
            
            # If we don't have enough recipes, add some popular fallback searches
            if len(recipes) < 3:
                fallback_searches = ["pasta", "chicken", "chocolate cake"]
                for fallback in fallback_searches:
                    if len(recipes) >= 6:
                        break
                    try:
                        search_results = client.search_recipes(fallback, number=1)
                        if search_results.get("results"):
                            recipe_data = search_results["results"][0]
                            detailed_recipe = client.get_recipe_information(recipe_data["id"])
                            parsed_recipe = parse_recipe_details(detailed_recipe)
                            recipes.append(parsed_recipe)
                    except Exception as e:
                        continue
                        
        except Exception as e:
            print(f"Error in popular recipes route: {e}")
    
    return render_template('popular_recipes.html', recipes=recipes, source_articles=source_articles)

if __name__ == '__main__':
    app.run(debug=True) 