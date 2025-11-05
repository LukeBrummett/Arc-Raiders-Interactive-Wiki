"""Add wiki_url columns to items and tasks

Revision ID: add_wiki_urls
Revises: 
Create Date: 2025-11-04

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_wiki_urls'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Add wiki_url column to items table
    op.add_column('items', sa.Column('wiki_url', sa.Text(), nullable=True))
    
    # Add wiki_url column to tasks table
    op.add_column('tasks', sa.Column('wiki_url', sa.Text(), nullable=True))


def downgrade():
    # Remove wiki_url column from tasks table
    op.drop_column('tasks', 'wiki_url')
    
    # Remove wiki_url column from items table
    op.drop_column('items', 'wiki_url')
