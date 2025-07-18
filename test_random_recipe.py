#!/usr/bin/env python3
"""
Test script for the random recipe functionality
"""

import os
import sys
import requests
import json

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_random_recipe():
    """Test the random recipe endpoint"""
    
    # Test data
    test_data = {
        'diet': 'none',
        'difficulty': 'easy',
        'intolerances': []
    }
    
    try:
        # Make request to the random recipe endpoint
        response = requests.post('http://127.0.0.1:5001/random-recipe', data=test_data)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Random recipe endpoint is working!")
            print(f"🎲 Dad Joke: {data.get('dad_joke', 'No joke found')}")
            
            if data.get('success') and data.get('recipe'):
                recipe = data['recipe']
                print(f"🍳 Recipe: {recipe.get('title', 'No title')}")
                print(f"⏱️  Time: {recipe.get('ready_in_minutes', 'Unknown')} minutes")
                print(f"👥 Servings: {recipe.get('servings', 'Unknown')}")
            else:
                print(f"❌ Error: {data.get('error', 'Unknown error')}")
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to the server. Make sure the Flask app is running on port 5001.")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    print("🧪 Testing Random Recipe Feature...")
    test_random_recipe() 