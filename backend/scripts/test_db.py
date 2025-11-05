"""Test database connection and schema"""

import os
import sys
from sqlalchemy import text, inspect

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.database import engine


def test_connection():
    """Test basic database connection"""
    print("Testing database connection...")
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version();"))
            version = result.fetchone()[0]
            print(f"✅ Connected to PostgreSQL")
            print(f"   Version: {version.split(',')[0]}")
            return True
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False


def test_tables():
    """Test that tables exist"""
    print("\nChecking database tables...")
    try:
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        expected_tables = ['items', 'tasks', 'alembic_version']
        
        for table in expected_tables:
            if table in tables:
                print(f"✅ Table '{table}' exists")
            else:
                print(f"❌ Table '{table}' NOT found")
        
        return all(table in tables for table in expected_tables)
    except Exception as e:
        print(f"❌ Error checking tables: {e}")
        return False


def test_table_structure():
    """Test table structure"""
    print("\nChecking table structure...")
    try:
        inspector = inspect(engine)
        
        # Check items table
        items_columns = [col['name'] for col in inspector.get_columns('items')]
        expected_items_cols = ['id', 'name', 'description', 'image_url', 'category', 
                              'rarity', 'type', 'stats', 'sources', 'crafting_recipes',
                              'recycled_into', 'salvaged_into', 'created_at', 'updated_at']
        
        print("\nItems table columns:")
        for col in expected_items_cols:
            if col in items_columns:
                print(f"  ✅ {col}")
            else:
                print(f"  ❌ {col} (missing)")
        
        # Check tasks table
        tasks_columns = [col['name'] for col in inspector.get_columns('tasks')]
        expected_tasks_cols = ['id', 'name', 'type', 'description', 'image_url', 
                              'images', 'trader', 'location', 'dialog', 'objectives',
                              'rewards', 'previous_task_id', 'next_tasks', 'stages',
                              'levels', 'station_type', 'max_level', 'created_at', 'updated_at']
        
        print("\nTasks table columns:")
        for col in expected_tasks_cols:
            if col in tasks_columns:
                print(f"  ✅ {col}")
            else:
                print(f"  ❌ {col} (missing)")
        
        return True
    except Exception as e:
        print(f"❌ Error checking structure: {e}")
        return False


def test_counts():
    """Test record counts"""
    print("\nChecking record counts...")
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT COUNT(*) FROM items;"))
            items_count = result.fetchone()[0]
            print(f"Items: {items_count}")
            
            result = conn.execute(text("SELECT COUNT(*) FROM tasks;"))
            tasks_count = result.fetchone()[0]
            print(f"Tasks: {tasks_count}")
            
        return True
    except Exception as e:
        print(f"❌ Error checking counts: {e}")
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("Arc Raiders Wiki - Database Test")
    print("=" * 60)
    
    # Run tests
    conn_ok = test_connection()
    
    if conn_ok:
        test_tables()
        test_table_structure()
        test_counts()
        
        print("\n" + "=" * 60)
        print("✅ Database setup looks good!")
        print("=" * 60)
        print("\nNext steps:")
        print("1. Run the scraper to populate data:")
        print("   python -m scraper.detail_page_scraper")
        print("\n2. Start the API server:")
        print("   uvicorn app.main:app --reload")
    else:
        print("\n" + "=" * 60)
        print("❌ Database connection failed")
        print("=" * 60)
        print("\nTroubleshooting:")
        print("1. Make sure PostgreSQL is running")
        print("2. Check your DATABASE_URL in .env")
        print("3. Run migrations: alembic upgrade head")
        print("\nSee docs/Database Setup Guide.md for help")
