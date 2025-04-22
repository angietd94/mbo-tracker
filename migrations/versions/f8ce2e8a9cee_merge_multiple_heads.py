"""merge multiple heads

Revision ID: f8ce2e8a9cee
Revises: add_profile_picture_s3_key, add_user_columns
Create Date: 2025-04-16 08:22:58.864393

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f8ce2e8a9cee'
down_revision = ('add_profile_picture_s3_key', 'add_user_columns')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
