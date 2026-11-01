"""screening answers

Revision ID: 0006
Revises: 0005
Create Date: 2026-11-01 15:07:17.866306
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = '0006'
down_revision: str | None = '0005'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table('screening_answers',
    sa.Column('analysis_id', sa.Uuid(), nullable=False),
    sa.Column('ordinal', sa.Integer(), nullable=False),
    sa.Column('question', sa.Text(), nullable=False),
    sa.Column('answer', sa.Text(), nullable=False),
    sa.Column('evidence', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
    sa.Column('needs_user_input', sa.Boolean(), nullable=False),
    sa.Column('user_question', sa.Text(), nullable=True),
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['analysis_id'], ['analyses.id'], name=op.f('fk_screening_answers_analysis_id_analyses'), ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_screening_answers'))
    )
    op.create_index(op.f('ix_screening_answers_analysis_id'), 'screening_answers', ['analysis_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_screening_answers_analysis_id'), table_name='screening_answers')
    op.drop_table('screening_answers')
