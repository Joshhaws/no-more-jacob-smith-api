#!/usr/bin/env python3
"""
Script to create database tables and seed test data for the Strava Segment Tracker API.
This ensures the database schema is set up correctly and populated with test segments.
"""

import os
import re
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import models

# Load environment variables
load_dotenv()

# Get database URL
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError(
        "DATABASE_URL environment variable is required. "
        "Format: postgresql://username:password@host:port/database"
    )

# Handle PostgreSQL URL format
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# Create engine and session
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create all tables
print("Creating database tables...")
models.Base.metadata.create_all(bind=engine)
print("✓ Database tables created successfully!")
print("\nTables created:")
for table_name in models.Base.metadata.tables.keys():
    print(f"  - {table_name}")

# Seed test data
print("\nSeeding test data...")
db = SessionLocal()

# Check if User table exists and is ready
print("\nChecking User table...")
try:
    user_count = db.query(models.User).count()
    print(f"✓ User table ready (contains {user_count} user(s))")
except Exception as e:
    print(f"⚠ User table check: {e}")
try:
    count = db.query(models.Item).count()
    if count > 0:
        print(f"⚠ Database already has {count} items. Skipping seed.")
    else:
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
            # Extract segment ID from Strava URL if present
            if segment_data.get("strava_url"):
                match = re.search(r'/segments/(\d+)', segment_data["strava_url"])
                if match:
                    segment_data["strava_segment_id"] = int(match.group(1))
            
            db_item = models.Item(**segment_data)
            db.add(db_item)
        
        db.commit()
        print(f"✓ Successfully seeded {len(test_segments)} test segments!")
        
        # Update existing segments to extract segment IDs from URLs
        print("\nUpdating existing segments with Strava segment IDs...")
        existing_items = db.query(models.Item).filter(models.Item.strava_segment_id == None).all()
        updated_count = 0
        for item in existing_items:
            if item.strava_url:
                match = re.search(r'/segments/(\d+)', item.strava_url)
                if match:
                    item.strava_segment_id = int(match.group(1))
                    updated_count += 1
        if updated_count > 0:
            db.commit()
            print(f"✓ Updated {updated_count} existing segments with Strava segment IDs")
        else:
            print("✓ No segments needed updating")
finally:
    db.close()

print("\n✓ Database setup complete!")
print("You can now run the API server with: uvicorn main:app --reload")

