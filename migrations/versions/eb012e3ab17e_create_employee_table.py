"""create employee table

Revision ID: eb012e3ab17e
Revises: 
Create Date: 2024-08-29 08:13:48.388367

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '000003'
down_revision: Union[str, None] = '000002'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:

    # Create employee table in dbo schema
    op.create_table(
        'employee',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('emp_id', sa.String(50), unique=True, nullable=False),
        sa.Column('first_name', sa.String(50), nullable=False),
        sa.Column('middle_name', sa.String(50), nullable=True),
        sa.Column('last_name', sa.String(50), nullable=False),
        sa.Column('email', sa.String(100), unique=True, nullable=False),
        sa.Column('designation_id', sa.Integer, sa.ForeignKey('dbo.designation.id', ondelete='SET NULL'), nullable=True),
        sa.Column('team_manager_id', sa.Integer, sa.ForeignKey('dbo.employee.id', ondelete='SET NULL'), nullable=True),
        sa.Column('department_id', sa.Integer, sa.ForeignKey('dbo.department.id', ondelete='SET NULL'), nullable=True),
        sa.Column('is_hr', sa.Boolean, nullable=True),
        sa.Column('is_supervisor', sa.Boolean, nullable=True),
        schema='dbo'  # Specify the schema
    )


def downgrade() -> None:
    # Drop employee table from dbo schema
    op.drop_table('employee', schema='dbo')

