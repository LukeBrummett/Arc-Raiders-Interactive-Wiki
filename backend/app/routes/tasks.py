"""API routes for tasks (quests, expeditions, workshops)"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
import math

from app.database import get_db
from app.models import Task
from app.schemas import TaskResponse, TaskListResponse

router = APIRouter(prefix="/api/tasks", tags=["tasks"])


@router.get("", response_model=TaskListResponse)
def get_tasks(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Tasks per page"),
    search: Optional[str] = Query(None, description="Search by name"),
    type: Optional[str] = Query(None, description="Filter by type (quest, expedition, workshop_station)"),
    trader: Optional[str] = Query(None, description="Filter by trader (quests only)"),
    station_type: Optional[str] = Query(None, description="Filter by station type (workshops only)"),
    db: Session = Depends(get_db)
):
    """
    Get paginated list of tasks with optional filters
    
    - **page**: Page number (starts at 1)
    - **page_size**: Number of tasks per page (max 100)
    - **search**: Search in task names (case-insensitive)
    - **type**: Filter by type (quest, expedition, workshop_station, workshop_scrappy)
    - **trader**: Filter by trader name (quests only)
    - **station_type**: Filter by station type (workshops only)
    """
    # Build query
    query = db.query(Task)
    
    # Apply filters
    if search:
        query = query.filter(Task.name.ilike(f"%{search}%"))
    
    if type:
        query = query.filter(Task.type == type)
    
    if trader:
        query = query.filter(Task.trader == trader)
    
    if station_type:
        query = query.filter(Task.station_type == station_type)
    
    # Get total count
    total = query.count()
    
    # Calculate pagination
    total_pages = math.ceil(total / page_size)
    offset = (page - 1) * page_size
    
    # Get paginated results
    tasks = query.offset(offset).limit(page_size).all()
    
    return TaskListResponse(
        tasks=tasks,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )


@router.get("/{task_id}", response_model=TaskResponse)
def get_task(task_id: int, db: Session = Depends(get_db)):
    """
    Get a specific task by ID
    
    - **task_id**: The ID of the task to retrieve
    """
    task = db.query(Task).filter(Task.id == task_id).first()
    
    if not task:
        raise HTTPException(status_code=404, detail=f"Task with ID {task_id} not found")
    
    return task


@router.get("/name/{task_name}", response_model=TaskResponse)
def get_task_by_name(task_name: str, db: Session = Depends(get_db)):
    """
    Get a specific task by name (case-insensitive)
    
    - **task_name**: The name of the task to retrieve
    """
    task = db.query(Task).filter(func.lower(Task.name) == task_name.lower()).first()
    
    if not task:
        raise HTTPException(status_code=404, detail=f"Task '{task_name}' not found")
    
    return task


@router.get("/types/list", response_model=List[str])
def get_task_types(db: Session = Depends(get_db)):
    """Get list of all unique task types"""
    types = db.query(Task.type).distinct().filter(Task.type.isnot(None)).all()
    return [t[0] for t in types if t[0]]


@router.get("/traders/list", response_model=List[str])
def get_traders(db: Session = Depends(get_db)):
    """Get list of all unique traders (quest givers)"""
    traders = db.query(Task.trader).distinct().filter(Task.trader.isnot(None)).all()
    return [t[0] for t in traders if t[0]]


@router.get("/stations/list", response_model=List[str])
def get_station_types(db: Session = Depends(get_db)):
    """Get list of all unique workshop station types"""
    stations = db.query(Task.station_type).distinct().filter(Task.station_type.isnot(None)).all()
    return [s[0] for s in stations if s[0]]
