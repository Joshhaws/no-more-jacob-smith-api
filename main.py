from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from typing import List, Optional
import os
import models
import schemas
from database import SessionLocal, engine
import httpx
from datetime import datetime, timedelta
import re

# Create database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Strava Segment Tracker API", version="1.0.0")


# Note: Database tables are created automatically on startup.
# To seed test data, use the /seed/ endpoint or run create_tables.py

# Add CORS middleware to allow frontend to access the API
# Get allowed origins from environment variable or use defaults
allowed_origins = os.getenv(
    "ALLOWED_ORIGINS",
    "http://localhost:5173,http://localhost:3000,http://127.0.0.1:5173"
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
def read_root():
    return {"message": "Welcome to FastAPI CRUD API"}


@app.post("/items/", response_model=schemas.Item)
def create_item(item: schemas.ItemCreate, db: Session = Depends(get_db)):
    """Create a new item"""
    try:
        # Check for duplicate segment by strava_segment_id
        if item.strava_segment_id:
            existing_item = db.query(models.Item).filter(
                models.Item.strava_segment_id == item.strava_segment_id
            ).first()
            if existing_item:
                raise HTTPException(
                    status_code=400,
                    detail=f"Segment with ID {item.strava_segment_id} already exists: '{existing_item.segment_name}'"
                )
        
        # Also check by strava_url as a fallback
        if item.strava_url:
            existing_item = db.query(models.Item).filter(
                models.Item.strava_url == item.strava_url
            ).first()
            if existing_item:
                raise HTTPException(
                    status_code=400,
                    detail=f"Segment with URL '{item.strava_url}' already exists: '{existing_item.segment_name}'"
                )
        
        item_data = item.model_dump()
        print(f"Creating item with data: {list(item_data.keys())}")
        print(f"Polyline present: {bool(item_data.get('polyline'))}")
        print(f"Start coordinates: {item_data.get('start_latitude')}, {item_data.get('start_longitude')}")
        
        db_item = models.Item(**item_data)
        db.add(db_item)
        db.commit()
        db.refresh(db_item)
        
        print(f"Created item ID {db_item.id} with polyline: {bool(db_item.polyline)}")
        return db_item
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        import traceback
        error_trace = traceback.format_exc()
        print(f"Error creating item: {error_trace}")
        raise HTTPException(status_code=400, detail=f"Error creating item: {str(e)}")


@app.get("/items/", response_model=List[schemas.Item])
def read_items(skip: int = 0, limit: int = 100, completed: Optional[bool] = None, db: Session = Depends(get_db)):
    """Get all items, optionally filtered by completed status"""
    query = db.query(models.Item)
    if completed is not None:
        query = query.filter(models.Item.completed == completed)
    items = query.offset(skip).limit(limit).all()
    return items


@app.get("/items/{item_id}", response_model=schemas.Item)
def read_item(item_id: int, db: Session = Depends(get_db)):
    """Get a specific item by ID"""
    db_item = db.query(models.Item).filter(models.Item.id == item_id).first()
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return db_item


@app.put("/items/{item_id}", response_model=schemas.Item)
def update_item(item_id: int, item: schemas.ItemUpdate, db: Session = Depends(get_db)):
    """Update an existing item"""
    db_item = db.query(models.Item).filter(models.Item.id == item_id).first()
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    
    update_data = item.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_item, field, value)
    
    db.commit()
    db.refresh(db_item)
    return db_item


@app.put("/items/{item_id}/complete")
def toggle_complete_item(item_id: int, db: Session = Depends(get_db)):
    """Toggle the completed status of an item"""
    db_item = db.query(models.Item).filter(models.Item.id == item_id).first()
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    
    db_item.completed = not db_item.completed
    db.commit()
    db.refresh(db_item)
    return {"message": f"Item marked as {'completed' if db_item.completed else 'incomplete'}", "completed": db_item.completed}


