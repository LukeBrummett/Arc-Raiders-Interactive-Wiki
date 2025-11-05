"""Reset database - drop all tables and recreate from migrations"""

import sys
import subprocess
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import engine, Base
from app.models import Item, Task  # Import models so Base knows about them

print("=" * 70)
print("DATABASE RESET")
print("=" * 70)
print()
print("⚠️  WARNING: This will delete ALL data in the database!")
print()

response = input("Are you sure you want to continue? (yes/no): ")

if response.lower() != 'yes':
    print("Cancelled")
    sys.exit(0)

print("\n🗑️  Dropping all tables...")
Base.metadata.drop_all(bind=engine)
print("✓ All tables dropped")

print("\n📦 Creating tables...")
Base.metadata.create_all(bind=engine)
print("✓ Tables created successfully")

print("\n🔍 Verifying tables exist...")
from sqlalchemy import inspect
inspector = inspect(engine)
tables = inspector.get_table_names()
print(f"Tables in database: {tables}")

if 'items' in tables and 'tasks' in tables:
    print("✓ Verified: items and tasks tables exist")
else:
    print("✗ ERROR: Tables were not created!")
    sys.exit(1)

print("\n✅ Database reset complete!")
print("Next step: Run `python populate_database.py` to scrape and populate data")
