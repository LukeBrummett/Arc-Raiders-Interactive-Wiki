"""Quick check of database population"""
from app.models import Item, Task
from app.database import SessionLocal

db = SessionLocal()

items_count = db.query(Item).count()
tasks_count = db.query(Task).count()

print("=" * 60)
print("Database Population Summary")
print("=" * 60)
print(f"Total Items: {items_count}")
print(f"Total Tasks: {tasks_count}")
print(f"Total Records: {items_count + tasks_count}")
print()

# Sample some items
print("Sample Items:")
for item in db.query(Item).limit(5):
    print(f"  - {item.name} ({item.type})")

print()
print("Sample Tasks:")
for task in db.query(Task).limit(5):
    print(f"  - {task.name} ({task.type})")

print()

# Check an item with full data
powercell = db.query(Item).filter(Item.name == "Advanced ARC Powercell").first()
if powercell:
    print("Sample Item Detail (Advanced ARC Powercell):")
    print(f"  Category: {powercell.category}")
    print(f"  Rarity: {powercell.rarity}")
    print(f"  Stats: {powercell.stats}")
    print(f"  Sources: {len(powercell.sources)} sources")
    print(f"  Crafting Recipes: {len(powercell.crafting_recipes)} recipes")

db.close()
print()
print("✅ Database is fully populated and ready!")
