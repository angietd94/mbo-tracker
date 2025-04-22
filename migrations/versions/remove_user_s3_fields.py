"""Remove S3-related fields from User model

Revision ID: remove_user_s3_fields
Revises: remove_s3_fields
Create Date: 2025-04-16 14:30:00.000000

"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'remove_user_s3_fields'
down_revision = 'remove_s3_fields'
branch_labels = None
depends_on = None

def upgrade():
    op.drop_column('users', 'profile_picture_s3_key')
    op.drop_column('users', 'profile_picture_updated_at')

def downgrade():
    op.add_column('users', sa.Column('profile_picture_s3_key', sa.String(length=512), nullable=True))
    op.add_column('users', sa.Column('profile_picture_updated_at', sa.DateTime(), nullable=True))