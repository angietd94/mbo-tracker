"""Add profile_picture_s3_key column to users table

Revision ID: add_profile_picture_s3_key
Revises: 8959d0511f12
Create Date: 2025-04-16 08:22:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_profile_picture_s3_key'
down_revision = '8959d0511f12'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('users', sa.Column('profile_picture_s3_key', sa.String(512), nullable=True))


def downgrade():
    op.drop_column('users', 'profile_picture_s3_key')