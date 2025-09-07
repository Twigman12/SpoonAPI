"""
Inventory Service - Handles all inventory-related business logic
"""
from datetime import datetime, date, timedelta
from typing import List, Dict, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from models import InventoryItem, StorageLocation, InventoryHistory, db


class InventoryService:
    """Service class for inventory management operations"""
    
    def __init__(self, db_session=None):
        self.db = db_session or db.session
    
    def add_item(self, user_id: int, item_data: Dict) -> Tuple[bool, str]:
        """
        Add a new item to inventory
        
        Args:
            user_id: ID of the user
            item_data: Dictionary containing item information
            
        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            # Validate required fields
            required_fields = ['name', 'category', 'quantity', 'unit', 'storage_location_id']
            for field in required_fields:
                if field not in item_data or not item_data[field]:
                    return False, f"Missing required field: {field}"
            
            # Check if storage location belongs to user
            storage_location = StorageLocation.query.filter_by(
                id=item_data['storage_location_id'], 
                user_id=user_id
            ).first()
            
            if not storage_location:
                return False, "Storage location not found or doesn't belong to user"
            
            # Check if item already exists in this location
            existing_item = InventoryItem.query.filter_by(
                user_id=user_id,
                storage_location_id=item_data['storage_location_id'],
                name=item_data['name']
            ).first()
            
            if existing_item:
                # Update existing item quantity
                old_quantity = existing_item.quantity
                existing_item.quantity += float(item_data['quantity'])
                existing_item.updated_at = datetime.utcnow()
                
                # Update other fields if provided
                if 'expiry_date' in item_data and item_data['expiry_date']:
                    existing_item.expiry_date = datetime.strptime(item_data['expiry_date'], '%Y-%m-%d').date()
                if 'notes' in item_data:
                    existing_item.notes = item_data['notes']
                
                # Record history
                self._record_history(
                    user_id=user_id,
                    item_id=existing_item.id,
                    action='add',
                    quantity_change=float(item_data['quantity']),
                    notes=f"Added {item_data['quantity']} {item_data['unit']} to existing item"
                )
                
                self.db.commit()
                return True, f"Updated existing item. New quantity: {existing_item.quantity} {existing_item.unit}"
            
            # Create new item
            new_item = InventoryItem(
                user_id=user_id,
                storage_location_id=item_data['storage_location_id'],
                name=item_data['name'],
                category=item_data['category'],
                quantity=float(item_data['quantity']),
                unit=item_data['unit'],
                expiry_date=datetime.strptime(item_data['expiry_date'], '%Y-%m-%d').date() if item_data.get('expiry_date') else None,
                notes=item_data.get('notes', ''),
                recipe_ingredient_id=item_data.get('recipe_ingredient_id')
            )
            
            self.db.add(new_item)
            self.db.flush()  # Get the ID
            
            # Record history
            self._record_history(
                user_id=user_id,
                item_id=new_item.id,
                action='add',
                quantity_change=float(item_data['quantity']),
                notes=f"Added new item: {item_data['name']}"
            )
            
            self.db.commit()
            return True, f"Item added successfully with ID: {new_item.id}"
            
        except Exception as e:
            self.db.rollback()
            return False, f"Error adding item: {str(e)}"
    
    def update_item_quantity(self, item_id: int, new_quantity: float, user_id: int, notes: str = None) -> Tuple[bool, str]:
        """
        Update item quantity with history tracking
        
        Args:
            item_id: ID of the item to update
            new_quantity: New quantity value
            user_id: ID of the user (for security)
            notes: Optional notes for the change
            
        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            item = InventoryItem.query.filter_by(id=item_id, user_id=user_id).first()
            
            if not item:
                return False, "Item not found or doesn't belong to user"
            
            old_quantity = item.quantity
            quantity_change = new_quantity - old_quantity
            
            item.quantity = new_quantity
            item.updated_at = datetime.utcnow()
            
            # Record history
            action = 'use' if quantity_change < 0 else 'add'
            self._record_history(
                user_id=user_id,
                item_id=item_id,
                action=action,
                quantity_change=quantity_change,
                notes=notes or f"Quantity updated from {old_quantity} to {new_quantity}"
            )
            
            self.db.commit()
            return True, f"Quantity updated successfully"
            
        except Exception as e:
            self.db.rollback()
            return False, f"Error updating quantity: {str(e)}"
    
    def delete_item(self, item_id: int, user_id: int) -> Tuple[bool, str]:
        """
        Delete an item from inventory
        
        Args:
            item_id: ID of the item to delete
            user_id: ID of the user (for security)
            
        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            item = InventoryItem.query.filter_by(id=item_id, user_id=user_id).first()
            
            if not item:
                return False, "Item not found or doesn't belong to user"
            
            item_name = item.name
            
            # Record history before deletion
            self._record_history(
                user_id=user_id,
                item_id=item_id,
                action='delete',
                quantity_change=-item.quantity,
                notes=f"Item deleted: {item_name}"
            )
            
            self.db.delete(item)
            self.db.commit()
            return True, f"Item '{item_name}' deleted successfully"
            
        except Exception as e:
            self.db.rollback()
            return False, f"Error deleting item: {str(e)}"
    
    def search_items(self, user_id: int, filters: Dict) -> List[Dict]:
        """
        Search items with multiple filters
        
        Args:
            user_id: ID of the user
            filters: Dictionary containing search filters
            
        Returns:
            List of item dictionaries
        """
        try:
            query = InventoryItem.query.filter_by(user_id=user_id)
            
            # Apply filters
            if filters.get('name'):
                query = query.filter(InventoryItem.name.ilike(f"%{filters['name']}%"))
            
            if filters.get('category'):
                query = query.filter(InventoryItem.category == filters['category'])
            
            if filters.get('storage_location_id'):
                query = query.filter(InventoryItem.storage_location_id == filters['storage_location_id'])
            
            if filters.get('expiry_filter'):
                today = date.today()
                if filters['expiry_filter'] == 'expiring_soon':
                    query = query.filter(
                        and_(
                            InventoryItem.expiry_date.isnot(None),
                            InventoryItem.expiry_date <= today + timedelta(days=7),
                            InventoryItem.expiry_date >= today
                        )
                    )
                elif filters['expiry_filter'] == 'expired':
                    query = query.filter(InventoryItem.expiry_date < today)
                elif filters['expiry_filter'] == 'good':
                    query = query.filter(
                        or_(
                            InventoryItem.expiry_date.is_(None),
                            InventoryItem.expiry_date > today + timedelta(days=7)
                        )
                    )
            
            # Order by name
            items = query.order_by(InventoryItem.name).all()
            
            # Convert to dictionaries with additional computed fields
            result = []
            for item in items:
                item_dict = self._item_to_dict(item)
                result.append(item_dict)
            
            return result
            
        except Exception as e:
            return []
    
    def get_expiring_items(self, user_id: int, days_ahead: int = 7) -> List[Dict]:
        """
        Get items expiring within specified days
        
        Args:
            user_id: ID of the user
            days_ahead: Number of days to look ahead
            
        Returns:
            List of expiring items
        """
        try:
            today = date.today()
            expiry_date = today + timedelta(days=days_ahead)
            
            items = InventoryItem.query.filter(
                and_(
                    InventoryItem.user_id == user_id,
                    InventoryItem.expiry_date.isnot(None),
                    InventoryItem.expiry_date <= expiry_date,
                    InventoryItem.expiry_date >= today
                )
            ).order_by(InventoryItem.expiry_date).all()
            
            return [self._item_to_dict(item) for item in items]
            
        except Exception as e:
            return []
    
    def get_low_stock_items(self, user_id: int, threshold: float = 1.0) -> List[Dict]:
        """
        Get items with low stock
        
        Args:
            user_id: ID of the user
            threshold: Stock threshold (items with quantity <= threshold)
            
        Returns:
            List of low stock items
        """
        try:
            items = InventoryItem.query.filter(
                and_(
                    InventoryItem.user_id == user_id,
                    InventoryItem.quantity <= threshold
                )
            ).order_by(InventoryItem.quantity).all()
            
            return [self._item_to_dict(item) for item in items]
            
        except Exception as e:
            return []
    
    def get_inventory_stats(self, user_id: int) -> Dict:
        """
        Get inventory statistics for user
        
        Args:
            user_id: ID of the user
            
        Returns:
            Dictionary with inventory statistics
        """
        try:
            total_items = InventoryItem.query.filter_by(user_id=user_id).count()
            
            # Count expiring soon (within 7 days)
            today = date.today()
            expiring_soon = InventoryItem.query.filter(
                and_(
                    InventoryItem.user_id == user_id,
                    InventoryItem.expiry_date.isnot(None),
                    InventoryItem.expiry_date <= today + timedelta(days=7),
                    InventoryItem.expiry_date >= today
                )
            ).count()
            
            # Count expired items
            expired = InventoryItem.query.filter(
                and_(
                    InventoryItem.user_id == user_id,
                    InventoryItem.expiry_date.isnot(None),
                    InventoryItem.expiry_date < today
                )
            ).count()
            
            # Count low stock items
            low_stock = InventoryItem.query.filter(
                and_(
                    InventoryItem.user_id == user_id,
                    InventoryItem.quantity <= 1.0
                )
            ).count()
            
            return {
                'total_items': total_items,
                'expiring_soon': expiring_soon,
                'expired': expired,
                'low_stock': low_stock
            }
            
        except Exception as e:
            return {
                'total_items': 0,
                'expiring_soon': 0,
                'expired': 0,
                'low_stock': 0
            }
    
    def use_item_for_recipe(self, user_id: int, recipe_ingredients: List[Dict]) -> Tuple[bool, str, List[Dict]]:
        """
        Deduct items when cooking a recipe
        
        Args:
            user_id: ID of the user
            recipe_ingredients: List of ingredients needed for recipe
            
        Returns:
            Tuple of (success: bool, message: str, missing_ingredients: List[Dict])
        """
        try:
            missing_ingredients = []
            used_items = []
            
            for ingredient in recipe_ingredients:
                # Find matching inventory item
                item = InventoryItem.query.filter(
                    and_(
                        InventoryItem.user_id == user_id,
                        InventoryItem.name.ilike(f"%{ingredient['name']}%"),
                        InventoryItem.quantity >= ingredient['amount']
                    )
                ).first()
                
                if item:
                    # Use the ingredient
                    old_quantity = item.quantity
                    item.quantity -= ingredient['amount']
                    item.updated_at = datetime.utcnow()
                    
                    # Record history
                    self._record_history(
                        user_id=user_id,
                        item_id=item.id,
                        action='use',
                        quantity_change=-ingredient['amount'],
                        notes=f"Used for recipe: {ingredient.get('recipe_name', 'Unknown')}"
                    )
                    
                    used_items.append({
                        'item_name': item.name,
                        'amount_used': ingredient['amount'],
                        'remaining': item.quantity
                    })
                else:
                    missing_ingredients.append(ingredient)
            
            self.db.commit()
            
            if missing_ingredients:
                return False, f"Missing {len(missing_ingredients)} ingredients", missing_ingredients
            else:
                return True, f"Successfully used {len(used_items)} ingredients", used_items
                
        except Exception as e:
            self.db.rollback()
            return False, f"Error using ingredients: {str(e)}", []
    
    def _record_history(self, user_id: int, item_id: int, action: str, quantity_change: float, notes: str = None):
        """Record inventory change in history"""
        history_entry = InventoryHistory(
            user_id=user_id,
            item_id=item_id,
            action=action,
            quantity_change=quantity_change,
            notes=notes
        )
        self.db.add(history_entry)
    
    def _item_to_dict(self, item: InventoryItem) -> Dict:
        """Convert InventoryItem to dictionary with computed fields"""
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
