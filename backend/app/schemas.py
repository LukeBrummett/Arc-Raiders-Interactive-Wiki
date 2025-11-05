"""Pydantic schemas for API request/response validation"""

from pydantic import BaseModel, ConfigDict
from typing import Optional, List, Any, Dict
from datetime import datetime


class ItemBase(BaseModel):
    """Base item schema"""
    name: str
    description: Optional[str] = None
    image_url: Optional[str] = None
    category: Optional[str] = None
    rarity: Optional[str] = None
    type: Optional[str] = None


class ItemCreate(ItemBase):
    """Schema for creating items"""
    stats: Optional[Dict[str, Any]] = None
    sources: Optional[List[Dict[str, Any]]] = None
    crafting_recipes: Optional[List[Dict[str, Any]]] = None
    recycled_into: Optional[List[Dict[str, Any]]] = None
    salvaged_into: Optional[List[Dict[str, Any]]] = None


class ItemResponse(ItemBase):
    """Schema for item responses"""
    id: int
    stats: Optional[Dict[str, Any]] = None
    sources: Optional[List[Dict[str, Any]]] = None
    crafting_recipes: Optional[List[Dict[str, Any]]] = None
    recycled_into: Optional[List[Dict[str, Any]]] = None
    salvaged_into: Optional[List[Dict[str, Any]]] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)


class ItemListResponse(BaseModel):
    """Schema for paginated item list"""
    items: List[ItemResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class TaskBase(BaseModel):
    """Base task schema"""
    name: str
    type: Optional[str] = None
    description: Optional[str] = None
    image_url: Optional[str] = None


class TaskCreate(TaskBase):
    """Schema for creating tasks"""
    images: Optional[List[Dict[str, str]]] = None
    trader: Optional[str] = None
    location: Optional[str] = None
    dialog: Optional[str] = None
    objectives: Optional[List[str]] = None
    rewards: Optional[List[Dict[str, Any]]] = None
    previous_task_id: Optional[int] = None
    next_tasks: Optional[List[Dict[str, Any]]] = None
    stages: Optional[List[Dict[str, Any]]] = None
    levels: Optional[List[Dict[str, Any]]] = None
    station_type: Optional[str] = None
    max_level: Optional[int] = None


class TaskResponse(TaskBase):
    """Schema for task responses"""
    id: int
    images: Optional[List[Dict[str, str]]] = None
    trader: Optional[str] = None
    location: Optional[str] = None
    dialog: Optional[str] = None
    objectives: Optional[List[str]] = None
    rewards: Optional[List[Dict[str, Any]]] = None
    previous_task_id: Optional[int] = None
    next_tasks: Optional[List[Dict[str, Any]]] = None
    stages: Optional[List[Dict[str, Any]]] = None
    levels: Optional[List[Dict[str, Any]]] = None
    station_type: Optional[str] = None
    max_level: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)


class TaskListResponse(BaseModel):
    """Schema for paginated task list"""
    tasks: List[TaskResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class SearchResult(BaseModel):
    """Schema for search results"""
    items: List[ItemResponse]
    tasks: List[TaskResponse]
    total_results: int


class HealthCheck(BaseModel):
    """Health check response"""
    status: str
    database: str
    items_count: int
    tasks_count: int
