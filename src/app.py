from flask import Flask, render_template, request, jsonify
from api_client import SpoonacularClient
from data_parser import parse_recipe_search_results, parse_recipe_details

app = Flask(__name__)
client = SpoonacularClient()

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
        return render_template('recipe.html', recipe=recipe)
    except Exception as e:
        return render_template('error.html', error=str(e))

if __name__ == '__main__':
    app.run(debug=True) 