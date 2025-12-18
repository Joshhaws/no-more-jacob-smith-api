# Quick Run Guide

## Option 1: Run Locally (Testing)

**Terminal 1 - Backend:**
```bash
cd no-more-jacob-smith-api
pip install -r requirements.txt
uvicorn main:app --reload
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

Follow the step-by-step guide in **DEPLOY_NOW.md**

**Quick summary:**
1. Create RDS database in AWS Console
2. Deploy to App Runner (connect GitHub)
3. Set environment variables
4. Update Amplify with API URL

**Time needed:** ~15 minutes

---

## Which Should You Do?

- **Testing/Development**: Run locally (Option 1)
- **Production/Live**: Deploy to AWS (Option 2)

