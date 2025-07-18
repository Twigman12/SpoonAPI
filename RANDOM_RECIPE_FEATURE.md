# 🎲 Random Recipe Feature

## Overview

The Random Recipe feature adds a fun and engaging way to discover new recipes with a retro dad joke twist! When users click the "Surprise Me!" button, they get a random recipe along with a classic dad joke.

## Features

### 🎯 Core Functionality
- **Random Recipe Selection**: Gets a random recipe from the Spoonacular API
- **Filter Support**: Respects user's diet preferences, intolerances, and cooking time filters
- **Dad Joke Integration**: Displays a random retro dad joke with each recipe
- **Visual Enhancement**: Special styling for random recipe cards with animations

### 🎨 User Experience
- **Dice Button**: Compact dice icon button next to the search input
- **Animated Elements**: Pulsing dad joke alerts
- **Retro Styling**: Special CSS classes for random recipe cards
- **Responsive Design**: Works on all device sizes

### 🔧 Technical Implementation

#### Backend (Flask)
- **New Route**: `/random-recipe` (POST)
- **API Integration**: Uses Spoonacular's `/recipes/random` endpoint
- **Filter Processing**: Converts form data to API parameters
- **Error Handling**: Graceful error handling with fallback jokes

#### Frontend (JavaScript)
- **AJAX Requests**: Fetches random recipes without page reload
- **Dynamic Display**: Updates UI with recipe and joke
- **Loading States**: Shows spinner during API calls
- **Error Handling**: Displays user-friendly error messages

#### Styling (CSS)
- **Custom Classes**: `.random-recipe-card`, `.dad-joke-alert`, `.surprise-me-btn`
- **Animations**: Pulse, bounce, and gradient effects
- **Retro Theme**: Consistent with the overall design

## Recipe-Relevant Dad Jokes

The feature includes recipe-relevant dad jokes organized by food categories:

### 🍝 Pasta Jokes
- "What do you call a fake noodle? An impasta! 🍝"
- "Why did the spaghetti go to the doctor? Because it was feeling a little saucy! 🍝"
- "What do you call pasta that's been in the sun too long? Sun-dried tomatoes! 🍅"

### 🐔 Chicken Jokes
- "Why did the chicken go to the doctor? Because it was feeling a little under the weather! 🌤️"
- "What do you call a chicken that crosses the road? A road runner! 🐔"
- "Why did the chicken join a band? Because it had the drumsticks! 🥁"

### 🐄 Beef Jokes
- "What do you call a cow that plays hide and seek? A moo-ving target! 🐄"
- "Why did the cow go to the gym? To get some beef-cake! 💪"
- "What do you call a sleeping bull? A bulldozer! 🐂"

### 🐟 Fish Jokes
- "What do you call a fish wearing a bowtie? So-fish-ticated! 🐟"
- "Why did the fish blush? Because it saw the ocean's bottom! 🐠"
- "What do you call a fish that's good at math? A calcu-lator! 🧮"

### 🥬 Vegetarian Jokes
- "Why did the tomato turn red? Because it saw the salad dressing! 🍅"
- "Why did the lettuce win the race? Because it was ahead! 🥬"
- "What do you call a lazy vegetable? A couch potato! 🥔"

### 🍰 Dessert Jokes
- "Why did the cookie go to the doctor? Because it was feeling crumbly! 🍪"
- "What do you call a bear with no teeth? A gummy bear! 🐻"
- "Why did the cake go to the doctor? Because it was feeling a little flaky! 🍰"

### 🥖 Bread Jokes
- "Why did the baker go to the bank? To get some dough! 🥖"
- "What do you call bread that's been in the oven too long? Toast! 🍞"
- "Why did the bread go to the doctor? Because it was feeling a little crusty! 🥖"

### 🧀 Cheese Jokes
- "What do you call cheese that isn't yours? Nacho cheese! 🧀"
- "Why did the cheese go to the doctor? Because it was feeling a little blue! 🧀"
- "What do you call cheese that's been in the sun? Melted! 🧀"

### 🥚 Egg Jokes
- "Why don't eggs tell jokes? They'd crack each other up! 🥚"
- "What do you call an egg that's been in the fridge too long? Hard-boiled! 🥚"
- "Why did the egg go to the doctor? Because it was feeling a little scrambled! 🍳"

### 🍄 Mushroom Jokes
- "Why did the mushroom go to the party? Because he was a fungi! 🍄"
- "What do you call a mushroom that's been in the rain? A wet one! 🍄"
- "Why did the mushroom get invited to all the parties? Because he was such a fungi! 🍄"

### ☕ Coffee Jokes
- "Why did the coffee file a police report? It got mugged! ☕"
- "What do you call coffee that's been in the fridge? Cold brew! ☕"
- "Why did the coffee go to the doctor? Because it was feeling a little bitter! ☕"

### 🌟 General Jokes
- "Why did the chef go to the doctor? Because he was feeling a little under the weather! 🌤️"
- "What do you call a can opener that doesn't work? A can't opener! 🥫"
- "Why did the grape stop in the middle of the road? Because it ran out of juice! 🍇"
- "What do you call a lazy kangaroo? A pouch potato! 🦘"
- "Why did the scarecrow win an award? Because he was outstanding in his field! 🌾"
- "What do you call a dinosaur that crashes his car? Tyrannosaurus wrecks! 🦖"
- "Why did the math book look so sad? Because it had too many problems! 📚"

## API Integration

### Spoonacular API Endpoint
- **Endpoint**: `/recipes/random`
- **Method**: GET
- **Parameters**:
  - `number`: Number of recipes to return (default: 1)
  - `tags`: Recipe tags for filtering
  - `diet`: Dietary restrictions
  - `intolerances`: Food intolerances
  - `maxReadyTime`: Maximum cooking time

### Response Format
```json
{
  "success": true,
  "recipe": {
    "id": 12345,
    "title": "Recipe Title",
    "ready_in_minutes": 30,
    "servings": 4,
    "image": "image_url",
    "summary": "Recipe description"
  },
  "dad_joke": "Why did the chef go to the doctor? Because he was feeling a little under the weather! 🌤️"
}
```

## Usage

### For Users
1. Navigate to the home page
2. Optionally set filters (diet, intolerances, cooking time)
3. Click the dice button (🎲 icon) next to the search bar
4. Enjoy the recipe-relevant dad joke and discover a new recipe!

### For Developers
1. The feature is automatically available when the app is running
2. Test with the provided test script: `python test_random_recipe.py`
3. Customize dad jokes by editing the `dad_jokes` list in `src/app.py`

## Files Modified

- `src/api_client.py`: Added `get_random_recipes()` method
- `src/app.py`: Added `/random-recipe` route and dad joke logic
- `src/templates/index.html`: Updated JavaScript for random recipe functionality
- `src/static/css/style.css`: Added styling for random recipe elements
- `test_random_recipe.py`: Test script for the feature

## Future Enhancements

- **Joke Categories**: Organize jokes by food type or theme
- **User Favorites**: Allow users to save favorite random recipes
- **Social Sharing**: Share random recipes with dad jokes on social media
- **Joke Voting**: Let users rate and vote on dad jokes
- **Seasonal Jokes**: Rotate jokes based on holidays or seasons

## Testing

Run the test script to verify the feature works:
```bash
python test_random_recipe.py
```

Make sure the Flask app is running on port 5001 before testing. 