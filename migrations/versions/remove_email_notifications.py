"""Remove email_notifications column from User model

Revision ID: remove_email_notifications
Revises: f8ce2e8a9cee
Create Date: 2025-06-10 12:09:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'remove_email_notifications'
down_revision = 'f8ce2e8a9cee'  # Update this to match your latest migration
branch_labels = None
depends_on = None


def upgrade():
    # Remove the email_notifications column from the users table
    op.drop_column('users', 'email_notifications')


def downgrade():
    # Add the email_notifications column back to the users table
    op.add_column('users', sa.Column('email_notifications', sa.Boolean(), nullable=True, server_default='true'))