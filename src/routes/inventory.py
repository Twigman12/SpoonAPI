"""
Inventory API Routes - Handles inventory-related HTTP requests
"""
from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from services.inventory_service import InventoryService
from services.storage_service import StorageService
from models import db

# Create blueprint
inventory_bp = Blueprint('inventory', __name__)

# Initialize services
inventory_service = InventoryService()
storage_service = StorageService()


@inventory_bp.route('/api/inventory/items', methods=['GET'])
@login_required
def get_inventory_items():
    """Get user's inventory items with optional filtering"""
    try:
        # Get query parameters
        name = request.args.get('name')
        category = request.args.get('category')
        storage_location_id = request.args.get('storage_location_id', type=int)
        expiry_filter = request.args.get('expiry_filter')
        
        # Build filters
        filters = {}
        if name:
            filters['name'] = name
        if category:
            filters['category'] = category
        if storage_location_id:
            filters['storage_location_id'] = storage_location_id
        if expiry_filter:
            filters['expiry_filter'] = expiry_filter
        
        # Get items
        items = inventory_service.search_items(current_user.id, filters)
        
        # Get stats
        stats = inventory_service.get_inventory_stats(current_user.id)
        
        return jsonify({
            'success': True,
            'items': items,
            'stats': stats
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error retrieving inventory: {str(e)}'
        }), 500


@inventory_bp.route('/api/inventory/items', methods=['POST'])
@login_required
def add_inventory_item():
    """Add new item to inventory"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'message': 'No data provided'
            }), 400
        
        # Validate required fields
        required_fields = ['name', 'category', 'quantity', 'unit', 'storage_location_id']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({
                    'success': False,
                    'message': f'Missing required field: {field}'
                }), 400
        
        # Add item
        success, message = inventory_service.add_item(current_user.id, data)
        
        if success:
            return jsonify({
                'success': True,
                'message': message
            })
        else:
            return jsonify({
                'success': False,
                'message': message
            }), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error adding item: {str(e)}'
        }), 500


@inventory_bp.route('/api/inventory/items/<int:item_id>', methods=['PUT'])
@login_required
def update_inventory_item(item_id):
    """Update existing inventory item"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'message': 'No data provided'
            }), 400
        
        # Handle quantity update
        if 'quantity' in data:
            success, message = inventory_service.update_item_quantity(
                item_id, 
                float(data['quantity']), 
                current_user.id,
                data.get('notes')
            )
        else:
            # Handle other field updates
            from models import InventoryItem
            
            item = InventoryItem.query.filter_by(
                id=item_id, 
                user_id=current_user.id
            ).first()
            
            if not item:
                return jsonify({
                    'success': False,
                    'message': 'Item not found'
                }), 404
            
            # Update fields
            if 'name' in data:
                item.name = data['name']
            if 'category' in data:
                item.category = data['category']
            if 'unit' in data:
                item.unit = data['unit']
            if 'expiry_date' in data:
                if data['expiry_date']:
                    from datetime import datetime
                    item.expiry_date = datetime.strptime(data['expiry_date'], '%Y-%m-%d').date()
                else:
                    item.expiry_date = None
            if 'notes' in data:
                item.notes = data['notes']
            if 'storage_location_id' in data:
                item.storage_location_id = data['storage_location_id']
            
            item.updated_at = datetime.utcnow()
            db.session.commit()
            
            success, message = True, "Item updated successfully"
        
        if success:
            return jsonify({
                'success': True,
                'message': message
            })
        else:
            return jsonify({
                'success': False,
                'message': message
            }), 400
            
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error updating item: {str(e)}'
        }), 500


@inventory_bp.route('/api/inventory/items/<int:item_id>', methods=['DELETE'])
@login_required
def delete_inventory_item(item_id):
    """Delete inventory item"""
    try:
        success, message = inventory_service.delete_item(item_id, current_user.id)
        
        if success:
            return jsonify({
                'success': True,
                'message': message
            })
        else:
            return jsonify({
                'success': False,
                'message': message
            }), 404
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error deleting item: {str(e)}'
        }), 500


@inventory_bp.route('/api/inventory/search', methods=['POST'])
@login_required
def search_inventory():
    """Search inventory with filters"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'message': 'No search criteria provided'
            }), 400
        
        # Search items
        items = inventory_service.search_items(current_user.id, data)
        
        return jsonify({
            'success': True,
            'items': items,
            'count': len(items)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error searching inventory: {str(e)}'
        }), 500


@inventory_bp.route('/api/inventory/expiring', methods=['GET'])
@login_required
def get_expiring_items():
    """Get items expiring soon"""
    try:
        days_ahead = request.args.get('days', 7, type=int)
        items = inventory_service.get_expiring_items(current_user.id, days_ahead)
        
        return jsonify({
            'success': True,
            'items': items,
            'count': len(items)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error retrieving expiring items: {str(e)}'
        }), 500


@inventory_bp.route('/api/inventory/low-stock', methods=['GET'])
@login_required
def get_low_stock_items():
    """Get items with low stock"""
    try:
        threshold = request.args.get('threshold', 1.0, type=float)
        items = inventory_service.get_low_stock_items(current_user.id, threshold)
        
        return jsonify({
            'success': True,
            'items': items,
            'count': len(items)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error retrieving low stock items: {str(e)}'
        }), 500


@inventory_bp.route('/api/inventory/stats', methods=['GET'])
@login_required
def get_inventory_stats():
    """Get inventory statistics"""
    try:
        stats = inventory_service.get_inventory_stats(current_user.id)
        
        return jsonify({
            'success': True,
            'stats': stats
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error retrieving inventory stats: {str(e)}'
        }), 500


@inventory_bp.route('/api/inventory/use-for-recipe', methods=['POST'])
@login_required
def use_items_for_recipe():
    """Use inventory items for a recipe"""
    try:
        data = request.get_json()
        
        if not data or 'ingredients' not in data:
            return jsonify({
                'success': False,
                'message': 'No ingredients provided'
            }), 400
        
        success, message, result = inventory_service.use_item_for_recipe(
            current_user.id, 
            data['ingredients']
        )
        
        return jsonify({
            'success': success,
            'message': message,
            'result': result
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error using items for recipe: {str(e)}'
        }), 500


@inventory_bp.route('/api/inventory/shopping-list', methods=['GET'])
@login_required
def get_shopping_list():
    """Generate shopping list based on meal plans and current inventory"""
    try:
        # This would integrate with meal planning service
        # For now, return a placeholder response
        return jsonify({
            'success': True,
            'message': 'Shopping list feature coming soon',
            'items': []
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error generating shopping list: {str(e)}'
        }), 500
