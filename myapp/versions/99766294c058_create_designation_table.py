"""create designation table

Revision ID: 99766294c058
Revises: eb012e3ab17e
Create Date: 2024-08-29 09:24:28.893113

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '000001'
down_revision: Union[str, None] = '000000'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:

    # Create designation table in dbo schema
    op.create_table(
        'designation',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('designation_name', sa.String(100), unique=True, nullable=False),
        schema='dbo'
    )

def downgrade() -> None:
    # Drop designation table from dbo schema
    op.drop_table('designation', schema='dbo')

