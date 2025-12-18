# Strava Authentication Setup

This guide explains how to set up Strava OAuth authentication for the segment tracker.

## Prerequisites

1. A Strava account
2. Access to Strava API (create an app at https://www.strava.com/settings/api)

## Step 1: Create a Strava Application

1. Go to https://www.strava.com/settings/api
2. Click "Create App"
3. Fill in:
   - **Application Name**: Your app name (e.g., "Segment Tracker")
   - **Category**: Choose appropriate category
   - **Website**: Your website URL (or `http://localhost:5173` for local dev)
   - **Authorization Callback Domain**: 
     - For local dev: `localhost`
     - For production: Your domain (e.g., `no-more-jacob-smith.com`)
4. Click "Create"
5. Note your **Client ID** and **Client Secret**

## Step 2: Set Environment Variables

Create a `.env` file in the `no-more-jacob-smith-api` directory with:

```bash
# Database
DATABASE_URL=postgresql://username:password@host:port/database

# Strava OAuth Credentials
STRAVA_CLIENT_ID=your_client_id_here
STRAVA_CLIENT_SECRET=your_client_secret_here

# URLs (adjust for your environment)
FRONTEND_URL=http://localhost:5173  # or https://your-domain.com for production
BACKEND_URL=http://localhost:8000   # or https://your-api-domain.com for production

# CORS (optional, defaults provided)
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000
```

**Note:** For production (AWS App Runner), set these in `apprunner.yaml` or AWS console environment variables.

## Step 3: Update Database

The User model will be created automatically when you start the API. If you need to create it manually:

```bash
python create_tables.py
```

## Step 4: Test the Integration

1. Start your backend API:
   ```bash
   uvicorn main:app --reload
   ```

2. Start your frontend:
   ```bash
   cd ../no-more-jacob-smith-ui
   npm run dev
   ```

3. Click "Connect Strava" in the header
4. Authorize the app in Strava
5. You should be redirected back and see "✓ Connected to Strava"

## Step 5: View Segment Data

Once connected:

1. **View Personal Stats**: Expand any segment row in the table to see your personal statistics
2. **Automatic Fetching**: Personal stats are fetched automatically when you expand a segment row

The accordion view shows:
- Personal Best Effort (clickable link to Strava activity)
- Personal Best Pace
- Grade Adjusted Pace (GAP)
- Your Attempts
- Last Attempt Date
- Crown Information (editable inline)

## API Endpoints

- `GET /auth/strava/authorize` - Get authorization URL
- `GET /auth/strava/callback` - OAuth callback handler
- `GET /auth/strava/status` - Check connection status
- `POST /auth/strava/disconnect` - Disconnect Strava account
- `GET /strava/segments/{segment_id}/times` - Get personal segment times and stats
- `GET /strava/segments/{segment_id}/metadata` - Get segment metadata (name, distance, elevation, crown info)

## Troubleshooting

**"Strava client ID not configured"**
- Make sure `STRAVA_CLIENT_ID` and `STRAVA_CLIENT_SECRET` are set in your environment

**"Failed to exchange authorization code"**
- Check that your redirect URI matches exactly what's configured in Strava
- For local dev: `http://localhost:8000/auth/strava/callback`
- Make sure the callback domain in Strava settings matches (e.g., `localhost`)

**"Strava token expired"**
- Tokens expire after 6 hours. The app will automatically refresh tokens when needed.
- If refresh fails, disconnect and reconnect.

**"Segment not found"**
- Make sure the segment ID is correct
- Verify the segment exists in Strava
- Check that your Strava account has access to the segment

## Features

- **Dynamic Data Fetching**: Personal stats are fetched on-demand when viewing segments (not stored in database)
- **Grade Adjusted Pace (GAP)**: Automatically calculated for segments with elevation
- **Crown Information**: Can be manually edited inline in the accordion view
- **Duplicate Prevention**: Cannot add the same segment twice (validated by segment ID)
- **Two-Phase Add Flow**: Enter Strava URL → Preview segment details → Confirm and save

## Notes

- Strava tokens expire after 6 hours but can be refreshed automatically
- The app stores tokens securely in the database
- Only one Strava account can be connected at a time (single-user app)
- Segment IDs are automatically extracted from Strava URLs when creating segments
- Personal stats are fetched dynamically from Strava and not stored in the database
- Crown/KOM information is not available via Strava API (deprecated in 2020) and must be entered manually

