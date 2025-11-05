# Arc Raiders Interactive Wiki - Progress & Next Steps

## Current Status (as of Nov 4, 2025 - 3 AM)

### ✅ Completed
- **Project structure** - Backend (FastAPI + PostgreSQL), Frontend (React + Vite)
- **PostgreSQL database** - Installed, configured, running locally
- **Database schema** - 2 tables (items, tasks) with JSONB fields
- **Precise index scraper** - Column-based categorization (215 items, 26 tasks)
- **Detail page scraper** - Extracts stats, sources, crafting recipes
- **Crafting parser** - Regex-based parser for "2x Item + 3x Item" format
- **Full database population** - 215 items + 26 tasks, 0 errors
- **Validation tools** - Interactive validation, diagnostic sampling, database reset
- **VS Code tasks** - Automated workflows for scraping, testing, diagnostics

### 📊 Data Quality Results

**Items (215 total):**
- ✅ Stats extracting correctly (weight, sell_price, stack_size, etc.)
- ✅ Sources extracting correctly
- ✅ Crafting recipes mostly working (e.g., "3 inputs → Bettina I")
- ✅ Categories accurate (Recyclable, Trinket, Topside Material, etc.)
- ❌ All missing description & rarity (might not exist on wiki)
- ❌ Some crafting recipes have 0 inputs (malformed tables on wiki)

**Tasks (26 total):**
- ✅ Correctly categorized as quests (no more items misclassified)
- ✅ Objectives extracting for some quests
- ✅ Rewards extracting
- ❌ Missing trader, location, description
- ❌ Rewards using item names instead of IDs

## Known Issues

1. **Missing description/rarity** - Need to check if these fields exist on wiki pages
2. **Crafting recipes with no inputs** - Some wiki tables might be malformed
3. **Task fields incomplete** - Trader, location, description not extracting
4. **Reward item references** - Using names instead of IDs (need lookup logic)

## Next Steps (Pick One or More)

### Option 1: Verify Description/Rarity Exist
- Manually check a few item pages on the wiki
- If they don't exist, remove from model or mark as optional
- If they do exist, fix extraction logic

### Option 2: Fix Crafting Recipe Edge Cases
- Inspect "Mod Components" page (has 0 inputs issue)
- Update parser to handle malformed tables
- Re-scrape affected items

### Option 3: Improve Task Extraction
- Add trader extraction (look for trader name on page)
- Add location extraction
- Add description extraction
- Implement reward item ID lookup (find item by name, store ID)

### Option 4: Build Frontend
- Start with item list view
- Add item detail view
- Add search/filter functionality
- Skip fixing extraction issues for now

### Option 5: Accept Current Quality
- Description/rarity might just not be on wiki
- Crafting data is 90% working
- Focus on building the frontend with what we have

## Quick Commands

**Reset database:**
```powershell
# Run VS Code task: "Reset Database (Clean Slate)"
# OR
cd backend
python scripts/reset_database.py
```

**Re-populate database:**
```powershell
# Run VS Code task: "Populate Database (Full - Runs Index Scraper First)"
# OR
cd backend
python populate_database.py
```

**Check data quality:**
```powershell
# Run VS Code task: "Diagnose Data Quality Issues"
# OR
cd backend
python scripts/diagnose_data.py
```

**Validate extraction:**
```powershell
# Run VS Code task: "Validate Data Extraction (Interactive)"
# OR
cd backend
python scripts/validate_extraction.py
```

## Important Files

- `backend/populate_database.py` - Main scraper with extraction logic
- `backend/scraper/precise_index_scraper.py` - Index scraper (finds all URLs)
- `backend/scripts/diagnose_data.py` - 10% random sampling diagnostic
- `backend/scripts/validate_extraction.py` - Interactive validation tool
- `backend/scripts/reset_database.py` - Drop/recreate database tables
- `backend/app/models/item.py` - Item model (JSONB fields)
- `backend/app/models/task.py` - Task model (quest/workshop/expedition)

## Technical Notes

- **Scraping delay:** 0.5s between requests (respectful)
- **Database approach:** Denormalized JSONB (optimized for reads)
- **Migrations:** Single Alembic migration creates initial schema
- **Reset script:** Uses `Base.metadata.create_all()` (simpler than Alembic)
- **Crafting parser:** Lines 290-395 in `populate_database.py`

## When You Come Back

1. Pick a next step from the list above
2. Run diagnostic script to see current data quality
3. If fixing extraction: Update `populate_database.py`, reset DB, re-scrape
4. If building frontend: Start in `frontend/src/` with item list component

---

**Last updated:** Nov 4, 2025, 3 AM  
**Database:** 215 items, 26 tasks, 0 errors
