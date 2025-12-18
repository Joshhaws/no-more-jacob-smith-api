from pydantic import BaseModel, ConfigDict
from typing import Optional


class ItemBase(BaseModel):
    segment_name: str
    distance: Optional[float] = None  # in miles
    elevation_gain: Optional[float] = None  # in feet
    elevation_loss: Optional[float] = None  # in feet
    crown_holder: Optional[str] = None
    crown_date: Optional[str] = None
    crown_time: Optional[str] = None  # format: MM:SS
    crown_pace: Optional[str] = None  # format: MM:SS per mile
    personal_best_time: Optional[str] = None  # format: MM:SS:00
    personal_best_pace: Optional[str] = None  # format: MM:SS per mile
    personal_attempts: int = 0
    overall_attempts: int = 0
    difficulty: Optional[int] = None
    last_attempt_date: Optional[str] = None
    strava_url: Optional[str] = None
    strava_segment_id: Optional[int] = None
    dibs: Optional[str] = None


class ItemCreate(ItemBase):
    pass


class ItemUpdate(BaseModel):
    segment_name: Optional[str] = None
    distance: Optional[float] = None
    elevation_gain: Optional[float] = None
    elevation_loss: Optional[float] = None
    crown_holder: Optional[str] = None
    crown_date: Optional[str] = None
    crown_time: Optional[str] = None
    crown_pace: Optional[str] = None
    personal_best_time: Optional[str] = None
    personal_best_pace: Optional[str] = None
    personal_attempts: Optional[int] = None
    overall_attempts: Optional[int] = None
    difficulty: Optional[int] = None
    last_attempt_date: Optional[str] = None
    strava_url: Optional[str] = None
    strava_segment_id: Optional[int] = None
    dibs: Optional[str] = None


class Item(ItemBase):
    id: int
    
    model_config = ConfigDict(from_attributes=True)


class StravaAuthStatus(BaseModel):
    connected: bool
    athlete_name: Optional[str] = None


class StravaSegmentTime(BaseModel):
    segment_id: int
    segment_name: str
    personal_best_time: Optional[str] = None
    personal_best_pace: Optional[str] = None
    personal_best_grade_adjusted_pace: Optional[str] = None  # Grade Adjusted Pace (GAP)
    personal_attempts: Optional[int] = None
    last_attempt_date: Optional[str] = None
    personal_best_activity_id: Optional[int] = None  # Activity ID for the personal best effort
    crown_holder: Optional[str] = None  # KOM/QOM holder name
    crown_time: Optional[str] = None  # KOM/QOM time
    crown_date: Optional[str] = None  # KOM/QOM date
    crown_pace: Optional[str] = None  # KOM/QOM pace


class StravaSegmentMetadata(BaseModel):
    segment_id: int
    segment_name: str
    distance: Optional[float] = None  # in miles
    elevation_gain: Optional[float] = None  # in feet
    strava_url: str
    crown_holder: Optional[str] = None  # KOM/QOM holder name
    crown_time: Optional[str] = None  # KOM/QOM time
    crown_date: Optional[str] = None  # KOM/QOM date
    crown_pace: Optional[str] = None  # KOM/QOM pace

