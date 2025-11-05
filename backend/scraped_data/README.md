# Scraped Data Directory

This directory stores temporary output files from the wiki scraper:

- `precise_links_*.json` - Index scraper output with categorized URLs
- `scraped_data_*.json` - Full scraped data before database insertion
- `analysis_report_*.md` - Analysis reports from data quality checks
- `findings_*.json` - Detailed findings from scraping runs

## Note

These files are automatically generated and excluded from version control (see `.gitignore`).
They are useful for debugging and manual inspection but should not be committed.
