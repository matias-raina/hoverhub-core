"""add_unique_constraint_application_job_account

Revision ID: bcc103cda934
Revises: b7dbb33042cf
Create Date: 2025-11-13 20:21:44.037359

"""

from collections.abc import Sequence

from alembic import op  # type: ignore[import-untyped]

# revision identifiers, used by Alembic.
revision: str = "bcc103cda934"
down_revision: str | None = "b7dbb33042cf"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Alembic op methods are dynamically available at runtime
    op.create_index(  # pyright: ignore[reportAttributeAccessIssue]
        "uix_application_job_account",
        "application",
        ["job_id", "account_id"],
        unique=True,
    )


def downgrade() -> None:
    # Alembic op methods are dynamically available at runtime
    op.drop_index("uix_application_job_account", table_name="application")  # pyright: ignore[reportAttributeAccessIssue]
