"""Add profile_picture_updated_at column to users table

Revision ID: add_profile_picture_updated_at
Revises: add_profile_picture_s3_key
Create Date: 2025-04-16 08:36:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_profile_picture_updated_at'
down_revision = 'add_profile_picture_s3_key'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('users', sa.Column('profile_picture_updated_at', sa.DateTime(), nullable=True))


def downgrade():
    op.drop_column('users', 'profile_picture_updated_at')