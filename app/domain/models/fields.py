from datetime import UTC, datetime

from sqlmodel import Field


def created_at_field() -> Field:
    """Factory function that creates a new created_at Field for each model."""
    return Field(
        default_factory=lambda: datetime.now(UTC),
    )


def updated_at_field() -> Field:
    """Factory function that creates a new updated_at Field for each model."""
    return Field(
        default_factory=lambda: datetime.now(UTC),
        sa_column_kwargs={"onupdate": lambda: datetime.now(UTC)},
    )
