# Backend Utility Scripts

This directory contains utility scripts for database management, diagnostics, and maintenance.

## Database Management

### `reset_database.py`
⚠️ **Drop all tables and recreate from migrations.**
```bash
python scripts/reset_database.py
```
Use this when you want to start fresh with a clean database. After running, use `python populate_database.py` to scrape and populate data.

### `check_population.py`
Quick check of database population status.
```bash
python scripts/check_population.py
```
Shows:
- Total items and tasks in database
- Sample records

### `lookup.py`
Lookup specific items or tasks by name or ID.
```bash
python scripts/lookup.py
```
Interactive CLI to search and inspect database records.

## Data Quality

### `validate_extraction.py`
🔍 **Interactive data extraction validator - USE THIS FIRST!**
```bash
python scripts/validate_extraction.py
```
Before populating the database, use this tool to:
- Test extraction logic on sample pages
- See exactly what data is being extracted
- Validate field by field
- Identify issues before bulk scraping

Features:
- Validate individual items or tasks
- Batch validate 10 samples of each type
- See extracted data in readable format
- Get validation warnings for missing fields

### `diagnose_data.py`
Analyze data quality issues in the database (run AFTER population).
```bash
python scripts/diagnose_data.py
```
Reports:
- Missing required fields
- Empty JSONB columns
- Data distribution statistics

## Development & Testing

### `test_db.py`
Test database connection and basic queries.
```bash
python scripts/test_db.py
```

## PowerShell/Batch Scripts

### `restart_postgres.ps1`
Restart PostgreSQL service (Windows).
```powershell
.\scripts\restart_postgres.ps1
```

### `setup_database.bat`
Initial database setup (deprecated - use Alembic migrations).

### `run_scraper.bat`
Legacy scraper runner (deprecated - use VS Code tasks or `python populate_database.py`).

## Notes

- All Python scripts should be run from the `backend/` directory
- They automatically activate the virtual environment when run via VS Code tasks
- Scripts use `.env` for configuration (database connection, etc.)