@app.post("/seed/")
def seed_test_data(db: Session = Depends(get_db)):
    """Seed the database with test Strava segment data"""
    # Check if data already exists
    existing_count = db.query(models.Item).count()
    if existing_count > 0:
        return {"message": f"Database already has {existing_count} items. Use DELETE /items/{{id}} to clear if needed."}
    
    test_segments = [
        {
            "segment_name": "Here lies Dobby a free elf",
            "distance": 2.68,
            "elevation_gain": 275.0,
            "elevation_loss": None,
            "crown_holder": "Jacob Smith",
            "crown_date": "12-Aug-25",
            "crown_time": "22:55",
            "crown_pace": "8:35",
            "personal_best_time": "32:59:00",
            "personal_best_pace": "12:17",
            "personal_attempts": 1,
            "overall_attempts": 6,
            "last_attempt_date": "7/3/2025",
            "strava_url": "https://www.strava.com/segments/12345"
        },
        {
            "segment_name": "Full Miyagi",
            "distance": 2.98,
            "elevation_gain": 1070.0,
            "elevation_loss": None,
            "crown_holder": "Jacob Smith",
            "crown_date": "15-Dec-25",
            "crown_time": "23:04",
            "crown_pace": "7:45",
            "personal_best_time": "27:10:00",
            "personal_best_pace": "9:07",
            "personal_attempts": 5,
            "overall_attempts": 111,
            "last_attempt_date": "4/22/2025",
            "strava_url": "https://www.strava.com/segments/12346"
        },
        {
            "segment_name": "StairSense",
            "distance": 0.46,
            "elevation_gain": 332.0,
            "elevation_loss": None,
            "crown_holder": "Jacob Smith",
            "crown_date": "13-Dec-25",
            "crown_time": "16:18",
            "crown_pace": "8:38",
            "personal_best_time": None,
            "personal_best_pace": None,
            "personal_attempts": 0,
            "overall_attempts": 10,
            "last_attempt_date": "11/28/2025",
            "strava_url": "https://www.strava.com/segments/12347"
        },
        {
            "segment_name": "Boneyard Trail Up",
            "distance": 1.2,
            "elevation_gain": 450.0,
            "elevation_loss": None,
            "crown_holder": "Jacob Smith",
            "crown_date": "14-Jul-25",
            "crown_time": "18:30",
            "crown_pace": "9:25",
            "personal_best_time": None,
            "personal_best_pace": None,
            "personal_attempts": 0,
            "overall_attempts": 30,
            "last_attempt_date": "11/9/2024",
            "strava_url": "https://www.strava.com/segments/12348"
        },
        {
            "segment_name": "TM Tower out-n-back",
            "distance": 3.5,
            "elevation_gain": 800.0,
            "elevation_loss": None,
            "crown_holder": "Jacob Smith",
            "crown_date": "8-Jul-25",
            "crown_time": "28:15",
            "crown_pace": "8:04",
            "personal_best_time": None,
            "personal_best_pace": None,
            "personal_attempts": 0,
            "overall_attempts": 1129,
            "last_attempt_date": "12/8/2025",
            "strava_url": "https://www.strava.com/segments/12349"
        },
        {
            "segment_name": "Maple/Telegraph/Eagle/Woods loop",
            "distance": 4.2,
            "elevation_gain": 650.0,
            "elevation_loss": None,
            "crown_holder": None,
            "crown_date": None,
            "crown_time": None,
            "crown_pace": None,
            "personal_best_time": None,
            "personal_best_pace": None,
            "personal_attempts": 0,
            "overall_attempts": 45,
            "last_attempt_date": "10/6/2025",
            "strava_url": "https://www.strava.com/segments/12350"
        },
        {
            "segment_name": "I solemnly swear I am up to no good",
            "distance": 1.8,
            "elevation_gain": 380.0,
            "elevation_loss": None,
            "crown_holder": "Jacob Smith",
            "crown_date": "17-Jun-25",
            "crown_time": "14:22",
            "crown_pace": "7:58",
            "personal_best_time": None,
            "personal_best_pace": None,
            "personal_attempts": 0,
            "overall_attempts": 25,
            "last_attempt_date": "11/29/2024",
            "strava_url": "https://www.strava.com/segments/12351"
        },
        {
            "segment_name": "Lap Squaw (Kyev) peak plus the campground-parking lot only",
            "distance": 5.1,
            "elevation_gain": 1200.0,
            "elevation_loss": None,
            "crown_holder": "Jacob Smith",
            "crown_date": "4-Feb-25",
            "crown_time": "35:45",
            "crown_pace": "7:00",
            "personal_best_time": None,
            "personal_best_pace": None,
            "personal_attempts": 0,
            "overall_attempts": 88,
            "last_attempt_date": "8/15/2024",
            "strava_url": "https://www.strava.com/segments/12352"
        }
    ]
    
    for segment_data in test_segments:
        db_item = models.Item(**segment_data)
        db.add(db_item)
    
    db.commit()
    return {"message": f"Successfully seeded {len(test_segments)} test segments"}


# Strava OAuth Configuration
STRAVA_CLIENT_ID = os.getenv("STRAVA_CLIENT_ID")
STRAVA_CLIENT_SECRET = os.getenv("STRAVA_CLIENT_SECRET")
STRAVA_REDIRECT_URI = os.getenv("STRAVA_REDIRECT_URI", "http://localhost:5173/auth/callback")

