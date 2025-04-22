"""empty message

Revision ID: 9ae4460c7a62
Revises: 29c946829a7f, add_tax_percentage
Create Date: 2025-04-16 09:57:57.583514

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9ae4460c7a62'
down_revision = ('29c946829a7f', 'add_tax_percentage')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
