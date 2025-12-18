# AWS Deployment Guide

Complete guide for deploying your FastAPI backend to AWS using Lightsail (database) and App Runner (API).

## Prerequisites
- AWS Account
- Code pushed to GitHub
- ~15 minutes

## Step-by-Step

### 1. Create Lightsail Database (5 min)

1. AWS Console → **Lightsail → Databases → Create database**
2. **Database engine**: PostgreSQL
3. **Database plan**: Choose a plan (e.g., `$15/month` for PostgreSQL with 1 GB RAM)
4. **Database name**: `strava-segments-db`
5. **Master username**: `admin` (or your choice)
6. **Master password**: Create strong password (save it!)
7. **Availability zone**: Choose any zone
8. Click **Create database**
9. Wait ~5 minutes for database to be available
10. Once created, go to **Connectivity & security** tab and note the **Endpoint** (e.g., `strava-segments-db.xxxxx.us-east-1.rds.amazonaws.com`)
11. Note your **Master username** and **Master password** (you'll need these for the connection string)

### 2. Enable Public Access (1 min)

1. In your Lightsail database, go to **Networking** tab
2. Under **Public mode**, toggle **Enable public mode** to ON
3. This allows App Runner to connect to your database

### 3. Deploy to App Runner (5 min)

1. **AWS Console → App Runner → Create service**
2. **Source configuration**:
   - **Source type**: Source code repository
   - **Connect to GitHub** (authorize if needed)
   - **Repository**: Select your repository
   - **Branch**: `main` (or your branch)
   - **Deployment trigger**: Automatic (on push)
3. **Build configuration**:
   - **Configuration file**: Use default (detects Dockerfile)
   - **Port**: `8000`
4. **Service configuration**:
   - **Service name**: `strava-segments-api`
   - **Virtual CPU**: 0.25 vCPU
   - **Memory**: 0.5 GB
   - **Auto scaling**: Enabled (min 1, max 5)
5. **Security & access**:
   - **Access role**: Create new service role (App Runner will create this)
6. **Environment variables** - **ADD THESE**:
   ```
   DATABASE_URL=postgresql://admin:YOUR_PASSWORD@YOUR_DB_ENDPOINT:5432/postgres
   ALLOWED_ORIGINS=https://no-more-jacob-smith.com
   ```
   Replace:
   - `admin` with your Lightsail database master username
   - `YOUR_PASSWORD` with your Lightsail database password
   - `YOUR_DB_ENDPOINT` with your Lightsail database endpoint (without `:5432`)
7. Click **Create & deploy**
8. Wait ~5-10 minutes for deployment

### 4. Get Your API URL (1 min)

1. App Runner service → Copy **Default domain**
2. Your API: `https://xxxxx.us-east-1.awsapprunner.com`

### 5. Update Amplify (2 min)

1. **Amplify Console → Your App → Environment variables**
2. Go to **App settings** → **Environment variables**
3. Click **Manage variables**
4. **Add variable**:
   - **Key**: `VITE_API_URL`
   - **Value**: `https://xxxxx.us-east-1.awsapprunner.com` (your API URL from Step 4)
5. Click **Save**
6. Go to **App settings** → **General**
7. Click **Redeploy this version** to apply the new environment variable

### 6. Test Everything (2 min)

1. Visit your app at `https://no-more-jacob-smith.com`
2. Open browser console (F12)
3. Check for any errors
4. Verify the table loads with data
5. **Test API directly**: Visit `https://xxxxx.us-east-1.awsapprunner.com/docs` to see the API docs
6. **Seed test data** (if needed): Visit `https://xxxxx.us-east-1.awsapprunner.com/seed/` to populate the database

## Done! ✅

Your API is now live on AWS and connected to your Amplify frontend.

## Troubleshooting

**Can't connect to database?**
- Verify public mode is enabled in Lightsail database settings
- Check Lightsail database endpoint is correct
- Verify password in DATABASE_URL matches your Lightsail database password
- Ensure database is in "Available" state

**CORS errors?**
- Verify `ALLOWED_ORIGINS` includes your domain: `https://no-more-jacob-smith.com`
- Check environment variable is set correctly in App Runner
- Restart App Runner service after changing environment variables

**502/503 errors?**
- Check CloudWatch logs in App Runner
- Verify port is 8000
- Check `DATABASE_URL` format is correct
- Ensure database is in "Available" state

**No data showing?**
- Database might be empty
- Visit `https://your-api-url/seed/` to seed test data
- Or use the API docs at `https://your-api-url/docs` to create items

## Cost

- **App Runner**: ~$5-10/month
- **Lightsail PostgreSQL**: ~$15/month (1 GB RAM plan) or ~$30/month (2 GB RAM plan)
- **Total**: ~$20-40/month depending on usage

## Quick Reference

**Lightsail Database Connection String Format:**
```
postgresql://username:password@endpoint:5432/postgres
```

**Environment Variables Needed:**
- `DATABASE_URL`: Your Lightsail PostgreSQL connection string
- `ALLOWED_ORIGINS`: Your domain (https://no-more-jacob-smith.com)

**Amplify Environment Variable:**
- `VITE_API_URL`: Your App Runner API URL

## Next Steps

- Set up custom domain for App Runner (optional)
- Configure auto-scaling thresholds
- Set up CloudWatch alarms for monitoring
- Use AWS Secrets Manager for database passwords (production)
- Set up automated backups for Lightsail database

