"""
Precise index page scraper that uses table column headers to correctly categorize links.

This scraper analyzes each index page's specific table structure and uses the column
headers to determine if a link points to an item or a task.

For example:
- Quests page has a "Quest" column -> links are tasks (quests)
- Loot page has an "Item" column -> links are items
- Workshop page has "Upgrade" column -> links are tasks (workshops)
"""

import requests
from bs4 import BeautifulSoup
import json
from typing import Dict, List, Set, Optional, Tuple
from datetime import datetime
from pathlib import Path
import time

class PreciseIndexScraper:
    def __init__(self, output_dir: str = "scraped_data"):
        self.base_url = "https://arcraiders.wiki"
        self.user_agent = "ArcRaidersWikiBot/2.0 (Precise Scraper)"
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": self.user_agent})
        
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Storage for discovered links
        self.item_pages: Set[str] = set()
        self.task_pages: Set[str] = set()
        
        # Track which page each link came from
        self.link_sources: Dict[str, str] = {}
        
        # Delay between requests (be polite!)
        self.delay = 0.5
    
    def fetch_page(self, url: str) -> Optional[BeautifulSoup]:
        """Fetch a page and return BeautifulSoup object"""
        try:
            print(f"  Fetching: {url}")
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            time.sleep(self.delay)
            return BeautifulSoup(response.content, 'lxml')
        except requests.RequestException as e:
            print(f"  ✗ Error: {e}")
            return None
    
    def scrape_loot_page(self) -> None:
        """
        Scrape the Loot page.
        Expected columns: Name | Rarity | Recycles To | Sell Price | Category | Keep for Quests/Workshop
        Links in "Name" column point to item pages.
        """
        print("\n" + "="*70)
        print("SCRAPING: Loot Page")
        print("="*70)
        
        url = f"{self.base_url}/wiki/Loot"
        soup = self.fetch_page(url)
        if not soup:
            return
        
        # Find all tables
        tables = soup.find_all('table')
        print(f"  Found {len(tables)} table(s)")
        
        for table_idx, table in enumerate(tables, 1):
            # Get headers
            headers = [th.get_text(strip=True) for th in table.find_all('th')]
            print(f"  Table {table_idx} headers: {headers}")
            
            # Look for "Name" or "Item" column
            target_col = None
            if "Name" in headers:
                target_col = headers.index("Name")
            elif "Item" in headers:
                target_col = headers.index("Item")
            
            if target_col is not None:
                # Extract links from target column
                for row in table.find_all('tr')[1:]:  # Skip header row
                    cells = row.find_all('td')
                    if len(cells) > target_col:
                        cell = cells[target_col]
                        link = cell.find('a', href=True)
                        if link:
                            href = link['href']
                            full_url = self._make_absolute_url(href)
                            self.item_pages.add(full_url)
                            self.link_sources[full_url] = "Loot Page"
                
                print(f"    → Extracted {len(self.item_pages)} total item links")
    
    def scrape_weapons_page(self) -> None:
        """
        Scrape the Weapons page.
        Expected columns: Name | Type | Damage Type | Fire Rate | ...
        Links in "Name" column point to item pages (weapons are items).
        """
        print("\n" + "="*70)
        print("SCRAPING: Weapons Page")
        print("="*70)
        
        url = f"{self.base_url}/wiki/Weapons"
        soup = self.fetch_page(url)
        if not soup:
            return
        
        initial_count = len(self.item_pages)
        tables = soup.find_all('table')
        print(f"  Found {len(tables)} table(s)")
        
        for table_idx, table in enumerate(tables, 1):
            headers = [th.get_text(strip=True) for th in table.find_all('th')]
            print(f"  Table {table_idx} headers: {headers}")
            
            # Look for "Name" or "Weapon" column
            target_col = None
            if "Name" in headers:
                target_col = headers.index("Name")
            elif "Weapon" in headers:
                target_col = headers.index("Weapon")
            
            if target_col is not None:
                for row in table.find_all('tr')[1:]:
                    cells = row.find_all('td')
                    if len(cells) > target_col:
                        cell = cells[target_col]
                        link = cell.find('a', href=True)
                        if link:
                            href = link['href']
                            full_url = self._make_absolute_url(href)
                            self.item_pages.add(full_url)
                            self.link_sources[full_url] = "Weapons Page"
                
                new_items = len(self.item_pages) - initial_count
                print(f"    → Extracted {new_items} weapon links")
    
    def scrape_equipment_page(self) -> None:
        """
        Scrape the Equipment page.
        Expected columns: Name | Type | Rarity | Description
        Links in "Name" column point to item pages (equipment are items).
        """
        print("\n" + "="*70)
        print("SCRAPING: Equipment Page")
        print("="*70)
        
        url = f"{self.base_url}/wiki/Equipment"
        soup = self.fetch_page(url)
        if not soup:
            return
        
        initial_count = len(self.item_pages)
        tables = soup.find_all('table')
        print(f"  Found {len(tables)} table(s)")
        
        for table_idx, table in enumerate(tables, 1):
            headers = [th.get_text(strip=True) for th in table.find_all('th')]
            print(f"  Table {table_idx} headers: {headers}")
            
            # Look for "Name" or "Equipment" column
            target_col = None
            if "Name" in headers:
                target_col = headers.index("Name")
            elif "Equipment" in headers:
                target_col = headers.index("Equipment")
            
            if target_col is not None:
                for row in table.find_all('tr')[1:]:
                    cells = row.find_all('td')
                    if len(cells) > target_col:
                        cell = cells[target_col]
                        link = cell.find('a', href=True)
                        if link:
                            href = link['href']
                            full_url = self._make_absolute_url(href)
                            self.item_pages.add(full_url)
                            self.link_sources[full_url] = "Equipment Page"
                
                new_items = len(self.item_pages) - initial_count
                print(f"    → Extracted {new_items} equipment links")
    
    def scrape_quests_page(self) -> None:
        """
        Scrape the Quests page.
        Expected columns: Quest | Trader | Location | ...
        Links in "Quest" column point to task pages (quests).
        """
        print("\n" + "="*70)
        print("SCRAPING: Quests Page")
        print("="*70)
        
        url = f"{self.base_url}/wiki/Quests"
        soup = self.fetch_page(url)
        if not soup:
            return
        
        tables = soup.find_all('table')
        print(f"  Found {len(tables)} table(s)")
        
        for table_idx, table in enumerate(tables, 1):
            headers = [th.get_text(strip=True) for th in table.find_all('th')]
            print(f"  Table {table_idx} headers: {headers}")
            
            # Look for "Quest" column
            if "Quest" in headers:
                quest_col_idx = headers.index("Quest")
                
                for row in table.find_all('tr')[1:]:
                    cells = row.find_all('td')
                    if len(cells) > quest_col_idx:
                        quest_cell = cells[quest_col_idx]
                        link = quest_cell.find('a', href=True)
                        if link:
                            href = link['href']
                            full_url = self._make_absolute_url(href)
                            self.task_pages.add(full_url)
                            self.link_sources[full_url] = "Quests Page"
                
                print(f"    → Extracted {len(self.task_pages)} quest links from Quest column")
    
    def scrape_expeditions_page(self) -> None:
        """
        Scrape the Expeditions page.
        Expected columns: Expedition | Type | Difficulty | ...
        Links in "Expedition" column point to task pages.
        """
        print("\n" + "="*70)
        print("SCRAPING: Expeditions Page")
        print("="*70)
        
        url = f"{self.base_url}/wiki/Expedition-1"
        soup = self.fetch_page(url)
        if not soup:
            return
        
        initial_count = len(self.task_pages)
        tables = soup.find_all('table')
        print(f"  Found {len(tables)} table(s)")
        
        for table_idx, table in enumerate(tables, 1):
            headers = [th.get_text(strip=True) for th in table.find_all('th')]
            print(f"  Table {table_idx} headers: {headers}")
            
            # Look for "Expedition" or "Name" column
            target_col = None
            if "Expedition" in headers:
                target_col = headers.index("Expedition")
            elif "Name" in headers:
                target_col = headers.index("Name")
            
            if target_col is not None:
                for row in table.find_all('tr')[1:]:
                    cells = row.find_all('td')
                    if len(cells) > target_col:
                        cell = cells[target_col]
                        link = cell.find('a', href=True)
                        if link:
                            href = link['href']
                            full_url = self._make_absolute_url(href)
                            self.task_pages.add(full_url)
                            self.link_sources[full_url] = "Expeditions Page"
                
                new_tasks = len(self.task_pages) - initial_count
                print(f"    → Extracted {new_tasks} expedition links")
    
    def scrape_workshop_page(self) -> None:
        """
        Scrape the Workshop page.
        Expected columns: Upgrade | Level | Requirements | ...
        Links in "Upgrade" column point to task pages (workshop upgrades).
        """
        print("\n" + "="*70)
        print("SCRAPING: Workshop Page")
        print("="*70)
        
        url = f"{self.base_url}/wiki/Workshop"
        soup = self.fetch_page(url)
        if not soup:
            return
        
        initial_count = len(self.task_pages)
        tables = soup.find_all('table')
        print(f"  Found {len(tables)} table(s)")
        
        for table_idx, table in enumerate(tables, 1):
            headers = [th.get_text(strip=True) for th in table.find_all('th')]
            print(f"  Table {table_idx} headers: {headers}")
            
            # Look for "Upgrade", "Station", or "Name" column
            target_col = None
            if "Upgrade" in headers:
                target_col = headers.index("Upgrade")
            elif "Station" in headers:
                target_col = headers.index("Station")
            elif "Name" in headers:
                target_col = headers.index("Name")
            
            if target_col is not None:
                for row in table.find_all('tr')[1:]:
                    cells = row.find_all('td')
                    if len(cells) > target_col:
                        cell = cells[target_col]
                        link = cell.find('a', href=True)
                        if link:
                            href = link['href']
                            full_url = self._make_absolute_url(href)
                            self.task_pages.add(full_url)
                            self.link_sources[full_url] = "Workshop Page"
                
                new_tasks = len(self.task_pages) - initial_count
                print(f"    → Extracted {new_tasks} workshop links")
    
    def _make_absolute_url(self, href: str) -> str:
        """Convert relative URL to absolute URL"""
        if href.startswith('http'):
            return href
        elif href.startswith('/'):
            return f"{self.base_url}{href}"
        else:
            return f"{self.base_url}/{href}"
    
    def run_all(self) -> Tuple[int, int]:
        """Run all scrapers and return counts"""
        print("\n" + "="*70)
        print("STARTING PRECISE INDEX SCRAPING")
        print("="*70)
        print("Strategy: Use table column headers to correctly categorize links")
        print("="*70)
        
        # Scrape all index pages
        self.scrape_loot_page()
        self.scrape_weapons_page()
        self.scrape_equipment_page()
        self.scrape_quests_page()
        self.scrape_expeditions_page()
        self.scrape_workshop_page()
        
        return len(self.item_pages), len(self.task_pages)
    
    def save_results(self) -> str:
        """Save discovered links to JSON file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        results = {
            "scraped_at": datetime.now().isoformat(),
            "strategy": "precise_column_based",
            "item_pages": sorted(list(self.item_pages)),
            "task_pages": sorted(list(self.task_pages)),
            "link_sources": self.link_sources,
            "counts": {
                "items": len(self.item_pages),
                "tasks": len(self.task_pages),
                "total": len(self.item_pages) + len(self.task_pages)
            }
        }
        
        output_file = self.output_dir / f"precise_links_{timestamp}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print("\n" + "="*70)
        print("RESULTS SAVED")
        print("="*70)
        print(f"File: {output_file}")
        print(f"Items: {len(self.item_pages)}")
        print(f"Tasks: {len(self.task_pages)}")
        print(f"Total: {len(self.item_pages) + len(self.task_pages)}")
        print("="*70)
        
        return str(output_file)
    
    def print_summary(self) -> None:
        """Print categorization summary"""
        print("\n" + "="*70)
        print("CATEGORIZATION SUMMARY")
        print("="*70)
        
        # Group by source
        sources = {}
        for url, source in self.link_sources.items():
            if source not in sources:
                sources[source] = {"items": 0, "tasks": 0}
            
            if url in self.item_pages:
                sources[source]["items"] += 1
            elif url in self.task_pages:
                sources[source]["tasks"] += 1
        
        for source, counts in sorted(sources.items()):
            print(f"\n{source}:")
            print(f"  Items: {counts['items']}")
            print(f"  Tasks: {counts['tasks']}")
        
        print("\n" + "="*70)
        print(f"TOTAL ITEMS: {len(self.item_pages)}")
        print(f"TOTAL TASKS: {len(self.task_pages)}")
        print(f"TOTAL PAGES: {len(self.item_pages) + len(self.task_pages)}")
        print("="*70)


def main():
    """Main entry point"""
    scraper = PreciseIndexScraper()
    
    # Run all scrapers
    item_count, task_count = scraper.run_all()
    
    # Save results
    output_file = scraper.save_results()
    
    # Print summary
    scraper.print_summary()
    
    print("\n" + "="*70)
    print("NEXT STEPS")
    print("="*70)
    print(f"1. Review the output file: {output_file}")
    print("2. Compare with previous discovered_links file to see differences")
    print("3. Use this new file with populate_database.py")
    print("4. Drop and recreate database if needed, then re-populate")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
