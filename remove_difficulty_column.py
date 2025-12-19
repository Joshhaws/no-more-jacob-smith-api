#!/usr/bin/env python3
"""
Migration script to remove the 'difficulty' column from the items table.
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

print("Removing 'difficulty' column from items table...")

try:
    with engine.connect() as conn:
        # Check if column exists
        check_query = text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='items' AND column_name='difficulty'
        """)
        result = conn.execute(check_query)
        exists = result.fetchone()
        
        if not exists:
            print("✓ Column 'difficulty' does not exist. No changes needed.")
        else:
            # Drop the column
            alter_query = text("""
                ALTER TABLE items 
                DROP COLUMN difficulty
            """)
            conn.execute(alter_query)
            conn.commit()
            print("✓ Successfully removed 'difficulty' column from items table!")
            
except Exception as e:
    print(f"❌ Error removing column: {e}")
    raise

print("\n✓ Migration complete!")


