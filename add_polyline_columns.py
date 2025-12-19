#!/usr/bin/env python3
"""
Migration script to add polyline and coordinate columns to the items table.
Run this once to update your existing database schema.
"""

import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

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

# Create engine
engine = create_engine(DATABASE_URL)

print("Adding polyline and coordinate columns to items table...")

try:
    with engine.connect() as conn:
        # Check if columns exist
        check_query = text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='items' AND column_name IN ('polyline', 'start_latitude', 'start_longitude')
        """)
        result = conn.execute(check_query)
        existing_columns = {row[0] for row in result}
        
        if 'polyline' not in existing_columns:
            alter_query = text("""
                ALTER TABLE items 
                ADD COLUMN polyline TEXT
            """)
            conn.execute(alter_query)
            print("✓ Added 'polyline' column")
        else:
            print("✓ Column 'polyline' already exists")
        
        if 'start_latitude' not in existing_columns:
            alter_query = text("""
                ALTER TABLE items 
                ADD COLUMN start_latitude DOUBLE PRECISION
            """)
            conn.execute(alter_query)
            print("✓ Added 'start_latitude' column")
        else:
            print("✓ Column 'start_latitude' already exists")
        
        if 'start_longitude' not in existing_columns:
            alter_query = text("""
                ALTER TABLE items 
                ADD COLUMN start_longitude DOUBLE PRECISION
            """)
            conn.execute(alter_query)
            print("✓ Added 'start_longitude' column")
        else:
            print("✓ Column 'start_longitude' already exists")
        
        conn.commit()
        print("\n✓ Migration complete!")
            
except Exception as e:
    print(f"❌ Error adding columns: {e}")
    raise


