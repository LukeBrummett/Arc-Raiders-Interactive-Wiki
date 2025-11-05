"""SQLAlchemy model for Items table"""

from sqlalchemy import Column, Integer, String, Text, TIMESTAMP
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from app.database import Base


class Item(Base):
    """
    Item model - stores all loot, weapons, and equipment
    
    Uses JSONB for flexible, denormalized storage optimized for fast reads.
    """
    __tablename__ = "items"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, nullable=False, index=True)
    description = Column(Text)
    image_url = Column(Text)
    wiki_url = Column(Text)  # URL to the wiki page for this item
    category = Column(String(100), index=True)
    rarity = Column(String(50))
    type = Column(String(50), index=True)  # 'loot', 'weapon', 'equipment'
    
    # JSONB columns for flexible, fast storage
    stats = Column(JSONB)
    # Example: {"weight": "0.5KG", "stack_size": 5, "sell_price": 640, 
    #           "can_be_found_in": "ARC", "ammo_type": "Medium", etc.}
    
    sources = Column(JSONB)
    # Example: [{"name": "Sentinel", "url": "/wiki/Sentinel"}, ...]
    
    crafting_recipes = Column(JSONB)
    # Example: [{"workshop": "Workbench 1", 
    #            "inputs": [{"item": "Battery", "quantity": 1}],
    #            "outputs": [{"item": "Energy Clip", "quantity": 5}]}, ...]
    
    recycled_into = Column(JSONB)
    # Example: [{"item": "ARC Powercell", "quantity": 2}]
    
    salvaged_into = Column(JSONB)
    # Example: [{"item": "ARC Powercell", "quantity": 1}]
    
    # Timestamps
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<Item(id={self.id}, name='{self.name}', type='{self.type}')>"
    
    def to_dict(self):
        """Convert model to dictionary for API responses"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "image_url": self.image_url,
            "wiki_url": self.wiki_url,
            "category": self.category,
            "rarity": self.rarity,
            "type": self.type,
            "stats": self.stats,
            "sources": self.sources,
            "crafting_recipes": self.crafting_recipes,
            "recycled_into": self.recycled_into,
            "salvaged_into": self.salvaged_into,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
