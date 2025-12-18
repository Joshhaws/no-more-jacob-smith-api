from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
import models
import schemas
from database import SessionLocal, engine

# Create database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Strava Segment Tracker API", version="1.0.0")


# Auto-seed test data on startup if database is empty
@app.on_event("startup")
def seed_on_startup():
    db = SessionLocal()
    try:
        count = db.query(models.Item).count()
        if count == 0:
            # Seed test data
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
                    "difficulty": 7,
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
                    "difficulty": 6,
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
                    "difficulty": 8,
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
                    "difficulty": 5,
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
                    "difficulty": 1,
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
                    "difficulty": 4,
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
                    "difficulty": 6,
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
                    "difficulty": 9,
                    "last_attempt_date": "8/15/2024",
                    "strava_url": "https://www.strava.com/segments/12352"
                }
            ]
            
            for segment_data in test_segments:
                db_item = models.Item(**segment_data)
                db.add(db_item)
            
            db.commit()
            print(f"✓ Auto-seeded {len(test_segments)} test segments")
    finally:
        db.close()

# Add CORS middleware to allow frontend to access the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "http://127.0.0.1:5173"],
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
    db_item = models.Item(**item.model_dump())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


@app.get("/items/", response_model=List[schemas.Item])
def read_items(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all items"""
    items = db.query(models.Item).offset(skip).limit(limit).all()
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


@app.delete("/items/{item_id}")
def delete_item(item_id: int, db: Session = Depends(get_db)):
    """Delete an item"""
    db_item = db.query(models.Item).filter(models.Item.id == item_id).first()
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    
    db.delete(db_item)
    db.commit()
    return {"message": "Item deleted successfully"}


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
            "difficulty": 7,
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
            "difficulty": 6,
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
            "difficulty": 8,
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
            "difficulty": 5,
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
            "difficulty": 1,
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
            "difficulty": 4,
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
            "difficulty": 6,
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
            "difficulty": 9,
            "last_attempt_date": "8/15/2024",
            "strava_url": "https://www.strava.com/segments/12352"
        }
    ]
    
    for segment_data in test_segments:
        db_item = models.Item(**segment_data)
        db.add(db_item)
    
    db.commit()
    return {"message": f"Successfully seeded {len(test_segments)} test segments"}

