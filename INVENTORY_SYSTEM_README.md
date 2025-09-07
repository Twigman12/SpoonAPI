# Inventory Management System

This document describes the new inventory management system added to the SpoonAPI application.

## 🎯 Overview

The inventory management system allows users to:
- Track ingredients in their kitchen storage locations
- Monitor expiry dates and quantities
- Get recipe suggestions based on available ingredients
- Generate shopping lists based on meal plans
- Reduce food waste through better inventory management

## 🏗️ Architecture

### Database Models

#### StorageLocation
- `id`: Primary key
- `user_id`: Foreign key to User
- `name`: Location name (e.g., "Refrigerator", "Pantry")
- `location_type`: Type of storage (fridge, freezer, pantry, etc.)
- `description`: Optional description
- `created_at`: Creation timestamp

#### InventoryItem
- `id`: Primary key
- `user_id`: Foreign key to User
- `storage_location_id`: Foreign key to StorageLocation
- `name`: Item name
- `category`: Item category (produce, dairy, meat, etc.)
- `quantity`: Current quantity
- `unit`: Unit of measurement (pcs, kg, l, etc.)
- `expiry_date`: Expiry date (optional)
- `purchase_date`: When item was added
- `notes`: Optional notes
- `recipe_ingredient_id`: Link to Spoonacular ingredient ID
- `created_at`, `updated_at`: Timestamps

#### InventoryHistory
- `id`: Primary key
- `user_id`: Foreign key to User
- `item_id`: Foreign key to InventoryItem
- `action`: Action type (add, use, expire, delete)
- `quantity_change`: Change in quantity
- `timestamp`: When action occurred
- `notes`: Optional notes

### Service Layer

#### InventoryService
- `add_item()`: Add new inventory item
- `update_item_quantity()`: Update item quantity with history tracking
- `delete_item()`: Delete inventory item
- `search_items()`: Search items with filters
- `get_expiring_items()`: Get items expiring soon
- `get_low_stock_items()`: Get items with low stock
- `get_inventory_stats()`: Get inventory statistics
- `use_item_for_recipe()`: Deduct items when cooking

#### StorageService
- `create_storage_location()`: Create new storage location
- `get_user_storage_locations()`: Get all user's storage locations
- `get_location_inventory()`: Get items in specific location
- `update_storage_location()`: Update storage location
- `delete_storage_location()`: Delete storage location
- `create_default_storage_locations()`: Create default locations for new users

#### RecipeSuggestionService
- `suggest_recipes_from_inventory()`: Suggest recipes based on available ingredients
- `get_cookable_recipes()`: Get recipes that can be cooked with current inventory
- `suggest_shopping_for_recipe()`: Suggest what to buy for a specific recipe
- `plan_meals_from_inventory()`: Suggest meal plan based on expiring ingredients

### API Endpoints

#### Inventory Management
- `GET /api/inventory/items` - Get user's inventory items
- `POST /api/inventory/items` - Add new inventory item
- `PUT /api/inventory/items/<id>` - Update inventory item
- `DELETE /api/inventory/items/<id>` - Delete inventory item
- `POST /api/inventory/search` - Search inventory with filters
- `GET /api/inventory/expiring` - Get items expiring soon
- `GET /api/inventory/low-stock` - Get low stock items
- `GET /api/inventory/stats` - Get inventory statistics
- `POST /api/inventory/use-for-recipe` - Use items for recipe

#### Storage Location Management
- `GET /api/storage/locations` - Get user's storage locations
- `POST /api/storage/locations` - Create new storage location
- `PUT /api/storage/locations/<id>` - Update storage location
- `DELETE /api/storage/locations/<id>` - Delete storage location
- `GET /api/storage/locations/<id>/items` - Get items in specific location
- `GET /api/storage/locations/default` - Get default storage location types
- `POST /api/storage/locations/create-defaults` - Create default locations
- `GET /api/storage/locations/stats` - Get storage location statistics

## 🚀 Installation & Setup

### 1. Database Migration

Run the migration script to create the new tables:

```bash
python migrate_inventory.py
```

This will:
- Create the new database tables
- Create default storage locations for existing users
- Display a summary of the migration

### 2. Test the Integration

Run the integration test to verify everything works:

```bash
python test_inventory_integration.py
```

### 3. Start the Application

```bash
python src/app.py
```

## 📱 User Interface

### Kitchen Inventory Page

The `/kitchen-inventory` page now provides:

#### Left Panel - Controls
- **Quick Add Form**: Add items directly to inventory
- **Search & Filter**: Search by name, category, expiry status
- **Storage Location Management**: View and manage storage locations

