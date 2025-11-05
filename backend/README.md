# Arc Raiders Interactive Wiki - Backend

Python FastAPI backend for the Arc Raiders Interactive Wiki.

## Setup

1. **Create a virtual environment:**
   ```bash
   python -m venv venv
   venv\Scripts\activate  # On Windows
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment:**
   ```bash
   copy .env.example .env
   # Edit .env with your database credentials
   ```

4. **Run the development server:**
   ```bash
   python -m app.main
   ```

   Or with uvicorn directly:
   ```bash
   uvicorn app.main:app --reload
   ```

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application entry point
│   ├── database.py          # Database configuration and session
│   ├── schemas.py           # Pydantic schemas for API validation
│   ├── models/              # SQLAlchemy ORM models
│   │   ├── item.py          # Item model (loot, weapons, equipment)
│   │   └── task.py          # Task model (quests, expeditions, workshops)
│   └── routes/              # API endpoint handlers
│       ├── items.py         # Item endpoints
│       ├── tasks.py         # Task endpoints
│       └── search.py        # Search endpoints
├── scraper/
│   ├── __init__.py
│   ├── wiki_scraper.py           # Original index scraper (legacy)
│   ├── precise_index_scraper.py  # Precise column-based index scraper
│   └── detail_page_scraper.py    # Detail page scraper (legacy)
├── scripts/                 # Utility scripts (see scripts/README.md)
│   ├── check_population.py  # Check database status
│   ├── diagnose_data.py     # Data quality analysis
│   ├── lookup.py            # CLI lookup tool
│   ├── fix_misclassified.py # Fix data categorization
│   └── fix_quest_rewards.py # Update quest reward links
├── migrations/              # Alembic database migrations
│   ├── env.py
│   └── versions/
├── scraped_data/            # Output from scrapers (JSON files)
├── populate_database.py     # Main scraper - runs index + detail scrapers
├── requirements.txt         # Python dependencies
├── .env.example            # Environment variables template
├── .env                    # Your local environment config (not in git)
└── alembic.ini             # Alembic configuration
```

## Quick Start

### Running the Application

Use VS Code tasks (recommended):
- Press `Ctrl+Shift+P` → `Tasks: Run Task`
- Choose "Start Backend Server" or "Start Both Servers"

Or manually:
```bash
cd backend
.\venv\Scripts\activate
uvicorn app.main:app --reload
```

### Populating the Database

**Recommended workflow with validation:**
```bash
# 1. Validate extraction logic on sample pages
python scripts/validate_extraction.py
# → Check items and tasks interactively
# → Fix any extraction issues in populate_database.py
# → Re-validate until satisfied

# 2. Reset database to clean state
python scripts/reset_database.py

# 3. Run full scraper and populate
python populate_database.py
```

**Quick options:**

Test mode (5 items + 5 tasks):
```bash
python populate_database.py --test --skip-index
```

Use existing links file:
```bash
python populate_database.py --skip-index --links scraped_data/precise_links_20251104_015130.json
```

### Database Management

**Reset database (clean slate):**
```bash
python scripts/reset_database.py
```
This drops all tables and recreates them from migrations.

**Run migrations:**
```bash
alembic upgrade head
```

**Check database status:**
```bash
python scripts/check_population.py
```

**Lookup specific item/task:**
```bash
python scripts/lookup.py
```

## API Documentation

Once running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Development Workflow

1. Make changes to code
2. Server auto-reloads (if using --reload flag)
3. Test endpoints at http://localhost:8000/docs
4. Run scraper manually when needed: `python -m scraper.wiki_scraper`

## Next Steps

- [ ] Perform initial wiki scrape to analyze data structure
- [ ] Design database schema based on scraped data
- [ ] Create SQLAlchemy models
- [ ] Set up database migrations
- [ ] Implement API endpoints
