"""merge application and favorite branches

Revision ID: b7dbb33042cf
Revises: 0b10bd19fc4e, 5d6ed782b4c0
Create Date: 2025-11-12 23:30:17.600306

"""

from collections.abc import Sequence

# revision identifiers, used by Alembic.
revision: str = "b7dbb33042cf"
down_revision: tuple[str, str] | str | None = ("0b10bd19fc4e", "5d6ed782b4c0")
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
