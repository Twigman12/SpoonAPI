#!/usr/bin/env python3
"""
Quick test script to verify inventory system is working
"""

import requests
import json

def test_inventory_api():
    """Test the inventory API endpoints"""
    base_url = "http://localhost:5001"
    
    print("🧪 Testing Inventory API Endpoints")
    print("=" * 40)
    
    # Test 1: Get storage locations (should work without auth for now)
    try:
        response = requests.get(f"{base_url}/api/storage/locations")
        print(f"1. Storage Locations API: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Response: {data}")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"   Error: {str(e)}")
    
    # Test 2: Get inventory items
    try:
        response = requests.get(f"{base_url}/api/inventory/items")
        print(f"2. Inventory Items API: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Response: {data}")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"   Error: {str(e)}")
    
    # Test 3: Check if kitchen inventory page loads
    try:
        response = requests.get(f"{base_url}/kitchen-inventory")
        print(f"3. Kitchen Inventory Page: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ Page loads successfully")
        else:
            print(f"   Error: {response.text[:200]}...")
    except Exception as e:
        print(f"   Error: {str(e)}")

if __name__ == '__main__':
    test_inventory_api()
