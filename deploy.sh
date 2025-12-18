#!/bin/bash

# AWS App Runner Deployment Script
# This script helps deploy your FastAPI backend to AWS App Runner

set -e

echo "🚀 AWS App Runner Deployment Helper"
echo "===================================="
echo ""

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null; then
    echo "❌ AWS CLI is not installed."
    echo "Install it from: https://aws.amazon.com/cli/"
    exit 1
fi

# Check if user is authenticated
if ! aws sts get-caller-identity &> /dev/null; then
    echo "❌ AWS CLI is not configured."
    echo "Run: aws configure"
    exit 1
fi

echo "✅ AWS CLI is installed and configured"
echo ""

# Get user input
read -p "Enter your app domain (default: no-more-jacob-smith.com): " AMPLIFY_DOMAIN
AMPLIFY_DOMAIN=${AMPLIFY_DOMAIN:-no-more-jacob-smith.com}
read -p "Enter your Lightsail database endpoint (e.g., your-db.xxxxx.us-east-1.rds.amazonaws.com): " DB_ENDPOINT
read -p "Enter your Lightsail database password: " -s DB_PASSWORD
echo ""
read -p "Enter your Lightsail database username (default: admin): " DB_USERNAME
DB_USERNAME=${DB_USERNAME:-admin}

# Construct DATABASE_URL
DATABASE_URL="postgresql://${DB_USERNAME}:${DB_PASSWORD}@${DB_ENDPOINT}:5432/postgres"
ALLOWED_ORIGINS="https://${AMPLIFY_DOMAIN}"

echo ""
echo "📋 Configuration:"
echo "  Amplify Domain: ${AMPLIFY_DOMAIN}"
echo "  Database Endpoint: ${DB_ENDPOINT}"
echo "  Database User: ${DB_USERNAME}"
echo ""

read -p "Continue with deployment? (y/n): " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Deployment cancelled."
    exit 1
fi

echo ""
echo "⚠️  Note: This script prepares your deployment."
echo "You'll need to complete the deployment in the AWS Console:"
echo ""
echo "1. Go to: https://console.aws.amazon.com/apprunner"
echo "2. Click 'Create service'"
echo "3. Connect your GitHub repository"
echo "4. Use these environment variables:"
echo ""
echo "   DATABASE_URL=${DATABASE_URL}"
echo "   ALLOWED_ORIGINS=${ALLOWED_ORIGINS}"
echo ""
echo "5. Deploy and get your API URL"
echo "6. Update Amplify with: VITE_API_URL=<your-api-url>"
echo ""

