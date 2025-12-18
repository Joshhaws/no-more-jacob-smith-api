# Run Backend Locally

Quick guide to test your API locally before deploying.

## Prerequisites

- Python 3.11+ installed
- pip installed
- PostgreSQL database (local or remote)

## Step 1: Install Dependencies

```bash
cd no-more-jacob-smith-api
pip install -r requirements.txt
```

## Step 2: Set Database URL

You can use the production database for local development. Create a `.env` file:

```bash
cp .env.example .env
```

The `.env.example` file contains the database connection string. The `.env` file is already in `.gitignore` so your credentials won't be committed.

Alternatively, you can set it directly:
```bash
export DATABASE_URL="postgresql://jacobsmith:jacobsmithmustgo@ls-b9bba8e36e6871b769e5ec6604833a4a0be3d3fd.c7mq6w6oszcl.us-west-2.rds.amazonaws.com:5432/postgres"
```

## Step 3: Run the API

```bash
uvicorn main:app --reload
```

The API will start at: **http://localhost:8000**

## Step 4: Test It

- **API Docs**: http://localhost:8000/docs
- **API Root**: http://localhost:8000/
- **Get Items**: http://localhost:8000/items/

## Step 5: Run Frontend (in another terminal)

```bash
cd no-more-jacob-smith-ui
npm install  # if first time
npm run dev
```

Frontend will run at: **http://localhost:5173**

The frontend is already configured to use `http://localhost:8000` by default.

## Stop the Server

Press `Ctrl+C` in the terminal where uvicorn is running.

