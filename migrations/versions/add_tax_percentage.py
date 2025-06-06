"""Add tax_percentage to User model

Revision ID: add_tax_percentage
Revises: add_profile_picture_updated_at
Create Date: 2025-04-16 09:55:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_tax_percentage'
down_revision = 'add_profile_picture_updated_at'
branch_labels = None
depends_on = None


def upgrade():
    # Add tax_percentage column to users table with default value of 30.0
    op.add_column('users', sa.Column('tax_percentage', sa.Float(), nullable=True, server_default='30.0'))


def downgrade():
    # Remove tax_percentage column from users table
    op.drop_column('users', 'tax_percentage')