#### Right Panel - Storage Locations
- **Storage Location List**: Click to view items in each location
- **Inventory Grid View**: Display items in selected storage location
- **Filter Tabs**: Filter by all items, expiring soon, or expired

#### Features
- **Real-time Updates**: All data comes from the backend API
- **Expiry Tracking**: Visual indicators for items expiring soon
- **Category Icons**: Visual representation of item categories
- **Responsive Design**: Works on desktop and mobile devices

### Dashboard Integration

The dashboard now shows inventory statistics:
- Total items in inventory
- Items expiring soon
- Expired items
- Low stock items

## 🔧 Configuration

### Default Storage Locations

The system automatically creates these default storage locations for new users:
- **Refrigerator** (fridge) - Main refrigerator for fresh items
- **Freezer** (freezer) - Freezer for frozen items
- **Pantry** (pantry) - Pantry for dry goods and non-perishables
- **Spice Rack** (spice_rack) - Spice rack for herbs and spices
- **Counter** (counter) - Kitchen counter for frequently used items

### Item Categories

Supported item categories:
- `produce` - Fruits and vegetables
- `dairy` - Dairy products and eggs
- `meat` - Meat and seafood
- `pantry` - Pantry staples
- `spices` - Spices and herbs
- `frozen` - Frozen foods
- `beverages` - Beverages

### Units of Measurement

Supported units:
- `pcs` - Pieces
- `kg` - Kilograms
- `g` - Grams
- `l` - Liters
- `ml` - Milliliters
- `cups` - Cups
- `tbsp` - Tablespoons
- `tsp` - Teaspoons

## 🔮 Future Enhancements

### Planned Features
1. **Barcode Scanning**: Add items by scanning barcodes
2. **Recipe Integration**: Auto-deduct ingredients when cooking recipes
3. **Shopping List Generation**: Generate shopping lists from meal plans
4. **Nutritional Tracking**: Track nutritional information of inventory items
5. **Expiry Notifications**: Email/push notifications for expiring items
6. **Analytics Dashboard**: Consumption patterns and waste analysis
7. **Grocery Store Integration**: Integration with grocery delivery services

### API Enhancements
1. **Bulk Operations**: Add/update multiple items at once
2. **Import/Export**: CSV import/export functionality
3. **Advanced Search**: More sophisticated search and filtering
4. **Recipe Suggestions**: Enhanced recipe recommendation engine
5. **Meal Planning Integration**: Better integration with meal planning features

## 🐛 Troubleshooting

### Common Issues

#### Database Migration Fails
- Ensure the database file exists and is writable
- Check that all required dependencies are installed
- Verify the database connection settings

#### API Endpoints Not Working
- Ensure the Flask application is running
- Check that the new blueprints are registered
- Verify user authentication is working

#### Frontend Not Loading Data
- Check browser console for JavaScript errors
- Verify API endpoints are accessible
- Ensure user is logged in

### Debug Mode

Enable debug mode in Flask to see detailed error messages:

```python
app.config['DEBUG'] = True
```

## 📊 Performance Considerations

### Database Optimization
- Indexes are automatically created on frequently queried fields
- Use pagination for large inventory lists
- Consider implementing caching for frequently accessed data

### API Performance
- Implement rate limiting for API endpoints
- Use database connection pooling
- Consider implementing Redis caching for session data

## 🔒 Security

### Data Protection
- All user data is isolated by user_id
- Input validation and sanitization on all endpoints
- SQL injection protection through parameterized queries

### Authentication
- All inventory endpoints require user authentication
- User can only access their own inventory data
- Proper authorization checks on all operations

## 📝 API Documentation

### Example API Calls

#### Add Inventory Item
```bash
curl -X POST http://localhost:5000/api/inventory/items \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Tomatoes",
    "category": "produce",
    "quantity": 5,
    "unit": "pcs",
    "expiry_date": "2024-01-15",
    "storage_location_id": 1,
    "notes": "Roma tomatoes"
  }'
```

#### Get Inventory Items
```bash
curl -X GET http://localhost:5000/api/inventory/items
```

#### Search Inventory
```bash
curl -X POST http://localhost:5000/api/inventory/search \
  -H "Content-Type: application/json" \
  -d '{
    "name": "tomato",
    "category": "produce"
  }'
```

## 🤝 Contributing

When contributing to the inventory system:

1. Follow the existing code patterns and structure
2. Add proper error handling and validation
3. Include unit tests for new functionality
4. Update this documentation for new features
5. Ensure backward compatibility with existing features

## 📄 License

This inventory management system is part of the SpoonAPI project and follows the same license terms.
