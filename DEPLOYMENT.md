# Deployment Guide

This application is deployed to AWS using:
- **Lightsail** for PostgreSQL database
- **App Runner** for the FastAPI backend
- **Amplify** for the frontend

## Quick Start

📖 **See [AWS_QUICK_START.md](./AWS_QUICK_START.md) for complete deployment instructions.**

The quick start guide covers:
- Creating a Lightsail PostgreSQL database
- Deploying to App Runner
- Connecting to Amplify
- Troubleshooting common issues

## Architecture

```
Frontend (Amplify) → API (App Runner) → Database (Lightsail PostgreSQL)
```

## Environment Variables

### App Runner (Backend)
- `DATABASE_URL`: PostgreSQL connection string from Lightsail
- `ALLOWED_ORIGINS`: `https://no-more-jacob-smith.com`
- `STRAVA_CLIENT_ID`: Your Strava application Client ID
- `STRAVA_CLIENT_SECRET`: Your Strava application Client Secret
- `FRONTEND_URL`: `https://no-more-jacob-smith.com`
- `BACKEND_URL`: Your App Runner service URL (e.g., `https://xxxxx.us-west-2.awsapprunner.com`)

### Amplify (Frontend)
- `VITE_API_URL`: Your App Runner API URL

## Database

The database tables are automatically created when the API starts. Test data is automatically seeded if the database is empty.

## Support

For detailed step-by-step instructions, see [AWS_QUICK_START.md](./AWS_QUICK_START.md).
