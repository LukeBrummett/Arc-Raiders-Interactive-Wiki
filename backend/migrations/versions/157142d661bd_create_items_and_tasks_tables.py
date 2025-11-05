"""create_items_and_tasks_tables

Revision ID: 157142d661bd
Revises: 
Create Date: 2025-11-04 00:57:40.713186

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB


# revision identifiers, used by Alembic.
revision: str = '157142d661bd'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create items table
    op.create_table(
        'items',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('image_url', sa.Text(), nullable=True),
        sa.Column('category', sa.String(length=100), nullable=True),
        sa.Column('rarity', sa.String(length=50), nullable=True),
        sa.Column('type', sa.String(length=50), nullable=True),
        sa.Column('stats', JSONB(), nullable=True),
        sa.Column('sources', JSONB(), nullable=True),
        sa.Column('crafting_recipes', JSONB(), nullable=True),
        sa.Column('recycled_into', JSONB(), nullable=True),
        sa.Column('salvaged_into', JSONB(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_items_id'), 'items', ['id'], unique=False)
    op.create_index(op.f('ix_items_name'), 'items', ['name'], unique=True)
    op.create_index(op.f('ix_items_category'), 'items', ['category'], unique=False)
    op.create_index(op.f('ix_items_type'), 'items', ['type'], unique=False)
    
    # Create tasks table
    op.create_table(
        'tasks',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('type', sa.String(length=50), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('image_url', sa.Text(), nullable=True),
        sa.Column('images', JSONB(), nullable=True),
        sa.Column('trader', sa.String(length=100), nullable=True),
        sa.Column('location', sa.String(length=100), nullable=True),
        sa.Column('dialog', sa.Text(), nullable=True),
        sa.Column('objectives', JSONB(), nullable=True),
        sa.Column('rewards', JSONB(), nullable=True),
        sa.Column('previous_task_id', sa.Integer(), nullable=True),
        sa.Column('next_tasks', JSONB(), nullable=True),
        sa.Column('stages', JSONB(), nullable=True),
        sa.Column('levels', JSONB(), nullable=True),
        sa.Column('station_type', sa.String(length=100), nullable=True),
        sa.Column('max_level', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['previous_task_id'], ['tasks.id'], )
    )
    op.create_index(op.f('ix_tasks_id'), 'tasks', ['id'], unique=False)
    op.create_index(op.f('ix_tasks_name'), 'tasks', ['name'], unique=True)
    op.create_index(op.f('ix_tasks_type'), 'tasks', ['type'], unique=False)
    op.create_index(op.f('ix_tasks_station_type'), 'tasks', ['station_type'], unique=False)


def downgrade() -> None:
    # Drop tasks table
    op.drop_index(op.f('ix_tasks_station_type'), table_name='tasks')
    op.drop_index(op.f('ix_tasks_type'), table_name='tasks')
    op.drop_index(op.f('ix_tasks_name'), table_name='tasks')
    op.drop_index(op.f('ix_tasks_id'), table_name='tasks')
    op.drop_table('tasks')
    
    # Drop items table
    op.drop_index(op.f('ix_items_type'), table_name='items')
    op.drop_index(op.f('ix_items_category'), table_name='items')
    op.drop_index(op.f('ix_items_name'), table_name='items')
    op.drop_index(op.f('ix_items_id'), table_name='items')
    op.drop_table('items')

