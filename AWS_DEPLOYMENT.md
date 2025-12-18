# AWS Deployment Guide

Complete guide for deploying your FastAPI backend to AWS. Since you're using Amplify for the frontend, these options integrate well with your AWS setup.

---

## Option 1: AWS App Runner (Easiest AWS Option) 🏃

**Best for:** Simple containerized deployment, auto-scaling, AWS-native

### Prerequisites:
- AWS Account
- Code in GitHub (or AWS CodeCommit)
- AWS RDS PostgreSQL database (or use AWS RDS Proxy)

### Steps:

#### 1. Create RDS PostgreSQL Database

1. Go to **AWS Console → RDS → Databases**
2. Click **Create database**
3. Choose **PostgreSQL**
4. Select **Free tier** (or your preferred tier)
5. Configure:
   - **DB instance identifier**: `strava-segments-db`
   - **Master username**: `admin` (or your choice)
   - **Master password**: Create a strong password (save it!)
   - **DB instance class**: `db.t3.micro` (free tier)
   - **Storage**: 20 GB (free tier)
6. **VPC**: Use default VPC or create new
7. **Public access**: Yes (for App Runner to connect)
8. **Security group**: Create new or use existing
9. Click **Create database**
10. Wait for database to be available (~5-10 minutes)
11. Note the **Endpoint** (e.g., `your-db.xxxxx.us-east-1.rds.amazonaws.com:5432`)

#### 2. Update Security Group

1. Go to **EC2 → Security Groups**
2. Find your RDS security group
3. **Edit inbound rules**
4. Add rule:
   - **Type**: PostgreSQL
   - **Source**: Your App Runner service security group (or `0.0.0.0/0` for testing - restrict later)
   - **Port**: 5432
5. Save rules

#### 3. Create App Runner Service

1. Go to **AWS Console → App Runner → Services**
2. Click **Create service**
3. **Source**:
   - **Source type**: Source code repository
   - **Connect to GitHub** (authorize if needed)
   - **Repository**: Select your repo
   - **Branch**: `main` (or your branch)
   - **Deployment trigger**: Automatic (on push)
4. **Configure build**:
   - **Configuration file**: Use default (detects Dockerfile)
   - **Build command**: (leave default)
   - **Port**: `8000`
5. **Configure service**:
   - **Service name**: `strava-segments-api`
   - **Virtual CPU**: 0.25 vCPU (free tier eligible)
   - **Memory**: 0.5 GB (free tier eligible)
   - **Auto scaling**: Enabled (min 1, max 5)
6. **Configure security**:
   - **Access role**: Create new service role (App Runner will create)
   - **Encryption**: Use default
7. **Add environment variables**:
   ```
   DATABASE_URL=postgresql://admin:YOUR_PASSWORD@your-db.xxxxx.us-east-1.rds.amazonaws.com:5432/postgres
   ALLOWED_ORIGINS=https://your-app.amplifyapp.com,https://main.xxxxx.amplifyapp.com
   ```
   Replace:
   - `YOUR_PASSWORD` with your RDS password
   - `your-db.xxxxx.us-east-1.rds.amazonaws.com` with your RDS endpoint
   - `your-app.amplifyapp.com` with your Amplify domain
8. Click **Create & deploy**
9. Wait for deployment (~5-10 minutes)

#### 4. Get Your API URL

1. Once deployed, go to your App Runner service
2. Copy the **Default domain** (e.g., `xxxxx.us-east-1.awsapprunner.com`)
3. Your API will be at: `https://xxxxx.us-east-1.awsapprunner.com`

#### 5. Update Amplify

1. Go to **Amplify Console → Your App → Environment variables**
2. Add: `VITE_API_URL=https://xxxxx.us-east-1.awsapprunner.com`
3. Redeploy your Amplify app

---

## Option 2: AWS Elastic Beanstalk 🌱

**Best for:** Traditional PaaS, easy deployment, good for learning AWS

### Steps:

#### 1. Install EB CLI

```bash
pip install awsebcli
```

#### 2. Initialize Elastic Beanstalk

```bash
cd no-more-jacob-smith-api
eb init
```

Follow prompts:
- **Select a region**: Choose your region (e.g., `us-east-1`)
- **Application name**: `strava-segments-api`
- **Platform**: Python
- **Platform version**: Python 3.11
- **SSH**: Yes (optional, for debugging)

#### 3. Create Application Version

