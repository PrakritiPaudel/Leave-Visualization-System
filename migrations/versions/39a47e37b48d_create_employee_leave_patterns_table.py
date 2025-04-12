"""create employee leave patterns table

Revision ID: 39a47e37b48d
Revises: 000014
Create Date: 2024-08-30 09:09:03.482470

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '000010'
down_revision: Union[str, None] = '000009'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Create the employee_leave_patterns table
    # Tracks patterns in employee leave behavior, like frequent leave takers or employees who haven’t taken any leave.
    op.create_table(
        'employee_leave_patterns',
        sa.Column('emp_id', sa.String(50), primary_key=True),
        sa.Column('total_leave_days', sa.Integer, nullable=False),
        sa.Column('leave_type_most_frequent', sa.String(50), nullable=False),
        sa.Column('total_leaves_taken', sa.Integer, nullable=False),
        sa.Column('has_taken_leave', sa.Boolean, nullable=False),
        sa.Column('average_leave_days', sa.Float, nullable=False),
        schema='dbo'  # Specify the schema if necessary
    )

def downgrade():
    # Drop the employee_leave_patterns table
    op.drop_table('employee_leave_patterns', schema='dbo')
    