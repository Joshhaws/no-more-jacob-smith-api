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

Add these to your `.env` file or environment:

```bash
# Strava OAuth Credentials
STRAVA_CLIENT_ID=your_client_id_here
STRAVA_CLIENT_SECRET=your_client_secret_here

# URLs (adjust for your environment)
FRONTEND_URL=http://localhost:5173  # or https://your-domain.com for production
BACKEND_URL=http://localhost:8000   # or https://your-api-domain.com for production
```

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

## Step 5: Sync Segment Data

Once connected:

1. **Sync Individual Segment**: Click the 🔄 button next to any segment with a Strava URL
2. **Sync All Segments**: Click "Sync All Segments" in the header

The sync will update:
- Personal Best Time
- Personal Best Pace
- Personal Attempts
- Last Attempt Date

## API Endpoints

- `GET /auth/strava/authorize` - Get authorization URL
- `GET /auth/strava/callback` - OAuth callback handler
- `GET /auth/strava/status` - Check connection status
- `POST /auth/strava/disconnect` - Disconnect Strava account
- `GET /strava/segments/{segment_id}/times` - Get segment times for a specific segment
- `POST /strava/segments/sync-all` - Sync all segments with Strava data

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

## Notes

- Strava tokens expire after 6 hours but can be refreshed automatically
- The app stores tokens securely in the database
- Only one Strava account can be connected at a time (single-user app)
- Segment IDs are automatically extracted from Strava URLs when creating/updating segments

