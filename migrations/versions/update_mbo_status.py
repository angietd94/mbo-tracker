"""Update MBO status values

Revision ID: update_mbo_status
Revises: remove_user_s3_fields
Create Date: 2025-04-16 14:41:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import text

# revision identifiers, used by Alembic.
revision = 'update_mbo_status'
down_revision = 'remove_user_s3_fields'
branch_labels = None
depends_on = None


def upgrade():
    # Update all MBOs with status "New" to "In progress"
    op.execute(text("UPDATE mbo SET progress_status = 'In progress' WHERE progress_status = 'New'"))
    
    # Update all MBOs with status "MVP" to "Completed" (which is the new name for "Finished")
    op.execute(text("UPDATE mbo SET progress_status = 'Completed' WHERE progress_status = 'MVP'"))
    
    # Update all MBOs with status "Finished" to "Completed"
    op.execute(text("UPDATE mbo SET progress_status = 'Completed' WHERE progress_status = 'Finished'"))
    
    # Update all MBOs with status "In Progress" to "In progress" (to standardize the naming)
    op.execute(text("UPDATE mbo SET progress_status = 'In progress' WHERE progress_status = 'In Progress'"))


def downgrade():
    # This is a data migration, so downgrade is not straightforward
    # We could potentially revert "In progress" to "New" and "Completed" to "Finished"
    # but we can't know which "Completed" were originally "MVP" vs "Finished"
    pass