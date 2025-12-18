from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# SQLite database URL (you can change this to PostgreSQL or other databases)
SQLALCHEMY_DATABASE_URL = "sqlite:///./app.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

