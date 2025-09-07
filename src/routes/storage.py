"""
Storage Location API Routes - Handles storage location management
"""
from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from services.storage_service import StorageService
from models import db

# Create blueprint
storage_bp = Blueprint('storage', __name__)

# Initialize service
storage_service = StorageService()


@storage_bp.route('/api/storage/locations', methods=['GET'])
@login_required
def get_storage_locations():
    """Get user's storage locations"""
    try:
        locations = storage_service.get_user_storage_locations(current_user.id)
        
        return jsonify({
            'success': True,
            'locations': locations
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error retrieving storage locations: {str(e)}'
        }), 500


@storage_bp.route('/api/storage/locations', methods=['POST'])
@login_required
def create_storage_location():
    """Create new storage location"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'message': 'No data provided'
            }), 400
        
        # Validate required fields
        required_fields = ['name', 'location_type']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({
                    'success': False,
                    'message': f'Missing required field: {field}'
                }), 400
        
        # Create location
        success, message = storage_service.create_storage_location(current_user.id, data)
        
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
            'message': f'Error creating storage location: {str(e)}'
        }), 500


@storage_bp.route('/api/storage/locations/<int:location_id>', methods=['PUT'])
@login_required
def update_storage_location(location_id):
    """Update storage location"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'message': 'No data provided'
            }), 400
        
        # Update location
        success, message = storage_service.update_storage_location(
            location_id, 
            current_user.id, 
            data
        )
        
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
            'message': f'Error updating storage location: {str(e)}'
        }), 500


@storage_bp.route('/api/storage/locations/<int:location_id>', methods=['DELETE'])
@login_required
def delete_storage_location(location_id):
    """Delete storage location"""
    try:
        success, message = storage_service.delete_storage_location(
            location_id, 
            current_user.id
        )
        
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
            'message': f'Error deleting storage location: {str(e)}'
        }), 500


@storage_bp.route('/api/storage/locations/<int:location_id>/items', methods=['GET'])
@login_required
def get_location_items(location_id):
    """Get items in specific storage location"""
    try:
        items = storage_service.get_location_inventory(current_user.id, location_id)
        
        return jsonify({
            'success': True,
            'items': items,
            'count': len(items)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error retrieving location items: {str(e)}'
        }), 500


@storage_bp.route('/api/storage/locations/default', methods=['GET'])
@login_required
def get_default_storage_locations():
    """Get list of default storage location types"""
    try:
        default_locations = storage_service.get_default_storage_locations()
        
        return jsonify({
            'success': True,
            'default_locations': default_locations
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error retrieving default storage locations: {str(e)}'
        }), 500


@storage_bp.route('/api/storage/locations/create-defaults', methods=['POST'])
@login_required
def create_default_storage_locations():
    """Create default storage locations for user"""
    try:
        success, message = storage_service.create_default_storage_locations(current_user.id)
        
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
            'message': f'Error creating default storage locations: {str(e)}'
        }), 500


@storage_bp.route('/api/storage/locations/stats', methods=['GET'])
@login_required
def get_storage_location_stats():
    """Get statistics for all storage locations"""
    try:
        stats = storage_service.get_storage_location_stats(current_user.id)
        
        return jsonify({
            'success': True,
            'stats': stats
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error retrieving storage location stats: {str(e)}'
        }), 500
