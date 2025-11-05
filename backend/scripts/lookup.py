"""Quick lookup tool for items and tasks"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.models import Item, Task
from app.database import SessionLocal
import json

def lookup_item(name):
    """Find an item by name (partial match)"""
    db = SessionLocal()
    items = db.query(Item).filter(Item.name.ilike(f"%{name}%")).all()
    
    if not items:
        print(f"No items found matching '{name}'")
        return
    
    if len(items) > 1:
        print(f"Found {len(items)} items:")
        for i, item in enumerate(items, 1):
            print(f"  {i}. {item.name} (ID: {item.id})")
        print()
    
    # Show details of first match
    item = items[0]
    print("=" * 70)
    print(f"ITEM: {item.name}")
    print("=" * 70)
    print(f"ID: {item.id}")
    print(f"Type: {item.type}")
    print(f"Category: {item.category}")
    print(f"Rarity: {item.rarity}")
    print(f"Description: {item.description}")
    print(f"Image URL: {item.image_url}")
    print()
    print("Stats:")
    print(json.dumps(item.stats, indent=2))
    print()
    print(f"Sources ({len(item.sources) if item.sources else 0}):")
    if item.sources:
        print(json.dumps(item.sources, indent=2))
    print()
    print(f"Crafting Recipes ({len(item.crafting_recipes) if item.crafting_recipes else 0}):")
    if item.crafting_recipes:
        print(json.dumps(item.crafting_recipes, indent=2))
    print()
    print(f"Recycled Into ({len(item.recycled_into) if item.recycled_into else 0}):")
    if item.recycled_into:
        print(json.dumps(item.recycled_into, indent=2))
    print()
    print(f"Salvaged Into ({len(item.salvaged_into) if item.salvaged_into else 0}):")
    if item.salvaged_into:
        print(json.dumps(item.salvaged_into, indent=2))
    
    db.close()

def lookup_task(name):
    """Find a task by name (partial match)"""
    db = SessionLocal()
    tasks = db.query(Task).filter(Task.name.ilike(f"%{name}%")).all()
    
    if not tasks:
        print(f"No tasks found matching '{name}'")
        return
    
    if len(tasks) > 1:
        print(f"Found {len(tasks)} tasks:")
        for i, task in enumerate(tasks, 1):
            print(f"  {i}. {task.name} (ID: {task.id}, Type: {task.type})")
        print()
    
    # Show details of first match
    task = tasks[0]
    print("=" * 70)
    print(f"TASK: {task.name}")
    print("=" * 70)
    print(f"ID: {task.id}")
    print(f"Type: {task.type}")
    print(f"Description: {task.description}")
    print(f"Image URL: {task.image_url}")
    
    if task.type == "quest":
        print(f"\nTrader: {task.trader}")
        print(f"Location: {task.location}")
        print(f"\nDialog:\n{task.dialog}")
        print(f"\nObjectives ({len(task.objectives) if task.objectives else 0}):")
        if task.objectives:
            for i, obj in enumerate(task.objectives, 1):
                print(f"  {i}. {obj}")
        print(f"\nRewards ({len(task.rewards) if task.rewards else 0}):")
        if task.rewards:
            print(json.dumps(task.rewards, indent=2))
        print(f"\nPrevious Task ID: {task.previous_task_id}")
        print(f"Next Tasks: {task.next_tasks}")
    
    if task.type == "expedition":
        print(f"\nStages ({len(task.stages) if task.stages else 0}):")
        if task.stages:
            print(json.dumps(task.stages, indent=2))
    
    if task.type in ["workshop_station", "workshop_scrappy"]:
        print(f"\nStation Type: {task.station_type}")
        print(f"Max Level: {task.max_level}")
        print(f"\nLevels ({len(task.levels) if task.levels else 0}):")
        if task.levels:
            print(json.dumps(task.levels, indent=2))
    
    if task.images:
        print(f"\nImages ({len(task.images)}):")
        print(json.dumps(task.images, indent=2))
    
    db.close()

def lookup_by_id(type, id):
    """Lookup by ID"""
    db = SessionLocal()
    
    if type == "item":
        obj = db.query(Item).filter(Item.id == id).first()
        if obj:
            lookup_item(obj.name)
        else:
            print(f"No item found with ID {id}")
    elif type == "task":
        obj = db.query(Task).filter(Task.id == id).first()
        if obj:
            lookup_task(obj.name)
        else:
            print(f"No task found with ID {id}")
    
    db.close()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python lookup.py item <name>         - Find item by name")
        print("  python lookup.py task <name>         - Find task by name")
        print("  python lookup.py item-id <id>        - Find item by ID")
        print("  python lookup.py task-id <id>        - Find task by ID")
        print()
        print("Examples:")
        print("  python lookup.py item powercell")
        print("  python lookup.py task 'picking up'")
        print("  python lookup.py item-id 1")
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    if command == "item" and len(sys.argv) >= 3:
        lookup_item(" ".join(sys.argv[2:]))
    elif command == "task" and len(sys.argv) >= 3:
        lookup_task(" ".join(sys.argv[2:]))
    elif command == "item-id" and len(sys.argv) >= 3:
        lookup_by_id("item", int(sys.argv[2]))
    elif command == "task-id" and len(sys.argv) >= 3:
        lookup_by_id("task", int(sys.argv[2]))
    else:
        print("Invalid command. See usage above.")
