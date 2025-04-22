"""merge heads

Revision ID: merge_heads
Revises: 01b858191275, add_email_notifications
Create Date: 2025-04-15 20:28:29.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'merge_heads'
down_revision = ('01b858191275', 'add_email_notifications')
branch_labels = None
depends_on = None

def upgrade():
    pass

def downgrade():
    pass