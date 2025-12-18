# Quick Run Guide

## Option 1: Run Locally (Testing)

**Terminal 1 - Backend:**
```bash
cd no-more-jacob-smith-api
pip install -r requirements.txt
export DATABASE_URL="postgresql://jacobsmith:jacobsmithmustgo@ls-b9bba8e36e6871b769e5ec6604833a4a0be3d3fd.c7mq6w6oszcl.us-west-2.rds.amazonaws.com:5432/postgres"
uvicorn main:app --reload
```

**Or create a `.env` file:**
```bash
echo 'DATABASE_URL=postgresql://jacobsmith:jacobsmithmustgo@ls-b9bba8e36e6871b769e5ec6604833a4a0be3d3fd.c7mq6w6oszcl.us-west-2.rds.amazonaws.com:5432/postgres' > .env
```

**Terminal 2 - Frontend:**
```bash
cd no-more-jacob-smith-ui
npm install
npm run dev
```

Visit: http://localhost:5173

---

## Option 2: Deploy to AWS (Production)

Follow the step-by-step guide in **[AWS_QUICK_START.md](./AWS_QUICK_START.md)**

**Quick summary:**
1. Create Lightsail PostgreSQL database
2. Deploy to App Runner (connect GitHub)
3. Set environment variables
4. Update Amplify with API URL

**Time needed:** ~15 minutes

---

## Which Should You Do?

- **Testing/Development**: Run locally (Option 1)
- **Production/Live**: Deploy to AWS (Option 2)

