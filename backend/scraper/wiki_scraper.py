"""
Targeted wiki scraper to analyze data structure from https://arcraiders.wiki/

This script will:
1. Scrape specific pages provided by the user
2. Extract and analyze the data structure
3. Document available fields and relationships
4. Output findings to help design the database schema
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

class WikiScraper:
    def __init__(self, output_dir: str = "scraped_data"):
        self.base_url = os.getenv("WIKI_BASE_URL", "https://arcraiders.wiki/")
        self.user_agent = os.getenv("SCRAPER_USER_AGENT", "ArcRaidersWikiBot/1.0")
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": self.user_agent})
        
        # Create output directory
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Storage for scraped data
        self.scraped_pages = []
        self.findings = {
            "items": [],
            "tasks": [],
            "other": []
        }
        self.discovered_links = {
            "item_pages": [],
            "task_pages": []
        }
    
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
    
    def extract_page_data(self, soup: BeautifulSoup, url: str, page_type: str = "unknown") -> Dict[str, Any]:
        """
        Extract raw data from a page for analysis
        
        Args:
            soup: BeautifulSoup object of the page
            url: URL of the page
            page_type: Type of page (item, quest, expedition, etc.)
        
        Returns:
            Dictionary containing extracted data
        """
        data = {
            "url": url,
            "page_type": page_type,
            "scraped_at": datetime.now().isoformat(),
            "title": None,
            "meta_tags": {},
            "headings": [],
            "tables": [],
            "images": [],
            "links": [],
            "text_content": None,
            "raw_html_structure": []
        }
        
        # Extract title
        title_tag = soup.find('title')
        if title_tag:
            data["title"] = title_tag.get_text(strip=True)
        
        # Extract meta tags
        for meta in soup.find_all('meta'):
            if meta.get('name') or meta.get('property'):
                key = meta.get('name') or meta.get('property')
                data["meta_tags"][key] = meta.get('content', '')
        
        # Extract headings
        for level in range(1, 7):
            for heading in soup.find_all(f'h{level}'):
                data["headings"].append({
                    "level": level,
                    "text": heading.get_text(strip=True)
                })
        
        # Extract tables
        for table in soup.find_all('table'):
            table_data = {
                "headers": [],
                "rows": [],
                "row_links": []  # Store links found in table rows
            }
            
            # Get headers
            for th in table.find_all('th'):
                table_data["headers"].append(th.get_text(strip=True))
            
            # Get rows
            for tr in table.find_all('tr'):
                row = []
                row_links = []
                for td in tr.find_all('td'):
                    row.append(td.get_text(strip=True))
                    # Extract links within table cells
                    for link in td.find_all('a', href=True):
                        row_links.append({
                            "href": link['href'],
                            "text": link.get_text(strip=True)
                        })
                if row:
                    table_data["rows"].append(row)
                    if row_links:
                        table_data["row_links"].append(row_links)
            
            if table_data["headers"] or table_data["rows"]:
                data["tables"].append(table_data)
        
        # Extract images
        for img in soup.find_all('img'):
            data["images"].append({
                "src": img.get('src', ''),
                "alt": img.get('alt', ''),
                "title": img.get('title', '')
            })
        
        # Extract internal links
        for link in soup.find_all('a', href=True):
            href = link['href']
            # Only include links that might be wiki pages
            if href.startswith('/') or self.base_url in href:
                data["links"].append({
                    "href": href,
                    "text": link.get_text(strip=True)
                })
        
        # Extract main content area (if identifiable)
        main_content = soup.find('main') or soup.find('article') or soup.find('div', class_='content')
        if main_content:
            data["text_content"] = main_content.get_text(separator='\n', strip=True)
        else:
            # Fallback to body
            body = soup.find('body')
            if body:
                data["text_content"] = body.get_text(separator='\n', strip=True)
        
        # Extract raw HTML structure (tag hierarchy)
        body = soup.find('body')
        if body:
            data["raw_html_structure"] = self._get_structure(body, max_depth=3)
        
        return data
    
    def _get_structure(self, element, current_depth=0, max_depth=3) -> List[Dict[str, Any]]:
        """Recursively extract HTML structure"""
        if current_depth >= max_depth:
            return []
        
        structure = []
        for child in element.children:
            if child.name:  # Skip text nodes
                child_data = {
                    "tag": child.name,
                    "classes": child.get('class', []),
                    "id": child.get('id', ''),
                    "children_count": len(list(child.children))
                }
                structure.append(child_data)
        
        return structure
    
    def scrape_urls(self, urls: List[Dict[str, str]]) -> None:
        """
        Scrape multiple URLs
        
        Args:
            urls: List of dictionaries with 'url' and 'type' keys
                  Example: [{"url": "https://...", "type": "item"}]
        """
        print(f"\n{'='*60}")
        print(f"Starting scrape of {len(urls)} page(s)")
        print(f"{'='*60}\n")
        
        for i, page_info in enumerate(urls, 1):
            url = page_info.get('url')
            page_type = page_info.get('type', 'unknown')
            
            print(f"\n[{i}/{len(urls)}] Processing {page_type} page...")
            
            soup = self.fetch_page(url)
            if soup:
                data = self.extract_page_data(soup, url, page_type)
                self.scraped_pages.append(data)
                
                # Categorize findings
                if page_type in self.findings:
                    self.findings[page_type].append(data)
                    
                    # Collect links from tables for further scraping
                    for table in data.get('tables', []):
                        for row_links in table.get('row_links', []):
                            for link in row_links:
                                href = link['href']
                                # Make absolute URL if relative
                                if href.startswith('/'):
                                    full_url = self.base_url.rstrip('/') + href
                                elif not href.startswith('http'):
                                    full_url = self.base_url.rstrip('/') + '/' + href
                                else:
                                    full_url = href
                                
                                # Categorize discovered links
                                if page_type == "items":
                                    if full_url not in self.discovered_links["item_pages"]:
                                        self.discovered_links["item_pages"].append(full_url)
                                elif page_type == "tasks":
                                    if full_url not in self.discovered_links["task_pages"]:
                                        self.discovered_links["task_pages"].append(full_url)
                else:
                    self.findings["other"].append(data)
                
                print(f"  → Extracted: {len(data['headings'])} headings, {len(data['tables'])} tables, {len(data['images'])} images")
            else:
                print(f"  → Failed to fetch page")
        
        print(f"\n{'='*60}")
        print(f"Scraping complete! Processed {len(self.scraped_pages)} page(s)")
        print(f"{'='*60}\n")
    
    def save_results(self) -> str:
        """Save scraped data to JSON files"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save full scraped data
        full_data_file = self.output_dir / f"scraped_data_{timestamp}.json"
        with open(full_data_file, 'w', encoding='utf-8') as f:
            json.dump(self.scraped_pages, f, indent=2, ensure_ascii=False)
        print(f"✓ Saved full data to: {full_data_file}")
        
        # Save categorized findings
        findings_file = self.output_dir / f"findings_{timestamp}.json"
        with open(findings_file, 'w', encoding='utf-8') as f:
            json.dump(self.findings, f, indent=2, ensure_ascii=False)
        print(f"✓ Saved findings to: {findings_file}")
        
        # Save discovered links for potential further scraping
        links_file = self.output_dir / f"discovered_links_{timestamp}.json"
        with open(links_file, 'w', encoding='utf-8') as f:
            json.dump(self.discovered_links, f, indent=2, ensure_ascii=False)
        print(f"✓ Saved discovered links to: {links_file}")
        print(f"  → Found {len(self.discovered_links['item_pages'])} item page links")
        print(f"  → Found {len(self.discovered_links['task_pages'])} task page links")
        
        # Generate and save analysis report
        report = self.generate_report()
        report_file = self.output_dir / f"analysis_report_{timestamp}.md"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"✓ Saved analysis report to: {report_file}")
        
        return str(report_file)
    
    def generate_report(self) -> str:
        """Generate a markdown report of findings"""
        report = ["# Wiki Scraping Analysis Report\n"]
        report.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        report.append(f"**Pages Scraped:** {len(self.scraped_pages)}\n\n")
        
        # Database design notes
        report.append("## Database Design Notes\n\n")
        report.append("Based on the requirements:\n\n")
        report.append("### Items Table (Shared)\n")
        report.append("- Loot, Weapons, and Equipment will share one `items` table\n")
        report.append("- Include a `type` field to denote: 'loot', 'weapon', 'equipment'\n")
        report.append("- Items can be used for crafting OR salvaged into other items\n")
        report.append("- Relationships: many-to-many for crafting and salvaging\n\n")
        
        report.append("### Tasks Table (Shared)\n")
        report.append("- Quests, Expeditions, and Workshops will share one `tasks` table\n")
        report.append("- Include a `type` field to denote: 'quest', 'expedition', 'workshop'\n")
        report.append("- Track components needed (for upgrades/completion)\n")
        report.append("- Checkable/completable items\n\n")
        
        report.append("---\n\n")
        
        # Summary by type
        report.append("## Summary by Page Type\n\n")
        for page_type, pages in self.findings.items():
            if pages:
                report.append(f"### {page_type.capitalize()} ({len(pages)} page(s))\n\n")
                for page in pages:
                    report.append(f"**URL:** {page['url']}\n")
                    report.append(f"**Title:** {page['title']}\n\n")
                    
                    if page['headings']:
                        report.append("**Headings:**\n")
                        for h in page['headings'][:10]:  # Limit to first 10
                            report.append(f"- H{h['level']}: {h['text']}\n")
                        report.append("\n")
                    
                    if page['tables']:
                        report.append(f"**Tables Found:** {len(page['tables'])}\n")
                        for i, table in enumerate(page['tables'][:3], 1):  # Show first 3 tables
                            report.append(f"\nTable {i} Headers: {', '.join(table['headers']) if table['headers'] else 'None'}\n")
                            if table.get('row_links'):
                                report.append(f"  → Contains {sum(len(links) for links in table['row_links'])} links to individual pages\n")
                        report.append("\n")
                    
                    if page['images']:
                        report.append(f"**Images:** {len(page['images'])}\n\n")
                    
                    report.append("---\n\n")
        
        # Discovered links section
        report.append("## Discovered Individual Pages\n\n")
        report.append(f"**Item Pages:** {len(self.discovered_links['item_pages'])} links found\n")
        report.append(f"**Task Pages:** {len(self.discovered_links['task_pages'])} links found\n\n")
        report.append("These links point to individual item/task detail pages that can be scraped for complete information.\n")
        report.append("See `discovered_links_*.json` for the full list of URLs.\n\n")
        
        # Recommendations
        report.append("## Next Steps\n\n")
        report.append("1. **Review the table structures** in the JSON files to understand data fields\n")
        report.append("2. **Scrape sample individual pages** from the discovered links to get full details\n")
        report.append("3. **Design the PostgreSQL schema** with:\n")
        report.append("   - `items` table (type: loot/weapon/equipment)\n")
        report.append("   - `tasks` table (type: quest/expedition/workshop)\n")
        report.append("   - `crafting_relationships` table (many-to-many)\n")
        report.append("   - `salvaging_relationships` table (many-to-many)\n")
        report.append("   - `task_requirements` table (components needed)\n")
        report.append("4. **Update Project Overview** with discovered data structure\n\n")
        
        return ''.join(report)
    
    def print_summary(self) -> None:
        """Print a summary of scraped data to console"""
        print("\n" + "="*60)
        print("SCRAPING SUMMARY")
        print("="*60)
        
        for page_type, pages in self.findings.items():
            if pages:
                print(f"\n{page_type.upper()}: {len(pages)} page(s)")
                for page in pages:
                    print(f"  • {page['title']}")
                    print(f"    {page['url']}")

