"""Add email notifications column

Revision ID: add_email_notifications
Revises: None
Create Date: 2025-04-15 20:25:10.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'add_email_notifications'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # Add email_notifications column with default True
    op.add_column('users', sa.Column('email_notifications', sa.Boolean(), nullable=False, server_default='true'))
    
    # Add attachment columns to MBO table
    op.add_column('mbo', sa.Column('attachment_filename', sa.String(length=256), nullable=True))
    op.add_column('mbo', sa.Column('attachment_s3_key', sa.String(length=512), nullable=True))
    op.add_column('mbo', sa.Column('attachment_content_type', sa.String(length=100), nullable=True))

def downgrade():
    # Remove the columns
    op.drop_column('users', 'email_notifications')
    op.drop_column('mbo', 'attachment_filename')
    op.drop_column('mbo', 'attachment_s3_key')
    op.drop_column('mbo', 'attachment_content_type')