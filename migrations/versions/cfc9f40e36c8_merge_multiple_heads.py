"""Merge multiple heads

Revision ID: cfc9f40e36c8
Revises: 9ae4460c7a62, remove_s3_fields
Create Date: 2025-04-16 14:17:40.966784

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'cfc9f40e36c8'
down_revision = ('9ae4460c7a62', 'remove_s3_fields')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
