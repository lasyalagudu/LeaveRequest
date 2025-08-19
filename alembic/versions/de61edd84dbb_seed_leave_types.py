"""Seed leave types

Revision ID: de61edd84dbb
Revises: 
Create Date: 2025-08-19 22:07:10.145622

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'de61edd84dbb'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

leave_types_table = sa.table(
    'leave_types',
    sa.column('name', sa.String),
    sa.column('description', sa.String),
    sa.column('default_balance', sa.Integer),
    sa.column('carry_forward', sa.Boolean),
)
def upgrade():
    op.bulk_insert(
        leave_types_table,
        [
            {'name': 'Annual Leave', 'description': 'Paid annual leave', 'default_balance': 20, 'carry_forward': True},
            {'name': 'Sick Leave', 'description': 'Paid sick leave', 'default_balance': 10, 'carry_forward': False},
            {'name': 'Casual Leave', 'description': 'Unpaid casual leave', 'default_balance': 5, 'carry_forward': False},
        ]
    )

def downgrade():
    op.execute("DELETE FROM leave_types WHERE name IN ('Annual Leave', 'Sick Leave', 'Casual Leave')")