"""merge heads

Revision ID: bfaa75799d2f
Revises: 46e1a4508d2c, f0519d845dae
Create Date: 2025-08-27 22:32:30.346328

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'bfaa75799d2f'
down_revision: Union[str, Sequence[str], None] = ('46e1a4508d2c', 'f0519d845dae')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
