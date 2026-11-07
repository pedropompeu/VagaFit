"""job extraction error

Revision ID: 0008
Revises: 0007
Create Date: 2026-11-07
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0008"
down_revision: str | None = "0007"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("jobs", sa.Column("extraction_error", sa.String(length=200), nullable=True))


def downgrade() -> None:
    op.drop_column("jobs", "extraction_error")
