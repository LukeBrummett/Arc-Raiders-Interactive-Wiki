"""Diagnose data quality issues with 10% random sampling"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.models import Item, Task
from app.database import SessionLocal
from collections import Counter
import random
import json

db = SessionLocal()

def print_section(title):
    """Print a section header"""
    print("\n" + "=" * 70)
    print(title)
    print("=" * 70)

def inspect_item(item):
    """Detailed inspection of an item"""
    print(f"\n📦 {item.name} (ID: {item.id})")
    print("-" * 70)
    
    issues = []
    
    # Basic fields
    if not item.description:
        issues.append("❌ Missing description")
    else:
        print(f"✓ Description: {len(item.description)} chars")
    
    if not item.category:
        issues.append("⚠️  Missing category")
    else:
        print(f"✓ Category: {item.category}")
    
    if not item.type:
        issues.append("⚠️  Missing type")
    else:
        print(f"✓ Type: {item.type}")
    
    if not item.rarity:
        issues.append("⚠️  Missing rarity")
    
    if not item.image_url:
        issues.append("⚠️  Missing image")
    
    # JSONB fields
    if item.stats:
        print(f"✓ Stats: {len(item.stats)} fields - {list(item.stats.keys())}")
    else:
        issues.append("⚠️  No stats")
    
    if item.sources:
        print(f"✓ Sources: {len(item.sources)} items")
    else:
        issues.append("⚠️  No sources")
    
    if item.crafting_recipes:
        print(f"✓ Crafting recipes: {len(item.crafting_recipes)} recipes")
        # Check recipe structure
        for i, recipe in enumerate(item.crafting_recipes[:2], 1):
            if not recipe.get("inputs"):
                issues.append(f"❌ Recipe {i}: No inputs")
            if not recipe.get("workshop"):
                issues.append(f"⚠️  Recipe {i}: No workshop")
            if not recipe.get("output"):
                issues.append(f"⚠️  Recipe {i}: No output")
            else:
                print(f"  Recipe {i}: {len(recipe.get('inputs', []))} inputs → {recipe.get('output', {}).get('item')}")
    
    if item.recycled_into:
        print(f"✓ Recycles into: {len(item.recycled_into)} materials")
    
    # Print issues
    if issues:
        print("\nIssues found:")
        for issue in issues:
            print(f"  {issue}")
    else:
        print("\n✅ No issues found")
    
    return len(issues)

def inspect_task(task):
    """Detailed inspection of a task"""
    print(f"\n📋 {task.name} (ID: {task.id})")
    print("-" * 70)
    
    issues = []
    
    # Basic fields
    if not task.description:
        issues.append("⚠️  Missing description")
    else:
        print(f"✓ Description: {len(task.description)} chars")
    
    if not task.type:
        issues.append("❌ Missing type")
    else:
        print(f"✓ Type: {task.type}")
    
    # Type-specific fields
    if task.type == "quest":
        if not task.trader:
            issues.append("⚠️  Missing trader")
        else:
            print(f"✓ Trader: {task.trader}")
        
        if not task.location:
            issues.append("⚠️  Missing location")
        else:
            print(f"✓ Location: {task.location}")
        
        if not task.objectives:
            issues.append("❌ Missing objectives")
        else:
            print(f"✓ Objectives: {len(task.objectives)} items")
        
        if not task.rewards:
            issues.append("⚠️  Missing rewards")
        else:
            print(f"✓ Rewards: {len(task.rewards)} items")
            # Check reward structure
            for i, reward in enumerate(task.rewards[:3], 1):
                item_name = reward.get('item') or reward.get('item_name')
                item_id = reward.get('item_id')
                
                if not item_name and not item_id:
                    issues.append(f"❌ Reward {i}: No item name or ID")
                elif item_id:
                    print(f"  Reward {i}: item_id={item_id}")
                else:
                    print(f"  Reward {i}: item_name='{item_name}' (should use ID)")
    
    elif task.type == "workshop":
        if not task.levels:
            issues.append("⚠️  Missing upgrade levels")
        else:
            print(f"✓ Levels: {len(task.levels)} upgrade levels")
    
    elif task.type == "expedition":
        if not task.stages:
            issues.append("⚠️  Missing stages")
        else:
            print(f"✓ Stages: {len(task.stages)} stages")
    
    # Print issues
    if issues:
        print("\nIssues found:")
        for issue in issues:
            print(f"  {issue}")
    else:
        print("\n✅ No issues found")
    
    return len(issues)

# Main diagnosis
print_section("DATA QUALITY DIAGNOSIS - 10% RANDOM SAMPLE")

# Get totals
total_items = db.query(Item).count()
total_tasks = db.query(Task).count()

print(f"\nTotal Items: {total_items}")
print(f"Total Tasks: {total_tasks}")

# Calculate sample sizes (10%)
item_sample_size = max(1, int(total_items * 0.1))
task_sample_size = max(1, int(total_tasks * 0.1))

print(f"\nSample Size:")
print(f"  Items: {item_sample_size} ({item_sample_size/total_items*100:.1f}%)")
print(f"  Tasks: {task_sample_size} ({task_sample_size/total_tasks*100:.1f}%)")

# Get random samples
all_items = db.query(Item).all()
all_tasks = db.query(Task).all()

item_sample = random.sample(all_items, min(item_sample_size, len(all_items)))
task_sample = random.sample(all_tasks, min(task_sample_size, len(all_tasks)))

# Inspect items
print_section(f"ITEM INSPECTION ({len(item_sample)} items)")

total_item_issues = 0
for item in item_sample:
    issue_count = inspect_item(item)
    total_item_issues += issue_count

# Inspect tasks
print_section(f"TASK INSPECTION ({len(task_sample)} tasks)")

total_task_issues = 0
for task in task_sample:
    issue_count = inspect_task(task)
    total_task_issues += issue_count

# Summary
print_section("SUMMARY")

print(f"\nItems Inspected: {len(item_sample)}")
print(f"Total Item Issues: {total_item_issues}")
print(f"Average Issues per Item: {total_item_issues/len(item_sample):.2f}")

print(f"\nTasks Inspected: {len(task_sample)}")
print(f"Total Task Issues: {total_task_issues}")
print(f"Average Issues per Task: {total_task_issues/len(task_sample):.2f}")

# Overall stats
print("\n" + "=" * 70)
print("OVERALL STATISTICS")
print("=" * 70)

# Category distribution
categories = [item.category for item in all_items if item.category]
category_counts = Counter(categories)
print("\nItem Categories:")
for cat, count in category_counts.most_common(10):
    print(f"  {cat}: {count}")

# Type distribution
types = [item.type for item in all_items if item.type]
type_counts = Counter(types)
print("\nItem Types:")
for t, count in type_counts.most_common():
    print(f"  {t}: {count}")

# Task types
task_types = [task.type for task in all_tasks if task.type]
task_type_counts = Counter(task_types)
print("\nTask Types:")
for t, count in task_type_counts.most_common():
    print(f"  {t}: {count}")

db.close()

print("\n" + "=" * 70)
print("Diagnosis complete!")
print("=" * 70)
