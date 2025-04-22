"""merge multiple heads

Revision ID: 29c946829a7f
Revises: add_profile_picture_updated_at, f8ce2e8a9cee
Create Date: 2025-04-16 08:39:33.227555

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '29c946829a7f'
down_revision = ('add_profile_picture_updated_at', 'f8ce2e8a9cee')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
