"""API routes for items"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from typing import List, Optional
import math

from app.database import get_db
from app.models import Item
from app.schemas import ItemResponse, ItemListResponse

router = APIRouter(prefix="/api/items", tags=["items"])


@router.get("", response_model=ItemListResponse)
def get_items(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    search: Optional[str] = Query(None, description="Search by name"),
    category: Optional[str] = Query(None, description="Filter by category"),
    type: Optional[str] = Query(None, description="Filter by type (loot, weapon, equipment)"),
    rarity: Optional[str] = Query(None, description="Filter by rarity"),
    db: Session = Depends(get_db)
):
    """
    Get paginated list of items with optional filters
    
    - **page**: Page number (starts at 1)
    - **page_size**: Number of items per page (max 100)
    - **search**: Search in item names (case-insensitive)
    - **category**: Filter by category
    - **type**: Filter by type (loot, weapon, equipment)
    - **rarity**: Filter by rarity
    """
    # Build query
    query = db.query(Item)
    
    # Apply filters
    if search:
        query = query.filter(Item.name.ilike(f"%{search}%"))
    
    if category:
        query = query.filter(Item.category == category)
    
    if type:
        query = query.filter(Item.type == type)
    
    if rarity:
        query = query.filter(Item.rarity == rarity)
    
    # Get total count
    total = query.count()
    
    # Calculate pagination
    total_pages = math.ceil(total / page_size)
    offset = (page - 1) * page_size
    
    # Get paginated results
    items = query.offset(offset).limit(page_size).all()
    
    return ItemListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )


@router.get("/{item_id}", response_model=ItemResponse)
def get_item(item_id: int, db: Session = Depends(get_db)):
    """
    Get a specific item by ID
    
    - **item_id**: The ID of the item to retrieve
    """
    item = db.query(Item).filter(Item.id == item_id).first()
    
    if not item:
        raise HTTPException(status_code=404, detail=f"Item with ID {item_id} not found")
    
    return item


@router.get("/name/{item_name}", response_model=ItemResponse)
def get_item_by_name(item_name: str, db: Session = Depends(get_db)):
    """
    Get a specific item by name (case-insensitive)
    
    - **item_name**: The name of the item to retrieve
    """
    item = db.query(Item).filter(func.lower(Item.name) == item_name.lower()).first()
    
    if not item:
        raise HTTPException(status_code=404, detail=f"Item '{item_name}' not found")
    
    return item


@router.get("/categories/list", response_model=List[str])
def get_categories(db: Session = Depends(get_db)):
    """Get list of all unique item categories"""
    categories = db.query(Item.category).distinct().filter(Item.category.isnot(None)).all()
    return [cat[0] for cat in categories if cat[0]]


@router.get("/types/list", response_model=List[str])
def get_types(db: Session = Depends(get_db)):
    """Get list of all unique item types"""
    types = db.query(Item.type).distinct().filter(Item.type.isnot(None)).all()
    return [t[0] for t in types if t[0]]


@router.get("/rarities/list", response_model=List[str])
def get_rarities(db: Session = Depends(get_db)):
    """Get list of all unique item rarities"""
    rarities = db.query(Item.rarity).distinct().filter(Item.rarity.isnot(None)).all()
    return [r[0] for r in rarities if r[0]]
