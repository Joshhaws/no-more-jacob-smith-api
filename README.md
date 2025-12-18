# Strava Segment Tracker API

A FastAPI backend for tracking and managing Strava running segments with personal statistics, crown information, and dynamic data fetching from Strava.

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

### Segment Management
- `GET /items/` - Get all segments (with pagination: skip, limit)
- `POST /items/` - Create a new segment (requires Strava URL)
- `GET /items/{item_id}` - Get a specific segment by ID
- `PUT /items/{item_id}` - Update a segment
- `DELETE /items/{item_id}` - Delete a segment

### Strava Authentication
- `GET /auth/strava/authorize` - Get Strava OAuth authorization URL
- `GET /auth/strava/callback` - Handle Strava OAuth callback
- `GET /auth/strava/status` - Check Strava connection status
- `POST /auth/strava/disconnect` - Disconnect Strava account

### Strava Data
- `GET /strava/segments/{segment_id}/times` - Get personal segment times and stats
- `GET /strava/segments/{segment_id}/metadata` - Get segment metadata (name, distance, elevation)

## Features

- **Dynamic Strava Integration**: Fetch personal stats on-demand from Strava
- **Grade Adjusted Pace (GAP)**: Automatically calculated for hilly segments
- **Crown Management**: Track and edit KOM/QOM information inline
- **Duplicate Prevention**: Validates segments before adding
- **Two-Phase Add Flow**: Preview segment details before saving

## Documentation

- [Strava Setup Guide](./STRAVA_SETUP.md) - Complete Strava OAuth setup
- [AWS Deployment Guide](./AWS_QUICK_START.md) - Deploy to AWS App Runner
- [Local Development](./RUN_LOCALLY.md) - Run locally

## Database

This application requires PostgreSQL. Set the `DATABASE_URL` environment variable in a `.env` file:

```bash
# Create .env file
DATABASE_URL=postgresql://username:password@host:port/database
STRAVA_CLIENT_ID=your_client_id
STRAVA_CLIENT_SECRET=your_client_secret
FRONTEND_URL=http://localhost:5173
BACKEND_URL=http://localhost:8000
```

Then run the application:
```bash
uvicorn main:app --reload
```

## Bulk Loading Segments

To load multiple segments at once, use the ETL script:

```bash
# Edit load_segments.py to add your segment IDs
python3 load_segments.py
```

This script will fetch segment metadata from Strava and load them into the database. Requires Strava authentication (connect via the app first).

