# Deploy to AWS Now - Step by Step

Follow these steps to deploy your backend and connect it to Amplify.

## Prerequisites Checklist

- [ ] AWS Account
- [ ] Code pushed to GitHub
- [ ] Amplify app domain (you should know this from your Amplify console)

## Step 1: Create RDS PostgreSQL Database (5 minutes)

1. **Go to AWS Console**: https://console.aws.amazon.com/rds
2. Click **"Create database"**
3. Select **"PostgreSQL"**
4. Choose **"Free tier"** template
5. **Settings**:
   - **DB instance identifier**: `strava-segments-db`
   - **Master username**: `admin` (or your choice)
   - **Master password**: Create a strong password ⚠️ **SAVE THIS!**
   - **DB instance class**: `db.t3.micro` (free tier)
6. **Connectivity**:
   - **Public access**: **Yes** (required for App Runner)
   - **VPC**: Default VPC
   - **Security group**: Create new
7. Click **"Create database"**
8. **Wait 5-10 minutes** for database to be available
9. **Note the Endpoint** (e.g., `strava-segments-db.xxxxx.us-east-1.rds.amazonaws.com`)

## Step 2: Update Security Group (2 minutes)

1. Go to **EC2 Console**: https://console.aws.amazon.com/ec2
2. Click **"Security Groups"** (left sidebar)
3. Find the security group for your RDS database (it will have your DB name)
4. Click on it → **"Edit inbound rules"**
5. Click **"Add rule"**:
   - **Type**: PostgreSQL
   - **Source**: `0.0.0.0/0` (for now - you can restrict later)
   - **Port**: 5432
6. Click **"Save rules"**

## Step 3: Deploy to App Runner (5 minutes)

1. **Go to App Runner**: https://console.aws.amazon.com/apprunner
2. Click **"Create service"**
3. **Source configuration**:
   - **Source type**: Source code repository
   - Click **"Connect to GitHub"** (authorize if needed)
   - **Repository**: Select your repository
   - **Branch**: `main` (or your branch)
   - **Deployment trigger**: Automatic
4. **Build configuration**:
   - **Configuration file**: Use default (will detect Dockerfile)
   - **Port**: `8000`
5. **Service configuration**:
   - **Service name**: `strava-segments-api`
   - **Virtual CPU**: 0.25 vCPU
   - **Memory**: 0.5 GB
   - **Auto scaling**: Enabled (min 1, max 5)
6. **Security & access**:
   - **Access role**: Create new service role (App Runner will create this)
7. **Environment variables** - **ADD THESE**:
   ```
   DATABASE_URL=postgresql://admin:YOUR_PASSWORD@YOUR_DB_ENDPOINT:5432/postgres
   ALLOWED_ORIGINS=https://YOUR_AMPLIFY_DOMAIN
   ```
   
   Replace:
   - `YOUR_PASSWORD` with your RDS password
   - `YOUR_DB_ENDPOINT` with your RDS endpoint (without `:5432`)
   - `YOUR_AMPLIFY_DOMAIN` with your Amplify domain (e.g., `main.xxxxx.amplifyapp.com`)

8. Click **"Create & deploy"**
9. **Wait 5-10 minutes** for deployment

## Step 4: Get Your API URL (1 minute)

1. Once deployment completes, go to your App Runner service
2. Copy the **"Default domain"** (e.g., `xxxxx.us-east-1.awsapprunner.com`)
3. Your API URL will be: `https://xxxxx.us-east-1.awsapprunner.com`
4. **Test it**: Visit `https://xxxxx.us-east-1.awsapprunner.com/docs` to see the API docs

## Step 5: Update Amplify (2 minutes)

1. **Go to Amplify Console**: https://console.aws.amazon.com/amplify
2. Select your app
3. Go to **"App settings"** → **"Environment variables"**
4. Click **"Manage variables"**
5. **Add variable**:
   - **Key**: `VITE_API_URL`
   - **Value**: `https://xxxxx.us-east-1.awsapprunner.com` (your API URL from Step 4)
6. Click **"Save"**
7. Go to **"App settings"** → **"General"**
8. Click **"Redeploy this version"** to apply the new environment variable

## Step 6: Test Everything (2 minutes)

1. Visit your Amplify app
2. Open browser console (F12)
3. Check for any errors
4. Verify the table loads with data
5. If you see CORS errors, double-check `ALLOWED_ORIGINS` includes your exact Amplify domain

## Troubleshooting

### Can't connect to database?
- Check security group allows port 5432
- Verify RDS endpoint is correct
- Check password in DATABASE_URL

### CORS errors?
- Verify `ALLOWED_ORIGINS` includes your Amplify domain (with `https://`)
- Check environment variable is set correctly in App Runner
- Restart App Runner service after changing environment variables

### 502/503 errors?
- Check CloudWatch logs in App Runner
- Verify port is 8000
- Check DATABASE_URL format is correct

### No data showing?
- Database might be empty
- Visit `https://your-api-url/seed/` to seed test data
- Or use the API docs at `https://your-api-url/docs` to create items

## Quick Reference

**RDS Endpoint Format:**
```
postgresql://username:password@endpoint:5432/postgres
```

**Environment Variables Needed:**
- `DATABASE_URL`: Your PostgreSQL connection string
- `ALLOWED_ORIGINS`: Your Amplify domain (comma-separated if multiple)

**Amplify Environment Variable:**
- `VITE_API_URL`: Your App Runner API URL

## Done! ✅

Your backend is now deployed and connected to Amplify!

