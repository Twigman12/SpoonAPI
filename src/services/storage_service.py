"""
Storage Service - Handles storage location management
"""
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from sqlalchemy.orm import Session
from models import StorageLocation, InventoryItem, db


class StorageService:
    """Service class for storage location management operations"""
    
    def __init__(self, db_session=None):
        self.db = db_session or db.session
    
    def create_storage_location(self, user_id: int, location_data: Dict) -> Tuple[bool, str]:
        """
        Create a new storage location
        
        Args:
            user_id: ID of the user
            location_data: Dictionary containing location information
            
        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            # Validate required fields
            required_fields = ['name', 'location_type']
            for field in required_fields:
                if field not in location_data or not location_data[field]:
                    return False, f"Missing required field: {field}"
            
            # Check if location name already exists for this user
            existing_location = StorageLocation.query.filter_by(
                user_id=user_id,
                name=location_data['name']
            ).first()
            
            if existing_location:
                return False, "Storage location with this name already exists"
            
            # Create new storage location
            new_location = StorageLocation(
                user_id=user_id,
                name=location_data['name'],
                location_type=location_data['location_type'],
                description=location_data.get('description', '')
            )
            
            self.db.add(new_location)
            self.db.commit()
            
            return True, f"Storage location '{location_data['name']}' created successfully with ID: {new_location.id}"
            
        except Exception as e:
            self.db.rollback()
            return False, f"Error creating storage location: {str(e)}"
    
    def get_user_storage_locations(self, user_id: int) -> List[Dict]:
        """
        Get all storage locations for a user
        
        Args:
            user_id: ID of the user
            
        Returns:
            List of storage location dictionaries
        """
        try:
            locations = StorageLocation.query.filter_by(user_id=user_id).order_by(StorageLocation.name).all()
            
            result = []
            for location in locations:
                # Get item count for this location
                item_count = InventoryItem.query.filter_by(
                    storage_location_id=location.id,
                    user_id=user_id
                ).count()
                
                location_dict = {
                    'id': location.id,
                    'name': location.name,
                    'location_type': location.location_type,
                    'description': location.description,
                    'item_count': item_count,
                    'created_at': location.created_at.isoformat()
                }
                result.append(location_dict)
            
            return result
            
        except Exception as e:
            return []
    
    def get_location_inventory(self, user_id: int, location_id: int) -> List[Dict]:
        """
        Get all items in a specific storage location
        
        Args:
            user_id: ID of the user
            location_id: ID of the storage location
            
        Returns:
            List of inventory item dictionaries
        """
        try:
            # Verify location belongs to user
            location = StorageLocation.query.filter_by(
                id=location_id,
                user_id=user_id
            ).first()
            
            if not location:
                return []
            
            # Get items in this location
            items = InventoryItem.query.filter_by(
                storage_location_id=location_id,
                user_id=user_id
            ).order_by(InventoryItem.name).all()
            
            # Convert to dictionaries
            result = []
            for item in items:
                item_dict = self._item_to_dict(item)
                result.append(item_dict)
            
            return result
            
        except Exception as e:
            return []
    
    def update_storage_location(self, location_id: int, user_id: int, update_data: Dict) -> Tuple[bool, str]:
        """
        Update a storage location
        
        Args:
            location_id: ID of the location to update
            user_id: ID of the user (for security)
            update_data: Dictionary containing updated information
            
        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            location = StorageLocation.query.filter_by(
                id=location_id,
                user_id=user_id
            ).first()
            
            if not location:
                return False, "Storage location not found or doesn't belong to user"
            
            # Check if new name conflicts with existing location
            if 'name' in update_data and update_data['name'] != location.name:
                existing_location = StorageLocation.query.filter_by(
                    user_id=user_id,
                    name=update_data['name']
                ).first()
                
                if existing_location:
                    return False, "Storage location with this name already exists"
            
            # Update fields
            if 'name' in update_data:
                location.name = update_data['name']
            if 'location_type' in update_data:
                location.location_type = update_data['location_type']
            if 'description' in update_data:
                location.description = update_data['description']
            
            self.db.commit()
            return True, "Storage location updated successfully"
            
        except Exception as e:
            self.db.rollback()
            return False, f"Error updating storage location: {str(e)}"
    
    def delete_storage_location(self, location_id: int, user_id: int) -> Tuple[bool, str]:
        """
        Delete a storage location and move items to default location
        
        Args:
            location_id: ID of the location to delete
            user_id: ID of the user (for security)
            
        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            location = StorageLocation.query.filter_by(
                id=location_id,
                user_id=user_id
            ).first()
            
            if not location:
                return False, "Storage location not found or doesn't belong to user"
            
            # Check if there are items in this location
            item_count = InventoryItem.query.filter_by(
                storage_location_id=location_id,
                user_id=user_id
            ).count()
            
            if item_count > 0:
                # Find a default location to move items to
                default_location = StorageLocation.query.filter(
                    StorageLocation.user_id == user_id,
                    StorageLocation.id != location_id
                ).first()
                
                if not default_location:
                    return False, "Cannot delete storage location with items. Create another location first."
                
                # Move items to default location
                InventoryItem.query.filter_by(
                    storage_location_id=location_id,
                    user_id=user_id
                ).update({'storage_location_id': default_location.id})
            
            location_name = location.name
            self.db.delete(location)
            self.db.commit()
            
            return True, f"Storage location '{location_name}' deleted successfully"
            
        except Exception as e:
            self.db.rollback()
            return False, f"Error deleting storage location: {str(e)}"
    
    def get_default_storage_locations(self) -> List[Dict]:
        """
        Get list of default storage location types
        
        Returns:
            List of default storage location configurations
        """
        return [
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
    
    def create_default_storage_locations(self, user_id: int) -> Tuple[bool, str]:
        """
        Create default storage locations for a new user
        
        Args:
            user_id: ID of the user
            
        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            default_locations = self.get_default_storage_locations()
            created_count = 0
            
            for location_data in default_locations:
                # Check if location already exists
                existing = StorageLocation.query.filter_by(
                    user_id=user_id,
                    name=location_data['name']
                ).first()
                
                if not existing:
                    new_location = StorageLocation(
                        user_id=user_id,
                        name=location_data['name'],
                        location_type=location_data['location_type'],
                        description=location_data['description']
                    )
                    self.db.add(new_location)
                    created_count += 1
            
            self.db.commit()
            return True, f"Created {created_count} default storage locations"
            
        except Exception as e:
            self.db.rollback()
            return False, f"Error creating default storage locations: {str(e)}"
    
    def get_storage_location_stats(self, user_id: int) -> Dict:
        """
        Get statistics for all storage locations
        
        Args:
            user_id: ID of the user
            
        Returns:
            Dictionary with storage location statistics
        """
        try:
            locations = StorageLocation.query.filter_by(user_id=user_id).all()
            
            stats = {
                'total_locations': len(locations),
                'locations': []
            }
            
            for location in locations:
                # Get item count and categories for this location
                items = InventoryItem.query.filter_by(
                    storage_location_id=location.id,
                    user_id=user_id
                ).all()
                
                item_count = len(items)
                categories = list(set([item.category for item in items]))
                
                location_stats = {
                    'id': location.id,
                    'name': location.name,
                    'location_type': location.location_type,
                    'item_count': item_count,
                    'categories': categories
                }
                stats['locations'].append(location_stats)
            
            return stats
            
        except Exception as e:
            return {
                'total_locations': 0,
                'locations': []
            }
    
    def _item_to_dict(self, item: InventoryItem) -> Dict:
        """Convert InventoryItem to dictionary with computed fields"""
        from datetime import date
        
        today = date.today()
        days_until_expiry = None
        expiry_status = "N/A"
        
        if item.expiry_date:
            days_until_expiry = (item.expiry_date - today).days
            if days_until_expiry < 0:
                expiry_status = f"Expired {abs(days_until_expiry)} days ago"
            elif days_until_expiry == 0:
                expiry_status = "Expires today"
            elif days_until_expiry == 1:
                expiry_status = "Expires tomorrow"
            else:
                expiry_status = f"Expires in {days_until_expiry} days"
        
        return {
            'id': item.id,
            'name': item.name,
            'category': item.category,
            'quantity': item.quantity,
            'unit': item.unit,
            'expiry_date': item.expiry_date.isoformat() if item.expiry_date else None,
            'expiry_status': expiry_status,
            'days_until_expiry': days_until_expiry,
            'notes': item.notes,
            'storage_location_id': item.storage_location_id,
            'storage_location_name': item.storage_location.name if item.storage_location else None,
            'created_at': item.created_at.isoformat(),
            'updated_at': item.updated_at.isoformat()
        }
