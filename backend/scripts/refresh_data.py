"""
Refresh individual items or tasks from the wiki
Usage:
    python scripts/refresh_data.py --item "Syringe"
    python scripts/refresh_data.py --task "A Bad Feeling"
    python scripts/refresh_data.py --item "Canister" --item "Battery"
"""

import sys
import argparse
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import SessionLocal
from app.models import Item, Task
from populate_database import WikiDatabasePopulator


def refresh_item(name: str, scraper: WikiDatabasePopulator, db):
    """Refresh a single item from the wiki"""
    print(f"\n{'='*70}")
    print(f"Refreshing Item: {name}")
    print(f"{'='*70}")
    
    # Find the item in database
    item = db.query(Item).filter_by(name=name).first()
    if not item:
        print(f"❌ Item '{name}' not found in database")
        return False
    
    print(f"✓ Found in database (ID: {item.id})")
    
    # Get the wiki URL
    wiki_url = item.wiki_url
    if not wiki_url:
        print(f"❌ No wiki URL stored for this item")
        return False
    
    print(f"  Fetching: {wiki_url}")
    
    # Fetch and parse
    soup = scraper.fetch_page(wiki_url)
    if not soup:
        print(f"❌ Failed to fetch page")
        return False
    
    # Extract data
    data = scraper.extract_item_data(soup, wiki_url)
    
    # Show what changed
    print(f"\n📊 Updates:")
    changes = []
    
    if item.description != data.get("description"):
        changes.append(f"  Description: {len(item.description or '')} → {len(data.get('description', ''))} chars")
        item.description = data.get("description")
    
    if item.rarity != data.get("rarity"):
        changes.append(f"  Rarity: '{item.rarity}' → '{data.get('rarity')}'")
        item.rarity = data.get("rarity")
    
    if item.category != data.get("category"):
        changes.append(f"  Category: '{item.category}' → '{data.get('category')}'")
        item.category = data.get("category")
    
    # Compare JSON fields
    old_stats = item.stats or {}
    new_stats = data.get("stats", {})
    if old_stats != new_stats:
        changes.append(f"  Stats: {len(old_stats)} → {len(new_stats)} fields")
        item.stats = new_stats
    
    old_recipes = item.crafting_recipes or []
    new_recipes = data.get("crafting_recipes", [])
    if old_recipes != new_recipes:
        changes.append(f"  Crafting recipes: {len(old_recipes)} → {len(new_recipes)} recipes")
        # Show recipe input counts
        for i, recipe in enumerate(new_recipes, 1):
            input_count = len(recipe.get("inputs", []))
            changes.append(f"    Recipe {i}: {input_count} input(s) → {recipe.get('output', {}).get('item', 'Unknown')}")
        item.crafting_recipes = new_recipes
    
    old_sources = item.sources or []
    new_sources = data.get("sources", [])
    if old_sources != new_sources:
        changes.append(f"  Sources: {len(old_sources)} → {len(new_sources)} sources")
        item.sources = new_sources
    
    if changes:
        for change in changes:
            print(change)
        db.commit()
        print(f"\n✅ Item '{name}' updated successfully")
        return True
    else:
        print(f"  No changes detected")
        return True


def refresh_task(name: str, scraper: WikiDatabasePopulator, db):
    """Refresh a single task from the wiki"""
    print(f"\n{'='*70}")
    print(f"Refreshing Task: {name}")
    print(f"{'='*70}")
    
    # Find the task in database
    task = db.query(Task).filter_by(name=name).first()
    if not task:
        print(f"❌ Task '{name}' not found in database")
        return False
    
    print(f"✓ Found in database (ID: {task.id})")
    
    # Get the wiki URL
    wiki_url = task.wiki_url
    if not wiki_url:
        print(f"❌ No wiki URL stored for this task")
        return False
    
    print(f"  Fetching: {wiki_url}")
    
    # Fetch and parse
    soup = scraper.fetch_page(wiki_url)
    if not soup:
        print(f"❌ Failed to fetch page")
        return False
    
    # Extract data
    data = scraper.extract_task_data(soup, wiki_url)
    
    # Show what changed
    print(f"\n📊 Updates:")
    changes = []
    
    if task.description != data.get("description"):
        changes.append(f"  Description: {len(task.description or '')} → {len(data.get('description', ''))} chars")
        task.description = data.get("description")
    
    if task.trader != data.get("trader"):
        changes.append(f"  Trader: '{task.trader}' → '{data.get('trader')}'")
        task.trader = data.get("trader")
    
    if task.location != data.get("location"):
        changes.append(f"  Location: '{task.location}' → '{data.get('location')}'")
        task.location = data.get("location")
    
    # Compare JSON fields
    old_objectives = task.objectives or []
    new_objectives = data.get("objectives", [])
    if old_objectives != new_objectives:
        changes.append(f"  Objectives: {len(old_objectives)} → {len(new_objectives)} objectives")
        task.objectives = new_objectives
    
    old_rewards = task.rewards or []
    new_rewards = data.get("rewards", [])
    if old_rewards != new_rewards:
        changes.append(f"  Rewards: {len(old_rewards)} → {len(new_rewards)} rewards")
        task.rewards = new_rewards
    
    if changes:
        for change in changes:
            print(change)
        db.commit()
        print(f"\n✅ Task '{name}' updated successfully")
        return True
    else:
        print(f"  No changes detected")
        return True


def main():
    parser = argparse.ArgumentParser(
        description="Refresh items or tasks from the wiki",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/refresh_data.py --item "Syringe"
  python scripts/refresh_data.py --task "A Bad Feeling"
  python scripts/refresh_data.py --item "Canister" --item "Battery"
  python scripts/refresh_data.py --all-items
        """
    )
    parser.add_argument('--item', action='append', help='Item name to refresh (can be used multiple times)')
    parser.add_argument('--task', action='append', help='Task name to refresh (can be used multiple times)')
    parser.add_argument('--all-items', action='store_true', help='Refresh all items in database')
    parser.add_argument('--all-tasks', action='store_true', help='Refresh all tasks in database')
    
    args = parser.parse_args()
    
    if not any([args.item, args.task, args.all_items, args.all_tasks]):
        parser.print_help()
        return
    
    # Initialize scraper
    scraper = WikiDatabasePopulator()
    db = SessionLocal()
    
    try:
        success_count = 0
        total_count = 0
        
        # Refresh items
        if args.item:
            for item_name in args.item:
                total_count += 1
                if refresh_item(item_name, scraper, db):
                    success_count += 1
        
        # Refresh tasks
        if args.task:
            for task_name in args.task:
                total_count += 1
                if refresh_task(task_name, scraper, db):
                    success_count += 1
        
        # Refresh all items
        if args.all_items:
            items = db.query(Item).all()
            print(f"\n{'='*70}")
            print(f"Refreshing all {len(items)} items")
            print(f"{'='*70}")
            for item in items:
                total_count += 1
                if refresh_item(item.name, scraper, db):
                    success_count += 1
        
        # Refresh all tasks
        if args.all_tasks:
            tasks = db.query(Task).all()
            print(f"\n{'='*70}")
            print(f"Refreshing all {len(tasks)} tasks")
            print(f"{'='*70}")
            for task in tasks:
                total_count += 1
                if refresh_task(task.name, scraper, db):
                    success_count += 1
        
        # Summary
        print(f"\n{'='*70}")
        print(f"SUMMARY")
        print(f"{'='*70}")
        print(f"Total: {total_count}")
        print(f"Success: {success_count}")
        print(f"Failed: {total_count - success_count}")
        
    finally:
        db.close()


if __name__ == "__main__":
    main()
