"""
Interactive data extraction validator

This tool lets you:
1. Pick a sample URL (item or task)
2. See exactly what data the scraper extracts
3. Validate each field one by one
4. Adjust extraction logic as needed

Run this BEFORE populating the database to ensure data quality.
"""

import requests
from bs4 import BeautifulSoup
from typing import Dict, Any, Optional
import json
import sys
import random
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from populate_database import WikiDatabasePopulator

class DataValidator:
    def __init__(self):
        self.populator = WikiDatabasePopulator()
        
    def load_sample_urls(self) -> Dict[str, list]:
        """Load random sample URLs from the most recent precise links file"""
        links_dir = Path("scraped_data")
        precise_files = sorted(links_dir.glob("precise_links_*.json"), reverse=True)
        
        if not precise_files:
            print("❌ No precise links file found. Run the index scraper first.")
            sys.exit(1)
        
        with open(precise_files[0], 'r') as f:
            data = json.load(f)
        
        # Get random samples
        item_pages = data.get("item_pages", [])
        task_pages = data.get("task_pages", [])
        
        return {
            "items": random.sample(item_pages, min(10, len(item_pages))),
            "tasks": random.sample(task_pages, min(10, len(task_pages)))
        }
    
    def display_extracted_data(self, data: Dict[str, Any], data_type: str):
        """Display extracted data in a readable format"""
        print("\n" + "=" * 70)
        print(f"EXTRACTED {data_type.upper()} DATA")
        print("=" * 70)
        
        for key, value in data.items():
            print(f"\n📋 {key}:")
            
            if isinstance(value, dict):
                if value:
                    print(json.dumps(value, indent=2))
                else:
                    print("  (empty dict)")
            elif isinstance(value, list):
                if value:
                    for i, item in enumerate(value[:5], 1):  # Show first 5
                        if isinstance(item, dict):
                            print(f"  [{i}] {json.dumps(item, indent=6)}")
                        else:
                            print(f"  [{i}] {item}")
                    if len(value) > 5:
                        print(f"  ... and {len(value) - 5} more")
                else:
                    print("  (empty list)")
            elif value is None:
                print(f"  ⚠️  None")
            else:
                # String or other
                if len(str(value)) > 200:
                    print(f"  {str(value)[:200]}...")
                else:
                    print(f"  {value}")
    
    def validate_item(self, url: str):
        """Validate item data extraction"""
        print("\n" + "=" * 70)
        print(f"VALIDATING ITEM")
        print("=" * 70)
        print(f"URL: {url}")
        
        # Fetch page
        soup = self.populator.fetch_page(url)
        if not soup:
            print("❌ Failed to fetch page")
            return
        
        # Extract data
        data = self.populator.extract_item_data(soup, url)
        
        # Display
        self.display_extracted_data(data, "item")
        
        # Show what would be saved to database
        print("\n" + "=" * 70)
        print("DATABASE RECORD (what would be saved)")
        print("=" * 70)
        
        from app.models import Item
        
        # Create a temporary item object (don't save)
        temp_item = Item(**data)
        
        print(f"\nTable: items")
        print(f"Columns:")
        print(f"  id: (auto-generated)")
        print(f"  name: {temp_item.name}")
        print(f"  description: {temp_item.description[:100] + '...' if temp_item.description and len(temp_item.description) > 100 else temp_item.description}")
        print(f"  image_url: {temp_item.image_url}")
        print(f"  category: {temp_item.category}")
        print(f"  rarity: {temp_item.rarity}")
        print(f"  type: {temp_item.type}")
        print(f"  stats (JSONB): {json.dumps(temp_item.stats, indent=2) if temp_item.stats else '{}'}")
        print(f"  sources (JSONB): {json.dumps(temp_item.sources, indent=2) if temp_item.sources else '[]'}")
        print(f"  crafting_recipes (JSONB): {json.dumps(temp_item.crafting_recipes, indent=2) if temp_item.crafting_recipes else '[]'}")
        print(f"  recycled_into (JSONB): {json.dumps(temp_item.recycled_into, indent=2) if temp_item.recycled_into else '[]'}")
        print(f"  salvaged_into (JSONB): {json.dumps(temp_item.salvaged_into, indent=2) if temp_item.salvaged_into else '[]'}")
        
        # Check if this item already exists in DB
        print("\n" + "=" * 70)
        print("DATABASE LOOKUP")
        print("=" * 70)
        
        existing = self.populator.db.query(Item).filter(Item.name == data.get("name")).first()
        if existing:
            print(f"\n✓ Item already exists in database (ID: {existing.id})")
            print(f"\nStored data:")
            print(f"  Description: {existing.description[:100] + '...' if existing.description and len(existing.description) > 100 else existing.description}")
            print(f"  Category: {existing.category}")
            print(f"  Type: {existing.type}")
            print(f"  Stats: {json.dumps(existing.stats, indent=2) if existing.stats else '{}'}")
            print(f"  Sources: {len(existing.sources) if existing.sources else 0} items")
            print(f"  Crafting recipes: {len(existing.crafting_recipes) if existing.crafting_recipes else 0} items")
            
            # Test JSONB queries
            print("\n" + "=" * 70)
            print("JSONB QUERY TESTS")
            print("=" * 70)
            
            if existing.stats:
                print("\n✓ Can query stats fields:")
                for key in list(existing.stats.keys())[:3]:
                    print(f"  stats->'{key}' = {existing.stats[key]}")
            
            if existing.sources:
                print("\n✓ Can query sources array:")
                for i, source in enumerate(existing.sources[:3]):
                    print(f"  sources[{i}] = {json.dumps(source)}")
        else:
            print(f"\n⚠️  Item not in database yet")
            print(f"Would be created with extracted data shown above")
        
        # Validation questions
        print("\n" + "=" * 70)
        print("VALIDATION QUESTIONS")
        print("=" * 70)
        
        issues = []
        
        if not data.get("name"):
            issues.append("❌ Missing name")
        else:
            print(f"✓ Name: {data['name']}")
        
        if not data.get("description"):
            issues.append("⚠️  Missing description")
        else:
            print(f"✓ Description: {len(data['description'])} chars")
        
        if not data.get("image_url"):
            issues.append("⚠️  Missing image")
        else:
            print(f"✓ Image URL found")
        
        if data.get("stats") and len(data["stats"]) > 0:
            print(f"✓ Stats: {len(data['stats'])} fields")
        else:
            print(f"⚠️  No stats extracted")
        
        if data.get("sources") and len(data["sources"]) > 0:
            print(f"✓ Sources: {len(data['sources'])} found")
        else:
            print(f"⚠️  No sources")
        
        if data.get("crafting_recipes") and len(data["crafting_recipes"]) > 0:
            print(f"✓ Crafting recipes: {len(data['crafting_recipes'])} found")
        
        if data.get("recycled_into") and len(data["recycled_into"]) > 0:
            print(f"✓ Recycled into: {len(data['recycled_into'])} items")
        
        print()
        
        if issues:
            print("Issues found:")
            for issue in issues:
                print(f"  {issue}")
            print()
        
        return data, issues
    
    def validate_task(self, url: str):
        """Validate task data extraction"""
        print("\n" + "=" * 70)
        print(f"VALIDATING TASK")
        print("=" * 70)
        print(f"URL: {url}")
        
        # Fetch page
        soup = self.populator.fetch_page(url)
        if not soup:
            print("❌ Failed to fetch page")
            return
        
        # Extract data
        data = self.populator.extract_task_data(soup, url)
        
        # Display
        self.display_extracted_data(data, "task")
        
        # Show what would be saved to database
        print("\n" + "=" * 70)
        print("DATABASE RECORD (what would be saved)")
        print("=" * 70)
        
        from app.models import Task
        
        # Create a temporary task object (don't save)
        temp_task = Task(**data)
        
        print(f"\nTable: tasks")
        print(f"Columns:")
        print(f"  id: (auto-generated)")
        print(f"  name: {temp_task.name}")
        print(f"  description: {temp_task.description[:100] + '...' if temp_task.description and len(temp_task.description) > 100 else temp_task.description}")
        print(f"  image_url: {temp_task.image_url}")
        print(f"  type: {temp_task.type}")
        
        if temp_task.type == "quest":
            print(f"\nQuest-specific fields:")
            print(f"  trader: {temp_task.trader}")
            print(f"  location: {temp_task.location}")
            print(f"  dialog (JSONB): {json.dumps(temp_task.dialog, indent=2) if temp_task.dialog else '{}'}")
            print(f"  objectives (JSONB): {json.dumps(temp_task.objectives, indent=2) if temp_task.objectives else '[]'}")
            print(f"  rewards (JSONB): {json.dumps(temp_task.rewards, indent=2) if temp_task.rewards else '[]'}")
        
        if temp_task.type == "workshop":
            print(f"\nWorkshop-specific fields:")
            print(f"  station_type: {temp_task.station_type}")
            print(f"  levels (JSONB): {json.dumps(temp_task.levels, indent=2) if temp_task.levels else '[]'}")
        
        if temp_task.type == "expedition":
            print(f"\nExpedition-specific fields:")
            print(f"  stages (JSONB): {json.dumps(temp_task.stages, indent=2) if temp_task.stages else '[]'}")
        
        # Check if this task already exists in DB
        print("\n" + "=" * 70)
        print("DATABASE LOOKUP")
        print("=" * 70)
        
        existing = self.populator.db.query(Task).filter(Task.name == data.get("name")).first()
        if existing:
            print(f"\n✓ Task already exists in database (ID: {existing.id})")
            print(f"\nStored data:")
            print(f"  Type: {existing.type}")
            print(f"  Trader: {existing.trader}")
            print(f"  Location: {existing.location}")
            
            if existing.rewards:
                print(f"  Rewards: {len(existing.rewards)} items")
                
                # Test reward item lookups
                print("\n" + "=" * 70)
                print("REWARD ITEM LOOKUPS")
                print("=" * 70)
                
                from app.models import Item
                
                for i, reward in enumerate(existing.rewards[:3], 1):
                    reward_name = reward.get('item') or reward.get('item_name')
                    reward_id = reward.get('item_id')
                    
                    print(f"\nReward {i}: {reward_name}")
                    
                    if reward_id:
                        # Try to find by ID
                        reward_item = self.populator.db.query(Item).filter(Item.id == reward_id).first()
                        if reward_item:
                            print(f"  ✓ Found by ID {reward_id}: {reward_item.name}")
                        else:
                            print(f"  ❌ ID {reward_id} not found in database")
                    elif reward_name:
                        # Try to find by name
                        reward_item = self.populator.db.query(Item).filter(Item.name.ilike(f"%{reward_name}%")).first()
                        if reward_item:
                            print(f"  ⚠️  Found by name lookup: {reward_item.name} (ID: {reward_item.id})")
                            print(f"  💡 Should store item_id: {reward_item.id}")
                        else:
                            print(f"  ❌ Item '{reward_name}' not found in database")
                    else:
                        print(f"  ❌ No item name or ID in reward")
            
            # Test JSONB queries
            print("\n" + "=" * 70)
            print("JSONB QUERY TESTS")
            print("=" * 70)
            
            if existing.objectives:
                print("\n✓ Can query objectives array:")
                for i, obj in enumerate(existing.objectives[:2]):
                    print(f"  objectives[{i}] = {json.dumps(obj)}")
            
            if existing.rewards:
                print("\n✓ Can query rewards array:")
                for i, reward in enumerate(existing.rewards[:2]):
                    print(f"  rewards[{i}] = {json.dumps(reward)}")
        else:
            print(f"\n⚠️  Task not in database yet")
            print(f"Would be created with extracted data shown above")
        
        # Validation questions
        print("\n" + "=" * 70)
        print("VALIDATION QUESTIONS")
        print("=" * 70)
        
        issues = []
        
        if not data.get("name"):
            issues.append("❌ Missing name")
        else:
            print(f"✓ Name: {data['name']}")
        
        if not data.get("type"):
            issues.append("❌ Missing type")
        else:
            print(f"✓ Type: {data['type']}")
        
        if data["type"] == "quest":
            if not data.get("trader"):
                issues.append("⚠️  Missing trader")
            if not data.get("objectives"):
                issues.append("⚠️  Missing objectives")
            if not data.get("rewards"):
                issues.append("⚠️  Missing rewards")
            else:
                print(f"✓ Rewards: {len(data['rewards'])} items")
        
        if data["type"] == "workshop":
            if not data.get("levels"):
                issues.append("⚠️  Missing levels")
            else:
                print(f"✓ Levels: {len(data['levels'])} upgrade levels")
        
        print()
        
        if issues:
            print("Issues found:")
            for issue in issues:
                print(f"  {issue}")
            print()
        
        return data, issues
    
    def interactive_validation(self):
        """Interactive validation session"""
        print("\n" + "=" * 70)
        print("INTERACTIVE DATA VALIDATION")
        print("=" * 70)
        print("\nLoading sample URLs...")
        
        urls = self.load_sample_urls()
        
        while True:
            print("\n" + "=" * 70)
            print("MENU")
            print("=" * 70)
            print("1. Validate a sample ITEM")
            print("2. Validate a sample TASK")
            print("3. Test extraction on custom URL")
            print("4. Run batch validation (all samples)")
            print("5. Exit")
            
            choice = input("\nChoice (1-5): ").strip()
            
            if choice == "1":
                print("\nSample Items:")
                for i, url in enumerate(urls["items"], 1):
                    name = url.split("/")[-1].replace("_", " ")
                    print(f"  {i}. {name}")
                
                idx = input("\nSelect item (1-10): ").strip()
                try:
                    url = urls["items"][int(idx) - 1]
                    self.validate_item(url)
                except (ValueError, IndexError):
                    print("Invalid selection")
            
            elif choice == "2":
                print("\nSample Tasks:")
                for i, url in enumerate(urls["tasks"], 1):
                    name = url.split("/")[-1].replace("_", " ").replace("%27", "'")
                    print(f"  {i}. {name}")
                
                idx = input("\nSelect task (1-10): ").strip()
                try:
                    url = urls["tasks"][int(idx) - 1]
                    self.validate_task(url)
                except (ValueError, IndexError):
                    print("Invalid selection")
            
            elif choice == "3":
                url = input("\nEnter URL: ").strip()
                data_type = input("Type (item/task): ").strip().lower()
                
                if data_type == "item":
                    self.validate_item(url)
                elif data_type == "task":
                    self.validate_task(url)
                else:
                    print("Invalid type")
            
            elif choice == "4":
                print("\n" + "=" * 70)
                print("BATCH VALIDATION")
                print("=" * 70)
                
                all_issues = {"items": [], "tasks": []}
                
                print("\nValidating items...")
                for i, url in enumerate(urls["items"], 1):
                    name = url.split("/")[-1].replace("_", " ")
                    print(f"\n[{i}/10] {name}")
                    data, issues = self.validate_item(url)
                    if issues:
                        all_issues["items"].append((name, issues))
                
                print("\n\nValidating tasks...")
                for i, url in enumerate(urls["tasks"], 1):
                    name = url.split("/")[-1].replace("_", " ").replace("%27", "'")
                    print(f"\n[{i}/10] {name}")
                    data, issues = self.validate_task(url)
                    if issues:
                        all_issues["tasks"].append((name, issues))
                
                # Summary
                print("\n" + "=" * 70)
                print("BATCH VALIDATION SUMMARY")
                print("=" * 70)
                
                if all_issues["items"]:
                    print(f"\n❌ Items with issues ({len(all_issues['items'])}):")
                    for name, issues in all_issues["items"]:
                        print(f"  • {name}")
                        for issue in issues:
                            print(f"    {issue}")
                else:
                    print("\n✅ All items validated successfully!")
                
                if all_issues["tasks"]:
                    print(f"\n❌ Tasks with issues ({len(all_issues['tasks'])}):")
                    for name, issues in all_issues["tasks"]:
                        print(f"  • {name}")
                        for issue in issues:
                            print(f"    {issue}")
                else:
                    print("\n✅ All tasks validated successfully!")
            
            elif choice == "5":
                print("\nGoodbye!")
                break
            
            else:
                print("Invalid choice")


if __name__ == "__main__":
    validator = DataValidator()
    validator.interactive_validation()
