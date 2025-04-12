"""create departmental leave impact table

Revision ID: 24900fb91b29
Revises: f4cc0277be10
Create Date: 2024-08-30 17:06:33.220581

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '000011'
down_revision: Union[str, None] = '000010'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create dbo.departmental_leave_impact table
    # Analyzes the impact of leaves on departments, considering the number of employees on leave and how it might affect overall productivity.
    op.create_table(
        'departmental_leave_impact',
        sa.Column('department_description', sa.String(length=500), primary_key=True),
        sa.Column('total_employees_on_leave', sa.Integer, nullable=False),
        sa.Column('average_leave_duration', sa.Float, nullable=False),
        sa.Column('total_leave_days', sa.Integer, nullable=False),
        sa.Column('impact_score', sa.Float, nullable=False),
        schema='dbo'
    )

def downgrade() -> None:
    # Drop dbo.departmental_leave_impact table
    op.drop_table('departmental_leave_impact', schema='dbo')