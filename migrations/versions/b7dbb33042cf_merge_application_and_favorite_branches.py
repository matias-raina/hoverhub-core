"""merge application and favorite branches

Revision ID: b7dbb33042cf
Revises: 0b10bd19fc4e, 5d6ed782b4c0
Create Date: 2025-11-12 23:30:17.600306

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = 'b7dbb33042cf'
down_revision: Union[str, None] = ('0b10bd19fc4e', '5d6ed782b4c0')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
