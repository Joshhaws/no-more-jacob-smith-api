#!/usr/bin/env python3
"""
Migration script to add the 'dibs' column to the items table.
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

print("Adding 'dibs' column to items table...")

try:
    with engine.connect() as conn:
        # Check if column already exists
        check_query = text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='items' AND column_name='dibs'
        """)
        result = conn.execute(check_query)
        exists = result.fetchone()
        
        if exists:
            print("✓ Column 'dibs' already exists. No changes needed.")
        else:
            # Add the column
            alter_query = text("""
                ALTER TABLE items 
                ADD COLUMN dibs VARCHAR
            """)
            conn.execute(alter_query)
            conn.commit()
            print("✓ Successfully added 'dibs' column to items table!")
            
except Exception as e:
    print(f"❌ Error adding column: {e}")
    raise

print("\n✓ Migration complete!")

