# Wiki Scraper

Targeted scraper for analyzing Arc Raiders wiki data structure.

## Quick Start

### 1. Add URLs to scrape

Edit `wiki_scraper.py` and update the `pages_to_scrape` list in the `main()` function:

```python
pages_to_scrape = [
    {"url": "https://arcraiders.wiki/items/your-item", "type": "item"},
    {"url": "https://arcraiders.wiki/quests/your-quest", "type": "quest"},
    {"url": "https://arcraiders.wiki/expeditions/your-expedition", "type": "expedition"},
]
```

### 2. Run the scraper

**Option A: Using VS Code Task**
- Press `Ctrl+Shift+P`
- Select "Tasks: Run Task"
- Choose "Run Wiki Scraper"

**Option B: Using Terminal**
```powershell
cd backend
.\venv\Scripts\Activate.ps1
python -m scraper.wiki_scraper
```

### 3. Review Results

The scraper will create files in `backend/scraped_data/`:
- `scraped_data_TIMESTAMP.json` - Full raw data
- `findings_TIMESTAMP.json` - Organized by page type
- `analysis_report_TIMESTAMP.md` - Human-readable report

## What It Extracts

For each page, the scraper analyzes and extracts:

- **Page metadata** (title, meta tags)
- **Headings** (H1-H6 hierarchy)
- **Tables** (headers and row data)
- **Images** (URLs and alt text)
- **Links** (internal wiki links)
- **Text content** (main content area)
- **HTML structure** (tag hierarchy for analysis)

## Output Structure

### scraped_data_*.json
```json
[
  {
    "url": "https://...",
    "page_type": "item",
    "title": "...",
    "headings": [...],
    "tables": [...],
    "images": [...],
    "links": [...],
    "text_content": "..."
  }
]
```

### findings_*.json
```json
{
  "items": [...],
  "quests": [...],
  "expeditions": [...],
  "other": [...]
}
```

### analysis_report_*.md
Human-readable markdown report with:
- Summary by page type
- Extracted data preview
- Database schema recommendations

## Example Usage

```python
# Scrape a few sample pages
pages_to_scrape = [
    {"url": "https://arcraiders.wiki/items/arc-rifle", "type": "item"},
    {"url": "https://arcraiders.wiki/items/iron-ore", "type": "item"},
    {"url": "https://arcraiders.wiki/quests/tutorial-quest", "type": "quest"},
]
```

Run the scraper, then review the generated files to understand the wiki's data structure.

## Next Steps After Scraping

1. Review the `analysis_report_*.md` file
2. Examine the JSON files for detailed field information
3. Identify common data patterns across pages
4. Design PostgreSQL schema based on findings
5. Update Project Overview with discovered structure
