from datetime import datetime, timezone

from sqlmodel import Field


def CreatedAtField():
    """Factory function that creates a new created_at Field for each model."""
    return Field(
        default_factory=lambda: datetime.now(timezone.utc),
    )


def UpdatedAtField():
    """Factory function that creates a new updated_at Field for each model."""
    return Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column_kwargs={"onupdate": lambda: datetime.now(timezone.utc)},
    )
