"""create department table

Revision ID: 23fdc1d88362
Revises: 99766294c058
Create Date: 2024-08-29 09:27:25.154150

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '000002'
down_revision: Union[str, None] = '000001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:

    # Create department table in dbo schema
    op.create_table(
        'department',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('department_description', sa.String(255), nullable=False),
        schema='dbo'
    )

def downgrade() -> None:
    # Drop department table from dbo schema
    op.drop_table('department', schema='dbo')