#!/usr/bin/env python3
"""
Migration script to add the 'completed' column to the items table.
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

print("Adding 'completed' column to items table...")

try:
    with engine.connect() as conn:
        # Check if column exists
        check_query = text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='items' AND column_name='completed'
        """)
        result = conn.execute(check_query)
        exists = result.fetchone()
        
        if exists:
            print("✓ Column 'completed' already exists. No changes needed.")
        else:
            # Add the column with default value False
            alter_query = text("""
                ALTER TABLE items 
                ADD COLUMN completed BOOLEAN NOT NULL DEFAULT FALSE
            """)
            conn.execute(alter_query)
            
            # Create index on completed column for better query performance
            index_query = text("""
                CREATE INDEX IF NOT EXISTS idx_items_completed ON items(completed)
            """)
            conn.execute(index_query)
            
            conn.commit()
            print("✓ Successfully added 'completed' column to items table!")
            print("✓ Created index on 'completed' column for better query performance!")
            
except Exception as e:
    print(f"❌ Error adding column: {e}")
    raise

print("\n✓ Migration complete!")


