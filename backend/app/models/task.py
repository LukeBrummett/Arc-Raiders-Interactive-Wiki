"""SQLAlchemy model for Tasks table"""

from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from app.database import Base


class Task(Base):
    """
    Task model - stores quests, expeditions, and workshop upgrades
    
    Uses JSONB for flexible, denormalized storage optimized for fast reads.
    """
    __tablename__ = "tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, nullable=False, index=True)
    type = Column(String(50), index=True)  # 'quest', 'expedition', 'workshop_station', 'workshop_scrappy'
    description = Column(Text)
    image_url = Column(Text)
    wiki_url = Column(Text)  # URL to the wiki page for this task
    images = Column(JSONB)  # [{"url": "...", "alt": "..."}]
    
    # Quest-specific fields
    trader = Column(String(100))
    location = Column(String(100))
    dialog = Column(Text)
    objectives = Column(JSONB)  # ["Objective 1", "Objective 2", ...]
    rewards = Column(JSONB)  # [{"item": "Rattler III", "quantity": 1}, ...]
    
    # Quest chains
    previous_task_id = Column(Integer, ForeignKey('tasks.id'), nullable=True)
    next_tasks = Column(JSONB)  # [{"name": "Next Quest", "id": 123}, ...]
    
    # Workshop/Expedition: Stages or Levels
    stages = Column(JSONB)
    # For expeditions: [{"stage": "Foundation (1/6)", "description": "...", 
    #                    "requirements": [{"item": "Metal Parts", "quantity": 150}]}, ...]
    
    levels = Column(JSONB)
    # For workshops: [{"level": 1, "requirements": [{"item": "Metal Parts", "quantity": 20}]}, ...]
    
    # Workshop-specific
    station_type = Column(String(100), index=True)  # 'Workbench', 'Gunsmith', 'Scrappy', etc.
    max_level = Column(Integer)  # 3 for most stations, 5 for Scrappy
    
    # Timestamps
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<Task(id={self.id}, name='{self.name}', type='{self.type}')>"
    
    def to_dict(self):
        """Convert model to dictionary for API responses"""
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type,
            "description": self.description,
            "image_url": self.image_url,
            "wiki_url": self.wiki_url,
            "images": self.images,
            "trader": self.trader,
            "location": self.location,
            "dialog": self.dialog,
            "objectives": self.objectives,
            "rewards": self.rewards,
            "previous_task_id": self.previous_task_id,
            "next_tasks": self.next_tasks,
            "stages": self.stages,
            "levels": self.levels,
            "station_type": self.station_type,
            "max_level": self.max_level,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
