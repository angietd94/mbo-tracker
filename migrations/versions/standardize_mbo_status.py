"""Standardize MBO status labels

Revision ID: standardize_mbo_status
Revises: update_mbo_status
Create Date: 2025-06-09 11:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import text

# revision identifiers, used by Alembic.
revision = 'standardize_mbo_status'
down_revision = None  # We'll use the merge migration to handle dependencies
branch_labels = None
depends_on = None


def upgrade():
    # Update any 'Completed' status to 'Finished'
    op.execute(text("UPDATE mbo SET progress_status = 'Finished' WHERE progress_status = 'Completed'"))


def downgrade():
    # Revert 'Finished' back to 'Completed' (though this is not recommended)
    op.execute(text("UPDATE mbo SET progress_status = 'Completed' WHERE progress_status = 'Finished'"))