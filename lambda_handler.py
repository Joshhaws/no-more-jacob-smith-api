"""
AWS Lambda handler for FastAPI application
Use this for serverless deployment with API Gateway
"""
from mangum import Mangum
from main import app

# Create Mangum handler
# lifespan="off" disables FastAPI lifespan events (not supported in Lambda)
handler = Mangum(app, lifespan="off")