```bash
eb create strava-segments-env
```

This will:
- Create EC2 instance
- Set up load balancer
- Deploy your app

#### 4. Set Environment Variables

```bash
eb setenv DATABASE_URL="postgresql://admin:password@your-db.xxxxx.us-east-1.rds.amazonaws.com:5432/postgres"
eb setenv ALLOWED_ORIGINS="https://your-app.amplifyapp.com"
```

Or use AWS Console:
1. Go to **Elastic Beanstalk → Your Environment → Configuration**
2. **Software** → **Environment properties**
3. Add variables

#### 5. Create RDS Database

Same as App Runner steps above, but:
- In Elastic Beanstalk console, go to **Configuration → Database**
- Click **Modify** → **Add RDS database**
- This creates RDS in same VPC as your EB environment

#### 6. Update Requirements

Create `Procfile`:
```
web: uvicorn main:app --host 0.0.0.0 --port 8000
```

#### 7. Deploy Updates

```bash
eb deploy
```

#### 8. Get Your URL

```bash
eb status
```

Or check Elastic Beanstalk console for the URL.

---

## Option 3: AWS ECS with Fargate (More Control) 🐳

**Best for:** Full container control, production workloads

### Steps:

#### 1. Push Docker Image to ECR

```bash
# Install AWS CLI if not installed
aws --version

# Login to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com

# Create repository
aws ecr create-repository --repository-name strava-segments-api --region us-east-1

# Build and push
docker build -t strava-segments-api .
docker tag strava-segments-api:latest YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/strava-segments-api:latest
docker push YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/strava-segments-api:latest
```

#### 2. Create ECS Cluster

1. Go to **ECS → Clusters**
2. **Create cluster**
3. **Cluster name**: `strava-segments-cluster`
4. **Infrastructure**: AWS Fargate
5. Click **Create**

#### 3. Create Task Definition

1. Go to **ECS → Task definitions → Create new**
2. **Task definition family**: `strava-segments-api`
3. **Launch type**: Fargate
4. **Task size**:
   - CPU: 0.25 vCPU
   - Memory: 0.5 GB
5. **Container**:
   - **Container name**: `api`
   - **Image URI**: `YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/strava-segments-api:latest`
   - **Port mappings**: `8000`
   - **Environment variables**:
     ```
     DATABASE_URL=postgresql://admin:password@your-db.xxxxx.us-east-1.rds.amazonaws.com:5432/postgres
     ALLOWED_ORIGINS=https://your-app.amplifyapp.com
     ```
6. Click **Create**

#### 4. Create Service

1. Go to your cluster → **Services** → **Create**
2. **Launch type**: Fargate
3. **Task definition**: Select your task definition
4. **Service name**: `strava-segments-service`
5. **Number of tasks**: 1
6. **VPC**: Select your VPC
7. **Subnets**: Select public subnets
8. **Security group**: Create new (allow port 8000 from internet)
9. **Load balancer**: Create Application Load Balancer
10. Click **Create**

#### 5. Get Your URL

Check the load balancer DNS name in EC2 → Load Balancers.

---

## Option 4: AWS Lambda + API Gateway (Serverless) ⚡

**Best for:** Pay-per-use, auto-scaling, cost-effective for low traffic

**Note:** Requires code changes. Use RDS PostgreSQL for database.

### Steps:

#### 1. Install Dependencies

```bash
pip install mangum
```

Add to `requirements.txt`:
```
mangum==0.17.0
```

#### 2. Create Lambda Handler

Create `lambda_handler.py`:
```python
from mangum import Mangum
from main import app

handler = Mangum(app, lifespan="off")
```

#### 3. Package for Lambda

Create `package.sh`:
```bash
#!/bin/bash
mkdir -p package
pip install -r requirements.txt -t package/
cp -r *.py package/
cd package
zip -r ../lambda-deployment.zip .
cd ..
```

Make executable:
```bash
chmod +x package.sh
./package.sh
```

#### 4. Create Lambda Function

1. Go to **Lambda → Functions → Create function**
2. **Function name**: `strava-segments-api`
3. **Runtime**: Python 3.11
4. **Architecture**: x86_64
5. Click **Create function**

#### 5. Upload Code

1. In Lambda function → **Code** tab
2. **Upload from** → `.zip file`
3. Upload `lambda-deployment.zip`

#### 6. Configure Environment Variables

