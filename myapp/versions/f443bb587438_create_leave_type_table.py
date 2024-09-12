"""create leave type table

Revision ID: f443bb587438
Revises: 27b875bfea0b
Create Date: 2024-08-29 10:53:29.286440

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '000004'
down_revision: Union[str, None] = '000003'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None



def upgrade() -> None:
    # Create leave_type table in dbo schema
    op.create_table(
        'leave_type',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('leave_type', sa.String(50), unique=True, nullable=False),
        sa.Column('default_days', sa.Integer, nullable=True),
        sa.Column('transferable_days', sa.Integer, nullable=True),
        sa.Column('is_consecutive', sa.Boolean, nullable=True),
        schema='dbo'
    )

def downgrade() -> None:
    # Drop leave_type table from dbo schema
    op.drop_table('leave_type', schema='dbo')