# Helper function to get or create user
def get_or_create_user(db: Session, strava_id: int):
    user = db.query(models.User).filter(models.User.strava_id == strava_id).first()
    if not user:
        user = models.User(strava_id=strava_id)
        db.add(user)
        db.commit()
        db.refresh(user)
    return user


# Helper function to refresh Strava token
async def refresh_strava_token_async(user: models.User, db: Session):
    """Async version of token refresh"""
    if not user.strava_refresh_token:
        return None
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://www.strava.com/oauth/token",
                data={
                    "client_id": STRAVA_CLIENT_ID,
                    "client_secret": STRAVA_CLIENT_SECRET,
                    "grant_type": "refresh_token",
                    "refresh_token": user.strava_refresh_token,
                },
                timeout=10.0
            )
            
            if response.status_code != 200:
                print(f"Token refresh failed: {response.status_code} - {response.text}")
                return None
            
            token_data = response.json()
            
            if "access_token" in token_data:
                user.strava_access_token = token_data["access_token"]
                user.strava_refresh_token = token_data.get("refresh_token", user.strava_refresh_token)
                expires_in = token_data.get("expires_at", 0)
                user.token_expires_at = datetime.fromtimestamp(expires_in) if expires_in else None
                db.commit()
                return user.strava_access_token
    except Exception as e:
        import traceback
        print(f"Error refreshing token: {e}")
        print(traceback.format_exc())
        return None
    
    return None


def refresh_strava_token(user: models.User, db: Session):
    """Sync wrapper for token refresh (for backward compatibility)"""
    if not user.strava_refresh_token:
        return None
    
    try:
        import asyncio
        try:
            # Try to get the current event loop
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If loop is running, we can't use asyncio.run()
                # This shouldn't happen in sync context, but handle it
                raise RuntimeError("Cannot use asyncio.run() in running event loop")
        except RuntimeError:
            # No event loop, safe to use asyncio.run()
            pass
        
        return asyncio.run(refresh_strava_token_async(user, db))
    except Exception as e:
        import traceback
        print(f"Error in sync token refresh wrapper: {e}")
        print(traceback.format_exc())
        return None


# Helper function to get valid access token (async version for use in async endpoints)
async def get_valid_access_token_async(user: models.User, db: Session):
    if not user.strava_access_token:
        return None
    
    # Check if token is expired or expires soon (within 5 minutes)
    if user.token_expires_at and user.token_expires_at <= datetime.utcnow() + timedelta(minutes=5):
        return await refresh_strava_token_async(user, db)
    
    return user.strava_access_token


# Helper function to get valid access token (sync version for backward compatibility)
def get_valid_access_token(user: models.User, db: Session):
    if not user.strava_access_token:
        return None
    
    # Check if token is expired or expires soon (within 5 minutes)
    if user.token_expires_at and user.token_expires_at <= datetime.utcnow() + timedelta(minutes=5):
        return refresh_strava_token(user, db)
    
    return user.strava_access_token


# Extract segment ID from Strava URL
def extract_segment_id(strava_url: Optional[str]) -> Optional[int]:
    if not strava_url:
        return None
    match = re.search(r'/segments/(\d+)', strava_url)
    return int(match.group(1)) if match else None


@app.get("/auth/strava/authorize")
def strava_authorize():
    """Generate Strava OAuth authorization URL"""
    if not STRAVA_CLIENT_ID:
        raise HTTPException(status_code=500, detail="Strava client ID not configured")
    
    # Get backend URL from environment or use default
    backend_url = os.getenv("BACKEND_URL", "http://localhost:8000")
    redirect_uri = f"{backend_url}/auth/strava/callback"
    
    auth_url = (
        f"https://www.strava.com/oauth/authorize"
        f"?client_id={STRAVA_CLIENT_ID}"
        f"&redirect_uri={redirect_uri}"
        f"&response_type=code"
        f"&scope=activity:read_all"
        f"&approval_prompt=force"
    )
    
    return {"authorization_url": auth_url}


