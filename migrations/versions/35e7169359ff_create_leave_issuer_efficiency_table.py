"""create leave issuer efficiency table

Revision ID: 35e7169359ff
Revises: 000016
Create Date: 2024-08-30 16:13:24.995229

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '000009'
down_revision: Union[str, None] = '000008'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Create the dbo.leave_issuer_efficiency table
    # This table measures the efficiency of leave issuers in approving or rejecting leave requests.
    op.create_table(
        'leave_issuer_efficiency',
        sa.Column('leave_issuer_id', sa.String(50), primary_key=True),
        sa.Column('total_leaves_processed', sa.Integer, nullable=False),
        sa.Column('average_response_time', sa.Float, nullable=False),
        sa.Column('approval_rate', sa.Float, nullable=False),
        sa.Column('rejection_rate', sa.Float, nullable=False),
        schema='dbo'  # Specify the schema
    )

def downgrade():
    # Drop the dbo.leave_issuer_efficiency table
    op.drop_table('leave_issuer_efficiency', schema='dbo')