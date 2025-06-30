"""empty message

Revision ID: 74263d5884c6
Revises: merge_heads_for_status, remove_email_notifications, remove_tax_percentage, standardize_mbo_status
Create Date: 2025-06-10 12:14:58.808910

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '74263d5884c6'
down_revision = ('merge_heads_for_status', 'remove_email_notifications', 'remove_tax_percentage', 'standardize_mbo_status')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
