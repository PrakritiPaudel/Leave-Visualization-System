"""Create schema dbo

Revision ID: 7ea2f2cbedab
Revises: 000008
Create Date: 2024-08-29 16:46:01.200059

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '000000'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
     # Create dbo schema
    op.execute('CREATE SCHEMA IF NOT EXISTS dbo')

def downgrade() -> None:
    # Drop dbo schema
    op.execute('DROP SCHEMA IF EXISTS dbo CASCADE')
