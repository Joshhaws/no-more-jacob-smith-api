#!/usr/bin/env python3
"""
ETL script to load multiple Strava segments into the database.
Usage: python load_segments.py
"""

import os
import sys
from dotenv import load_dotenv
from sqlalchemy.orm import Session
import httpx
from datetime import datetime, timedelta
import asyncio

# Import database and models
from database import SessionLocal
import models

# Load environment variables
load_dotenv()

# Strava segment IDs to load
SEGMENT_IDS = [
    8403912,
    13651993,
    16075927,
    18422851,
    20575625,
    20604418,
    22773897,
    23438807,
    23438840,
    24187653,
    24493380,
    24510396,
    26541273,
    31728133,
    31728137,
    34399452,
    34256984,
    37539566,
    37539572,
    37602106,
    37736878,
    37736883,
    38243476,
    39573933,
    40369467,
    32885277,
]


async def get_valid_access_token_async(user: models.User, db: Session):
    """Get valid access token, refreshing if needed"""
    if not user.strava_access_token:
        return None
    
    # Check if token is expired or expires soon (within 5 minutes)
    if user.token_expires_at and user.token_expires_at <= datetime.utcnow() + timedelta(minutes=5):
        return await refresh_strava_token_async(user, db)
    
    return user.strava_access_token


async def refresh_strava_token_async(user: models.User, db: Session):
    """Refresh Strava access token"""
    if not user.strava_refresh_token:
        return None
    
    try:
        STRAVA_CLIENT_ID = os.getenv("STRAVA_CLIENT_ID")
        STRAVA_CLIENT_SECRET = os.getenv("STRAVA_CLIENT_SECRET")
        
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
        print(f"Error refreshing token: {e}")
        return None
    
    return None


async def fetch_segment_metadata(segment_id: int, access_token: str):
    """Fetch segment metadata from Strava API"""
    async with httpx.AsyncClient() as client:
        try:
            segment_response = await client.get(
                f"https://www.strava.com/api/v3/segments/{segment_id}",
                headers={"Authorization": f"Bearer {access_token}"},
                timeout=10.0
            )
            
            if segment_response.status_code != 200:
                if segment_response.status_code == 404:
                    return None, f"Segment {segment_id} not found"
                if segment_response.status_code == 401:
                    return None, f"Authentication failed for segment {segment_id}"
                return None, f"Error {segment_response.status_code} for segment {segment_id}"
            
            segment_data = segment_response.json()
            
            # Convert distance from meters to miles
            distance_meters = segment_data.get("distance", 0)
            distance_miles = distance_meters / 1609.34 if distance_meters > 0 else None
            
            # Convert elevation from meters to feet
            elevation_high = segment_data.get("elevation_high", 0)
            elevation_low = segment_data.get("elevation_low", 0)
            elevation_gain_meters = elevation_high - elevation_low if elevation_high > elevation_low else 0
            elevation_gain_feet = elevation_gain_meters * 3.28084 if elevation_gain_meters > 0 else None
            
            return {
                "segment_name": segment_data.get("name", ""),
                "distance": round(distance_miles, 2) if distance_miles else None,
                "elevation_gain": round(elevation_gain_feet, 1) if elevation_gain_feet else None,
                "elevation_loss": None,
                "strava_url": f"https://www.strava.com/segments/{segment_id}",
                "strava_segment_id": segment_id,
                "crown_holder": None,
                "crown_date": None,
                "crown_time": None,
                "crown_pace": None,
                "personal_best_time": None,
                "personal_best_pace": None,
                "personal_attempts": 0,
                "overall_attempts": 0,
                "last_attempt_date": None,
                "dibs": None,
            }, None
            
        except Exception as e:
            return None, f"Exception fetching segment {segment_id}: {str(e)}"


async def load_segments():
    """Main ETL function to load segments"""
    db = SessionLocal()
    
    try:
        # Check for Strava user
        user = db.query(models.User).first()
        if not user or not user.strava_access_token:
            print("❌ Error: No Strava user found. Please connect Strava first.")
            print("   Run the app and connect your Strava account, then run this script again.")
            return
        
        # Get valid access token
        access_token = await get_valid_access_token_async(user, db)
        if not access_token:
            print("❌ Error: Could not get valid Strava access token.")
            print("   Please reconnect your Strava account in the app.")
            return
        
        print(f"✓ Authenticated with Strava")
        print(f"📋 Loading {len(SEGMENT_IDS)} segments...\n")
        
        loaded_count = 0
        skipped_count = 0
        error_count = 0
        
        for segment_id in SEGMENT_IDS:
            # Check if segment already exists
            existing = db.query(models.Item).filter(
                models.Item.strava_segment_id == segment_id
            ).first()
            
            if existing:
                print(f"⏭️  Segment {segment_id}: Already exists ('{existing.segment_name}')")
                skipped_count += 1
                continue
            
            # Fetch segment metadata
            segment_data, error = await fetch_segment_metadata(segment_id, access_token)
            
            if error:
                print(f"❌ Segment {segment_id}: {error}")
                error_count += 1
                continue
            
            if not segment_data:
                print(f"❌ Segment {segment_id}: No data returned")
                error_count += 1
                continue
            
            # Create database item
            try:
                db_item = models.Item(**segment_data)
                db.add(db_item)
                db.commit()
                db.refresh(db_item)
                print(f"✓ Segment {segment_id}: Loaded '{segment_data['segment_name']}' ({segment_data['distance']} mi, {segment_data['elevation_gain']} ft)")
                loaded_count += 1
            except Exception as e:
                db.rollback()
                print(f"❌ Segment {segment_id}: Database error - {str(e)}")
                error_count += 1
        
        print(f"\n{'='*60}")
        print(f"📊 Summary:")
        print(f"   ✓ Loaded: {loaded_count}")
        print(f"   ⏭️  Skipped (already exists): {skipped_count}")
        print(f"   ❌ Errors: {error_count}")
        print(f"   📋 Total: {len(SEGMENT_IDS)}")
        print(f"{'='*60}")
        
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    asyncio.run(load_segments())

