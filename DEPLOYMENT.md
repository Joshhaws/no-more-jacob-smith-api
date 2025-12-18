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

### Amplify (Frontend)
- `VITE_API_URL`: Your App Runner API URL

## Database

The database tables are automatically created when the API starts. Test data is automatically seeded if the database is empty.

## Support

For detailed step-by-step instructions, see [AWS_QUICK_START.md](./AWS_QUICK_START.md).
