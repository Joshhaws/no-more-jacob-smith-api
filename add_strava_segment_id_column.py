#!/usr/bin/env python3
"""
Migration script to add the 'strava_segment_id' column to the items table.
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

print("Adding 'strava_segment_id' column to items table...")

try:
    with engine.connect() as conn:
        # Check if column already exists
        check_query = text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='items' AND column_name='strava_segment_id'
        """)
        result = conn.execute(check_query)
        exists = result.fetchone()
        
        if exists:
            print("✓ Column 'strava_segment_id' already exists. No changes needed.")
        else:
            # Add the column
            alter_query = text("""
                ALTER TABLE items 
                ADD COLUMN strava_segment_id INTEGER
            """)
            conn.execute(alter_query)
            
            # Create index on the column for better query performance
            index_query = text("""
                CREATE INDEX IF NOT EXISTS ix_items_strava_segment_id 
                ON items(strava_segment_id)
            """)
            conn.execute(index_query)
            
            conn.commit()
            print("✓ Successfully added 'strava_segment_id' column to items table!")
            print("✓ Created index on 'strava_segment_id' column")
            
except Exception as e:
    print(f"❌ Error adding column: {e}")
    raise

print("\n✓ Migration complete!")

