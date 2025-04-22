"""Remove tax_percentage column from User model

Revision ID: remove_tax_percentage
Revises: merge_heads_for_mbo_status
Create Date: 2025-04-16 14:46:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'remove_tax_percentage'
down_revision = 'merge_heads_for_mbo_status'
branch_labels = None
depends_on = None


def upgrade():
    # Remove tax_percentage column from users table
    op.drop_column('users', 'tax_percentage')


def downgrade():
    # Add tax_percentage column back to users table
    op.add_column('users', sa.Column('tax_percentage', sa.Float(), nullable=True, server_default='30.0'))