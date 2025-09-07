#!/usr/bin/env python3
"""
Database Migration Script for Inventory Management System
This script creates the new inventory-related tables in the database.
"""

import os
import sys
from datetime import datetime

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.app import create_app
from src.models import db, StorageLocation, InventoryItem, InventoryHistory, User

def migrate_database():
    """Create new inventory tables in the database"""
    app = create_app()
    
    with app.app_context():
        print("Starting database migration for inventory management system...")
        
        try:
            # Create all tables (this will only create new ones)
            db.create_all()
            print("✅ Database tables created successfully!")
            
            # Check if we have any users
            user_count = User.query.count()
            print(f"📊 Found {user_count} users in the database")
            
            if user_count > 0:
                # Create default storage locations for existing users
                users = User.query.all()
                created_locations = 0
                
                for user in users:
                    # Check if user already has storage locations
                    existing_locations = StorageLocation.query.filter_by(user_id=user.id).count()
                    
                    if existing_locations == 0:
                        # Create default storage locations for this user
                        default_locations = [
                            {
                                'name': 'Refrigerator',
                                'location_type': 'fridge',
                                'description': 'Main refrigerator for fresh items'
                            },
                            {
                                'name': 'Freezer',
                                'location_type': 'freezer',
                                'description': 'Freezer for frozen items'
                            },
                            {
                                'name': 'Pantry',
                                'location_type': 'pantry',
                                'description': 'Pantry for dry goods and non-perishables'
                            },
                            {
                                'name': 'Spice Rack',
                                'location_type': 'spice_rack',
                                'description': 'Spice rack for herbs and spices'
                            },
                            {
                                'name': 'Counter',
                                'location_type': 'counter',
                                'description': 'Kitchen counter for frequently used items'
                            }
                        ]
                        
                        for location_data in default_locations:
                            location = StorageLocation(
                                user_id=user.id,
                                name=location_data['name'],
                                location_type=location_data['location_type'],
                                description=location_data['description']
                            )
                            db.session.add(location)
                            created_locations += 1
                
                if created_locations > 0:
                    db.session.commit()
                    print(f"✅ Created {created_locations} default storage locations for existing users")
                else:
                    print("ℹ️  All users already have storage locations")
            
            # Display summary
            storage_count = StorageLocation.query.count()
            inventory_count = InventoryItem.query.count()
            history_count = InventoryHistory.query.count()
            
            print("\n📈 Migration Summary:")
            print(f"   • Storage Locations: {storage_count}")
            print(f"   • Inventory Items: {inventory_count}")
            print(f"   • Inventory History: {history_count}")
            
            print("\n🎉 Migration completed successfully!")
            print("\nNext steps:")
            print("1. Start your Flask application")
            print("2. Visit /kitchen-inventory to start managing your inventory")
            print("3. Add items to your storage locations")
            
        except Exception as e:
            print(f"❌ Migration failed: {str(e)}")
            db.session.rollback()
            return False
    
    return True

if __name__ == '__main__':
    print("SpoonAPI Inventory Management System - Database Migration")
    print("=" * 60)
    
    success = migrate_database()
    
    if success:
        print("\n✅ Migration completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Migration failed!")
        sys.exit(1)
