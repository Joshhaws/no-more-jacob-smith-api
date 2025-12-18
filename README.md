# FastAPI CRUD Boilerplate

A basic FastAPI application with CRUD endpoints for managing items.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the application:
```bash
uvicorn main:app --reload
```

3. Access the API:
- API: http://localhost:8000
- Interactive API docs: http://localhost:8000/docs
- Alternative API docs: http://localhost:8000/redoc

## API Endpoints

- `GET /` - Welcome message
- `POST /items/` - Create a new item
- `GET /items/` - Get all items (with pagination: skip, limit)
- `GET /items/{item_id}` - Get a specific item by ID
- `PUT /items/{item_id}` - Update an item
- `DELETE /items/{item_id}` - Delete an item

## Example Usage

### Create an item:
```bash
curl -X POST "http://localhost:8000/items/" \
  -H "Content-Type: application/json" \
  -d '{"name": "Test Item", "description": "A test item", "is_active": true}'
```

### Get all items:
```bash
curl "http://localhost:8000/items/"
```

### Get a specific item:
```bash
curl "http://localhost:8000/items/1"
```

### Update an item:
```bash
curl -X PUT "http://localhost:8000/items/1" \
  -H "Content-Type: application/json" \
  -d '{"name": "Updated Item", "description": "Updated description"}'
```

### Delete an item:
```bash
curl -X DELETE "http://localhost:8000/items/1"
```

## Database

The application uses SQLite by default (stored in `app.db`). You can modify `database.py` to use PostgreSQL or other databases.

