"""API routes for search and health check"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.database import get_db
from app.models import Item, Task
from app.schemas import SearchResult, HealthCheck

router = APIRouter(prefix="/api", tags=["general"])


@router.get("/search", response_model=SearchResult)
def search(
    q: str = Query(..., min_length=1, description="Search query"),
    limit: int = Query(10, ge=1, le=50, description="Max results per category"),
    db: Session = Depends(get_db)
):
    """
    Search across all items and tasks
    
    - **q**: Search query (searches in names)
    - **limit**: Maximum results to return per category (items/tasks)
    """
    search_term = f"%{q}%"
    
    # Search items
    items = db.query(Item).filter(
        Item.name.ilike(search_term)
    ).limit(limit).all()
    
    # Search tasks
    tasks = db.query(Task).filter(
        Task.name.ilike(search_term)
    ).limit(limit).all()
    
    return SearchResult(
        items=items,
        tasks=tasks,
        total_results=len(items) + len(tasks)
    )


@router.get("/health", response_model=HealthCheck)
def health_check(db: Session = Depends(get_db)):
    """
    Health check endpoint - verifies database connection and returns stats
    """
    try:
        items_count = db.query(Item).count()
        tasks_count = db.query(Task).count()
        
        return HealthCheck(
            status="healthy",
            database="connected",
            items_count=items_count,
            tasks_count=tasks_count
        )
    except Exception as e:
        return HealthCheck(
            status="unhealthy",
            database=f"error: {str(e)}",
            items_count=0,
            tasks_count=0
        )
