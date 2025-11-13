"""add application table

Revision ID: 5d6ed782b4c0
Revises: 82c956358d26
Create Date: 2025-11-12 23:29:47.072711

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = '5d6ed782b4c0'
down_revision: Union[str, None] = '82c956358d26'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create enum type if it doesn't exist (using raw SQL to avoid conflicts)
    conn = op.get_bind()
    conn.execute(
        sa.text(
            "DO $$ BEGIN "
            "CREATE TYPE applicationstatus AS ENUM ('PENDING', 'ACCEPTED', 'REJECTED', 'WITHDRAWN'); "
            "EXCEPTION WHEN duplicate_object THEN null; "
            "END $$;"
        )
    )
    
    op.create_table(
        'application',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('job_id', sa.Uuid(), nullable=False),
        sa.Column('account_id', sa.Uuid(), nullable=False),
        sa.Column('message', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column(
            'status',
            postgresql.ENUM('PENDING', 'ACCEPTED', 'REJECTED', 'WITHDRAWN', name='applicationstatus', create_type=False),
            nullable=False,
        ),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['job_id'], ['job.id']),
        sa.ForeignKeyConstraint(['account_id'], ['account.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_application_id'), 'application', ['id'], unique=False)
    op.create_index(op.f('ix_application_job_id'), 'application', ['job_id'], unique=False)
    op.create_index(op.f('ix_application_account_id'), 'application', ['account_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_application_account_id'), table_name='application')
    op.drop_index(op.f('ix_application_job_id'), table_name='application')
    op.drop_index(op.f('ix_application_id'), table_name='application')
    op.drop_table('application')
    # Drop enum type if it exists
    conn = op.get_bind()
    conn.execute(
        sa.text(
            "DO $$ BEGIN "
            "DROP TYPE applicationstatus; "
            "EXCEPTION WHEN undefined_object THEN null; "
            "END $$;"
        )
    )
