"""merge multiple heads

Revision ID: 8959d0511f12
Revises: 5130ea57b3c2, add_user_settings_table
Create Date: 2025-04-15 14:51:59.787713

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8959d0511f12'
down_revision = ('5130ea57b3c2', 'add_user_settings_table')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
