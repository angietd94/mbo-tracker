"""Add user columns

Revision ID: add_user_columns
Revises: merge_heads
Create Date: 2025-04-15 20:46:43.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'add_user_columns'
down_revision = 'merge_heads'
branch_labels = None
depends_on = None

def upgrade():
    # Add quarter_compensation column
    op.add_column('users', sa.Column('quarter_compensation', sa.Float(), nullable=True))

def downgrade():
    # Remove the column
    op.drop_column('users', 'quarter_compensation')