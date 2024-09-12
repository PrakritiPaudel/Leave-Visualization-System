"""create allocation table

Revision ID: dc8a7d29cf5a
Revises: 91d0f90d6eda
Create Date: 2024-08-29 10:57:10.368925

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '000007'
down_revision: Union[str, None] = '000006'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# This table connects employees with their allocations and references the employee table.
def upgrade() -> None:
    # Create allocation table in dbo schema
    op.create_table(
        'allocation',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('emp_id', sa.String(50), sa.ForeignKey('dbo.employee.emp_id', ondelete='CASCADE'), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('type', sa.String(50), nullable=False),
        schema='dbo'
    )

def downgrade() -> None:
    # Drop allocation table from dbo schema
    op.drop_table('allocation', schema='dbo')