def main():
    """
    Main function - scrape Arc Raiders wiki pages
    """
    # Initialize scraper (use relative path from backend directory)
    scraper = WikiScraper(output_dir="scraped_data")
    
    # Define pages to scrape
    # These are the main index/list pages that contain tables with links to individual items
    pages_to_scrape = [
        # Item-related pages (Loot, Weapons, Equipment share the items table)
        {"url": "https://arcraiders.wiki/wiki/Loot", "type": "items"},
        {"url": "https://arcraiders.wiki/wiki/Weapons", "type": "items"},
        {"url": "https://arcraiders.wiki/wiki/Equipment", "type": "items"},
        
        # Taskable pages (Quests, Expeditions, Workshops share the tasks table)
        {"url": "https://arcraiders.wiki/wiki/Quests", "type": "tasks"},
        {"url": "https://arcraiders.wiki/wiki/Expedition-1", "type": "tasks"},
        {"url": "https://arcraiders.wiki/wiki/Workshop", "type": "tasks"},
    ]
    
    if not pages_to_scrape:
        print("\n" + "!"*60)
        print("NO PAGES CONFIGURED!")
        print("!"*60)
        print("\nPlease add URLs to the 'pages_to_scrape' list in main()")
        print("\nExample:")
        print('pages_to_scrape = [')
        print('    {"url": "https://arcraiders.wiki/items/arc-weapon", "type": "item"},')
        print('    {"url": "https://arcraiders.wiki/quests/main-quest-1", "type": "quest"},')
        print(']')
        print("\nThen run: python -m scraper.wiki_scraper")
        return
    
    # Scrape the pages
    scraper.scrape_urls(pages_to_scrape)
    
    # Save results
    report_file = scraper.save_results()
    
    # Print summary
    scraper.print_summary()
    
    print(f"\n{'='*60}")
    print("Next Steps:")
    print("="*60)
    print(f"1. Review the analysis report: {report_file}")
    print("2. Check the JSON files in backend/scraped_data/")
    print("3. Design database schema based on findings")
    print("4. Update Project Overview with discovered data structure")
    print("="*60 + "\n")

if __name__ == "__main__":
    main()
