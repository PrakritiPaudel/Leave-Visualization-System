"""create leave summary table

Revision ID: 3bc9c4d7bf08
Revises: 000010
Create Date: 2024-08-29 22:56:23.170529

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '000008'
down_revision: Union[str, None] = '000007'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Create leave_summary table
    op.create_table(
        'leave_summary',
        sa.Column('department_description', sa.String(length=200), nullable=False),
        sa.Column('designation_name', sa.String(length=200), nullable=False),
        sa.Column('leave_type', sa.String(length=200), nullable=False),
        sa.Column('total_leave_days', sa.Integer, nullable=True),
        sa.Column('average_leave_days_per_employee', sa.Float, nullable=True),
        sa.Column('total_employees', sa.Integer, nullable=True),
        sa.Column('fiscal_year', sa.String(length=500), nullable=False),
        sa.PrimaryKeyConstraint('department_description', 'designation_name', 'leave_type', 'fiscal_year'),
        schema='dbo'
    )

def downgrade():
    # Drop leave_summary table
    op.drop_table('leave_summary', schema='dbo')