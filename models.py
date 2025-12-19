from sqlalchemy import Column, Integer, String, Boolean, Float, Date, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    strava_id = Column(Integer, unique=True, nullable=True, index=True)  # Strava athlete ID
    strava_access_token = Column(String, nullable=True)
    strava_refresh_token = Column(String, nullable=True)
    token_expires_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    segment_name = Column(String, index=True)
    distance = Column(Float, nullable=True)  # in miles
    elevation_gain = Column(Float, nullable=True)  # in feet
    elevation_loss = Column(Float, nullable=True)  # in feet
    crown_holder = Column(String, nullable=True)
    crown_date = Column(String, nullable=True)
    crown_time = Column(String, nullable=True)  # format: MM:SS
    crown_pace = Column(String, nullable=True)  # format: MM:SS per mile
    personal_best_time = Column(String, nullable=True)  # format: MM:SS:00
    personal_best_pace = Column(String, nullable=True)  # format: MM:SS per mile
    personal_attempts = Column(Integer, default=0)
    overall_attempts = Column(Integer, default=0)
    last_attempt_date = Column(String, nullable=True)
    strava_url = Column(String, nullable=True)
    strava_segment_id = Column(Integer, nullable=True, index=True)  # Extract from URL for API calls
    dibs = Column(String, nullable=True)  # Person who claimed this segment
    completed = Column(Boolean, default=False, nullable=False, index=True)  # Whether segment is completed
    polyline = Column(String, nullable=True)  # Encoded polyline for map display
    start_latitude = Column(Float, nullable=True)  # Start point latitude
    start_longitude = Column(Float, nullable=True)  # Start point longitude

