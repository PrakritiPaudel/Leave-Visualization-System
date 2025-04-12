from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '000006'
down_revision: Union[str, None] = '000005'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create leave table in dbo schema
    op.create_table(
        'leave',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('employee_id', sa.String(50), sa.ForeignKey('dbo.employee.emp_id', ondelete='CASCADE'), nullable=False),
        sa.Column('start_date', sa.Date, nullable=False),
        sa.Column('end_date', sa.Date, nullable=False),
        sa.Column('leave_days', sa.Integer, nullable=False),
        sa.Column('reason', sa.Text, nullable=True),
        sa.Column('leave_status', sa.String(50), nullable=True),
        sa.Column('status', sa.String(50), nullable=True),
        sa.Column('response_remarks', sa.Text, nullable=True),
        sa.Column('leave_type_id', sa.Integer, sa.ForeignKey('dbo.leave_type.id', ondelete='SET NULL'), nullable=True),
        sa.Column('fiscal_id', sa.Integer, sa.ForeignKey('dbo.fiscal.id', ondelete='SET NULL'), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP, server_default=sa.func.current_timestamp(), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP, server_default=sa.func.current_timestamp(), onupdate=sa.func.current_timestamp(), nullable=False),
        sa.Column('is_automated', sa.Boolean, nullable=True),
        sa.Column('is_converted', sa.Boolean, nullable=True),
        sa.UniqueConstraint('employee_id', 'start_date', 'end_date', name='unique_leave_constraint'),
        schema='dbo'
    )

def downgrade() -> None:
    # Drop leave table from dbo schema
    op.drop_table('leave', schema='dbo')