In Lambda function → **Configuration → Environment variables**:
```
DATABASE_URL=postgresql://admin:password@your-db.xxxxx.us-east-1.rds.amazonaws.com:5432/postgres
ALLOWED_ORIGINS=https://your-app.amplifyapp.com
```

#### 7. Set Handler

**Runtime settings** → **Handler**: `lambda_handler.handler`

#### 8. Create API Gateway

1. Go to **API Gateway → Create API**
2. Choose **REST API**
3. **API name**: `strava-segments-api`
4. Click **Create API**
5. **Actions** → **Create Resource**
6. **Resource name**: `{proxy+}`
7. **Actions** → **Create Method** → `ANY`
8. **Integration type**: Lambda Function
9. **Lambda Function**: `strava-segments-api`
10. Click **Save**
11. **Actions** → **Deploy API**
12. **Deployment stage**: `prod`
13. Note the **Invoke URL**

#### 9. Use RDS Proxy (Recommended for Lambda)

Lambda + RDS needs connection pooling. Use RDS Proxy:
1. Go to **RDS → Proxies → Create proxy**
2. Connect to your RDS instance
3. Update `DATABASE_URL` to use proxy endpoint

---

## Database Setup (All Options)

### Create RDS PostgreSQL

1. **AWS Console → RDS → Create database**
2. **Engine**: PostgreSQL
3. **Template**: Free tier (or Production)
4. **Settings**:
   - DB instance: `strava-segments-db`
   - Master username: `admin`
   - Master password: (save this!)
5. **Instance configuration**: `db.t3.micro` (free tier)
6. **Storage**: 20 GB
7. **Connectivity**: 
   - **Public access**: Yes (or configure VPC properly)
   - **VPC**: Default or your VPC
   - **Security group**: Create new (allow PostgreSQL from your service)
8. **Database name**: `postgres` (or create new)
9. Click **Create database**

### Get Connection String

After database is available:
```
postgresql://admin:YOUR_PASSWORD@your-db.xxxxx.us-east-1.rds.amazonaws.com:5432/postgres
```

---

## Security Best Practices

1. **Use AWS Secrets Manager** for database passwords:
   ```python
   import boto3
   import json
   
   def get_secret():
       secret_name = "strava-segments/database"
       region_name = "us-east-1"
       
       session = boto3.session.Session()
       client = session.client(service_name='secretsmanager', region_name=region_name)
       
       get_secret_value_response = client.get_secret_value(SecretId=secret_name)
       secret = json.loads(get_secret_value_response['SecretString'])
       return secret['DATABASE_URL']
   ```

2. **Restrict Security Groups**: Only allow connections from your App Runner/ECS service

3. **Use RDS Proxy** for Lambda (connection pooling)

4. **Enable VPC** for private networking

5. **Use IAM Roles** instead of access keys

---

## Cost Estimates (Monthly)

- **App Runner**: ~$5-10/month (0.25 vCPU, 0.5 GB)
- **Elastic Beanstalk**: ~$15-30/month (EC2 + Load Balancer)
- **ECS Fargate**: ~$10-20/month (similar to App Runner)
- **Lambda**: ~$0-5/month (pay per request, free tier: 1M requests)
- **RDS PostgreSQL**: Free tier (750 hours/month) or ~$15/month (db.t3.micro)

---

## Recommended: AWS App Runner

For your use case, **AWS App Runner** is recommended:
- ✅ Easiest AWS deployment
- ✅ Auto-scaling
- ✅ Integrates with GitHub
- ✅ Similar to Render but AWS-native
- ✅ Works great with Amplify

---

## Troubleshooting

### CORS Errors
- Check `ALLOWED_ORIGINS` includes your Amplify domain
- Verify environment variable is set correctly

### Database Connection Errors
- Check security group allows PostgreSQL (port 5432)
- Verify RDS is publicly accessible (or in same VPC)
- Check `DATABASE_URL` format is correct

### 502/503 Errors
- Check application logs in CloudWatch
- Verify port is 8000
- Check health endpoint works

### Environment Variables Not Working
- Restart service after setting variables
- Check variable names match exactly
- Verify no typos in values

---

## Next Steps

1. Choose your deployment option (App Runner recommended)
2. Create RDS PostgreSQL database
3. Deploy your API
4. Update Amplify with `VITE_API_URL`
5. Test the connection
6. Monitor in CloudWatch

