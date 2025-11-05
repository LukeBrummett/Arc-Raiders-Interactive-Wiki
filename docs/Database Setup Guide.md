# Database Setup Guide

This guide will help you set up PostgreSQL for the Arc Raiders Interactive Wiki project.

## Prerequisites

- PostgreSQL 14 or higher
- Python virtual environment activated (see main README)

## Installation Options

### Option 1: Windows Installer (Recommended for Windows)

1. **Download PostgreSQL**
   - Visit [PostgreSQL Downloads](https://www.postgresql.org/download/windows/)
   - Download the latest version (14+)
   - Run the installer

2. **Installation Settings**
   - Port: `5432` (default)
   - Superuser password: Choose a secure password (remember this!)
   - Locale: Default
   - Components: Install all (PostgreSQL Server, pgAdmin, Command Line Tools)

3. **Add to PATH** (if not done automatically)
   - Add `C:\Program Files\PostgreSQL\{version}\bin` to your system PATH
   - Restart your terminal after this

### Option 2: Docker (Cross-platform)

```bash
# Pull PostgreSQL image
docker pull postgres:15

# Run PostgreSQL container
docker run --name arcraiders-postgres \
  -e POSTGRES_USER=arcraiders \
  -e POSTGRES_PASSWORD=arcraiders \
  -e POSTGRES_DB=arcraiders_wiki \
  -p 5432:5432 \
  -d postgres:15
```

## Database Setup

### Step 1: Create Database

**Using PowerShell (Windows with native install):**

```powershell
# Connect to PostgreSQL
psql -U postgres

# At the psql prompt:
CREATE USER arcraiders WITH PASSWORD 'arcraiders';
CREATE DATABASE arcraiders_wiki OWNER arcraiders;
GRANT ALL PRIVILEGES ON DATABASE arcraiders_wiki TO arcraiders;
\q
```

**Using Docker:**

The Docker command above already creates the database and user.

### Step 2: Configure Environment Variables

Create a `.env` file in the `backend/` directory:

```env
# Database Configuration
DATABASE_URL=postgresql://arcraiders:arcraiders@localhost:5432/arcraiders_wiki

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000

# Frontend URL for CORS
FRONTEND_URL=http://localhost:3000
```

### Step 3: Run Migrations

```powershell
# Make sure you're in the backend directory
cd c:\Arc-Raiders-Interactive-Wiki\backend

# Activate virtual environment (if not already active)
.venv\Scripts\Activate.ps1

# Run the migration
alembic upgrade head
```

You should see output like:
```
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
INFO  [alembic.runtime.migration] Running upgrade  -> 157142d661bd, create_items_and_tasks_tables
```

## Verify Setup

### Check Database Connection

```powershell
# Connect to the database
psql -U arcraiders -d arcraiders_wiki

# List tables
\dt

# You should see:
#          List of relations
#  Schema |   Name    | Type  |   Owner    
# --------+-----------+-------+------------
#  public | items     | table | arcraiders
#  public | tasks     | table | arcraiders
#  public | alembic_version | table | arcraiders

# Check items table structure
\d items

# Exit psql
\q
```

### Test with Python

Create a test script in `backend/`:

```python
# test_db.py
from app.database import engine
from sqlalchemy import text

with engine.connect() as conn:
    result = conn.execute(text("SELECT version();"))
    print("PostgreSQL version:", result.fetchone()[0])
    
    result = conn.execute(text("SELECT COUNT(*) FROM items;"))
    print("Items count:", result.fetchone()[0])
    
    result = conn.execute(text("SELECT COUNT(*) FROM tasks;"))
    print("Tasks count:", result.fetchone()[0])
```

Run it:
```powershell
python test_db.py
```

## Database Schema

### Items Table

Stores all loot, weapons, and equipment with JSONB for flexible data:

- **id**: Primary key
- **name**: Unique item name (indexed)
- **description**: Item description
- **image_url**: URL to item image
- **category**: Item category (indexed)
- **rarity**: Common, Uncommon, Rare, etc.
- **type**: 'loot', 'weapon', 'equipment' (indexed)
- **stats**: JSONB - weight, stack_size, sell_price, etc.
- **sources**: JSONB - where item drops (ARC, enemies)
- **crafting_recipes**: JSONB - how to craft this item
- **recycled_into**: JSONB - recycling outputs
- **salvaged_into**: JSONB - salvage outputs
- **created_at**, **updated_at**: Timestamps

### Tasks Table

Stores quests, expeditions, and workshop stations:

- **id**: Primary key
- **name**: Unique task name (indexed)
- **type**: 'quest', 'expedition', 'workshop_station', 'workshop_scrappy' (indexed)
- **description**: Task description
- **image_url**: Main image URL
- **images**: JSONB - array of additional images
- **trader**: Quest giver (quests only)
- **location**: Quest location
- **dialog**: Quest dialog
- **objectives**: JSONB - array of objectives
- **rewards**: JSONB - array of reward items
- **previous_task_id**: Foreign key to tasks (quest chains)
- **next_tasks**: JSONB - array of follow-up tasks
- **stages**: JSONB - expedition stages with requirements
- **levels**: JSONB - workshop upgrade levels
- **station_type**: 'Workbench', 'Gunsmith', etc. (indexed)
- **max_level**: Maximum upgrade level
- **created_at**, **updated_at**: Timestamps

## Troubleshooting

### Connection Refused

If you get "connection refused" errors:

1. Check PostgreSQL is running:
   ```powershell
   # Windows
   Get-Service postgresql*
   
   # Docker
   docker ps | findstr arcraiders-postgres
   ```

2. Start PostgreSQL:
   ```powershell
   # Windows
   Start-Service postgresql-x64-{version}
   
   # Docker
   docker start arcraiders-postgres
   ```

### Authentication Failed

1. Verify username/password in `.env` match what you created
2. Check `pg_hba.conf` allows password authentication for local connections

### Port Already in Use

If port 5432 is taken:
- Change the port in both PostgreSQL config and `DATABASE_URL`
- Or stop the other service using port 5432

## Next Steps

Once your database is set up and migrations are run:

1. **Run the scraper** to populate data:
   ```powershell
   python -m scraper.detail_page_scraper
   ```

2. **Start the API server**:
   ```powershell
   uvicorn app.main:app --reload
   ```

3. **Test API endpoints**:
   - http://localhost:8000/docs (Swagger UI)
   - http://localhost:8000/api/items
   - http://localhost:8000/api/tasks

## Maintenance

### Backup Database

```powershell
pg_dump -U arcraiders arcraiders_wiki > backup_$(Get-Date -Format "yyyyMMdd_HHmmss").sql
```

### Restore Database

```powershell
psql -U arcraiders arcraiders_wiki < backup_20241104_123456.sql
```

### Reset Database

```powershell
# Drop and recreate
psql -U postgres
DROP DATABASE arcraiders_wiki;
CREATE DATABASE arcraiders_wiki OWNER arcraiders;
\q

# Run migrations again
alembic upgrade head
```
