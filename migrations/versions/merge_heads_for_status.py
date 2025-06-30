"""merge multiple heads

Revision ID: merge_heads_for_status
Revises: update_mbo_status, standardize_mbo_status
Create Date: 2025-06-09 11:03:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'merge_heads_for_status'
down_revision = None
branch_labels = None
depends_on = None

# This is a merge migration to handle multiple heads
# It doesn't contain any operations itself

def upgrade():
    pass


def downgrade():
    pass