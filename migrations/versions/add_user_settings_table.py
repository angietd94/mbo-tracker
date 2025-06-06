"""Add UserSettings table

Revision ID: add_user_settings_table
Revises: 
Create Date: 2025-04-15 14:44:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_user_settings_table'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Create the user_settings table
    op.create_table('user_settings',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('key', sa.String(length=64), nullable=False),
        sa.Column('value', sa.String(length=256), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'key', name='_user_key_uc')
    )


def downgrade():
    # Drop the user_settings table
    op.drop_table('user_settings')