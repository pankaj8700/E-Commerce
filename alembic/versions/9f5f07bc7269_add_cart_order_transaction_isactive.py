"""add_cart_order_transaction_isactive

Revision ID: 9f5f07bc7269
Revises: e309b5b01345
Create Date: 2026-04-02 23:11:10.884164

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


revision: str = '9f5f07bc7269'
down_revision: Union[str, Sequence[str], None] = 'e309b5b01345'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('order',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('total_amount', sa.Float(), nullable=False),
        sa.Column('status', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('order', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_order_user_id'), ['user_id'], unique=False)

    op.create_table('cartitem',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('quantity', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('product_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['product_id'], ['product.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'product_id', name='uq_cart_user_product')
    )
    with op.batch_alter_table('cartitem', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_cartitem_product_id'), ['product_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_cartitem_user_id'), ['user_id'], unique=False)

    op.create_table('orderitem',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('quantity', sa.Integer(), nullable=False),
        sa.Column('price_at_purchase', sa.Float(), nullable=False),
        sa.Column('order_id', sa.Integer(), nullable=False),
        sa.Column('product_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['order_id'], ['order.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['product_id'], ['product.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('orderitem', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_orderitem_order_id'), ['order_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_orderitem_product_id'), ['product_id'], unique=False)

    op.create_table('transaction',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('amount', sa.Float(), nullable=False),
        sa.Column('type', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('category', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('date', sa.DateTime(), nullable=False),
        sa.Column('notes', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('order_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['order_id'], ['order.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('transaction', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_transaction_category'), ['category'], unique=False)
        batch_op.create_index(batch_op.f('ix_transaction_date'), ['date'], unique=False)
        batch_op.create_index(batch_op.f('ix_transaction_user_id'), ['user_id'], unique=False)

    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('is_active', sa.Boolean(), nullable=False, server_default='1'))


def downgrade() -> None:
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_column('is_active')

    with op.batch_alter_table('transaction', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_transaction_user_id'))
        batch_op.drop_index(batch_op.f('ix_transaction_date'))
        batch_op.drop_index(batch_op.f('ix_transaction_category'))

    op.drop_table('transaction')

    with op.batch_alter_table('orderitem', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_orderitem_product_id'))
        batch_op.drop_index(batch_op.f('ix_orderitem_order_id'))

    op.drop_table('orderitem')

    with op.batch_alter_table('cartitem', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_cartitem_user_id'))
        batch_op.drop_index(batch_op.f('ix_cartitem_product_id'))

    op.drop_table('cartitem')

    with op.batch_alter_table('order', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_order_user_id'))

    op.drop_table('order')
