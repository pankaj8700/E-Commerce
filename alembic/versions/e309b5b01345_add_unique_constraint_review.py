"""add_unique_constraint_review

Revision ID: e309b5b01345
Revises: 4d4938fddb30
Create Date: 2026-04-02 22:12:28.401589

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'e309b5b01345'
down_revision: Union[str, Sequence[str], None] = '4d4938fddb30'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table('review', schema=None) as batch_op:
        batch_op.create_unique_constraint('uq_review_user_product', ['user_id', 'product_id'])


def downgrade() -> None:
    with op.batch_alter_table('review', schema=None) as batch_op:
        batch_op.drop_constraint('uq_review_user_product', type_='unique')
