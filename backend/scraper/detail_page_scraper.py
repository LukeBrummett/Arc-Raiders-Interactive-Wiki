"""
Enhanced scraper for Arc Raiders wiki detail pages

This scraper extracts complete information from individual item/task pages
including stats, crafting recipes, sources, and relationships.
"""

import requests
from bs4 import BeautifulSoup
import json
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv
import os
from datetime import datetime
from pathlib import Path

load_dotenv()


class DetailPageScraper:
    def __init__(self, output_dir: str = "scraped_data/details"):
        self.base_url = os.getenv("WIKI_BASE_URL", "https://arcraiders.wiki/")
        self.user_agent = os.getenv("SCRAPER_USER_AGENT", "ArcRaidersWikiBot/1.0")
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": self.user_agent})
        
        # Create output directory
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Storage for scraped items
        self.items = []
        self.tasks = []
    
    def fetch_page(self, url: str) -> Optional[BeautifulSoup]:
        """Fetch a page and return BeautifulSoup object"""
        try:
            print(f"Fetching: {url}")
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            print(f"✓ Success (Status: {response.status_code})")
            return BeautifulSoup(response.content, 'lxml')
        except requests.RequestException as e:
            print(f"✗ Error fetching {url}: {e}")
            return None
    
    def extract_item_page(self, soup: BeautifulSoup, url: str) -> Dict[str, Any]:
        """
        Extract detailed item data from an individual item page
        
        Based on the structure seen in Advanced ARC Powercell page
        """
        item = {
            "url": url,
            "scraped_at": datetime.now().isoformat(),
            "name": None,
            "description": None,
            "image_url": None,
            "category": None,
            "rarity": None,
            "stats": {
                "can_be_found_in": None,
                "weight": None,
                "stack_size": None,
                "sell_price": None,
                "ammo_type": None,  # For weapons
                "damage": None,      # For weapons
                "firing_mode": None, # For weapons
                "range": None        # For weapons
            },
            "sources": [],  # Where to obtain (enemies, locations)
            "crafting_recipes": [],  # What you can craft WITH this item
            "recycled_material": [],  # What you get when recycling this
            "salvaged_material": [],  # What you get when salvaging this
            "keep_for_quests_workshop": False
        }
        
        # Extract title/name
        h1 = soup.find('h1')
        if h1:
            item["name"] = h1.get_text(strip=True)
        
        # Extract main image
        # Look for the main item image in the infobox or content area
        main_image = soup.find('img', class_='thumbimage') or soup.find('a', class_='image')
        if main_image:
            if main_image.name == 'img':
                item["image_url"] = main_image.get('src', '')
            else:
                img = main_image.find('img')
                if img:
                    item["image_url"] = img.get('src', '')
        
        # Extract description (first paragraph or intro text)
        # Usually appears right after the title or in a specific div
        intro = soup.find('div', class_='mw-parser-output')
        if intro:
            # Get first paragraph or text before first heading
            for elem in intro.children:
                if elem.name == 'p':
                    desc_text = elem.get_text(strip=True)
                    if desc_text:
                        item["description"] = desc_text
                        break
        
        # Extract category (from bottom of page or infobox)
        category_elem = soup.find('div', id='mw-normal-catlinks')
        if category_elem:
            category_links = category_elem.find_all('a')
            if category_links:
                # Last category is usually the most specific
                item["category"] = category_links[-1].get_text(strip=True)
        
        # Extract stats from the info table (right side of page)
        # Look for table or div containing stats
        stats_found = False
        
        # Try to find infobox or stats table
        for table in soup.find_all('table'):
            rows = table.find_all('tr')
            for row in rows:
                cells = row.find_all(['th', 'td'])
                if len(cells) >= 2:
                    key = cells[0].get_text(strip=True).lower()
                    value = cells[1].get_text(strip=True)
                    
                    # Map to our stats structure
                    if 'can be found' in key or 'found in' in key:
                        item["stats"]["can_be_found_in"] = value
                        stats_found = True
                    elif 'weight' in key:
                        item["stats"]["weight"] = value
                        stats_found = True
                    elif 'stack size' in key:
                        try:
                            item["stats"]["stack_size"] = int(value)
                        except:
                            item["stats"]["stack_size"] = value
                        stats_found = True
                    elif 'sell price' in key or 'price' in key:
                        item["stats"]["sell_price"] = value
                        stats_found = True
                    elif 'rarity' in key:
                        item["rarity"] = value
                        stats_found = True
                    elif 'ammo type' in key or 'ammo' in key:
                        item["stats"]["ammo_type"] = value
                        stats_found = True
                    elif 'damage' in key:
                        item["stats"]["damage"] = value
                        stats_found = True
                    elif 'firing mode' in key:
                        item["stats"]["firing_mode"] = value
                        stats_found = True
                    elif 'range' in key:
                        item["stats"]["range"] = value
                        stats_found = True
        
        # Extract Sources section
        sources_heading = soup.find(['h2', 'h3'], string=lambda s: s and 'source' in s.lower())
        if sources_heading:
            # Find the list after the heading
            next_elem = sources_heading.find_next(['ul', 'ol'])
            if next_elem:
                for li in next_elem.find_all('li'):
                    source_text = li.get_text(strip=True)
                    # Also get link if available
                    link = li.find('a')
                    item["sources"].append({
                        "name": source_text,
                        "url": link.get('href', '') if link else None
                    })
        
        # Extract Crafting section (recipes using this item)
        crafting_heading = soup.find(['h2', 'h3'], string=lambda s: s and 'crafting' in s.lower())
        if crafting_heading:
            item["crafting_recipes"] = self._extract_crafting_recipes(crafting_heading)
        
        # Extract Recycled Material section
        recycled_heading = soup.find(['h2', 'h3'], string=lambda s: s and 'recycled material' in s.lower())
        if recycled_heading:
            item["recycled_material"] = self._extract_material_conversion(recycled_heading)
        
        # Extract Salvaged Material section
        salvaged_heading = soup.find(['h2', 'h3'], string=lambda s: s and 'salvaged material' in s.lower())
        if salvaged_heading:
            item["salvaged_material"] = self._extract_material_conversion(salvaged_heading)
        
        return item
    
    def _extract_crafting_recipes(self, heading) -> List[Dict[str, Any]]:
        """Extract crafting recipe information"""
        recipes = []
        
        # Look for table or structured data after the heading
        next_elem = heading.find_next(['table', 'div'])
        if not next_elem:
            return recipes
        
        # If it's a table, parse rows
        if next_elem.name == 'table':
            for row in next_elem.find_all('tr')[1:]:  # Skip header
                cells = row.find_all(['td', 'th'])
                if len(cells) >= 3:
                    recipe = {
                        "ingredients": [],
                        "workshop": None,
                        "output": []
                    }
                    
                    # Parse ingredients (first cell)
                    ingredients_text = cells[0].get_text(strip=True)
                    recipe["ingredients"] = self._parse_item_quantity(ingredients_text)
                    
                    # Workshop/crafting station (middle cell)
                    if len(cells) > 1:
                        recipe["workshop"] = cells[1].get_text(strip=True)
                    
                    # Output (last cell)
                    if len(cells) > 2:
                        output_text = cells[2].get_text(strip=True)
                        recipe["output"] = self._parse_item_quantity(output_text)
                    
                    recipes.append(recipe)
        
        return recipes
    
    def _extract_material_conversion(self, heading) -> List[Dict[str, Any]]:
        """Extract recycling/salvaging material conversion data"""
        conversions = []
        
        # Look for content after heading
        next_elem = heading.find_next(['table', 'p', 'div'])
        if not next_elem:
            return conversions
        
        # Parse conversion data (format: 1x Item A → 2x Item B)
        if next_elem.name == 'table':
            for row in next_elem.find_all('tr')[1:]:  # Skip header
                cells = row.find_all(['td', 'th'])
                if len(cells) >= 2:
                    conversion = {
                        "input": self._parse_item_quantity(cells[0].get_text(strip=True)),
                        "output": self._parse_item_quantity(cells[1].get_text(strip=True))
                    }
                    conversions.append(conversion)
        else:
            # Parse from text (e.g., "1x Advanced ARC Powercell → 2x ARC Powercell")
            text = next_elem.get_text()
            # TODO: Implement text parsing if needed
        
        return conversions
    
    def _parse_item_quantity(self, text: str) -> List[Dict[str, Any]]:
        """
        Parse item quantities from text like "1x Battery" or "5x Energy Clip"
        Returns list of {item: name, quantity: number}
        """
        items = []
        
        # Split by common separators
        parts = text.split('+')
        for part in parts:
            part = part.strip()
            
            # Try to extract quantity and item name
            # Pattern: "1x Item Name" or "Item Name"
            if 'x' in part:
                qty_str, item_name = part.split('x', 1)
                try:
                    quantity = int(qty_str.strip())
                except:
                    quantity = 1
                item_name = item_name.strip()
            else:
                quantity = 1
                item_name = part.strip()
            
            if item_name:
                items.append({
                    "item": item_name,
                    "quantity": quantity
                })
        
        return items
    
    def scrape_sample_items(self, urls: List[str]) -> None:
        """Scrape a sample of item detail pages"""
        print(f"\n{'='*60}")
        print(f"Scraping {len(urls)} sample item page(s)")
        print(f"{'='*60}\n")
        
        for i, url in enumerate(urls, 1):
            print(f"\n[{i}/{len(urls)}] Processing item...")
            
            soup = self.fetch_page(url)
            if soup:
                item_data = self.extract_item_page(soup, url)
                self.items.append(item_data)
                
                print(f"  → Extracted: {item_data['name']}")
                print(f"     Category: {item_data['category']}")
                print(f"     Sources: {len(item_data['sources'])}")
                print(f"     Crafting recipes: {len(item_data['crafting_recipes'])}")
            else:
                print(f"  → Failed to fetch page")
        
        print(f"\n{'='*60}")
        print(f"Scraping complete! Processed {len(self.items)} item(s)")
        print(f"{'='*60}\n")
    
    def save_results(self) -> str:
        """Save scraped detail data to JSON files"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save items
        if self.items:
            items_file = self.output_dir / f"items_detail_{timestamp}.json"
            with open(items_file, 'w', encoding='utf-8') as f:
                json.dump(self.items, f, indent=2, ensure_ascii=False)
            print(f"✓ Saved {len(self.items)} items to: {items_file}")
        
        # Generate schema analysis
        schema_report = self.generate_schema_analysis()
        schema_file = self.output_dir / f"schema_analysis_{timestamp}.md"
        with open(schema_file, 'w', encoding='utf-8') as f:
            f.write(schema_report)
        print(f"✓ Saved schema analysis to: {schema_file}")
        
        return str(schema_file)
    
    def generate_schema_analysis(self) -> str:
        """Generate a detailed schema analysis based on scraped detail pages"""
        report = ["# Detailed Schema Analysis from Detail Pages\n"]
        report.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        report.append(f"**Items Analyzed:** {len(self.items)}\n\n")
        report.append("---\n\n")
        
        # Analyze fields
        report.append("## Discovered Fields\n\n")
        
        if self.items:
            sample_item = self.items[0]
            report.append("### Item Fields\n\n")
            report.append("```json\n")
            report.append(json.dumps(sample_item, indent=2))
            report.append("\n```\n\n")
            
            # Field statistics
            report.append("### Field Usage Statistics\n\n")
            for item in self.items:
                report.append(f"**{item['name']}**\n")
                report.append(f"- Category: {item['category']}\n")
                report.append(f"- Has Stats: {bool(any(item['stats'].values()))}\n")
                report.append(f"- Sources: {len(item['sources'])}\n")
                report.append(f"- Crafting Recipes: {len(item['crafting_recipes'])}\n")
                report.append(f"- Can be Recycled: {bool(item['recycled_material'])}\n")
                report.append(f"- Can be Salvaged: {bool(item['salvaged_material'])}\n")
                report.append("\n")
        
        # SQL Schema recommendations
        report.append("## Updated SQL Schema Recommendations\n\n")
        report.append("Based on detail page analysis:\n\n")
        
        report.append("### Items Table\n")
        report.append("```sql\n")
        report.append("CREATE TABLE items (\n")
        report.append("    id SERIAL PRIMARY KEY,\n")
        report.append("    name VARCHAR(255) NOT NULL UNIQUE,\n")
        report.append("    description TEXT,\n")
        report.append("    image_url TEXT,\n")
        report.append("    category VARCHAR(100),\n")
        report.append("    rarity VARCHAR(50),\n")
        report.append("    type VARCHAR(50), -- 'loot', 'weapon', 'equipment'\n")
        report.append("    \n")
        report.append("    -- Stats\n")
        report.append("    can_be_found_in VARCHAR(255),\n")
        report.append("    weight VARCHAR(50),\n")
        report.append("    stack_size INTEGER,\n")
        report.append("    sell_price INTEGER,\n")
        report.append("    \n")
        report.append("    -- Weapon-specific (nullable)\n")
        report.append("    ammo_type VARCHAR(50),\n")
        report.append("    damage VARCHAR(50),\n")
        report.append("    firing_mode VARCHAR(50),\n")
        report.append("    range VARCHAR(50),\n")
        report.append("    \n")
        report.append("    -- Flags\n")
        report.append("    keep_for_quests_workshop BOOLEAN DEFAULT FALSE,\n")
        report.append("    \n")
        report.append("    -- Metadata\n")
        report.append("    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,\n")
        report.append("    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP\n")
        report.append(");\n")
        report.append("```\n\n")
        
        report.append("### Item Sources Table\n")
        report.append("```sql\n")
        report.append("CREATE TABLE item_sources (\n")
        report.append("    id SERIAL PRIMARY KEY,\n")
        report.append("    item_id INTEGER REFERENCES items(id) ON DELETE CASCADE,\n")
        report.append("    source_name VARCHAR(255), -- Enemy, location, etc.\n")
        report.append("    source_url TEXT,\n")
        report.append("    UNIQUE(item_id, source_name)\n")
        report.append(");\n")
        report.append("```\n\n")
        
        report.append("### Crafting Recipes Table\n")
        report.append("```sql\n")
        report.append("CREATE TABLE crafting_recipes (\n")
        report.append("    id SERIAL PRIMARY KEY,\n")
        report.append("    workshop VARCHAR(100), -- 'Workbench 1', 'Medical Lab 2', etc.\n")
        report.append("    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP\n")
        report.append(");\n")
        report.append("```\n\n")
        
        report.append("### Recipe Ingredients Table\n")
        report.append("```sql\n")
        report.append("CREATE TABLE recipe_ingredients (\n")
        report.append("    id SERIAL PRIMARY KEY,\n")
        report.append("    recipe_id INTEGER REFERENCES crafting_recipes(id) ON DELETE CASCADE,\n")
        report.append("    item_id INTEGER REFERENCES items(id) ON DELETE CASCADE,\n")
        report.append("    quantity INTEGER NOT NULL\n")
        report.append(");\n")
        report.append("```\n\n")
        
        report.append("### Recipe Outputs Table\n")
        report.append("```sql\n")
        report.append("CREATE TABLE recipe_outputs (\n")
        report.append("    id SERIAL PRIMARY KEY,\n")
        report.append("    recipe_id INTEGER REFERENCES crafting_recipes(id) ON DELETE CASCADE,\n")
        report.append("    item_id INTEGER REFERENCES items(id) ON DELETE CASCADE,\n")
        report.append("    quantity INTEGER NOT NULL\n")
        report.append(");\n")
        report.append("```\n\n")
        
        report.append("### Material Conversions Table (Recycling/Salvaging)\n")
        report.append("```sql\n")
        report.append("CREATE TABLE material_conversions (\n")
        report.append("    id SERIAL PRIMARY KEY,\n")
        report.append("    input_item_id INTEGER REFERENCES items(id) ON DELETE CASCADE,\n")
        report.append("    output_item_id INTEGER REFERENCES items(id) ON DELETE CASCADE,\n")
        report.append("    input_quantity INTEGER NOT NULL,\n")
        report.append("    output_quantity INTEGER NOT NULL,\n")
        report.append("    conversion_type VARCHAR(50) -- 'recycle' or 'salvage'\n")
        report.append(");\n")
        report.append("```\n\n")
        
        return ''.join(report)


def main():
    """Scrape sample detail pages to understand structure"""
    scraper = DetailPageScraper()
    
    # Sample URLs based on your discovered links
    sample_item_urls = [
        "https://arcraiders.wiki/wiki/Advanced_ARC_Powercell",  # The one you showed
        "https://arcraiders.wiki/wiki/Rattler",  # A weapon
        "https://arcraiders.wiki/wiki/Battery",  # Simple crafting material
        "https://arcraiders.wiki/wiki/Light_Shield",  # Equipment
    ]
    
    # Scrape the samples
    scraper.scrape_sample_items(sample_item_urls)
    
    # Save results
    schema_file = scraper.save_results()
    
    print(f"\n{'='*60}")
    print("Next Steps:")
    print("="*60)
    print(f"1. Review the schema analysis: {schema_file}")
    print("2. Check the detailed JSON data")
    print("3. Refine the SQL schema based on findings")
    print("4. Create database migrations")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
