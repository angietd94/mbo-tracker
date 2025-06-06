"""Remove S3 attachment fields

Revision ID: remove_s3_fields
Revises: add_email_notifications
Create Date: 2025-04-16 14:05:00.000000

"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'remove_s3_fields'
down_revision = 'add_email_notifications'
branch_labels = None
depends_on = None

def upgrade():
    op.drop_column('mbo', 'attachment_filename')
    op.drop_column('mbo', 'attachment_s3_key')
    op.drop_column('mbo', 'attachment_content_type')

def downgrade():
    op.add_column('mbo', sa.Column('attachment_filename', sa.String(length=256), nullable=True))
    op.add_column('mbo', sa.Column('attachment_s3_key', sa.String(length=512), nullable=True))
    op.add_column('mbo', sa.Column('attachment_content_type', sa.String(length=100), nullable=True))