@app.get("/auth/strava/callback")
async def strava_callback(code: str, db: Session = Depends(get_db)):
    """Handle Strava OAuth callback"""
    if not STRAVA_CLIENT_ID or not STRAVA_CLIENT_SECRET:
        raise HTTPException(status_code=500, detail="Strava credentials not configured")
    
    frontend_url = os.getenv("FRONTEND_URL", "http://localhost:5173")
    
    try:
        async with httpx.AsyncClient() as client:
            # Exchange code for token
            response = await client.post(
                "https://www.strava.com/oauth/token",
                data={
                    "client_id": STRAVA_CLIENT_ID,
                    "client_secret": STRAVA_CLIENT_SECRET,
                    "code": code,
                    "grant_type": "authorization_code",
                },
            )
            
            if response.status_code != 200:
                raise HTTPException(status_code=400, detail="Failed to exchange authorization code")
            
            token_data = response.json()
            athlete = token_data.get("athlete", {})
            strava_id = athlete.get("id")
            
            if not strava_id:
                raise HTTPException(status_code=400, detail="No athlete ID in response")
            
            # Get or create user
            user = get_or_create_user(db, strava_id)
            
            # Update tokens
            user.strava_access_token = token_data["access_token"]
            user.strava_refresh_token = token_data.get("refresh_token")
            expires_at = token_data.get("expires_at")
            if expires_at:
                user.token_expires_at = datetime.fromtimestamp(expires_at)
            user.updated_at = datetime.utcnow()
            db.commit()
            
            # Redirect to frontend with success
            return RedirectResponse(url=f"{frontend_url}?strava_connected=true")
            
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=400, detail=f"Strava API error: {e.response.text}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error connecting to Strava: {str(e)}")


@app.get("/auth/strava/status", response_model=schemas.StravaAuthStatus)
def strava_auth_status(db: Session = Depends(get_db)):
    """Check Strava connection status"""
    # For now, return the first user's status (single user app)
    # In production, you'd use session/auth to identify the user
    user = db.query(models.User).first()
    
    if user and user.strava_access_token:
        # Check if token is still valid
        token = get_valid_access_token(user, db)
        if token:
            # Try to get athlete name
            athlete_name = None
            try:
                import httpx
                response = httpx.get(
                    "https://www.strava.com/api/v3/athlete",
                    headers={"Authorization": f"Bearer {token}"},
                    timeout=5.0
                )
                if response.status_code == 200:
                    athlete_data = response.json()
                    athlete_name = athlete_data.get("firstname", "") + " " + athlete_data.get("lastname", "")
                    athlete_name = athlete_name.strip()
            except Exception:
                pass  # If we can't get athlete name, just return connected=True
            
            return schemas.StravaAuthStatus(connected=True, athlete_name=athlete_name)
    
    return schemas.StravaAuthStatus(connected=False)


@app.get("/auth/strava/athlete")
async def get_athlete_info(db: Session = Depends(get_db)):
    """Get authenticated athlete information from Strava"""
    user = db.query(models.User).first()
    
    if not user or not user.strava_access_token:
        raise HTTPException(status_code=401, detail="Not authenticated with Strava")
    
    access_token = await get_valid_access_token_async(user, db)
    if not access_token:
        raise HTTPException(status_code=401, detail="Strava authentication expired. Please reconnect.")
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://www.strava.com/api/v3/athlete",
                headers={"Authorization": f"Bearer {access_token}"},
                timeout=10.0
            )
            
            if response.status_code != 200:
                if response.status_code == 401:
                    raise HTTPException(status_code=401, detail="Strava authentication expired. Please reconnect.")
                raise HTTPException(status_code=response.status_code, detail="Failed to fetch athlete info")
            
            athlete_data = response.json()
            firstname = athlete_data.get("firstname", "")
            lastname = athlete_data.get("lastname", "")
            athlete_name = f"{firstname} {lastname}".strip()
            
            return {
                "athlete_name": athlete_name,
                "athlete_id": athlete_data.get("id"),
                "firstname": firstname,
                "lastname": lastname
            }
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 401:
            raise HTTPException(status_code=401, detail="Strava authentication expired. Please reconnect.")
        raise HTTPException(status_code=e.response.status_code, detail=f"Strava API error: {e.response.text[:200]}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching athlete info: {str(e)}")


@app.post("/auth/strava/disconnect")
def strava_disconnect(db: Session = Depends(get_db)):
    """Disconnect Strava account"""
    user = db.query(models.User).first()
    if user:
        user.strava_access_token = None
        user.strava_refresh_token = None
        user.token_expires_at = None
        db.commit()
    
    return {"message": "Strava account disconnected"}


