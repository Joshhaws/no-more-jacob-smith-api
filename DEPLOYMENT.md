# Backend Deployment Guide

This guide covers several options for hosting your FastAPI backend.

## ⚠️ Important: PostgreSQL Required

This application requires PostgreSQL. You must set the `DATABASE_URL` environment variable with a PostgreSQL connection string.

**Format:** `postgresql://username:password@host:port/database`

---

## Option 1: Render 🎨

**Best for:** Simple deployments, free tier, PostgreSQL included

### Steps:

1. **Sign up at [render.com](https://render.com)**

2. **Create a PostgreSQL database:**
   - New → PostgreSQL
   - Copy the "Internal Database URL"

3. **Create a Web Service:**
   - New → Web Service
   - Connect your GitHub repo
   - Build command: `pip install -r requirements.txt`
   - Start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`

4. **Set environment variables:**
   - `DATABASE_URL`: Your PostgreSQL URL
   - `ALLOWED_ORIGINS`: Your Amplify domain

5. **Deploy and get your API URL**

---

## Option 2: AWS Lambda + API Gateway (Serverless) ⚡

**Best for:** AWS integration, pay-per-use, scales automatically

**Note:** Requires significant code changes. Use Mangum adapter.

### Steps:

1. **Install Mangum:**
   ```bash
   pip install mangum
   ```

2. **Create `lambda_handler.py`:**
   ```python
   from mangum import Mangum
   from main import app

   handler = Mangum(app)
   ```

3. **Update requirements.txt:**
   ```
   mangum==0.17.0
   # ... rest of your requirements
   ```

4. **Deploy using:**
   - AWS SAM
   - Serverless Framework
   - AWS CDK
   - Or use [Zappa](https://github.com/Miserlou/Zappa)

5. **Use RDS PostgreSQL** for database

---

## Option 3: AWS App Runner 🏃

**Best for:** AWS-native, containerized, easy setup, works great with Amplify

**📖 See [AWS_DEPLOYMENT.md](./AWS_DEPLOYMENT.md) for complete AWS deployment guide**

Quick steps:
1. Create RDS PostgreSQL database
2. Push code to GitHub
3. Create App Runner service (connects to GitHub)
4. Set environment variables (DATABASE_URL, ALLOWED_ORIGINS)
5. Deploy and get your API URL

Full detailed instructions: [AWS_DEPLOYMENT.md](./AWS_DEPLOYMENT.md)

---

## Option 4: Fly.io 🪰

**Best for:** Global edge deployment, simple CLI

### Steps:

1. **Install Fly CLI:**
   ```bash
   curl -L https://fly.io/install.sh | sh
   ```

2. **Login:**
   ```bash
   fly auth login
   ```

3. **Initialize:**
   ```bash
   cd no-more-jacob-smith-api
   fly launch
   ```

4. **Add PostgreSQL:**
   ```bash
   fly postgres create
   fly postgres attach <db-name> -a <app-name>
   ```

5. **Deploy:**
   ```bash
   fly deploy
   ```

---

---

## After Deployment

1. **Update Amplify environment variables:**
   - `VITE_API_URL`: Your deployed API URL (e.g., `https://your-api.render.com` or `https://your-api.awsapprunner.com`)

2. **Update API CORS:**
   - Set `ALLOWED_ORIGINS` environment variable in your backend
   - Include your Amplify domain: `https://your-app.amplifyapp.com`

3. **Test the connection:**
   - Visit your Amplify app
   - Check browser console for CORS errors
   - Verify data loads correctly

---

## Recommended: AWS App Runner or Render

For fastest setup, I recommend **AWS App Runner** (if using AWS/Amplify) or **Render**:
- ✅ Free tier available (Render)
- ✅ PostgreSQL included
- ✅ Simple deployment
- ✅ Auto-deploys on git push
- ✅ Good documentation

**For AWS users:** AWS App Runner integrates seamlessly with Amplify and RDS.

