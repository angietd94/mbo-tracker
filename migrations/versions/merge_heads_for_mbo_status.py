"""Merge heads for MBO status update

Revision ID: merge_heads_for_mbo_status
Revises: 91a44754c204, update_mbo_status
Create Date: 2025-04-16 14:42:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'merge_heads_for_mbo_status'
down_revision = ('91a44754c204', 'update_mbo_status')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass