"""add_prompt_version

Revision ID: e68dbaadab2c
Revises: f783d6aeef81
Create Date: 2026-06-23 09:40:49.968726

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e68dbaadab2c'
down_revision: Union[str, Sequence[str], None] = 'f783d6aeef81'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
