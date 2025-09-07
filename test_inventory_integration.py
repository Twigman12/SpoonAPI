#!/usr/bin/env python3
"""
Test Script for Inventory Management System Integration
This script tests the basic functionality of the inventory system.
"""

import os
import sys
from datetime import datetime, date, timedelta

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.app import create_app
from src.models import db, User, StorageLocation, InventoryItem, InventoryHistory
from src.services.inventory_service import InventoryService
from src.services.storage_service import StorageService

def test_inventory_system():
    """Test the inventory management system"""
    app = create_app()
    
    with app.app_context():
        print("🧪 Testing Inventory Management System")
        print("=" * 50)
        
        try:
            # Test 1: Create test user if not exists
            print("\n1. Testing User Creation...")
            test_user = User.query.filter_by(username='test_inventory_user').first()
            if not test_user:
                test_user = User(
                    username='test_inventory_user',
                    email='test@inventory.com',
                    password_hash='test_hash'
                )
                db.session.add(test_user)
                db.session.commit()
                print("✅ Test user created")
            else:
                print("✅ Test user already exists")
            
            # Test 2: Create storage locations
            print("\n2. Testing Storage Location Creation...")
            storage_service = StorageService()
            
            # Create test storage location
            location_data = {
                'name': 'Test Refrigerator',
                'location_type': 'fridge',
                'description': 'Test refrigerator for testing'
            }
            
            success, message = storage_service.create_storage_location(test_user.id, location_data)
            if success:
                print("✅ Storage location created successfully")
                
                # Get the created location
                locations = storage_service.get_user_storage_locations(test_user.id)
                test_location = locations[0] if locations else None
                
                if test_location:
                    print(f"   Location ID: {test_location['id']}")
                    print(f"   Location Name: {test_location['name']}")
                else:
                    print("❌ Failed to retrieve created location")
                    return False
            else:
                print(f"❌ Failed to create storage location: {message}")
                return False
            
            # Test 3: Add inventory items
            print("\n3. Testing Inventory Item Creation...")
            inventory_service = InventoryService()
            
            # Test item data
            test_items = [
                {
                    'name': 'Test Tomatoes',
                    'category': 'produce',
                    'quantity': 5,
                    'unit': 'pcs',
                    'expiry_date': (date.today() + timedelta(days=7)).isoformat(),
                    'storage_location_id': test_location['id'],
                    'notes': 'Test tomatoes for testing'
                },
                {
                    'name': 'Test Milk',
                    'category': 'dairy',
                    'quantity': 2,
                    'unit': 'l',
                    'expiry_date': (date.today() + timedelta(days=3)).isoformat(),
                    'storage_location_id': test_location['id'],
                    'notes': 'Test milk for testing'
                }
            ]
            
            for item_data in test_items:
                success, message = inventory_service.add_item(test_user.id, item_data)
                if success:
                    print(f"✅ Added item: {item_data['name']}")
                else:
                    print(f"❌ Failed to add item {item_data['name']}: {message}")
                    return False
            
            # Test 4: Search inventory items
            print("\n4. Testing Inventory Search...")
            items = inventory_service.search_items(test_user.id, {})
            print(f"✅ Found {len(items)} items in inventory")
            
            for item in items:
                print(f"   - {item['name']}: {item['quantity']} {item['unit']} ({item['expiry_status']})")
            
            # Test 5: Get inventory stats
            print("\n5. Testing Inventory Statistics...")
            stats = inventory_service.get_inventory_stats(test_user.id)
            print(f"✅ Inventory Stats:")
            print(f"   - Total Items: {stats['total_items']}")
            print(f"   - Expiring Soon: {stats['expiring_soon']}")
            print(f"   - Expired: {stats['expired']}")
            print(f"   - Low Stock: {stats['low_stock']}")
            
            # Test 6: Update item quantity
            print("\n6. Testing Item Quantity Update...")
            if items:
                first_item = items[0]
                success, message = inventory_service.update_item_quantity(
                    first_item['id'], 
                    first_item['quantity'] - 1, 
                    test_user.id,
                    "Used for testing"
                )
                if success:
                    print(f"✅ Updated quantity for {first_item['name']}")
                else:
                    print(f"❌ Failed to update quantity: {message}")
                    return False
            
            # Test 7: Get expiring items
            print("\n7. Testing Expiring Items...")
            expiring_items = inventory_service.get_expiring_items(test_user.id, 7)
            print(f"✅ Found {len(expiring_items)} items expiring within 7 days")
            
            # Test 8: Clean up test data
            print("\n8. Cleaning up test data...")
            
            # Delete test items
            InventoryItem.query.filter_by(user_id=test_user.id).delete()
            
            # Delete test storage location
            StorageLocation.query.filter_by(user_id=test_user.id).delete()
            
            # Delete test user
            User.query.filter_by(id=test_user.id).delete()
            
            db.session.commit()
            print("✅ Test data cleaned up")
            
            print("\n🎉 All tests passed successfully!")
            return True
            
        except Exception as e:
            print(f"\n❌ Test failed with error: {str(e)}")
            db.session.rollback()
            return False

def test_api_endpoints():
    """Test API endpoints (requires running Flask app)"""
    print("\n🌐 API Endpoint Tests")
    print("=" * 30)
    print("Note: These tests require the Flask app to be running")
    print("You can test these endpoints manually:")
    print("1. GET /api/inventory/items")
    print("2. POST /api/inventory/items")
    print("3. GET /api/storage/locations")
    print("4. POST /api/storage/locations")
    print("5. GET /api/inventory/stats")

if __name__ == '__main__':
    print("SpoonAPI Inventory Management System - Integration Test")
    print("=" * 60)
    
    # Run database tests
    success = test_inventory_system()
    
    # Show API endpoint information
    test_api_endpoints()
    
    if success:
        print("\n✅ Integration test completed successfully!")
        print("\nNext steps:")
        print("1. Run: python migrate_inventory.py")
        print("2. Start your Flask application")
        print("3. Visit /kitchen-inventory to test the UI")
        sys.exit(0)
    else:
        print("\n❌ Integration test failed!")
        sys.exit(1)
