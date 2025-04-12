"""create fiscal table

Revision ID: b774344d4d78
Revises: f443bb587438
Create Date: 2024-08-29 10:54:31.287712

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '000005'
down_revision: Union[str, None] = '000004'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # Create fiscal table in dbo schema
    op.create_table(
        'fiscal',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('fiscal_start_date', sa.Date, nullable=False),
        sa.Column('fiscal_end_date', sa.Date, nullable=False),
        sa.Column('fiscal_is_current', sa.Boolean, nullable=True),
        sa.PrimaryKeyConstraint('id'),
        schema='dbo'
    )

    # Add unique constraint on fiscal_start_date and fiscal_end_date
    op.create_unique_constraint(
        'uq_fiscal_dates',
        'fiscal',
        ['fiscal_start_date', 'fiscal_end_date'],
        schema='dbo'
    )

def downgrade() -> None:
    # Drop unique constraint from fiscal table
    op.drop_constraint('uq_fiscal_dates', 'fiscal', schema='dbo', type_='unique')

    # Drop fiscal table from dbo schema
    op.drop_table('fiscal', schema='dbo')
