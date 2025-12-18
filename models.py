from sqlalchemy import Column, Integer, String, Boolean, Float, Date
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


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
    difficulty = Column(Integer, nullable=True)
    last_attempt_date = Column(String, nullable=True)
    strava_url = Column(String, nullable=True)

