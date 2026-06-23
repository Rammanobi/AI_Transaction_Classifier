"""phase2_schema_updates

Revision ID: cd4f81aa96d7
Revises: 0cb50e58a0e5
Create Date: 2026-06-23 09:04:15.504556

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'cd4f81aa96d7'
down_revision: Union[str, Sequence[str], None] = '0cb50e58a0e5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
