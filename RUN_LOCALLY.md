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

You need a PostgreSQL database. Set the `DATABASE_URL` environment variable:

```bash
export DATABASE_URL="postgresql://username:password@localhost:5432/database_name"
```

Or create a `.env` file (you'll need python-dotenv):
```bash
DATABASE_URL=postgresql://username:password@localhost:5432/database_name
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

