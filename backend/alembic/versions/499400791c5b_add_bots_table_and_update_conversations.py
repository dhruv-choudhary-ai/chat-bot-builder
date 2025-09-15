"""add_bots_table_and_update_conversations

Revision ID: 499400791c5b
Revises: bfaa75799d2f
Create Date: 2025-09-04 17:24:52.443294

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '499400791c5b'
down_revision: Union[str, Sequence[str], None] = 'bfaa75799d2f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('bots',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=True),
    sa.Column('bot_type', sa.String(), nullable=True),
    sa.Column('admin_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['admin_id'], ['admins.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_bots_bot_type'), 'bots', ['bot_type'], unique=False)
    op.create_index(op.f('ix_bots_id'), 'bots', ['id'], unique=False)
    op.create_index(op.f('ix_bots_name'), 'bots', ['name'], unique=False)
    op.add_column('conversations', sa.Column('bot_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'conversations', 'bots', ['bot_id'], ['id'])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint(None, 'conversations', type_='foreignkey')
    op.drop_column('conversations', 'bot_id')
    op.drop_index(op.f('ix_bots_name'), table_name='bots')
    op.drop_index(op.f('ix_bots_id'), table_name='bots')
    op.drop_index(op.f('ix_bots_bot_type'), table_name='bots')
    op.drop_table('bots')