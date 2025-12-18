# AWS Quick Start Guide

Fastest way to deploy to AWS (App Runner method).

## Prerequisites
- AWS Account
- Code pushed to GitHub
- ~15 minutes

## Step-by-Step

### 1. Create RDS Database (5 min)

1. AWS Console → **RDS → Databases → Create database**
2. **PostgreSQL** → **Free tier**
3. Settings:
   - **DB instance**: `strava-segments-db`
   - **Username**: `admin`
   - **Password**: Create strong password (save it!)
   - **Instance**: `db.t3.micro`
4. **Public access**: Yes
5. **VPC**: Default VPC
6. **Security group**: Create new
7. Click **Create database**
8. Wait ~5 minutes, note the **Endpoint**

### 2. Update Security Group (2 min)

1. **EC2 → Security Groups** → Find your RDS security group
2. **Edit inbound rules** → **Add rule**:
   - Type: PostgreSQL
   - Source: `0.0.0.0/0` (for testing - restrict later)
   - Port: 5432
3. Save

### 3. Deploy to App Runner (5 min)

1. **AWS Console → App Runner → Create service**
2. **Source**: GitHub → Connect repo → Select branch
3. **Build**: Auto-detect (uses Dockerfile)
4. **Service name**: `strava-segments-api`
5. **CPU**: 0.25 vCPU, **Memory**: 0.5 GB
6. **Environment variables**:
   ```
   DATABASE_URL=postgresql://admin:YOUR_PASSWORD@YOUR_DB_ENDPOINT:5432/postgres
   ALLOWED_ORIGINS=https://your-app.amplifyapp.com
   ```
   Replace:
   - `YOUR_PASSWORD` with your RDS password
   - `YOUR_DB_ENDPOINT` with your RDS endpoint (without `:5432`)
   - `your-app.amplifyapp.com` with your Amplify domain
7. Click **Create & deploy**
8. Wait ~5 minutes

### 4. Get Your API URL (1 min)

1. App Runner service → Copy **Default domain**
2. Your API: `https://xxxxx.us-east-1.awsapprunner.com`

### 5. Update Amplify (2 min)

1. **Amplify Console → Your App → Environment variables**
2. Add: `VITE_API_URL=https://xxxxx.us-east-1.awsapprunner.com`
3. **Redeploy** your Amplify app

## Done! ✅

Your API is now live on AWS and connected to your Amplify frontend.

## Troubleshooting

**Can't connect to database?**
- Check security group allows port 5432
- Verify RDS endpoint is correct
- Check password in DATABASE_URL

**CORS errors?**
- Verify ALLOWED_ORIGINS includes your Amplify domain
- Check environment variable is set correctly

**502 errors?**
- Check CloudWatch logs in App Runner
- Verify port is 8000
- Check application is running

## Cost

- **App Runner**: ~$5-10/month
- **RDS (free tier)**: Free for 12 months, then ~$15/month
- **Total**: ~$5-25/month depending on usage

## Next Steps

- Set up custom domain (optional)
- Configure auto-scaling
- Set up CloudWatch alarms
- Use AWS Secrets Manager for passwords