# Helper function to fetch segment times from Strava
async def fetch_segment_times_from_strava(segment_id: int, access_token: str) -> schemas.StravaSegmentTime:
    """Fetch segment times from Strava API"""
    async with httpx.AsyncClient() as client:
        # Get segment details
        segment_response = await client.get(
            f"https://www.strava.com/api/v3/segments/{segment_id}",
            headers={"Authorization": f"Bearer {access_token}"},
            timeout=10.0
        )
        
        if segment_response.status_code != 200:
            if segment_response.status_code == 404:
                raise HTTPException(status_code=404, detail="Segment not found")
            elif segment_response.status_code == 401:
                raise HTTPException(status_code=401, detail="Strava authentication expired. Please reconnect your Strava account.")
            elif segment_response.status_code == 429:
                raise HTTPException(status_code=429, detail="Rate limit exceeded. Please try again in a few minutes.")
            else:
                error_text = segment_response.text[:200] if segment_response.text else "Unknown error"
                raise HTTPException(
                    status_code=segment_response.status_code, 
                    detail=f"Strava API error ({segment_response.status_code}): {error_text}"
                )
        
        segment_data = segment_response.json()
        segment_name = segment_data.get("name", "")
        distance_meters = segment_data.get("distance", 0)
        elevation_high = segment_data.get("elevation_high", 0)
        elevation_low = segment_data.get("elevation_low", 0)
        elevation_gain_meters = elevation_high - elevation_low if elevation_high > elevation_low else 0
        
        # Try to get leaderboard/KOM information (may be deprecated but worth trying)
        crown_holder = None
        crown_time = None
        crown_date = None
        crown_pace = None
        
        try:
            leaderboard_response = await client.get(
                f"https://www.strava.com/api/v3/segments/{segment_id}/leaderboard",
                headers={"Authorization": f"Bearer {access_token}"},
                params={"per_page": 1},  # Just get the top entry
                timeout=5.0
            )
            
            if leaderboard_response.status_code == 200:
                leaderboard_data = leaderboard_response.json()
                entries = leaderboard_data.get("entries", [])
                
                if entries:
                    # Get the top entry (KOM/QOM)
                    top_entry = entries[0]
                    athlete = top_entry.get("athlete_name", "")
                    elapsed_time = top_entry.get("elapsed_time")
                    
                    if athlete and elapsed_time:
                        crown_holder = athlete
                        
                        # Convert seconds to MM:SS format
                        minutes = elapsed_time // 60
                        seconds = elapsed_time % 60
                        crown_time = f"{int(minutes)}:{int(seconds):02d}"
                        
                        # Calculate pace
                        if distance_meters > 0:
                            distance_miles = distance_meters / 1609.34
                            pace_seconds_per_mile = elapsed_time / distance_miles
                            pace_minutes = int(pace_seconds_per_mile // 60)
                            pace_seconds = int(pace_seconds_per_mile % 60)
                            crown_pace = f"{pace_minutes}:{pace_seconds:02d}"
                        
                        # Get date if available
                        start_date = top_entry.get("start_date")
                        if start_date:
                            try:
                                dt = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
                                crown_date = dt.strftime("%m/%d/%Y")
                            except:
                                pass
        except Exception as e:
            # Leaderboard endpoint may be deprecated or unavailable - that's okay
            print(f"Could not fetch leaderboard data: {e}")
        
        # Get athlete's segment stats
        stats_response = await client.get(
            f"https://www.strava.com/api/v3/segments/{segment_id}/all_efforts",
            headers={"Authorization": f"Bearer {access_token}"},
            params={"per_page": 200},  # Get all efforts to find best
        )
        
        personal_best_time = None
        personal_best_pace = None
        personal_best_grade_adjusted_pace = None
        personal_attempts = 0
        last_attempt_date = None
        personal_best_activity_id = None
        
        if stats_response.status_code == 200:
            efforts = stats_response.json()
            personal_attempts = len(efforts)
            
            if efforts:
                # Find best effort
                best_effort = min(efforts, key=lambda e: e.get("elapsed_time", float('inf')))
                elapsed_time = best_effort.get("elapsed_time")
                
                # Get activity ID from the best effort
                activity = best_effort.get("activity")
                if activity:
                    personal_best_activity_id = activity.get("id")
                
                if elapsed_time and distance_meters > 0:
                    # Convert seconds to MM:SS format
                    minutes = elapsed_time // 60
                    seconds = elapsed_time % 60
                    personal_best_time = f"{int(minutes)}:{int(seconds):02d}"
                    
                    # Calculate pace
                    distance_miles = distance_meters / 1609.34
                    pace_seconds_per_mile = elapsed_time / distance_miles
                    pace_minutes = int(pace_seconds_per_mile // 60)
                    pace_seconds = int(pace_seconds_per_mile % 60)
                    personal_best_pace = f"{pace_minutes}:{pace_seconds:02d}"
                    
                    # Calculate Grade Adjusted Pace (GAP)
                    # GAP adjusts pace to what it would be on flat terrain
                    # Formula: GAP = actual_pace / (1 + k * grade)
                    # Where k ≈ 0.04 for uphill, k ≈ 0.02 for downhill
                    # Grade = elevation_gain / distance (as decimal)
                    if elevation_gain_meters > 0:
                        grade = elevation_gain_meters / distance_meters  # Grade as decimal (e.g., 0.05 = 5%)
                        # Use k = 0.04 for uphill segments (positive grade)
                        # This is a simplified model - Strava's exact formula is proprietary
                        k = 0.04 if grade > 0 else 0.02
                        gap_factor = 1 + (k * grade)
                        gap_seconds_per_mile = pace_seconds_per_mile / gap_factor
                        gap_minutes = int(gap_seconds_per_mile // 60)
                        gap_seconds = int(gap_seconds_per_mile % 60)
                        personal_best_grade_adjusted_pace = f"{gap_minutes}:{gap_seconds:02d}"
                    elif elevation_gain_meters == 0:
                        # Flat segment - GAP equals actual pace
                        personal_best_grade_adjusted_pace = personal_best_pace
                
                # Get last attempt date (most recent)
                latest_effort = max(efforts, key=lambda e: e.get("start_date", ""))
                start_date = latest_effort.get("start_date")
                if start_date:
                    try:
                        dt = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
                        last_attempt_date = dt.strftime("%m/%d/%Y")
                    except:
                        pass
        
        # Get polyline and start coordinates from segment data
        polyline = None
        start_latitude = None
        start_longitude = None
        
        try:
            segment_response = await client.get(
                f"https://www.strava.com/api/v3/segments/{segment_id}",
                headers={"Authorization": f"Bearer {access_token}"},
                timeout=10.0
            )
            if segment_response.status_code == 200:
                segment_data = segment_response.json()
                polyline = segment_data.get("polyline")
                start_latitude = segment_data.get("start_latitude")
                start_longitude = segment_data.get("start_longitude")
        except Exception:
            pass  # If we can't get polyline, continue without it
        
        return schemas.StravaSegmentTime(
            segment_id=segment_id,
            segment_name=segment_name,
            personal_best_time=personal_best_time,
            personal_best_pace=personal_best_pace,
            personal_best_grade_adjusted_pace=personal_best_grade_adjusted_pace,
            personal_attempts=personal_attempts if personal_attempts > 0 else None,
            last_attempt_date=last_attempt_date,
            personal_best_activity_id=personal_best_activity_id,
            polyline=polyline,
            start_latitude=start_latitude,
            start_longitude=start_longitude,
            crown_holder=crown_holder,
            crown_time=crown_time,
            crown_date=crown_date,
            crown_pace=crown_pace,
        )


@app.get("/strava/segments/{segment_id}/times", response_model=schemas.StravaSegmentTime)
async def get_segment_times(segment_id: int, db: Session = Depends(get_db)):
    """Get personal best time for a segment from Strava, with database fallback for rate limits"""
    user = db.query(models.User).first()
    
    if not user or not user.strava_access_token:
        raise HTTPException(status_code=401, detail="Strava not connected")
    
    access_token = await get_valid_access_token_async(user, db)
    if not access_token:
        raise HTTPException(status_code=401, detail="Invalid Strava token. Please reconnect.")
    
    # Get database data as fallback
    db_item = db.query(models.Item).filter(models.Item.strava_segment_id == segment_id).first()
    
    # Log which segment we're trying to fetch
    print(f"Fetching segment times for segment_id: {segment_id}")
    
    try:
        return await fetch_segment_times_from_strava(segment_id, access_token)
    except HTTPException as e:
        # For rate limits (429), return database data if available
        if e.status_code == 429 and db_item:
            print(f"Rate limit hit for segment {segment_id}, returning database data")
            return schemas.StravaSegmentTime(
                segment_id=segment_id,
                segment_name=db_item.segment_name or "",
                personal_best_time=db_item.personal_best_time,
                personal_best_pace=db_item.personal_best_pace,
                personal_best_grade_adjusted_pace=None,  # Not stored in DB
                personal_attempts=db_item.personal_attempts if db_item.personal_attempts else None,
                last_attempt_date=db_item.last_attempt_date,
                personal_best_activity_id=None,  # Not stored in DB
                polyline=db_item.polyline,
                start_latitude=db_item.start_latitude,
                start_longitude=db_item.start_longitude,
                crown_holder=db_item.crown_holder,
                crown_time=db_item.crown_time,
                crown_date=db_item.crown_date,
                crown_pace=db_item.crown_pace,
            )
        # For auth errors, still raise
        if e.status_code == 401:
            raise
        # Log the error for debugging
        print(f"HTTPException fetching segment {segment_id}: {e.status_code} - {e.detail}")
        raise
    except httpx.HTTPStatusError as e:
        print(f"HTTPStatusError fetching segment {segment_id}: {e.response.status_code} - {e.response.text[:200]}")
        # For rate limits, return database data if available
        if e.response.status_code == 429 and db_item:
            print(f"Rate limit hit for segment {segment_id}, returning database data")
            return schemas.StravaSegmentTime(
                segment_id=segment_id,
                segment_name=db_item.segment_name or "",
                personal_best_time=db_item.personal_best_time,
                personal_best_pace=db_item.personal_best_pace,
                personal_best_grade_adjusted_pace=None,
                personal_attempts=db_item.personal_attempts if db_item.personal_attempts else None,
                last_attempt_date=db_item.last_attempt_date,
                personal_best_activity_id=None,
                polyline=db_item.polyline,
                start_latitude=db_item.start_latitude,
                start_longitude=db_item.start_longitude,
                crown_holder=db_item.crown_holder,
                crown_time=db_item.crown_time,
                crown_date=db_item.crown_date,
                crown_pace=db_item.crown_pace,
            )
        if e.response.status_code == 401:
            raise HTTPException(status_code=401, detail="Strava token expired. Please reconnect.")
        elif e.response.status_code == 404:
            raise HTTPException(status_code=404, detail=f"Segment {segment_id} not found on Strava. It may have been deleted or made private.")
        raise HTTPException(status_code=e.response.status_code, detail=f"Strava API error ({e.response.status_code}): {e.response.text[:200]}")
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"Error fetching segment times for {segment_id}: {error_trace}")
        raise HTTPException(status_code=500, detail=f"Error fetching segment data: {str(e)}")


@app.get("/strava/segments/{segment_id}/metadata", response_model=schemas.StravaSegmentMetadata)
async def get_segment_metadata(segment_id: int, db: Session = Depends(get_db)):
    """Get segment metadata (name, distance, elevation, crown info) from Strava"""
    # Require Strava authentication
    user = db.query(models.User).first()
    
    if not user or not user.strava_access_token:
        raise HTTPException(status_code=401, detail="Strava authentication required. Please connect your Strava account.")
    
    access_token = await get_valid_access_token_async(user, db)
    if not access_token:
        raise HTTPException(status_code=401, detail="Invalid Strava token. Please reconnect your Strava account.")
    
    try:
        async with httpx.AsyncClient() as client:
            segment_response = await client.get(
                f"https://www.strava.com/api/v3/segments/{segment_id}",
                headers={"Authorization": f"Bearer {access_token}"},
                timeout=10.0
            )
            
            if segment_response.status_code != 200:
                if segment_response.status_code == 401:
                    raise HTTPException(status_code=401, detail="Strava authentication expired. Please reconnect your Strava account.")
                if segment_response.status_code == 404:
                    raise HTTPException(status_code=404, detail="Segment not found")
                error_text = segment_response.text[:200] if segment_response.text else "Unknown error"
                raise HTTPException(status_code=segment_response.status_code, detail=f"Strava API error: {error_text}")
            
            segment_data = segment_response.json()
            
            # Convert distance from meters to miles
            distance_meters = segment_data.get("distance", 0)
            distance_miles = distance_meters / 1609.34 if distance_meters > 0 else None
            
            # Convert elevation from meters to feet
            # Strava provides elevation_high and elevation_low, but we want total elevation gain
            # For segments, we can use average_grade and distance to estimate, or use elevation_high - elevation_low
            elevation_high = segment_data.get("elevation_high", 0)
            elevation_low = segment_data.get("elevation_low", 0)
            elevation_gain_meters = elevation_high - elevation_low if elevation_high > elevation_low else 0
            elevation_gain_feet = elevation_gain_meters * 3.28084 if elevation_gain_meters > 0 else None
            
            # Get polyline and start coordinates for map display
            # Strava API may return polyline in different formats:
            # 1. Direct "polyline" field
            # 2. Inside "map" object as "polyline" or "summary_polyline"
            polyline = segment_data.get("polyline")
            if not polyline or (isinstance(polyline, str) and polyline.strip() == ""):
                map_obj = segment_data.get("map", {})
                polyline = map_obj.get("polyline") or map_obj.get("summary_polyline")
                # Convert empty strings to None
                if polyline and isinstance(polyline, str) and polyline.strip() == "":
                    polyline = None
            
            # Strava may return coordinates as:
            # 1. Separate "start_latitude" and "start_longitude" fields
            # 2. "start_latlng" array [latitude, longitude]
            start_latitude = segment_data.get("start_latitude")
            start_longitude = segment_data.get("start_longitude")
            
            if not start_latitude or not start_longitude:
                start_latlng = segment_data.get("start_latlng")
                if start_latlng and isinstance(start_latlng, list) and len(start_latlng) >= 2:
                    start_latitude = start_latlng[0]
                    start_longitude = start_latlng[1]
            
            # Convert to None if invalid (must be valid float/int and within valid lat/lng ranges)
            if start_latitude is not None:
                if not isinstance(start_latitude, (int, float)) or not (-90 <= start_latitude <= 90):
                    start_latitude = None
            if start_longitude is not None:
                if not isinstance(start_longitude, (int, float)) or not (-180 <= start_longitude <= 180):
                    start_longitude = None
            
            # Log for debugging
            print(f"Segment {segment_id} map data: polyline={'present' if polyline else 'missing'}, "
                  f"start_lat={start_latitude}, start_lng={start_longitude}")
            
            # Note: Strava deprecated the leaderboard API in 2020, so crown/KOM information
            # is no longer available via the API. Users must manually enter this information
            # or view it directly on Strava's website.
            crown_holder = None
            crown_time = None
            crown_date = None
            crown_pace = None
            
            # Attempt to fetch leaderboard data (will likely fail due to API deprecation)
            # This is kept for potential future API changes or if Strava re-enables it
            try:
                leaderboard_response = await client.get(
                    f"https://www.strava.com/api/v3/segments/{segment_id}/leaderboard",
                    headers={"Authorization": f"Bearer {access_token}"},
                    params={"per_page": 1},
                    timeout=5.0
                )
                
                if leaderboard_response.status_code == 200:
                    leaderboard_data = leaderboard_response.json()
                    entries = leaderboard_data.get("entries", [])
                    
                    if entries:
                        top_entry = entries[0]
                        athlete = top_entry.get("athlete_name", "")
                        elapsed_time = top_entry.get("elapsed_time")
                        
                        if athlete and elapsed_time:
                            crown_holder = athlete
                            
                            # Convert seconds to MM:SS format
                            minutes = elapsed_time // 60
                            seconds = elapsed_time % 60
                            crown_time = f"{int(minutes)}:{int(seconds):02d}"
                            
                            # Calculate pace
                            if distance_meters > 0:
                                distance_miles = distance_meters / 1609.34
                                pace_seconds_per_mile = elapsed_time / distance_miles
                                pace_minutes = int(pace_seconds_per_mile // 60)
                                pace_seconds = int(pace_seconds_per_mile % 60)
                                crown_pace = f"{pace_minutes}:{pace_seconds:02d}"
                            
                            # Get date if available
                            start_date = top_entry.get("start_date")
                            if start_date:
                                try:
                                    dt = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
                                    crown_date = dt.strftime("%m/%d/%Y")
                                except:
                                    pass
            except Exception as e:
                # Leaderboard endpoint is deprecated - this is expected
                # Crown information will remain None and can be manually entered
                pass
            
            metadata = schemas.StravaSegmentMetadata(
                segment_id=segment_id,
                segment_name=segment_data.get("name", ""),
                distance=round(distance_miles, 2) if distance_miles else None,
                elevation_gain=round(elevation_gain_feet, 1) if elevation_gain_feet else None,
                strava_url=f"https://www.strava.com/segments/{segment_id}",
                polyline=polyline,
                start_latitude=start_latitude,
                start_longitude=start_longitude,
                crown_holder=crown_holder,
                crown_time=crown_time,
                crown_date=crown_date,
                crown_pace=crown_pace,
            )
            
            # Update existing segment in database with polyline data if it exists
            existing_item = db.query(models.Item).filter(
                models.Item.strava_segment_id == segment_id
            ).first()
            
            if existing_item:
                existing_item.polyline = polyline
                existing_item.start_latitude = start_latitude
                existing_item.start_longitude = start_longitude
                db.commit()
            
            return metadata
            
    except HTTPException:
        raise
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 401:
            raise HTTPException(status_code=401, detail="Strava authentication expired. Please reconnect your Strava account.")
        if e.response.status_code == 404:
            raise HTTPException(status_code=404, detail="Segment not found")
        error_text = e.response.text[:200] if e.response.text else "Unknown error"
        raise HTTPException(status_code=e.response.status_code, detail=f"Strava API error: {error_text}")
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="Request to Strava API timed out. Please try again.")
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"Error fetching segment metadata: {error_trace}")
        raise HTTPException(status_code=500, detail=f"Error fetching segment metadata: {str(e)}")

