#!/usr/bin/env python3
"""
Script to fetch missing map data (polyline and coordinates) for all segments.
This will update existing records in the database with map data from Strava API.
Usage: python fetch_missing_map_data.py
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


async def fetch_segment_map_data(segment_id: int, access_token: str):
    """Fetch map data (polyline and coordinates) from Strava API"""
    async with httpx.AsyncClient() as client:
        try:
            segment_response = await client.get(
                f"https://www.strava.com/api/v3/segments/{segment_id}",
                headers={"Authorization": f"Bearer {access_token}"},
                timeout=10.0
            )
            
            if segment_response.status_code != 200:
                if segment_response.status_code == 404:
                    return None, None, None, f"Segment {segment_id} not found"
                if segment_response.status_code == 401:
                    return None, None, None, f"Authentication failed for segment {segment_id}"
                return None, None, None, f"Error {segment_response.status_code} for segment {segment_id}"
            
            segment_data = segment_response.json()
            
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
            
            return polyline, start_latitude, start_longitude, None
            
        except Exception as e:
            return None, None, None, f"Exception fetching segment {segment_id}: {str(e)}"


async def update_missing_map_data():
    """Main function to update missing map data for all segments"""
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
        
        # Find all items that have a strava_segment_id but are missing map data
        items_missing_map = db.query(models.Item).filter(
            models.Item.strava_segment_id.isnot(None)
        ).filter(
            (models.Item.polyline.is_(None)) | 
            (models.Item.start_latitude.is_(None)) | 
            (models.Item.start_longitude.is_(None))
        ).all()
        
        if not items_missing_map:
            print("✓ All segments already have map data!")
            return
        
        print(f"📋 Found {len(items_missing_map)} segments missing map data\n")
        
        updated_count = 0
        skipped_count = 0
        error_count = 0
        no_data_count = 0
        
        for item in items_missing_map:
            segment_id = item.strava_segment_id
            segment_name = item.segment_name or f"Segment {segment_id}"
            
            # Check what's missing
            missing = []
            if not item.polyline:
                missing.append("polyline")
            if not item.start_latitude:
                missing.append("start_latitude")
            if not item.start_longitude:
                missing.append("start_longitude")
            
            print(f"🔄 [{updated_count + skipped_count + error_count + no_data_count + 1}/{len(items_missing_map)}] "
                  f"Segment {segment_id} ('{segment_name}') - Missing: {', '.join(missing)}")
            
            # Fetch map data from Strava
            polyline, start_lat, start_lng, error = await fetch_segment_map_data(segment_id, access_token)
            
            if error:
                print(f"   ❌ Error: {error}")
                error_count += 1
                continue
            
            # Check if we got any new data
            has_new_data = False
            updates = {}
            
            if polyline and not item.polyline:
                updates['polyline'] = polyline
                has_new_data = True
            
            if start_lat and not item.start_latitude:
                updates['start_latitude'] = start_lat
                has_new_data = True
            
            if start_lng and not item.start_longitude:
                updates['start_longitude'] = start_lng
                has_new_data = True
            
            if not has_new_data:
                print(f"   ⏭️  No map data available from Strava")
                no_data_count += 1
                continue
            
            # Update the database record
            try:
                for field, value in updates.items():
                    setattr(item, field, value)
                
                db.commit()
                db.refresh(item)
                
                updated_fields = list(updates.keys())
                print(f"   ✓ Updated: {', '.join(updated_fields)}")
                updated_count += 1
                
                # Small delay to avoid rate limiting
                await asyncio.sleep(0.5)
                
            except Exception as e:
                db.rollback()
                print(f"   ❌ Database error: {str(e)}")
                error_count += 1
        
        print(f"\n{'='*60}")
        print(f"📊 Summary:")
        print(f"   ✓ Updated: {updated_count}")
        print(f"   ⏭️  No data available: {no_data_count}")
        print(f"   ❌ Errors: {error_count}")
        print(f"   📋 Total processed: {len(items_missing_map)}")
        print(f"{'='*60}")
        
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    asyncio.run(update_missing_map_data())

