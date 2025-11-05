"""
Complete scraper to populate Arc Raiders Wiki database

This scraper:
1. Loads discovered URLs from JSON
2. Scrapes each detail page
3. Transforms HTML to database model format
4. Inserts into PostgreSQL database
"""

import requests
from bs4 import BeautifulSoup
import json
import re
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv
import os
import sys
from pathlib import Path
from datetime import datetime
import time

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.models import Item, Task
from app.database import SessionLocal

load_dotenv()


class WikiDatabasePopulator:
    def __init__(self):
        self.base_url = os.getenv("WIKI_BASE_URL", "https://arcraiders.wiki")
        self.user_agent = os.getenv("SCRAPER_USER_AGENT", "ArcRaidersWikiBot/1.0")
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": self.user_agent})
        
        # Database session
        self.db = SessionLocal()
        
        # Verify tables exist
        from sqlalchemy import inspect
        from app.database import engine
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        if 'items' not in tables or 'tasks' not in tables:
            print(f"❌ ERROR: Required tables not found in database!")
            print(f"   Found tables: {tables}")
            print(f"   Please run: python scripts/reset_database.py")
            sys.exit(1)
        
        # Stats
        self.stats = {
            "items_scraped": 0,
            "items_created": 0,
            "items_updated": 0,
            "tasks_scraped": 0,
            "tasks_created": 0,
            "tasks_updated": 0,
            "errors": []
        }
    
    def fetch_page(self, url: str) -> Optional[BeautifulSoup]:
        """Fetch a page and return BeautifulSoup object"""
        try:
            print(f"  Fetching: {url}")
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            return BeautifulSoup(response.content, 'lxml')
        except requests.RequestException as e:
            print(f"  ✗ Error fetching {url}: {e}")
            self.stats["errors"].append({"url": url, "error": str(e)})
            return None
    
    def extract_item_data(self, soup: BeautifulSoup, url: str) -> Dict[str, Any]:
        """Extract item data from detail page"""
        data = {
            "name": None,
            "description": None,
            "image_url": None,
            "wiki_url": url,
            "category": None,
            "rarity": None,
            "type": "loot",  # Default type
            "stats": {},
            "sources": [],
            "crafting_recipes": [],
            "recycled_into": [],
            "salvaged_into": []
        }
        
        # Extract name from title
        h1 = soup.find('h1', class_='firstHeading') or soup.find('h1')
        if h1:
            data["name"] = h1.get_text(strip=True)
        
        # Extract image
        infobox = soup.find('table', class_=['infobox', 'wikitable'])
        if infobox:
            img = infobox.find('img')
            if img and img.get('src'):
                data["image_url"] = self.base_url + img['src'] if img['src'].startswith('/') else img['src']
            
            # Extract description from infobox-quote (the in-game description)
            quote_row = infobox.find('tr', class_='infobox-quote')
            if quote_row:
                quote_td = quote_row.find('td')
                if quote_td:
                    data["description"] = quote_td.get_text(separator=' ', strip=True)
            
            # Extract rarity from infobox (look for data-tag or td with rarity text)
            rarity_elem = infobox.find('span', class_=lambda x: x and 'data-tag' in x) or infobox.find('td', string=lambda x: x and x.strip().lower() in ['common', 'uncommon', 'rare', 'epic', 'legendary'])
            if rarity_elem:
                data["rarity"] = rarity_elem.get_text(strip=True).title()
            
            # Extract category from infobox (look for data-tag elements)
            category_elem = infobox.find('span', class_='data-tag')
            if category_elem and not data["category"]:
                cat_text = category_elem.get_text(strip=True)
                # Only use if it's not the rarity
                if cat_text.lower() not in ['common', 'uncommon', 'rare', 'epic', 'legendary']:
                    data["category"] = cat_text
        
        
        # Extract stats from tables
        for table in soup.find_all('table'):
            for row in table.find_all('tr'):
                cells = row.find_all(['th', 'td'])
                if len(cells) >= 2:
                    key = cells[0].get_text(separator=' ', strip=True).lower()
                    value = cells[1].get_text(separator=' ', strip=True)
                    
                    # Map table rows to stats
                    if 'weight' in key:
                        data["stats"]["weight"] = value
                    elif 'stack size' in key or 'stack' in key:
                        data["stats"]["stack_size"] = self._parse_int(value)
                    elif 'sell price' in key or 'sell' in key:
                        data["stats"]["sell_price"] = self._parse_int(value)
                    elif 'can be found' in key or 'found in' in key:
                        data["stats"]["can_be_found_in"] = value
                    elif 'rarity' in key:
                        data["rarity"] = value
                    elif 'category' in key:
                        data["category"] = value
                    elif 'type' in key:
                        data["type"] = value.lower()
                    elif 'ammo type' in key:
                        data["stats"]["ammo_type"] = value
                    elif 'damage' in key:
                        data["stats"]["damage"] = value
                    elif 'firing mode' in key:
                        data["stats"]["firing_mode"] = value
                    elif 'range' in key:
                        data["stats"]["range"] = value
        
        # Extract category from page categories
        if not data["category"]:
            cat_div = soup.find('div', id='mw-normal-catlinks')
            if cat_div:
                cats = cat_div.find_all('a')
                if cats:
                    # Skip "Categories:" link, get the actual categories
                    categories = [c.get_text(strip=True) for c in cats if '/wiki/Category:' in c.get('href', '')]
                    if categories:
                        data["category"] = categories[0]  # Use first category
        
        # Extract sources
        sources_heading = self._find_heading(soup, ['source', 'obtained from', 'where to find'])
        if sources_heading:
            data["sources"] = self._extract_list_items(sources_heading)
        
        # Extract crafting recipes
        crafting_heading = self._find_heading(soup, ['crafting', 'recipes', 'used in'])
        if crafting_heading:
            data["crafting_recipes"] = self._extract_crafting_table(crafting_heading)
        
        # Extract recycling output
        recycled_heading = self._find_heading(soup, ['recycled', 'recycling'])
        if recycled_heading:
            data["recycled_into"] = self._extract_material_list(recycled_heading)
        
        # Extract salvage output
        salvaged_heading = self._find_heading(soup, ['salvaged', 'salvage'])
        if salvaged_heading:
            data["salvaged_into"] = self._extract_material_list(salvaged_heading)
        
        return data
    
    def extract_task_data(self, soup: BeautifulSoup, url: str) -> Dict[str, Any]:
        """Extract quest/expedition/workshop data"""
        data = {
            "name": None,
            "type": None,
            "description": None,
            "image_url": None,
            "wiki_url": url,
            "images": [],
            "trader": None,
            "location": None,
            "dialog": None,
            "objectives": [],
            "rewards": [],
            "previous_task_id": None,
            "next_tasks": [],
            "stages": [],
            "levels": [],
            "station_type": None,
            "max_level": None
        }
        
        # Extract name
        h1 = soup.find('h1', class_='firstHeading') or soup.find('h1')
        if h1:
            name = h1.get_text(strip=True)
            data["name"] = name
            
            # Determine type from name
            if 'expedition' in name.lower():
                data["type"] = "expedition"
            elif 'workbench' in name.lower() or 'gunsmith' in name.lower() or 'scrappy' in name.lower():
                data["type"] = "workshop_station"
                data["station_type"] = name
            else:
                data["type"] = "quest"
        
        # Extract description from first paragraph
        content = soup.find('div', class_='mw-parser-output')
        if content:
            # Try to find the first paragraph - it might be in the first section
            first_section = content.find('section', class_='citizen-section')
            search_area = first_section if first_section else content
            
            # Find first paragraph that's not inside an infobox
            for p in search_area.find_all('p'):
                # Skip if paragraph is inside infobox
                if p.find_parent('table', class_='infobox'):
                    continue
                # Use separator=' ' to preserve spacing between linked text
                text = p.get_text(separator=' ', strip=True)
                if text and len(text) > 20:
                    data["description"] = text
                    break
        
        # Extract trader and location from infobox table
        infobox = soup.find('table', class_='infobox')
        if infobox:
            # Look for trader row
            trader_row = infobox.find('tr', class_='data-trader')
            if trader_row:
                trader_td = trader_row.find('td')
                if trader_td:
                    trader_link = trader_td.find('a')
                    if trader_link:
                        data["trader"] = trader_link.get_text(strip=True)
                    else:
                        data["trader"] = trader_td.get_text(strip=True)
            
            # Look for location row
            location_row = infobox.find('tr', class_='data-location')
            if location_row:
                location_td = location_row.find('td')
                if location_td:
                    # Extract all location links
                    location_links = location_td.find_all('a')
                    if location_links:
                        data["location"] = ', '.join([link.get_text(strip=True) for link in location_links])
                    else:
                        data["location"] = location_td.get_text(strip=True)
        
        # Extract dialog
        dialog_heading = self._find_heading(soup, ['dialog', 'dialogue'])
        if dialog_heading:
            # Look for italic/em text after the heading
            next_elem = dialog_heading.find_next(['p', 'div', 'blockquote'])
            if next_elem:
                # Try to find italic text (dialog is usually in italics)
                dialog_text = None
                em_tag = next_elem.find(['em', 'i'])
                if em_tag:
                    dialog_text = em_tag.get_text(separator=' ', strip=True)
                else:
                    dialog_text = next_elem.get_text(separator=' ', strip=True)
                
                if dialog_text and len(dialog_text) > 10:
                    data["dialog"] = dialog_text
        
        # Extract objectives
        objectives_heading = self._find_heading(soup, ['objective', 'goal', 'task'])
        if objectives_heading:
            obj_list = self._extract_simple_list(objectives_heading)
            data["objectives"] = obj_list
        
        # Extract rewards
        rewards_heading = self._find_heading(soup, ['reward', 'prize'])
        if rewards_heading:
            data["rewards"] = self._extract_material_list(rewards_heading)
        
        # Extract stages (for expeditions)
        stages_heading = self._find_heading(soup, ['stage', 'phase', 'level'])
        if stages_heading and data["type"] == "expedition":
            data["stages"] = self._extract_stages(stages_heading)
        
        # Extract levels (for workshops)
        if data["type"] == "workshop_station":
            data["levels"] = self._extract_workshop_levels(soup)
            if data["levels"]:
                data["max_level"] = len(data["levels"])
        
        return data
    
    def _find_heading(self, soup: BeautifulSoup, keywords: List[str]) -> Optional:
        """Find a heading containing any of the keywords"""
        for heading in soup.find_all(['h2', 'h3', 'h4']):
            text = heading.get_text(strip=True).lower()
            if any(kw in text for kw in keywords):
                return heading
        return None
    
    def _extract_list_items(self, heading) -> List[Dict[str, str]]:
        """Extract items from a list after a heading, with links"""
        items = []
        next_elem = heading.find_next(['ul', 'ol'])
        if next_elem:
            for li in next_elem.find_all('li', recursive=False):
                text = li.get_text(separator=' ', strip=True)
                link = li.find('a')
                items.append({
                    "name": text,
                    "url": link.get('href', '') if link else None
                })
        return items
    
    def _extract_simple_list(self, heading) -> List[str]:
        """Extract simple text list after a heading"""
        items = []
        next_elem = heading.find_next(['ul', 'ol'])
        if next_elem:
            for li in next_elem.find_all('li', recursive=False):
                items.append(li.get_text(separator=' ', strip=True))
        return items
    
    def _extract_material_list(self, heading) -> List[Dict[str, Any]]:
        """Extract material list with quantities (e.g., '5x Metal Parts', 'x33,000 XP')"""
        materials = []
        next_elem = heading.find_next(['ul', 'ol', 'table'])
        
        if next_elem and next_elem.name in ['ul', 'ol']:
            for li in next_elem.find_all('li', recursive=False):
                text = li.get_text(separator=' ', strip=True)
                # Parse different formats:
                # "5x Metal Parts" - quantity before 'x'
                # "x33,000 XP" - quantity after 'x' with commas
                # "Metal Parts x5" - quantity after item
                
                # Try "x33,000 XP" format first (x followed by number with possible commas)
                match = re.match(r'x\s*([\d,]+)\s+(.+)', text, re.IGNORECASE)
                if match:
                    quantity_str = match.group(1).replace(',', '')
                    materials.append({
                        "item": match.group(2).strip(),
                        "quantity": int(quantity_str)
                    })
                else:
                    # Try "5x Metal Parts" format (number followed by x)
                    match = re.search(r'([\d,]+)\s*x\s*(.+)', text, re.IGNORECASE)
                    if match:
                        quantity_str = match.group(1).replace(',', '')
                        materials.append({
                            "item": match.group(2).strip(),
                            "quantity": int(quantity_str)
                        })
                    else:
                        # No quantity found, assume 1
                        materials.append({
                            "item": text,
                            "quantity": 1
                        })
        
        return materials
    
    def _extract_crafting_table(self, heading) -> List[Dict[str, Any]]:
        """Extract crafting recipes from table"""
        recipes = []
        next_elem = heading.find_next('table')
        
        if next_elem:
            rows = next_elem.find_all('tr')
            
            # Find header row to identify columns
            headers = []
            header_row = None
            for row in rows:
                ths = row.find_all('th')
                if ths:
                    headers = [th.get_text(strip=True).lower() for th in ths]
                    header_row = row
                    break
            
            # If no header row, try first row with td
            if not headers:
                first_row = rows[0] if rows else None
                if first_row:
                    headers = [td.get_text(strip=True).lower() for td in first_row.find_all('td')]
            
            # Find column indices
            recipe_col = None
            workshop_col = None
            output_col = None
            
            for i, h in enumerate(headers):
                if 'recipe' in h or 'input' in h or 'material' in h or 'ingredient' in h or 'blueprint' in h:
                    recipe_col = i
                elif 'workshop' in h or 'station' in h or 'bench' in h:
                    workshop_col = i
                elif 'craft' in h or 'output' in h or 'result' in h or 'product' in h:
                    output_col = i
            
            # Parse data rows
            start_idx = rows.index(header_row) + 1 if header_row else 1
            for row in rows[start_idx:]:
                cells = row.find_all(['td', 'th'])
                if len(cells) < 2:
                    continue
                
                # Skip rows with just "?"
                cell_texts = [c.get_text(separator=' ', strip=True) for c in cells]
                if all(text == '?' for text in cell_texts):
                    continue
                
                recipe = {
                    "inputs": [],
                    "workshop": None,
                    "output": None
                }
                
                # Extract inputs (recipe column)
                if recipe_col is not None and len(cells) > recipe_col:
                    recipe_text = cells[recipe_col].get_text(separator=' ', strip=True)
                    recipe["inputs"] = self._parse_crafting_materials(recipe_text)
                    
                    # Also try to get item names from links
                    links = cells[recipe_col].find_all('a', href=True)
                    if links and not recipe["inputs"]:
                        # If text parsing failed, try extracting from links
                        for link in links:
                            item_name = link.get_text(separator=' ', strip=True)
                            # Try to extract quantity from surrounding text
                            recipe["inputs"].append({
                                "item": item_name,
                                "quantity": 1  # Default
                            })
                
                # Extract workshop
                if workshop_col is not None and len(cells) > workshop_col:
                    workshop_text = cells[workshop_col].get_text(separator=' ', strip=True)
                    if workshop_text and workshop_text != '?':
                        recipe["workshop"] = workshop_text
                
                # Extract output
                if output_col is not None and len(cells) > output_col:
                    output_text = cells[output_col].get_text(separator=' ', strip=True)
                    parsed_output = self._parse_crafting_materials(output_text)
                    if parsed_output and len(parsed_output) > 0:
                        recipe["output"] = parsed_output[0]  # Single output
                
                # Only add if we got useful data
                if recipe["inputs"] or recipe["output"]:
                    recipes.append(recipe)
        
        return recipes
    
    def _parse_crafting_materials(self, text: str) -> List[Dict[str, Any]]:
        """
        Parse crafting material string like:
        - "2x ARC Motion Core+2xAdvanced Mechanical Components"
        - "5x Metal Parts"
        - "ARC Alloy + 3x Steel"
        - "33,000 XP" (numbers with commas)
        
        Returns list of {item: str, quantity: int}
        """
        if not text or text == '?':
            return []
        
        materials = []
        
        # Split by + or & (but NOT comma, as it might be in numbers like "33,000")
        parts = re.split(r'[+&]', text)
        
        for part in parts:
            part = part.strip()
            if not part or part == '?':
                continue
            
            # Try to match "5x Item Name" or "5 Item Name" or "33,000 XP"
            # This regex handles numbers with commas
            match = re.match(r'([\d,]+)\s*[x×]?\s*(.+)', part, re.IGNORECASE)
            if match:
                # Remove commas from quantity string and convert to int
                quantity_str = match.group(1).replace(',', '')
                quantity = int(quantity_str)
                item_name = match.group(2).strip()
            else:
                # No quantity found, assume 1
                quantity = 1
                item_name = part.strip()
            
            if item_name:
                materials.append({
                    "item": item_name,
                    "quantity": quantity
                })
        
        return materials
    
    def _extract_stages(self, heading) -> List[Dict[str, Any]]:
        """Extract expedition stages"""
        stages = []
        # Look for table or structured list
        next_elem = heading.find_next(['table', 'div'])
        if next_elem and next_elem.name == 'table':
            rows = next_elem.find_all('tr')[1:]  # Skip header
            for row in rows:
                cells = row.find_all(['td', 'th'])
                if cells:
                    stage = {
                        "stage": cells[0].get_text(strip=True) if len(cells) > 0 else None,
                        "description": cells[1].get_text(strip=True) if len(cells) > 1 else None,
                        "requirements": []
                    }
                    stages.append(stage)
        return stages
    
    def _extract_workshop_levels(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Extract workshop upgrade levels and requirements"""
        levels = []
        # Look for level headings or table
        for i in range(1, 6):  # Max 5 levels
            level_heading = self._find_heading(soup, [f'level {i}', f'tier {i}'])
            if level_heading:
                requirements = self._extract_material_list(level_heading)
                levels.append({
                    "level": i,
                    "requirements": requirements
                })
        return levels
    
    def _parse_int(self, value: str) -> Optional[int]:
        """Parse integer from string, handling formats like '1,000' or '5x'"""
        if not value:
            return None
        # Remove common characters
        cleaned = re.sub(r'[,x\s]', '', value)
        try:
            return int(cleaned)
        except:
            return None
    
    def save_item(self, data: Dict[str, Any]) -> bool:
        """Save or update item in database"""
        if not data.get("name"):
            print(f"  ⚠ Skipping item - no name found")
            return False
        
        try:
            # Check if item already exists
            existing = self.db.query(Item).filter(Item.name == data["name"]).first()
            
            if existing:
                # Update existing
                for key, value in data.items():
                    if hasattr(existing, key):
                        setattr(existing, key, value)
                self.db.commit()
                self.stats["items_updated"] += 1
                print(f"  ✓ Updated: {data['name']}")
            else:
                # Create new
                item = Item(**data)
                self.db.add(item)
                self.db.commit()
                self.stats["items_created"] += 1
                print(f"  ✓ Created: {data['name']}")
            
            return True
        except Exception as e:
            print(f"  ✗ Error saving item {data.get('name')}: {e}")
            self.db.rollback()
            self.stats["errors"].append({"name": data.get("name"), "error": str(e)})
            return False
    
    def save_task(self, data: Dict[str, Any]) -> bool:
        """Save or update task in database"""
        if not data.get("name"):
            print(f"  ⚠ Skipping task - no name found")
            return False
        
        try:
            # Check if task already exists
            existing = self.db.query(Task).filter(Task.name == data["name"]).first()
            
            if existing:
                # Update existing
                for key, value in data.items():
                    if hasattr(existing, key):
                        setattr(existing, key, value)
                self.db.commit()
                self.stats["tasks_updated"] += 1
                print(f"  ✓ Updated: {data['name']}")
            else:
                # Create new
                task = Task(**data)
                self.db.add(task)
                self.db.commit()
                self.stats["tasks_created"] += 1
                print(f"  ✓ Created: {data['name']}")
            
            return True
        except Exception as e:
            print(f"  ✗ Error saving task {data.get('name')}: {e}")
            self.db.rollback()
            self.stats["errors"].append({"name": data.get("name"), "error": str(e)})
            return False
    
    def scrape_item_page(self, url: str):
        """Scrape a single item page and save to database"""
        soup = self.fetch_page(url)
        if not soup:
            return
        
        data = self.extract_item_data(soup, url)
        if self.save_item(data):
            self.stats["items_scraped"] += 1
        
        # Be polite to the server
        time.sleep(0.5)
    
    def scrape_task_page(self, url: str):
        """Scrape a single task/quest/workshop page and save to database"""
        soup = self.fetch_page(url)
        if not soup:
            return
        
        data = self.extract_task_data(soup, url)
        if self.save_task(data):
            self.stats["tasks_scraped"] += 1
        
        # Be polite to the server
        time.sleep(0.5)
    
    def run_full_scrape(self, links_file: str, limit: Optional[int] = None):
        """Load discovered links and scrape all pages"""
        print("=" * 70)
        print("Arc Raiders Wiki - Database Population")
        print("=" * 70)
        print()
        
        # Load discovered links
        with open(links_file, 'r') as f:
            links = json.load(f)
        
        item_urls = links.get("item_pages", [])
        task_urls = links.get("task_pages", [])
        
        print(f"Loaded {len(item_urls)} item URLs")
        print(f"Loaded {len(task_urls)} task URLs")
        
        if limit:
            print(f"Limiting to first {limit} of each type for testing")
            item_urls = item_urls[:limit]
            task_urls = task_urls[:limit]
        
        print()
        
        # Scrape items
        print(f"Scraping {len(item_urls)} items...")
        print("-" * 70)
        for i, url in enumerate(item_urls, 1):
            print(f"[{i}/{len(item_urls)}] Item:")
            self.scrape_item_page(url)
        
        print()
        
        # Scrape tasks
        print(f"Scraping {len(task_urls)} tasks...")
        print("-" * 70)
        for i, url in enumerate(task_urls, 1):
            print(f"[{i}/{len(task_urls)}] Task:")
            self.scrape_task_page(url)
        
        print()
        self.print_stats()
    
    def print_stats(self):
        """Print scraping statistics"""
        print("=" * 70)
        print("Scraping Complete!")
        print("=" * 70)
        print(f"Items:")
        print(f"  - Scraped: {self.stats['items_scraped']}")
        print(f"  - Created: {self.stats['items_created']}")
        print(f"  - Updated: {self.stats['items_updated']}")
        print(f"Tasks:")
        print(f"  - Scraped: {self.stats['tasks_scraped']}")
        print(f"  - Created: {self.stats['tasks_created']}")
        print(f"  - Updated: {self.stats['tasks_updated']}")
        print(f"Errors: {len(self.stats['errors'])}")
        if self.stats['errors']:
            print("\nErrors:")
            for err in self.stats['errors'][:10]:  # Show first 10
                print(f"  - {err}")
    
    def close(self):
        """Close database connection"""
        self.db.close()


if __name__ == "__main__":
    import argparse
    from scraper.precise_index_scraper import PreciseIndexScraper
    
    parser = argparse.ArgumentParser(description='Scrape Arc Raiders wiki and populate database')
    parser.add_argument('--links', help='Path to discovered links JSON file (if not provided, will run index scraper)')
    parser.add_argument('--limit', type=int, help='Limit number of pages to scrape (for testing)')
    parser.add_argument('--test', action='store_true', help='Test mode - scrape only 5 of each type')
    parser.add_argument('--skip-index', action='store_true', help='Skip running index scraper, use existing links file')
    
    args = parser.parse_args()
    
    # Determine links file to use
    links_file = args.links
    
    if not args.skip_index and not links_file:
        # Run the precise index scraper first
        print("=" * 70)
        print("Step 1: Running Index Scraper")
        print("=" * 70)
        index_scraper = PreciseIndexScraper()
        index_scraper.run_all()
        links_file = index_scraper.save_results()
        index_scraper.print_summary()
        print("\n")
    
    # If still no links file, try to find the most recent one
    if not links_file:
        links_dir = Path("scraped_data")
        precise_files = sorted(links_dir.glob("precise_links_*.json"), reverse=True)
        if precise_files:
            links_file = str(precise_files[0])
            print(f"Using most recent links file: {links_file}\n")
        else:
            print("❌ No links file found. Run with --links or without --skip-index")
            sys.exit(1)
    
    # Run the database populator
    print("=" * 70)
    print("Step 2: Populating Database")
    print("=" * 70)
    scraper = WikiDatabasePopulator()
    
    try:
        if args.test:
            print("🧪 TEST MODE - Scraping 5 items and 5 tasks")
            print()
            scraper.run_full_scrape(links_file, limit=5)
        else:
            scraper.run_full_scrape(links_file, limit=args.limit)
    finally:
        scraper.close()
